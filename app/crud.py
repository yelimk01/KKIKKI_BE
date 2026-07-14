from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import TourContent


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