import os
import uuid
import io
import tempfile
from PIL import Image
from google.cloud import storage
from werkzeug.utils import secure_filename
from utils.helpers import allowed_file
from config import Config

class GoogleCloudService:
    def __init__(self):
        """Set up our Google Cloud connection"""
        self.project_id = Config.GOOGLE_CLOUD_PROJECT
        self.bucket_name = Config.GOOGLE_CLOUD_BUCKET
        self.use_cloud = Config.USE_GOOGLE_CLOUD
        
        if self.use_cloud:
            try:
                self.storage_client = storage.Client()
                self.bucket = self.storage_client.bucket(self.bucket_name)
                print("🌩️ Connected to Google Cloud Storage!")
            except Exception as e:
                print(f"⚠️ Google Cloud Storage not available: {e}")
                self.use_cloud = False
        
        # 🤖 NEW: Initialize Gemini AI (Direct API)
        try:
            import google.generativeai as genai
            
            # Get API key from config
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
                # Remove quotes if they exist
                api_key = api_key.strip('"')
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("🤖 Gemini AI ready!")
                self.ai_available = True
            else:
                print("⚠️ No GOOGLE_API_KEY found in environment")
                self.ai_available = False
                
        except Exception as ai_error:
            print(f"⚠️ Gemini AI not available: {ai_error}")
            self.ai_available = False

    def enhance_product_description(self, raw_description, product_name, craft_type, materials):
        """Use Gemini AI or fallback to create compelling product descriptions"""
        try:
            if not self.ai_available:
                print("📝 Using fallback text enhancement")
                return self._fallback_enhance_description(raw_description, product_name, craft_type, materials)
            
            # Prepare materials text
            materials_text = ', '.join(materials) if materials else 'Traditional materials'
            
            # Create a prompt for Gemini
            prompt = f"""Transform this simple artisan product description into a deeply emotional, story-driven marketing copy that connects hearts:

PRODUCT DETAILS:
- Name: {product_name}
- Craft: {craft_type} 
- Materials: {materials_text}
- Basic Description: {raw_description}

CREATE AN EMOTIONAL STORY that includes:


🏛️ HERITAGE & LEGACY:
- Mention generations of artisan families
- Reference ancient techniques and traditions
- Connect to India's rich cultural tapestry

💝 HUMAN CONNECTION:
- Tell the story of the artisan's hands creating this piece
- Mention the time, care, and love invested
- Reference the hopes and dreams embedded in each piece

🌟 SENSORY & EMOTIONAL APPEAL:
- Use words that evoke touch, warmth, and comfort
- Create imagery of the artisan's workshop
- Make the buyer feel they're bringing home a piece of someone's soul

🇮🇳 CULTURAL PRIDE:
- Celebrate the beauty of Indian craftsmanship
- Reference the spiritual significance of handmade items
- Connect to festivals, traditions, or daily rituals

📝 REQUIREMENTS:
- Write 3-4 sentences that tell a STORY, not just describe features
- Use emotional, warm, and evocative language
- Make it feel like bringing home a piece of India's heart
- End with how this piece will enrich the buyer's life
- Be specific about the craft and cultural context

Write a description that makes someone fall in love with this piece and the story behind it."""
            
            # Call Gemini AI
            response = self.gemini_model.generate_content(prompt)
            enhanced_text = response.text.strip()
            print(f"✨ Description enhanced with Gemini AI!")
            return enhanced_text
            
        except Exception as e:
            print(f"⚠️ AI enhancement failed: {e}")
            print("📝 Using fallback text enhancement")
            return self._fallback_enhance_description(raw_description, product_name, craft_type, materials)
    
    def _fallback_enhance_description(self, raw_description, product_name, craft_type, materials):
        """Fallback text enhancement when AI is not available"""
        materials_text = ', '.join(materials) if materials else 'traditional materials'
        
        enhanced = f"This exquisite handcrafted {product_name.lower()} showcases the artistry of {craft_type.lower()} masters, featuring {raw_description.lower()} using {materials_text}. Each piece reflects skilled craftsmanship and celebrates India's rich cultural heritage, bringing authentic traditional artistry to your collection."
        
        print("✨ Description enhanced with fallback method!")
        return enhanced

    # ...rest of your existing methods remain the same...
    def _generate_unique_filename(self, original_filename):
        """Create a unique name for the file so no two files have same name"""
        _, ext = os.path.splitext(original_filename)
        unique_name = str(uuid.uuid4())
        return secure_filename(f"{unique_name}{ext}")
    
    def _enhance_image_with_ai(self, image_bytes):
        """Use AI to make images look better (simplified for demo)"""
        try:
            print("🤖 Enhancing image with AI...")
            
            # Open the image from bytes
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if it has transparency
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Make it web-friendly size
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            
            print("✨ Image enhanced successfully!")
            return output.getvalue()
            
        except Exception as e:
            print(f"⚠️ Image enhancement failed: {e}")
            return image_bytes
    
    def upload_product_image(self, file, product_id):
        """Upload product image with AI enhancement"""
        try:
            # Basic checks
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not allowed_file(file.filename):
                return {'success': False, 'error': 'Only image files allowed'}
            
            print(f"📸 Uploading image for product {product_id}...")
            
            # Read the file
            file_content = file.read()
            
            # Enhance it with AI
            enhanced_content = self._enhance_image_with_ai(file_content)
            
            # Create unique filename
            filename = self._generate_unique_filename(file.filename)
            
            if self.use_cloud:
                # Upload to Google Cloud Storage
                blob_path = f"products/{product_id}/{filename}"
                blob = self.bucket.blob(blob_path)
                
                # Upload the enhanced image
                blob.upload_from_string(
                    enhanced_content,
                    content_type='image/jpeg'
                )
                
                # Make it accessible to everyone
                blob.make_public()
                
                url = blob.public_url
                storage_type = "Google Cloud Storage"
                
            else:
                # Fallback logic
                product_dir = os.path.join('uploads/products', product_id)
                os.makedirs(product_dir, exist_ok=True)
                
                file_path = os.path.join(product_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(enhanced_content)
                
                url = f"uploads/products/{product_id}/{filename}"
                storage_type = "Local Storage"
            
            print(f"✅ Image uploaded successfully to {storage_type}!")
            
            return {
                'success': True,
                'filename': filename,
                'url': url,
                'enhanced': True,
                'storage_type': storage_type,
                'ai_enhanced': True
            }
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def upload_profile_image(self, file, artisan_id):
        """Upload artisan profile image with AI enhancement"""
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not allowed_file(file.filename):
                return {'success': False, 'error': 'Only image files allowed'}
            
            print(f"👤 Uploading profile image for artisan {artisan_id}...")
            
            file_content = file.read()
            enhanced_content = self._enhance_image_with_ai(file_content)
            filename = self._generate_unique_filename(file.filename)
            
            if self.use_cloud:
                blob_path = f"profiles/{filename}"
                blob = self.bucket.blob(blob_path)
                blob.upload_from_string(enhanced_content, content_type='image/jpeg')
                blob.make_public()
                url = blob.public_url
                storage_type = "Google Cloud Storage"
            else:
                file_path = os.path.join('uploads/profiles', filename)
                with open(file_path, 'wb') as f:
                    f.write(enhanced_content)
                url = f"uploads/profiles/{filename}"
                storage_type = "Local Storage"
            
            print(f"✅ Profile image uploaded to {storage_type}!")
            
            return {
                'success': True,
                'filename': filename,
                'url': url,
                'enhanced': True,
                'storage_type': storage_type,
                'ai_enhanced': True
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Upload failed: {str(e)}'}