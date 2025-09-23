# 🎨 KALA KAKSH - AI-Powered Artisan Marketplace

KALA KAKSH revolutionises the way Indian artisans showcase their craft online, built on **Google Cloud's cutting-edge AI stack**, this transforms simple product descriptions into compelling cultural narratives while providing enterprise-grade image processing and storage.

##  Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Access**: http://localhost:5000

## 📸 Screenshots of the Seller Portal at the backend

<img width="1887" height="989" alt="Screenshot 2025-09-23 130939" src="https://github.com/user-attachments/assets/b021663e-df8a-43fb-ada0-1238b989bcd6" />

<img width="1892" height="904" alt="Screenshot 2025-09-23 130954" src="https://github.com/user-attachments/assets/5e1d1862-6d54-4373-9484-3d45e2b1e2e4" />

<img width="1887" height="359" alt="Screenshot 2025-09-23 131007" src="https://github.com/user-attachments/assets/2f5f9e1c-bfbc-421b-ba54-7e6c6242bf7f" />








## 🤖 Features

- **Artisan Registration** - Complete onboarding system
- **AI Description Enhancement** - Gemini AI transforms basic descriptions into cultural stories
- **Smart Image Processing** - Automatic optimization and cloud storage
- **Real-time Preview** - Inline AI enhancement with instant feedback

## 🛠️ Tech Stack

- **Backend**: Flask + Python
- **AI**: Google Gemini 1.5 Flash
- **Storage**: Google Cloud Storage 
- **Data**: JSON-based 
- **Frontend**: Vanilla HTML/CSS/JS

## 📁 Project Structure

```
├── app.py              # Main Flask application
|──config.py            # Configuration Settings
├── models/             # Data models (Artisan, Product)
├── services/           # Business logic & Google Cloud integration
├── templates/          # Frontend interface
├── data/               # JSON storage
└── utils/              # Helper functions
└── workflow.md        # Detailed workflow documentation
```

##  Demo Flow

1. **Register Artisan** → Get unique ID
2. **Create Product** → Basic product details
3. **AI Enhancement** → Click "🤖 Enhance with Google AI"
4. **Upload Images** → Automatic processing & storage
5. **Live Product** → Complete marketplace listing

## 🔧 Configuration

Set environment variables in `.env`:
```env
GOOGLE_API_KEY="your-gemini-api-key"
GOOGLE_CLOUD_PROJECT="your-project-id"
USE_GOOGLE_CLOUD=true
```


*For detailed workflow and technical documentation, see [`workflow.md`](workflow.md)*
