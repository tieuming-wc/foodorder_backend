"""Tự thêm các cột mới vào bảng ĐÃ TỒN TẠI khi server khởi động.

`Base.metadata.create_all()` chỉ tạo bảng còn thiếu, KHÔNG thêm cột vào bảng đã có.
Vì vậy code mới chạy trên database cũ sẽ lỗi 500 kiểu
`Unknown column 'users.is_admin' in 'field list'`.

Muốn thêm cột cho 1 model đã có bảng trong DB: thêm 1 dòng vào _COLUMN_MIGRATIONS
bên dưới (cột đã có thì bỏ qua, chạy lại nhiều lần không lỗi).
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# (bảng, cột, câu SQL thêm cột)
_COLUMN_MIGRATIONS: list[tuple[str, str, str]] = [
    (
        "users",
        "is_admin",
        "ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0 "
        "AFTER is_active",
    ),
]


def apply_column_migrations(engine: Engine) -> list[str]:
    """Thêm các cột còn thiếu. Trả về danh sách cột vừa thêm, vd ["users.is_admin"]."""
    applied: list[str] = []
    inspector = inspect(engine)
    for table, column, ddl in _COLUMN_MIGRATIONS:
        if not inspector.has_table(table):
            continue  # bảng chưa có -> create_all đã tạo đúng cấu trúc mới rồi
        if column in {col["name"] for col in inspector.get_columns(table)}:
            continue
        with engine.begin() as conn:
            conn.execute(text(ddl))
        applied.append(f"{table}.{column}")
    return applied
