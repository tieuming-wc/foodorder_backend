from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud.recommendation import get_recommended_foods
from app.db.session import get_db
from app.schemas.recommendation import RecommendedFoodItem

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=list[RecommendedFoodItem])
def list_recommended_foods(
    context: Literal["home", "food_detail", "cart"] = Query(
        default="home",
        description="Vị trí hiển thị: Trang chủ, Chi tiết món, Giỏ hàng",
    ),
    food_id: int | None = Query(
        default=None,
        description="ID món ăn đang xem",
    ),
    user_id: int | None = Query(
        default=None,
        description="ID người dùng để gợi ý theo lịch sử đặt món gần đây",
    ),
    exclude_ids: list[int] | None = Query(
        default=None,
        description="Danh sách ID món cần loại trừ",
    ),
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return get_recommended_foods(
        db=db,
        context=context,
        food_id=food_id,
        user_id=user_id,
        exclude_ids=exclude_ids,
        limit=limit,
    )
