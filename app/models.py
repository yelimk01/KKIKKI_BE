from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


# 관광 데이터
class TourContent(Base):
    __tablename__ = "tour_contents"

    contentid = Column(String, primary_key=True, index=True)
    contenttypeid = Column(Integer, nullable=False)

    title = Column(String, nullable=False)

    addr1 = Column(String)
    addr2 = Column(String)
    zipcode = Column(String)

    tel = Column(String)

    mapx = Column(Float)
    mapy = Column(Float)

    mlevel = Column(Integer)

    areacode = Column(String)
    sigungucode = Column(String)

    lDongRegnCd = Column(String)
    lDongSignguCd = Column(String)

    cat1 = Column(String)
    cat2 = Column(String)
    cat3 = Column(String)

    lclsSystm1 = Column(String)
    lclsSystm2 = Column(String)
    lclsSystm3 = Column(String)

    firstimage = Column(Text)
    firstimage2 = Column(Text)

    cpyrhtDivCd = Column(String)

    createdtime = Column(String)
    modifiedtime = Column(String)


# 게시판
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    author = Column(String, nullable=False)
    password = Column(String, nullable=False)

    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete"
    )


# 댓글
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(
        Integer,
        ForeignKey("posts.id")
    )

    author = Column(String, nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime)

    post = relationship(
        "Post",
        back_populates="comments"
    )