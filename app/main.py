from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app import models

from app.routers import contents, posts, comments, chatbot, images

from app.services.json_loader import load_json_to_db


# FastAPI 앱 생성
app = FastAPI(
    title="LocalHub API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://kkikkilocalhub.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# JSON 데이터 적재git remote remove origin
load_json_to_db()

# Router 등록
app.include_router(contents.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(chatbot.router)
app.include_router(images.router)


@app.get("/")
def root():
    return {"message": "LocalHub API Server"}