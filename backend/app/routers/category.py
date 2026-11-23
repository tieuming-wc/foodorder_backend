from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.deps import get_current_admin_user
from app.models.category import Category
from app.models.food import Food
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(
        Category.display_order.asc()).all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    existing_category = db.query(Category).filter(
        Category.name == category_in.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tên danh mục này đã tồn tại, vui lòng chọn tên khác."
        )

    new_category = Category(
        name=category_in.name,
        image=category_in.image,
        display_order=category_in.display_order
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy danh mục cần cập nhật."
        )

    if category_in.name and category_in.name != category.name:
        name_check = db.query(Category).filter(
            Category.name == category_in.name).first()
        if name_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tên danh mục này đã tồn tại."
            )
        category.name = category_in.name

    if category_in.image is not None:
        category.image = category_in.image
    if category_in.display_order is not None:
        category.display_order = category_in.display_order

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy danh mục."
        )

    foods_in_category = db.query(Food).filter(
        Food.category_id == category_id).first()
    if foods_in_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa danh mục vì vẫn còn món ăn thuộc danh mục này."
        )

    db.delete(category)
    db.commit()
    return {"detail": "Xóa danh mục thành công."}
