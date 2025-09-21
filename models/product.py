from utils.helpers import generate_id, get_timestamp

class Product:
    def __init__(self, artisan_id, name, description, price, category, 
                 subcategory=None, materials=None, dimensions=None, 
                 weight=None, stock_quantity=1, images=None):
        # Basic product info
        self.id = generate_id()
        self.artisan_id = artisan_id
        self.name = name
        self.description = description
        self.price = float(price) 
        self.category = category
        self.subcategory = subcategory
        
        # Product details
        self.materials = materials if materials else []
        self.dimensions = dimensions  
        self.weight = weight
        self.stock_quantity = int(stock_quantity)  
        # Media and metadata
        self.images = images or []  
        self.created_at = get_timestamp()
        self.updated_at = get_timestamp()
        self.status = "active" 
        self.tags = []
        self.featured = False
        
    def to_dict(self):
        return {
            'id': self.id,
            'artisan_id': self.artisan_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'subcategory': self.subcategory,
            'materials': self.materials,
            'dimensions': self.dimensions,
            'weight': self.weight,
            'stock_quantity': self.stock_quantity,
            'images': self.images,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'tags': self.tags,
            'featured': self.featured
        }
    
    @classmethod
    def from_dict(cls, data):
        product = cls(
            artisan_id=data['artisan_id'],
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=data['category'],
            subcategory=data.get('subcategory'),
            materials=data.get('materials', []),
            dimensions=data.get('dimensions'),
            weight=data.get('weight'),
            stock_quantity=data.get('stock_quantity', 1),
            images=data.get('images', [])
        )
        
        product.id = data['id']
        product.created_at = data['created_at']
        product.updated_at = data.get('updated_at', get_timestamp())
        product.status = data.get('status', 'active')
        product.tags = data.get('tags', [])
        product.featured = data.get('featured', False)
        
        return product
    
    def update_stock(self, quantity):
        """Update stock and automatically change status if needed"""
        self.stock_quantity = max(0, quantity)
        
        if self.stock_quantity == 0:
            self.status = "out_of_stock"
        elif self.status == "out_of_stock" and self.stock_quantity > 0:
            self.status = "active"
            
        self.updated_at = get_timestamp()
        
    def add_image(self, image_url):
        """Add an image URL if it's not already in the list"""
        if image_url and image_url not in self.images:
            self.images.append(image_url)
            self.updated_at = get_timestamp()
            return True
        return False
    
    def remove_image(self, image_url):
        """Remove an image URL from the list"""
        if image_url in self.images:
            self.images.remove(image_url)
            self.updated_at = get_timestamp()
            return True
        return False
    
    def toggle_featured(self):
        """Toggle whether this product is featured"""
        self.featured = not self.featured
        self.updated_at = get_timestamp()
        return self.featured
    
    def get_dimensions_text(self):
        """Get a formatted string of dimensions"""
        if not self.dimensions:
            return "Not specified"
            
        d = self.dimensions
        if all(k in d for k in ['length', 'width', 'height']):
            return f"{d['length']}L × {d['width']}W × {d['height']}H"
        elif all(k in d for k in ['length', 'width']):
            return f"{d['length']}L × {d['width']}W"
        elif 'diameter' in d:
            return f"Diameter: {d['diameter']}"
        else:
            return ", ".join(f"{k}: {v}" for k, v in d.items())
    
    def is_low_stock(self, threshold=5):
        """Check if product is running low on stock"""
        return 0 < self.stock_quantity <= threshold