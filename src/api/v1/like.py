from sqlalchemy.orm import Session
from src.database import get_db
from src.models import User, Post, Like
from src.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(prefix="/v1")

# Like Endpoints
@router.post("/like/{post_id}")
async def like_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate post_id exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Only allow liking public or own post
    if not post.is_public and post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot like a private post you don't own")

    like_exist = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.id).first()
    if like_exist:
        raise HTTPException(status_code=400, detail="You have already liked this post.")
    like = Like(post_id=post_id, user_id=current_user.id)

    db.add(like)
    db.commit()
    return {"message": "Post liked"}

@router.delete("/like/{post_id}")
async def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate post_id exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.id).first()
    if like:
        db.delete(like)
        db.commit()
        return {"message": "Post unliked"}
    raise HTTPException(status_code=400, detail="You have not liked this post")
