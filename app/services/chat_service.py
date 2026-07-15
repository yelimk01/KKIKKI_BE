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
# 💡 핵심: 실행 환경(Render vs 로컬) 구분하기
# ==========================================
IS_RENDER = os.environ.get("RENDER") == "true"

if IS_RENDER:
    # 1. Render 배포 환경 (클라우드) -> 실제 OpenAI API 사용
    print("☁️ [System] Render 클라우드 환경입니다. OpenAI API를 연결합니다.")
    api_key = os.environ.get("OPENAI_API_KEY", "dummy_key")
    client = AsyncOpenAI(api_key=api_key)
    MODEL_NAME = "gpt-4o-mini" # OpenAI 모델 사용
else:
    # 2. 로컬 개발 환경 (내 PC) -> 로컬 LLM 사용
    print("💻 [System] 로컬 환경입니다. 로컬 LLM 서버에 연결합니다.")
    api_key = "local-llm"
    client = AsyncOpenAI(
        api_key=api_key, 
        base_url="http://localhost:8000/v1" # LM Studio, Ollama 등 포트에 맞게 수정 (예: 1234, 11434, 8000)
    )
    MODEL_NAME = "여기에-로컬-모델명-입력" # ⚠️ 내 PC에서 쓰는 모델명으로 반드시 변경! (예: gemma-2-2b-it)

async def get_chat_response(user_question: str, db: Session) -> str:
    # 키가 없을 때의 임시(Mock) 응답 처리
    if IS_RENDER and (api_key == "dummy_key" or api_key.startswith("sk-여기에")):
        return f"안녕하세요! 현재 챗봇 API 키가 등록되지 않아 임시로 답변해 드립니다. (질문 확인: '{user_question}')"

    # 1. 질문에서 검색 키워드 추출
    keywords = [word for word in user_question.split() if len(word) >= 2]
    search_results = []
    
    # 2. DB에서 관광 데이터 검색
    if keywords:
        for keyword in keywords:
            results = crud.search_contents(db, keyword)
            if results:
                search_results.extend(results)
                break  

    if not search_results:
        search_results = crud.get_contents_by_type(db, content_type_id=15)[:10]

    # 객체 ID 기반 중복 제거
    unique_results = {item.contentid: item for item in search_results}.values()
    
    # 3. 프롬프트 문맥 생성
    context_text = "다음은 관련된 서울 지역 정보입니다:\n"
    for item in unique_results:
        title = item.title or "이름 없음"
        addr = item.addr1 or "주소 미상"
        context_text += f"- {title} (주소: {addr})\n"

    # 4. API 호출
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME, # 위에서 설정한 모델명이 자동으로 들어갑니다.
            messages=[
                {"role": "system", "content": f"너는 지역 정보 공유 커뮤니티 'LocalHub'의 안내 챗봇이야. 제공된 [지역 정보]를 참고해 답변해줘.\n\n[지역 정보]\n{context_text}"},
                {"role": "user", "content": user_question}
            ],
            temperature=0.5,
            max_completion_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Chatbot Error: {str(e)}") # Render 로그 확인용
        return f"죄송합니다, 챗봇 서버 응답에 문제가 발생했습니다. 관리자에게 문의해주세요."