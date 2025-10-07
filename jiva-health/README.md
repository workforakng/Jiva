# Jīva Health - AI-Powered Health Record Management

Complete healthcare platform for digitizing and managing medical records in India.

## 🚀 Features

- **AI-Powered OCR**: Extract medical data from documents using Google Cloud Vision API
- **Smart NLP**: Automatically identify biomarkers and test results
- **Secure Storage**: Firebase Authentication and Firestore for data security
- **Mobile-First**: React Native (Expo) mobile application
- **RESTful API**: FastAPI backend with comprehensive documentation

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Google Cloud Account** with Vision API enabled
- **Firebase Project** with Authentication, Firestore, and Storage enabled

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jiva-health.git
cd jiva-health
```

### 2. Backend Setup

```bash
cd jiva-health/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Add your Firebase service account key as jiva-health-key.json
```

### 3. Mobile App Setup

```bash
cd jiva-health/mobile-app

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your Firebase credentials
```

## ⚙️ Configuration

### Backend (.env)

```env
# Firebase Admin SDK
GOOGLE_APPLICATION_CREDENTIALS=jiva-health-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# Google Cloud Services
GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-storage-bucket

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:19006

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# OCR & NLP
SPACY_MODEL=en_core_web_sm
OCR_CONFIDENCE_THRESHOLD=0.7
```

### Mobile App (.env)

```env
# Firebase Configuration
EXPO_PUBLIC_FIREBASE_API_KEY=your_api_key
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
EXPO_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
EXPO_PUBLIC_FIREBASE_APP_ID=your_app_id

# Backend API
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
EXPO_PUBLIC_API_TIMEOUT=30000
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
chmod +x start-backend.sh
./start-backend.sh
```

Backend will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Mobile App

```bash
cd mobile-app

# Start Expo development server
npm start

# Or use specific platform
npm run android  # For Android
npm run ios      # For iOS
npm run web      # For Web
```

### Quick Start All Services

```bash
# On Unix/Linux/Mac
chmod +x start-all.sh
./start-all.sh

# On Windows
start-all.bat
```

## 📁 Project Structure

```
jiva-health/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── config.py          # Configuration settings
│   │   ├── main.py            # FastAPI application
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── health_records.py
│   │   │   └── upload.py
│   │   ├── services/          # Business logic
│   │   │   ├── firestore_service.py
│   │   │   ├── ocr_service.py
│   │   │   └── nlp_service.py
│   │   └── utils/             # Utility functions
│   ├── requirements.txt
│   └── .env
│
├── mobile-app/                 # React Native mobile app
│   ├── app/                   # Expo Router screens
│   │   ├── (tabs)/           # Tab navigation
│   │   ├── _layout.tsx
│   │   └── +not-found.tsx
│   ├── components/            # Reusable components
│   ├── config/                # App configuration
│   │   ├── api.config.ts
│   │   └── firebase.config.ts
│   ├── constants/             # Constants and types
│   │   └── Types.ts
│   ├── services/              # API and Firebase services
│   │   ├── api.ts
│   │   ├── firebase.ts
│   │   └── storage.ts
│   ├── package.json
│   ├── app.json
│   └── .env
│
└── cloud-functions/           # Google Cloud Functions
```

## 🔑 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile
- `POST /auth/verify-token` - Verify authentication token

### Health Records
- `GET /api/health-records` - List all health records
- `POST /api/health-records` - Create health record
- `GET /api/health-records/{id}` - Get specific record
- `PUT /api/health-records/{id}` - Update record
- `DELETE /api/health-records/{id}` - Delete record

### Document Upload
- `POST /api/upload/document` - Upload and process document
- `POST /api/upload/process` - Reprocess existing document
- `GET /api/upload/status/{id}` - Get processing status
- `DELETE /api/upload/document/{id}` - Delete document

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Mobile App Tests
```bash
cd mobile-app
npm test
```

## 🔒 Security

- Firebase Authentication for user management
- JWT tokens for API authentication
- Secure storage of sensitive data
- CORS configuration for API access
- Input validation and sanitization

## 📝 Environment Variables

Make sure to set all required environment variables before running the application. Never commit `.env` files or service account keys to version control.

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Unix/Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**Firebase credentials error:**
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account key
- Check that the service account has necessary permissions

### Mobile App Issues

**Expo not starting:**
```bash
# Clear cache
npm start --clear

# Or
expo start -c
```

**Firebase connection issues:**
- Verify all Firebase config values in `.env`
- Ensure Firebase project is properly configured
- Check that Firebase services are enabled

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Expo Documentation](https://docs.expo.dev/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google Cloud Vision API](https://cloud.google.com/vision/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Google Cloud Platform for Vision API
- Firebase for backend services
- FastAPI framework
- React Native and Expo teams
- spaCy NLP library

---

**Note:** This is a development setup. For production deployment, additional configuration for security, scaling, and monitoring is required.
