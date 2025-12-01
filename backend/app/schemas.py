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
    price: Optional[float] = Field(None, ge=0, description="Стоимость десерта")
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
    price: Optional[float] = Field(None, ge=0, description="Стоимость десерта")
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
    logo_url: Optional[str] = Field(None, description="URL логотипа компании")
    catalog_description: Optional[str] = Field(None, description="Описание каталога (философия компании)")
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
    logo_url: Optional[str] = None
    company_name: Optional[str] = None
    manager_contact: Optional[str] = None
    catalog_description: Optional[str] = None
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


class UpdateCompanyProfileRequest(BaseModel):
    """Запрос на обновление профиля компании"""
    logo_url: Optional[str] = Field(None, description="URL логотипа компании")
    company_name: Optional[str] = Field(None, max_length=200, description="Название компании")
    manager_contact: Optional[str] = Field(None, max_length=500, description="Контакты менеджера")
    catalog_description: Optional[str] = Field(None, description="Описание каталога (философия компании)")


# Схемы для управления пользователями (админка)
class UserUpdateRequest(BaseModel):
    """Запрос на обновление пользователя администратором"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    company_name: Optional[str] = Field(None, max_length=200)
    manager_contact: Optional[str] = Field(None, max_length=500)
    catalog_description: Optional[str] = None


class UserListResponse(BaseModel):
    """Список пользователей для админки"""
    users: list[UserResponse]
    total: int


# Схемы для логов активности
class ActivityLogResponse(BaseModel):
    """Ответ с записью лога активности"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogListResponse(BaseModel):
    """Список логов активности"""
    logs: list[ActivityLogResponse]
    total: int
    page: int
    page_size: int
