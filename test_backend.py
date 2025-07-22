#!/usr/bin/env python3
"""Quick test script for the backend API"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_health():
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_login():
    try:
        data = {'email': 'requester@mit.edu', 'password': 'password123'}
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Login test: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Login test failed: {e}")
        return False

def main():
    print("Testing backend API...")
    
    if not test_health():
        print("❌ Backend is not running. Start with: cd backend && python run.py")
        return
    
    print("✅ Backend is running")
    
    if test_login():
        print("✅ Authentication working")
    else:
        print("❌ Authentication failed - run: flask create-test-users")

if __name__ == '__main__':
    main()
