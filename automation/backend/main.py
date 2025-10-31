"""
Main FastAPI application for WKP Automation WebApp
Phase 1: Backend Core Implementation
"""

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncio
import os

from database import get_db, Simulation, init_db
from netbatch_monitor import (
    query_netbatch_status,
    get_summary_stats,
    capture_job_ids_from_log,
    estimate_completion_time,
    CURRENT_USER
)
from simulation import (
    generate_sim_id,
    create_work_directory,
    copy_simulation_files,
    update_config_file,
    run_generation_stage,
    run_submission_stage,
    run_extraction_stage,
    run_sorting_stage,
    run_backup_stage
)

# Initialize FastAPI app
app = FastAPI(
    title="WKP Automation WebApp",
    description="Automated PVT Simulation Platform",
    version="1.0.0"
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"🚀 WKP Automation WebApp started")
    print(f"👤 Current user: {CURRENT_USER}")


# Pydantic models for API requests/responses
class SimulationConfig(BaseModel):
    project: str  # "i3c" or "gpio"
    voltage_domain: str  # "1p1v"
    corner_set: str  # "nom_tt", "full_tt", "full_tt_gsgf", etc.
    library: Optional[str] = "enable_i3c"  # "enable" or "enable_i3c"


class SimulationResponse(BaseModel):
    sim_id: str
    status: str
    message: str
    work_dir: Optional[str] = None


class StatusResponse(BaseModel):
    sim_id: str
    state: str
    progress: dict
    created_at: str
    work_dir: str
    error_message: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "WKP Automation WebApp",
        "version": "1.0.0",
        "status": "running",
        "user": CURRENT_USER,
        "endpoints": {
            "submit": "/api/submit",
            "status": "/api/status/{sim_id}",
            "simulations": "/api/simulations",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "user": CURRENT_USER
    }


@app.get("/api/simulations")
async def list_simulations(db: Session = Depends(get_db)):
    """List all simulations for current user"""
    simulations = db.query(Simulation).filter(
        Simulation.username == CURRENT_USER
    ).order_by(Simulation.created_at.desc()).all()
    
    return {
        "count": len(simulations),
        "simulations": [
            {
                "sim_id": sim.sim_id,
                "project": sim.project,
                "corner_set": sim.corner_set,
                "state": sim.state,
                "progress_pct": sim.progress_pct,
                "created_at": sim.created_at.isoformat(),
                "work_dir": sim.work_dir
            }
            for sim in simulations
        ]
    }


@app.post("/api/submit", response_model=SimulationResponse)
async def submit_simulation(
    config: SimulationConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a new simulation
    
    Phase 1: Runs gen + run stages, captures job IDs, starts monitoring
    """
    
    # 1. Generate simulation ID
    sim_id = generate_sim_id()
    
    print(f"\n{'='*60}")
    print(f"📝 New simulation request: {sim_id}")
    print(f"   Project: {config.project}")
    print(f"   Corner set: {config.corner_set}")
    print(f"   User: {CURRENT_USER}")
    print(f"{'='*60}\n")
    
    try:
        # 2. Create working directory
        work_dir = create_work_directory(
            config.project,
            config.voltage_domain,
            sim_id
        )
        
        # 3. Copy simulation files
        if not copy_simulation_files(config.project, config.voltage_domain, work_dir):
            raise Exception("Failed to copy simulation files")
        
        # 4. Update config.cfg with corner set
        update_config_file(work_dir, config.corner_set)
        
        # 5. Create database entry
        sim = Simulation(
            sim_id=sim_id,
            project=config.project,
            voltage_domain=config.voltage_domain,
            corner_set=config.corner_set,
            library=config.library,
            state="created",
            work_dir=work_dir,
            username=CURRENT_USER
        )
        db.add(sim)
        db.commit()
        db.refresh(sim)
        
        # 6. Run generation stage
        print("\n🔧 Stage 1: Generation")
        if not run_generation_stage(work_dir):
            sim.state = "failed"
            sim.error_message = "Generation stage failed"
            db.commit()
            raise HTTPException(status_code=500, detail="Generation failed")
        
        # 7. Run submission stage
        print("\n🚀 Stage 2: Submission")
        job_log_path = run_submission_stage(work_dir)
        
        if not job_log_path:
            sim.state = "failed"
            sim.error_message = "Submission stage failed"
            db.commit()
            raise HTTPException(status_code=500, detail="Submission failed")
        
        # 8. Capture job IDs
        job_ids = capture_job_ids_from_log(job_log_path)
        
        if not job_ids:
            sim.state = "failed"
            sim.error_message = "No job IDs captured from log"
            db.commit()
            raise HTTPException(status_code=500, detail="No job IDs found")
        
        # 9. Update database
        sim.state = "submitted"
        sim.submitted_at = datetime.utcnow()
        sim.netbatch_job_ids = job_ids
        sim.job_log_path = job_log_path
        sim.total_jobs = len(job_ids)
        db.commit()
        
        print(f"\n✅ Simulation submitted successfully!")
        print(f"   Sim ID: {sim_id}")
        print(f"   Jobs submitted: {len(job_ids)}")
        print(f"   Work directory: {work_dir}")
        
        # 10. Start background monitoring
        background_tasks.add_task(monitor_simulation, sim.id, db)
        
        return SimulationResponse(
            sim_id=sim_id,
            status="submitted",
            message=f"Simulation submitted with {len(job_ids)} jobs",
            work_dir=work_dir
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Submission error: {e}")
        # Clean up database entry if exists
        if 'sim' in locals():
            db.delete(sim)
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{sim_id}", response_model=StatusResponse)
async def get_simulation_status(sim_id: str, db: Session = Depends(get_db)):
    """Get status of a simulation"""
    
    sim = db.query(Simulation).filter(
        Simulation.sim_id == sim_id,
        Simulation.username == CURRENT_USER
    ).first()
    
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Query current NetBatch status if running
    if sim.state in ["submitted", "running"] and sim.netbatch_job_ids:
        statuses = query_netbatch_status(sim.netbatch_job_ids)
        stats = get_summary_stats(statuses, sim.total_jobs)
        
        # Update database
        sim.jobs_completed = stats["completed"]
        sim.jobs_running = stats["running"]
        sim.jobs_waiting = stats["waiting"]
        sim.jobs_errors = stats["errors"]
        sim.progress_pct = int(stats["progress_pct"])
        
        if stats["all_complete"]:
            sim.state = "completed"
            sim.completed_at = datetime.utcnow()
        elif sim.state == "submitted" and stats["running"] > 0:
            sim.state = "running"
        
        db.commit()
    else:
        stats = {
            "total": sim.total_jobs,
            "completed": sim.jobs_completed,
            "running": sim.jobs_running,
            "waiting": sim.jobs_waiting,
            "errors": sim.jobs_errors,
            "progress_pct": sim.progress_pct
        }
    
    return StatusResponse(
        sim_id=sim.sim_id,
        state=sim.state,
        progress=stats,
        created_at=sim.created_at.isoformat(),
        work_dir=sim.work_dir,
        error_message=sim.error_message
    )


@app.post("/api/extract/{sim_id}")
async def trigger_extraction(
    sim_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger extraction for a completed simulation"""
    
    sim = db.query(Simulation).filter(
        Simulation.sim_id == sim_id,
        Simulation.username == CURRENT_USER
    ).first()
    
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if sim.state not in ["completed", "extracting", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot extract - simulation state is {sim.state}"
        )
    
    # Run extraction in background
    background_tasks.add_task(run_extraction_workflow, sim.id, db)
    
    return {"message": "Extraction started", "sim_id": sim_id}


# Background task functions

async def monitor_simulation(sim_db_id: int, db: Session):
    """
    Background task to monitor NetBatch jobs
    Polls every 1 second until all complete
    """
    # Need to get fresh DB session for background task
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        sim = db.query(Simulation).filter(Simulation.id == sim_db_id).first()
        
        if not sim or not sim.netbatch_job_ids:
            print(f"⚠️ Cannot monitor - no job IDs for sim {sim_db_id}")
            return
        
        print(f"\n👀 Starting monitoring for {sim.sim_id} ({sim.total_jobs} jobs)")
        
        poll_count = 0
        while True:
            poll_count += 1
            
            # Query NetBatch
            statuses = query_netbatch_status(sim.netbatch_job_ids)
            stats = get_summary_stats(statuses, sim.total_jobs)
            
            # Update database
            sim.jobs_completed = stats["completed"]
            sim.jobs_running = stats["running"]
            sim.jobs_waiting = stats["waiting"]
            sim.jobs_errors = stats["errors"]
            sim.progress_pct = int(stats["progress_pct"])
            
            if stats["running"] > 0 and sim.state == "submitted":
                sim.state = "running"
            
            db.commit()
            
            # Log progress every 10 polls (10 seconds)
            if poll_count % 10 == 0:
                print(f"📊 {sim.sim_id}: {stats['completed']}/{stats['total']} complete ({stats['progress_pct']:.1f}%)")
            
            # Check completion
            if stats["all_complete"]:
                print(f"\n✅ All jobs completed for {sim.sim_id}!")
                sim.state = "completed"
                sim.completed_at = datetime.utcnow()
                db.commit()
                
                # Trigger extraction
                await run_extraction_workflow(sim.id, db)
                break
            
            # Check for errors
            if stats["has_errors"]:
                print(f"\n⚠️ {stats['errors']} jobs failed for {sim.sim_id}")
                sim.state = "failed"
                sim.error_message = f"{stats['errors']} NetBatch jobs failed"
                db.commit()
                break
            
            # Sleep 1 second
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"\n❌ Monitor error for sim {sim_db_id}: {e}")
        if sim:
            sim.state = "failed"
            sim.error_message = f"Monitoring error: {str(e)}"
            db.commit()
    finally:
        db.close()


async def run_extraction_workflow(sim_db_id: int, db: Session):
    """
    Background task to run extraction workflow
    Runs: ext -> srt -> bkp stages
    """
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        sim = db.query(Simulation).filter(Simulation.id == sim_db_id).first()
        
        if not sim:
            print(f"⚠️ Simulation {sim_db_id} not found for extraction")
            return
        
        print(f"\n📊 Starting extraction workflow for {sim.sim_id}")
        
        # Stage 1: Extraction
        sim.state = "extracting"
        db.commit()
        
        if not run_extraction_stage(sim.work_dir):
            sim.state = "failed"
            sim.error_message = "Extraction stage failed"
            db.commit()
            return
        
        # Stage 2: Sorting
        sim.state = "sorting"
        db.commit()
        
        if not run_sorting_stage(sim.work_dir):
            sim.state = "failed"
            sim.error_message = "Sorting stage failed"
            db.commit()
            return
        
        # Stage 3: Backup
        sim.state = "backing_up"
        db.commit()
        
        backup_dir = run_backup_stage(sim.work_dir)
        if not backup_dir:
            sim.state = "failed"
            sim.error_message = "Backup stage failed"
            db.commit()
            return
        
        # Success!
        sim.state = "finished"
        sim.finished_at = datetime.utcnow()
        sim.backup_dir = backup_dir
        db.commit()
        
        print(f"\n🎉 Extraction workflow complete for {sim.sim_id}")
        print(f"   Results: {backup_dir}")
        
    except Exception as e:
        print(f"\n❌ Extraction workflow error for sim {sim_db_id}: {e}")
        if sim:
            sim.state = "failed"
            sim.error_message = f"Extraction workflow error: {str(e)}"
            db.commit()
    finally:
        db.close()


# Run with: uvicorn main:app --host 127.0.0.1 --port 5000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
