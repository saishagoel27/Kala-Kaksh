import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename

# ID generation
def generate_id():
    """Simple UUID wrapper for our IDs"""
    return str(uuid.uuid4())

def get_timestamp():
    return datetime.now().isoformat()

def get_readable_date(timestamp=None):
    """Get a human-readable date string"""
    if not timestamp:
        dt = datetime.now()
    else:
        try:
            dt = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            return "Invalid date"
    
    return dt.strftime("%d %b %Y, %H:%M")

# File helpers
def allowed_file(filename, allowed_extensions=None):
    """Check if uploaded file type is allowed"""
    if allowed_extensions is None:
        # Default allowed types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
    if '.' not in filename:
        return False
        
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

# JSON handling
def save_json_data(data, filepath):
    """Save data to a JSON file with error handling"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        return False

def load_json_data(filepath):
    """Load data from a JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:

        return []
    except json.JSONDecodeError:
        print(f"Warning: Couldn't parse JSON in {filepath}")
        return []
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return []

def format_currency(amount):
    """Format a price with Indian Rupee symbol"""
    if amount is None:
        return "₹0.00"
    
    try:
        amount = float(amount)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

def truncate_text(text, max_length=100):
    """Truncate long text for display"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
        
    return text[:max_length].rstrip() + "..."

def is_valid_phone(phone):
    """Basic validation for Indian phone numbers"""
    if not phone:
        return False
    
    digits = ''.join(c for c in phone if c.isdigit())
    
    if len(digits) == 10 and digits[0] in '6789':
        return True
        
    if len(digits) == 12 and digits.startswith('91') and digits[2] in '6789':
        return True
        
    return False

def create_backup(filepath):
    """Create a backup of a file before modifying"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.bak"
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
    return False