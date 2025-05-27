"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Case(Base):
    """案件表"""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    subjects = relationship("Subject", back_populates="case")
    analysis_sessions = relationship("AnalysisSession", back_populates="case")

class Subject(Base):
    """当事人表"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    name = Column(String)
    role = Column(String)  # suspect, witness, victim, other
    gender = Column(String)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    case = relationship("Case", back_populates="subjects")
    analysis_sessions = relationship("AnalysisSession", back_populates="subject")

class AnalysisSession(Base):
    """分析会话表"""
    __tablename__ = "analysis_sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String)  # initializing, processing, analyzing, fusing, assessing, generating, completed, failed
    error_message = Column(Text, nullable=True)
    
    # 关系
    case = relationship("Case", back_populates="analysis_sessions")
    subject = relationship("Subject", back_populates="analysis_sessions")
    raw_data_refs = relationship("RawDataRef", back_populates="session")
    facial_expressions = relationship("FacialExpressionEvent", back_populates="session")
    speech_emotions = relationship("SpeechEmotionSegment", back_populates="session")
    text_sentiments = relationship("TextSentimentSnippet", back_populates="session")
    fused_states = relationship("FusedEmotionState", back_populates="session")
    psychological_assessments = relationship("PsychologicalAssessment", back_populates="session")
    alerts = relationship("SystemAlert", back_populates="session")

class RawDataRef(Base):
    """原始数据引用表"""
    __tablename__ = "raw_data_references"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    file_path = Column(String)
    modality = Column(String)  # video, audio, text, physiological
    file_size = Column(Integer, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("AnalysisSession", back_populates="raw_data_refs")

class FacialExpressionEvent(Base):
    """面部表情事件表"""
    __tablename__ = "facial_expression_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    timestamp = Column(DateTime)
    type = Column(String)  # 微表情类型
    intensity = Column(Float)  # 强度 0-1
    confidence = Column(Float)  # 置信度 0-1
    frame_number = Column(Integer, nullable=True)
    roi_coordinates = Column(JSON, nullable=True)  # 感兴趣区域坐标
    
    # 关系
    session = relationship("AnalysisSession", back_populates="facial_expressions")

class SpeechEmotionSegment(Base):
    """语音情感片段表"""
    __tablename__ = "speech_emotion_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    emotion_type = Column(String)  # 情感类型
    intensity = Column(Float)  # 强度 0-1
    confidence = Column(Float)  # 置信度 0-1
    acoustic_features = Column(JSON, nullable=True)  # 声学特征
    speaker_id = Column(String, nullable=True)
    
    # 关系
    session = relationship("AnalysisSession", back_populates="speech_emotions")

class TextSentimentSnippet(Base):
    """文本情感片段表"""
    __tablename__ = "text_sentiment_snippets"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    timestamp = Column(DateTime)
    text_content = Column(Text)
    sentiment_polarity = Column(String)  # positive, negative, neutral
    emotion_type = Column(String, nullable=True)
    intensity = Column(Float)  # 情感强度
    confidence = Column(Float)  # 置信度
    keywords = Column(JSON, nullable=True)  # 关键词列表
    
    # 关系
    session = relationship("AnalysisSession", back_populates="text_sentiments")

class FusedEmotionState(Base):
    """融合情感状态表"""
    __tablename__ = "fused_emotion_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    timestamp = Column(DateTime)
    fused_emotion_vector = Column(JSON)  # 融合情感向量
    activation_level = Column(Float, nullable=True)  # 激活度
    valence_level = Column(Float, nullable=True)  # 效价度
    
    # 关系
    session = relationship("AnalysisSession", back_populates="fused_states")

class PsychologicalAssessment(Base):
    """心理状态评估表"""
    __tablename__ = "psychological_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    timestamp = Column(DateTime)
    psychological_state_vector = Column(JSON)  # 心理状态向量
    radar_data_points = Column(JSON)  # 雷达图数据点
    overall_emotion_intensity = Column(Float, nullable=True)  # 整体情感强度
    identified_risks = Column(JSON, nullable=True)  # 识别的风险
    intervention_suggestions = Column(JSON, nullable=True)  # 干预建议
    risk_level = Column(String, nullable=True)  # 风险等级
    
    # 关系
    session = relationship("AnalysisSession", back_populates="psychological_assessments")

class SystemAlert(Base):
    """系统预警表"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("analysis_sessions.session_id"))
    alert_type = Column(String)  # 预警类型
    severity = Column(String)  # low, medium, high
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="active")  # active, acknowledged, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # 关系
    session = relationship("AnalysisSession", back_populates="alerts")
