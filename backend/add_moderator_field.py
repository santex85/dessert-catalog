"""
Скрипт миграции для добавления поля is_moderator в таблицу users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_moderator_field():
    """Добавляет поле is_moderator в таблицу users, если его нет"""
    db = SessionLocal()
    try:
        if engine.url.drivername == 'sqlite':
            # Для SQLite проверяем структуру таблицы
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'is_moderator' not in columns:
                print("Adding is_moderator column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN is_moderator BOOLEAN DEFAULT 0"))
                db.commit()
                print("✓ Column 'is_moderator' added successfully")
            else:
                print("✓ Column 'is_moderator' already exists")
        else:
            # Для PostgreSQL и других БД
            try:
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='is_moderator'
                """))
                if result.fetchone() is None:
                    print("Adding is_moderator column to users table...")
                    db.execute(text("ALTER TABLE users ADD COLUMN is_moderator BOOLEAN DEFAULT FALSE"))
                    db.commit()
                    print("✓ Column 'is_moderator' added successfully")
                else:
                    print("✓ Column 'is_moderator' already exists")
            except Exception as e:
                print(f"Error checking/adding column: {e}")
                db.rollback()
                raise
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_moderator_field()

