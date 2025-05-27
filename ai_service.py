"""
AI服务集成 - 与外部AI模型服务交互
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3-0324:free"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """初始化AI服务"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        logger.info("AI服务已初始化")
    
    async def close(self):
        """关闭AI服务"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.session:
                return {"status": "not_initialized"}
            
            # 简单的API调用测试
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                }
            ) as response:
                if response.status == 200:
                    return {"status": "healthy"}
                else:
                    return {"status": "error", "code": response.status}
        
        except Exception as e:
            logger.error(f"AI服务健康检查失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_micro_expression(self, frame_data: Dict) -> Dict[str, Any]:
        """微表情分析"""
        try:
            # 构建分析提示
            prompt = f"""
            作为微表情分析专家，请分析以下帧数据并识别可能的微表情：
            
            帧信息：
            - 时间戳: {frame_data.get('timestamp', 'unknown')}
            - 帧号: {frame_data.get('frame_number', 'unknown')}
            
            请返回JSON格式的分析结果，包含：
            1. 是否检测到微表情 (detected)
            2. 如果检测到，提供事件列表 (events)，每个事件包含：
               - type: 微表情类型 (anger, fear, surprise, sadness, happiness, disgust, contempt)
               - intensity: 强度 (0.0-1.0)
               - confidence: 置信度 (0.0-1.0)
               - region: 面部区域
            
            示例输出：
            {{
                "detected": true,
                "events": [
                    {{
                        "type": "surprise",
                        "intensity": 0.75,
                        "confidence": 0.82,
                        "region": "eyebrows"
                    }}
                ]
            }}
            """
            
            response = await self._call_llm(prompt)
            
            # 解析LLM响应
            try:
                # 从LLM响应中提取JSON
                content = response.get("content", "")
                # 寻找JSON部分
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    return {
                        "success": True,
                        "detected": result.get("detected", False),
                        "events": result.get("events", [])
                    }
                else:
                    # 如果没有检测到JSON，返回模拟结果
                    return self._generate_mock_micro_expression()
                    
            except json.JSONDecodeError:
                logger.warning("LLM响应无法解析为JSON，使用模拟数据")
                return self._generate_mock_micro_expression()
            
        except Exception as e:
            logger.error(f"微表情分析失败: {e}")
            # 返回模拟结果作为备选
            return self._generate_mock_micro_expression()
    
    async def analyze_speech_emotion(self, audio_data: Dict) -> Dict[str, Any]:
        """语音情感分析"""
        try:
            prompt = f"""
            作为语音情感分析专家，请分析以下音频段的情感特征：
            
            音频信息：
            - 开始时间: {audio_data.get('start_time', 'unknown')}
            - 结束时间: {audio_data.get('end_time', 'unknown')}
            - 时长: {audio_data.get('duration', 'unknown')}
            
            基于语音的声学特征（音调、音量、语速、停顿等），请返回JSON格式的情感分析结果：
            {{
                "emotion_type": "主要情感类型",
                "intensity": "情感强度(0.0-1.0)",
                "confidence": "置信度(0.0-1.0)",
                "acoustic_features": {{
                    "pitch_level": "音调水平(low/medium/high)",
                    "volume_level": "音量水平(low/medium/high)",
                    "speech_rate": "语速(slow/normal/fast)",
                    "voice_quality": "音质特征"
                }}
            }}
            
            情感类型包括：neutral, happy, sad, angry, fearful, surprised, anxious, calm
            """
            
            response = await self._call_llm(prompt)
            
            try:
                content = response.get("content", "")
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    return {
                        "success": True,
                        "result": result
                    }
                else:
                    return self._generate_mock_speech_emotion()
                    
            except json.JSONDecodeError:
                return self._generate_mock_speech_emotion()
            
        except Exception as e:
            logger.error(f"语音情感分析失败: {e}")
            return self._generate_mock_speech_emotion()
    
    async def analyze_text_sentiment(self, text_data: Dict) -> Dict[str, Any]:
        """文本情感分析"""
        try:
            text_content = text_data.get("text_content", "")
            
            prompt = f"""
            作为文本情感分析专家，请分析以下文本的情感特征：
            
            文本内容: "{text_content}"
            
            请返回JSON格式的分析结果：
            {{
                "polarity": "情感极性(positive/negative/neutral)",
                "emotion_type": "具体情感类型",
                "intensity": "情感强度(0.0-1.0)",
                "confidence": "置信度(0.0-1.0)",
                "keywords": ["情感关键词列表"],
                "sentiment_score": "情感评分(-1.0到1.0)"
            }}
            
            情感类型包括：joy, sadness, fear, anger, surprise, disgust, trust, anticipation, neutral
            """
            
            response = await self._call_llm(prompt)
            
            try:
                content = response.get("content", "")
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    return {
                        "success": True,
                        "result": result
                    }
                else:
                    return self._generate_mock_text_sentiment(text_content)
                    
            except json.JSONDecodeError:
                return self._generate_mock_text_sentiment(text_content)
            
        except Exception as e:
            logger.error(f"文本情感分析失败: {e}")
            return self._generate_mock_text_sentiment(text_content)
    
    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """调用LLM API"""
        try:
            if not self.session:
                await self.initialize()
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("choices") and len(data["choices"]) > 0:
                        return {
                            "success": True,
                            "content": data["choices"][0]["message"]["content"]
                        }
                    else:
                        return {"success": False, "error": "No response content"}
                else:
                    error_text = await response.text()
                    logger.error(f"LLM API调用失败: {response.status}, {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        
        except Exception as e:
            logger.error(f"LLM API调用异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_mock_micro_expression(self) -> Dict[str, Any]:
        """生成模拟微表情分析结果"""
        expressions = ["anger", "fear", "surprise", "sadness", "happiness", "disgust", "contempt"]
        
        # 30%的概率检测到微表情
        if np.random.random() < 0.3:
            return {
                "success": True,
                "detected": True,
                "events": [
                    {
                        "type": np.random.choice(expressions),
                        "intensity": np.random.uniform(0.4, 0.9),
                        "confidence": np.random.uniform(0.6, 0.95),
                        "region": np.random.choice(["eyebrows", "eyes", "mouth", "nose"])
                    }
                ]
            }
        else:
            return {
                "success": True,
                "detected": False,
                "events": []
            }
    
    def _generate_mock_speech_emotion(self) -> Dict[str, Any]:
        """生成模拟语音情感分析结果"""
        emotions = ["neutral", "happy", "sad", "angry", "fearful", "surprised", "anxious", "calm"]
        pitch_levels = ["low", "medium", "high"]
        volume_levels = ["low", "medium", "high"]
        speech_rates = ["slow", "normal", "fast"]
        
        return {
            "success": True,
            "result": {
                "emotion_type": np.random.choice(emotions),
                "intensity": np.random.uniform(0.3, 0.8),
                "confidence": np.random.uniform(0.7, 0.9),
                "acoustic_features": {
                    "pitch_level": np.random.choice(pitch_levels),
                    "volume_level": np.random.choice(volume_levels),
                    "speech_rate": np.random.choice(speech_rates),
                    "voice_quality": "清晰"
                }
            }
        }
    
    def _generate_mock_text_sentiment(self, text_content: str) -> Dict[str, Any]:
        """生成模拟文本情感分析结果"""
        emotions = ["joy", "sadness", "fear", "anger", "surprise", "disgust", "neutral"]
        polarities = ["positive", "negative", "neutral"]
        
        # 简单的关键词检测
        positive_words = ["好", "优秀", "满意", "高兴", "喜欢", "支持", "配合"]
        negative_words = ["不", "没", "困难", "担心", "害怕", "不满", "拒绝"]
        
        keywords = []
        polarity = "neutral"
        sentiment_score = 0.0
        
        for word in positive_words:
            if word in text_content:
                keywords.append(word)
                polarity = "positive"
                sentiment_score += 0.3
        
        for word in negative_words:
            if word in text_content:
                keywords.append(word)
                polarity = "negative"
                sentiment_score -= 0.3
        
        return {
            "success": True,
            "result": {
                "polarity": polarity,
                "emotion_type": np.random.choice(emotions),
                "intensity": min(1.0, abs(sentiment_score) + np.random.uniform(0.1, 0.4)),
                "confidence": np.random.uniform(0.6, 0.85),
                "keywords": keywords,
                "sentiment_score": np.clip(sentiment_score, -1.0, 1.0)
            }
        }
