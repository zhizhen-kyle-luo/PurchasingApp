"""
Application entry point
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))
from flask.cli import with_appcontext
import click

from app import create_app
from app.models.base import db
from app.models import User, UserRole


app = create_app()


@app.cli.command()
@with_appcontext
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
@with_appcontext
def create_test_users():
    """Create test users for development"""
    test_users = [
        {
            'email': 'requester@mit.edu',
            'full_name': 'Test Requester',
            'role': UserRole.REQUESTER,
            'password': 'password123'
        },
        {
            'email': 'sublead@mit.edu',
            'full_name': 'Test Sublead',
            'role': UserRole.SUBLEAD,
            'password': 'password123'
        },
        {
            'email': 'executive@mit.edu',
            'full_name': 'Test Executive',
            'role': UserRole.EXECUTIVE,
            'password': 'password123'
        },
        {
            'email': 'business@mit.edu',
            'full_name': 'Test Business',
            'role': UserRole.BUSINESS,
            'password': 'password123'
        }
    ]
    
    for user_data in test_users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")
    
    db.session.commit()
    print("Test users created!")


@app.cli.command()
@with_appcontext
def reset_db():
    """Reset the database (drop and recreate all tables)"""
    db.drop_all()
    db.create_all()
    print("Database reset!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
