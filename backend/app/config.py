import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Директория для загрузки изображений
UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Максимальный размер файла (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Разрешенные типы файлов
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# URL для доступа к изображениям
IMAGES_URL_PREFIX = "/static/images/"

