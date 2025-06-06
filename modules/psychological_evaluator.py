import numpy as np
from sklearn.preprocessing import MinMaxScaler


class PsychologicalEvaluator:
    def __init__(self):
        self.scaler = MinMaxScaler()

        # 心理状态维度
        self.psychological_dimensions = [
            'emotional_stability',  # 情绪稳定性
            'stress_level',  # 压力水平
            'anxiety_level',  # 焦虑水平
            'depression_risk',  # 抑郁风险
            'cognitive_clarity',  # 认知清晰度
            'social_adaptability',  # 社会适应性
            'self_control',  # 自我控制
            'resilience'  # 心理韧性
        ]

    def integrate_multimodal_data(self, face_data, voice_data, text_data):
        """整合多模态数据"""
        integrated = {
            'overall_intensity': 0,
            'emotional_profile': {},
            'behavioral_indicators': {},
            'cognitive_patterns': {}
        }

        # 整合面部数据
        if face_data:
            face_intensity = face_data.get('intensity', 0)
            face_emotions = face_data.get('data', {}).get('emotions', {})
            integrated['overall_intensity'] += face_intensity * 0.3

            # 合并情绪数据
            for emotion, value in face_emotions.items():
                integrated['emotional_profile'][f'face_{emotion}'] = value

        # 整合语音数据
        if voice_data:
            voice_intensity = voice_data.get('intensity', 0)
            voice_metrics = voice_data.get('data', {})
            integrated['overall_intensity'] += voice_intensity * 0.3

            # 添加行为指标
            integrated['behavioral_indicators']['voice_pitch'] = voice_metrics.get('pitch', {})
            integrated['behavioral_indicators']['voice_volume'] = voice_metrics.get('volume', {})
            integrated['behavioral_indicators']['voice_speed'] = voice_metrics.get('speed', {})

        # 整合文本数据
        if text_data:
            text_vector = text_data.get('data', {}).get('emotion_vector', [])
            semantic_analysis = text_data.get('data', {}).get('semantic_analysis', {})

            integrated['overall_intensity'] += np.mean(np.abs(text_vector)) * 40

            # 添加认知模式
            integrated['cognitive_patterns'] = {
                'consistency': semantic_analysis.get('consistency', 0),
                'complexity': len(semantic_analysis.get('sentences', [])),
                'emotional_valence': text_vector[0] if len(text_vector) > 0 else 0
            }

        return integrated

    def build_psychological_radar(self, integrated_data):
        """构建心理状态雷达图"""
        radar_data = {}

        # 计算每个维度的值
        emotions = integrated_data.get('emotional_profile', {})
        behaviors = integrated_data.get('behavioral_indicators', {})
        cognitions = integrated_data.get('cognitive_patterns', {})

        # 情绪稳定性
        emotion_variance = np.var(list(emotions.values())) if emotions else 0
        radar_data['emotional_stability'] = 1 - min(1, emotion_variance)

        # 压力水平
        stress_indicators = [
            behaviors.get('voice_pitch', {}).get('intensity', 0),
            behaviors.get('voice_speed', {}).get('intensity', 0)
        ]
        radar_data['stress_level'] = np.mean(stress_indicators)

        # 焦虑水平
        anxiety_emotions = ['fear', 'fearful', 'nervous']
        anxiety_scores = [emotions.get(f'face_{e}', 0) for e in anxiety_emotions]
        radar_data['anxiety_level'] = np.mean(anxiety_scores) if anxiety_scores else 0

        # 抑郁风险
        depression_emotions = ['sad', 'sadness']
        depression_scores = [emotions.get(f'face_{e}', 0) for e in depression_emotions]
        radar_data['depression_risk'] = np.mean(depression_scores) if depression_scores else 0

        # 认知清晰度
        radar_data['cognitive_clarity'] = cognitions.get('consistency', 0.5)

        # 社会适应性
        positive_emotions = ['happy', 'calm', 'neutral']
        positive_scores = [emotions.get(f'face_{e}', 0) for e in positive_emotions]
        radar_data['social_adaptability'] = np.mean(positive_scores) if positive_scores else 0.5

        # 自我控制
        radar_data['self_control'] = 1 - radar_data['stress_level']

        # 心理韧性
        radar_data['resilience'] = (
                radar_data['emotional_stability'] * 0.4 +
                radar_data['cognitive_clarity'] * 0.3 +
                (1 - radar_data['depression_risk']) * 0.3
        )

        # 归一化到0-100
        for key in radar_data:
            radar_data[key] = min(100, max(0, radar_data[key] * 100))

        return radar_data

    def generate_interventions(self, psychological_risks, communication_barriers):
        """生成干预建议"""
        interventions = {
            'immediate': [],  # 即时干预
            'short_term': [],  # 短期建议
            'long_term': [],  # 长期建议
            'resources': []  # 资源推荐
        }

        # 基于风险等级生成建议
        for risk in psychological_risks:
            if risk['level'] == 'high':
                interventions['immediate'].append({
                    'type': risk['type'],
                    'action': self._get_immediate_action(risk['type']),
                    'priority': 'high'
                })

            elif risk['level'] == 'medium':
                interventions['short_term'].append({
                    'type': risk['type'],
                    'action': self._get_short_term_action(risk['type']),
                    'priority': 'medium'
                })

        # 基于沟通障碍生成建议
        for barrier in communication_barriers:
            interventions['short_term'].append({
                'type': 'communication',
                'action': self._get_communication_suggestion(barrier),
                'priority': 'medium'
            })

        # 添加通用建议
        interventions['long_term'] = [
            {
                'action': '建立定期心理健康检查机制',
                'frequency': '每月一次',
                'priority': 'low'
            },
            {
                'action': '参加压力管理培训课程',
                'frequency': '每季度一次',
                'priority': 'low'
            }
        ]

        # 推荐资源
        interventions['resources'] = [
            {
                'type': 'hotline',
                'name': '心理援助热线',
                'contact': '12355',
                'availability': '24/7'
            },
            {
                'type': 'app',
                'name': '冥想放松APP',
                'recommendation': '每日使用15分钟'
            }
        ]

        return interventions

    def _get_immediate_action(self, risk_type):
        """获取即时干预措施"""
        actions = {
            'severe_anxiety': '立即安排心理咨询师介入，提供情绪稳定技术指导',
            'acute_stress': '引导进行深呼吸练习，转移到安静环境',
            'emotional_breakdown': '提供情绪支持，确保人身安全，联系紧急心理干预团队',
            'communication_crisis': '暂停当前对话，引入中立调解员'
        }
        return actions.get(risk_type, '提供基础心理支持')

    def _get_short_term_action(self, risk_type):
        """获取短期干预建议"""
        actions = {
            'moderate_anxiety': '安排3-5次认知行为治疗课程',
            'chronic_stress': '制定压力管理计划，学习放松技巧',
            'mild_depression': '建议进行心理评估，考虑支持性心理治疗',
            'social_withdrawal': '参加小组活动，逐步恢复社交功能'
        }
        return actions.get(risk_type, '定期心理健康监测')

    def _get_communication_suggestion(self, barrier):
        """获取沟通改善建议"""
        suggestions = {
            'emotional_blocking': '使用情感反映技术，建立情感连接',
            'defensive_attitude': '采用非暴力沟通方式，降低防御性',
            'expression_difficulty': '提供表达辅助工具，鼓励多样化表达方式',
            'trust_issues': '建立渐进式信任关系，保持透明沟通'
        }
        return suggestions.get(barrier['type'], '改善沟通技巧培训')
