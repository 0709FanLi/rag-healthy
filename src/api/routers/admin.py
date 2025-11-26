from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from typing import List
import random
from datetime import datetime

from src.api.dependencies import get_db, get_current_user
from src.models.tables import Session, Report, User, Message
from src.schemas.admin import (
    DashboardMetricsResponse,
    DashboardFunnelResponse,
    DashboardDistributionResponse,
    RecordListResponse,
    RecordListItem,
    RecordDetailResponse,
    FunnelStep,
    TrackDistributionItem
)

router = APIRouter(prefix="/admin", tags=["Admin"])

# --- 工具函数 ---

def format_rid(session_id: int, created_at: datetime) -> str:
    date_str = created_at.strftime("%Y%m%d")
    return f"R-{date_str}-{session_id:02d}"

def format_uid(user_id: int) -> str:
    return f"U-{user_id}"

def get_mock_status(session_id: int) -> str:
    # 基于 ID 的确定性模拟：ID 为偶数则"已转化"
    return "已转化" if session_id % 2 == 0 else "未转化"

# --- 看板接口 ---

@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取核心指标数据 (部分 Mock)"""
    # 真实数据
    session_count = await db.scalar(select(func.count(Session.id)))
    report_count = await db.scalar(select(func.count(Report.id)))
    
    # Mock 数据 (基于真实数据按比例生成)
    converting_reports = int(report_count * 0.67) # 假定 67% 转化
    total_clicks = int(report_count * 1.7)        # 假定人均 1.7 次点击
    
    return {
        "consults": session_count or 0,
        "reports": report_count or 0,
        "converting_reports": converting_reports,
        "total_clicks": total_clicks
    }

@router.get("/dashboard/funnel", response_model=DashboardFunnelResponse)
async def get_dashboard_funnel(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取漏斗数据"""
    session_count = await db.scalar(select(func.count(Session.id))) or 0
    report_count = await db.scalar(select(func.count(Report.id))) or 0
    
    # Mock 点击数
    click_count = int(report_count * 0.67)
    
    return {
        "steps": [
            {"label": "1. 会话接入", "value": session_count, "percentage": 100},
            {"label": "2. 报告生成", "value": report_count, "percentage": int(report_count/session_count*100) if session_count else 0},
            {"label": "3. 转化点击", "value": click_count, "percentage": int(click_count/session_count*100) if session_count else 0}
        ]
    }

@router.get("/dashboard/distribution", response_model=DashboardDistributionResponse)
async def get_dashboard_distribution(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取赛道分布数据"""
    # 尝试从 meta_data 统计赛道，但由于 meta_data 是 JSON，SQLAlchemy 直接聚合可能依赖数据库特定语法
    # 这里为了兼容性，我们先查出所有 session 的 meta_data 在内存中统计（数据量大时需优化）
    
    result = await db.execute(select(Session.meta_data))
    all_meta = result.scalars().all()
    
    track_counts = {}
    total = 0
    
    for meta in all_meta:
        if meta and isinstance(meta, dict):
            track = meta.get("track", "其他")
            track_counts[track] = track_counts.get(track, 0) + 1
            total += 1
            
    if total == 0:
        # 如果没有数据，返回空或默认Mock
        return {"distribution": []}

    # 转换为响应格式
    colors = ["bg-primary", "bg-success", "bg-warning", "bg-secondary", "bg-info", "bg-danger", "bg-dark"]
    distribution = []
    
    sorted_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (name, count) in enumerate(sorted_tracks):
        color = colors[i % len(colors)]
        distribution.append({
            "name": name,
            "value": int(count / total * 100),
            "color": color
        })
        
    return {"distribution": distribution}


# --- 记录列表接口 ---

@router.get("/records/list", response_model=RecordListResponse)
async def get_records_list(
    current_user = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
    track: str = None,
    status: str = None,
    search: str = None,
    db: AsyncSession = Depends(get_db)
):
    """分页获取评估记录列表"""
    query = select(Session, Report, User).join(User, Session.user_id == User.id).outerjoin(Report, Session.id == Report.session_id)
    
    # 排序
    query = query.order_by(desc(Session.created_at))
    
    # 简单的内存过滤 (复杂过滤建议在 DB 层，但 JSON 字段过滤在 SQLite/PG 间有差异)
    # 这里先取出分页的一批，注意：这种方式在数据量大时有性能问题，
    # 但由于 Track 在 JSON 中，且 Status 是 Mock 的，只能这样处理或 Mock DB字段。
    # 修正：为了演示，我们先只做 DB 层的分页，Filter 逻辑简单处理
    
    # 计算 offset
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    # 获取总数
    total_result = await db.scalar(select(func.count(Session.id)))
    
    records = []
    for session, report, user in rows:
        # 解析 Track
        current_track = "未知赛道"
        if session.meta_data and isinstance(session.meta_data, dict):
            current_track = session.meta_data.get("track", "未知赛道")
            
        # Mock Status
        current_status = get_mock_status(session.id)
        
        # 风险等级
        risk = "未评估"
        if report:
            risk = report.risk_level or "未评估"
            # 简单的风险转换逻辑，保证前端样式
            if "高" in risk: risk = "高"
            elif "中" in risk: risk = "中"
            elif "低" in risk: risk = "低"
        
        # 过滤逻辑 (内存中补充过滤，实际生产应在 SQL 中)
        if track and track != current_track:
            continue
        if status and status != current_status:
            continue
            
        records.append(RecordListItem(
            rid=format_rid(session.id, session.created_at),
            uid=format_uid(user.id),
            session_id=session.id,
            user_id=user.id,
            track=current_track,
            risk=risk,
            time=session.created_at.strftime("%m-%d %H:%M"),
            status=current_status
        ))
        
    return {
        "total": total_result or 0,
        "records": records
    }

@router.get("/records/{session_id}", response_model=RecordDetailResponse)
async def get_record_detail(
    session_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单条记录详情"""
    # 查询 Session, Report, User
    result = await db.execute(
        select(Session, Report, User)
        .join(User, Session.user_id == User.id)
        .outerjoin(Report, Session.id == Report.session_id)
        .where(Session.id == session_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session, report, user = row
    
    # 查询消息构建 QnA
    msgs_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = msgs_result.scalars().all()
    
    qna_list = []
    # 简单策略：提取所有 role=user 的消息作为 A，它前面的一条作为 Q
    for i, msg in enumerate(messages):
        if msg.role == "user":
            answer = msg.content
            question = "AI 提问"
            if i > 0 and messages[i-1].role == "assistant":
                # 截取前 15 个字符作为问题摘要
                prev_content = messages[i-1].content
                # 清理一下内容，去掉"【给用户的回复】"等
                if "【给用户的回复】" in prev_content:
                    prev_content = prev_content.split("【给用户的回复】")[-1].strip()
                question = prev_content[:10] + "..."
            
            qna_list.append(f"Q:{question} A:{answer}")
            
    qna_str = "; ".join(qna_list)
    
    # 提取报告 HTML
    report_html = "<div>暂无报告数据</div>"
    risk = "未评估"
    
    if report and report.content and isinstance(report.content, dict):
        report_html = report.content.get("html", "")
        risk = report.risk_level or "未评估"
        if "高" in risk: risk = "高"
        elif "中" in risk: risk = "中"
        elif "低" in risk: risk = "低"

    # 兼容 track 字段
    current_track = "未知赛道"
    if session.meta_data and isinstance(session.meta_data, dict):
        current_track = session.meta_data.get("track", "未知赛道")

    return RecordDetailResponse(
        rid=format_rid(session.id, session.created_at),
        uid=format_uid(user.id),
        track=current_track,
        risk=risk,
        status=get_mock_status(session.id),
        qna=qna_str,
        report_html=report_html,
        created_at=session.created_at
    )

