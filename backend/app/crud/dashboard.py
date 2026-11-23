from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.food import Food
from app.models.order import Order, OrderItem
from app.models.user import User


def get_dashboard_stats(db: Session) -> dict:
    revenue_stmt = select(func.sum(Order.final_amount)).where(
        Order.order_status == "Đã hoàn thành"
    )
    total_revenue = db.scalar(revenue_stmt) or 0

    orders_stmt = select(func.count(Order.id))
    total_orders = db.scalar(orders_stmt) or 0

    users_stmt = select(func.count(User.id))
    total_users = db.scalar(users_stmt) or 0

    top_foods_stmt = (
        select(
            Food.id.label("food_id"),
            Food.name.label("name"),
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.total_price).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.food_id == Food.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.order_status == "Đã hoàn thành")
        .group_by(Food.id, Food.name)
        .order_by(desc("total_sold"))
        .limit(5)
    )
    rows = db.execute(top_foods_stmt).all()

    top_foods = [
        {
            "food_id": row.food_id,
            "name": row.name,
            "total_sold": int(row.total_sold or 0),
            "total_revenue": float(row.total_revenue or 0),
        }
        for row in rows
    ]

    return {
        "total_revenue": float(total_revenue),
        "total_orders": int(total_orders),
        "total_users": int(total_users),
        "top_foods": top_foods,
    }
