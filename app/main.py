from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, engine
from app.routers import chatbot, comments, contents, posts
from app.services.json_loader import load_json_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 서버가 시작될 때 실행되는 초기화 로직.

    1. SQLAlchemy 모델을 기준으로 테이블 생성
    2. TourAPI JSON 데이터를 SQLite에 적재 또는 갱신
    """

    print("LocalHub API 서버 초기화를 시작합니다.")

    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블 확인 완료")

    load_json_to_db()
    print("TourAPI JSON 데이터 확인 완료")

    yield

    print("LocalHub API 서버를 종료합니다.")


app = FastAPI(
    title="LocalHub API",
<<<<<<< HEAD
    version="1.0.0"
    "https://kkikkilocalhub.netlify.app"
=======
    description=(
        "TourAPI 공공데이터 기반 서울 관광정보 및 "
        "익명 커뮤니티 서비스 API"
    ),
    version="1.0.0",
    lifespan=lifespan,
>>>>>>> 41f1055d3595bbfc762c68a336cece01dd3f39b1
)


# ==========================================
# CORS 설정
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000"   # <-- Nuxt 프론트엔드 포트(3000)를 필수로 추가해 주세요!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Router 등록
# ==========================================

app.include_router(contents.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(chatbot.router)


# ==========================================
# 기본 API
# ==========================================

@app.get(
    "/",
    tags=["system"],
)
def root():
    return {
        "message": "LocalHub API Server",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    tags=["system"],
)
def health_check():
    return {
        "status": "ok",
        "service": "LocalHub API",
        "version": "1.0.0",
    }