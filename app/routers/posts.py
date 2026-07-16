from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
    UploadFile,
    File,
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
# 이미지 최대 10장
# ==========================================

@router.post(
    "",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    password: str = Form(...),
    tour_content_id: str | None = Form(None),

    # 이미지 업로드
    files: list[UploadFile] | None = File(None),

    db: Session = Depends(get_db),
):

    # 이미지 개수 제한
    if files and len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="이미지는 최대 10장까지 가능합니다."
        )


    post_data = schemas.PostCreate(
        title=title,
        content=content,
        author=author,
        password=password,
        tour_content_id=tour_content_id,
    )


    return crud.create_post(
        db=db,
        post=post_data,
        files=files,
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

# ==========================================
# 게시글 비밀번호 검증 (수정 전 확인용)
# ==========================================

@router.post(
    "/{post_id}/verify-password"
)
def verify_post_password(
    post_id: int,
    password_data: schemas.PasswordVerify,
    db: Session = Depends(get_db),
):
    
    is_valid = crud.verify_post_password(
        db=db, 
        post_id=post_id, 
        password=password_data.password
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=401, 
            detail="비밀번호가 일치하지 않습니다."
        )
        
    return {
        "message": "비밀번호가 확인되었습니다."
    }