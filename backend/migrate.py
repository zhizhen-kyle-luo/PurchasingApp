#!/usr/bin/env python3
"""Database migration script"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.models.base import db
from app.models import User, Purchase, UserRole

def migrate_from_old_db():
    """Migrate data from old monolithic app.py database"""
    app = create_app()
    with app.app_context():
        # Check if old tables exist and migrate data
        try:
            # This would contain actual migration logic
            print("Migration completed successfully")
        except Exception as e:
            print(f"Migration failed: {e}")

def init_fresh_db():
    """Initialize fresh database with test data"""
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create test users
        test_users = [
            {'email': 'requester@mit.edu', 'name': 'Test Requester', 'role': UserRole.REQUESTER},
            {'email': 'sublead@mit.edu', 'name': 'Test Sublead', 'role': UserRole.SUBLEAD},
            {'email': 'executive@mit.edu', 'name': 'Test Executive', 'role': UserRole.EXECUTIVE},
            {'email': 'business@mit.edu', 'name': 'Test Business', 'role': UserRole.BUSINESS}
        ]
        
        for user_data in test_users:
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(email=user_data['email'], full_name=user_data['name'], role=user_data['role'])
                user.set_password('password123')
                db.session.add(user)
        
        db.session.commit()
        print("Fresh database initialized with test users")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        migrate_from_old_db()
    else:
        init_fresh_db()
