import os
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app import crud

# .env 파일 로드
load_dotenv()

# 비동기 OpenAI 클라이언트 초기화 (.env에 OPENAI_API_KEY 필수)
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def get_chat_response(user_question: str, db: Session) -> str:
    # 1. 질문에서 검색 키워드 추출 (간단하게 띄어쓰기 기준 2글자 이상 단어)
    keywords = [word for word in user_question.split() if len(word) >= 2]
    
    search_results = []
    
    # 2. DB에서 관광 데이터 검색
    if keywords:
        for keyword in keywords:
            # 만들어두신 crud.search_contents 활용
            results = crud.search_contents(db, keyword)
            if results:
                search_results.extend(results)
                break  # 첫 번째로 매칭된 결과만 가져와도 충분함

    # 검색 결과가 없다면 임의의 데이터(예: 축제/행사 - contenttypeid=15) 상위 10개 가져오기
    if not search_results:
        search_results = crud.get_contents_by_type(db, content_type_id=15)[:10]

    # 중복 제거 및 상위 10개로 제한 (토큰 제한 방지)
    search_results = list(set(search_results))[:10]

    # 3. 프롬프트에 주입할 컨텍스트(문맥) 문자열 생성
    context_text = "다음은 관련된 서울 지역 정보입니다:\n"
    for item in search_results:
        title = item.title or "이름 없음"
        addr = item.addr1 or "주소 미상"
        tel = item.tel or "전화번호 없음"
        context_text += f"- {title} (주소: {addr}, 전화: {tel})\n"

    # 4. OpenAI API 호출
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # 또는 gpt-4o-mini
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "너는 지역 정보 공유 커뮤니티 'LocalHub'의 안내 챗봇이야. "
                        "친절하고 간결하게 대답해. 다음 제공된 [지역 정보]를 최우선으로 참고해서 답변하고, "
                        f"데이터에 없는 내용은 일반적인 상식선에서 답변해줘.\n\n[지역 정보]\n{context_text}"
                    )
                },
                {"role": "user", "content": user_question}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"죄송합니다, 챗봇 서버 응답에 문제가 발생했습니다. ({str(e)})"