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
                
                # Vertex AI for text generation
                try:
                    import vertexai
                    from vertexai.language_models import TextGenerationModel
                    
                    vertexai.init(project=self.project_id, location="us-central1")
                    self.text_model = TextGenerationModel.from_pretrained("text-bison@001")
                    print("🤖 Vertex AI Text Generation ready!")
                    self.ai_available = True
                except Exception as ai_error:
                    print(f"⚠️ Vertex AI not available: {ai_error}")
                    self.ai_available = False
                    
            except Exception as e:
                print(f"⚠️ Google Cloud not available: {e}")
                self.use_cloud = False
                self.ai_available = False
        else:
            self.ai_available = False

    def enhance_product_description(self, raw_description, product_name, craft_type, materials):
        """Use Vertex AI to create compelling product descriptions"""
        try:
            if not self.use_cloud or not self.ai_available:
                print("📝 AI not available, returning original description")
                return raw_description
            
            materials_text = ', '.join(materials) if materials else 'Traditional materials'
            
            prompt = f"""Transform this artisan product description into compelling marketing copy:

Product: {product_name}
Craft Type: {craft_type}
Materials: {materials_text}
Original Description: {raw_description}

Create a 2-3 sentence description that:
- Highlights traditional Indian craftsmanship
- Mentions the artisan's skill and heritage
- Appeals to buyers seeking authentic handmade items
- Uses warm, storytelling language

Enhanced Description:"""
            
            # Calling Vertex AI
            response = self.text_model.predict(
                prompt=prompt,
                max_output_tokens=150,
                temperature=0.7,
                top_p=0.8
            )
            
            enhanced_text = response.text.strip()
            print(f"✨ Description enhanced with AI!")
            return enhanced_text
            
        except Exception as e:
            print(f"⚠️ AI enhancement failed: {e}")
            return raw_description 

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
            return image_bytes  # Return original if enhancement fails
    
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