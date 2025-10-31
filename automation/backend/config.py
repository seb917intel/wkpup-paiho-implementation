#!/usr/bin/env python3
"""
Configuration file for WKP Automation WebApp
Defines paths and settings for the repository
"""

import os
from pathlib import Path

# Get repository root (2 levels up from backend/)
BACKEND_DIR = Path(__file__).parent.resolve()
AUTOMATION_DIR = BACKEND_DIR.parent.resolve()
REPO_ROOT = AUTOMATION_DIR.parent.resolve()

# Project directories
GPIO_ROOT = REPO_ROOT / "gpio"
I3C_ROOT = REPO_ROOT / "i3c"

# Database path
DB_PATH = str(AUTOMATION_DIR / "webapp.db")

# Default voltage domains
DEFAULT_VOLTAGE_DOMAINS = {
    'gpio': ['1p1v'],
    'i3c': ['1p1v', '1p2v', '1p8v', '1p15v']
}

# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000

# Debug settings
DEBUG = True

def get_project_root(project: str) -> Path:
    """Get root directory for a project"""
    if project == 'gpio':
        return GPIO_ROOT
    elif project == 'i3c':
        return I3C_ROOT
    else:
        raise ValueError(f"Unknown project: {project}")

def get_voltage_domain_path(project: str, voltage_domain: str) -> Path:
    """Get path to voltage domain directory"""
    return get_project_root(project) / voltage_domain
