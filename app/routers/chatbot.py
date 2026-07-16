from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_response

router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)

@router.post("", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    # DB 세션, 사용자의 질문, 그리고 히스토리를 함께 넘김
    answer = await get_chat_response(request.question, request.history, db)
    return ChatResponse(answer=answer)