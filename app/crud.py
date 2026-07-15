from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import TourContent

from datetime import datetime
from app.models import Post
from app.models import Comment
from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas



# ==========================
# TourContent CRUD
# ==========================

def get_all_contents(db: Session):
    """전체 관광 데이터 조회"""
    return db.query(TourContent).all()


def get_content_by_id(db: Session, content_id: str):
    """contentid로 관광 데이터 조회"""
    return (
        db.query(TourContent)
        .filter(TourContent.contentid == content_id)
        .first()
    )


def get_contents_by_type(db: Session, content_type_id: int):
    """콘텐츠 타입별 조회"""
    return (
        db.query(TourContent)
        .filter(TourContent.contenttypeid == content_type_id)
        .all()
    )


def search_contents(db: Session, keyword: str):
    """장소명 또는 주소 검색"""
    return (
        db.query(TourContent)
        .filter(
            or_(
                TourContent.title.contains(keyword),
                TourContent.addr1.contains(keyword)
            )
        )
        .all()
    )


def get_contents_by_area(db: Session, area_code: str):
    """지역코드 조회"""
    return (
        db.query(TourContent)
        .filter(TourContent.areacode == area_code)
        .all()
    )


# ==========================
# Post CRUD
# ==========================

def create_post(db, post):
    db_post = Post(
        title=post.title,
        content=post.content,
        author=post.author,
        password=post.password,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


def get_posts(db):
    return (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .all()
    )


def get_post(db, post_id: int):
    return (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

def increase_view_count(db, post_id: int):
    db_post = get_post(db, post_id)

    if db_post:
        db_post.view_count += 1
        db.commit()

    return db_post


def increase_like_count(db, post_id: int):
    db_post = get_post(db, post_id)

    if db_post:
        db_post.like_count += 1
        db.commit()

    return db_post

def update_post(db: Session, post_id: int, post: schemas.PostUpdate):
    db_post = get_post(db, post_id)

    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 비밀번호 평문 비교 검증
    if db_post.password != post.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    db_post.title = post.title
    db_post.content = post.content
    db_post.updated_at = datetime.now()

    db.commit()
    db.refresh(db_post)

    return db_post


def delete_post(db: Session, post_id: int, password: str):
    db_post = get_post(db, post_id)

    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 비밀번호 평문 비교 검증
    if db_post.password != password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    db.delete(db_post)
    db.commit()

    return True

# ==========================
# Comment CRUD
# ==========================

# 댓글 생성
def create_comment(db: Session, post_id: int, comment: schemas.CommentCreate):
    db_comment = models.Comment(
        post_id=post_id,
        author=comment.author,
        content=comment.content,
        password=comment.password # 평문 저장
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# 게시글의 댓글 목록 조회
def get_comments_by_post(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

# 댓글 삭제 (비밀번호 검증)
def delete_comment(db: Session, comment_id: int, password: str):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if not db_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    # 비밀번호 평문 비교 검증
    if db_comment.password != password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    db.delete(db_comment)
    db.commit()
    return {"message": "댓글이 삭제되었습니다."}