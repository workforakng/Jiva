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
```bash
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

### Mobile App Issues

**"Metro bundler error"**
```bash
# Clear cache and restart
npm start -- --clear
```

**"Firebase config error"**
- Double-check all EXPO_PUBLIC_ variables in .env
- Ensure no spaces in values
- Restart expo after changing .env

**"Module not found: Types"**
- Already fixed! The Types.ts file has been created
- Restart expo if still seeing this error

## Essential Environment Variables

### Backend (.env)
```env
GOOGLE_APPLICATION_CREDENTIALS=jiva-health-key.json
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
JWT_SECRET_KEY=change-this-to-random-string
```

### Mobile App (.env)
```env
EXPO_PUBLIC_FIREBASE_API_KEY=your-api-key
EXPO_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Testing Your Setup

### 1. Test Backend API

**Create a test user (using API docs):**
1. Go to http://localhost:8000/docs
2. Click on `POST /auth/register`
3. Try it out with test data
4. Execute

**Test OCR endpoint:**
1. Click on `POST /api/upload/document`
2. Authorize with token from registration
3. Upload a sample medical report image
4. Check the response

### 2. Test Mobile App

**Sign Up Flow:**
1. Open app in Expo Go
2. Navigate to Sign Up screen
3. Create test account
4. Verify you can log in

**Upload Flow:**
1. Log in with test account
2. Click Upload Document
3. Select a sample medical report
4. Verify it processes successfully

## Next Steps

Now that everything is working:

1. **Read the full README.md** for detailed documentation
2. **Check FIXES.md** to see what was fixed
3. **Start developing** your features!

## Need Help?

- **API Issues**: Check http://localhost:8000/docs for API documentation
- **Mobile Issues**: Run `expo doctor` to diagnose problems
- **Firebase Issues**: Check Firebase Console for errors
- **Other Issues**: See README.md Troubleshooting section

## Development Workflow

```bash
# Day-to-day development

# Start backend (Terminal 1)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start mobile (Terminal 2)
cd mobile-app && npm start

# Make changes, save, and auto-reload handles the rest!
```

## Production Checklist

Before deploying to production:

- [ ] Change all default secrets and keys
- [ ] Set DEBUG=False in backend .env
- [ ] Configure proper CORS origins
- [ ] Enable Firebase security rules
- [ ] Set up Cloud Storage CORS
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Enable HTTPS
- [ ] Test all endpoints
- [ ] Run security audit

---

**🎉 You're all set! Happy coding!**

For detailed documentation, see [README.md](README.md)
For fix details, see [FIXES.md](FIXES.md)
