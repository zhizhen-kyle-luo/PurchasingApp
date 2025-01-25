from app import app, db, User, UserRole

def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Core test accounts only
        test_accounts = [
            {
                'email': 'requester@mit.edu',
                'full_name': 'Requester',
                'role': UserRole.REQUESTER.value,
                'password': '1'
            },
            {
                'email': 'lzz20051017@gmail.com',
                'full_name': 'Sublead',
                'role': UserRole.SUBLEAD.value,
                'password': '1'
            },
            {
                'email': 'zhizhen.luo07@gmail.com',
                'full_name': 'Exec',
                'role': UserRole.EXECUTIVE.value,
                'password': '1'
            },
            {
                'email': 'zhizhen@mit.edu',
                'full_name': 'Business',
                'role': UserRole.BUSINESS.value,
                'password': '1'
            }
        ]
        
        # Create each account
        for account in test_accounts:
            # Check if user already exists
            existing_user = User.query.filter_by(email=account['email'].lower()).first()
            if not existing_user:
                user = User(
                    email=account['email'].lower(),
                    full_name=account['full_name'],
                    role=account['role']
                )
                user.set_password(account['password'])
                db.session.add(user)
                print(f"Adding user: {account['email']}")
            else:
                print(f"Skipping existing user: {account['email']}")
            
        try:
            db.session.commit()
            print("Database initialized with all accounts successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing accounts: {str(e)}")

if __name__ == '__main__':
    init_db()