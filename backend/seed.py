from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.food import Food
from app.models.category import Category
from app.db.session import SessionLocal
import os
import sys
from sqlalchemy.orm import Session

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
APP_DIR = os.path.join(CURRENT_DIR, "app")

for path in (CURRENT_DIR, BACKEND_ROOT, APP_DIR):
    if path not in sys.path:
        sys.path.append(path)


def seed_data():
    db: Session = SessionLocal()
    try:
        print("🌱 Bắt đầu seed dữ liệu mẫu cho FoodOrder...")

        categories_data = [
            {"name": "Món Chính", "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5", "display_order": 1},
            {"name": "Đồ Uống", "image": "https://images.unsplash.com/photo-1551024709-8f23befc6f87", "display_order": 2},
            {"name": "Đồ Ăn Nhanh",
                "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd", "display_order": 3},
            {"name": "Tráng Miệng",
                "image": "https://images.unsplash.com/photo-1551024709-8f23befc6f87", "display_order": 4},
            {"name": "Món Ăn Vặt", "image": "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5", "display_order": 5},
            {"name": "Salad & Healthy",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd", "display_order": 6},
        ]

        created_categories = []
        for cat_data in categories_data:
            existing_cat = db.query(Category).filter(
                Category.name == cat_data["name"]).first()
            if not existing_cat:
                category = Category(**cat_data)
                db.add(category)
                db.commit()
                db.refresh(category)
                created_categories.append(category)
                print(f"Đã tạo danh mục: {category.name}")
            else:
                created_categories.append(existing_cat)
                print(f"Danh mục đã tồn tại: {existing_cat.name}")

        foods_data = [
            {"category_idx": 0, "name": "Cơm rang dưa bò", "description": "Cơm rang giòn hòa quyện với thịt bò và dưa chua",
                "price": 45000, "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b"},
            {"category_idx": 0, "name": "Phở bò đặc biệt", "description": "Phở bò truyền thống nước dùng đậm đà",
                "price": 50000, "image": "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43"},
            {"category_idx": 0, "name": "Bún chả Hà Nội", "description": "Bún chả nướng than hoa thơm lừng",
                "price": 40000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624"},
            {"category_idx": 0, "name": "Cơm gà sốt cay", "description": "Cơm gà giòn rụm sốt cay Hàn Quốc",
                "price": 55000, "image": "https://images.unsplash.com/photo-1562967914-608f82629710"},
            {"category_idx": 0, "name": "Mì xào hải sản", "description": "Mì tươi xào tôm mực tươi ngon",
                "price": 60000, "image": "https://images.unsplash.com/photo-1552611052-33e04de081de"},

            {"category_idx": 1, "name": "Trà sữa trân châu đường đen", "description": "Trà sữa thơm béo kèm trân châu dai giòn",
                "price": 35000, "image": "https://images.unsplash.com/photo-1541658016709-82535e94bc69"},
            {"category_idx": 1, "name": "Trà đào cam sả", "description": "Trà đào thanh mát giải nhiệt mùa hè",
                "price": 30000, "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc"},
            {"category_idx": 1, "name": "Cà phê sữa đá", "description": "Cà phê nguyên chất đậm đà vị Việt",
                "price": 25000, "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd"},
            {"category_idx": 1, "name": "Sinh tố bơ", "description": "Sinh tố bơ dầm đặc sánh thơm béo",
                "price": 40000, "image": "https://images.unsplash.com/photo-1553530666-ba11a7da3888"},
            {"category_idx": 1, "name": "Nước ép cam tươi", "description": "Cam tươi vắt nguyên chất giàu vitamin C",
                "price": 35000, "image": "https://images.unsplash.com/photo-1613478223719-2ab802602423"},

            {"category_idx": 2, "name": "Hamburger bò phô mai", "description": "Bánh mì kẹp thịt bò nướng và phô mai chảy",
                "price": 45000, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"},
            {"category_idx": 2, "name": "Pizza hải sản cỡ vừa", "description": "Pizza đế mỏng phủ phô mai và tôm mực",
                "price": 120000, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591"},
            {"category_idx": 2, "name": "Gà rán lắc sốt cay (3 miếng)", "description": "Gà rán giòn rụm đậm vị",
                "price": 55000, "image": "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58"},
            {"category_idx": 2, "name": "Khoai tây chiên", "description": "Khoai tây chiên giòn rụm kèm sốt mayonnaise",
                "price": 25000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877"},
            {"category_idx": 2, "name": "Xúc xích Đức nướng", "description": "Xúc xích nướng thơm mùi khói",
                "price": 30000, "image": "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f"},

            {"category_idx": 3, "name": "Chè hạt sen long nhãn", "description": "Chè thanh ngọt từ hạt sen tươi và long nhãn",
                "price": 30000, "image": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac"},
            {"category_idx": 3, "name": "Chè khúc bạch phô mai", "description": "Khúc bạch béo ngậy kết hợp hạnh nhân rang giòn",
                "price": 35000, "image": "https://images.unsplash.com/photo-1560008511-11c63416e52d"},
            {"category_idx": 3, "name": "Bánh Mousse Chanh Dây", "description": "Bánh kem lạnh chua ngọt thơm vị chanh dây tự nhiên",
                "price": 45000, "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff"},
            {"category_idx": 3, "name": "Kem trái dừa", "description": "Kem mát lạnh đựng trong gáo dừa tươi",
                "price": 35000, "image": "https://images.unsplash.com/photo-1560008511-11c63416e52d"},
            {"category_idx": 3, "name": "Sữa chua dẻo trái cây", "description": "Sữa chua cắt miếng dẻo mịn kết hợp hoa quả tươi",
                "price": 35000, "image": "https://images.unsplash.com/photo-1571115177098-24ec42ed204d"},

            {"category_idx": 4, "name": "Nem chua rán Hà Nội", "description": "Nem chua tẩm bột chiên xù giòn rụm, chấm kèm tương ớt cay ngọt",
                "price": 30000, "image": "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5"},
            {"category_idx": 4, "name": "Khoai tây lốc xoáy", "description": "Khoai tây cắt xoắn chiên giòn rụm rắc bột phô mai béo ngậy",
                "price": 25000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877"},
            {"category_idx": 4, "name": "Bạch tuộc nướng sa tế", "description": "Bạch tuộc tươi giòn cay cay vị sa tế",
                "price": 70000, "image": "https://images.unsplash.com/photo-1544025162-d76694265947"},
            {"category_idx": 4, "name": "Cá viên chiên mắm tỏi", "description": "Cá viên sốt mắm tỏi đậm đà kích thích vị giác",
                "price": 30000, "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8"},
            {"category_idx": 4, "name": "Khoai lang lắc phô mai", "description": "Khoai lang giòn phủ bột phô mai thơm phức",
                "price": 30000, "image": "https://images.unsplash.com/photo-1585109649139-366815a0d713"},

            {"category_idx": 5, "name": "Salad cá hồi xông khói", "description": "Cá hồi tươi kết hợp rau xanh và sốt mè rang",
                "price": 75000, "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999"},
            {"category_idx": 5, "name": "Salad ức gà sốt chanh leo", "description": "Ức gà áp chảo ăn kèm rau củ tươi sạch",
                "price": 55000, "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"},
            {"category_idx": 5, "name": "Ức gà áp chảo ngũ cốc", "description": "Thực đơn giảm cân giàu protein và chất xơ",
                "price": 60000, "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"},
            {"category_idx": 5, "name": "Sinh tố thanh lọc cơ thể (Green Detox)", "description": "Rau bó xôi, táo xanh và cần tây nguyên chất",
                "price": 40000, "image": "https://images.unsplash.com/photo-1610970881699-44a5587cabec"},
            {"category_idx": 5, "name": "Sữa chua hạt dưa Hy Lạp", "description": "Sữa chua nguyên chất kèm các loại hạt dinh dưỡng",
                "price": 45000, "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777"},
        ]

        for food_item in foods_data:
            cat_idx = food_item.pop("category_idx")
            target_category = created_categories[cat_idx]

            existing_food = db.query(Food).filter(
                Food.name == food_item["name"]).first()
            if not existing_food:
                food = Food(**food_item, category_id=target_category.id)
                db.add(food)
                db.commit()
                print(
                    f"Đã thêm món: {food.name} vào danh mục {target_category.name}")

        users_seed = [
            {
                "username": "admin_demo",
                "email": "admin@foodorder.local",
                "password_hash": "hashed_admin_password_123",
                "full_name": "Admin FoodOrder",
                "role": "admin",
                "status": 1,
            },
            {
                "username": "user1_demo",
                "email": "user1@foodorder.local",
                "password_hash": "hashed_user1_password_123",
                "full_name": "Nguyễn Văn A",
                "role": "customer",
                "status": 1,
            },
            {
                "username": "user2_demo",
                "email": "user2@foodorder.local",
                "password_hash": "hashed_user2_password_123",
                "full_name": "Trần Thị B",
                "role": "customer",
                "status": 1,
            },
        ]

        seeded_users = []
        for u_data in users_seed:
            existing_user = db.query(User).filter(
                User.email == u_data["email"]).first()
            if not existing_user:
                u = User(**u_data)
                db.add(u)
                db.commit()
                db.refresh(u)
                seeded_users.append(u)
            else:
                seeded_users.append(existing_user)

        all_foods = db.query(Food).order_by(Food.id.asc()).all()
        customer = next(
            (u for u in seeded_users if u.role == "customer"),
            seeded_users[0],
        )

        if len(all_foods) >= 3 and db.query(Order).count() == 0:
            orders_spec = [
                {
                    "order_status": "Đã hoàn thành",
                    "payment_method": "COD",
                    "payment_status": "Đã thanh toán",
                    "discount_amount": 0,
                    "lines": [
                        (all_foods[0], 3),
                        (all_foods[1], 2),
                    ],
                },
                {
                    "order_status": "Đã hoàn thành",
                    "payment_method": "Banking",
                    "payment_status": "Đã thanh toán",
                    "discount_amount": 10000,
                    "lines": [
                        (all_foods[0], 2),
                        (all_foods[2], 4),
                    ],
                },
                {
                    "order_status": "Chờ xác nhận",
                    "payment_method": "COD",
                    "payment_status": "Chưa thanh toán",
                    "discount_amount": 0,
                    "lines": [
                        (all_foods[1], 5),
                    ],
                },
            ]

            for spec in orders_spec:
                raw_total = sum(float(f.price) * qty for f,
                                qty in spec["lines"])
                discount = float(spec["discount_amount"])
                final_amt = max(0.0, raw_total - discount)

                order = Order(
                    user_id=customer.id,
                    total_amount=raw_total,
                    discount_amount=discount,
                    final_amount=final_amt,
                    payment_method=spec["payment_method"],
                    payment_status=spec["payment_status"],
                    order_status=spec["order_status"],
                )
                db.add(order)
                db.commit()
                db.refresh(order)

                for food_obj, qty in spec["lines"]:
                    line_total = float(food_obj.price) * qty
                    db.add(
                        OrderItem(
                            order_id=order.id,
                            food_id=food_obj.id,
                            quantity=qty,
                            price=food_obj.price,
                            total_price=line_total,
                        )
                    )
                db.commit()

        print("🎉 Seed dữ liệu mẫu thành công hoàn toàn!")
    except Exception as e:
        print(f"❌ Lỗi khi seed dữ liệu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
