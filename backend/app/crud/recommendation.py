from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.food import Food
from app.models.order import Order, OrderItem
from app.schemas.recommendation import RecommendedFoodItem


def get_recommended_foods(
    db: Session,
    *,
    context: str = "home",
    food_id: int | None = None,
    user_id: int | None = None,
    exclude_ids: list[int] | None = None,
    limit: int = 8,
) -> list[RecommendedFoodItem]:
    excluded: set[int] = set(exclude_ids or [])
    if food_id is not None:
        excluded.add(food_id)

    results: list[RecommendedFoodItem] = []

    def append_foods(foods: list[Food], reason: str) -> None:
        for food in foods:
            if len(results) >= limit:
                break
            if food.id in excluded:
                continue
            excluded.add(food.id)
            results.append(
                RecommendedFoodItem(
                    id=food.id,
                    category_id=food.category_id,
                    name=food.name,
                    price=food.price,
                    image=food.image,
                    sales_count=food.sales_count,
                    reason=reason,
                )
            )

    if context == "food_detail" and food_id is not None:
        current_food = db.get(Food, food_id)
        if current_food:
            stmt_same_cat = (
                select(Food)
                .where(
                    Food.is_available.is_(True),
                    Food.category_id == current_food.category_id,
                    Food.id.notin_(excluded) if excluded else True,
                )
                .order_by(desc(Food.sales_count), desc(Food.id))
                .limit(limit)
            )
            same_cat_foods = list(db.scalars(stmt_same_cat).all())
            append_foods(same_cat_foods, reason="same_category")

    if len(results) < limit and user_id is not None:
        stmt_recent_food_ids = (
            select(OrderItem.food_id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                Order.user_id == user_id,
                Order.order_status != "Đã hủy",
            )
            .order_by(desc(Order.created_at))
            .limit(limit * 3)
        )
        recent_food_ids = list(dict.fromkeys(
            db.scalars(stmt_recent_food_ids).all()))
        valid_recent_ids = [
            fid for fid in recent_food_ids if fid not in excluded]

        if valid_recent_ids:
            stmt_recent_foods = select(Food).where(
                Food.is_available.is_(True),
                Food.id.in_(valid_recent_ids),
            )
            food_map = {f.id: f for f in db.scalars(stmt_recent_foods).all()}
            ordered_recent_foods = [
                food_map[fid] for fid in valid_recent_ids if fid in food_map
            ]
            append_foods(ordered_recent_foods, reason="recent_order")

    if len(results) < limit:
        stmt_best_sellers = (
            select(Food)
            .where(
                Food.is_available.is_(True),
                Food.id.notin_(excluded) if excluded else True,
            )
            .order_by(desc(Food.sales_count), desc(Food.id))
            .limit(limit - len(results))
        )
        best_sellers = list(db.scalars(stmt_best_sellers).all())
        append_foods(best_sellers, reason="best_seller")

    return results
