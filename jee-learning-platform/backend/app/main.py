from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

# Import database and models
from app.database.database import engine, Base
from app.models import models

# Import routes
from app.routes import auth, content, analytics, ai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup
    logger.info("Starting JEE Learning Platform API...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down JEE Learning Platform API...")

# Create FastAPI app
app = FastAPI(
    title="JEE Learning Platform API",
    description="""
    A comprehensive adaptive learning platform for JEE Main preparation with:
    
    * **Adaptive Learning**: AI-powered personalized quizzes and recommendations
    * **Analytics Tracking**: Detailed progress monitoring and mastery assessment
    * **Content Management**: Structured courses, chapters, and topics
    * **User Management**: Authentication and profile management
    * **Session Analytics**: Time tracking and study pattern analysis
    
    ## Features
    
    * 📚 Structured learning content with progress tracking
    * 🧠 AI-generated adaptive quizzes based on weak areas
    * 📊 Comprehensive analytics and reporting
    * 🎯 Personalized learning paths and study plans
    * ⏱️ Session management and time tracking
    * 📈 Mastery level calculation and recommendations
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(analytics.router)
app.include_router(ai.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "JEE Learning Platform API",
        "version": "1.0.0",
        "description": "Adaptive learning platform for JEE Main preparation",
        "features": [
            "Adaptive AI-powered quizzes",
            "Comprehensive analytics",
            "Progress tracking",
            "Personalized learning paths",
            "Session management"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# API Info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints."""
    return {
        "api_name": "JEE Learning Platform API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth",
            "content": "/content", 
            "analytics": "/analytics",
            "ai": "/ai"
        },
        "features": {
            "user_management": "User registration, authentication, and profile management",
            "content_delivery": "Structured courses, chapters, topics with progress tracking",
            "analytics": "Comprehensive learning analytics and reporting",
            "adaptive_learning": "AI-powered personalized quizzes and recommendations",
            "session_tracking": "Time tracking and study pattern analysis"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )