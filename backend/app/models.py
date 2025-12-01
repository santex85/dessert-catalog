from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Dessert(Base):
    """Модель десерта"""
    __tablename__ = "desserts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    image_url = Column(String(500))
    description = Column(Text)
    ingredients = Column(Text)
    calories = Column(Float)
    proteins = Column(Float)
    fats = Column(Float)
    carbs = Column(Float)
    weight = Column(String(50))  # Вес/фасовка
    price = Column(Float)  # Стоимость
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<Dessert {self.title}>"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    logo_url = Column(String(500))  # URL логотипа компании
    company_name = Column(String(200))  # Название компании
    manager_contact = Column(String(500))  # Контакты менеджера
    catalog_description = Column(Text)  # Описание каталога (философия компании)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"


class ActivityLog(Base):
    """Модель лога активности пользователей"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # ID пользователя, который выполнил действие
    username = Column(String(50), nullable=True, index=True)  # Имя пользователя для быстрого поиска
    action = Column(String(100), nullable=False, index=True)  # Тип действия (create, update, delete, login, etc.)
    entity_type = Column(String(50), nullable=True, index=True)  # Тип сущности (user, dessert, etc.)
    entity_id = Column(Integer, nullable=True, index=True)  # ID измененной сущности
    description = Column(Text, nullable=True)  # Описание действия
    old_values = Column(Text, nullable=True)  # Старые значения (JSON строка)
    new_values = Column(Text, nullable=True)  # Новые значения (JSON строка)
    ip_address = Column(String(45), nullable=True)  # IP адрес
    user_agent = Column(String(500), nullable=True)  # User agent браузера
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<ActivityLog {self.action} by {self.username}>"

