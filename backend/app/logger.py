"""
Модуль логирования действий пользователей
"""
from sqlalchemy.orm import Session
from app.models import ActivityLog, User
from typing import Optional, Dict, Any
from datetime import datetime
import json


def log_activity(
    db: Session,
    action: str,
    user: Optional[User] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    description: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ActivityLog:
    """
    Записать действие в лог
    
    Args:
        db: Сессия базы данных
        action: Тип действия (create, update, delete, login, logout, etc.)
        user: Пользователь, выполнивший действие
        entity_type: Тип сущности (user, dessert, etc.)
        entity_id: ID измененной сущности
        description: Описание действия
        old_values: Старые значения (словарь)
        new_values: Новые значения (словарь)
        ip_address: IP адрес
        user_agent: User agent браузера
    
    Returns:
        ActivityLog: Созданная запись лога
    """
    log_entry = ActivityLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_values=json.dumps(old_values, ensure_ascii=False) if old_values else None,
        new_values=json.dumps(new_values, ensure_ascii=False) if new_values else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return log_entry


def get_client_ip(request) -> Optional[str]:
    """Получить IP адрес клиента из запроса"""
    if hasattr(request, 'client') and request.client:
        return request.client.host
    return None


def get_user_agent(request) -> Optional[str]:
    """Получить User-Agent из запроса"""
    if hasattr(request, 'headers'):
        return request.headers.get('user-agent')
    return None

