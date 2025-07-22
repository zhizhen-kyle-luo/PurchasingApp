"""
File handling service
"""
import os
import uuid
from typing import Optional, Dict, Any, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app
from PIL import Image
import mimetypes


class FileService:
    """Service for handling file uploads and management"""
    
    def __init__(self):
        self.upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        self.allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
        self.max_file_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file(self, file: FileStorage) -> Dict[str, Any]:
        """Validate uploaded file"""
        result = {'valid': False, 'message': ''}
        
        if not file or not file.filename:
            result['message'] = 'No file selected'
            return result
        
        if not self.is_allowed_file(file.filename):
            result['message'] = f'File type not allowed. Allowed types: {", ".join(self.allowed_extensions)}'
            return result
        
        # Check file size (if we can get it)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            result['message'] = f'File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB'
            return result
        
        # Validate file content type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type and not self._is_allowed_mime_type(mime_type):
            result['message'] = 'Invalid file content'
            return result
        
        result['valid'] = True
        return result
    
    def save_file(self, file: FileStorage, subfolder: str = '', custom_name: str = None) -> Dict[str, Any]:
        """Save uploaded file with validation"""
        result = {'success': False, 'message': '', 'filename': None, 'filepath': None}
        
        # Validate file
        validation = self.validate_file(file)
        if not validation['valid']:
            result['message'] = validation['message']
            return result
        
        try:
            # Generate secure filename
            if custom_name:
                filename = self._generate_unique_filename(custom_name, file.filename)
            else:
                filename = self._generate_unique_filename(file.filename)
            
            # Create upload directory if it doesn't exist
            upload_path = os.path.join(self.upload_folder, subfolder) if subfolder else self.upload_folder
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)
            
            # Process image if it's an image file
            if self._is_image_file(filename):
                self._process_image(filepath)
            
            result['success'] = True
            result['message'] = 'File uploaded successfully'
            result['filename'] = filename
            result['filepath'] = filepath
            
            current_app.logger.info(f'File saved: {filepath}')
            
        except Exception as e:
            result['message'] = f'Failed to save file: {str(e)}'
            current_app.logger.error(f'File save failed: {str(e)}')
        
        return result
    
    def delete_file(self, filename: str, subfolder: str = '') -> Dict[str, Any]:
        """Delete a file"""
        result = {'success': False, 'message': ''}
        
        try:
            filepath = os.path.join(self.upload_folder, subfolder, filename) if subfolder else \
                      os.path.join(self.upload_folder, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                result['success'] = True
                result['message'] = 'File deleted successfully'
                current_app.logger.info(f'File deleted: {filepath}')
            else:
                result['message'] = 'File not found'
                
        except Exception as e:
            result['message'] = f'Failed to delete file: {str(e)}'
            current_app.logger.error(f'File deletion failed: {str(e)}')
        
        return result
    
    def get_file_info(self, filename: str, subfolder: str = '') -> Dict[str, Any]:
        """Get file information"""
        filepath = os.path.join(self.upload_folder, subfolder, filename) if subfolder else \
                  os.path.join(self.upload_folder, filename)
        
        if not os.path.exists(filepath):
            return {'exists': False}
        
        stat = os.stat(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        
        return {
            'exists': True,
            'filename': filename,
            'filepath': filepath,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'mime_type': mime_type,
            'is_image': self._is_image_file(filename)
        }
    
    def cleanup_orphaned_files(self, referenced_files: list, subfolder: str = '') -> Dict[str, Any]:
        """Clean up files that are no longer referenced"""
        result = {'deleted': 0, 'errors': []}
        
        try:
            upload_path = os.path.join(self.upload_folder, subfolder) if subfolder else self.upload_folder
            
            if not os.path.exists(upload_path):
                return result
            
            for filename in os.listdir(upload_path):
                if filename not in referenced_files:
                    try:
                        filepath = os.path.join(upload_path, filename)
                        os.remove(filepath)
                        result['deleted'] += 1
                        current_app.logger.info(f'Orphaned file deleted: {filepath}')
                    except Exception as e:
                        result['errors'].append(f'Failed to delete {filename}: {str(e)}')
                        
        except Exception as e:
            result['errors'].append(f'Cleanup failed: {str(e)}')
        
        return result
    
    def _generate_unique_filename(self, original_filename: str, fallback_filename: str = None) -> str:
        """Generate a unique filename"""
        filename = secure_filename(original_filename or fallback_filename or 'file')
        
        # Add UUID to ensure uniqueness
        name, ext = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{name}_{unique_id}{ext}"
    
    def _is_allowed_mime_type(self, mime_type: str) -> bool:
        """Check if MIME type is allowed"""
        allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf'
        }
        return mime_type in allowed_mime_types
    
    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        return filename.rsplit('.', 1)[1].lower() in image_extensions
    
    def _process_image(self, filepath: str) -> None:
        """Process uploaded image (resize, optimize)"""
        try:
            with Image.open(filepath) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (1920, 1080)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(filepath, optimize=True, quality=85)
                
        except Exception as e:
            current_app.logger.warning(f'Image processing failed for {filepath}: {str(e)}')
            # Don't fail the upload if image processing fails
    
    def create_thumbnail(self, filepath: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """Create thumbnail for image"""
        if not self._is_image_file(filepath):
            return None
        
        try:
            with Image.open(filepath) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                name, ext = os.path.splitext(filepath)
                thumbnail_path = f"{name}_thumb{ext}"
                
                img.save(thumbnail_path, optimize=True, quality=85)
                return thumbnail_path
                
        except Exception as e:
            current_app.logger.error(f'Thumbnail creation failed: {str(e)}')
            return None
