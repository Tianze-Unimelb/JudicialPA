"""
司法心理情感计算分析系统 - 后端主服务
基于FastAPI的RESTful API服务
"""

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uuid
import os
import asyncio
from datetime import datetime
import json
import logging

from database import get_db, SessionLocal
from models import (
    Case, Subject, AnalysisSession, RawDataRef, 
    FacialExpressionEvent, SpeechEmotionSegment, 
    TextSentimentSnippet, FusedEmotionState, 
    PsychologicalAssessment, SystemAlert
)
from schemas import (
    CaseCreate, SubjectCreate, AnalysisSessionCreate,
    AnalysisResult, ReportResult, AlertCreate
)
from analysis_engine import AnalysisEngine
from ai_service import AIService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="司法心理情感计算分析系统",
    description="基于多模态AI的司法心理分析平台",
    version="1.0.0"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 依赖注入
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 全局服务实例
analysis_engine = AnalysisEngine()
ai_service = AIService()

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("司法心理情感计算分析系统启动中...")
    await ai_service.initialize()
    logger.info("AI服务已初始化")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "司法心理情感计算分析系统 API v1.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_service": await ai_service.health_check()
    }

# 案件管理API
@app.post("/api/cases/", response_model=CaseCreate)
async def create_case(case: CaseCreate, db: SessionLocal = Depends(get_db_session)):
    """创建新案件"""
    db_case = Case(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@app.get("/api/cases/")
async def list_cases(db: SessionLocal = Depends(get_db_session)):
    """获取案件列表"""
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    return cases

@app.get("/api/cases/{case_id}")
async def get_case(case_id: int, db: SessionLocal = Depends(get_db_session)):
    """获取案件详情"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件未找到")
    return case

# 当事人管理API
@app.post("/api/subjects/", response_model=SubjectCreate)
async def create_subject(subject: SubjectCreate, db: SessionLocal = Depends(get_db_session)):
    """创建当事人记录"""
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/api/subjects/")
async def list_subjects(db: SessionLocal = Depends(get_db_session)):
    """获取当事人列表"""
    subjects = db.query(Subject).order_by(Subject.created_at.desc()).all()
    return subjects

# 分析会话API
@app.post("/api/sessions/start", status_code=202)
async def start_analysis_session(
    case_id: int,
    subject_id: int,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: SessionLocal = Depends(get_db_session)
):
    """启动分析会话"""
    session_id = str(uuid.uuid4())
    start_time = datetime.now()

    # 创建会话记录
    db_session = AnalysisSession(
        session_id=session_id,
        case_id=case_id,
        subject_id=subject_id,
        start_time=start_time,
        status="initializing"
    )
    db.add(db_session)
    db.commit()

    # 处理上传文件
    upload_dir = f"uploads/{session_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_paths = []
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        file_paths.append(file_path)
        
        # 记录原始数据引用
        raw_data_ref = RawDataRef(
            session_id=session_id,
            file_path=file_path,
            modality=determine_modality(file.filename),
            upload_time=datetime.now()
        )
        db.add(raw_data_ref)
    
    db.commit()

    # 启动后台分析任务
    background_tasks.add_task(
        analysis_engine.process_analysis_task,
        session_id,
        file_paths,
        db
    )

    return {
        "message": "分析任务已启动",
        "session_id": session_id,
        "status": "processing"
    }

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str, db: SessionLocal = Depends(get_db_session)):
    """获取会话状态"""
    session = db.query(AnalysisSession).filter(AnalysisSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    return {
        "session_id": session.session_id,
        "status": session.status,
        "progress": calculate_progress(session, db),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None
    }

@app.get("/api/sessions/{session_id}/results", response_model=AnalysisResult)
async def get_analysis_results(session_id: str, db: SessionLocal = Depends(get_db_session)):
    """获取分析结果"""
    session = db.query(AnalysisSession).filter(AnalysisSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")

    # 获取心理评估结果
    assessments = db.query(PsychologicalAssessment).filter(
        PsychologicalAssessment.session_id == session_id
    ).order_by(PsychologicalAssessment.timestamp).all()

    if not assessments:
        return {
            "session_id": session_id,
            "status": session.status,
            "message": "分析进行中，暂无结果"
        }

    # 构建返回数据
    latest_assessment = assessments[-1]
    
    emotion_intensity_data = [
        {
            "timestamp": a.timestamp.isoformat(),
            "intensity": a.overall_emotion_intensity or 0
        }
        for a in assessments
    ]

    return {
        "session_id": session_id,
        "status": session.status,
        "emotion_intensity_time_series": emotion_intensity_data,
        "psychological_radar_data": latest_assessment.radar_data_points,
        "potential_risks": latest_assessment.identified_risks,
        "intervention_suggestions": latest_assessment.intervention_suggestions
    }

# 实时分析API
@app.get("/api/sessions/{session_id}/realtime")
async def get_realtime_analysis(session_id: str, db: SessionLocal = Depends(get_db_session)):
    """获取实时分析数据"""
    # 获取最近的分析数据
    latest_assessment = db.query(PsychologicalAssessment).filter(
        PsychologicalAssessment.session_id == session_id
    ).order_by(PsychologicalAssessment.timestamp.desc()).first()
    
    latest_micro = db.query(FacialExpressionEvent).filter(
        FacialExpressionEvent.session_id == session_id
    ).order_by(FacialExpressionEvent.timestamp.desc()).first()
    
    latest_speech = db.query(SpeechEmotionSegment).filter(
        SpeechEmotionSegment.session_id == session_id
    ).order_by(SpeechEmotionSegment.start_time.desc()).first()

    return {
        "current_intensity": latest_assessment.overall_emotion_intensity if latest_assessment else 0,
        "latest_microexpression": latest_micro.type if latest_micro else "无",
        "latest_speech_emotion": latest_speech.emotion_type if latest_speech else "无",
        "radar_data": latest_assessment.radar_data_points if latest_assessment else None,
        "timestamp": datetime.now().isoformat()
    }

# 预警系统API
@app.get("/api/sessions/{session_id}/alerts")
async def get_session_alerts(session_id: str, db: SessionLocal = Depends(get_db_session)):
    """获取会话预警"""
    alerts = db.query(SystemAlert).filter(
        SystemAlert.session_id == session_id
    ).order_by(SystemAlert.created_at.desc()).limit(10).all()
    
    return [
        {
            "id": alert.id,
            "type": alert.alert_type,
            "level": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "time": alert.created_at.strftime("%H:%M:%S"),
            "status": alert.status
        }
        for alert in alerts
    ]

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: SessionLocal = Depends(get_db_session)):
    """确认处理预警"""
    alert = db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警未找到")
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now()
    db.commit()
    
    return {"message": "预警已确认"}

# 报告生成API
@app.get("/api/sessions/{session_id}/report", response_model=ReportResult)
async def generate_report(session_id: str, db: SessionLocal = Depends(get_db_session)):
    """生成分析报告"""
    session = db.query(AnalysisSession).filter(AnalysisSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    if session.status != "completed":
        return {
            "session_id": session_id,
            "status": session.status,
            "message": "分析未完成，报告暂不可用"
        }

    # 获取所有相关数据
    case_info = db.query(Case).filter(Case.id == session.case_id).first()
    subject_info = db.query(Subject).filter(Subject.id == session.subject_id).first()
    assessments = db.query(PsychologicalAssessment).filter(
        PsychologicalAssessment.session_id == session_id
    ).order_by(PsychologicalAssessment.timestamp).all()
    
    micro_events = db.query(FacialExpressionEvent).filter(
        FacialExpressionEvent.session_id == session_id
    ).order_by(FacialExpressionEvent.timestamp).all()
    
    speech_segments = db.query(SpeechEmotionSegment).filter(
        SpeechEmotionSegment.session_id == session_id
    ).order_by(SpeechEmotionSegment.start_time).all()
    
    text_snippets = db.query(TextSentimentSnippet).filter(
        TextSentimentSnippet.session_id == session_id
    ).order_by(TextSentimentSnippet.timestamp).all()

    # 生成报告内容
    report_content = generate_report_content(
        session, case_info, subject_info, assessments,
        micro_events, speech_segments, text_snippets
    )

    return {
        "session_id": session_id,
        "status": session.status,
        "report_data": report_content
    }

# AI服务集成API
@app.post("/api/ai/analyze-micro-expression")
async def analyze_micro_expression_endpoint(
    session_id: str,
    frame_data: dict
):
    """微表情分析接口"""
    try:
        result = await ai_service.analyze_micro_expression(frame_data)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"微表情分析失败: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/ai/analyze-speech-emotion")
async def analyze_speech_emotion_endpoint(
    session_id: str,
    audio_data: dict
):
    """语音情感分析接口"""
    try:
        result = await ai_service.analyze_speech_emotion(audio_data)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"语音情感分析失败: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/ai/analyze-text-sentiment")
async def analyze_text_sentiment_endpoint(
    session_id: str,
    text_data: dict
):
    """文本情感分析接口"""
    try:
        result = await ai_service.analyze_text_sentiment(text_data)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"文本情感分析失败: {e}")
        return {"success": False, "error": str(e)}

# 系统管理API
@app.get("/api/system/stats")
async def get_system_stats(db: SessionLocal = Depends(get_db_session)):
    """获取系统统计信息"""
    total_sessions = db.query(AnalysisSession).count()
    active_sessions = db.query(AnalysisSession).filter(
        AnalysisSession.status.in_(["processing", "analyzing"])
    ).count()
    total_cases = db.query(Case).count()
    
    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_cases": total_cases,
        "system_status": "operational"
    }

# 工具函数
def determine_modality(filename: str) -> str:
    """根据文件名确定模态类型"""
    ext = filename.lower().split('.')[-1]
    if ext in ['mp4', 'avi', 'mov', 'mkv']:
        return 'video'
    elif ext in ['wav', 'mp3', 'aac', 'flac']:
        return 'audio'
    elif ext in ['txt', 'docx', 'doc']:
        return 'text'
    else:
        return 'unknown'

def calculate_progress(session: AnalysisSession, db) -> int:
    """计算分析进度"""
    if session.status == "completed":
        return 100
    elif session.status == "failed":
        return 0
    
    # 基于已完成的分析步骤计算进度
    steps_completed = 0
    total_steps = 5
    
    if session.status in ["processing", "analyzing", "fusing", "assessing", "generating"]:
        steps_completed += 1
    if session.status in ["analyzing", "fusing", "assessing", "generating"]:
        steps_completed += 1
    if session.status in ["fusing", "assessing", "generating"]:
        steps_completed += 1
    if session.status in ["assessing", "generating"]:
        steps_completed += 1
    if session.status == "generating":
        steps_completed += 1
    
    return int((steps_completed / total_steps) * 100)

def generate_report_content(session, case_info, subject_info, assessments, 
                          micro_events, speech_segments, text_snippets) -> dict:
    """生成报告内容"""
    latest_assessment = assessments[-1] if assessments else None
    
    return {
        "header": {
            "case_number": case_info.case_number if case_info else "N/A",
            "subject_name": subject_info.name if subject_info else "N/A",
            "analysis_session_id": session.session_id,
            "analysis_time_range": f"{session.start_time.isoformat()} - {session.end_time.isoformat() if session.end_time else '进行中'}",
            "analyst": "智能分析系统"
        },
        "summary": generate_summary_text(assessments, micro_events, speech_segments, text_snippets),
        "emotion_intensity_analysis": {
            "time_series_data": [
                {"timestamp": a.timestamp.isoformat(), "intensity": a.overall_emotion_intensity}
                for a in assessments if a.overall_emotion_intensity
            ],
            "average_intensity": sum(a.overall_emotion_intensity for a in assessments if a.overall_emotion_intensity) / len(assessments) if assessments else 0,
            "peak_intensity": max(a.overall_emotion_intensity for a in assessments if a.overall_emotion_intensity) if assessments else 0
        },
        "psychological_radar_data": latest_assessment.radar_data_points if latest_assessment else {},
        "modality_analysis": {
            "micro_expressions": format_micro_expression_analysis(micro_events),
            "speech_emotions": format_speech_emotion_analysis(speech_segments),
            "text_sentiment": format_text_sentiment_analysis(text_snippets)
        },
        "risk_assessment": latest_assessment.identified_risks if latest_assessment else [],
        "intervention_suggestions": latest_assessment.intervention_suggestions if latest_assessment else [],
        "disclaimer": "本报告仅供辅助决策参考，不能替代专业的司法判断和心理评估。"
    }

def generate_summary_text(assessments, micro_events, speech_segments, text_snippets) -> str:
    """生成分析摘要"""
    if not assessments:
        return "分析数据不足，无法生成摘要。"
    
    avg_intensity = sum(a.overall_emotion_intensity for a in assessments if a.overall_emotion_intensity) / len(assessments)
    
    if avg_intensity > 70:
        stress_level = "高度紧张"
    elif avg_intensity > 40:
        stress_level = "中度紧张"
    else:
        stress_level = "相对平静"
    
    micro_count = len(micro_events)
    speech_count = len(speech_segments)
    text_count = len(text_snippets)
    
    return f"当事人在本次分析中表现出{stress_level}状态，检测到{micro_count}次微表情事件，{speech_count}个语音情感段落，{text_count}个文本情感片段。建议根据具体情况调整沟通策略。"

def format_micro_expression_analysis(micro_events) -> dict:
    """格式化微表情分析结果"""
    if not micro_events:
        return {"total_events": 0, "main_types": [], "average_intensity": 0}
    
    type_counts = {}
    total_intensity = 0
    
    for event in micro_events:
        type_counts[event.type] = type_counts.get(event.type, 0) + 1
        total_intensity += event.intensity
    
    main_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "total_events": len(micro_events),
        "main_types": [{"type": t[0], "count": t[1]} for t in main_types],
        "average_intensity": total_intensity / len(micro_events)
    }

def format_speech_emotion_analysis(speech_segments) -> dict:
    """格式化语音情感分析结果"""
    if not speech_segments:
        return {"total_segments": 0, "main_emotions": [], "average_intensity": 0}
    
    emotion_counts = {}
    total_intensity = 0
    
    for segment in speech_segments:
        emotion_counts[segment.emotion_type] = emotion_counts.get(segment.emotion_type, 0) + 1
        total_intensity += segment.intensity
    
    main_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "total_segments": len(speech_segments),
        "main_emotions": [{"emotion": e[0], "count": e[1]} for e in main_emotions],
        "average_intensity": total_intensity / len(speech_segments)
    }

def format_text_sentiment_analysis(text_snippets) -> dict:
    """格式化文本情感分析结果"""
    if not text_snippets:
        return {"total_snippets": 0, "sentiment_distribution": {}, "key_keywords": []}
    
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    all_keywords = []
    
    for snippet in text_snippets:
        sentiment_counts[snippet.sentiment_polarity.lower()] += 1
        if snippet.keywords:
            all_keywords.extend(snippet.keywords)
    
    keyword_counts = {}
    for keyword in all_keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    key_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_snippets": len(text_snippets),
        "sentiment_distribution": sentiment_counts,
        "key_keywords": [{"keyword": k[0], "count": k[1]} for k in key_keywords]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
