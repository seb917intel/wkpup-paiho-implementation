#!/bin/bash
# WKPUP Server Startup Script
# Starts the Tornado web server with all components

set -e

# Configuration
PORT=${PORT:-8888}
MAX_WORKERS=${MAX_WORKERS:-4}
PAIHO_SCRIPT_PATH=${PAIHO_SCRIPT_PATH:-"/path/to/auto_pvt/ver03/configuration"}
DB_PATH=${DB_PATH:-"data/wkpup.db"}
LOG_FILE=${LOG_FILE:-"logs/wkpup_server.log"}

echo "========================================="
echo "WKPUP Server Startup"
echo "========================================="
echo ""
echo "Configuration:"
echo "  Port: $PORT"
echo "  Max Workers: $MAX_WORKERS"
echo "  Pai Ho Scripts: $PAIHO_SCRIPT_PATH"
echo "  Database: $DB_PATH"
echo "  Log File: $LOG_FILE"
echo ""

# Check if Pai Ho scripts exist
if [ ! -d "$PAIHO_SCRIPT_PATH" ]; then
    echo "WARNING: Pai Ho script path not found: $PAIHO_SCRIPT_PATH"
    echo "Please update PAIHO_SCRIPT_PATH in this script or set environment variable"
    echo ""
fi

# Start server
echo "Starting server..."
python3 -c "
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from database import DatabaseManager
from job_manager import BackgroundJobManager
from config_generator import PaiHoConfigGenerator
from result_parser import ResultParser
from paiho_executor import PaiHoExecutor
from web_server import make_app
import tornado.ioloop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('$LOG_FILE'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    # Initialize components
    logger.info('Initializing database...')
    db = DatabaseManager('$DB_PATH')
    
    logger.info('Initializing config generator...')
    config_gen = PaiHoConfigGenerator('$PAIHO_SCRIPT_PATH')
    
    logger.info('Initializing result parser...')
    result_parser = ResultParser()
    
    logger.info('Initializing job manager...')
    def executor_factory(domain_path):
        return PaiHoExecutor(domain_path)
    
    job_mgr = BackgroundJobManager(db, executor_factory, max_workers=$MAX_WORKERS)
    
    # Create and start web app
    logger.info('Creating web application...')
    app = make_app(db, job_mgr, config_gen, result_parser)
    
    logger.info('Starting web server on port $PORT...')
    app.listen($PORT)
    
    print('')
    print('========================================')
    print('Server running at http://localhost:$PORT')
    print('Press Ctrl+C to stop')
    print('========================================')
    print('')
    
    tornado.ioloop.IOLoop.current().start()
    
except KeyboardInterrupt:
    logger.info('Shutting down...')
    job_mgr.shutdown(wait=True)
    db.close()
    logger.info('Shutdown complete')
except Exception as e:
    logger.exception('Server error')
    sys.exit(1)
"
