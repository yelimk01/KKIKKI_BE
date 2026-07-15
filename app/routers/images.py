from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PostImage, Post
from app import schemas


router = APIRouter(
    prefix="/posts",
    tags=["images"]
)


@router.post(
    "/{post_id}/images",
    response_model=list[schemas.PostImageResponse]
)
def upload_images(
    post_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):

    # 게시글 존재 확인
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다."
        )


    # ⭐ 여기서 최대 10장 검사
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="이미지는 최대 10장까지 가능합니다."
        )


    images = []


    for file in files:

        # 파일 저장 로직
        image_url = save_file(file)


        image = PostImage(
            post_id=post_id,
            image_url=image_url
        )

        db.add(image)

        images.append(image)


    db.commit()


    for image in images:
        db.refresh(image)


    return images