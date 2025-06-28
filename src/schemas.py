# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    is_public: bool = True
    category_id: int
    sub_category_id: int


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True


class PostGetResponse(PostResponse):
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
