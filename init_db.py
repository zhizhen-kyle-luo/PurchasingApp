from app import app, db, User, Purchase
import os

def init_database():
    with app.app_context():
        # Create directories if they don't exist
        os.makedirs('instance', exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)
        
        # Initialize database
        db.drop_all()
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()