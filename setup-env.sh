#!/bin/bash

# Setup environment variables helper script

echo "🔧 Jīva Health - Environment Setup"
echo ""

# Backend setup
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env..."
    cat > backend/.env << EOF
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./jiva-health-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name

# Firebase Configuration
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# API Configuration
API_SECRET_KEY=$(openssl rand -hex 32)
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:19006,exp://$(ipconfig getifaddr en0):8081
EOF
    echo "✅ backend/.env created"
fi

# Mobile app setup
if [ ! -f "mobile-app/.env" ]; then
    echo "Creating mobile-app/.env..."
    cat > mobile-app/.env << EOF
# Firebase Configuration
EXPO_PUBLIC_FIREBASE_API_KEY=your_api_key
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
EXPO_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
EXPO_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123

# Backend API
EXPO_PUBLIC_API_BASE_URL=http://$(ipconfig getifaddr en0):8000
EXPO_PUBLIC_API_TIMEOUT=30000

# Google Cloud
EXPO_PUBLIC_CLOUD_STORAGE_BUCKET=your-bucket-name
EOF
    echo "✅ mobile-app/.env created"
fi

echo ""
echo "⚠️  Please update the .env files with your actual credentials"
echo "   - backend/.env"
echo "   - mobile-app/.env"
