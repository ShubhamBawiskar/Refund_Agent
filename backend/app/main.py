import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.api.main import api_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup hook
    print("Running database initialization hook...")
    init_db()
    yield
    # Shutdown hook
    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME)

# Configure CORS
origins = [
    "http://localhost:8501", # Streamlit
    "http://localhost:3000", # Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
