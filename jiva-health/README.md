# Jīva Health - AI-Powered Health Record Management

Complete healthcare platform for digitizing and managing medical records in India.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Google Cloud account
- Firebase project

### Installation

1. **Clone the repository**
git clone https://github.com/yourusername/jiva-health.git
cd jiva-health

text

2. **Setup environment**
chmod +x setup-env.sh
./setup-env.sh

text

3. **Update credentials**
- Edit `backend/.env`
- Edit `mobile-app/.env`
- Add service account key to `backend/jiva-health-key.json`

4. **Start all services**
chmod +x start-all.sh
./start-all.sh

text

## Project Structure

jiva-health/
├── mobile-app/ # React Native mobile app
├── backend/ # FastAPI backend
├── cloud-functions/ # Google Cloud Functions
└── docs/ # Documentation

text

## Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Mobile App**: http://localhost:19006

## Documentation

See `/docs` for detailed documentation.

## License

MIT License
Make all scripts executable:

bash
chmod +x start-all.sh
chmod +x stop-all.sh
chmod +x start-backend.sh
chmod +x start-mobile.sh
chmod +x setup-env.sh
Now you can start everything with:

bash
./start-all.sh
This complete file structure and startup scripts will help you verify your setup and quickly start all services! 🚀