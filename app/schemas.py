from datetime import datetime
from pydantic import BaseModel


# ==========================
# TourContent
# ==========================

class TourContentBase(BaseModel):
    contentid: str
    contenttypeid: int
    title: str

    addr1: str | None = None
    addr2: str | None = None
    zipcode: str | None = None

    tel: str | None = None

    mapx: float | None = None
    mapy: float | None = None

    firstimage: str | None = None
    firstimage2: str | None = None


class TourContentResponse(TourContentBase):
    class Config:
        from_attributes = True


# ==========================
# Post
# ==========================

class PostCreate(BaseModel):
    title: str
    content: str
    author: str
    password: str


class PostUpdate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int

    title: str
    content: str

    author: str

    view_count: int
    like_count: int

    created_at: datetime | None

    class Config:
        from_attributes = True


# ==========================
# Comment
# ==========================

class CommentCreate(BaseModel):
    author: str
    content: str


class CommentResponse(BaseModel):
    id: int

    author: str
    content: str

    created_at: datetime | None

    class Config:
        from_attributes = True


# ==========================
# ChatBot
# ==========================

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str