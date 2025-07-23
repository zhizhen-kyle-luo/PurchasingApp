#!/usr/bin/env python3
"""
Database migration and initialization script
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.base import db
from app.models import User, UserRole

def init_database():
    """Initialize the database with tables and test users"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("🔧 Creating database tables...")
        db.create_all()
        print("✅ Database tables created!")
        
        # Check if users already exist
        user_count = User.query.count()
        if user_count > 0:
            print(f"✅ Database already has {user_count} users")
            return
        
        # Create test users
        print("🔧 Creating test users...")
        test_users = [
            {
                'email': 'requester@mit.edu',
                'password': 'password123',
                'first_name': 'Test',
                'last_name': 'Requester',
                'role': UserRole.REQUESTER
            },
            {
                'email': 'sublead@mit.edu',
                'password': 'password123',
                'first_name': 'Test',
                'last_name': 'Sublead',
                'role': UserRole.SUBLEAD
            },
            {
                'email': 'executive@mit.edu',
                'password': 'password123',
                'first_name': 'Test',
                'last_name': 'Executive',
                'role': UserRole.EXECUTIVE
            },
            {
                'email': 'business@mit.edu',
                'password': 'password123',
                'first_name': 'Test',
                'last_name': 'Business',
                'role': UserRole.BUSINESS
            }
        ]
        
        for user_data in test_users:
            user = User(
                email=user_data['email'],
                full_name=f"{user_data['first_name']} {user_data['last_name']}",
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"✅ Created user: {user_data['email']}")
        
        try:
            db.session.commit()
            print("✅ All test users created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating users: {e}")
            raise

if __name__ == '__main__':
    init_database()
