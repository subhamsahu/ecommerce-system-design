from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user, hash_password, require_admin
from app.auth.schemas import UserCreate, UserResponse
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, min_length=1, max_length=320)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class AdminUserUpdate(ProfileUpdate):
    role: models.UserRole | None = None
    is_active: bool | None = None


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: models.User = Depends(get_current_user)):
    """Return the authenticated user's profile.

    Returns:
        The current user's public profile.

    Raises:
        HTTPException: 401 if the bearer token is missing or invalid.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(updates: ProfileUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Update fields on the authenticated user's profile.

    Args:
        updates: Optional full name, email, or password changes.

    Returns:
        The updated user profile.

    Raises:
        HTTPException: 401 if unauthenticated; 409 if the email is already in use; 422 for invalid input.
    """
    if updates.email:
        email = updates.email.strip().lower()
        duplicate = db.query(models.User).filter(models.User.email == email, models.User.id != current_user.id).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Email already registered")
        current_user.email = email
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    if updates.password:
        current_user.hashed_password = hash_password(updates.password)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """List all user profiles in creation order.

    Returns:
        A list of user profiles.

    Raises:
        HTTPException: 401 if unauthenticated or 403 if the user is not an administrator.
    """
    return db.query(models.User).order_by(models.User.created_at).all()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """Create a user account as an administrator.

    Args:
        user_in: Username, email, name, password, and role for the account.

    Returns:
        The created user profile.

    Raises:
        HTTPException: 401 if unauthenticated, 403 if not an administrator, 409 if the username or email conflicts, or 422 for invalid input.
    """
    username = user_in.username.strip().lower()
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    email = user_in.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    user = models.User(
        username=username,
        email=email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="User conflicts with an existing record") from exc
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updates: AdminUserUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """Update a user's profile, role, or active status as an administrator.

    Args:
        user_id: ID of the user to update.
        updates: Optional profile, role, and active-status changes.

    Returns:
        The updated user profile.

    Raises:
        HTTPException: 401 if unauthenticated, 403 if not an administrator, 404 if the user does not exist, 409 if the email conflicts, or 422 for invalid input.
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if updates.role is not None:
        user.role = updates.role
    if updates.is_active is not None:
        user.is_active = updates.is_active
    if updates.email is not None:
        email = updates.email.strip().lower()
        duplicate = db.query(models.User).filter(models.User.email == email, models.User.id != user.id).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Email already exists")
        user.email = email
    if updates.full_name is not None:
        user.full_name = updates.full_name
    if updates.password:
        user.hashed_password = hash_password(updates.password)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="User conflicts with an existing record") from exc
    db.refresh(user)
    return user
