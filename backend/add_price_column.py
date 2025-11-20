"""
Скрипт миграции для добавления колонки price в таблицу desserts
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_price_column():
    """Добавляет колонку price в таблицу desserts, если её нет"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли колонка price
        if engine.url.drivername == 'sqlite':
            # Для SQLite проверяем структуру таблицы
            result = db.execute(text("PRAGMA table_info(desserts)"))
            columns = [row[1] for row in result]
            
            if 'price' not in columns:
                print("Adding price column to desserts table...")
                db.execute(text("ALTER TABLE desserts ADD COLUMN price REAL"))
                db.commit()
                print("✓ Column 'price' added successfully")
            else:
                print("✓ Column 'price' already exists")
        else:
            # Для PostgreSQL и других БД
            try:
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='desserts' AND column_name='price'
                """))
                if result.fetchone() is None:
                    print("Adding price column to desserts table...")
                    db.execute(text("ALTER TABLE desserts ADD COLUMN price REAL"))
                    db.commit()
                    print("✓ Column 'price' added successfully")
                else:
                    print("✓ Column 'price' already exists")
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
    add_price_column()

