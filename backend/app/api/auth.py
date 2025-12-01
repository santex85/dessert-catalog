from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user_by_username,
    get_user_by_email,
    get_current_user,
    get_current_admin_user,
)
from app.schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    UserLogin,
    UpdateEmailRequest,
    UpdatePasswordRequest,
    ProfileUpdateResponse,
    UpdateCompanyProfileRequest
)
from app.auth import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверка существования username
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )
    
    # Проверка существования email
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Создание нового пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=False  # Первый пользователь может быть админом, но лучше сделать отдельную логику
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin,
            logo_url=user.logo_url,
            company_name=user.company_name,
            manager_contact=user.manager_contact,
            catalog_description=user.catalog_description,
            created_at=user.created_at
        )
    )


@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя через JSON (альтернатива OAuth2)"""
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin,
            logo_url=user.logo_url,
            company_name=user.company_name,
            manager_contact=user.manager_contact,
            catalog_description=user.catalog_description,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/admin/check")
def check_admin_access(current_user: User = Depends(get_current_admin_user)):
    """Проверка доступа администратора"""
    return {"is_admin": True, "username": current_user.username}


@router.put("/profile/email", response_model=ProfileUpdateResponse)
def update_email(
    email_data: UpdateEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить email пользователя"""
    # Проверка, что новый email не занят другим пользователем
    existing_user = get_user_by_email(db, email_data.email)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Обновление email
    current_user.email = email_data.email
    db.commit()
    db.refresh(current_user)
    
    return ProfileUpdateResponse(
        message="Email updated successfully",
        user=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            is_active=current_user.is_active,
            is_admin=current_user.is_admin,
            logo_url=current_user.logo_url,
            company_name=current_user.company_name,
            manager_contact=current_user.manager_contact,
            catalog_description=current_user.catalog_description,
            created_at=current_user.created_at
        )
    )


@router.put("/profile/password", response_model=ProfileUpdateResponse)
def update_password(
    password_data: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменить пароль пользователя"""
    # Проверка текущего пароля
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Проверка, что новый пароль отличается от текущего
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Обновление пароля
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(current_user)
    
    return ProfileUpdateResponse(
        message="Password updated successfully",
        user=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            is_active=current_user.is_active,
            is_admin=current_user.is_admin,
            logo_url=current_user.logo_url,
            company_name=current_user.company_name,
            manager_contact=current_user.manager_contact,
            catalog_description=current_user.catalog_description,
            created_at=current_user.created_at
        )
    )


@router.put("/profile/company", response_model=ProfileUpdateResponse)
def update_company_profile(
    profile_data: UpdateCompanyProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить профиль компании (логотип, название, контакты, описание)"""
    # Обновление полей профиля компании
    if profile_data.logo_url is not None:
        current_user.logo_url = profile_data.logo_url
    if profile_data.company_name is not None:
        current_user.company_name = profile_data.company_name
    if profile_data.manager_contact is not None:
        current_user.manager_contact = profile_data.manager_contact
    if profile_data.catalog_description is not None:
        current_user.catalog_description = profile_data.catalog_description
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileUpdateResponse(
        message="Company profile updated successfully",
        user=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            is_active=current_user.is_active,
            is_admin=current_user.is_admin,
            logo_url=current_user.logo_url,
            company_name=current_user.company_name,
            manager_contact=current_user.manager_contact,
            catalog_description=current_user.catalog_description,
            created_at=current_user.created_at
        )
    )
