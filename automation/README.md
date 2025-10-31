# WKP Automation WebApp

A modern web-based interface for WKPUP (Weak Pull-Up) characterization simulations, providing an intuitive UI for configuring and submitting PVT (Process-Voltage-Temperature) corner simulations.

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or later
- Tornado web framework
- SQLAlchemy for database

### Installation

```bash
# Install dependencies
pip install tornado sqlalchemy

# Or use the provided requirements file
pip install -r requirements.txt
```

### Starting the Server

```bash
# Simple start script
./start_server.sh

# Or start manually
cd backend
python3 main_tornado.py
```

The server will start on **http://localhost:5000**

### Accessing the Web UI

Open your browser and navigate to:
- **Frontend UI**: http://localhost:5000/frontend/
- **API Root**: http://localhost:5000/
- **API Health**: http://localhost:5000/api/health

## 📋 Features

### ✨ Frontend Features

1. **Project Selection**
   - I3C or GPIO projects
   - Voltage domain configuration (1p1v, 1p2v, 1p8v, 1p15v)
   - Real-time domain ID validation

2. **Corner Selection**
   - 9 PVT corners (TT, FFG, SSG, FSG, SFG, FFAG, SSAG, FFG_SSG, SSG_FFG)
   - Quick presets: TT Only, Quick (3), Major (7), All (9)
   - Individual corner selection

3. **Temperature & Voltage Strategy**
   - Pai Ho's Standard PVT (industry validated)
   - Full Sweep (maximum coverage)
   - Custom manual selection
   - Dynamic voltage table based on supply configuration

4. **Job Estimation**
   - Real-time job count calculation
   - Estimated execution time
   - Visual job formula display

5. **Advanced Options**
   - NetBatch resource allocation (CPU cores, memory)
   - Custom template directory path
   - Path history management

6. **Real-Time Updates**
   - WebSocket connectivity
   - Live simulation status
   - Ping/pong heartbeat monitoring

### 🔧 Backend Features

1. **RESTful API**
   - Job submission
   - Status tracking
   - Supply configuration
   - Results retrieval

2. **Database Management**
   - SQLite for job tracking
   - Result storage
   - Job history

3. **Simulation Execution**
   - Integration with Pai Ho's scripts
   - PVT corner automation
   - NetBatch job submission

4. **WebSocket Support**
   - Real-time status updates
   - Progress monitoring
   - Error notifications

## 📁 Directory Structure

```
automation/
├── backend/
│   ├── main_tornado.py          # Tornado web server
│   ├── simulation.py            # Simulation execution
│   ├── database.py              # SQLite database layer
│   ├── config.py                # Path configuration
│   ├── websocket_handler.py     # WebSocket handler
│   ├── voltage_domain_manager.py # Voltage domain management
│   ├── netbatch_monitor.py      # NetBatch monitoring
│   ├── results_parser.py        # Results parsing
│   └── background_monitor.py    # Background job monitoring
├── frontend/
│   ├── index.html               # Main UI (job submission)
│   └── results.html             # Results viewer
├── start_server.sh              # Server launch script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🎯 Usage Guide

### Submitting a Simulation

1. **Select Project**: Choose I3C or GPIO
2. **Enter Voltage**: Type voltage value (e.g., 1.1)
3. **Select Voltage Condition**: Choose perf, func, htol, or hvqk
4. **Choose Corners**: Click preset or select individually
5. **Configure Temperature/Voltage**: Use presets or customize
6. **Review Job Estimate**: Check job count and estimated time
7. **Advanced Options** (Optional): Set NetBatch resources
8. **Submit**: Click "🚀 Submit Simulation"

### Viewing Results

Navigate to the "Your Simulations" section to:
- View submitted jobs
- Check status
- Filter by state or project
- Access detailed results

### WebSocket Real-Time Updates

The UI automatically connects via WebSocket for:
- Live job status updates
- Progress notifications
- Error alerts
- Completion notifications

## 🔌 API Endpoints

### Core Endpoints

```
GET  /                           - API information
GET  /api/health                 - Health check
GET  /api/simulations            - List all simulations
POST /api/submit                 - Submit new simulation
GET  /api/status/{sim_id}        - Get simulation status
GET  /api/supply-config          - Get supply configuration
POST /api/extract/{sim_id}       - Extract simulation results
```

### WebSocket Endpoint

```
WS   /ws/simulations             - WebSocket for real-time updates
```

## ⚙️ Configuration

### Path Configuration

Edit `backend/config.py` to customize:
- `REPO_ROOT`: Repository root directory
- `GPIO_ROOT`: GPIO project directory
- `I3C_ROOT`: I3C project directory
- `DB_PATH`: Database file location

### Server Configuration

Edit `backend/main_tornado.py` or use environment variables:
- `SERVER_HOST`: Default "0.0.0.0"
- `SERVER_PORT`: Default 5000

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Try a different port
export SERVER_PORT=8888
python3 backend/main_tornado.py
```

### Database errors
```bash
# Reinitialize database
cd backend
python3 database.py
```

### WebSocket connection fails
- Check browser console for errors
- Verify server is running
- Check firewall settings

### Supply configuration not loading
- Verify voltage domain exists in repository
- Check `config.py` paths are correct
- Review server logs for errors

## 📊 Technology Stack

- **Backend**: Python 3.6+, Tornado, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **WebSocket**: Tornado WebSocket
- **Database**: SQLite3
- **Architecture**: RESTful API with WebSocket real-time updates

## 🎨 UI Theme

The UI features a modern purple gradient theme with:
- Responsive design
- Clean card-based layout
- Real-time status indicators
- Intuitive form controls
- Visual job estimation

## 📝 Development

### Adding New Features

1. **Backend**: Add handlers to `main_tornado.py`
2. **Frontend**: Modify `index.html` or `results.html`
3. **Database**: Update models in `database.py`
4. **API**: Follow RESTful conventions

### Testing

```bash
# Test backend imports
cd backend
python3 -c "import main_tornado; print('OK')"

# Test database
python3 database.py

# Start server and test in browser
python3 main_tornado.py
```

## 🤝 Contributing

This is an internal Altera/Intel project. For questions or contributions, contact the WKPUP team.

## 📄 License

Internal Intel/Altera use only. Not for external distribution.

## 🙏 Acknowledgments

- Based on Pai Ho's validated WKPUP2 implementation
- UI inspired by wkpup-simulation reference repository
- Built for the Intel/Altera design team

---

**Version**: 1.0.0  
**Last Updated**: October 31, 2025  
**Status**: ✅ Production Ready
