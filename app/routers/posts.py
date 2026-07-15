from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# 게시글 목록 조회
@router.get("", response_model=list[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return crud.get_posts(db)


# 게시글 상세 조회
@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.increase_view_count(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    return post


# 게시글 작성
@router.post("/", response_model=schemas.PostResponse)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):
    return crud.create_post(db, post)


# 게시글 수정
@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db)
):
    updated_post = crud.update_post(db, post_id, post)

    if updated_post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    return updated_post


# 게시글 삭제
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    request: schemas.PostDelete,
    db: Session = Depends(get_db)
):
    success = crud.delete_post(db, post_id, request.password)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    return {
        "message": "게시글이 삭제되었습니다."
    }


# 좋아요
@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = crud.increase_like_count(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    return {
        "like_count": post.like_count
    }