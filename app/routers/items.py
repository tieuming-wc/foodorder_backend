"""API CRUD mẫu cho items. Đường dẫn đầy đủ: /api/items

    GET    /api/items          danh sách (tìm theo tên: ?q=com, sắp xếp: ?sort=id_desc)
    GET    /api/items/{id}     chi tiết 1 item
    POST   /api/items          thêm mới
    PUT    /api/items/{id}     sửa
    DELETE /api/items/{id}     xoá

`sort` nhận: id_desc (mặc định), id_asc, price_asc, price_desc. Giá trị khác -> 422.

Phân quyền: mọi API đều cần đăng nhập (Authorization: Bearer <token>).
    GET              -> user đã đăng nhập là xem được
    POST/PUT/DELETE  -> chỉ admin (users.is_admin = 1), user thường nhận 403
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user
from app.crud import item as item_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["Items"])


def get_item_or_404(item_id: int, db: Session = Depends(get_db)):
    item = item_crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy item id={item_id}")
    return item


@router.get("", response_model=list[ItemOut])
def list_items(
    q: str | None = None,
    sort: Literal["id_desc", "id_asc", "price_asc", "price_desc"] = Query(
        default="id_desc",
        description="Thứ tự sắp xếp: id_desc (mặc định), id_asc, price_asc, price_desc",
    ),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return item_crud.get_items(db, keyword=q, sort=sort)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item=Depends(get_item_or_404), _current_user: User = Depends(get_current_user)):
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return item_crud.create_item(db, data)


@router.put("/{item_id}", response_model=ItemOut)
def update_item(
    data: ItemUpdate,
    # Kiểm tra quyền TRƯỚC khi tìm item: user thường luôn nhận 403, không bị lộ
    # item nào có thật hay không qua 404.
    _admin: User = Depends(get_current_admin),
    item=Depends(get_item_or_404),
    db: Session = Depends(get_db),
):
    return item_crud.update_item(db, item, data)


# 204 = "không có nội dung": phải trả về body rỗng, không được để FastAPI tự sinh "null"
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_item(
    _admin: User = Depends(get_current_admin),
    item=Depends(get_item_or_404),
    db: Session = Depends(get_db),
) -> Response:
    item_crud.delete_item(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
