"""
分析引擎 - 协调多模态分析流程
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import numpy as np

from models import (
    AnalysisSession, FacialExpressionEvent, SpeechEmotionSegment,
    TextSentimentSnippet, FusedEmotionState, PsychologicalAssessment, SystemAlert
)
from ai_service import AIService

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.ai_service = AIService()
    
    async def process_analysis_task(self, session_id: str, file_paths: List[str], db):
        """处理分析任务的主流程"""
        logger.info(f"开始处理分析任务: {session_id}")
        
        try:
            # 更新会话状态
            await self.update_session_status(session_id, "processing", db)
            
            # 1. 数据预处理
            processed_data = await self.preprocess_data(session_id, file_paths)
            
            # 2. 多模态分析
            await self.update_session_status(session_id, "analyzing", db)
            analysis_results = await self.analyze_modalities(session_id, processed_data, db)
            
            # 3. 多模态融合
            await self.update_session_status(session_id, "fusing", db)
            fused_results = await self.fuse_analysis_results(session_id, analysis_results, db)
            
            # 4. 心理状态评估
            await self.update_session_status(session_id, "assessing", db)
            psychological_assessments = await self.assess_psychological_state(session_id, fused_results, db)
            
            # 5. 风险识别和预警
            await self.identify_risks_and_alerts(session_id, psychological_assessments, db)
            
            # 6. 完成分析
            await self.update_session_status(session_id, "completed", db)
            
            logger.info(f"分析任务完成: {session_id}")
            
        except Exception as e:
            logger.error(f"分析任务失败: {session_id}, 错误: {e}")
            await self.update_session_status(session_id, "failed", db, str(e))
            raise
    
    async def update_session_status(self, session_id: str, status: str, db, error_message: str = None):
        """更新会话状态"""
        session = db.query(AnalysisSession).filter(AnalysisSession.session_id == session_id).first()
        if session:
            session.status = status
            if status == "completed" or status == "failed":
                session.end_time = datetime.now()
            if error_message:
                session.error_message = error_message
            db.commit()
    
    async def preprocess_data(self, session_id: str, file_paths: List[str]) -> Dict[str, Any]:
        """数据预处理"""
        logger.info(f"开始数据预处理: {session_id}")
        
        processed_data = {
            "video_frames": [],
            "audio_segments": [],
            "text_snippets": []
        }
        
        for file_path in file_paths:
            if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                # 处理视频文件
                video_data = await self.process_video_file(file_path)
                processed_data["video_frames"].extend(video_data)
                
            elif file_path.lower().endswith(('.wav', '.mp3', '.aac')):
                # 处理音频文件
                audio_data = await self.process_audio_file(file_path)
                processed_data["audio_segments"].extend(audio_data)
                
            elif file_path.lower().endswith(('.txt', '.docx')):
                # 处理文本文件
                text_data = await self.process_text_file(file_path)
                processed_data["text_snippets"].extend(text_data)
        
        logger.info(f"数据预处理完成: {session_id}")
        return processed_data
    
    async def process_video_file(self, file_path: str) -> List[Dict]:
        """处理视频文件，提取帧"""
        # 这里实现视频帧提取逻辑
        # 使用OpenCV或类似库
        frames = []
        
        # 模拟提取的帧数据
        for i in range(10):  # 模拟10帧
            frame_data = {
                "timestamp": datetime.now() + timedelta(seconds=i),
                "frame_number": i,
                "frame_data": f"frame_{i}_data"  # 实际应该是图像数据
            }
            frames.append(frame_data)
        
        return frames
    
    async def process_audio_file(self, file_path: str) -> List[Dict]:
        """处理音频文件，分段"""
        # 这里实现音频分段逻辑
        # 使用librosa或类似库
        segments = []
        
        # 模拟音频分段数据
        for i in range(5):  # 模拟5个音频段
            segment_data = {
                "start_time": datetime.now() + timedelta(seconds=i*10),
                "end_time": datetime.now() + timedelta(seconds=(i+1)*10),
                "audio_data": f"audio_segment_{i}"  # 实际应该是音频特征
            }
            segments.append(segment_data)
        
        return segments
    
    async def process_text_file(self, file_path: str) -> List[Dict]:
        """处理文本文件，分句"""
        # 这里实现文本分句逻辑
        snippets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单分句（实际应该使用更复杂的NLP处理）
            sentences = content.split('。')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    snippet_data = {
                        "timestamp": datetime.now() + timedelta(seconds=i*5),
                        "text_content": sentence.strip(),
                        "sequence": i
                    }
                    snippets.append(snippet_data)
        except Exception as e:
            logger.error(f"处理文本文件失败: {file_path}, 错误: {e}")
        
        return snippets
    
    async def analyze_modalities(self, session_id: str, processed_data: Dict, db) -> Dict[str, List]:
        """多模态分析"""
        logger.info(f"开始多模态分析: {session_id}")
        
        # 并行执行多模态分析
        tasks = []
        
        if processed_data.get("video_frames"):
            tasks.append(self.analyze_video_modality(session_id, processed_data["video_frames"], db))
        
        if processed_data.get("audio_segments"):
            tasks.append(self.analyze_audio_modality(session_id, processed_data["audio_segments"], db))
        
        if processed_data.get("text_snippets"):
            tasks.append(self.analyze_text_modality(session_id, processed_data["text_snippets"], db))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        analysis_results = {
            "micro_expressions": [],
            "speech_emotions": [],
            "text_sentiments": []
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"模态分析失败: {result}")
                continue
            
            if i == 0 and processed_data.get("video_frames"):
                analysis_results["micro_expressions"] = result
            elif i == 1 and processed_data.get("audio_segments"):
                analysis_results["speech_emotions"] = result
            elif i == 2 and processed_data.get("text_snippets"):
                analysis_results["text_sentiments"] = result
        
        logger.info(f"多模态分析完成: {session_id}")
        return analysis_results
    
    async def analyze_video_modality(self, session_id: str, video_frames: List[Dict], db) -> List:
        """分析视频模态（微表情）"""
        logger.info(f"开始微表情分析: {session_id}")
        
        micro_expressions = []
        
        for frame_data in video_frames:
            try:
                # 调用AI服务进行微表情分析
                ai_result = await self.ai_service.analyze_micro_expression(frame_data)
                
                if ai_result.get("success") and ai_result.get("events"):
                    for event in ai_result["events"]:
                        micro_expr = FacialExpressionEvent(
                            session_id=session_id,
                            timestamp=frame_data["timestamp"],
                            type=event.get("type", "unknown"),
                            intensity=event.get("intensity", 0.0),
                            confidence=event.get("confidence", 0.0),
                            frame_number=frame_data.get("frame_number")
                        )
                        db.add(micro_expr)
                        micro_expressions.append(micro_expr)
                
            except Exception as e:
                logger.error(f"微表情分析失败: {e}")
                continue
        
        db.commit()
        logger.info(f"微表情分析完成: {session_id}, 检测到 {len(micro_expressions)} 个事件")
        return micro_expressions
    
    async def analyze_audio_modality(self, session_id: str, audio_segments: List[Dict], db) -> List:
        """分析音频模态（语音情感）"""
        logger.info(f"开始语音情感分析: {session_id}")
        
        speech_emotions = []
        
        for segment_data in audio_segments:
            try:
                # 调用AI服务进行语音情感分析
                ai_result = await self.ai_service.analyze_speech_emotion(segment_data)
                
                if ai_result.get("success"):
                    result = ai_result.get("result", {})
                    speech_emotion = SpeechEmotionSegment(
                        session_id=session_id,
                        start_time=segment_data["start_time"],
                        end_time=segment_data["end_time"],
                        emotion_type=result.get("emotion_type", "neutral"),
                        intensity=result.get("intensity", 0.0),
                        confidence=result.get("confidence", 0.0),
                        acoustic_features=result.get("acoustic_features")
                    )
                    db.add(speech_emotion)
                    speech_emotions.append(speech_emotion)
                
            except Exception as e:
                logger.error(f"语音情感分析失败: {e}")
                continue
        
        db.commit()
        logger.info(f"语音情感分析完成: {session_id}, 分析了 {len(speech_emotions)} 个片段")
        return speech_emotions
    
    async def analyze_text_modality(self, session_id: str, text_snippets: List[Dict], db) -> List:
        """分析文本模态（情感）"""
        logger.info(f"开始文本情感分析: {session_id}")
        
        text_sentiments = []
        
        for snippet_data in text_snippets:
            try:
                # 调用AI服务进行文本情感分析
                ai_result = await self.ai_service.analyze_text_sentiment(snippet_data)
                
                if ai_result.get("success"):
                    result = ai_result.get("result", {})
                    text_sentiment = TextSentimentSnippet(
                        session_id=session_id,
                        timestamp=snippet_data["timestamp"],
                        text_content=snippet_data["text_content"],
                        sentiment_polarity=result.get("polarity", "neutral"),
                        emotion_type=result.get("emotion_type"),
                        intensity=result.get("intensity", 0.0),
                        confidence=result.get("confidence", 0.0),
                        keywords=result.get("keywords", [])
                    )
                    db.add(text_sentiment)
                    text_sentiments.append(text_sentiment)
                
            except Exception as e:
                logger.error(f"文本情感分析失败: {e}")
                continue
        
        db.commit()
        logger.info(f"文本情感分析完成: {session_id}, 分析了 {len(text_sentiments)} 个片段")
        return text_sentiments
    
    async def fuse_analysis_results(self, session_id: str, analysis_results: Dict, db) -> List:
        """融合分析结果"""
        logger.info(f"开始多模态融合: {session_id}")
        
        # 获取时间对齐的数据
        aligned_data = self.align_modality_results_by_time(analysis_results)
        
        fused_states = []
        
        for timestamp, modality_data in aligned_data:
            try:
                # 执行融合算法
                fused_vector = self.calculate_fusion(modality_data)
                
                fused_state = FusedEmotionState(
                    session_id=session_id,
                    timestamp=timestamp,
                    fused_emotion_vector=fused_vector,
                    activation_level=fused_vector.get("activation", 0.0),
                    valence_level=fused_vector.get("valence", 0.0)
                )
                db.add(fused_state)
                fused_states.append(fused_state)
                
            except Exception as e:
                logger.error(f"融合计算失败: {e}")
                continue
        
        db.commit()
        logger.info(f"多模态融合完成: {session_id}, 生成 {len(fused_states)} 个融合状态")
        return fused_states
    
    def align_modality_results_by_time(self, analysis_results: Dict) -> List:
        """按时间对齐多模态结果"""
        timeline = {}
        
        # 处理微表情事件
        for expr in analysis_results.get("micro_expressions", []):
            timestamp = expr.timestamp
            if timestamp not in timeline:
                timeline[timestamp] = {}
            timeline[timestamp]["micro_expression"] = {
                "type": expr.type,
                "intensity": expr.intensity,
                "confidence": expr.confidence
            }
        
        # 处理语音情感
        for emotion in analysis_results.get("speech_emotions", []):
            timestamp = emotion.start_time  # 使用开始时间
            if timestamp not in timeline:
                timeline[timestamp] = {}
            timeline[timestamp]["speech_emotion"] = {
                "emotion_type": emotion.emotion_type,
                "intensity": emotion.intensity,
                "confidence": emotion.confidence
            }
        
        # 处理文本情感
        for sentiment in analysis_results.get("text_sentiments", []):
            timestamp = sentiment.timestamp
            if timestamp not in timeline:
                timeline[timestamp] = {}
            timeline[timestamp]["text_sentiment"] = {
                "polarity": sentiment.sentiment_polarity,
                "intensity": sentiment.intensity,
                "confidence": sentiment.confidence
            }
        
        # 按时间排序返回
        sorted_timeline = sorted(timeline.items())
        return sorted_timeline
    
    def calculate_fusion(self, modality_data: Dict) -> Dict:
        """计算融合向量"""
        # 简化的融合算法
        weights = {
            "micro_expression": 0.4,
            "speech_emotion": 0.3,
            "text_sentiment": 0.3
        }
        
        activation = 0.0
        valence = 0.0
        total_weight = 0.0
        
        # 从微表情计算激活度和效价
        if "micro_expression" in modality_data:
            micro_data = modality_data["micro_expression"]
            intensity = micro_data["intensity"]
            confidence = micro_data["confidence"]
            weight = weights["micro_expression"] * confidence
            
            # 映射微表情类型到激活度和效价
            expr_mappings = {
                "anger": {"activation": 0.8, "valence": -0.7},
                "fear": {"activation": 0.9, "valence": -0.8},
                "surprise": {"activation": 0.7, "valence": 0.1},
                "sadness": {"activation": 0.3, "valence": -0.6},
                "happiness": {"activation": 0.6, "valence": 0.8},
                "disgust": {"activation": 0.5, "valence": -0.6},
                "neutral": {"activation": 0.0, "valence": 0.0}
            }
            
            mapping = expr_mappings.get(micro_data["type"].lower(), {"activation": 0.0, "valence": 0.0})
            activation += mapping["activation"] * intensity * weight
            valence += mapping["valence"] * intensity * weight
            total_weight += weight
        
        # 从语音情感计算
        if "speech_emotion" in modality_data:
            speech_data = modality_data["speech_emotion"]
            intensity = speech_data["intensity"]
            confidence = speech_data["confidence"]
            weight = weights["speech_emotion"] * confidence
            
            # 映射语音情感到激活度和效价
            emotion_mappings = {
                "angry": {"activation": 0.8, "valence": -0.7},
                "anxious": {"activation": 0.7, "valence": -0.5},
                "calm": {"activation": 0.2, "valence": 0.3},
                "excited": {"activation": 0.9, "valence": 0.6},
                "neutral": {"activation": 0.0, "valence": 0.0}
            }
            
            mapping = emotion_mappings.get(speech_data["emotion_type"].lower(), {"activation": 0.0, "valence": 0.0})
            activation += mapping["activation"] * intensity * weight
            valence += mapping["valence"] * intensity * weight
            total_weight += weight
        
        # 从文本情感计算
        if "text_sentiment" in modality_data:
            text_data = modality_data["text_sentiment"]
            intensity = text_data["intensity"]
            confidence = text_data["confidence"]
            weight = weights["text_sentiment"] * confidence
            
            # 映射文本极性到激活度和效价
            polarity_mappings = {
                "positive": {"activation": 0.4, "valence": 0.6},
                "negative": {"activation": 0.6, "valence": -0.6},
                "neutral": {"activation": 0.0, "valence": 0.0}
            }
            
            mapping = polarity_mappings.get(text_data["polarity"].lower(), {"activation": 0.0, "valence": 0.0})
            activation += mapping["activation"] * intensity * weight
            valence += mapping["valence"] * intensity * weight
            total_weight += weight
        
        # 归一化
        if total_weight > 0:
            activation /= total_weight
            valence /= total_weight
        
        return {
            "activation": activation,
            "valence": valence,
            "total_weight": total_weight,
            "modalities_count": len(modality_data)
        }
    
    async def assess_psychological_state(self, session_id: str, fused_states: List, db) -> List:
        """心理状态评估"""
        logger.info(f"开始心理状态评估: {session_id}")
        
        assessments = []
        
        for fused_state in fused_states:
            try:
                # 计算心理维度
                psych_state = self.calculate_psychological_dimensions(fused_state)
                
                # 生成雷达图数据
                radar_data = self.generate_radar_data(psych_state)
                
                # 识别风险
                risks = self.identify_risks(psych_state, assessments)
                
                # 生成建议
                suggestions = self.generate_suggestions(psych_state, risks)
                
                assessment = PsychologicalAssessment(
                    session_id=session_id,
                    timestamp=fused_state.timestamp,
                    psychological_state_vector=psych_state,
                    radar_data_points=radar_data,
                    overall_emotion_intensity=self.calculate_overall_intensity(psych_state),
                    identified_risks=risks,
                    intervention_suggestions=suggestions,
                    risk_level=self.calculate_risk_level(risks)
                )
                db.add(assessment)
                assessments.append(assessment)
                
            except Exception as e:
                logger.error(f"心理状态评估失败: {e}")
                continue
        
        db.commit()
        logger.info(f"心理状态评估完成: {session_id}, 生成 {len(assessments)} 个评估")
        return assessments
    
    def calculate_psychological_dimensions(self, fused_state) -> Dict:
        """计算心理维度"""
        activation = fused_state.activation_level or 0
        valence = fused_state.valence_level or 0
        
        # 计算各个心理维度
        tension = max(0, min(100, activation * 60 + abs(valence) * 40))
        anxiety = max(0, min(100, activation * 70 - valence * 30))
        cooperation = max(0, min(100, 50 + valence * 50 - activation * 20))
        calmness = max(0, min(100, 80 - activation * 80))
        defensiveness = max(0, min(100, activation * 50 - valence * 30))
        credibility = max(0, min(100, 70 + valence * 20 - abs(activation - 0.5) * 40))
        
        return {
            "tension": tension,
            "anxiety": anxiety,
            "cooperation": cooperation,
            "calmness": calmness,
            "defensiveness": defensiveness,
            "credibility": credibility,
            "activation": activation,
            "valence": valence
        }
    
    def generate_radar_data(self, psych_state: Dict) -> Dict:
        """生成雷达图数据"""
        return {
            "紧张度": psych_state["tension"],
            "焦虑度": psych_state["anxiety"],
            "合作意愿": psych_state["cooperation"],
            "冷静度": psych_state["calmness"],
            "防御程度": psych_state["defensiveness"],
            "可信度": psych_state["credibility"]
        }
    
    def identify_risks(self, psych_state: Dict, recent_assessments: List) -> List[Dict]:
        """识别风险"""
        risks = []
        
        # 规则1：高焦虑风险
        if psych_state["anxiety"] > 80:
            risks.append({
                "type": "高焦虑风险",
                "level": "high",
                "evidence": f"焦虑度达到{psych_state['anxiety']:.1f}，超过危险阈值",
                "timestamp": datetime.now().isoformat()
            })
        
        # 规则2：低合作意愿
        if psych_state["cooperation"] < 30:
            risks.append({
                "type": "合作意愿低",
                "level": "medium",
                "evidence": f"合作意愿仅{psych_state['cooperation']:.1f}，可能存在抵触情绪",
                "timestamp": datetime.now().isoformat()
            })
        
        # 规则3：高防御程度
        if psych_state["defensiveness"] > 70:
            risks.append({
                "type": "防御心理强",
                "level": "medium",
                "evidence": f"防御程度达到{psych_state['defensiveness']:.1f}，可能隐瞒信息",
                "timestamp": datetime.now().isoformat()
            })
        
        # 规则4：情感剧烈波动（需要历史数据）
        if len(recent_assessments) > 1:
            prev_assessment = recent_assessments[-2]
            if prev_assessment.psychological_state_vector:
                prev_tension = prev_assessment.psychological_state_vector.get("tension", 0)
                tension_change = abs(psych_state["tension"] - prev_tension)
                if tension_change > 30:
                    risks.append({
                        "type": "情感剧烈波动",
                        "level": "high",
                        "evidence": f"紧张度在短时间内变化{tension_change:.1f}分",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return risks
    
    def generate_suggestions(self, psych_state: Dict, risks: List[Dict]) -> List[str]:
        """生成干预建议"""
        suggestions = []
        
        # 基于心理状态的建议
        if psych_state["anxiety"] > 70:
            suggestions.append("建议语气温和，避免施压")
            suggestions.append("可适当提供休息时间")
        
        if psych_state["cooperation"] < 40:
            suggestions.append("尝试建立信任关系")
            suggestions.append("避免对抗性提问方式")
        
        if psych_state["tension"] > 80:
            suggestions.append("注意缓解当事人紧张情绪")
            suggestions.append("可暂停敏感话题讨论")
        
        # 基于风险的建议
        for risk in risks:
            if risk["type"] == "高焦虑风险":
                suggestions.append("建议安排心理专家介入")
            elif risk["type"] == "防御心理强":
                suggestions.append("重新审视提问策略，减少防御触发")
            elif risk["type"] == "情感剧烈波动":
                suggestions.append("密切关注情绪状态，准备应急措施")
        
        return list(set(suggestions))  # 去重
    
    def calculate_overall_intensity(self, psych_state: Dict) -> float:
        """计算总体情感强度"""
        # 综合各维度计算总体强度
        weights = {
            "tension": 0.3,
            "anxiety": 0.25,
            "defensiveness": 0.2,
            "cooperation": -0.15,  # 负权重，合作意愿高时强度较低
            "calmness": -0.1       # 负权重，冷静时强度较低
        }
        
        intensity = sum(psych_state[dim] * weight for dim, weight in weights.items())
        return max(0, min(100, intensity))
    
    def calculate_risk_level(self, risks: List[Dict]) -> str:
        """计算风险等级"""
        if not risks:
            return "low"
        
        high_risks = [r for r in risks if r["level"] == "high"]
        medium_risks = [r for r in risks if r["level"] == "medium"]
        
        if len(high_risks) >= 2 or len(high_risks) >= 1 and len(medium_risks) >= 2:
            return "critical"
        elif len(high_risks) >= 1 or len(medium_risks) >= 3:
            return "high"
        elif len(medium_risks) >= 1:
            return "medium"
        else:
            return "low"
    
    async def identify_risks_and_alerts(self, session_id: str, assessments: List, db):
        """识别风险并发送预警"""
        logger.info(f"开始风险识别和预警: {session_id}")
        
        latest_assessment = assessments[-1] if assessments else None
        if not latest_assessment or not latest_assessment.identified_risks:
            return
        
        # 为每个风险创建预警
        for risk in latest_assessment.identified_risks:
            alert = SystemAlert(
                session_id=session_id,
                alert_type=risk["type"],
                severity=risk["level"],
                title=f'检测到{risk["type"]}',
                description=risk["evidence"],
                status="active"
            )
            db.add(alert)
        
        db.commit()
        logger.info(f"风险识别和预警完成: {session_id}")
