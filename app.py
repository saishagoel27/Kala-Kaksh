from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from models.artisan import Artisan
from models.product import Product
from services.data_service import DataService 
from services.file_service import FileService
from config import Config
from services.google_cloud_service import GoogleCloudService


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  

# Services
data = DataService()  
files = FileService() 
google_service = GoogleCloudService()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def index():
    return send_from_directory('templates', 'seller_upload.html')

@app.route('/seller-upload')
def seller_upload():
    return send_from_directory('templates', 'seller_upload.html')

# API routes
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'KALA KAKSH Backend is running',
        'version': '1.0.0'
    })

@app.route('/api/dashboard')
def get_dashboard_stats():
    try:
        return jsonify({
            'success': True,
            'data': data.get_dashboard_stats()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Artisan endpoints
@app.route('/api/artisans')
def get_artisans():
    craft = request.args.get('craft_type') 
    verified = request.args.get('verified') == 'true'
    
    try:
        all_artisans = data.get_all_artisans()
        
        # Apply filters if needed
        result = all_artisans
        if craft:
            result = [a for a in result if a.craft_type.lower() == craft.lower()]
        if verified:
            result = [a for a in result if a.verified]
        
        # Return response
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in result],
            'count': len(result)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/artisans/<artisan_id>')
def get_artisan(artisan_id):
    try:
        artisan = data.get_artisan_by_id(artisan_id)
        if not artisan:
            return jsonify({'success': False, 'error': 'Artisan not found'}), 404
            
        return jsonify({'success': True, 'data': artisan.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/artisans', methods=['POST'])
def create_artisan():
    try:
        # Get request data
        req = request.json
        if not req:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        # Required fields
        required = ['name', 'email', 'phone', 'craft_type', 'location']
        for field in required:
            if field not in req:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if data.get_artisan_by_email(req['email']):
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Create artisan object
        artisan = Artisan(
            name=req['name'],
            email=req['email'],
            phone=req['phone'],
            craft_type=req['craft_type'],
            location=req['location'],
            bio=req.get('bio'),
            experience_years=req.get('experience_years', 0)
        )
        
        data.create_artisan(artisan)
        
        return jsonify({'success': True, 'data': artisan.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/artisans/<artisan_id>', methods=['PUT'])
def update_artisan(artisan_id):
    try:
        # Get existing artisan
        artisan = data.get_artisan_by_id(artisan_id)
        if not artisan:
            return jsonify({'success': False, 'error': 'Artisan not found'}), 404
        
        # Get request data
        req = request.json
        if not req:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in req:
            artisan.name = req['name']
        if 'phone' in req:
            artisan.phone = req['phone']
        if 'craft_type' in req:
            artisan.craft_type = req['craft_type']
        if 'location' in req:
            artisan.location = req['location']
        if 'bio' in req:
            artisan.bio = req['bio']
        if 'experience_years' in req:
            artisan.experience_years = int(req['experience_years'])
        if 'verified' in req:
            artisan.verified = bool(req['verified'])
        if 'status' in req:
            artisan.status = req['status']
        
        # Update in "database"
        updated = data.update_artisan(artisan)
        
        return jsonify({'success': True, 'data': updated.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/artisans/<artisan_id>/profile-image', methods=['POST'])
def upload_profile_image(artisan_id):
    try:
        # Check if artisan exists
        artisan = data.get_artisan_by_id(artisan_id)
        if not artisan:
            return jsonify({'success': False, 'error': 'Artisan not found'}), 404
        
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
            
        file = request.files['image']
        
        # Upload and process image
        result = files.upload_profile_image(file, artisan_id)
        
        if not result['success']:
            return jsonify(result), 400
            
        # Update artisan with new image URL
        artisan.profile_image = result['url']
        data.update_artisan(artisan)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Product endpoints
@app.route('/api/products')
def get_products():
    try:
        # Get filter params
        category = request.args.get('category')
        artisan_id = request.args.get('artisan_id')
        search = request.args.get('search')
        featured = request.args.get('featured') == 'true'
        status = request.args.get('status', 'active')
        
        # Get products based on primary filter
        if search:
            products = data.search_products(search)
        elif category:
            products = data.get_products_by_category(category)
        elif artisan_id:
            products = data.get_products_by_artisan(artisan_id)
        else:
            products = data.get_all_products()
        
        # Apply secondary filters
        if featured:
            products = [p for p in products if p.featured]
        
        if status != 'all':
            products = [p for p in products if p.status == status]
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<product_id>')
def get_product(product_id):
    try:
        product = data.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
            
        return jsonify({'success': True, 'data': product.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        # Get request data
        req = request.json
        if not req:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        # Check required fields
        required = ['artisan_id', 'name', 'description', 'price', 'category']
        for field in required:
            if field not in req:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check if artisan exists
        if not data.get_artisan_by_id(req['artisan_id']):
            return jsonify({'success': False, 'error': 'Artisan not found'}), 404
        
        # Create product object
        product = Product(
            artisan_id=req['artisan_id'],
            name=req['name'],
            description=req['description'],
            price=req['price'],
            category=req['category'],
            subcategory=req.get('subcategory'),
            materials=req.get('materials', []),
            dimensions=req.get('dimensions'),
            weight=req.get('weight'),
            stock_quantity=req.get('stock_quantity', 1)
        )
        
        # Save to database
        data.create_product(product)
        
        return jsonify({'success': True, 'data': product.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        # Get existing product
        product = data.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Get request data
        req = request.json
        if not req:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in req:
            product.name = req['name']
        if 'description' in req:
            product.description = req['description']
        if 'price' in req:
            product.price = float(req['price'])
        if 'category' in req:
            product.category = req['category']
        if 'subcategory' in req:
            product.subcategory = req['subcategory']
        if 'materials' in req:
            product.materials = req['materials']
        if 'dimensions' in req:
            product.dimensions = req['dimensions']
        if 'weight' in req:
            product.weight = req['weight']
        if 'stock_quantity' in req:
            product.update_stock(int(req['stock_quantity']))
        if 'status' in req:
            product.status = req['status']
        if 'featured' in req:
            product.featured = bool(req['featured'])
        if 'tags' in req:
            product.tags = req['tags']
        
        updated = data.update_product(product)
        
        return jsonify({'success': True, 'data': updated.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<product_id>/images', methods=['POST'])
def upload_product_image(product_id):
    try:
        # Check if product exists
        product = data.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
            
        file = request.files['image']
        
        # Upload and process image
        result = files.upload_product_image(file, product_id)
        
        if not result['success']:
            return jsonify(result), 400
            
        # Add image URL to product
        product.add_image(result['url'])
        data.update_product(product)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enhance-description-preview', methods=['POST'])
def enhance_description_preview():
    """Enhance description without saving to database (for inline preview)"""
    try:
        req = request.json
        if not req:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required = ['description', 'product_name', 'craft_type', 'materials']
        for field in required:
            if field not in req:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        enhanced_description = google_service.enhance_product_description(
            req['description'], 
            req['product_name'], 
            req['craft_type'], 
            req['materials']
        )
        
        return jsonify({
            'success': True,
            'original_description': req['description'],
            'enhanced_description': enhanced_description,
            'ai_powered': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Utility endpoints
@app.route('/api/categories')
def get_categories():
    try:
        categories = data.get_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/craft-types')
def get_craft_types():
    try:
        craft_types = data.get_craft_types()
        return jsonify({
            'success': True,
            'data': craft_types
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/products/<product_id>/images/enhanced', methods=['POST'])
def upload_enhanced_product_image(product_id):
    """Upload product image with Google AI enhancement"""
    try:
        product = data.get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
            
        file = request.files['image']
        
        result = google_service.upload_product_image(file, product_id)
        
        if not result['success']:
            return jsonify(result), 400
            
        product.add_image(result['url'])
        data.update_product(product)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    
    print("Starting KALA KAKSH Backend...")
    print("Health Check: http://localhost:5000/api/health")
    print("Dashboard: http://localhost:5000/api/dashboard")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)