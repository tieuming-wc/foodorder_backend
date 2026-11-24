import unittest
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import Item, Order, OrderItem, User
from app.routers.items import list_popular_items
from app.schemas.item import PopularItemOut


class PopularItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        self.user = User(
            full_name="Nguyễn An",
            phone="0900000000",
            email="an@example.com",
            hashed_password="hash",
        )
        self.best_seller = Item(name="Món bán chạy", price=Decimal("100000"))
        self.second_best = Item(name="Món thứ hai", price=Decimal("80000"))
        self.unavailable = Item(
            name="Món đã ngừng bán",
            price=Decimal("50000"),
            is_available=False,
        )
        self.db.add_all(
            [self.user, self.best_seller, self.second_best, self.unavailable]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add_order_item(self, item: Item, quantity: int):
        order = Order(
            user_id=self.user.id,
            recipient_name="Nguyễn An",
            phone_number="0900000000",
            address_line="123 Đường Một",
            subtotal=Decimal("100000"),
            shipping_fee=Decimal("30000"),
            discount_amount=Decimal("0"),
            total_amount=Decimal("130000"),
            payment_method="cod",
            payment_status="pending",
            status="pending",
        )
        self.db.add(order)
        self.db.flush()
        self.db.add(
            OrderItem(
                order_id=order.id,
                item_id=item.id,
                item_name=item.name,
                quantity=quantity,
                unit_price=item.price,
                total_price=item.price * quantity,
            )
        )
        self.db.commit()

    def test_orders_by_total_quantity_and_omits_unavailable_items(self):
        self.add_order_item(self.best_seller, 2)
        self.add_order_item(self.best_seller, 3)
        self.add_order_item(self.second_best, 4)
        self.add_order_item(self.unavailable, 10)

        popular = list_popular_items(self.db)

        self.assertEqual(
            [entry["item"].id for entry in popular],
            [self.best_seller.id, self.second_best.id],
        )
        self.assertEqual(
            [entry["sold_quantity"] for entry in popular],
            [5, 4],
        )
        response = PopularItemOut.model_validate(popular[0])
        self.assertEqual(response.item.name, "Món bán chạy")
        self.assertEqual(response.sold_quantity, 5)

    def test_returns_empty_list_when_there_are_no_orders(self):
        self.assertEqual(list_popular_items(self.db), [])


if __name__ == "__main__":
    unittest.main()
