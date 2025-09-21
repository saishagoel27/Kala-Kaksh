import os
import json
from typing import List, Optional, Dict, Any
from models.artisan import Artisan
from models.product import Product
from utils.helpers import save_json_data, load_json_data

class DataService:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.artisans_file = os.path.join(data_dir, "artisans.json")
        self.products_file = os.path.join(data_dir, "products.json")
        
        os.makedirs(data_dir, exist_ok=True)
        
        if not os.path.exists(self.artisans_file):
            save_json_data([], self.artisans_file)
        
        if not os.path.exists(self.products_file):
            save_json_data([], self.products_file)
    
    # Artisan methods
    def get_all_artisans(self) -> List[Artisan]:
        data = load_json_data(self.artisans_file)
        return [Artisan.from_dict(item) for item in data]
    
    def get_artisan_by_id(self, artisan_id: str) -> Optional[Artisan]:
        for artisan in self.get_all_artisans():
            if artisan.id == artisan_id:
                return artisan
        return None
    
    def get_artisan_by_email(self, email: str) -> Optional[Artisan]:
        for artisan in self.get_all_artisans():
            if artisan.email == email:
                return artisan
        return None
    
    def create_artisan(self, artisan: Artisan) -> Artisan:
        artisans = load_json_data(self.artisans_file)
        artisans.append(artisan.to_dict())
        save_json_data(artisans, self.artisans_file)
        return artisan
    
    def update_artisan(self, artisan: Artisan) -> Optional[Artisan]:
        artisans = load_json_data(self.artisans_file)
        
        for i, item in enumerate(artisans):
            if item['id'] == artisan.id:
                artisans[i] = artisan.to_dict()
                save_json_data(artisans, self.artisans_file)
                return artisan
        
        return None  
    
    # Product methods
    def get_all_products(self) -> List[Product]:
        data = load_json_data(self.products_file)
        return [Product.from_dict(item) for item in data]
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        for product in self.get_all_products():
            if product.id == product_id:
                return product
        return None
    
    def get_products_by_artisan(self, artisan_id: str) -> List[Product]:
        return [p for p in self.get_all_products() if p.artisan_id == artisan_id]
    
    def get_products_by_category(self, category: str) -> List[Product]:
        return [p for p in self.get_all_products() if p.category.lower() == category.lower()]
    
    def search_products(self, query: str) -> List[Product]:
        query = query.lower()
        results = []
        
        for product in self.get_all_products():
            # Check name, description, materials
            if (query in product.name.lower() or 
                query in product.description.lower() or
                any(query in m.lower() for m in product.materials)):
                results.append(product)
        
        return results
    
    def create_product(self, product: Product) -> Product:
        products = load_json_data(self.products_file)
        products.append(product.to_dict())
        save_json_data(products, self.products_file)
        
        # Update artisan's product count
        artisan = self.get_artisan_by_id(product.artisan_id)
        if artisan:
            artisan.increment_products()
            self.update_artisan(artisan)
        
        return product
    
    def update_product(self, product: Product) -> Optional[Product]:
        products = load_json_data(self.products_file)
        
        for i, item in enumerate(products):
            if item['id'] == product.id:
                products[i] = product.to_dict()
                save_json_data(products, self.products_file)
                return product
        
        return None  
    
    def get_categories(self) -> List[str]:
        products = self.get_all_products()
        categories = set(p.category for p in products)
        return sorted(list(categories))
    
    def get_craft_types(self) -> List[str]:
        artisans = self.get_all_artisans()
        craft_types = set(a.craft_type for a in artisans)
        return sorted(list(craft_types))
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        artisans = self.get_all_artisans()
        products = self.get_all_products()
        
        return {
            'total_artisans': len(artisans),
            'total_products': len(products),
            'verified_artisans': sum(1 for a in artisans if a.verified),
            'active_products': sum(1 for p in products if p.status == 'active'),
            'categories': self.get_categories(),
            'craft_types': self.get_craft_types()
        }