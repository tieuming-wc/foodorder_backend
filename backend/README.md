# Savoris backend

FastAPI + MySQL. Backend tự tạo bảng còn thiếu, bổ sung các cột thực đơn cho database cũ và nạp 12 món mẫu khi khởi động lần đầu. Việc nạp món có kiểm tra tên nên khởi động lại không tạo bản sao.

## Chuẩn bị lần đầu (Windows PowerShell)

1. Khởi động MySQL Server.
2. Trong MySQL Workbench, chạy `sql/init.sql` để tạo database `app_db`. Nếu bạn dùng database khác, sửa `DB_NAME` trong `.env`.
3. Mở terminal tại thư mục `D:\foodorder_backend\backend`, rồi chạy:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Mở `.env`, điền mật khẩu MySQL vào `DB_PASSWORD` và thay `AUTH_SECRET_KEY` bằng chuỗi bí mật riêng dài ít nhất 32 ký tự. Không chia sẻ hoặc commit `.env`.

4. Cài thư viện và chạy API:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Kiểm tra `http://127.0.0.1:8000/api/health`; kết quả đúng có `"database":"connected"`. Tài liệu API: `http://127.0.0.1:8000/docs`.

Nếu PowerShell chặn kích hoạt môi trường ảo, dùng `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` và `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.

## API chính

- `GET /api/items`: thực đơn; hỗ trợ tìm kiếm `?q=...`.
- `GET /api/items/popular`: tối đa 4 món được đặt nhiều nhất, xếp theo tổng số lượng trong đơn hàng.
- `POST /api/auth/register`, `POST /api/auth/login`, `GET/PUT /api/auth/me`.
- `PUT /api/auth/me/password`.
- `POST /api/orders`: tạo đơn, server tự tính lại giá/voucher/phí giao hàng.
- `GET /api/orders`: lịch sử đơn của người đăng nhập.

Voucher mẫu: `SAVORIS10` giảm 10% (tối đa 200.000đ); `WELCOME15` giảm 15% (tối đa 300.000đ, đơn từ 300.000đ). Phí giao hàng hiện là 30.000đ.

## Thanh toán

COD hoạt động đầy đủ. Lựa chọn chuyển khoản hiện ghi nhận đơn ở trạng thái chờ thanh toán, chưa kết nối cổng thanh toán trực tuyến; muốn nhận tiền tự động cần cấu hình thông tin ngân hàng/cổng thanh toán của cửa hàng.

Database cũ không cần xóa dữ liệu: lúc khởi động backend tự thêm các cột menu bị thiếu và tạo bảng đơn hàng. `sql/init.sql` chỉ cần chạy lần đầu để tạo database.
