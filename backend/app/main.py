 
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials
import uvicorn
import logging

from app.config import settings
from app.routes import health_records, upload, auth
from app.services.firestore_service import FirestoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.google_application_credentials)
    firebase_admin.initialize_app(cred, {
        'projectId': settings.firebase_project_id,
        'storageBucket': settings.google_cloud_storage_bucket
    })

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered health record management system for India",
    version=settings.version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else None}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Firestore connection
        firestore_service = FirestoreService()
        await firestore_service.test_connection()
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.version,
            "timestamp": "2025-10-05T20:03:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(health_records.router, prefix="/api/health-records", tags=["Health Records"])
app.include_router(upload.router, prefix="/api/upload", tags=["Document Upload"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Jīva Health API",
        "version": settings.version,
        "docs": "/docs" if settings.debug else "Docs disabled in production"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
