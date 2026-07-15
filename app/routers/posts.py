from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

# 라우터 설정 (prefix를 /posts로 지정)
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

# 1. 게시글 전체 목록 조회
@router.get("", response_model=List[schemas.Post])
def read_posts(db: Session = Depends(get_db)):
    posts = crud.get_posts(db)
    return posts

# 2. 게시글 상세 조회
@router.get("/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return db_post

# 3. 게시글 작성
@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)

# 4. 게시글 삭제 (비밀번호 검증)
@router.delete("/{post_id}")
def delete_post(post_id: int, password: schemas.PostDelete, db: Session = Depends(get_db)):
    db_post = crud.delete_post(db, post_id=post_id, password=password.password)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="게시글을 찾을 수 없거나 비밀번호가 일치하지 않습니다."
        )
    return {"message": "성공적으로 삭제되었습니다."}