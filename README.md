# LocalHub 🗺️

> 관광 데이터와 생성형 AI를 연결한 지역 정보 커뮤니티 서비스

LocalHub는 서울의 관광 정보를 탐색하고 사용자 간 정보를 공유할 수 있는
지역 기반 커뮤니티 서비스입니다.

관광 콘텐츠 조회뿐만 아니라 게시글과 댓글을 통해 정보를 공유할 수 있으며,
사용자가 자연어로 지역 정보를 탐색할 수 있도록
**서비스 데이터베이스와 OpenAI API를 연결한 AI 챗봇**을 구현했습니다.

---

## 1. Project Overview

기존 관광 정보 서비스에서는 사용자가 원하는 장소를 찾기 위해
검색 조건을 직접 설정하거나 여러 정보를 확인해야 합니다.

LocalHub에서는 이러한 탐색 과정을 개선하기 위해

- 관광 콘텐츠 검색 및 지역별 탐색
- 관광지와 연결된 커뮤니티
- 자연어 기반 AI 관광정보 탐색

기능을 하나의 서비스로 구성했습니다.

특히 AI 챗봇에서는 사용자의 질문을 LLM에 그대로 전달하는 대신,
**서비스가 보유한 관광 데이터를 먼저 검색하고 해당 정보를
LLM의 Context로 제공하는 구조**를 적용했습니다.

이를 통해 생성형 AI와 기존 서비스 데이터를 연결하는 방법을
직접 설계하고 구현했습니다.

---


## 2. Tech Stack

### Backend

| Technology | Usage |
|---|---|
| Python | Backend development |
| FastAPI | REST API / AI Chatbot API |
| SQLAlchemy | ORM / Database access |
| SQLite | LocalHub database |
| Pydantic | Request / Response validation |
| Uvicorn | ASGI server |

### AI

| Technology | Usage |
|---|---|
| OpenAI API | Natural language response generation |
| AsyncOpenAI | Asynchronous LLM API requests |
| Prompt Context | DB search results 기반 응답 생성 |
| Conversation History | Multi-turn conversation context |

### Deployment / Integration

| Technology | Usage |
|---|---|
| Render | Backend deployment environment |
| Netlify | Frontend deployment environment |
| REST API | Frontend–Backend communication |

---

## 3. System Architecture

```text
┌───────────────┐
│     User      │
└───────┬───────┘
        │
        │ HTTP Request
        ▼
┌───────────────────────┐
│       Frontend        │
└───────────┬───────────┘
            │ REST API
            ▼
┌───────────────────────────────┐
│            FastAPI            │
│                               │
│  ┌──────────┐  ┌───────────┐ │
│  │ Contents │  │ Community │ │
│  │   API    │  │    API    │ │
│  └────┬─────┘  └───────────┘ │
│       │                       │
│  ┌────▼─────────────────────┐ │
│  │      AI Chatbot API      │ │
│  └────┬───────────────┬─────┘ │
└───────┼───────────────┼───────┘
        │               │
        ▼               ▼
┌──────────────┐  ┌──────────────┐
│    SQLite    │  │  OpenAI API  │
│ Tourism Data │  │     LLM      │
└──────────────┘  └──────────────┘
```

---

## 4. AI Chatbot

### 핵심 설계

AI 챗봇을 구현하면서 가장 중요하게 고려한 부분은

> **LLM이 자체 지식에만 의존하지 않고
> LocalHub가 보유한 데이터를 우선 활용하도록 하는 것**

이었습니다.

사용자의 질문을 그대로 LLM에 전달하는 대신,
질문과 관련된 관광 데이터를 먼저 데이터베이스에서 검색한 뒤
해당 결과를 Prompt Context로 구성하여 전달하도록 설계했습니다.

### Chatbot Flow

```text
사용자 질문
    │
    ▼
질문에서 검색 키워드 추출
    │
    ▼
LocalHub DB 검색
    │
    ▼
검색 결과 중복 제거
    │
    ▼
관련 관광 정보 선택
    │
    ▼
Prompt Context 생성
    │
    ├──── 이전 대화 History
    │
    ▼
OpenAI API 호출
    │
    ▼
사용자에게 답변 반환
```

### 1) Keyword Extraction

사용자 질문을 단어 단위로 분리하고
2자 이상의 단어를 검색 키워드 후보로 사용합니다.

```python
keywords = [
    word
    for word in user_question.split()
    if len(word) >= 2
]
```

### 2) Database Search

추출한 키워드를 이용하여 LocalHub 데이터베이스에서
관련 관광 콘텐츠를 검색합니다.

검색 결과가 존재하면 해당 데이터를 AI 답변의 근거 정보로 사용합니다.

### 3) Duplicate Removal

동일한 관광 콘텐츠가 중복으로 전달되지 않도록
`contentid`를 기준으로 검색 결과를 정리합니다.

```python
unique_results = {
    getattr(item, "contentid", id(item)): item
    for item in search_results
}.values()
```

### 4) Context Generation

검색 결과 중 주요 관광 정보를 선택하여
장소명, 주소, 전화번호를 포함한 Context를 생성합니다.

```text
[지역 정보]

- 장소 A
  주소: ...
  전화번호: ...

- 장소 B
  주소: ...
  전화번호: ...
```

생성된 Context를 System Prompt에 포함해
LLM이 서비스 데이터를 우선 참고하도록 구성했습니다.

### 5) Conversation History

현재 질문뿐만 아니라 이전 대화 내용을 함께 전달하여
연속된 질문에서도 대화의 맥락을 유지하도록 구현했습니다.

```text
System Prompt
     +
DB Context
     +
Previous Conversation History
     +
Current User Question
          │
          ▼
      OpenAI API
```

---

## 5. Main Features

### 관광 콘텐츠

- 관광 콘텐츠 목록 조회
- Keyword 검색
- 자치구별 필터링
- 콘텐츠 유형별 필터링
- 페이지네이션
- 이름 / 최신순 / 조회수 / 언급수 정렬
- 상세 조회
- 상세 조회 시 조회수 증가

### Community

- 게시글 작성 및 조회
- 관광 콘텐츠와 게시글 연결
- 댓글 기능
- 게시글 이미지 관리
- 조회수 및 좋아요 관리

### AI Chatbot

- 자연어 질문 입력
- 질문 기반 관광 데이터 검색
- DB 검색 결과 기반 Prompt Context 생성
- OpenAI API 기반 응답 생성
- 이전 대화 History 반영
- API 오류 발생 시 예외 응답

---

## 6. Database

### TourContent

관광 콘텐츠 정보를 관리합니다.

주요 데이터

```text
contentid
contenttypeid
title
addr1 / addr2
district_name
tel
mapx / mapy
firstimage
view_count
mention_count
```

### Post

커뮤니티 게시글을 관리하며,
특정 관광 콘텐츠와 연결할 수 있도록 설계했습니다.

```text
Post
 ├── TourContent
 ├── Comment
 └── PostImage
```

관광 콘텐츠가 삭제되는 경우에도 게시글 자체는 유지될 수 있도록
TourContent와 Post 사이의 관계를 구성했습니다.

---

## 7. Project Structure

```text
KKIKKI_BE
│
├── app
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   │
│   ├── routers
│   │   ├── contents.py
│   │   ├── posts.py
│   │   ├── comments.py
│   │   ├── images.py
│   │   └── chatbot.py
│   │
│   ├── services
│   │   ├── chat_service.py
│   │   ├── json_loader.py
│   │   └── file_upload.py
│   │
│   ├── data
│   ├── static
│   └── utils
│
└── requirements.txt
```

Router와 Service를 분리하여
API 요청 처리와 비즈니스 로직의 역할을 구분했습니다.

---

## 8. What I Learned

### 1. AI 모델과 서비스 데이터의 연결

생성형 AI를 호출하는 것만으로는
서비스가 보유한 정보를 정확하게 활용하기 어렵다는 점을 경험했습니다.

이를 해결하기 위해

**질문 → 데이터 검색 → Context 구성 → LLM 호출**

과정을 직접 설계하면서
AI와 서비스 데이터를 연결하는 방법을 학습했습니다.

### 2. AI도 하나의 Backend Component이다

챗봇을 구현하면서 AI 기능 역시 독립적인 기능이 아니라
DB, API, 사용자 요청과 연결되는 Backend Component라는 점을 배웠습니다.

따라서 모델 성능뿐만 아니라

- 어떤 데이터를 모델에 제공할지
- 어떤 정보를 우선하도록 할지
- 대화 맥락을 어떻게 유지할지
- API 오류를 어떻게 처리할지

까지 함께 고려해야 안정적인 AI 서비스를 만들 수 있다는 것을 경험했습니다.

### 3. 데이터 구조의 중요성

관광 콘텐츠와 게시글을 연결하고
조회수와 언급 횟수를 관리하면서
서비스 요구사항에 맞는 데이터 모델과 관계를 설계하는 경험을 쌓았습니다.

---

## 9. Local Setup

### Repository Clone

```bash
git clone <repository-url>
cd KKIKKI_BE
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

> API Key는 GitHub에 업로드하지 않습니다.

### Run Server

```bash
uvicorn app.main:app --reload
```

FastAPI Swagger UI를 통해 API를 확인할 수 있습니다.

```text
http://localhost:8000/docs
```
