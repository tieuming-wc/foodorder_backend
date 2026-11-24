from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone: str | None
    email: EmailStr
    role: str


class UserUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut