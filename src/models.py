# models.py
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Boolean,
    DateTime, func
)
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)

    posts = relationship("Post", back_populates="owner")
    likes = relationship("Like", back_populates="user")


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'))

    owner = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")
    category = relationship("Category", back_populates="post")
    sub_category = relationship("SubCategory", back_populates="post")


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    post = relationship("Post", back_populates="category")
    sub_category = relationship("SubCategory", back_populates="category")


class SubCategory(Base):
    __tablename__ = 'sub_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("Category", back_populates="sub_category")
    post = relationship("Post", back_populates="sub_category")
