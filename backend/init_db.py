"""
Скрипт для инициализации базы данных с тестовыми данными
"""
from app.database import SessionLocal, engine, Base
from app.models import Dessert, User
from app.auth import get_password_hash

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Тестовые данные
sample_desserts = [
    {
        "title": "Чизкейк Нью-Йорк",
        "category": "Торты",
        "description": "Классический чизкейк с нежным сливочным вкусом и хрустящей основой из печенья. Идеален для особых случаев.",
        "ingredients": "Творожный сыр, сахар, яйца, сливки, печенье, сливочное масло, ваниль",
        "calories": 321.5,
        "proteins": 5.2,
        "fats": 22.1,
        "carbs": 25.8,
        "weight": "800 г",
        "is_active": True
    },
    {
        "title": "Тирамису",
        "category": "Десерты",
        "description": "Итальянский десерт с кофе, маскарпоне и какао. Нежный и воздушный, с насыщенным кофейным ароматом.",
        "ingredients": "Маскарпоне, сахар, яйца, кофе эспрессо, савоярди, какао-порошок, коньяк",
        "calories": 287.3,
        "proteins": 6.1,
        "fats": 18.5,
        "carbs": 24.2,
        "weight": "600 г",
        "is_active": True
    },
    {
        "title": "Красный бархат",
        "category": "Торты",
        "description": "Яркий торт с шоколадным вкусом и крем-чизом. Визуально эффектный десерт для праздников.",
        "ingredients": "Мука, сахар, какао, яйца, растительное масло, пахта, крем-чиз, пищевой краситель",
        "calories": 345.2,
        "proteins": 4.8,
        "fats": 19.3,
        "carbs": 38.7,
        "weight": "1200 г",
        "is_active": True
    },
    {
        "title": "Эклер с заварным кремом",
        "category": "Пирожные",
        "description": "Классическое французское пирожное с нежным заварным кремом и шоколадной глазурью.",
        "ingredients": "Мука, яйца, молоко, сахар, сливочное масло, шоколад, ваниль",
        "calories": 298.6,
        "proteins": 5.5,
        "fats": 16.2,
        "carbs": 32.1,
        "weight": "80 г",
        "is_active": True
    },
    {
        "title": "Веганский брауни",
        "category": "Веганские",
        "description": "Шоколадный брауни без яиц и молочных продуктов. Богатый вкус и текстура, подходит для веганов.",
        "ingredients": "Мука, какао, сахар, растительное масло, банан, орехи, разрыхлитель",
        "calories": 312.4,
        "proteins": 4.2,
        "fats": 15.8,
        "carbs": 42.3,
        "weight": "400 г",
        "is_active": True
    },
    {
        "title": "Торт без сахара",
        "category": "Без сахара",
        "description": "Диетический торт на основе стевии и фруктов. Подходит для диабетиков и приверженцев здорового питания.",
        "ingredients": "Мука, стевия, яйца, растительное масло, яблоки, корица, грецкие орехи",
        "calories": 198.7,
        "proteins": 6.1,
        "fats": 8.5,
        "carbs": 24.2,
        "weight": "900 г",
        "is_active": True
    }
]

def init_db():
    db = SessionLocal()
    try:
        desserts_count = 0
        users_count = 0
        
        # Проверяем и добавляем тестовые десерты
        if db.query(Dessert).count() == 0:
            for dessert_data in sample_desserts:
                dessert = Dessert(**dessert_data)
                db.add(dessert)
            desserts_count = len(sample_desserts)
        
        # Проверяем и создаем тестового администратора
        if db.query(User).filter(User.username == "admin").count() == 0:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            users_count = 1
            print("✓ Создан тестовый администратор:")
            print("  Username: admin")
            print("  Password: admin123")
        
        # Создаем тестового обычного пользователя
        if db.query(User).filter(User.username == "user").count() == 0:
            user = User(
                username="user",
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                is_admin=False,
                is_active=True
            )
            db.add(user)
            users_count += 1
            print("✓ Создан тестовый пользователь:")
            print("  Username: user")
            print("  Password: user123")
        
        db.commit()
        
        if desserts_count > 0:
            print(f"✓ Успешно добавлено {desserts_count} десертов в базу данных.")
        if users_count > 0:
            print(f"✓ Создано {users_count} тестовых пользователей.")
        
        if desserts_count == 0 and users_count == 0:
            print("База данных уже содержит данные. Пропускаем инициализацию.")
            
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

