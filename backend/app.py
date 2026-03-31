"""
KeyGuard Backend - Main FastAPI Application
Real-time keystroke-based intrusion detection system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from .routes import auth, predict, train, capture
    from .database.db import Base, engine
    from .utils.logger import get_logger
    from .utils.config import NORMAL_THRESHOLD, SUSPICIOUS_THRESHOLD
except ImportError:
    from routes import auth, predict, train, capture
    from database.db import Base, engine
    from utils.logger import get_logger
    from utils.config import NORMAL_THRESHOLD, SUSPICIOUS_THRESHOLD

# Setup logging
logger = get_logger()

# Create FastAPI app
app = FastAPI(
    title="KeyGuard Backend",
    description="Real-time keystroke-based intrusion detection API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

# Include routers
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(predict.router, prefix="", tags=["prediction"])
app.include_router(train.router, prefix="", tags=["training"])
app.include_router(capture.router, prefix="", tags=["capture"])

@app.get("/")
async def read_root():
    """Root endpoint with API info"""
    return {
        "application": "KeyGuard Backend",
        "version": "1.0.0",
        "description": "Real-time keystroke-based intrusion detection system",
        "endpoints": {
            "capture": {
                "POST /capture/start": "Start keystroke capture session",
                "POST /capture/end": "End keystroke capture session",
                "GET /capture/status": "Check session status"
            },
            "auth": {
                "POST /auth/register": "Create a new account",
                "POST /auth/login": "Login and create a session",
                "POST /auth/logout": "Logout and end the active session",
                "GET /auth/session/{token}": "Restore a logged-in session"
            },
            "prediction": {
                "POST /predict": "Predict intrusion from keystroke data",
                "GET /predict/health": "Health check"
            },
            "training": {
                "POST /train": "Train user behavior profile",
                "GET /train/health": "Health check"
            },
            "system": {
                "GET /health": "System health check",
                "GET /config": "Get system configuration"
            }
        }
    }

@app.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "service": "KeyGuard Backend",
        "version": "1.0.0",
        "database": "connected"
    }

@app.get("/config")
async def get_config():
    """Get system configuration"""
    return {
        "thresholds": {
            "normal_threshold": NORMAL_THRESHOLD,
            "suspicious_threshold": SUSPICIOUS_THRESHOLD
        },
        "features": {
            "expected_feature_count": 5,
            "feature_names": [
                "dwell_time",
                "flight_time",
                "key_press_rate",
                "key_release_interval",
                "typing_speed"
            ]
        },
        "models": {
            "random_forest": "Enabled",
            "one_class_svm": "Enabled"
        }
    }

@app.get("/status")
async def get_status():
    """Get detailed system status"""
    return {
        "service": "KeyGuard Backend",
        "status": "running",
        "version": "1.0.0",
        "components": {
            "database": "operational",
            "predict_service": "operational",
            "train_service": "operational",
            "capture_service": "operational",
            "ml_models": "loaded"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting KeyGuard Backend server")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
