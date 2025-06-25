from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.auth import (
    get_current_user, create_access_token, verify_password, get_password_hash
)
from src.database import get_db
from src.models import User
from src.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/v1")


# Account Endpoints
@router.post("/accounts", response_model=UserResponse)
async def create_account(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(**user.dict(exclude={"password"}), password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/accounts/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.put("/accounts", response_model=UserResponse)
async def update_account(updated: UserCreate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    current_user.name = updated.name
    current_user.email = updated.email
    current_user.password = get_password_hash(updated.password)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/accounts")
async def delete_account(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await db.delete(current_user)
    await db.commit()
    return {"message": "Account deleted successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
