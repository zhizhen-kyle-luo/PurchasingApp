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

@app.cli.command()
@with_appcontext
def init_db():
    """Initialize the database"""
    db.create_all()
    print("✅ Database tables created!")

@app.cli.command()
@with_appcontext
def create_test_users():
    """Create test users for development"""
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
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            print(f"⚠️  User {user_data['email']} already exists")
            continue
            
        # Create new user
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

@app.cli.command()
@with_appcontext
def reset_db():
    """Reset the database (drop and recreate all tables)"""
    db.drop_all()
    db.create_all()
    print("✅ Database reset complete!")

if __name__ == '__main__':
    # Initialize database and create test users on first run
    with app.app_context():
        db.create_all()
        
        # Check if any users exist
        user_count = User.query.count()
        if user_count == 0:
            print("🔧 No users found, creating test users...")
            # Create test users programmatically
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
                print("✅ Test users created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating users: {e}")
        else:
            print(f"✅ Database already has {user_count} users")
    
    print("🚀 Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
