"""
Скрипт для создания администратора
"""
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash
import sys

def create_admin(username: str, email: str, password: str):
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже пользователь
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"Пользователь с именем '{username}' или email '{email}' уже существует!")
            return False
        
        # Создаем администратора
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"✓ Администратор '{username}' успешно создан!")
        return True
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании администратора: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username, email, password = sys.argv[1], sys.argv[2], sys.argv[3]
    create_admin(username, email, password)

