from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.api import desserts, pdf, upload, auth
from app.config import UPLOAD_DIR, IMAGES_URL_PREFIX
from pathlib import Path
import os

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="Dessert Catalog API",
    description="Interactive dessert catalog with PDF generation",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Подключаем статические файлы для изображений
app.mount(IMAGES_URL_PREFIX, StaticFiles(directory=str(UPLOAD_DIR)), name="images")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(desserts.router)
app.include_router(pdf.router)
app.include_router(upload.router)


@app.get("/")
def root():
    return {"message": "Каталог десертов API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

