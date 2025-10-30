#!/bin/bash
# WKPUP Installation Script
# Installs dependencies and sets up the WKPUP web application

set -e

echo "========================================="
echo "WKPUP Installation Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Check pip
echo "Checking pip..."
pip3 --version || { echo "Error: pip3 is required"; exit 1; }

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install tornado

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p data

# Set permissions
echo ""
echo "Setting permissions..."
chmod +x start_server.sh
chmod 755 src/*.py
chmod 644 templates/*.html
chmod 644 static/css/*.css

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "
from src.database import DatabaseManager
db = DatabaseManager('data/wkpup.db')
print('Database initialized successfully')
db.close()
"

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure Pai Ho script paths in start_server.sh"
echo "2. Run: ./start_server.sh"
echo ""
