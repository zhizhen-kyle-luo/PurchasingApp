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
from sqlalchemy import case, or_, and_
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

# Database configuration
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    # PythonAnywhere environment - update to match your actual directory
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kyleluo/instance/purchases.db'
    BASE_URL = 'https://kyleluo.pythonanywhere.com'
    UPLOAD_FOLDER = '/home/kyleluo/static/uploads'  # Update upload folder path
else:
    # Local environment paths remain the same
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "purchases.db")}'
    BASE_URL = 'http://127.0.0.1:5000'
    UPLOAD_FOLDER = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Restore upload folder configuration
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
    
    # Check if user has permission to approve
    if current_user.is_sublead() and order.approval_status == 'Pending Sublead Approval':
        # Check if this sublead was selected for this order
        if current_user.email != order.sublead_email:
            return jsonify({
                'success': False, 
                'error': 'You are not the designated sublead for this order'
            }), 403
            
        order.approval_status = 'Pending Executive Approval'
        # Notify executive for their approval
        send_exec_approval_notification(order)
        # Notify requester of sublead approval
        send_approval_status_notification(order, 'approved by sublead')
        
    elif current_user.is_executive() and order.approval_status == 'Pending Executive Approval':
        # Check if this executive was selected for this order
        if current_user.email != order.exec_email:
            return jsonify({
                'success': False, 
                'error': 'You are not the designated executive for this order'
            }), 403
            
        order.exec_approval_status = 'Approved'
        order.approval_status = 'Fully Approved'
        send_approval_status_notification(order, 'fully approved')
        
    else:
        return jsonify({
            'success': False, 
            'error': 'You do not have permission to approve this order at its current status'
        }), 403
        
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
    exec_email = db.Column(db.String(120))
    exec_approval_status = db.Column(db.String(50), default='Pending')
    arrival_photo = db.Column(db.String(200))
    arrived_at = db.Column(db.DateTime)
    is_resolved = db.Column(db.Boolean, default=False)
    shipped_at = db.Column(db.DateTime)
    sublead_email = db.Column(db.String(120))

# Add the User model before the Purchase model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20))
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    purchases = db.relationship('Purchase', backref='user', lazy=True)

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
                full_name=account['full_name'],
                role=account['role']
            )
            new_user.set_password(account['password'])
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
        sublead_email=sublead_email,  # Store the sublead email
        exec_email=exec_email,  # Store the exec email
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

APPROVED_EMAILS = {
    'requester': [
        'requester@mit.edu',
        'ambecker@mit.edu', 'acdeleon@mit.edu', 'aaronhu@mit.edu', 'aaliu04@mit.edu', 
        'ahindman@mit.edu', 'abimek@mit.edu', 'abrahaml@mit.edu', 'abrianna@mit.edu', 
        'achyuta@mit.edu', 'avining@mit.edu', 'asyordan@mit.edu', 'advikan@mit.edu', 
        'ahmadtak@mit.edu', 'aaurora@mit.edu', 'akivar@mit.edu', 'akshatc@mit.edu', 
        'akap@mit.edu', 'aalahmad@mit.edu', 'alomba@mit.edu', 'alaysia@mit.edu', 
        'amtenshi@mit.edu', 'alec.heif@gmail.com', 'ajr305@mit.edu', 'ale12@mit.edu', 
        'agarbuz@mit.edu', 'abelyan@mit.edu', 'kamin135@mit.edu', 'ayhu@mit.edu', 
        'ayuz@mit.edu', 'alexyxc@mit.edu', 'alex154@mit.edu', 'apmendez@mit.edu', 
        'ashanafi@mit.edu', 'ajg19@mit.edu', 'alexyh@mit.edu', 'warrena@mit.edu', 
        'astuder@mit.edu', 'acbanks@mit.edu', 'huynha@mit.edu', 'aliciar@mit.edu', 
        'alicia.ramirez.2057@gmail.com', 'soong@mit.edu', 'lonz@mit.edu', 'ajmel@mit.edu', 
        'alvinqz@mit.edu', 'ahulver@mit.edu', 'amir_a@mit.edu', 'amiusmmd@mit.edu', 
        'amyjyo@mit.edu', 'anqik@mit.edu', 'anacamba@mit.edu', 'anadalai@mit.edu', 
        'anahi183@mit.edu', 'ananthv@mit.edu', 'ajurs@mit.edu', 'anderjurs@hotmail.com', 
        'andraye@mit.edu', 'aabreu@mit.edu', 'andresjc@mit.edu', 'andrew8@mit.edu', 
        'andyou@mit.edu', 'andyy455@mit.edu', 'amwang28@mit.edu', 'dstaff@mit.edu', 
        'anhdinh@mit.edu', 'anichari@mit.edu', 'anjalina@mit.edu', 'akim05@mit.edu', 
        'annahj@mit.edu', 'ajvega@mit.edu', 'antonio3@mit.edu', 'apmendex@mit.edu', 
        'arianee@mit.edu', 'arthchen@mit.edu', 'arthu@mit.edu', 'aryanj@mit.edu', 
        'paparoa@mit.edu', 'aenglish@mit.edu', 'agallitt@mit.edu', 'ashj126@mit.edu', 
        'aslid@mit.edu', 'atharvj@mit.edu', 'a_pal@mit.edu', 'mide@mit.edu', 
        'barryxu2@mit.edu', 'belindav@mit.edu', 'bemnetaa@mit.edu', 'bxwu@mit.edu', 
        'bljin@mit.edu', 'brupesh@mit.edu', 'boeseany@gmail.com', 'fsdi321@mit.edu', 
        'brayn@mit.edu', 'bvjohn@mit.edu', 'chowb@mit.edu', 'zhang108@mit.edu', 
        'bfors15@mit.edu', 'cai_bell@mit.edu', 'cjh1312@mit.edu', 'ceordone@gmail.com', 
        'cam47@mit.edu', 'osbo@mit.edu', 'carlosgl@mit.edu', 'cgreq114@mit.edu', 
        'carjiang@mit.edu', 'ctucker4@mit.edu', 'cbassett@mit.edu', 'cibanez@mit.edu', 
        'catyao@mit.edu', 'cvorbach@mit.edu', 'chelton@mit.edu', 'chenharp@mit.edu', 
        'cheyenne@mit.edu', 'c_zeng@mit.edu', 'duesselc@mit.edu', 'cpnguyen@mit.edu', 
        'christianapakyen@gmail.com', 'clll@mit.edu', 'keedy@mit.edu', 'chriskc@mit.edu', 
        'chrishc@mit.edu', 'chrisdlr@mit.edu', 'evagora@mit.edu', 'cindybw@mit.edu', 
        'cttewari@mit.edu', 'cojocarugabi31415@gmail.com', 'cguo3@mit.edu', 
        'd.g.lopez101@gmail.com', 'dtbrown@mit.edu', 'dnl_fdz@mit.edu', 'dlobelo@mit.edu', 
        'dwang97@mit.edu', 'dzaiden@mit.edu', 'dmwhite@mit.edu', 'mapleint@mit.edu', 
        'd_akin@mit.edu', 'dglopez@mit.edu', 'dfw@mit.edu', 'davidakinyoyenu@gmail.com', 
        'debbiela@mit.edu', 'lukei@mit.edu', 'derek16@mit.edu', 'dianocly@mit.edu', 
        'dr_orona@mit.edu', 'dcao2028@mit.edu', 'tjokro@mit.edu', 'cechez79@mit.edu', 
        'dynguyen@mit.edu', 'dcryan@mit.edu'
        # ... continuing with all other emails
    ],
    'sublead': [
        'lzz20051017@gmail.com'  # Test sublead
        'nic26@mit.edu'
    ],
    'executive': [
        'zhizhen.luo07@gmail.com',  # Test exec
        'hezpen@mit.edu',
        'alex154@mit.edu',
        'mochan@mit.edu',
        'cttewari@mit.edu',
        'ericz217@mit.edu'
    ],
    'business': [
        'zhizhen@mit.edu'  # Test business
    ]
}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('purchases'))
    
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Check if email is approved in any role
        role = None
        for role_name, emails in APPROVED_EMAILS.items():
            if email in emails:
                role = role_name
                break
                
        if role is None:
            flash('Unapproved email. Please contact Kyle for approval.')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        # Create new user with the correct role
        new_user = User(
            email=email,
            full_name=full_name,
            role=role
        )
        new_user.set_password(password)
        
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
        # Show orders that are fully approved, purchased, or shipped (but not arrived)
        current_orders = Purchase.query.filter(
            and_(
                Purchase.is_deleted == False,
                Purchase.status != 'Arrived',
                or_(
                    Purchase.user_id == current_user.id,
                    Purchase.approval_status == 'Fully Approved',
                    Purchase.status == 'Purchased',
                    Purchase.status == 'Shipped'
                )
            )
        ).order_by(Purchase.purchase_date.desc()).all()
    elif current_user.is_sublead():
        # Show their own orders and orders they need to approve
        current_orders = Purchase.query.filter(
            and_(
                Purchase.is_deleted == False,
                Purchase.status != 'Arrived',
                or_(
                    Purchase.user_id == current_user.id,
                    and_(
                        Purchase.sublead_email == current_user.email,
                        Purchase.approval_status == 'Pending Sublead Approval'
                    )
                )
            )
        ).order_by(Purchase.purchase_date.desc()).all()
    elif current_user.is_executive():
        # Show their own orders and orders they need to approve
        current_orders = Purchase.query.filter(
            and_(
                Purchase.is_deleted == False,
                Purchase.status != 'Arrived',
                or_(
                    Purchase.user_id == current_user.id,
                    and_(
                        Purchase.exec_email == current_user.email,
                        Purchase.approval_status == 'Pending Executive Approval'
                    )
                )
            )
        ).order_by(Purchase.purchase_date.desc()).all()
    else:
        # Regular users only see orders where they are the requester (not arrived)
        current_orders = Purchase.query.filter(
            and_(
                Purchase.requester_email == current_user.email,  # Changed from user_id to requester_email
                Purchase.is_deleted == False,
                Purchase.status != 'Arrived'
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

@app.route('/purchase/<int:purchase_id>/details')
@login_required
def get_purchase_details(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return jsonify({
        'id': purchase.id,
        'item_name': purchase.item_name,
        'vendor_name': purchase.vendor_name,
        'item_link': purchase.item_link,
        'price': purchase.price,
        'shipping_cost': purchase.shipping_cost,
        'quantity': purchase.quantity,
        'subteam': purchase.subteam,
        'subproject': purchase.subproject,
        'purpose': purchase.purpose,
        'notes': purchase.notes,
        'requester_name': purchase.requester_name,
        'requester_email': purchase.requester_email,
        'purchase_date': purchase.purchase_date.strftime('%Y-%m-%d'),
        'approval_status': purchase.approval_status,
        'status': purchase.status,
        'urgency': purchase.urgency,
        'is_deleted': purchase.is_deleted,
        'arrival_photo': purchase.arrival_photo,
        'arrived_at': purchase.arrived_at.isoformat() if purchase.arrived_at else None,
        'is_resolved': purchase.is_resolved,
        'shipped_at': purchase.shipped_at.isoformat() if purchase.shipped_at else None
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
            
            # Use the BASE_URL for the reset link
            reset_url = f"{BASE_URL}{url_for('reset_password', token=token)}"
            msg = Message('Password Reset Request - MIT Motorsports',
                         sender=('MIT Motorsports', 'sclark061951@gmail.com'),
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
    # Check if user is a business account
    if not current_user.is_business():
        return jsonify({'success': False, 'error': 'Only business accounts can update order status'}), 403
        
    purchase = Purchase.query.get_or_404(purchase_id)
    new_status = request.form.get('status')
    
    try:
        if new_status == 'purchased':
            if purchase.approval_status != 'Fully Approved':
                return jsonify({'success': False, 'error': 'Order must be fully approved first'})
            purchase.status = 'Purchased'
            purchase.approval_status = 'Purchased'  # Update approval status too
            
        elif new_status == 'shipped':
            if purchase.status != 'Purchased':
                return jsonify({'success': False, 'error': 'Order must be purchased first'})
            purchase.status = 'Shipped'
            purchase.approval_status = 'Shipped'  # Update approval status too
            purchase.shipped_at = datetime.utcnow()
            
        elif new_status == 'arrived':
            if purchase.status != 'Shipped':
                return jsonify({'success': False, 'error': 'Order must be shipped first'})
            
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
            purchase.approval_status = 'Arrived'  # Update approval status too
            purchase.arrived_at = datetime.utcnow()
            purchase.is_resolved = True
            purchase.is_deleted = True
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_name', methods=['POST'])
@login_required
def update_name():
    data = request.get_json()
    new_name = data.get('name')
    
    if not new_name:
        return jsonify({'success': False, 'error': 'No name provided'})
        
    current_user.full_name = new_name
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/purchase/<int:purchase_id>/delete', methods=['POST'])
@login_required
def delete_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    purchase.is_deleted = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/purchase/<int:purchase_id>/restore', methods=['POST'])
@login_required
def restore_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # If the order was marked as arrived, restore it to shipped state
    if purchase.status == 'Arrived':
        purchase.status = 'Shipped'
        purchase.is_deleted = False
        purchase.is_resolved = False
        purchase.arrived_at = None
        purchase.arrival_photo = None  # Optionally remove the arrival photo
    else:
        # Normal restore for deleted orders
        purchase.is_deleted = False
    
    db.session.commit()
    return jsonify({'success': True})

# Add this at the very end of the file
if __name__ == '__main__':
    with app.app_context():
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
