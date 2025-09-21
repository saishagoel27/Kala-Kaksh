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
        
        try:
            import google.generativeai as genai
            
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
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
            
            materials_text = ', '.join(materials) if materials else 'Traditional materials'
            
            prompt = f"""You are a master storyteller and a passionate advocate for Indian artisans. Your voice is warm, poetic, and deeply respectful of cultural heritage. Your mission is to transform a simple product description into a soulful narrative that makes a buyer feel an emotional connection to the artisan and their craft.

**CONTEXT (संदर्भ):**
*   **उत्पाद (Product):** {product_name}
*   **शिल्प (Craft):** {craft_type}
*   **सामग्री (Materials):** {materials_text}
*   **मूल विवरण (Original Description):** {raw_description}

**YOUR TASK (आपका काम):**
Craft a short, poetic, and deeply personal product description (3-4 sentences) that tells a story. This is not marketing copy; it is a piece of the artisan's soul translated into words.

**STORYTELLING PILLARS (कहानी के स्तंभ):**
1.  **The Artisan's Hands (कारीगर के हाथ):** Begin with the human touch. Describe the hands that made this item—are they weathered, gentle, skilled? Mention the "समर्पण" (dedication) and love poured into the work.
2.  **Generational Echoes (पीढ़ियों की गूंज):** Connect the craft to a lineage. Use phrases that evoke a sense of time, like "wisdom passed down through generations" or "techniques whispered from mother to daughter."
3.  **A Piece of India (भारत का एक टुकड़ा):** Ground the product in its cultural soil. What does it represent? A festival's joy? The peace of a rural morning? The sanctity of a home?
4.  **The Buyer's Blessing (खरीदार का आशीर्वाद):** Conclude by explaining the emotional or spiritual value for the buyer. They are not just buying an object; they are receiving a blessing, preserving a tradition, or bringing home a piece of "विरासत" (heritage).

**TONE & STYLE (शैली और अंदाज़):**
*   **Heartfelt & Intimate:** Write as if you are sharing a precious secret.
*   **Poetic Language:** Use metaphors and sensory details (e.g., "the warmth of the sun-baked clay," "threads that shimmer like a monsoon sky").
*   **Authentic Blend:** Weave in 1-2 simple Hindi words naturally to add authenticity, followed by their English meaning in parentheses. For example: "...carries the artisan's *आशीर्वाद* (blessings)..."
*   **AVOID:** Do not use generic marketing phrases like "exquisite," "masterpiece," "high-quality," or "buy now." Let the story sell itself.

**EXAMPLE OUTPUT STRUCTURE:**
(Sentence 1: The Artisan's Hands) -> (Sentence 2: Generational Echoes) -> (Sentence 3: A Piece of India & The Buyer's Blessing).

Now, using this framework, create the soulful narrative for the product detailed above.
"""
            
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
    
    def _generate_unique_filename(self, original_filename):
        """Create a unique name for the file so no two files have same name"""
        _, ext = os.path.splitext(original_filename)
        unique_name = str(uuid.uuid4())
        return secure_filename(f"{unique_name}{ext}")
    
    def _enhance_image_with_ai(self, image_bytes):
        """Use AI to make images look better (simplified for demo)"""
        try:
            print("🤖 Enhancing image with AI...")
            
            img = Image.open(io.BytesIO(image_bytes))
            
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
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
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            if not allowed_file(file.filename):
                return {'success': False, 'error': 'Only image files allowed'}
            
            print(f"📸 Uploading image for product {product_id}...")
            

            file_content = file.read()
            
            enhanced_content = self._enhance_image_with_ai(file_content)
            
            filename = self._generate_unique_filename(file.filename)
            
            if self.use_cloud:
                blob_path = f"products/{product_id}/{filename}"
                blob = self.bucket.blob(blob_path)
                
                blob.upload_from_string(
                    enhanced_content,
                    content_type='image/jpeg'
                )
                
                blob.make_public()
                
                url = blob.public_url
                storage_type = "Google Cloud Storage"
                
            else:
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