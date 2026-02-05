from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .core.config import settings
from .core.database import mongodb
from .api import files, chat

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await mongodb.connect()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await mongodb.disconnect()

app = FastAPI(
    title="File Chat System API",
    version="1.0.0",
    lifespan=lifespan
)

# Add routes
app.include_router(files.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "File Chat System API"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mongodb": "connected" if mongodb.client else "disconnected"
    }

# We'll add more routes later