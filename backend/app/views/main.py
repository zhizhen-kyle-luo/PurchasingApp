"""
Main routes for serving the Angular frontend and basic pages
"""
from flask import Blueprint, render_template, send_from_directory, current_app
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the Angular frontend"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MIT Motorsports Purchasing System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; margin-bottom: 30px; }
            .status { background: #e0f2fe; padding: 20px; border-radius: 6px; margin: 20px 0; }
            .endpoints { background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0; }
            .endpoint { margin: 10px 0; font-family: monospace; }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏎️ MIT Motorsports Purchasing System</h1>
            <div class="status">
                <h3>✅ Backend Server Running</h3>
                <p>The Flask backend is running successfully on port 5000.</p>
            </div>
            
            <div class="endpoints">
                <h3>Available Endpoints:</h3>
                <div class="endpoint">🔍 <a href="/health">GET /health</a> - Health check</div>
                <div class="endpoint">🔐 <a href="/auth/login">POST /auth/login</a> - User login</div>
                <div class="endpoint">📝 <a href="/auth/register">POST /auth/register</a> - User registration</div>
                <div class="endpoint">🛒 <a href="/api/purchases">GET /api/purchases</a> - Get purchases</div>
                <div class="endpoint">➕ <a href="/api/purchases">POST /api/purchases</a> - Create purchase</div>
            </div>
            
            <div class="status">
                <h3>🚀 Getting Started</h3>
                <p>1. Start the Angular frontend: <code>cd frontend && npm start</code></p>
                <p>2. Access the application at: <a href="http://localhost:4200">http://localhost:4200</a></p>
                <p>3. Use test accounts:</p>
                <ul>
                    <li><strong>requester@mit.edu</strong> / password123</li>
                    <li><strong>sublead@mit.edu</strong> / password123</li>
                    <li><strong>executive@mit.edu</strong> / password123</li>
                    <li><strong>business@mit.edu</strong> / password123</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard route - will be handled by Angular"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - MIT Motorsports</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; }
            .message { background: #fff3cd; padding: 20px; border-radius: 6px; margin: 20px 0; }
            a { color: #2563eb; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏎️ MIT Motorsports Dashboard</h1>
            <div class="message">
                <p>This is the backend server. Please access the full application through the Angular frontend.</p>
                <p><a href="http://localhost:4200">→ Go to Frontend Application</a></p>
            </div>
        </div>
    </body>
    </html>
    '''


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'purchasing-app-backend'}


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    return send_from_directory(upload_folder, filename)
