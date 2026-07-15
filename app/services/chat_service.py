import os
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app import crud

# .env 파일 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)


# 환경 변수에서 가져오기
api_key = os.environ.get("OPENAI_API_KEY", "local-llm")

client = AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

async def get_chat_response(user_question: str, db: Session) -> str:
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
            model="gpt-5-mini", 
            messages=[
                {"role": "system", "content": f"안내 챗봇이야. [지역 정보]를 참고해 답변해줘.\n\n[지역 정보]\n{context_text}"},
                {"role": "user", "content": user_question}
            ],
            temperature=0.5,
            max_completion_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"챗봇 연결 실패: {str(e)}"