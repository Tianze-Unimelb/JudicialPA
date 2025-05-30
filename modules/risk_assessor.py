import numpy as np
from datetime import datetime


class RiskAssessor:
    def __init__(self):
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.95
        }

        self.psychological_indicators = {
            'anxiety': ['fear', 'nervous', 'worried', 'tense'],
            'depression': ['sad', 'hopeless', 'empty', 'worthless'],
            'anger': ['angry', 'frustrated', 'irritated', 'hostile'],
            'trauma': ['flashback', 'nightmare', 'avoidance', 'hypervigilance']
        }

    def identify_psychological_risks(self, integrated_data):
        """识别心理风险"""
        risks = []

        # 分析情绪模式
        emotional_profile = integrated_data.get('emotional_profile', {})

        # 检查各类心理风险
        for risk_type, indicators in self.psychological_indicators.items():
            risk_score = self._calculate_risk_score(emotional_profile, indicators)

            if risk_score > self.risk_thresholds['low']:
                risk_level = self._get_risk_level(risk_score)

                risks.append({
                    'type': risk_type,
                    'score': risk_score,
                    'level': risk_level,
                    'indicators': self._get_present_indicators(emotional_profile, indicators),
                    'timestamp': datetime.now().isoformat()
                })

        # 检查综合风险
        overall_risk = self._assess_overall_risk(integrated_data)
        if overall_risk['score'] > self.risk_thresholds['medium']:
            risks.append(overall_risk)

        # 检查急性风险
        acute_risks = self._identify_acute_risks(integrated_data)
        risks.extend(acute_risks)

        return sorted(risks, key=lambda x: x['score'], reverse=True)

    def assess_communication_barriers(self, integrated_data):
        """评估沟通障碍"""
        barriers = []

        # 分析语言模式
        cognitive_patterns = integrated_data.get('cognitive_patterns', {})
        behavioral_indicators = integrated_data.get('behavioral_indicators', {})

        # 检查表达困难
        expression_difficulty = self._assess_expression_difficulty(
            cognitive_patterns,
            behavioral_indicators
        )
        if expression_difficulty['present']:
            barriers.append(expression_difficulty)

        # 检查情绪阻滞
        emotional_blocking = self._assess_emotional_blocking(
            integrated_data.get('emotional_profile', {})
        )
        if emotional_blocking['present']:
            barriers.append(emotional_blocking)

        # 检查防御态度
        defensive_attitude = self._assess_defensive_attitude(
            behavioral_indicators,
            cognitive_patterns
        )
        if defensive_attitude['present']:
            barriers.append(defensive_attitude)

        # 检查信任问题
        trust_issues = self._assess_trust_issues(integrated_data)
        if trust_issues['present']:
            barriers.append(trust_issues)

        return barriers

    def _calculate_risk_score(self, emotional_profile, indicators):
        """计算风险分数"""
        scores = []

        for indicator in indicators:
            # 检查各种形式的指标
            for key, value in emotional_profile.items():
                if indicator in key.lower():
                    scores.append(value)

        return np.mean(scores) if scores else 0

    def _get_risk_level(self, score):
        """获取风险等级"""
        if score >= self.risk_thresholds['critical']:
            return 'critical'
        elif score >= self.risk_thresholds['high']:
            return 'high'
        elif score >= self.risk_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def _get_present_indicators(self, emotional_profile, indicators):
        """获取存在的指标"""
        present = []

        for indicator in indicators:
            for key, value in emotional_profile.items():
                if indicator in key.lower() and value > 0.3:
                    present.append({
                        'indicator': indicator,
                        'source': key,
                        'value': value
                    })

        return present

    def _assess_overall_risk(self, integrated_data):
        """评估综合风险"""
        overall_intensity = integrated_data.get('overall_intensity', 0)

        # 计算情绪不稳定性
        emotional_profile = integrated_data.get('emotional_profile', {})
        emotional_instability = np.std(list(emotional_profile.values())) if emotional_profile else 0

        # 计算认知混乱度
        cognitive_patterns = integrated_data.get('cognitive_patterns', {})
        cognitive_confusion = 1 - cognitive_patterns.get('consistency', 1)

        # 综合风险分数
        risk_score = (
                overall_intensity * 0.4 +
                emotional_instability * 0.3 +
                cognitive_confusion * 0.3
        )

        return {
            'type': 'overall_psychological_risk',
            'score': risk_score,
            'level': self._get_risk_level(risk_score),
            'components': {
                'intensity': overall_intensity,
                'instability': emotional_instability,
                'confusion': cognitive_confusion
            },
            'timestamp': datetime.now().isoformat()
        }

    def _identify_acute_risks(self, integrated_data):
        """识别急性风险"""
        acute_risks = []

        # 检查情绪强度峰值
        overall_intensity = integrated_data.get('overall_intensity', 0)
        if overall_intensity > 85:
            acute_risks.append({
                'type': 'emotional_crisis',
                'score': overall_intensity / 100,
                'level': 'high',
                'description': '情绪强度达到危险水平',
                'immediate_action_required': True,
                'timestamp': datetime.now().isoformat()
            })

        # 检查自伤/自杀风险指标
        emotional_profile = integrated_data.get('emotional_profile', {})
        despair_indicators = ['hopeless', 'worthless', 'empty']
        despair_score = self._calculate_risk_score(emotional_profile, despair_indicators)

        if despair_score > 0.7:
            acute_risks.append({
                'type': 'self_harm_risk',
                'score': despair_score,
                'level': 'critical',
                'description': '存在潜在自伤风险',
                'immediate_action_required': True,
                'timestamp': datetime.now().isoformat()
            })

        return acute_risks

    def _assess_expression_difficulty(self, cognitive_patterns, behavioral_indicators):
        """评估表达困难"""
        difficulty_score = 0

        # 检查语速异常
        voice_speed = behavioral_indicators.get('voice_speed', {})
        if voice_speed.get('type') in ['very_slow', 'very_fast']:
            difficulty_score += 0.3

        # 检查认知复杂度
        if cognitive_patterns.get('complexity', 0) < 3:  # 句子过少
            difficulty_score += 0.3

        # 检查一致性
        if cognitive_patterns.get('consistency', 1) < 0.5:
            difficulty_score += 0.4

        return {
            'type': 'expression_difficulty',
            'present': difficulty_score > 0.5,
            'severity': difficulty_score,
            'aspects': {
                'verbal_fluency': voice_speed.get('type', 'normal'),
                'cognitive_organization': cognitive_patterns.get('consistency', 1),
                'expression_complexity': cognitive_patterns.get('complexity', 0)
            }
        }

    def _assess_emotional_blocking(self, emotional_profile):
        """评估情绪阻滞"""
        # 检查情绪平淡
        emotion_values = list(emotional_profile.values())

        if not emotion_values:
            return {'type': 'emotional_blocking', 'present': False}

        # 计算情绪范围
        emotion_range = np.max(emotion_values) - np.min(emotion_values)

        # 检查是否过度中性
        neutral_score = emotional_profile.get('face_neutral', 0)

        blocking_present = emotion_range < 0.2 or neutral_score > 0.8

        return {
            'type': 'emotional_blocking',
            'present': blocking_present,
            'severity': 1 - emotion_range if blocking_present else 0,
            'characteristics': {
                'emotional_range': emotion_range,
                'neutrality': neutral_score,
                'flat_affect': emotion_range < 0.1
            }
        }

    def _assess_defensive_attitude(self, behavioral_indicators, cognitive_patterns):
        """评估防御态度"""
        defensiveness_score = 0

        # 检查声音指标
        voice_volume = behavioral_indicators.get('voice_volume', {})
        if voice_volume.get('level') == 'loud':
            defensiveness_score += 0.3

        voice_pitch = behavioral_indicators.get('voice_pitch', {})
        if voice_pitch.get('type') == 'high' and voice_pitch.get('variation', 0) > 0.5:
            defensiveness_score += 0.3

        # 检查认知模式
        emotional_valence = cognitive_patterns.get('emotional_valence', 0)
        if emotional_valence < -0.5:  # 负面情绪
            defensiveness_score += 0.4

        return {
            'type': 'defensive_attitude',
            'present': defensiveness_score > 0.5,
            'severity': defensiveness_score,
            'indicators': {
                'verbal_aggression': voice_volume.get('level') == 'loud',
                'emotional_reactivity': voice_pitch.get('variation', 0) > 0.5,
                'negative_bias': emotional_valence < -0.5
            }
        }

    def _assess_trust_issues(self, integrated_data):
        """评估信任问题"""
        trust_score = 1.0  # 初始信任分数

        # 检查情绪指标
        emotional_profile = integrated_data.get('emotional_profile', {})

        # 怀疑和恐惧相关情绪
        suspicion_emotions = ['fearful', 'suspicious', 'anxious']
        for emotion in suspicion_emotions:
            for key, value in emotional_profile.items():
                if emotion in key.lower():
                    trust_score -= value * 0.3

        # 检查防御性指标
        cognitive_patterns = integrated_data.get('cognitive_patterns', {})
        if cognitive_patterns.get('consistency', 1) < 0.6:
            trust_score -= 0.2

        trust_issues_present = trust_score < 0.7

        return {
            'type': 'trust_issues',
            'present': trust_issues_present,
            'severity': 1 - trust_score if trust_issues_present else 0,
            'manifestations': {
                'emotional_guardedness': 1 - trust_score,
                'communication_hesitancy': cognitive_patterns.get('consistency', 1) < 0.6,
                'avoidance_behaviors': False  # 需要更多数据判断
            }
        }
