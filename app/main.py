from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import User, Post, Like
from app.schemas import UserCreate, UserResponse, PostCreate, PostResponse
from app.auth import get_current_user, create_access_token, verify_password, get_password_hash

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Account Endpoints
@app.post("/accounts", response_model=UserResponse)
async def create_account(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(**user.dict(exclude={"password"}), password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/accounts/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.put("/accounts", response_model=UserResponse)
async def update_account(updated: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.name = updated.name
    current_user.email = updated.email
    current_user.password = get_password_hash(updated.password)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/accounts")
async def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

@app.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Blog Endpoints
@app.post("/blog", response_model=PostResponse)
async def create_blog(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/blog", response_model=list[PostResponse])
async def get_all_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    posts = db.query(Post).filter((Post.is_public == True) | (Post.owner_id == current_user.id)).all()
    return posts

@app.get("/blog/{post_id}", response_model=PostResponse)
async def get_blog(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_public and post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return post

@app.put("/blog/{post_id}", response_model=PostResponse)
async def update_blog(post_id: int, post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for attr, value in post_data.dict().items():
        setattr(post, attr, value)
    db.commit()
    db.refresh(post)
    return post

@app.delete("/blog/{post_id}")
async def delete_blog(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

# Like Endpoints
@app.post("/like/{post_id}")
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

@app.delete("/like/{post_id}")
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
