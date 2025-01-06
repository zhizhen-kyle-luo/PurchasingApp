from app import app, db, User, UserRole

def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create test accounts
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
        
        # Create each test account
        for account in test_accounts:
            user = User(
                email=account['email'],
                full_name=account['full_name'],
                role=account['role']
            )
            user.set_password(account['password'])
            db.session.add(user)
            
        db.session.commit()
        print("Database initialized with test accounts!")

if __name__ == '__main__':
    init_db()