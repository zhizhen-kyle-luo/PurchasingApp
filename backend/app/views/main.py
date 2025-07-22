"""
Main routes for serving the Angular frontend and basic pages
"""
from flask import Blueprint, render_template, send_from_directory, current_app
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the Angular frontend"""
    # In production, this would serve the built Angular app
    # For now, we'll serve a simple index page
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard route - will be handled by Angular"""
    return render_template('index.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'purchasing-app-backend'}


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    return send_from_directory(upload_folder, filename)
