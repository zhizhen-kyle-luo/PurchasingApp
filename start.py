#!/usr/bin/env python3
"""Unified startup script for the purchasing system"""
import os
import sys
import subprocess
import time

def start_backend():
    """Start the Flask backend"""
    os.chdir('backend')
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Initialize database if needed
    if not os.path.exists('instance/purchases_dev.db'):
        print("Initializing database...")
        subprocess.run([sys.executable, 'migrate.py'])
    
    print("Starting backend server...")
    subprocess.Popen([sys.executable, 'run.py'])
    os.chdir('..')

def start_frontend():
    """Start the Angular frontend"""
    os.chdir('frontend')
    if not os.path.exists('node_modules'):
        print("Installing frontend dependencies...")
        subprocess.run(['npm', 'install'])
    
    print("Starting frontend server...")
    subprocess.Popen(['npm', 'start'])
    os.chdir('..')

def main():
    print("🚀 Starting MIT Motorsports Purchasing System...")
    
    # Start backend
    start_backend()
    time.sleep(3)
    
    # Start frontend
    start_frontend()
    
    print("\n✅ System started!")
    print("📊 Backend: http://localhost:5000")
    print("🌐 Frontend: http://localhost:4200")
    print("📖 API Docs: http://localhost:5000/health")
    print("\n👤 Test accounts:")
    print("   requester@mit.edu / password123")
    print("   sublead@mit.edu / password123")
    print("   executive@mit.edu / password123")
    print("   business@mit.edu / password123")

if __name__ == '__main__':
    main()
