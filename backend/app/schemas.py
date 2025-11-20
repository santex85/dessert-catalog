from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class DessertBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    image_url: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    calories: Optional[float] = Field(None, ge=0)
    proteins: Optional[float] = Field(None, ge=0)
    fats: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    weight: Optional[str] = None
    is_active: bool = True


class DessertCreate(DessertBase):
    pass


class DessertUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    image_url: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    calories: Optional[float] = Field(None, ge=0)
    proteins: Optional[float] = Field(None, ge=0)
    fats: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    weight: Optional[str] = None
    is_active: Optional[bool] = None


class DessertResponse(DessertBase):
    id: int

    class Config:
        from_attributes = True


class PDFExportSettings(BaseModel):
    """Настройки экспорта PDF"""
    dessert_ids: list[int] = Field(..., description="ID выбранных десертов")
    include_ingredients: bool = Field(True, description="Включить состав")
    include_nutrition: bool = Field(True, description="Включить КБЖУ")
    include_title_page: bool = Field(True, description="Добавить титульный лист")
    company_name: Optional[str] = Field(None, description="Название компании")
    manager_contact: Optional[str] = Field(None, description="Контакты менеджера")
    template: str = Field('minimal', description="Шаблон дизайна: minimal, classic, modern, luxury")


# Схемы для аутентификации
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None


class UpdateEmailRequest(BaseModel):
    """Запрос на обновление email"""
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    """Запрос на изменение пароля"""
    current_password: str = Field(..., min_length=6, description="Текущий пароль")
    new_password: str = Field(..., min_length=6, description="Новый пароль")


class ProfileUpdateResponse(BaseModel):
    """Ответ при обновлении профиля"""
    message: str
    user: UserResponse
