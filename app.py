# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from enum import Enum 
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import secrets
import logging
from logging.handlers import RotatingFileHandler
from flask_migrate import Migrate
from sqlalchemy import case, or_, and_
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

# Database configuration
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    # PythonAnywhere environment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kyleluo/mysite/instance/purchases.db'
else:
    # Local environment - use absolute path
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "purchases.db")}'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Restore upload folder configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'sclark061951@gmail.com'
app.config['MAIL_PASSWORD'] = 'wcwa mxtt xgfw abol'  # New app password for MIT Motorsports
app.config['MAIL_DEFAULT_SENDER'] = ('MIT Motorsports', 'sclark061951@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True  # Enable debug mode for more detailed logging

# Initialize mail after all configurations
mail = Mail(app)

# Add logging configuration
if not os.path.exists('logs'):
    os.mkdir('logs')
    
file_handler = RotatingFileHandler('logs/password_reset.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Password reset system startup')

def send_approval_notification(order, sublead_email):
    """Send email notification to sublead for approval"""
    if not sublead_email:
        app.logger.error('No sublead email provided for approval notification')
        return
        
    msg = Message('New Order Needs Approval - MIT Motorsports',
                 sender=('MIT Motorsports', 'sclark061951@gmail.com'),
                 recipients=[sublead_email])
    
    msg.body = f"""Hello,

A new order needs your approval:

Item: {order.item_name}
Requester: {order.requester_name}
Total: ${order.price + order.shipping_cost:.2f}
Subteam: {order.subteam}

Please log in to the MY25 system to approve or reject this order.

Best regards,
MIT Motorsports Team"""
    
    try:
        mail.send(msg)
        app.logger.info(f'Approval notification sent to {sublead_email}')
    except Exception as e:
        app.logger.error(f'Failed to send approval notification: {str(e)}')
        raise

def send_approval_status_notification(order, status):
    """Send email notification to requester about approval status"""
    msg = Message(f'Order Status Update - MIT Motorsports',
                 sender=('MIT Motorsports', 'sclark061951@gmail.com'),
                 recipients=[order.requester_email])
    
    status_messages = {
        'approved by sublead': 'Your order has been approved by the sublead and is now awaiting executive approval.',
        'rejected by sublead': 'Your order has been rejected by the sublead.',
        'fully approved': 'Your order has been fully approved by both sublead and executive.',
        'rejected by executive': 'Your order has been rejected by the executive.'
    }
    
    msg.body = f"""Hello {order.requester_name},

{status_messages[status]}

Order Details:
Item: {order.item_name}
Total: ${order.price + order.shipping_cost:.2f}
Subteam: {order.subteam}

{'' if 'rejected' in status else 'You can now proceed with the purchase.'}

Best regards,
MIT Motorsports Team

This is an automated message. Please do not reply to this email."""
    
    mail.send(msg)

def send_exec_approval_notification(order):
    """Send email notification to executive for approval after sublead approves"""
    if not order.exec_email:
        app.logger.error('No executive email provided for approval notification')
        return
        
    msg = Message('New Order Needs Executive Approval - MIT Motorsports',
                 sender=('MIT Motorsports', 'sclark061951@gmail.com'),
                 recipients=[order.exec_email])
    
    msg.body = f"""Hello,

A new order has been approved by the sublead and needs your approval:

Item: {order.item_name}
Requester: {order.requester_name}
Total: ${order.price + order.shipping_cost:.2f}
Subteam: {order.subteam}

Please log in to the MY25 system to approve or reject this order.

Best regards,
MIT Motorsports Team

This is an automated message. Please do not reply to this email."""
    
    try:
        mail.send(msg)
        app.logger.info(f'Executive approval notification sent to {order.exec_email}')
    except Exception as e:
        app.logger.error(f'Failed to send executive approval notification: {str(e)}')
        raise

@app.route('/purchase/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_order(order_id):
    order = Purchase.query.get_or_404(order_id)
    action = request.json.get('action')
    
    if current_user.is_sublead():
        if action == 'approve':
            order.approval_status = 'Pending Executive Approval'
            # Notify executive for their approval
            send_exec_approval_notification(order)
            # Notify requester of sublead approval
            send_approval_status_notification(order, 'approved by sublead')
        elif action == 'reject':
            order.approval_status = 'Rejected by Sublead'
            order.exec_approval_status = 'Cancelled'
            send_approval_status_notification(order, 'rejected by sublead')
    
    elif current_user.is_executive():
        if action == 'approve':
            order.exec_approval_status = 'Approved'
            order.approval_status = 'Fully Approved'
            send_approval_status_notification(order, 'fully approved')
        elif action == 'reject':
            order.exec_approval_status = 'Rejected'
            order.approval_status = 'Rejected by Executive'
            send_approval_status_notification(order, 'rejected by executive')
    
    else:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.commit()
    return jsonify({'success': True})

# Add the Purchase model
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    vendor_name = db.Column(db.String(200), nullable=False)
    item_link = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=1)
    subteam = db.Column(db.String(100), nullable=False)
    subproject = db.Column(db.String(200))
    purpose = db.Column(db.Text)
    notes = db.Column(db.Text)
    requester_name = db.Column(db.String(200), nullable=False)
    requester_email = db.Column(db.String(200), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    approval_status = db.Column(db.String(50), default='Pending Sublead Approval')
    status = db.Column(db.String(50), default='Not Yet Purchased')
    is_deleted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    urgency = db.Column(db.String(50), default='Neither')
    exec_email = db.Column(db.String(200))
    exec_approval_status = db.Column(db.String(50), default='Pending')
    arrival_photo = db.Column(db.String(200))
    arrived_at = db.Column(db.DateTime)
    is_resolved = db.Column(db.Boolean, default=False)
    shipped_at = db.Column(db.DateTime)

# Add the User model before the Purchase model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='member')  # member, sublead, executive, business
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_sublead(self):
        return self.role == 'sublead'
    
    def is_executive(self):
        return self.role == 'executive'
    
    def is_business(self):
        return self.role == 'business'

# Add this after the User model definition
class UserRole(Enum):
    REQUESTER = 'requester'
    SUBLEAD = 'sublead'
    EXECUTIVE = 'executive'
    BUSINESS = 'business'

def init_default_accounts():
    default_accounts = [
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

    for account in default_accounts:
        # Check if user already exists
        if not User.query.filter_by(email=account['email']).first():
            new_user = User(
                email=account['email'],
                password_hash=generate_password_hash(account['password']),
                full_name=account['full_name'],
                role=account['role']
            )
            db.session.add(new_user)
            print(f"Created account for {account['email']} with role {account['role']}")
    
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/purchase/new', methods=['POST'])
@login_required
def create_purchase():
    # Initialize variables
    sublead_email = None
    exec_email = None
    initial_status = 'Pending Sublead Approval'
    exec_approval_status = 'Pending'

    # Handle different user roles
    if current_user.is_executive():
        # Executives don't need approval
        initial_status = 'Fully Approved'
        exec_approval_status = 'Approved'
    elif current_user.is_sublead():
        # Subleads only need executive approval
        exec_email = request.form.get('exec_verifier')
        if not exec_email:
            flash('Please select an executive verifier')
            return redirect(url_for('new_purchase'))
        initial_status = 'Pending Executive Approval'
    else:
        # Regular members need both approvals
        sublead_email = request.form.get('sublead_verifier')
        exec_email = request.form.get('exec_verifier')
        if not sublead_email or not exec_email:
            flash('Please select both a sublead and executive verifier')
            return redirect(url_for('new_purchase'))

    new_purchase = Purchase(
        item_name=request.form.get('item_name'),
        vendor_name=request.form.get('vendor_name'),
        item_link=request.form.get('item_link'),
        price=float(request.form.get('price', 0)),
        shipping_cost=float(request.form.get('shipping_cost', 0)),
        quantity=int(request.form.get('quantity', 1)),
        subteam=request.form.get('subteam'),
        subproject=request.form.get('subproject'),
        purpose=request.form.get('purpose'),
        notes=request.form.get('notes'),
        requester_name=current_user.full_name,
        requester_email=current_user.email,
        user_id=current_user.id,
        urgency=request.form.get('urgency', 'Neither'),
        exec_email=exec_email,
        approval_status=initial_status,
        exec_approval_status=exec_approval_status
    )
    
    try:
        db.session.add(new_purchase)
        db.session.commit()
        
        # Send notifications based on role
        if current_user.is_executive():
            flash('Purchase request created and automatically approved')
        elif current_user.is_sublead():
            send_exec_approval_notification(new_purchase)
            flash('Purchase request created and sent to executive for approval')
        else:
            send_approval_notification(new_purchase, sublead_email)
            flash('Purchase request created and sent to sublead for approval')
            
        return redirect(url_for('purchases'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error creating purchase: {str(e)}')
        flash('An error occurred while creating the purchase request')
        return redirect(url_for('new_purchase'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('purchases'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('purchases'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            return redirect(url_for('purchases'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('purchases'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Validate MIT email
        if not email.endswith('@mit.edu'):
            flash('Please use your MIT email address')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role='member'  # Default role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/purchase/new', methods=['GET'])
@login_required
def new_purchase():
    return render_template('new_purchase.html')

@app.route('/purchases')
@login_required
def purchases():
    # For My Current Orders section
    if current_user.is_business():
        # Show orders that are fully approved or shipped (but not arrived), and their own orders
        current_orders = Purchase.query.filter(
            and_(
                Purchase.is_deleted == False,  # Not deleted
                Purchase.status != 'Arrived',  # Not arrived
                or_(
                    Purchase.user_id == current_user.id,  # Their own orders
                    # Orders that need business attention
                    or_(
                        Purchase.approval_status == 'Fully Approved',
                        Purchase.status == 'Shipped'
                    )
                )
            )
        ).order_by(Purchase.purchase_date.desc()).all()
    else:
        # For other roles, keep existing logic but exclude arrived orders
        current_orders = Purchase.query.filter(
            and_(
                Purchase.user_id == current_user.id,
                Purchase.is_deleted == False,
                Purchase.status != 'Arrived'  # Exclude arrived orders
            )
        ).order_by(Purchase.purchase_date.desc()).all()

    # All Current Orders section - show all non-deleted and non-arrived orders
    all_current_orders = Purchase.query.filter(
        and_(
            Purchase.is_deleted == False,
            Purchase.status != 'Arrived'  # Exclude arrived orders
        )
    ).order_by(Purchase.purchase_date.desc()).all()
    
    # Previous Orders section - show all deleted OR arrived orders
    previous_orders = Purchase.query.filter(
        or_(
            Purchase.is_deleted == True,
            Purchase.status == 'Arrived'
        )
    ).order_by(Purchase.purchase_date.desc()).all()
    
    return render_template('purchases.html',
                         current_orders=current_orders,
                         all_current_orders=all_current_orders,
                         previous_orders=previous_orders)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/order/<int:order_id>/details')
@login_required
def get_order_details(order_id):
    order = Purchase.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'item_name': order.item_name,
        'vendor_name': order.vendor_name,
        'item_link': order.item_link,
        'price': order.price,
        'shipping_cost': order.shipping_cost,
        'quantity': order.quantity,
        'subteam': order.subteam,
        'subproject': order.subproject,
        'purpose': order.purpose,
        'notes': order.notes,
        'requester_name': order.requester_name,
        'requester_email': order.requester_email,
        'purchase_date': order.purchase_date.strftime('%Y-%m-%d'),
        'approval_status': order.approval_status,
        'status': order.status,
        'urgency': order.urgency,
        'is_deleted': order.is_deleted,
        'arrival_photo': order.arrival_photo,
        'arrived_at': order.arrived_at.isoformat() if order.arrived_at else None,
        'is_resolved': order.is_resolved,
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None
    })

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send reset email
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request - MIT Motorsports',
                         sender=('MIT Motorsports', 'sclark061951@gmail.com'),  # Display name will show as "MIT Motorsports"
                         recipients=[email])
            
            # Simple text email with the requested format
            msg.body = f"""Hello {user.full_name},

You have requested to reset your password for your MIT Motorsports account.

To reset your password, please click on the following link:
{reset_url}

Note: This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email and ensure your account is secure.

Best regards,
MIT Motorsports Team

This is an automated message. Please do not reply to this email."""
            
            mail.send(msg)
            
            flash('Password reset instructions sent to your email')
            return redirect(url_for('login'))
        
        flash('Email address not found')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('reset_password.html')
        
        user.password_hash = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Your password has been reset successfully')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/purchase/<int:purchase_id>/update_status', methods=['POST'])
@login_required
def update_purchase_status(purchase_id):
    if not current_user.is_business():
        return jsonify({'success': False, 'error': 'Unauthorized'})
        
    purchase = Purchase.query.get_or_404(purchase_id)
    new_status = request.form.get('status')
    
    try:
        if new_status == 'shipped':
            if purchase.approval_status != 'Fully Approved':
                return jsonify({'success': False, 'error': 'Order must be fully approved first'})
            purchase.status = 'Shipped'
            purchase.shipped_at = datetime.utcnow()
            
        elif new_status == 'arrived':
            if purchase.status != 'Shipped':
                return jsonify({'success': False, 'error': 'Order must be shipped first'})
            
            # Handle photo upload
            if 'photo' not in request.files:
                return jsonify({'success': False, 'error': 'No photo provided'})
                
            photo = request.files['photo']
            if photo.filename == '':
                return jsonify({'success': False, 'error': 'No photo selected'})
                
            if photo and allowed_file(photo.filename):
                filename = secure_filename(f"arrival_{purchase_id}_{photo.filename}")
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                purchase.arrival_photo = filename
                
            purchase.status = 'Arrived'
            purchase.arrived_at = datetime.utcnow()
            purchase.is_resolved = True  # Mark as resolved when arrived
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Add this at the very end of the file
if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create test accounts using the UserRole enum
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
        
        for account in test_accounts:
            # Check if user already exists
            existing_user = User.query.filter_by(email=account['email']).first()
            if not existing_user:
                user = User(
                    email=account['email'],
                    full_name=account['full_name'],
                    role=account['role']
                )
                user.set_password(account['password'])
                db.session.add(user)
        
        try:
            db.session.commit()
            print("Test accounts initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing test accounts: {str(e)}")
        
    app.run(debug=True)

# Add this near the top of app.py, after creating the db
migrate = Migrate(app, db)
