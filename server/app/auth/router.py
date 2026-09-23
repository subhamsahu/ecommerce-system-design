from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.auth.dependencies import create_access_token, hash_password, verify_password
from app.auth.schemas import LoginRequest, Token, UserCreate, UserResponse
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    username = user_in.username.strip().lower()
    email = user_in.email.strip().lower() if user_in.email else None
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already registered")
    if email and db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = models.User(
        username=username,
        email=email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role=models.UserRole.customer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    username = login_data.username.strip().lower()
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.is_active or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer", "user": user}