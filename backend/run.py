#!/usr/bin/env python3
"""
Backend server entry point
"""
import os
import sys
from flask.cli import with_appcontext
import click

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.base import db
from app.models import User, UserRole

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
