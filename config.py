import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kala-kaksh-dev-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    DATA_DIR = 'data'
    ARTISANS_FILE = os.path.join(DATA_DIR, 'artisans.json')
    PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', 'kala-kaksh-hackathon')
    GOOGLE_CLOUD_BUCKET = os.environ.get('GOOGLE_CLOUD_BUCKET', 'kala-kaksh-images')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    USE_GOOGLE_CLOUD = os.environ.get('USE_GOOGLE_CLOUD', 'False').lower() == 'true'
    
    VERSION = '1.0.0'
    APP_NAME = 'KALA KAKSH'
    
    @staticmethod
    def init_app(app):
        pass