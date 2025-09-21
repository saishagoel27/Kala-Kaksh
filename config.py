import os
from dotenv import load_dotenv

# Loading vars from .env file
load_dotenv()

class Config:
    # Core settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kala-kaksh-dev-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File handling - 16MB should be plenty for most images
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'
    
    # Image types 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # store data as JSON files locally
    DATA_DIR = 'data'
    ARTISANS_FILE = os.path.join(DATA_DIR, 'artisans.json')
    PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
    
    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', 'kala-kaksh-demo')
    GOOGLE_CLOUD_BUCKET = os.environ.get('GOOGLE_CLOUD_BUCKET', 'kala-kaksh-uploads')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    USE_GOOGLE_CLOUD = os.environ.get('USE_GOOGLE_CLOUD', 'False').lower() == 'true'
    
    # App versioning
    VERSION = '1.0.0'
    APP_NAME = 'KALA KAKSH'
    
    @staticmethod
    def init_app(app):
        pass