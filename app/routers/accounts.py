"""API quản lý tài khoản cho admin (trang /admin).

    GET /api/admin/accounts              danh sách 10 tài khoản, lọc ?role=
    PUT /api/admin/accounts/{id}/role    đổi vai trò của một tài khoản
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, USER_ROLES, User
from app.schemas.user import UserOut, UserRoleUpdate

router = APIRouter(
    prefix="/admin/accounts",
    tags=["Admin - Accounts"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[UserOut])
def list_accounts(
    role: str | None = Query(
        default=None,
        description="Lọc theo vai trò: admin, customer, restaurant, shipper",
    ),
    db: Session = Depends(get_db),
):
    """Danh sách tài khoản (không bao giờ trả mật khẩu)."""
    if role is not None and role not in USER_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Vai trò không hợp lệ, chọn một trong: {', '.join(USER_ROLES)}",
        )
    return user_crud.list_users(db, role=role)


@router.put("/{user_id}/role", response_model=UserOut)
def update_account_role(
    user_id: int,
    data: UserRoleUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Đổi vai trò. Không tự đổi vai trò của chính mình để khỏi mất quyền admin."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Không thể tự đổi vai trò của chính mình",
        )
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản id={user_id}")

    user.role = data.role
    # Giữ is_admin đồng bộ với role để các API cũ kiểm tra is_admin vẫn đúng
    user.is_admin = data.role == ROLE_ADMIN
    db.commit()
    db.refresh(user)
    return user
