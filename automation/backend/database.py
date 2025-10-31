"""
Database module for WKP Automation WebApp
Uses SQLite for lightweight local deployment
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from pathlib import Path

# Database path (in automation directory) - use absolute path for consistency
BACKEND_DIR = Path(__file__).parent.resolve()
AUTOMATION_DIR = BACKEND_DIR.parent.resolve()
DB_PATH = str(AUTOMATION_DIR / "webapp.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Debug logging to confirm database location
print(f"📊 Database path: {DB_PATH}")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Simulation(Base):
    """Simulation run model"""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    sim_id = Column(String, unique=True, index=True)  # e.g., "sim_20251021_143012"
    project = Column(String)  # "i3c" or "gpio"
    voltage_domain = Column(String)  # "1p1v"
    corner_set = Column(String)  # "nom_tt", "full_tt", etc.
    library = Column(String)  # "enable" or "enable_i3c"
    
    # State tracking
    state = Column(String, default="created")  # created, submitted, running, completed, extracting, moving, backing_up, finished, failed
    
    # Paths
    work_dir = Column(String)  # Working directory path
    backup_dir = Column(String, nullable=True)  # Backup directory path (after completion)
    
    # NetBatch tracking
    netbatch_job_ids = Column(JSON)  # List of NetBatch job IDs
    job_log_path = Column(String)  # Path to job_log.txt
    
    # Progress tracking
    total_jobs = Column(Integer, default=0)
    jobs_completed = Column(Integer, default=0)
    jobs_running = Column(Integer, default=0)
    jobs_waiting = Column(Integer, default=0)
    jobs_errors = Column(Integer, default=0)
    progress_pct = Column(Integer, default=0)
    
    # Resume data
    resume_data = Column(JSON, nullable=True)  # Store step-specific data
    last_successful_step = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    # User tracking
    username = Column(String)  # User who created the simulation
    
    def __repr__(self):
        return f"<Simulation {self.sim_id} state={self.state} progress={self.progress_pct}%>"


def init_db():
    """Initialize database - create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DB_PATH}")


def get_db():
    """Get database session (for dependency injection in FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Can run this directly to initialize database
    init_db()
