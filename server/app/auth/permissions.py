from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user, require_admin
from app.core.database import get_db

router = APIRouter(prefix="/permissions", tags=["Permissions"])


class PermissionsUpdateRequest(BaseModel):
    permissions: Dict[str, bool]


def _ensure_seeded(db: Session) -> None:
    for role_name, permission_set in models.DEFAULT_ROLE_PERMISSIONS.items():
        role = models.UserRole(role_name)
        exists = db.query(models.RolePermissions).filter(models.RolePermissions.role == role).first()
        if not exists:
            db.add(models.RolePermissions(role=role, permissions=permission_set))
    db.commit()


@router.get("", response_model=Dict[str, Dict[str, bool]])
def get_all_permissions(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    _ensure_seeded(db)
    rows = db.query(models.RolePermissions).all()
    return {row.role.value: row.permissions for row in rows}


@router.put("/{role}", response_model=Dict[str, bool])
def update_role_permissions(
    role: str,
    body: PermissionsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if role == "admin":
        raise HTTPException(status_code=400, detail="Admin permissions cannot be changed")

    try:
        role_enum = models.UserRole(role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"Role '{role}' not found") from exc

    _ensure_seeded(db)
    row = db.query(models.RolePermissions).filter(models.RolePermissions.role == role_enum).first()
    if not row:
        raise HTTPException(status_code=404, detail="Permissions record not found")

    row.permissions = body.permissions
    row.updated_by = current_user.id
    db.commit()
    db.refresh(row)
    return row.permissions