from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, Dict, List
from src.models.database import get_db
from src.models.tables import User, Session as DBSession, Message
from src.api.dependencies import get_current_user
from src.services.business_service import business_service

router = APIRouter()

class MessageItem(BaseModel):
    role: str
    content: str

class StartSessionResponse(BaseModel):
    session_id: int
    messages: List[MessageItem]

class ChatRequest(BaseModel):
    session_id: int
    content: str

class ChatResponse(BaseModel):
    messages: Optional[List[str]] = None  # 多条消息（新格式）
    response: Optional[str] = None  # 单条消息（兼容旧格式）
    action: str  # 'chat' or 'report'
    report_data: Optional[Dict] = None

class SessionHistoryResponse(BaseModel):
    session_id: int
    messages: List[MessageItem]

@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 创建新会话
    session = await business_service.create_session(db, current_user.id)
    
    # 初始欢迎语（分成两条独立消息）
    # 第一条消息：问候语
    greeting_msg = "您好！我是您的 AI 健康管家。"
    msg1 = Message(session_id=session.id, role="assistant", content=greeting_msg)
    db.add(msg1)
    
    # 第二条消息：指引语
    instruction_msg = "为了提供精准的评估，我们需要为您进行定制化的对话采集。请描述您的年龄、性别，以及最近最困扰您的问题。"
    msg2 = Message(session_id=session.id, role="assistant", content=instruction_msg)
    db.add(msg2)
    
    await db.commit()
    
    # 返回两条消息
    return {
        "session_id": session.id,
        "messages": [
            {"role": "assistant", "content": greeting_msg},
            {"role": "assistant", "content": instruction_msg}
        ]
    }

@router.get("/active", response_model=SessionHistoryResponse)
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的活跃会话和历史消息"""
    try:
        # 查找最新的活跃会话
        result = await db.execute(
            select(DBSession)
            .where(DBSession.user_id == current_user.id)
            .where(DBSession.status == "active")
            .order_by(desc(DBSession.created_at))
        )
        session = result.scalars().first()  # 使用 first() 获取第一个结果
        
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")
        
        # 获取该会话的所有消息
        messages_result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()
        
        return {
            "session_id": session.id,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_active_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定会话的历史消息"""
    # 验证 session 归属
    result = await db.execute(
        select(DBSession).where(DBSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 获取该会话的所有消息
    messages_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return {
        "session_id": session.id,
        "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
    }

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 验证 session 属于当前用户
    session = await business_service.get_session(db, request.session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
        
    # 处理消息
    result = await business_service.process_chat(db, request.session_id, request.content)
    
    return result
