import os
from pathlib import Path

# Базовая директория проекта
# В Docker контейнере это будет /app
# Локально это будет корень проекта backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# Директория для загрузки изображений
UPLOAD_DIR = BASE_DIR / "uploads" / "images"

# Создаем директорию только если её нет (безопасно для Docker)
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError) as e:
    # Если не удалось создать (например, в Docker), пытаемся использовать существующую
    # или создадим в entrypoint.sh
    pass

# Максимальный размер файла (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Разрешенные типы файлов
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# URL для доступа к изображениям
IMAGES_URL_PREFIX = "/static/images/"

