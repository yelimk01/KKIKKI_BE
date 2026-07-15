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

    # 화면에서 자치구 필터에 사용
    district_name: str | None = None

    # TourAPI 원본 등록·수정 시각
    createdtime: str | None = None
    modifiedtime: str | None = None

    # 서비스 내부 통계용
    view_count: int = 0
    mention_count: int = 0


class TourContentResponse(TourContentBase):
    model_config = ConfigDict(from_attributes=True)


class TourContentSimpleResponse(BaseModel):
    """
    게시글 응답에 포함할 간단한 관광정보
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
    DB 모델과 직접 매핑되는 기본 Post 스키마
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

    # 게시글당 장소 또는 행사 하나만 선택
    # 일반 게시글은 장소를 선택하지 않아도 되므로 None 허용
    tour_content_id: str | None = None


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

    # 선택한 관광정보 ID
    tour_content_id: str | None = None

    # 선택한 관광정보의 간단한 상세 정보
    tour_content: TourContentSimpleResponse | None = None


class PostListResponse(BaseModel):
    """
    게시글 목록 화면용 응답
    본문 전체는 제외한다.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str

    view_count: int
    like_count: int

    created_at: datetime

    tour_content_id: str | None = None
    tour_content: TourContentSimpleResponse | None = None


class PostUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: str = Field(
        min_length=1,
    )

    # 수정 권한 확인용 비밀번호
    password: str = Field(
        min_length=1,
        max_length=100,
    )

    # 수정 시 장소를 변경하거나 제거할 수 있음
    tour_content_id: str | None = None


class PostDelete(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PasswordVerifyRequest(BaseModel):
    """
    게시글 수정·삭제 전 비밀번호 확인 모달 요청
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

    # 대화 내역은 프론트에서 전달
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

    # 챗봇 답변 아래에 장소·게시글 카드를 표시할 때 사용
    places: list[ChatPlaceResponse] = Field(
        default_factory=list,
    )

    posts: list[ChatPostResponse] = Field(
        default_factory=list,
    )