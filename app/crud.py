import math

from fastapi import HTTPException, UploadFile
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.models import (
    Comment,
    Post,
    TourContent,
    PostImage,
)

from app.services.file_upload import save_file


# ==========================================
# TourContent CRUD
# ==========================================

def get_all_contents(db: Session):
    """
    전체 관광정보 조회

    간단한 내부 확인용 함수다.
    실제 목록 화면에서는 get_contents_page() 사용을 권장한다.
    """
    return (
        db.query(TourContent)
        .order_by(TourContent.title.asc())
        .all()
    )


def get_content_by_id(
    db: Session,
    content_id: str,
):
    """
    contentid로 관광정보 한 건 조회
    """
    return (
        db.query(TourContent)
        .filter(TourContent.contentid == content_id)
        .first()
    )


def get_content_or_404(
    db: Session,
    content_id: str,
):
    """
    관광정보를 조회하고 존재하지 않으면 404를 발생시킨다.
    """
    content = get_content_by_id(
        db=db,
        content_id=content_id,
    )

    if content is None:
        raise HTTPException(
            status_code=404,
            detail="관광정보를 찾을 수 없습니다.",
        )

    return content


def get_contents_page(
    db: Session,
    page: int = 1,
    size: int = 12,
    content_type_id: int | None = None,
    district: str | None = None,
    keyword: str | None = None,
    sort: str = "name",
):
    """
    관광정보 목록 조회

    지원 기능:
    - 콘텐츠 유형 필터
    - 자치구 필터
    - 장소명 및 주소 검색
    - 이름순, 인기순, 최신순 정렬
    - 페이지네이션
    """

    query = db.query(TourContent)

    if content_type_id is not None:
        query = query.filter(
            TourContent.contenttypeid == content_type_id
        )

    if district:
        query = query.filter(
            TourContent.district_name == district
        )

    if keyword:
        cleaned_keyword = keyword.strip()

        if cleaned_keyword:
            query = query.filter(
                or_(
                    TourContent.title.contains(
                        cleaned_keyword
                    ),
                    TourContent.addr1.contains(
                        cleaned_keyword
                    ),
                )
            )

    if sort == "popular":
        query = query.order_by(
            desc(TourContent.view_count),
            asc(TourContent.title),
        )

    elif sort == "latest":
        query = query.order_by(
            desc(TourContent.modifiedtime),
            asc(TourContent.title),
        )

    else:
        # 기본값: 이름순
        query = query.order_by(
            asc(TourContent.title)
        )

    total_items = query.count()

    total_pages = (
        math.ceil(total_items / size)
        if total_items > 0
        else 0
    )

    items = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "size": size,
        "total_items": total_items,
        "total_pages": total_pages,
    }


def get_contents_by_type(
    db: Session,
    content_type_id: int,
):
    """
    콘텐츠 유형별 관광정보 조회
    """
    return (
        db.query(TourContent)
        .filter(
            TourContent.contenttypeid == content_type_id
        )
        .order_by(TourContent.title.asc())
        .all()
    )


def search_contents(
    db: Session,
    keyword: str,
    limit: int = 10,
):
    """
    게시글 작성 화면의 장소 선택 검색에 사용한다.

    장소명 또는 주소를 검색하고 최대 limit개를 반환한다.
    """

    cleaned_keyword = keyword.strip()

    if not cleaned_keyword:
        return []

    return (
        db.query(TourContent)
        .filter(
            or_(
                TourContent.title.contains(
                    cleaned_keyword
                ),
                TourContent.addr1.contains(
                    cleaned_keyword
                ),
            )
        )
        .order_by(
            TourContent.title.asc()
        )
        .limit(limit)
        .all()
    )


def get_contents_by_area(
    db: Session,
    area_code: str,
):
    """
    지역코드 기준 관광정보 조회
    """
    return (
        db.query(TourContent)
        .filter(
            TourContent.areacode == area_code
        )
        .order_by(TourContent.title.asc())
        .all()
    )


def get_contents_by_district(
    db: Session,
    district: str,
):
    """
    자치구 기준 관광정보 조회
    """
    return (
        db.query(TourContent)
        .filter(
            TourContent.district_name == district
        )
        .order_by(TourContent.title.asc())
        .all()
    )


def get_districts(db: Session):
    """
    DB에 저장된 자치구 목록을 중복 없이 조회한다.
    """
    rows = (
        db.query(TourContent.district_name)
        .filter(
            TourContent.district_name.isnot(None)
        )
        .distinct()
        .order_by(TourContent.district_name.asc())
        .all()
    )

    return [
        row[0]
        for row in rows
        if row[0]
    ]


def increase_content_view_count(
    db: Session,
    content_id: str,
):
    """
    관광정보 상세 조회수를 1 증가시킨다.
    """
    content = get_content_or_404(
        db=db,
        content_id=content_id,
    )

    content.view_count += 1

    db.commit()
    db.refresh(content)

    return content


def get_most_viewed_contents(
    db: Session,
    district: str | None = None,
    limit: int = 3,
):
    """
    많이 클릭한 장소 조회
    """
    query = db.query(TourContent)

    if district:
        query = query.filter(
            TourContent.district_name == district
        )

    return (
        query
        .order_by(
            TourContent.view_count.desc(),
            TourContent.title.asc(),
        )
        .limit(limit)
        .all()
    )


def get_most_mentioned_contents(
    db: Session,
    district: str | None = None,
    limit: int = 3,
):
    """
    게시글에서 많이 언급된 장소 조회
    """
    query = db.query(TourContent)

    if district:
        query = query.filter(
            TourContent.district_name == district
        )

    return (
        query
        .order_by(
            TourContent.mention_count.desc(),
            TourContent.title.asc(),
        )
        .limit(limit)
        .all()
    )


# ==========================================
# Post CRUD
# ==========================================

def get_post(
    db: Session,
    post_id: int,
):
    """
    게시글 한 건 조회

    연결된 관광정보와 이미지를 함께 조회한다.
    """

    return (
        db.query(Post)
        .options(
            joinedload(Post.tour_content),
            joinedload(Post.images),
        )
        .filter(
            Post.id == post_id
        )
        .first()
    )


def get_post_or_404(
    db: Session,
    post_id: int,
):
    """
    게시글을 조회하고 존재하지 않으면 404를 발생시킨다.
    """
    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다.",
        )

    return post


def create_post(
    db: Session,
    post: schemas.PostCreate,
    files: list[UploadFile] | None
):
    """
    게시글 생성

    처리:
    1. 게시글 저장
    2. 선택 장소 mention_count 증가
    3. 이미지 파일 저장
    4. post_images 저장
    """

    selected_content = None

    # 장소 선택 확인
    if post.tour_content_id is not None:

        selected_content = get_content_by_id(
            db=db,
            content_id=post.tour_content_id,
        )

        if selected_content is None:
            raise HTTPException(
                status_code=404,
                detail="선택한 장소를 찾을 수 없습니다.",
            )


    db_post = Post(
        title=post.title.strip(),
        content=post.content.strip(),
        author=post.author.strip(),
        password=post.password,
        tour_content_id=post.tour_content_id,
    )


    try:
        # 게시글 저장
        db.add(db_post)

        db.flush()
        # flush를 해야 db_post.id 생성됨


        # 장소 언급 수 증가
        if selected_content is not None:
            selected_content.mention_count += 1


        # ==========================
        # 이미지 저장
        # ==========================

        if files:
            for file in files:
                image_url = save_file(file)

                post_image = PostImage(
                    post_id=db_post.id,
                    image_url=image_url,
                )

                db.add(post_image)


        db.commit()

        db.refresh(db_post)


        return get_post(
            db=db,
            post_id=db_post.id,
        )


    except Exception:
        db.rollback()
        raise


def get_posts_page(
    db: Session,
    page: int = 1,
    size: int = 12,
    keyword: str | None = None,
    search_type: str = "all",
    tour_content_id: str | None = None,
    sort: str = "latest",
):
    """
    게시글 목록 조회

    지원 기능:
    - 제목, 내용, 작성자 검색
    - 특정 장소와 연결된 게시글 조회
    - 최신순, 조회수순, 좋아요순
    - 페이지네이션
    """

    query = (
        db.query(Post)
        .options(
            joinedload(Post.tour_content)
        )
    )

    if tour_content_id:
        query = query.filter(
            Post.tour_content_id == tour_content_id
        )

    if keyword:
        cleaned_keyword = keyword.strip()

        if cleaned_keyword:
            if search_type == "title":
                query = query.filter(
                    Post.title.contains(
                        cleaned_keyword
                    )
                )

            elif search_type == "content":
                query = query.filter(
                    Post.content.contains(
                        cleaned_keyword
                    )
                )

            elif search_type == "author":
                query = query.filter(
                    Post.author.contains(
                        cleaned_keyword
                    )
                )

            else:
                query = query.filter(
                    or_(
                        Post.title.contains(
                            cleaned_keyword
                        ),
                        Post.content.contains(
                            cleaned_keyword
                        ),
                        Post.author.contains(
                            cleaned_keyword
                        ),
                        Post.tour_content.has(
                            TourContent.title.contains(
                                cleaned_keyword
                            )
                        ),
                    )
                )

    if sort == "views":
        query = query.order_by(
            Post.view_count.desc(),
            Post.created_at.desc(),
        )

    elif sort == "likes":
        query = query.order_by(
            Post.like_count.desc(),
            Post.created_at.desc(),
        )

    else:
        query = query.order_by(
            Post.created_at.desc()
        )

    total_items = query.count()

    total_pages = (
        math.ceil(total_items / size)
        if total_items > 0
        else 0
    )

    items = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "size": size,
        "total_items": total_items,
        "total_pages": total_pages,
    }


def increase_view_count(
    db: Session,
    post_id: int,
):
    """
    게시글 상세 조회수를 1 증가시킨다.
    """
    db_post = get_post_or_404(
        db=db,
        post_id=post_id,
    )

    db_post.view_count += 1

    db.commit()
    db.refresh(db_post)

    return db_post


def increase_like_count(
    db: Session,
    post_id: int,
):
    """
    게시글 좋아요 수를 1 증가시킨다.
    """
    db_post = get_post_or_404(
        db=db,
        post_id=post_id,
    )

    db_post.like_count += 1

    db.commit()
    db.refresh(db_post)

    return db_post


def verify_post_password(
    db: Session,
    post_id: int,
    password: str,
):
    """
    수정·삭제 모달에서 게시글 비밀번호를 확인한다.
    """
    db_post = get_post_or_404(
        db=db,
        post_id=post_id,
    )

    return db_post.password == password


def update_post(
    db: Session,
    post_id: int,
    post: schemas.PostUpdate,
):
    """
    게시글 수정

    장소가 변경되는 경우:
    - 기존 장소 mention_count 1 감소
    - 새로운 장소 mention_count 1 증가
    """

    db_post = get_post_or_404(
        db=db,
        post_id=post_id,
    )

    if db_post.password != post.password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다.",
        )

    old_content_id = db_post.tour_content_id
    new_content_id = post.tour_content_id

    new_content = None

    if new_content_id is not None:
        new_content = get_content_by_id(
            db=db,
            content_id=new_content_id,
        )

        if new_content is None:
            raise HTTPException(
                status_code=404,
                detail="변경할 장소를 찾을 수 없습니다.",
            )

    try:
        # 장소가 실제로 변경된 경우에만 언급 수를 변경한다.
        if old_content_id != new_content_id:
            if old_content_id is not None:
                old_content = get_content_by_id(
                    db=db,
                    content_id=old_content_id,
                )

                if old_content is not None:
                    old_content.mention_count = max(
                        0,
                        old_content.mention_count - 1,
                    )

            if new_content is not None:
                new_content.mention_count += 1

        db_post.title = post.title.strip()
        db_post.content = post.content.strip()
        db_post.tour_content_id = new_content_id

        db.commit()
        db.refresh(db_post)

        return get_post(
            db=db,
            post_id=db_post.id,
        )

    except Exception:
        db.rollback()
        raise


def delete_post(
    db: Session,
    post_id: int,
    password: str,
):
    """
    게시글 삭제

    장소가 연결되어 있다면 해당 장소 mention_count를 1 감소시킨다.
    """

    db_post = get_post_or_404(
        db=db,
        post_id=post_id,
    )

    if db_post.password != password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다.",
        )

    try:
        if db_post.tour_content_id is not None:
            content = get_content_by_id(
                db=db,
                content_id=db_post.tour_content_id,
            )

            if content is not None:
                content.mention_count = max(
                    0,
                    content.mention_count - 1,
                )

        db.delete(db_post)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

# ==========================================
# Comment CRUD
# ==========================================

def create_comment(
    db: Session,
    post_id: int,
    comment: schemas.CommentCreate,
):
    """
    댓글 생성
    """

    # 존재하지 않는 게시글에는 댓글을 작성할 수 없다.
    get_post_or_404(
        db=db,
        post_id=post_id,
    )

    db_comment = Comment(
        post_id=post_id,
        author=comment.author.strip(),
        content=comment.content.strip(),
        password=comment.password,
    )

    try:
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    except Exception:
        db.rollback()
        raise


def get_comments_by_post(
    db: Session,
    post_id: int,
):
    """
    게시글의 댓글 목록 조회
    """

    get_post_or_404(
        db=db,
        post_id=post_id,
    )

    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


def delete_comment(
    db: Session,
    comment_id: int,
    password: str,
):
    """
    댓글 삭제
    """

    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if db_comment is None:
        raise HTTPException(
            status_code=404,
            detail="댓글을 찾을 수 없습니다.",
        )

    if db_comment.password != password:
        raise HTTPException(
            status_code=403,
            detail="비밀번호가 일치하지 않습니다.",
        )

    try:
        db.delete(db_comment)
        db.commit()

        return {
            "message": "댓글이 삭제되었습니다.",
        }

    except Exception:
        db.rollback()
        raise