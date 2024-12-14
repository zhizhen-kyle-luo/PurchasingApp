# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from enum import Enum 
from datetime import datetime
import os
from werkzeug.utils import secure_filename

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

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    #split by . and look at what the file is allowed type
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PurchaseStatus(Enum):
    PENDING = "Not Yet Shipped"
    SHIPPED = "Shipped"
    DELIVERED = "Arrived"

class PurchaseApprovalStatus(Enum):
    PENDING = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class UserRole(Enum):
    REQUESTER = "requester"
    EXECUTIVE = "executive"
    BUSINESS = "business"

# Approved emails list
APPROVED_EMAILS = {
    'requester@mit.edu': UserRole.REQUESTER,
    'business@mit.edu': UserRole.BUSINESS,
    'exec@mit.edu': UserRole.EXECUTIVE,
    
    'zhizhen@mit.edu': UserRole.BUSINESS,
    'katecar@mit.edu': UserRole.BUSINESS,
    'vjhaveri@mit.edu': UserRole.BUSINESS,
    'ktruong4@mit.edu': UserRole.BUSINESS,
    
    'ambecker@mit.edu': UserRole.REQUESTER,
    'akshatc@mit.edu': UserRole.REQUESTER,
    'ayhu@mit.edu': UserRole.REQUESTER,
    'alex154@mit.edu': UserRole.REQUESTER,
    'apmendez@mit.edu': UserRole.REQUESTER,
    'astuder@mit.edu': UserRole.REQUESTER,
    'lonz@mit.edu': UserRole.REQUESTER,
    'amir_a@mit.edu': UserRole.REQUESTER,
    'amyjyo@mit.edu': UserRole.REQUESTER,
    'aabreu@mit.edu': UserRole.REQUESTER,
    'amwang28@mit.edu': UserRole.REQUESTER,
    'anhdinh@mit.edu': UserRole.REQUESTER,
    'arthchen@mit.edu': UserRole.REQUESTER,
    'aenglish@mit.edu': UserRole.REQUESTER,
    'bfors15@mit.edu': UserRole.REQUESTER,
    'cai_bell@mit.edu': UserRole.REQUESTER,
    'chenharp@mit.edu': UserRole.REQUESTER,
    'cttewari@mit.edu': UserRole.REQUESTER,
    'd_akin@mit.edu': UserRole.REQUESTER,
    'dglopez@mit.edu': UserRole.REQUESTER,
    'derek16@mit.edu': UserRole.REQUESTER,
    'dcao2028@mit.edu': UserRole.REQUESTER,
    'tjokro@mit.edu': UserRole.REQUESTER,
    'metalor@mit.edu': UserRole.REQUESTER,
    'egoncha@mit.edu': UserRole.REQUESTER,
    'ericz217@mit.edu': UserRole.REQUESTER,
    'faris@mit.edu': UserRole.REQUESTER,
    'fdma2405@mit.edu': UserRole.REQUESTER,
    'gblosen@mit.edu': UserRole.REQUESTER,
    'gloriazh@mit.edu': UserRole.REQUESTER,
    'heinevdw@mit.edu': UserRole.REQUESTER,
    'hezpen@mit.edu': UserRole.REQUESTER,
    'ifrankel@mit.edu': UserRole.REQUESTER,
    'iav1305@mit.edu': UserRole.REQUESTER,
    'jchen609@mit.edu': UserRole.REQUESTER,
    'johnpeng@mit.edu': UserRole.REQUESTER,
    'jmei0311@mit.edu': UserRole.REQUESTER,
    'kadams@mit.edu': UserRole.REQUESTER,
    'katyan@mit.edu': UserRole.REQUESTER,
    'keijii@mit.edu': UserRole.REQUESTER,
    'klogan@mit.edu': UserRole.REQUESTER,
    'lroman10@mit.edu': UserRole.REQUESTER,
    'turino14@mit.edu': UserRole.REQUESTER,
    'ls0955@mit.edu': UserRole.REQUESTER,
    'mhliu@mit.edu': UserRole.REQUESTER,
    'maxmasri@mit.edu': UserRole.REQUESTER,
    'megangs@mit.edu': UserRole.REQUESTER,
    'li_me@mit.edu': UserRole.REQUESTER,
    'mialuna@mit.edu': UserRole.REQUESTER,
    'mtala@mit.edu': UserRole.REQUESTER,
    'mochan@mit.edu': UserRole.REQUESTER,
    'nerwong@mit.edu': UserRole.REQUESTER,
    'nevint@mit.edu': UserRole.REQUESTER,
    'nic26@mit.edu': UserRole.REQUESTER,
    'nicolems@mit.edu': UserRole.REQUESTER,
    'nidhirn@mit.edu': UserRole.REQUESTER,
    'neuvrard@mit.edu': UserRole.REQUESTER,
    'nkothnur@mit.edu': UserRole.REQUESTER,
    'ojasg@mit.edu': UserRole.REQUESTER,
    'orchen@mit.edu': UserRole.REQUESTER,
    'osampson@mit.edu': UserRole.REQUESTER,
    'ocerv6@mit.edu': UserRole.REQUESTER,
    'pbala@mit.edu': UserRole.REQUESTER,
    'kpriyank@mit.edu': UserRole.REQUESTER,
    'rcm17@mit.edu': UserRole.REQUESTER,
    'rakibul@mit.edu': UserRole.REQUESTER,
    'r_soto@mit.edu': UserRole.REQUESTER,
    'rzheng@mit.edu': UserRole.REQUESTER,
    'rengz@mit.edu': UserRole.REQUESTER,
    'ericjzou@mit.edu': UserRole.REQUESTER,
    'rsgriff@mit.edu': UserRole.REQUESTER,
    'rumilee@mit.edu': UserRole.REQUESTER,
    'swhuels@mit.edu': UserRole.REQUESTER,
    'skn@mit.edu': UserRole.REQUESTER,
    'scoston@mit.edu': UserRole.REQUESTER,
    'seanboe@mit.edu': UserRole.REQUESTER,
    'roboseb@mit.edu': UserRole.REQUESTER,
    'selinna@mit.edu': UserRole.REQUESTER,
    'sykang06@mit.edu': UserRole.REQUESTER,
    'stasya@mit.edu': UserRole.REQUESTER,
    'tlangley@mit.edu': UserRole.REQUESTER,
    'vednaik@mit.edu': UserRole.REQUESTER,
    'vincentx@mit.edu': UserRole.REQUESTER,
    'vbofill@mit.edu': UserRole.REQUESTER,
    'wasp_e@mit.edu': UserRole.REQUESTER,
    'wenyuh@mit.edu': UserRole.REQUESTER,
    'yugap@mit.edu': UserRole.REQUESTER,
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    purchases = db.relationship('Purchase', 
                              foreign_keys='Purchase.user_id',
                              backref='user', 
                              lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_executive(self):
        return self.role == UserRole.EXECUTIVE.value

    def is_business(self):
        return self.role == UserRole.BUSINESS.value

    def is_requester(self):
        return self.role == UserRole.REQUESTER.value

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(500), nullable=False)
    item_link = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    purpose = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float)
    exec_verifier = db.Column(db.String(100), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    subteam = db.Column(db.String(100), nullable=False)
    subproject = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=PurchaseStatus.PENDING.value)
    tracking_number = db.Column(db.String(100))
    shipping_confirmation_email = db.Column(db.String(200))
    arrival_date = db.Column(db.DateTime)
    approval_status = db.Column(db.String(20), nullable=False, default=PurchaseApprovalStatus.PENDING.value)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_date = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    image_filename = db.Column(db.String(300))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_mit_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@mit\.edu$', email))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not is_mit_email(email):
            flash('Please use an MIT email address.')
            return redirect(url_for('register'))
            
        if email not in APPROVED_EMAILS:
            flash('This email is not authorized to register.')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
            
        user = User(
            email=email,
            role=APPROVED_EMAILS[email].value
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/purchase/new', methods=['GET', 'POST'])
@login_required
def new_purchase():
    if request.method == 'POST':
        try:
            purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
            purchase = Purchase(
                user_id=current_user.id,
                purchase_date=purchase_date,
                urgency=request.form['urgency'],
                vendor_name=request.form['vendor_name'],
                item_name=request.form['item_name'],
                item_link=request.form['item_link'],
                quantity=int(request.form['quantity']),
                notes=request.form['notes'],
                purpose=request.form['purpose'],
                price=float(request.form['price']),
                shipping_cost=float(request.form['shipping_cost']) if request.form['shipping_cost'] else None,
                exec_verifier=request.form.get('exec_verifier') if current_user.is_requester() else 'N/A',
                requester_name=request.form['requester_name'],
                subteam=request.form['subteam'],
                subproject=request.form['subproject']
            )
            
            # Auto-approve if user is executive or business
            if current_user.is_executive() or current_user.is_business():
                purchase.approval_status = PurchaseApprovalStatus.APPROVED.value
                purchase.approved_by = current_user.id
                purchase.approval_date = datetime.utcnow()
            
            db.session.add(purchase)
            db.session.commit()
            flash('Purchase request submitted successfully!')
            return redirect(url_for('purchases'))
        except ValueError as e:
            flash(f'Error in form submission: {str(e)}')
            return redirect(url_for('new_purchase'))
    return render_template('new_purchase.html')

@app.route('/purchases')
@login_required
def purchases():
    # Get user's purchases
    my_purchases = Purchase.query.filter_by(user_id=current_user.id)\
        .order_by(Purchase.urgency.desc(), Purchase.purchase_date.desc()).all()
    
    # Get all purchases based on role
    if current_user.is_business():
        # Business can see and edit all purchases
        all_purchases = Purchase.query\
            .order_by(Purchase.urgency.desc(), Purchase.purchase_date.desc()).all()
    elif current_user.is_executive():
        # Executives see all purchases but can only edit their own
        all_purchases = Purchase.query\
            .order_by(Purchase.urgency.desc(), Purchase.purchase_date.desc()).all()
    else:
        # Requesters see all purchases but can only edit their own
        all_purchases = Purchase.query\
            .order_by(Purchase.urgency.desc(), Purchase.purchase_date.desc()).all()
    
    return render_template('purchases.html', 
                         my_purchases=my_purchases,
                         all_purchases=all_purchases,
                         is_business=current_user.is_business(),
                         is_executive=current_user.is_executive(),
                         is_requester=current_user.is_requester())

@app.route('/purchase/<int:purchase_id>/update_status', methods=['POST'])
@login_required
def update_status(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Updated permissions: business can edit any order, executives can edit any order
    if not (current_user.is_business() or current_user.is_executive() or purchase.user_id == current_user.id):
        flash('Unauthorized access')
        return redirect(url_for('purchases'))
    
    new_status = request.form['status']
    tracking_number = request.form.get('tracking_number')
    shipping_confirmation = request.form.get('shipping_confirmation_email')
    arrival_date_str = request.form.get('arrival_date')
    
    # Validate required fields for shipped status
    if new_status == PurchaseStatus.SHIPPED.value:
        if not tracking_number or not shipping_confirmation:
            flash('Tracking number and shipping confirmation are required for shipped status')
            return redirect(url_for('purchases'))
    
    # Validate required fields for delivered status
    if new_status == PurchaseStatus.DELIVERED.value:
        if not arrival_date_str:
            flash('Arrival date is required for delivered status')
            return redirect(url_for('purchases'))
        try:
            arrival_date = datetime.strptime(arrival_date_str, '%Y-%m-%d')
            purchase.arrival_date = arrival_date
        except ValueError:
            flash('Invalid arrival date format')
            return redirect(url_for('purchases'))
    
    purchase.status = new_status
    purchase.tracking_number = tracking_number
    purchase.shipping_confirmation_email = shipping_confirmation
    db.session.commit()
    
    flash('Purchase status updated successfully')
    return redirect(url_for('purchases'))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('purchases'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('purchases'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/purchase/<int:purchase_id>/approve', methods=['POST'])
@login_required
def approve_purchase(purchase_id):
    if not (current_user.is_executive() or current_user.is_business()):
        flash('Unauthorized access')
        return redirect(url_for('purchases'))
        
    purchase = Purchase.query.get_or_404(purchase_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        purchase.approval_status = PurchaseApprovalStatus.APPROVED.value
    elif action == 'reject':
        purchase.approval_status = PurchaseApprovalStatus.REJECTED.value
    else:
        flash('Invalid action')
        return redirect(url_for('purchases'))
        
    purchase.approved_by = current_user.id
    purchase.approval_date = datetime.utcnow()
    purchase.approval_notes = notes
    db.session.commit()
    
    flash(f'Purchase request {action}d successfully')
    return redirect(url_for('purchases'))

@app.route('/purchase/<int:purchase_id>/update_admin', methods=['POST'])
@login_required
def update_admin_notes(purchase_id):
    if not (current_user.is_executive() or current_user.is_business()):
        flash('Unauthorized access')
        return redirect(url_for('purchases'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Update notes
    if 'admin_notes' in request.form:
        purchase.admin_notes = request.form['admin_notes']
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{purchase_id}_{file.filename}")
            
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            purchase.image_filename = filename
    
    db.session.commit()
    flash('Purchase details updated successfully')
    return redirect(url_for('purchases'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()