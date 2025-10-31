#!/bin/bash
################################################################################
# WKP Automation WebApp Launcher
# Single script to start the web application
################################################################################

echo "🚀 Starting WKP Automation WebApp..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python found: $PYTHON_VERSION"

# 2. Install dependencies to user directory (no venv needed)
if [ ! -f ".deps_installed" ] || [ requirements.txt -nt .deps_installed ]; then
    echo "📥 Installing dependencies to user directory..."
    echo "   (Skipping venv due to network/authentication issues)"
    echo ""
    
    # Install packages to ~/.local (user site-packages)
    python3 -m pip install --user -r requirements.txt --default-timeout=100 --retries 2
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Failed to install dependencies"
        echo ""
        echo "Troubleshooting options:"
        echo "  1. Check network/proxy: env | grep -i proxy"
        echo "  2. Try manual install: python3 -m pip install --user fastapi uvicorn sqlalchemy"
        echo "  3. Contact IT for PyPI access"
        exit 1
    fi
    touch .deps_installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies up to date"
fi

# 3. Initialize database (if not exists)
if [ ! -f "webapp.db" ]; then
    echo "🗄️  Initializing database..."
    python3 -c "from backend.database import init_db; init_db()"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to initialize database"
        exit 1
    fi
    echo "✓ Database initialized"
else
    echo "✓ Database exists"
fi

# 4. Display info
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         WKP Automation WebApp - Phase 1                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  🌐 Server:    http://localhost:5000"
echo "  📊 API Docs:  http://localhost:5000/docs"
echo "  👤 User:      $USER"
echo ""
echo "  📁 Work dir:  /nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup"
echo ""
echo "  Available endpoints:"
echo "    GET  /                     - Service info"
echo "    GET  /api/health           - Health check"
echo "    GET  /api/simulations      - List your simulations"
echo "    POST /api/submit           - Submit new simulation"
echo "    GET  /api/status/{sim_id}  - Get simulation status"
echo "    POST /api/extract/{sim_id} - Trigger extraction"
echo ""
echo "  Press Ctrl+C to stop"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# 5. Start backend server
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 5000 --reload
