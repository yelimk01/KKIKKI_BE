from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas


router = APIRouter(
    prefix="/contents",
    tags=["Tour Contents"],
)


# ==========================================
# 관광 콘텐츠 목록
# 페이지네이션 + 검색 + 자치구 + 타입 + 정렬
# ==========================================

@router.get(
    "",
    response_model=schemas.TourContentPageResponse,
)
def get_contents(
    page: int = Query(
        1,
        ge=1,
    ),
    size: int = Query(
        12,
        ge=1,
        le=100,
    ),
    keyword: str | None = None,
    content_type_id: int | None = None,
    district_name: str | None = None,
    sort: str = "latest",
    db: Session = Depends(get_db),
):

    return crud.get_contents_page(
        db=db,
        page=page,
        size=size,
        keyword=keyword,
        content_type_id=content_type_id,
        district_name=district_name,
        sort=sort,
    )


# ==========================================
# 관광 콘텐츠 상세
# 조회수 증가
# ==========================================

@router.get(
    "/{content_id}",
    response_model=schemas.TourContentResponse,
)
def get_content(
    content_id: str,
    db: Session = Depends(get_db),
):

    content = crud.increase_content_view_count(
        db=db,
        content_id=content_id,
    )

    if content is None:
        raise HTTPException(
            status_code=404,
            detail="관광 정보를 찾을 수 없습니다.",
        )

    return content