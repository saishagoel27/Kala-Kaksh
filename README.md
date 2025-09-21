# 🎨 KALA KAKSH - AI-Powered Artisan Marketplace

**KALA KAKSH revolutionises the way Indian artisans showcase their craft online, built on **Google Cloud's cutting-edge AI stack, this transforms simple product descriptions into compelling cultural narratives while providing enterprise-grade image processing and storage.**

##  Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Access**: http://localhost:5000

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
