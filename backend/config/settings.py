import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mit-motorsports-secret-key-2025'
    
    # Database configuration - supports both POSTGRES_* and DB_* variable naming
    @staticmethod
    def get_database_url():
        # Check for DATABASE_URL first (common in production)
        if os.environ.get('DATABASE_URL'):
            return os.environ.get('DATABASE_URL')
        
        # Try POSTGRES_* variables (your current setup)
        postgres_user = os.environ.get('POSTGRES_USER')
        postgres_password = os.environ.get('POSTGRES_PASSWORD')
        postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
        postgres_port = os.environ.get('POSTGRES_PORT', '5432')
        postgres_db = os.environ.get('POSTGRES_DB')
        
        # Try DB_* variables as fallback
        if not postgres_user:
            postgres_user = os.environ.get('DB_USER')
        if not postgres_password:
            postgres_password = os.environ.get('DB_PASSWORD')
        if not postgres_host or postgres_host == 'localhost':
            postgres_host = os.environ.get('DB_HOST', 'localhost')
        if not postgres_port or postgres_port == '5432':
            postgres_port = os.environ.get('DB_PORT', '5432')
        if not postgres_db:
            postgres_db = os.environ.get('DB_NAME')
        
        # If we have postgres credentials, build the URL
        if postgres_user and postgres_password and postgres_db:
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        
        # Fallback to SQLite for development
        return 'sqlite:///mit_motorsports_purchasing.db'
    
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)  # Longer for development
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # CORS configuration
    CORS_ORIGINS = [
        "http://localhost:3000",    # React default
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:4200",    # Angular default
        "http://127.0.0.1:4200"
    ]
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'csv'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Purchasing System specific settings
    APPROVAL_THRESHOLDS = {
        'team_member': 100.00,      # Team members can approve up to $100
        'team_lead': 500.00,        # Team leads can approve up to $500
        'treasurer': 2000.00,       # Treasurer can approve up to $2000
        'faculty_advisor': 10000.00 # Faculty advisor for larger purchases
    }
    
    # Request statuses
    REQUEST_STATUSES = [
        'draft',
        'submitted',
        'pending_approval',
        'approved',
        'ordered',
        'received',
        'rejected',
        'cancelled'
    ]
    
    # Priority levels
    PRIORITY_LEVELS = [
        'low',
        'normal',
        'high',
        'urgent'
    ]
    
    # Categories for purchases
    PURCHASE_CATEGORIES = [
        'electronics',
        'mechanical_parts',
        'materials',
        'tools',
        'safety_equipment',
        'software',
        'services',
        'travel',
        'other'
    ]
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@mit-motorsports.edu'
    
    # Team information
    TEAM_NAME = "MIT Motorsports"
    TEAM_EMAIL = "motorsports@mit.edu"
    CURRENT_SEASON = "2025"
    
    # Budget settings
    DEFAULT_BUDGET_LIMIT = 50000.00  # Default annual budget
    BUDGET_WARNING_THRESHOLD = 0.8   # Warn when 80% of budget is used
    
    # Notification settings
    ENABLE_EMAIL_NOTIFICATIONS = True
    NOTIFICATION_EMAILS = {
        'new_request': True,
        'approval_needed': True,
        'status_change': True,
        'budget_warning': True
    }
    
    # API settings
    API_VERSION = "v1"
    API_TITLE = "MIT Motorsports Purchasing API"
    API_DESCRIPTION = "API for managing purchasing requests and approvals"
    
    # Security settings
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Cache settings
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries in development
    BCRYPT_LOG_ROUNDS = 4   # Faster hashing in development

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False
    ENABLE_EMAIL_NOTIFICATIONS = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/mit_motorsports_purchasing'
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

# Export commonly used configurations
__all__ = ['Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig', 'get_config']