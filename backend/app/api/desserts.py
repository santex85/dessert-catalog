from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models import Dessert, User
from app.schemas import DessertCreate, DessertUpdate, DessertResponse
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/desserts", tags=["desserts"])


@router.get("/", response_model=List[DessertResponse])
def get_desserts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Получить список десертов с фильтрацией"""
    query = db.query(Dessert)

    if is_active is not None:
        query = query.filter(Dessert.is_active == is_active)

    if category:
        # Поддержка нескольких категорий через запятую
        # Если указана одна категория, ищем точное совпадение или категорию в списке
        # Если указано несколько категорий через запятую, ищем десерты, у которых есть хотя бы одна из них
        category_list = [cat.strip() for cat in category.split(',')]
        if len(category_list) == 1:
            # Одна категория - ищем точное совпадение или категорию в списке через запятую
            query = query.filter(
                or_(
                    Dessert.category == category_list[0],
                    Dessert.category.like(f"%{category_list[0]}%")
                )
            )
        else:
            # Несколько категорий - ищем десерты, у которых есть хотя бы одна из них
            conditions = []
            for cat in category_list:
                conditions.append(
                    or_(
                        Dessert.category == cat,
                        Dessert.category.like(f"%{cat}%")
                    )
                )
            query = query.filter(or_(*conditions))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Dessert.title.ilike(search_term),
                Dessert.description.ilike(search_term)
            )
        )

    desserts = query.order_by(Dessert.title).offset(skip).limit(limit).all()
    return desserts


@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """Получить список всех категорий (уникальные, разделенные по запятой)"""
    categories_raw = db.query(Dessert.category).distinct().all()
    # Собираем все уникальные категории, разделяя по запятой
    all_categories = set()
    for cat_tuple in categories_raw:
        if cat_tuple[0]:
            # Разделяем категории по запятой и добавляем каждую отдельно
            for cat in cat_tuple[0].split(','):
                all_categories.add(cat.strip())
    return sorted(list(all_categories))


@router.get("/{dessert_id}", response_model=DessertResponse)
def get_dessert(dessert_id: int, db: Session = Depends(get_db)):
    """Получить десерт по ID"""
    dessert = db.query(Dessert).filter(Dessert.id == dessert_id).first()
    if not dessert:
        raise HTTPException(status_code=404, detail="Десерт не найден")
    return dessert


@router.post("/", response_model=DessertResponse, status_code=201)
def create_dessert(
    dessert: DessertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Создать новый десерт (только для администраторов)"""
    db_dessert = Dessert(**dessert.model_dump())
    db.add(db_dessert)
    db.commit()
    db.refresh(db_dessert)
    return db_dessert


@router.put("/{dessert_id}", response_model=DessertResponse)
def update_dessert(
    dessert_id: int,
    dessert: DessertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Обновить десерт (только для администраторов)"""
    db_dessert = db.query(Dessert).filter(Dessert.id == dessert_id).first()
    if not db_dessert:
        raise HTTPException(status_code=404, detail="Десерт не найден")

    update_data = dessert.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dessert, field, value)

    db.commit()
    db.refresh(db_dessert)
    return db_dessert


@router.delete("/{dessert_id}", status_code=204)
def delete_dessert(
    dessert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Удалить десерт (только для администраторов)"""
    db_dessert = db.query(Dessert).filter(Dessert.id == dessert_id).first()
    if not db_dessert:
        raise HTTPException(status_code=404, detail="Десерт не найден")

    db.delete(db_dessert)
    db.commit()
    return None

