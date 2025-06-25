from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.auth import get_current_user
from src.database import get_db
from src.models import User, Post
from src.schemas import PostCreate, PostResponse

router = APIRouter(prefix="/v1")


# Blog Endpoints
@router.post("/blog", response_model=PostResponse)
async def create_blog(
        post: PostCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_post = Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("/blog", response_model=list[PostResponse])
async def get_all_blogs(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    stmt = select(Post).where(or_(Post.is_public, Post.owner_id == current_user.id))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/blog/{post_id}", response_model=PostResponse)
async def get_blog(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_public and post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return post


@router.put("/blog/{post_id}", response_model=PostResponse)
async def update_blog(
        post_id: int,
        post_data: PostCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for attr, value in post_data.dict().items():
        setattr(post, attr, value)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/blog/{post_id}")
async def delete_blog(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted"}