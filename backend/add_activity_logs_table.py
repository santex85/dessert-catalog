"""
Скрипт миграции для создания таблицы activity_logs
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def add_activity_logs_table():
    """Создает таблицу activity_logs, если её нет"""
    db = SessionLocal()
    try:
        if engine.url.drivername == 'sqlite':
            # Для SQLite проверяем существование таблицы
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_logs'"))
            if result.fetchone() is None:
                print("Creating activity_logs table...")
                db.execute(text("""
                    CREATE TABLE activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username VARCHAR(50),
                        action VARCHAR(100) NOT NULL,
                        entity_type VARCHAR(50),
                        entity_id INTEGER,
                        description TEXT,
                        old_values TEXT,
                        new_values TEXT,
                        ip_address VARCHAR(45),
                        user_agent VARCHAR(500),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.execute(text("CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id)"))
                db.execute(text("CREATE INDEX idx_activity_logs_username ON activity_logs(username)"))
                db.execute(text("CREATE INDEX idx_activity_logs_action ON activity_logs(action)"))
                db.execute(text("CREATE INDEX idx_activity_logs_entity_type ON activity_logs(entity_type)"))
                db.execute(text("CREATE INDEX idx_activity_logs_entity_id ON activity_logs(entity_id)"))
                db.execute(text("CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at)"))
                db.commit()
                print("✓ Table 'activity_logs' created successfully")
            else:
                print("✓ Table 'activity_logs' already exists")
        else:
            # Для PostgreSQL и других БД
            try:
                result = db.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'activity_logs'
                    )
                """))
                if not result.scalar():
                    print("Creating activity_logs table...")
                    db.execute(text("""
                        CREATE TABLE activity_logs (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            username VARCHAR(50),
                            action VARCHAR(100) NOT NULL,
                            entity_type VARCHAR(50),
                            entity_id INTEGER,
                            description TEXT,
                            old_values TEXT,
                            new_values TEXT,
                            ip_address VARCHAR(45),
                            user_agent VARCHAR(500),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    db.execute(text("CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id)"))
                    db.execute(text("CREATE INDEX idx_activity_logs_username ON activity_logs(username)"))
                    db.execute(text("CREATE INDEX idx_activity_logs_action ON activity_logs(action)"))
                    db.execute(text("CREATE INDEX idx_activity_logs_entity_type ON activity_logs(entity_type)"))
                    db.execute(text("CREATE INDEX idx_activity_logs_entity_id ON activity_logs(entity_id)"))
                    db.execute(text("CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at)"))
                    db.commit()
                    print("✓ Table 'activity_logs' created successfully")
                else:
                    print("✓ Table 'activity_logs' already exists")
            except Exception as e:
                print(f"Error checking/creating table: {e}")
                db.rollback()
                raise
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_activity_logs_table()

