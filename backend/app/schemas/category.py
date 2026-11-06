from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    image: str | None = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    display_order: int | None = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True
