from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import relationship
from src.models.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # status: 'active', 'completed'
    status = Column(String, default="active")
    # metadata: 存储年龄、性别、主诉、赛道等上下文信息
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False)
    user = relationship("User")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    # role: 'user', 'assistant', 'system'
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())

    session = relationship("Session", back_populates="messages")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), unique=True)
    score = Column(Integer)
    risk_level = Column(String)
    # 完整报告内容的 JSON 结构
    content = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    session = relationship("Session", back_populates="report")

