from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/api/posts/{post_id}/comments",
    tags=["Comments"]
)

@router.post("", response_model=schemas.CommentResponse)
def create_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return crud.create_comment(db=db, post_id=post_id, comment=comment)

@router.get("", response_model=list[schemas.CommentResponse])
def read_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments_by_post(db=db, post_id=post_id)

@router.delete("/{comment_id}")
def delete_comment(post_id: int, comment_id: int, request: schemas.CommentDelete, db: Session = Depends(get_db)):
    # post_id는 URL 구조의 일관성을 위해 포함
    return crud.delete_comment(db=db, comment_id=comment_id, password=request.password)