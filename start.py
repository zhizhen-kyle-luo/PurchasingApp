import os
import sys
import subprocess
import time

def start_backend():
    """Start the Flask backend"""
    os.chdir('backend')
    
    # Initialize database and create test users
    print("Initializing database...")
    subprocess.run(['flask', 'init_db'], shell=True)
    print("Creating test users...")
    subprocess.run(['flask', 'create_test_users'], shell=True)
    
    print("Starting backend server...")
    subprocess.Popen([sys.executable, 'run.py'])
    os.chdir('..')

def start_frontend():
    """Start the Angular frontend"""
    os.chdir('frontend')
    if not os.path.exists('node_modules'):
        print("Installing frontend dependencies...")
        subprocess.run(['npm.cmd', 'install'], shell=True)
    
    print("Starting frontend server...")
    subprocess.Popen(['npm.cmd', 'start'], shell=True)
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
