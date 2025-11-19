from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, IMAGES_URL_PREFIX
from app.auth import get_current_user
from app.models import User
from pathlib import Path
import uuid
import shutil
from typing import Optional

router = APIRouter(prefix="/api/upload", tags=["upload"])


def validate_image_file(file: UploadFile) -> None:
    """Валидация загружаемого файла"""
    # Проверка расширения
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload image to server (requires authentication)"""
    try:
        # Валидация расширения файла
        validate_image_file(file)
        
        # Читаем файл для проверки размера
        contents = await file.read()
        file_size = len(contents)
        
        # Проверка размера
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File is too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Validate and sanitize filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Get file extension and validate
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename to prevent path traversal and collisions
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Additional path traversal protection
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Возвращаем URL для доступа к файлу
        image_url = f"{IMAGES_URL_PREFIX}{unique_filename}"
        
        return JSONResponse(
            status_code=200,
            content={
                "url": image_url,
                "filename": unique_filename,
                "original_filename": file.filename
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )


@router.delete("/image/{filename}")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete image from server (requires authentication)"""
    try:
        # Path traversal protection
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = UPLOAD_DIR / filename
        
        # Additional path traversal protection
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Проверяем существование файла
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Удаляем файл
        file_path.unlink()
        
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )

