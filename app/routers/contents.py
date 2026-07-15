from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import crud, schemas
from app.models import TourContent as ContentModel

router = APIRouter(
    prefix="/contents",
    tags=["Tour Contents"]
)

@router.get("", response_model=list[schemas.TourContentResponse])
def get_contents(db: Session = Depends(get_db)):
    return crud.get_all_contents(db)

@router.get("/search", response_model=list[schemas.TourContentResponse])
def search_contents(keyword: str, db: Session = Depends(get_db)):
    return crud.search_contents(db, keyword)

@router.get("/type/{content_type_id}", response_model=list[schemas.TourContentResponse])
def get_contents_by_type(content_type_id: int, db: Session = Depends(get_db)):
    return crud.get_contents_by_type(db, content_type_id)

@router.get("/area/{area_code}", response_model=list[schemas.TourContentResponse])
def get_contents_by_area(area_code: str, db: Session = Depends(get_db)):
    results = db.query(ContentModel).filter(
        ContentModel.zipcode.isnot(None),
        func.substr(ContentModel.zipcode, 1, 3) == area_code
    ).all()
    return results

@router.get("/{content_id}", response_model=schemas.TourContentResponse)
def get_content(content_id: str, db: Session = Depends(get_db)):
    content = crud.get_content_by_id(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="관광 정보를 찾을 수 없습니다.")
    return content