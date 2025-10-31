#!/bin/bash
# Simple launcher for the WKP Automation WebApp

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    WKP Automation WebApp - Development Server              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "  🐍 Python:    $(python3 --version 2>&1)"
echo "  🌪️  Tornado:   $(python3 -c 'import tornado; print(tornado.version)' 2>/dev/null || echo 'Not installed')"
echo "  🌐 Server:    http://localhost:5000"
echo "  📊 Frontend:  http://localhost:5000/frontend/"
echo "  👤 User:      $USER"
echo "  📁 Database:  $SCRIPT_DIR/webapp.db"
echo "  📁 Repo root: $(cd $SCRIPT_DIR/.. && pwd)"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

# Initialize database if needed
if [ ! -f "$SCRIPT_DIR/webapp.db" ]; then
    echo "  📊 Initializing database..."
    cd "$BACKEND_DIR"
    python3 database.py
    echo "  ✓ Database ready"
    echo ""
fi

# Start the server
cd "$BACKEND_DIR"
exec python3 main_tornado.py
