from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from src.models.database import get_db
from src.models.tables import Report, Session, User
from src.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

class ReportResponse(BaseModel):
    id: int
    score: int
    risk_level: str
    content: Dict[str, Any]
    created_at: datetime

class ReportListItem(BaseModel):
    session_id: int
    report_id: int
    score: int
    risk_level: str
    created_at: datetime
    preview: str  # 会话预览文字

class ReportListResponse(BaseModel):
    reports: List[ReportListItem]

# ⚠️ 重要：具体路由必须在参数路由之前定义
@router.get("/list", response_model=ReportListResponse)
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有报告列表"""
    from src.models.tables import Message
    
    # 查询用户所有的 session（有报告的）
    result = await db.execute(
        select(Session, Report)
        .join(Report, Session.id == Report.session_id)
        .where(Session.user_id == current_user.id)
        .order_by(desc(Report.created_at))
    )
    session_reports = result.all()
    
    reports_list = []
    for session, report in session_reports:
        # 获取该 session 的第一条用户消息作为预览
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .where(Message.role == "user")
            .order_by(Message.created_at)
            .limit(1)
        )
        first_msg = msg_result.scalar_one_or_none()
        preview = first_msg.content[:50] + "..." if first_msg and len(first_msg.content) > 50 else (first_msg.content if first_msg else "无预览")
        
        reports_list.append({
            "session_id": session.id,
            "report_id": report.id,
            "score": report.score,
            "risk_level": report.risk_level,
            "created_at": report.created_at,
            "preview": preview
        })
    
    return {"reports": reports_list}

@router.get("/{session_id}", response_model=ReportResponse)
async def get_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 验证 session 归属
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 获取报告
    report_result = await db.execute(select(Report).where(Report.session_id == session_id))
    report = report_result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "score": report.score,
        "risk_level": report.risk_level,
        "content": report.content,
        "created_at": report.created_at
    }

@router.post("/{session_id}/generate")
async def generate_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """触发报告生成（如果尚未生成）"""
    from src.services.business_service import business_service
    
    # 验证 session 归属
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 获取报告
    report_result = await db.execute(select(Report).where(Report.session_id == session_id))
    report = report_result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # 检查报告状态
    if report.content.get("status") == "generating":
        # 调用生成逻辑
        await business_service.generate_report_content(db, session_id)
        await db.refresh(report)
    
    return {
        "id": report.id,
        "score": report.score,
        "risk_level": report.risk_level,
        "content": report.content,
        "created_at": report.created_at
    }

