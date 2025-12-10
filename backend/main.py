from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router as api_router
from api.auth_routes import router as auth_router
from api.admin_routes import router as admin_router
from database import engine, Base
from models import RegistrationToken, VALID_TOKENS
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
import traceback

app = FastAPI(title="Engineering Equation Solver", version="0.1.0")

# Configure CORS - MUST be added before exception handlers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Global exception handler to ensure CORS headers are in error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with proper CORS headers."""
    error_detail = str(exc)
    print(f"Unhandled exception: {error_detail}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {error_detail}"},
    )


# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


def init_database():
    """Initialize database tables and seed data."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Seed registration tokens if not present
        db = SessionLocal()
        try:
            existing_tokens = db.query(RegistrationToken).count()
            if existing_tokens == 0:
                for token in VALID_TOKENS:
                    db.add(RegistrationToken(token=token))
                db.commit()
                print(f"Initialized {len(VALID_TOKENS)} registration tokens")
        finally:
            db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")
        print(traceback.format_exc())


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_database()


@app.get("/")
async def root():
    return {"message": "Engineering Equation Solver API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/health/db")
async def database_health_check():
    """Check database connectivity."""
    try:
        db = SessionLocal()
        try:
            # Try a simple query
            result = db.execute(text("SELECT 1")).fetchone()
            return {"status": "ok", "database": "connected", "result": result[0]}
        finally:
            db.close()
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}

