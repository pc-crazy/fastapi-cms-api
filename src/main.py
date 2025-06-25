from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.database import Base, engine, get_db
from src.models import User, Post, Like
from src.schemas import UserCreate, UserResponse, PostCreate, PostResponse
from src.auth import get_current_user, create_access_token, verify_password, get_password_hash
from src.api.v1 import like
from src.api.v1 import accounts
from src.api.v1 import blog


app = FastAPI(title="CMS demo api",
              description="Rest api for user authentication and registration, make a blog, like & dislike blog",
              version="0.1.0",
              openapi_url="/openapi.json",
              docs_url="/docs",  # swagger UI
              redoc_url="/redoc")
app.include_router(like.router)
app.include_router(accounts.router)
app.include_router(blog.router)

Base.metadata.create_all(bind=engine)




