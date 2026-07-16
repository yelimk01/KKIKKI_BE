import os
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app import crud

# .env 파일 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# ==========================================
# 1. 환경 설정 및 클라이언트 초기화
# ==========================================
IS_RENDER = os.environ.get("RENDER") == "true"

if IS_RENDER:
    # Render 배포 환경 (클라우드)
    print("☁️ [System] Render 클라우드 환경입니다. OpenAI API를 연결합니다.")
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_key")
    
    client = AsyncOpenAI(api_key=api_key)
    
    # PDF 가이드에 명시된 전용 모델명 사용
    MODEL_NAME = "gpt-5-mini" 
else:
    # 로컬 개발 환경 (내 PC)
    print("💻 [System] 로컬 환경입니다. API에 연결합니다.")
    
    # 로컬 테스트 시에도 .env에 있는 키를 불러옵니다.
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_key")
    
    client = AsyncOpenAI(
        api_key=api_key
        # 로컬 프록시나 별도 서버 주소가 있다면 아래 주석을 풀고 사용하세요.
        # base_url="http://localhost:8000/v1" 
    )
    
    MODEL_NAME = "gpt-5-mini"


# ==========================================
# 2. 챗봇 응답 생성 함수
# ==========================================
async def get_chat_response(user_question: str, history: list[ChatHistoryItem], db: Session) -> str:
    # 키가 없을 때의 임시(Mock) 응답 처리
    if api_key == "dummy_key" or api_key.startswith("sk-여기에"):
        return f"안녕하세요! 현재 챗봇 API 키가 등록되지 않아 임시로 답변해 드립니다. (질문 확인: '{user_question}')"

    # 1. 질문에서 검색 키워드 추출 (생략, 기존 코드와 동일)
    keywords = [word for word in user_question.split() if len(word) >= 2]
    search_results = []
    
    if keywords:
        for keyword in keywords:
            results = crud.search_contents(db, keyword)
            if results:
                search_results.extend(results)
                break  

    if not search_results:
        search_results = crud.get_contents_by_type(db, content_type_id=15)[:10]

    unique_results = {getattr(item, 'contentid', id(item)): item for item in search_results}.values()
    
    # 3. 프롬프트 문맥 생성
    context_text = "다음은 관련된 서울 지역 정보입니다:\n"
    for item in list(unique_results)[:3]:
        title = getattr(item, 'title', "이름 없음")
        addr = getattr(item, 'addr1', "주소 미상")
        tel = getattr(item, 'tel', "전화번호 없음")
        context_text += f"- {title} (주소: {addr}, 전화: {tel})\n"

    # 4. API 호출
    try:
        # (1) 시스템 프롬프트 설정
        messages = [
            {
                "role": "system", 
                "content": (
                    "너는 지역 정보 공유 커뮤니티 'LocalHub'의 안내 챗봇이야. "
                    "친절하고 간결하게 대답해. 다음 제공된 [지역 정보]를 최우선으로 참고해서 답변하고, "
                    f"데이터에 없는 내용은 일반적인 상식선에서 답변해줘.\n\n[지역 정보]\n{context_text}"
                )
            }
        ]
        
        # (2) 이전 대화 히스토리 추가
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
            
        # (3) 현재 사용자 질문 추가
        messages.append({"role": "user", "content": user_question})

        response = await client.chat.completions.create(
            model=MODEL_NAME, 
            messages=messages,
            max_completion_tokens=2000 
        )
        print("========== RESPONSE ==========")
        print(response.model_dump())
        print("==============================")
    
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Chatbot Error: {str(e)}")
        return f"죄송합니다, 챗봇 서버 연결에 문제가 발생했습니다. (내부 에러 로그를 확인해주세요.)"