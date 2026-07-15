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
@router.get("/area/{area_code}")
def get_contents_by_area(area_code: str, db: Session = Depends(get_db)):
    # zipcode의 앞 3자리가 area_code와 일치하는 데이터 조회
    # func.substr을 사용하여 zipcode의 1번째 자리부터 3글자를 추출 후 비교
    results = db.query(ContentModel).filter(
        func.substr(ContentModel.zipcode, 1, 3) == area_code
    ).all()
    
    # 또는 LIKE 연산자를 사용하고 싶다면:
    # results = db.query(ContentModel).filter(
    #     ContentModel.zipcode.like(f"{area_code}%")
    # ).all()

    if not results:
        return [] # 데이터가 없어도 에러 대신 빈 리스트 반환이 프론트엔드 처리에 좋습니다.
        
    return results

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