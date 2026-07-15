from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ==========================
# TourContent
# ==========================

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

    district_name: str | None = None

    view_count: int = 0
    mention_count: int = 0


class TourContentResponse(TourContentBase):
    model_config = ConfigDict(from_attributes=True)


# 게시글 응답에 포함할 간단한 장소 정보
class TourContentSimpleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contentid: str
    contenttypeid: int
    title: str

    addr1: str | None = None
    district_name: str | None = None

    firstimage: str | None = None
    firstimage2: str | None = None


# ==========================
# Post
# ==========================

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

    # 장소는 최대 한 개만 선택
    # 선택하지 않아도 글을 작성할 수 있게 None 허용
    tour_content_id: str | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    content: str
    author: str

    view_count: int
    like_count: int

    created_at: datetime
    updated_at: datetime

    # 선택된 장소의 contentid
    tour_content_id: str | None = None

    # 선택된 장소 상세 정보
    tour_content: TourContentSimpleResponse | None = None


class PostListResponse(BaseModel):
    """
    게시글 목록 화면에서 사용하는 간단한 응답 형식
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

    # 수정 권한 확인용
    password: str = Field(
        min_length=1,
        max_length=100,
    )

    # 수정할 때 장소를 변경하거나 제거할 수 있음
    tour_content_id: str | None = None


class PostDelete(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=100,
    )


class PasswordVerifyRequest(BaseModel):
    """
    게시글 수정·삭제 전 비밀번호 확인 모달에서 사용
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


# ==========================
# Pagination
# ==========================

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


# ==========================
# Comment
# ==========================

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


# ==========================
# ChatBot
# ==========================

class ChatHistoryItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
    )

    # 처음에는 사용하지 않아도 됨
    # 나중에 챗봇 대화 문맥을 전달할 때 사용
    history: list[ChatHistoryItem] = []


class ChatPlaceResponse(BaseModel):
    contentid: str
    title: str

    addr1: str | None = None
    district_name: str | None = None

    mapx: float | None = None
    mapy: float | None = None

    firstimage: str | None = None


class ChatPostResponse(BaseModel):
    id: int
    title: str

    author: str
    view_count: int
    like_count: int


class ChatResponse(BaseModel):
    answer: str

    # 챗봇 답변과 함께 프론트에 장소·게시글 카드를 보여주기 위한 값
    places: list[ChatPlaceResponse] = []
    posts: list[ChatPostResponse] = []