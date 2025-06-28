from fastapi import FastAPI

from src.api.v1 import accounts
from src.api.v1 import blog
from src.api.v1 import like
from src.database import Base, engine

app = FastAPI(
    title="CMS demo api",
    description="Rest api for user authentication and registration,"
    " make a blog, like & dislike blog",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",  # swagger UI
    redoc_url="/redoc",
)
app.include_router(like.router)
app.include_router(accounts.router)
app.include_router(blog.router)

Base.metadata.create_all(bind=engine)
