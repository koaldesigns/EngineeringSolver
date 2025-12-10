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
    print(f"Unhandled exception: {error_detail}", flush=True)
    print(traceback.format_exc(), flush=True)
    
    # Explicitly add CORS headers to error responses
    # This is needed because some reverse proxies strip CORS headers on 500s
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {error_detail}"},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
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


@app.get("/health/auth")
async def auth_health_check():
    """Check auth configuration and user table."""
    import os
    from models import User
    
    try:
        db = SessionLocal()
        try:
            # Check environment variables (don't expose password)
            admin_username = os.environ.get("ADMIN_USERNAME")
            admin_password_set = bool(os.environ.get("ADMIN_PASSWORD"))
            jwt_secret_set = bool(os.environ.get("JWT_SECRET"))
            
            # Check if users table exists and count users
            try:
                user_count = db.query(User).count()
                admin_exists = db.query(User).filter(User.username == admin_username).first() is not None if admin_username else False
            except Exception as table_err:
                return {
                    "status": "error",
                    "error": f"User table issue: {str(table_err)}",
                    "admin_username_set": bool(admin_username),
                    "admin_password_set": admin_password_set,
                }
            
            return {
                "status": "ok",
                "admin_username_set": bool(admin_username),
                "admin_username": admin_username,  # Show the username for debugging
                "admin_password_set": admin_password_set,
                "jwt_secret_set": jwt_secret_set,
                "user_count": user_count,
                "admin_exists": admin_exists,
            }
        finally:
            db.close()
    except Exception as e:
        return {"status": "error", "error": str(e)}
