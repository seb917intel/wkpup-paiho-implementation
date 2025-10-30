#!/usr/bin/env python3
"""
WKPUP Web Server

Tornado-based web server for job submission, monitoring, and result viewing.
This module is part of the WKPUP reconciliation project, providing a web interface
for Pai Ho's simulation workflow.

Reference: ULTIMATE_MASTER_PLAN.md - Module 6: web_server.py (~400 lines)
Feature Extraction: Web UI from wkpup-simulation
"""

import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import logging
from typing import Dict, List, Set
from pathlib import Path


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common functionality"""
    
    def initialize(self, db, job_manager, config_generator, result_parser):
        """
        Initialize handler with dependencies.
        
        Args:
            db: DatabaseManager instance
            job_manager: BackgroundJobManager instance
            config_generator: PaiHoConfigGenerator instance
            result_parser: ResultParser instance
        """
        self.db = db
        self.job_manager = job_manager
        self.config_generator = config_generator
        self.result_parser = result_parser
    
    def set_default_headers(self):
        """Set CORS and security headers"""
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("X-Frame-Options", "DENY")
        self.set_header("X-XSS-Protection", "1; mode=block")


class MainHandler(BaseHandler):
    """
    Main page handler - Job submission form.
    
    GET: Display submission form with parameter options
    POST: Handle job submission
    """
    
    def get(self):
        """Display job submission form"""
        # Get valid options from config generator
        valid_corners = self.config_generator.get_valid_corners()
        valid_voltages = self.config_generator.get_valid_voltages('ac')
        
        # Get queue status
        queue_status = self.job_manager.get_queue_status()
        
        self.render("templates/index.html",
                   corners=valid_corners,
                   voltages=valid_voltages,
                   queue_status=queue_status)
    
    def post(self):
        """Handle job submission"""
        try:
            # Extract parameters from form
            params = {
                'mode': self.get_argument('mode'),
                'vccn': self.get_argument('vccn'),
                'vcctx': self.get_argument('vcctx', default='1p0v'),
                '1st_supply_swp': self.get_argument('1st_supply_swp', default='v1nom'),
                '2nd_supply_swp': self.get_argument('2nd_supply_swp', default='v2nom'),
                '3rd_supply_swp': self.get_argument('3rd_supply_swp', default='v3nom'),
                'condition': self.get_argument('condition', default='perf'),
                'CPU': self.get_argument('CPU', default='16'),
                'MEM': self.get_argument('MEM', default='32G'),
                'sim_mode': self.get_argument('sim_mode', default='ac'),
                'simulator': self.get_argument('simulator', default='primesim'),
                'domain_path': self.get_argument('domain_path'),
                'user': self.get_argument('user', default='web_user'),
                'description': self.get_argument('description', default='')
            }
            
            # Validate parameters
            is_valid, error = self.config_generator.validate_params(params)
            if not is_valid:
                self.set_status(400)
                self.write({
                    'success': False,
                    'error': f'Validation error: {error}'
                })
                return
            
            # Create job in database
            job_id = self.db.create_job(params)
            
            # Submit to background job manager
            self.job_manager.submit(job_id)
            
            # Return success with job_id
            self.write({
                'success': True,
                'job_id': job_id,
                'message': 'Job submitted successfully'
            })
            
        except Exception as e:
            logging.exception("Job submission error")
            self.set_status(500)
            self.write({
                'success': False,
                'error': str(e)
            })


class ResultsHandler(BaseHandler):
    """
    Results page handler - View job results.
    
    GET: Display results for a specific job
    """
    
    def get(self, job_id=None):
        """Display job results"""
        if not job_id:
            # Show list of recent jobs
            jobs = self.db.get_job_history(limit=50)
            self.render("templates/results.html", jobs=jobs, job=None, results=None)
            return
        
        # Get specific job
        job = self.db.get_job(job_id)
        if not job:
            self.set_status(404)
            self.write("Job not found")
            return
        
        # Get results
        results = self.db.get_job_results(job_id)
        
        # Generate summary
        if results:
            summary = self.result_parser.generate_summary(results)
        else:
            summary = None
        
        self.render("templates/results.html",
                   jobs=None,
                   job=job,
                   results=results,
                   summary=summary)


class JobsHandler(BaseHandler):
    """
    Jobs list API handler.
    
    GET: Return list of jobs (JSON)
    """
    
    def get(self):
        """Get job list"""
        status_filter = self.get_argument('status', default=None)
        limit = int(self.get_argument('limit', default='100'))
        
        jobs = self.db.get_job_history(limit=limit, status_filter=status_filter)
        
        self.write({
            'success': True,
            'jobs': jobs
        })


class JobStatusHandler(BaseHandler):
    """
    Job status API handler.
    
    GET: Get status of specific job
    """
    
    def get(self, job_id):
        """Get job status"""
        job = self.db.get_job(job_id)
        
        if not job:
            self.set_status(404)
            self.write({
                'success': False,
                'error': 'Job not found'
            })
            return
        
        # Get completed stages
        if job.get('completed_stages'):
            completed_stages = json.loads(job['completed_stages'])
        else:
            completed_stages = []
        
        self.write({
            'success': True,
            'job_id': job_id,
            'status': job['status'],
            'current_stage': job.get('current_stage'),
            'completed_stages': completed_stages,
            'created_at': job.get('created_at'),
            'started_at': job.get('started_at'),
            'completed_at': job.get('completed_at'),
            'elapsed_seconds': job.get('elapsed_seconds'),
            'error_message': job.get('error_message')
        })


class CancelJobHandler(BaseHandler):
    """
    Job cancellation handler.
    
    POST: Cancel a job
    """
    
    def post(self, job_id):
        """Cancel a job"""
        try:
            success = self.job_manager.cancel_job(job_id)
            
            if success:
                self.write({
                    'success': True,
                    'message': 'Job cancelled'
                })
            else:
                self.set_status(400)
                self.write({
                    'success': False,
                    'error': 'Job cannot be cancelled'
                })
                
        except Exception as e:
            logging.exception("Cancel job error")
            self.set_status(500)
            self.write({
                'success': False,
                'error': str(e)
            })


class QueueStatusHandler(BaseHandler):
    """
    Queue status API handler.
    
    GET: Get current queue status
    """
    
    def get(self):
        """Get queue status"""
        status = self.job_manager.get_queue_status()
        
        self.write({
            'success': True,
            **status
        })


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    WebSocket handler for real-time job status updates.
    
    Clients can subscribe to job updates and receive real-time notifications.
    """
    
    # Class-level set of all connected clients
    clients: Set['WebSocketHandler'] = set()
    
    def initialize(self, db, job_manager):
        """Initialize with dependencies"""
        self.db = db
        self.job_manager = job_manager
        self.subscribed_jobs = set()
    
    def check_origin(self, origin):
        """Allow connections from any origin (configure for production)"""
        return True
    
    def open(self):
        """WebSocket connection opened"""
        WebSocketHandler.clients.add(self)
        logging.info(f"WebSocket opened. Total clients: {len(WebSocketHandler.clients)}")
    
    def on_message(self, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'subscribe':
                # Subscribe to job updates
                job_id = data.get('job_id')
                if job_id:
                    self.subscribed_jobs.add(job_id)
                    self.write_message({
                        'type': 'subscribed',
                        'job_id': job_id
                    })
            
            elif action == 'unsubscribe':
                # Unsubscribe from job updates
                job_id = data.get('job_id')
                if job_id:
                    self.subscribed_jobs.discard(job_id)
                    self.write_message({
                        'type': 'unsubscribed',
                        'job_id': job_id
                    })
            
            elif action == 'ping':
                # Heartbeat
                self.write_message({'type': 'pong'})
                
        except json.JSONDecodeError:
            logging.warning("Invalid WebSocket message")
        except Exception as e:
            logging.exception("WebSocket message error")
    
    def on_close(self):
        """WebSocket connection closed"""
        WebSocketHandler.clients.discard(self)
        logging.info(f"WebSocket closed. Total clients: {len(WebSocketHandler.clients)}")
    
    @classmethod
    def broadcast_status_update(cls, job_id: str, status: str, **kwargs):
        """
        Broadcast status update to all subscribed clients.
        
        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional status information
        """
        message = {
            'type': 'status_update',
            'job_id': job_id,
            'status': status,
            **kwargs
        }
        
        # Send to all clients subscribed to this job
        for client in list(cls.clients):
            try:
                if job_id in client.subscribed_jobs:
                    client.write_message(message)
            except Exception as e:
                logging.exception("WebSocket broadcast error")


def make_app(db, job_manager, config_generator, result_parser, 
             template_path="templates", static_path="static"):
    """
    Create Tornado application.
    
    Args:
        db: DatabaseManager instance
        job_manager: BackgroundJobManager instance
        config_generator: PaiHoConfigGenerator instance
        result_parser: ResultParser instance
        template_path: Path to templates directory
        static_path: Path to static files directory
        
    Returns:
        Tornado Application instance
    """
    # Register status callback for WebSocket updates
    job_manager.register_status_callback(WebSocketHandler.broadcast_status_update)
    
    return tornado.web.Application([
        (r"/", MainHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/results/?([^/]*)", ResultsHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/api/jobs", JobsHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/api/job/([^/]+)/status", JobStatusHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/api/job/([^/]+)/cancel", CancelJobHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/api/queue/status", QueueStatusHandler, {
            'db': db,
            'job_manager': job_manager,
            'config_generator': config_generator,
            'result_parser': result_parser
        }),
        (r"/ws", WebSocketHandler, {
            'db': db,
            'job_manager': job_manager
        }),
    ],
    template_path=template_path,
    static_path=static_path,
    debug=True)


# Example usage
if __name__ == "__main__":
    from database import DatabaseManager
    from job_manager import BackgroundJobManager
    from config_generator import PaiHoConfigGenerator
    from result_parser import ResultParser
    from paiho_executor import PaiHoExecutor
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize components
    db = DatabaseManager('wkpup.db')
    config_gen = PaiHoConfigGenerator('/path/to/ver03/configuration')
    result_parser = ResultParser()
    
    def executor_factory(domain_path):
        return PaiHoExecutor(domain_path)
    
    job_mgr = BackgroundJobManager(db, executor_factory, max_workers=4)
    
    # Create and start web app
    app = make_app(db, job_mgr, config_gen, result_parser)
    port = 8888
    
    app.listen(port)
    logging.info(f"Web server started on http://localhost:{port}")
    
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        job_mgr.shutdown(wait=True)
        db.close()
