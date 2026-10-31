from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routes import auth, tokens, admin

# Instantiate database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance, secure Token Conversion System with Glassmorphism Black & Red UI",
    version="1.0.0"
)

# Apply Cross-Origin Resource Sharing (CORS)
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router)
app.include_router(tokens.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "ONLINE", "project": settings.PROJECT_NAME, "version": "1.0.0"}