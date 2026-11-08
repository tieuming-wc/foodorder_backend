"""Test API giỏ hàng (POST /api/cart/items, GET /api/cart) bằng SQLite trong bộ nhớ.

Chạy trong thư mục `backend/`:

    python -m unittest discover -s tests -v
"""
import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token
from app.db.session import Base, get_db
from app.main import app
from app.models import Food, User


class CartApiTestCase(unittest.TestCase):
    def setUp(self):
        # SQLite trong bộ nhớ: không cần MySQL, mỗi test có DB sạch
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

        # Cho API dùng session của SQLite thay vì MySQL
        app.dependency_overrides[get_db] = self._override_get_db
        self.client = TestClient(app)

        db = self.Session()
        self.an = User(
            username="an", email="an@example.com", password_hash="hash", full_name="Nguyễn An"
        )
        self.binh = User(username="binh", email="binh@example.com", password_hash="hash")
        self.com = Food(name="Cơm rang", price=Decimal("45000"), stock=10)
        self.tra = Food(name="Trà đá", price=Decimal("5000"), stock=100)
        self.het_mon = Food(name="Bún chả", price=Decimal("40000"), is_available=False)
        db.add_all([self.an, self.binh, self.com, self.tra, self.het_mon])
        db.commit()

        # Lưu id lại: đóng session xong thì object cũ không đọc thuộc tính được nữa
        self.an_id = self.an.id
        self.binh_id = self.binh.id
        self.com_id = self.com.id
        self.tra_id = self.tra.id
        self.het_mon_id = self.het_mon.id

        self.headers_an = {"Authorization": f"Bearer {create_access_token(self.an_id)}"}
        self.headers_binh = {"Authorization": f"Bearer {create_access_token(self.binh_id)}"}
        db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _override_get_db(self):
        db = self.Session()
        try:
            yield db
        finally:
            db.close()

    def _them_mon(self, food_id, quantity, headers=None):
        return self.client.post(
            "/api/cart/items",
            json={"foodId": food_id, "quantity": quantity},
            headers=self.headers_an if headers is None else headers,
        )

    # ---------------------------------------------------------- bắt buộc login
    def test_chua_dang_nhap_bi_chan(self):
        self.assertEqual(self.client.get("/api/cart").status_code, 401)
        self.assertEqual(self._them_mon(self.com_id, 1, headers={}).status_code, 401)

    def test_token_sai_bi_chan(self):
        headers = {"Authorization": "Bearer abc.def"}
        self.assertEqual(self.client.get("/api/cart", headers=headers).status_code, 401)

    # ------------------------------------------------------------ thêm vào giỏ
    def test_them_mon_moi(self):
        response = self._them_mon(self.com_id, 2)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["food_id"], self.com_id)
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["line_total"], 90000.0)  # 45.000 × 2

    def test_mon_da_co_thi_cong_don_so_luong(self):
        self._them_mon(self.com_id, 2)
        response = self._them_mon(self.com_id, 3)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quantity"], 5)
        self.assertEqual(response.json()["line_total"], 225000.0)

        # vẫn chỉ 1 dòng cho món đó trong giỏ
        cart = self.client.get("/api/cart", headers=self.headers_an).json()
        self.assertEqual(len(cart["items"]), 1)

    def test_mon_ngung_ban_bi_chan(self):
        response = self._them_mon(self.het_mon_id, 1)

        self.assertEqual(response.status_code, 400)
        self.assertIn("ngừng bán", response.json()["detail"])

    def test_mon_khong_ton_tai(self):
        self.assertEqual(self._them_mon(99999, 1).status_code, 404)

    def test_so_luong_khong_hop_le(self):
        self.assertEqual(self._them_mon(self.com_id, 0).status_code, 422)
        self.assertEqual(self._them_mon(self.com_id, -1).status_code, 422)

    # -------------------------------------------------------------- xem giỏ
    def test_get_cart_tra_thanh_tien_va_tong(self):
        self._them_mon(self.com_id, 2)
        self._them_mon(self.tra_id, 3)
        response = self.client.get("/api/cart", headers=self.headers_an)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([item["food"]["name"] for item in data["items"]], ["Cơm rang", "Trà đá"])
        self.assertEqual([item["quantity"] for item in data["items"]], [2, 3])
        self.assertEqual([item["line_total"] for item in data["items"]], [90000.0, 15000.0])
        self.assertEqual(data["total_quantity"], 5)
        self.assertEqual(data["total_price"], 105000.0)

    def test_gio_rong_tra_ve_0(self):
        response = self.client.get("/api/cart", headers=self.headers_binh)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["items"], [])
        self.assertEqual(data["total_quantity"], 0)
        self.assertEqual(data["total_price"], 0.0)

    def test_gio_tach_rieng_tung_user(self):
        self._them_mon(self.com_id, 2)

        cart_cua_an = self.client.get("/api/cart", headers=self.headers_an).json()
        cart_cua_binh = self.client.get("/api/cart", headers=self.headers_binh).json()

        self.assertEqual(cart_cua_an["total_quantity"], 2)
        self.assertEqual(cart_cua_binh["total_quantity"], 0)


if __name__ == "__main__":
    unittest.main()
