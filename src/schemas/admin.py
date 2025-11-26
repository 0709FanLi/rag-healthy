from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- 看板相关 ---

class DashboardMetricsResponse(BaseModel):
    consults: int
    reports: int
    converting_reports: int
    total_clicks: int

class FunnelStep(BaseModel):
    label: str
    value: int
    percentage: int

class DashboardFunnelResponse(BaseModel):
    steps: List[FunnelStep]

class TrackDistributionItem(BaseModel):
    name: str
    value: int
    color: str

class DashboardDistributionResponse(BaseModel):
    distribution: List[TrackDistributionItem]


# --- 记录列表相关 ---

class RecordListItem(BaseModel):
    rid: str  # 格式化的 Session ID, e.g., R-20231124-01
    uid: str  # 格式化的 User ID, e.g., U-1001
    session_id: int
    user_id: int
    track: str
    risk: str
    time: str # 格式化后的时间字符串
    status: str # "已转化" | "未转化"

class RecordListResponse(BaseModel):
    total: int
    records: List[RecordListItem]


# --- 记录详情相关 ---

class RecordDetailResponse(BaseModel):
    rid: str
    uid: str
    track: str
    risk: str
    status: str
    qna: str # 拼接后的问答摘要
    report_html: str # HTML 报告快照
    created_at: datetime

