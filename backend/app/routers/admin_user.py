from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.core.deps import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserListResponse, UserOut, UpdateRoleRequest, UpdateStatusRequest

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get("", response_model=UserListResponse)
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    query = db.query(User)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )

    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"total": total, "items": users}


@router.put("/{id}/role", response_model=UserOut)
def update_user_role(
    id: int,
    body: UpdateRoleRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy người dùng")

    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


@router.put("/{id}/status", response_model=UserOut)
def update_user_status(
    id: int,
    body: UpdateStatusRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy người dùng")

    user.status = body.status
    db.commit()
    db.refresh(user)
    return user
