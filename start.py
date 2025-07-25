import os
import sys
import subprocess
import time

def start_backend():
    """Start the Flask backend"""
    # Load .env file
    from dotenv import dotenv_values
    env_vars = dotenv_values('.env')
    
    # Create a copy of the current environment and update with .env values
    backend_env = os.environ.copy()
    backend_env.update(env_vars)
    
    os.chdir('backend')
    
    # Initialize database and create test users
    print("Initializing database and creating test users...")
    subprocess.run([sys.executable, 'migrate.py'], env=backend_env, shell=True)
    
    print("Starting backend server...")
    subprocess.Popen([sys.executable, 'run.py'], env=backend_env)
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
    print("Starting MIT Motorsports Purchasing System...")
    
    # Start backend
    start_backend()
    time.sleep(3)
    
    # Start frontend
    start_frontend()
    
    print("\nSystem started!")
    print("Backend: http://localhost:5000")
    print("Frontend: http://localhost:4200")
    print("API Docs: http://localhost:5000/health")
    print("\nTest accounts:")
    print("   requester@mit.edu / password123")
    print("   sublead@mit.edu / password123")
    print("   executive@mit.edu / password123")
    print("   business@mit.edu / password123")

if __name__ == '__main__':
    main()
