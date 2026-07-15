from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ==========================================
# 관광 데이터
# ==========================================
class TourContent(Base):
    __tablename__ = "tour_contents"

    # TourAPI 콘텐츠 고유 ID
    contentid = Column(
        String,
        primary_key=True,
        index=True,
    )

    # 12: 관광지, 14: 문화시설, 15: 축제 등
    contenttypeid = Column(
        Integer,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
        index=True,
    )

    addr1 = Column(String, nullable=True)
    addr2 = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)

    # 화면에서 구 필터를 편하게 사용하기 위한 컬럼
    # 예: 종로구, 강남구, 송파구
    district_name = Column(
        String,
        nullable=True,
        index=True,
    )

    tel = Column(String, nullable=True)

    # mapx: 경도, mapy: 위도
    mapx = Column(Float, nullable=True)
    mapy = Column(Float, nullable=True)

    mlevel = Column(Integer, nullable=True)

    areacode = Column(String, nullable=True)
    sigungucode = Column(
        String,
        nullable=True,
        index=True,
    )

    lDongRegnCd = Column(String, nullable=True)
    lDongSignguCd = Column(String, nullable=True)

    cat1 = Column(String, nullable=True)
    cat2 = Column(String, nullable=True)
    cat3 = Column(String, nullable=True)

    lclsSystm1 = Column(String, nullable=True)
    lclsSystm2 = Column(String, nullable=True)
    lclsSystm3 = Column(String, nullable=True)

    firstimage = Column(Text, nullable=True)
    firstimage2 = Column(Text, nullable=True)

    cpyrhtDivCd = Column(String, nullable=True)

    # TourAPI 원본 형식을 유지하기 위해 우선 문자열로 저장
    createdtime = Column(String, nullable=True)
    modifiedtime = Column(
        String,
        nullable=True,
        index=True,
    )

    # 상세정보를 열어본 횟수
    view_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # 이 장소가 게시글에서 선택된 횟수
    mention_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # 이 장소를 선택한 게시글들
    posts = relationship(
        "Post",
        back_populates="tour_content",
        passive_deletes=True,
    )


# ==========================================
# 게시판
# ==========================================
class Post(Base):
    __tablename__ = "posts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(200),
        nullable=False,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    author = Column(
        String(50),
        nullable=False,
    )

    password = Column(
        String(100),
        nullable=False,
    )

    # 게시글에서 선택한 장소 한 개
    # 장소를 선택하지 않아도 글을 쓸 수 있도록 nullable=True
    tour_content_id = Column(
        String,
        ForeignKey(
            "tour_contents.contentid",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    view_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    like_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 게시글이 선택한 관광정보
    tour_content = relationship(
        "TourContent",
        back_populates="posts",
    )

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    
    images = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    
# ==========================================
# 게시글 이미지
# ==========================================
class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    post_id = Column(
        Integer,
        ForeignKey(
            "posts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    image_url = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    post = relationship(
        "Post",
        back_populates="images",
    )


# ==========================================
# 댓글
# ==========================================
class Comment(Base):
    __tablename__ = "comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    post_id = Column(
        Integer,
        ForeignKey(
            "posts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    author = Column(
        String(50),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    password = Column(
        String(100),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    post = relationship(
        "Post",
        back_populates="comments",
    )