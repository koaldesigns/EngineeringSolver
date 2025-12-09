from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.auth_routes import router as auth_router
from api.admin_routes import router as admin_router
from database import engine, Base
from models import RegistrationToken, VALID_TOKENS
from sqlalchemy.orm import Session
from database import SessionLocal

app = FastAPI(title="Engineering Equation Solver", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


def init_database():
    """Initialize database tables and seed data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
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
