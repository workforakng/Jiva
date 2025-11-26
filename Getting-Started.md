````markdown
# 🚀 Quick Start Guide - Jiva Health

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, make sure you have:
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Firebase project created
- [ ] Google Cloud project with Vision API enabled

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd jiva-health/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy and configure environment
cp .env.example .env
# Edit .env with your Firebase and GCP credentials
```

**Important:** Place your Firebase service account JSON file in the backend directory as `jiva-health-key.json`

## Step 2: Mobile App Setup (2 minutes)

```bash
# Navigate to mobile app
cd jiva-health/mobile-app

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env
# Edit .env with your Firebase Web config
```

## Step 3: Start Everything (1 minute)

### Option A: Start Separately

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Mobile App:**
```bash
cd mobile-app
npm start
```

### Option B: Use Start Scripts

**Unix/Linux/Mac:**
```bash
chmod +x start-all.sh
./start-all.sh
```

**Windows:**
```powershell
start-all.bat
```

## Step 4: Verify Installation

### Backend Health Check
Open browser and visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "service": "Jīva Health API",
  "version": "1.0.0"
}
```

### Mobile App Check
- Expo DevTools should open automatically
- Scan QR code with Expo Go app on your phone
- Or press 'w' to open in web browser

## Common Issues & Quick Fixes

### Backend Issues

**"Port 8000 already in use"**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000 && taskkill /PID <PID> /F  # Windows
```

**"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

**"Firebase credentials not found"**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path in .env
- Ensure service account JSON file exists
- Verify filename matches exactly

## Need Help?

- **API Issues**: Check http://localhost:8000/docs for API documentation
- **Mobile Issues**: Run `expo doctor` to diagnose problems
- **Firebase Issues**: Check Firebase Console for errors
- **Other Issues**: See README.md Troubleshooting section

For detailed documentation, see [README.md](README.md)
For fix details, see [FIXES.md](FIXES.md)

````
