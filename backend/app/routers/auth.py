from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.security import SECRET_KEY, ALGORITHM

# Dòng này giúp Swagger UI hiện nút "Authorize" (ổ khoá) để bạn nhập Token test thử
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Chặn email trùng (Lỗi 409)
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email này đã được đăng ký trong hệ thống."
        )
    
    # 2. Mã hoá mật khẩu và lưu database
    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        role="USER"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # FastAPI sẽ tự ép kiểu về schema UserResponse (ẩn mật khẩu)
    return new_user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc không có quyền truy cập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Dùng Secret Key để giải mã JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token đã hết hạn, vui lòng đăng nhập lại!"
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    # Lấy thông tin User từ Database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # 1. Tìm user theo email
    user = db.query(User).filter(User.email == user_in.email).first()
    
    # 2. Kiểm tra user tồn tại và khớp mật khẩu (Lỗi 401)
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác."
        )
    
    # 3. Tạo JWT Access Token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "message": "Đăng nhập thành công"
    }
    
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    API này trả về thông tin cá nhân.
    Nếu chạy được vào trong hàm này nghĩa là Token hợp lệ.
    """
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    API Đăng xuất (Stateless cơ bản).
    Backend xác nhận yêu cầu, Frontend sẽ thực hiện việc xóa Token khỏi Local Storage.
    """
    return {
        "message": f"Tạm biệt {current_user.full_name}, đăng xuất thành công!",
        "action_required": "Frontend vui lòng xóa token khỏi bộ nhớ trình duyệt."
    }