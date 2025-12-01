"""
API endpoints для просмотра логов активности (только для администраторов)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.database import get_db
from app.models import ActivityLog, User
from app.auth import get_current_admin_user
from app.schemas import ActivityLogResponse, ActivityLogListResponse
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/", response_model=ActivityLogListResponse)
def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    search: Optional[str] = None,
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter logs for last N days"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Получить список логов активности (только для администраторов)"""
    query = db.query(ActivityLog)
    
    # Фильтр по типу действия
    if action:
        query = query.filter(ActivityLog.action == action)
    
    # Фильтр по типу сущности
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    
    # Фильтр по ID пользователя
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    # Фильтр по имени пользователя
    if username:
        query = query.filter(ActivityLog.username.ilike(f"%{username}%"))
    
    # Поиск по описанию
    if search:
        query = query.filter(ActivityLog.description.ilike(f"%{search}%"))
    
    # Фильтр по дате (последние N дней)
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(ActivityLog.created_at >= cutoff_date)
    
    total = query.count()
    
    # Сортировка по дате (новые сначала)
    logs = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
    
    return ActivityLogListResponse(
        logs=[ActivityLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=log.username,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            description=log.description,
            old_values=log.old_values,
            new_values=log.new_values,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at
        ) for log in logs],
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{log_id}", response_model=ActivityLogResponse)
def get_log(
    log_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Получить конкретную запись лога по ID (только для администраторов)"""
    log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return ActivityLogResponse(
        id=log.id,
        user_id=log.user_id,
        username=log.username,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        description=log.description,
        old_values=log.old_values,
        new_values=log.new_values,
        ip_address=log.ip_address,
        user_agent=log.user_agent,
        created_at=log.created_at
    )


@router.get("/stats/summary")
def get_logs_summary(
    days: int = Query(7, ge=1, le=365, description="Statistics for last N days"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Получить статистику по логам (только для администраторов)"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Общее количество логов
    total_logs = db.query(ActivityLog).filter(ActivityLog.created_at >= cutoff_date).count()
    
    # Количество логов по действиям
    from sqlalchemy import func
    action_stats = db.query(
        ActivityLog.action,
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.created_at >= cutoff_date
    ).group_by(ActivityLog.action).all()
    
    # Количество логов по типам сущностей
    entity_stats = db.query(
        ActivityLog.entity_type,
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.created_at >= cutoff_date,
        ActivityLog.entity_type.isnot(None)
    ).group_by(ActivityLog.entity_type).all()
    
    # Топ пользователей по активности
    user_stats = db.query(
        ActivityLog.username,
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.created_at >= cutoff_date,
        ActivityLog.username.isnot(None)
    ).group_by(ActivityLog.username).order_by(desc('count')).limit(10).all()
    
    return {
        "period_days": days,
        "total_logs": total_logs,
        "actions": {action: count for action, count in action_stats},
        "entities": {entity_type: count for entity_type, count in entity_stats},
        "top_users": [{"username": username, "count": count} for username, count in user_stats]
    }

