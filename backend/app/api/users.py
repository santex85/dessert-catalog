"""
API endpoints для управления пользователями (только для администраторов)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User
from app.auth import get_current_admin_user
from app.schemas import UserResponse, UserUpdateRequest, UserListResponse
from app.logger import log_activity, get_client_ip, get_user_agent
from typing import Optional

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Получить список всех пользователей (только для администраторов)"""
    query = db.query(User)
    
    # Поиск по username или email
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.company_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return UserListResponse(
        users=[UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            is_admin=u.is_admin,
            is_moderator=u.is_moderator,
            logo_url=u.logo_url,
            company_name=u.company_name,
            manager_contact=u.manager_contact,
            catalog_description=u.catalog_description,
            created_at=u.created_at
        ) for u in users],
        total=total
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Получить информацию о пользователе по ID (только для администраторов)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_moderator=user.is_moderator,
        logo_url=user.logo_url,
        company_name=user.company_name,
        manager_contact=user.manager_contact,
        catalog_description=user.catalog_description,
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Обновить пользователя (только для администраторов)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Сохраняем старые значения для лога
    old_values = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_moderator": user.is_moderator,
        "company_name": user.company_name,
        "manager_contact": user.manager_contact,
        "catalog_description": user.catalog_description,
    }
    
    # Обновляем поля
    if user_data.email is not None:
        # Проверяем, что email не занят другим пользователем
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        user.email = user_data.email
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.is_admin is not None:
        # Не позволяем убрать права администратора у самого себя
        if user_id == current_user.id and not user_data.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove admin rights from yourself"
            )
        user.is_admin = user_data.is_admin
    
    if user_data.is_moderator is not None:
        user.is_moderator = user_data.is_moderator
    
    if user_data.company_name is not None:
        user.company_name = user_data.company_name
    
    if user_data.manager_contact is not None:
        user.manager_contact = user_data.manager_contact
    
    if user_data.catalog_description is not None:
        user.catalog_description = user_data.catalog_description
    
    db.commit()
    db.refresh(user)
    
    # Логируем изменение
    new_values = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_moderator": user.is_moderator,
        "company_name": user.company_name,
        "manager_contact": user.manager_contact,
        "catalog_description": user.catalog_description,
    }
    
    log_activity(
        db=db,
        action="user_update",
        user=current_user,
        entity_type="user",
        entity_id=user.id,
        description=f"Admin {current_user.username} updated user {user.username}",
        old_values=old_values,
        new_values=new_values,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_moderator=user.is_moderator,
        logo_url=user.logo_url,
        company_name=user.company_name,
        manager_contact=user.manager_contact,
        catalog_description=user.catalog_description,
        created_at=user.created_at
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Удалить пользователя (только для администраторов)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Не позволяем удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Сохраняем информацию для лога перед удалением
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    
    db.delete(user)
    db.commit()
    
    # Логируем удаление
    log_activity(
        db=db,
        action="user_delete",
        user=current_user,
        entity_type="user",
        entity_id=user_id,
        description=f"Admin {current_user.username} deleted user {user.username}",
        old_values=user_info,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return None

