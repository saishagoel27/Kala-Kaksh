from utils.helpers import generate_id, get_timestamp

class Artisan:
    def __init__(self, name, email, phone, craft_type, location, 
                 bio=None, experience_years=0):
        # Basic info
        self.id = generate_id()
        self.name = name
        self.email = email
        self.phone = phone
        self.craft_type = craft_type  
        self.location = location      
        self.bio = bio
        self.experience_years = int(experience_years) if experience_years else 0
        
        self.profile_image = None
        self.created_at = get_timestamp()
        self.updated_at = get_timestamp()
        self.status = "active"
        self.verified = False
        
        self.rating = 0.0
        self.total_products = 0
        self.total_orders = 0
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'craft_type': self.craft_type,
            'location': self.location,
            'bio': self.bio,
            'experience_years': self.experience_years,
            'profile_image': self.profile_image,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'verified': self.verified,
            'rating': self.rating,
            'total_products': self.total_products,
            'total_orders': self.total_orders
        }
    
    @classmethod
    def from_dict(cls, data):
        artisan = cls(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            craft_type=data['craft_type'],
            location=data['location'],
            bio=data.get('bio'),
            experience_years=data.get('experience_years', 0)
        )
        artisan.id = data['id']
        artisan.profile_image = data.get('profile_image')
        artisan.created_at = data['created_at']
        artisan.updated_at = data.get('updated_at', get_timestamp())
        artisan.status = data.get('status', 'active')
        artisan.verified = data.get('verified', False)
        artisan.rating = data.get('rating', 0.0)
        artisan.total_products = data.get('total_products', 0)
        artisan.total_orders = data.get('total_orders', 0)
        return artisan
    
    def update_rating(self, new_rating):
        self.rating = round(float(new_rating), 1)
        self.updated_at = get_timestamp()
    
    def increment_products(self):
        self.total_products += 1
        self.updated_at = get_timestamp()
    
    def increment_orders(self):
        self.total_orders += 1
        self.updated_at = get_timestamp()