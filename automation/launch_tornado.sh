#!/bin/bash
################################################################################
# WKP Automation WebApp Launcher - Phase 1b (Tornado-based)
# PREREQUISITE: Must run from Cheetah-enabled shell (after setup_cheetah.csh)
################################################################################

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         WKP Automation WebApp - Phase 1b                   ║"
echo "║              (Tornado-based - No pip needed)               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Cheetah environment is available
if ! command -v primesim &> /dev/null || ! command -v nbjob &> /dev/null; then
    echo "❌ Cheetah environment not found!"
    echo ""
    echo "Please run this first:"
    echo "  csh setup_cheetah.csh"
    echo ""
    echo "Then launch the webapp from the CTH-psg shell."
    exit 1
fi

# Use system Python (has Tornado), not Cheetah Python
PYTHON_BIN="/usr/bin/python3"

# Verify system Python has Tornado
if ! $PYTHON_BIN -c "import tornado" 2>/dev/null; then
    echo "❌ Tornado not found in system Python"
    echo "   Tried: $PYTHON_BIN"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')
TORNADO_VERSION=$($PYTHON_BIN -c "import tornado; print(tornado.version)" 2>/dev/null)

echo "  🐍 Python:    $PYTHON_VERSION (system)"
echo "  🌪️  Tornado:   $TORNADO_VERSION"
echo "  🌐 Server:    http://localhost:5000"
echo "  📊 Frontend:  http://localhost:5000/frontend/"
echo "  👤 User:      $USER"
echo "  📁 Database:  ./webapp.db"
echo "  📁 Work dir:  /nfs/site/disks/km6_io_37/users/chinseba/simulation/wkpup"
echo ""
echo "  ✓ NetBatch:   $(which nbjob)"
echo "  ✓ Primesim:   $(which primesim)"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

# Initialize database if needed
if [ ! -f "$SCRIPT_DIR/webapp.db" ]; then
    echo "  📊 Initializing database..."
    cd "$SCRIPT_DIR/backend"
    $PYTHON_BIN -c "from database import init_db; init_db()"
    echo "  ✓ Database ready"
    echo ""
fi

# Sync shared files across voltage domains
echo "  🔄 Syncing shared files across voltage domains..."
cd "$SCRIPT_DIR"
$PYTHON_BIN backend/sync_shared_files.py --quiet
if [ $? -eq 0 ]; then
    echo "  ✓ Files synchronized"
else
    echo "  ⚠️  Sync completed with warnings"
fi
echo ""

# Run webapp with system Python (has Tornado)
# Environment variables from Cheetah are preserved, so NetBatch tools work
cd "$SCRIPT_DIR/backend"
exec $PYTHON_BIN main_tornado.py
