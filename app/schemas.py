from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# TourContent
# ==========================================

class TourContentBase(BaseModel):
    contentid: str
    contenttypeid: int
    title: str

    addr1: str | None = None
    addr2: str | None = None
    zipcode: str | None = None

    tel: str | None = None

    # mapx: 경도, mapy: 위도
    mapx: float | None = None
    mapy: float | None = None

    firstimage: str | None = None
    firstimage2: str | None = None

    # 자치구 필터용
    district_name: str | None = None

    # TourAPI 등록/수정 시간
    createdtime: str | None = None
    modifiedtime: str | None = None

    # 서비스 통계
    view_count: int = 0
    mention_count: int = 0


class TourContentResponse(TourContentBase):
    model_config = ConfigDict(from_attributes=True)


class TourContentSimpleResponse(BaseModel):
    """
    게시글 상세에 포함할 간단한 관광정보
    """

    model_config = ConfigDict(from_attributes=True)

    contentid: str
    contenttypeid: int
    title: str

    addr1: str | None = None
    district_name: str | None = None

    firstimage: str | None = None
    firstimage2: str | None = None

    view_count: int = 0
    mention_count: int = 0


# ==========================================
# Post
# ==========================================

class Post(BaseModel):
    """
    기존 호환용 기본 Post Schema
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    content: str
    author: str

    view_count: int
    like_count: int

    created_at: datetime
    updated_at: datetime

    tour_content_id: str | None = None


class PostCreate(BaseModel):
    """
    게시글 작성 요청
    """

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: str = Field(
        min_length=1,
    )

    author: str = Field(
        min_length=1,
        max_length=50,
    )

    password: str = Field(
        min_length=1,
        max_length=100,
    )

    # 선택한 장소
    tour_content_id: str | None = None


# ==========================================
# Post Image
# ==========================================

class PostImageResponse(BaseModel):
    """
    게시글 이미지 응답
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str


# ==========================================
# Post Response
# ==========================================

class PostResponse(BaseModel):
    """
    게시글 상세 응답
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    content: str
    author: str

    view_count: int
    like_count: int

    created_at: datetime
    updated_at: datetime

    # 선택한 관광정보
    tour_content_id: str | None = None

    tour_content: TourContentSimpleResponse | None = None

    # 첨부 이미지
    images: list[PostImageResponse] = []


class PostListResponse(BaseModel):
    """
    게시글 목록 화면 응답

    표시:
    - 번호
    - 제목
    - 작성자
    - 작성일
    - 조회수
    - 좋아요
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    author: str

    created_at: datetime

    view_count: int
    like_count: int


class PostUpdate(BaseModel):
    """
    게시글 수정 요청
    """

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: str = Field(
        min_length=1,
    )

    # 수정 권한 확인용
    password: str = Field(
        min_length=1,
        max_length=100,
    )

    # 장소 변경 가능
    tour_content_id: str | None = None


class PostDelete(BaseModel):
    """
    게시글 삭제 요청
    """

    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PasswordVerifyRequest(BaseModel):
    """
    수정/삭제 전 비밀번호 확인
    """

    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PasswordVerifyResponse(BaseModel):
    verified: bool


class PostLikeResponse(BaseModel):
    post_id: int
    like_count: int


# ==========================================
# Pagination
# ==========================================

class PostPageResponse(BaseModel):
    """
    게시글 목록 페이지 응답
    """

    items: list[PostListResponse]

    page: int
    size: int

    total_items: int
    total_pages: int


class TourContentPageResponse(BaseModel):
    items: list[TourContentResponse]

    page: int
    size: int

    total_items: int
    total_pages: int


# ==========================================
# Comment
# ==========================================

class CommentCreate(BaseModel):

    author: str = Field(
        min_length=1,
        max_length=50,
    )

    content: str = Field(
        min_length=1,
    )

    password: str = Field(
        min_length=1,
        max_length=100,
    )


class CommentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int

    author: str
    content: str

    created_at: datetime


class CommentDelete(BaseModel):

    password: str = Field(
        min_length=1,
        max_length=100,
    )


# ==========================================
# ChatBot
# ==========================================

class ChatHistoryItem(BaseModel):

    role: str = Field(
        pattern="^(user|assistant)$",
    )

    content: str = Field(
        min_length=1,
        max_length=2000,
    )


class ChatRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=1000,
    )

    history: list[ChatHistoryItem] = Field(
        default_factory=list,
    )


class ChatPlaceResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    contentid: str
    title: str

    addr1: str | None = None
    district_name: str | None = None

    mapx: float | None = None
    mapy: float | None = None

    firstimage: str | None = None

    view_count: int = 0
    mention_count: int = 0


class ChatPostResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str

    author: str
    view_count: int
    like_count: int


class ChatResponse(BaseModel):

    answer: str

    places: list[ChatPlaceResponse] = Field(
        default_factory=list,
    )

    posts: list[ChatPostResponse] = Field(
        default_factory=list,
    )

class PasswordVerify(BaseModel): 
    password: str