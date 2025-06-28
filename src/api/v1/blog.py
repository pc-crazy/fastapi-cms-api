from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models import User, Post, Category, SubCategory
from src.schemas import PostCreate, PostResponse, PostGetResponse

router = APIRouter(prefix="/v1")


# Blog Endpoints
@router.post("/blog", response_model=PostResponse)
async def create_blog(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat_exist = (
        db.query(Category).filter(Category.id == post.category_id).first()
    )
    if not cat_exist:
        raise HTTPException(
            status_code=400, detail="Category doesn't match with id"
        )
    sub_cat_exist = (
        db.query(SubCategory)
        .filter(SubCategory.id == post.sub_category_id)
        .first()
    )
    if not sub_cat_exist:
        raise HTTPException(
            status_code=400, detail="Sub Category doesn't match with id"
        )
    new_post = Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/blog", response_model=list[PostGetResponse])
async def get_all_blogs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = (
        db.query(
            Post,
            Category.name.label("category_name"),
            SubCategory.name.label("sub_category_name"),
        )
        .outerjoin(Category, Category.id == Post.category_id)
        .outerjoin(SubCategory, SubCategory.id == Post.sub_category_id)
        .filter(Post.is_public | (Post.owner_id == current_user.id))
        .all()
    )
    response = []
    for post, category_name, sub_category_name in posts:
        item = post.__dict__.copy()
        del item["_sa_instance_state"]
        item["category_name"] = category_name
        item["sub_category_name"] = sub_category_name
        response.append(item)
    return response


@router.get("/blog/{post_id}", response_model=PostGetResponse)
async def get_blog(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.is_public and post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return post


@router.put("/blog/{post_id}", response_model=PostResponse)
async def update_blog(
    post_id: int,
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for attr, value in post_data.dict().items():
        setattr(post, attr, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/blog/{post_id}")
async def delete_blog(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
