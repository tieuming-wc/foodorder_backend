"""API danh mục món ăn. Đường dẫn đầy đủ: /api/categories

    GET    /api/categories         danh sách danh mục (kèm số món) - user đã đăng nhập
    POST   /api/categories         thêm danh mục (chỉ admin)
    PUT    /api/categories/{id}    sửa danh mục (chỉ admin)
    DELETE /api/categories/{id}    xoá danh mục (chỉ admin); món vẫn còn, chỉ mất danh mục
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user
from app.crud import category as category_crud
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


def _to_out(category: Category, item_count: int = 0) -> CategoryOut:
    out = CategoryOut.model_validate(category)
    out.item_count = item_count
    return out


def get_category_or_404(category_id: int, db: Session = Depends(get_db)) -> Category:
    category = category_crud.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy danh mục id={category_id}")
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return [_to_out(category, count) for category, count in category_crud.get_categories(db)]


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if category_crud.get_category_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail=f"Danh mục '{data.name}' đã tồn tại")
    return _to_out(category_crud.create_category(db, data))


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    data: CategoryUpdate,
    _admin: User = Depends(get_current_admin),
    category: Category = Depends(get_category_or_404),
    db: Session = Depends(get_db),
):
    if data.name and data.name != category.name:
        existing = category_crud.get_category_by_name(db, data.name)
        if existing is not None and existing.id != category.id:
            raise HTTPException(status_code=400, detail=f"Danh mục '{data.name}' đã tồn tại")
    return _to_out(category_crud.update_category(db, category, data))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_category(
    _admin: User = Depends(get_current_admin),
    category: Category = Depends(get_category_or_404),
    db: Session = Depends(get_db),
) -> Response:
    category_crud.delete_category(db, category)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
