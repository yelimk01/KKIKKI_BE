from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import TourContentResponse

router = APIRouter(
    prefix="/contents",
    tags=["Tour Contents"]
)


# 전체 관광 데이터 조회
@router.get("/", response_model=list[TourContentResponse])
def get_contents(db: Session = Depends(get_db)):
    return crud.get_all_contents(db)




# 키워드 검색
@router.get("/search/", response_model=list[TourContentResponse])
def search_contents(
    keyword: str,
    db: Session = Depends(get_db)
):
    return crud.search_contents(db, keyword)

# 콘텐츠 타입별 조회
@router.get("/type/{content_type_id}", response_model=list[TourContentResponse])
def get_contents_by_type(
    content_type_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_contents_by_type(db, content_type_id)


# 지역 코드 조회
@router.get("/area/{area_code}", response_model=list[TourContentResponse])
def get_contents_by_area(
    area_code: str,
    db: Session = Depends(get_db)
):
    return crud.get_contents_by_area(db, area_code)

# 관광 데이터 상세 조회
@router.get("/{content_id}", response_model=TourContentResponse)
def get_content(content_id: str, db: Session = Depends(get_db)):
    content = crud.get_content_by_id(db, content_id)

    if content is None:
        raise HTTPException(
            status_code=404,
            detail="관광 정보를 찾을 수 없습니다."
        )

    return content