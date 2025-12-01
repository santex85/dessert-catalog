"""
Скрипт миграции для добавления поля catalog_description в таблицу users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_catalog_description_field():
    """Добавляет поле catalog_description в таблицу users, если его нет"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли колонка catalog_description
        if engine.url.drivername == 'sqlite':
            # Для SQLite проверяем структуру таблицы
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'catalog_description' not in columns:
                print("Adding catalog_description column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN catalog_description TEXT"))
                db.commit()
                print("✓ Column 'catalog_description' added successfully")
            else:
                print("✓ Column 'catalog_description' already exists")
        else:
            # Для PostgreSQL и других БД
            try:
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='catalog_description'
                """))
                if result.fetchone() is None:
                    print("Adding catalog_description column to users table...")
                    db.execute(text("ALTER TABLE users ADD COLUMN catalog_description TEXT"))
                    db.commit()
                    print("✓ Column 'catalog_description' added successfully")
                else:
                    print("✓ Column 'catalog_description' already exists")
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
    add_catalog_description_field()


