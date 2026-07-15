from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


# ==========================================
# 게시글 목록 조회
# 페이지네이션
# ==========================================

@router.get(
    "",
    response_model=schemas.PostPageResponse
)
def read_posts(
    page: int = 1,
    size: int = 12,
    keyword: str | None = None,
    search_type: str = "all",
    tour_content_id: str | None = None,
    sort: str = "latest",
    db: Session = Depends(get_db),
):

    return crud.get_posts_page(
        db=db,
        page=page,
        size=size,
        keyword=keyword,
        search_type=search_type,
        tour_content_id=tour_content_id,
        sort=sort,
    )


# ==========================================
# 게시글 상세 조회
# 조회수 증가
# ==========================================

@router.get(
    "/{post_id}",
    response_model=schemas.PostResponse
)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):

    # 먼저 존재 확인 + 상세 데이터 조회
    db_post = crud.get_post(
        db=db,
        post_id=post_id,
    )

    if db_post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )

    # 게시글 조회수 증가
    return crud.increase_view_count(
        db=db,
        post_id=post_id,
    )


# ==========================================
# 게시글 작성
# ==========================================

@router.post(
    "",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
):

    return crud.create_post(
        db=db,
        post=post,
    )


# ==========================================
# 게시글 수정
# ==========================================

@router.put(
    "/{post_id}",
    response_model=schemas.PostResponse,
)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
):

    return crud.update_post(
        db=db,
        post_id=post_id,
        post=post,
    )


# ==========================================
# 게시글 삭제
# ==========================================

@router.delete(
    "/{post_id}"
)
def delete_post(
    post_id: int,
    password: schemas.PostDelete,
    db: Session = Depends(get_db),
):

    crud.delete_post(
        db=db,
        post_id=post_id,
        password=password.password,
    )

    return {
        "message": "성공적으로 삭제되었습니다."
    }


# ==========================================
# 게시글 좋아요
# ==========================================

@router.post(
    "/{post_id}/like",
    response_model=schemas.PostLikeResponse,
)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
):

    post = crud.increase_like_count(
        db=db,
        post_id=post_id,
    )

    return {
        "post_id": post.id,
        "like_count": post.like_count,
    }