"""
Скрипт миграции для добавления полей профиля компании в таблицу users
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_company_profile_fields():
    """Добавляет поля logo_url, company_name, manager_contact в таблицу users, если их нет"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли колонка logo_url
        if engine.url.drivername == 'sqlite':
            # Для SQLite проверяем структуру таблицы
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'logo_url' not in columns:
                print("Adding logo_url column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN logo_url VARCHAR(500)"))
                db.commit()
                print("✓ Column 'logo_url' added successfully")
            else:
                print("✓ Column 'logo_url' already exists")
            
            if 'company_name' not in columns:
                print("Adding company_name column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN company_name VARCHAR(200)"))
                db.commit()
                print("✓ Column 'company_name' added successfully")
            else:
                print("✓ Column 'company_name' already exists")
            
            if 'manager_contact' not in columns:
                print("Adding manager_contact column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN manager_contact VARCHAR(500)"))
                db.commit()
                print("✓ Column 'manager_contact' added successfully")
            else:
                print("✓ Column 'manager_contact' already exists")
        else:
            # Для PostgreSQL и других БД
            try:
                # Проверяем logo_url
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='logo_url'
                """))
                if result.fetchone() is None:
                    print("Adding logo_url column to users table...")
                    db.execute(text("ALTER TABLE users ADD COLUMN logo_url VARCHAR(500)"))
                    db.commit()
                    print("✓ Column 'logo_url' added successfully")
                else:
                    print("✓ Column 'logo_url' already exists")
                
                # Проверяем company_name
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='company_name'
                """))
                if result.fetchone() is None:
                    print("Adding company_name column to users table...")
                    db.execute(text("ALTER TABLE users ADD COLUMN company_name VARCHAR(200)"))
                    db.commit()
                    print("✓ Column 'company_name' added successfully")
                else:
                    print("✓ Column 'company_name' already exists")
                
                # Проверяем manager_contact
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='manager_contact'
                """))
                if result.fetchone() is None:
                    print("Adding manager_contact column to users table...")
                    db.execute(text("ALTER TABLE users ADD COLUMN manager_contact VARCHAR(500)"))
                    db.commit()
                    print("✓ Column 'manager_contact' added successfully")
                else:
                    print("✓ Column 'manager_contact' already exists")
            except Exception as e:
                print(f"Error checking/adding columns: {e}")
                db.rollback()
                raise
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_company_profile_fields()

