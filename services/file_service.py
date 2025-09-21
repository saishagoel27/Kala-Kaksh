import os
import uuid
import shutil
from PIL import Image
from werkzeug.utils import secure_filename
from utils.helpers import allowed_file

class FileService:
    def __init__(self, upload_dir="uploads"):
        self.upload_dir = upload_dir
        self.product_images_dir = os.path.join(upload_dir, "products")
        self.profile_images_dir = os.path.join(upload_dir, "profiles")
        
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary folders for file uploads"""
        os.makedirs(self.product_images_dir, exist_ok=True)
        os.makedirs(self.profile_images_dir, exist_ok=True)
        
        for directory in [self.product_images_dir, self.profile_images_dir]:
            gitkeep = os.path.join(directory, ".gitkeep")
            if not os.path.exists(gitkeep):
                open(gitkeep, 'w').close()
    
    def _generate_unique_filename(self, original_filename):
        """Create unique filename to avoid conflicts"""
        _, ext = os.path.splitext(original_filename)
        
        unique_name = str(uuid.uuid4())
        
        return secure_filename(f"{unique_name}{ext}")
    
    def _resize_image(self, image_path, max_width=800, max_height=600, quality=85):
        """Make images smaller and web-friendly"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                
        except Exception as e:
            print(f"Couldn't resize image {image_path}: {e}")
    
    def upload_product_image(self, file, product_id):
        """Handle product image upload and processing"""
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not allowed_file(file.filename):
                return {'success': False, 'error': 'Only image files allowed (PNG, JPG, JPEG, GIF, WEBP)'}
            
            filename = self._generate_unique_filename(file.filename)
            
            product_dir = os.path.join(self.product_images_dir, product_id)
            os.makedirs(product_dir, exist_ok=True)
            
            file_path = os.path.join(product_dir, filename)
            file.save(file_path)
            
            self._resize_image(file_path)
            
            url_path = f"uploads/products/{product_id}/{filename}"
            
            return {
                'success': True,
                'filename': filename,
                'url': url_path,
                'file_path': file_path
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Upload problem: {str(e)}'}
    
    def upload_profile_image(self, file, artisan_id):
        """Save and optimize artisan profile photos"""
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not allowed_file(file.filename):
                return {'success': False, 'error': 'Only image files allowed'}
            
            filename = self._generate_unique_filename(file.filename)
            file_path = os.path.join(self.profile_images_dir, filename)
            file.save(file_path)
            
            self._resize_image(file_path, max_width=400, max_height=400)
            
            url_path = f"uploads/profiles/{filename}"
            
            return {
                'success': True,
                'filename': filename,
                'url': url_path,
                'file_path': file_path
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def delete_image(self, file_path):
        """Remove an image from disk"""
        try:
            full_path = file_path
            if file_path.startswith('uploads/'):
                full_path = file_path
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
                
            print(f"Can't find {full_path} to delete")
            return False
                
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False
    
    def get_product_images(self, product_id):
        """Get all images for a product"""
        product_dir = os.path.join(self.product_images_dir, product_id)
        
        if not os.path.exists(product_dir):
            return []
        
        images = []
        for filename in os.listdir(product_dir):
            if filename != '.gitkeep' and allowed_file(filename):
                url_path = f"uploads/products/{product_id}/{filename}"
                images.append(url_path)
        
        return images
    
    def cleanup_orphaned_images(self, valid_product_ids):
        """Delete images for products that no longer exist"""
        try:
            for product_dir in os.listdir(self.product_images_dir):
                full_path = os.path.join(self.product_images_dir, product_dir)
                
                if os.path.isdir(full_path) and product_dir not in valid_product_ids:
                    shutil.rmtree(full_path)
                    print(f"Cleaned up images for deleted product: {product_dir}")
                    
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
    
    def get_file_info(self, file_path):
        """Get metadata about an uploaded file"""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                
                return {
                    'exists': True,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                }
            else:
                return {'exists': False}
                
        except Exception as e:
            return {'exists': False, 'error': str(e)}