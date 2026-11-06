"""Test model giỏ hàng và schema trả về (chạy bằng SQLite trong bộ nhớ).

Chạy trong thư mục `backend/`:

    python -m unittest discover -s tests -v
"""
import unittest
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import Cart, CartItem, Food, User
from app.schemas.cart import CartOut


class CartTestCase(unittest.TestCase):
    def setUp(self):
        # SQLite trong bộ nhớ: không cần MySQL, mỗi test có DB sạch
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        self.user = User(
            username="an", email="an@example.com", password_hash="hash", full_name="Nguyễn An"
        )
        self.com = Food(name="Cơm rang", price=Decimal("45000"), stock=10)
        self.tra = Food(name="Trà đá", price=Decimal("5000"), stock=100)
        self.db.add_all([self.user, self.com, self.tra])
        self.db.commit()

        self.cart = Cart(user_id=self.user.id)
        self.db.add(self.cart)
        self.db.commit()
        self.db.add_all(
            [
                CartItem(cart_id=self.cart.id, food_id=self.com.id, quantity=2),
                CartItem(cart_id=self.cart.id, food_id=self.tra.id, quantity=3),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_schema_tra_ve_thong_tin_mon_va_thanh_tien(self):
        out = CartOut.model_validate(self.cart)

        self.assertEqual(out.user_id, self.user.id)
        self.assertEqual([item.food.name for item in out.items], ["Cơm rang", "Trà đá"])
        self.assertEqual([item.quantity for item in out.items], [2, 3])
        # thành tiền từng dòng
        self.assertEqual(out.items[0].line_total, 90000.0)  # 45.000 × 2
        self.assertEqual(out.items[1].line_total, 15000.0)  # 5.000 × 3
        # tổng của cả giỏ
        self.assertEqual(out.total_quantity, 5)
        self.assertEqual(out.total_price, 105000.0)

    def test_computed_field_co_trong_json(self):
        data = CartOut.model_validate(self.cart).model_dump()

        self.assertEqual(data["total_price"], 105000.0)
        self.assertEqual(data["total_quantity"], 5)
        self.assertEqual(data["items"][0]["line_total"], 90000.0)

    def test_gio_rong_thanh_tien_bang_0(self):
        empty = Cart(user_id=self.user.id + 1)
        self.db.add(empty)
        self.db.commit()

        out = CartOut.model_validate(empty)
        self.assertEqual(out.items, [])
        self.assertEqual(out.total_quantity, 0)
        self.assertEqual(out.total_price, 0.0)

    def test_khong_duoc_trung_mon_trong_cung_gio(self):
        self.db.add(CartItem(cart_id=self.cart.id, food_id=self.com.id, quantity=1))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_moi_user_chi_co_mot_gio(self):
        self.db.add(Cart(user_id=self.user.id))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_so_luong_phai_duong(self):
        rau = Food(name="Rau muống", price=Decimal("10000"), stock=5)
        self.db.add(rau)
        self.db.commit()

        self.db.add(CartItem(cart_id=self.cart.id, food_id=rau.id, quantity=0))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_xoa_gio_thi_xoa_luon_cac_dong(self):
        self.db.delete(self.cart)
        self.db.commit()

        con_lai = self.db.scalars(select(CartItem)).all()
        self.assertEqual(con_lai, [])


if __name__ == "__main__":
    unittest.main()
