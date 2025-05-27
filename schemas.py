"""
Pydantic模型定义 - 用于API请求/响应验证
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CaseCreate(BaseModel):
    case_number: str
    title: str
    description: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    case_number: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubjectCreate(BaseModel):
    case_id: int
    name: str
    role: str  # suspect, witness, victim, other
    gender: Optional[str] = None
    age: Optional[int] = None

class SubjectResponse(BaseModel):
    id: int
    case_id: int
    name: str
    role: str
    gender: Optional[str] = None
    age: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisSessionCreate(BaseModel):
    case_id: int
    subject_id: int

class AnalysisSessionResponse(BaseModel):
    session_id: str
    case_id: int
    subject_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    
    class Config:
        from_attributes = True

class EmotionIntensityData(BaseModel):
    timestamp: str
    intensity: float

class AnalysisResult(BaseModel):
    session_id: str
    status: str
    emotion_intensity_time_series: List[EmotionIntensityData]
    psychological_radar_data: Optional[Dict[str, Any]] = None
    potential_risks: Optional[List[Dict[str, Any]]] = None
    intervention_suggestions: Optional[List[str]] = None

class AlertCreate(BaseModel):
    session_id: str
    alert_type: str
    severity: str
    title: str
    description: str

class AlertResponse(BaseModel):
    id: int
    session_id: str
    alert_type: str
    severity: str
    title: str
    description: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportResult(BaseModel):
    session_id: str
    status: str
    report_data: Optional[Dict[str, Any]] = None
    report_url: Optional[str] = None

class RealTimeAnalysisData(BaseModel):
    current_intensity: float
    latest_microexpression: str
    latest_speech_emotion: str
    radar_data: Optional[Dict[str, Any]] = None
    timestamp: str

class SystemStats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_cases: int
    system_status: str
