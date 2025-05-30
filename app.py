from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
from datetime import datetime
import json

# 导入分析模块
from modules.face_emotion import FaceEmotionAnalyzer
from modules.voice_emotion import VoiceEmotionAnalyzer
from modules.text_emotion import TextEmotionAnalyzer
from modules.psychological_evaluator import PsychologicalEvaluator
from modules.risk_assessor import RiskAssessor

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化分析器
face_analyzer = FaceEmotionAnalyzer()
voice_analyzer = VoiceEmotionAnalyzer()
text_analyzer = TextEmotionAnalyzer()
psych_evaluator = PsychologicalEvaluator()
risk_assessor = RiskAssessor()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze/face', methods=['POST'])
def analyze_face():
    """分析面部表情"""
    try:
        image_data = request.json['image']

        # 面部情感分析
        emotion_data = face_analyzer.analyze(image_data)

        # 计算情感强度指数
        emotion_intensity = face_analyzer.calculate_intensity(emotion_data)

        # 标记关键情感波动
        key_moments = face_analyzer.detect_emotion_peaks(emotion_data)

        return jsonify({
            'status': 'success',
            'data': {
                'emotions': emotion_data,
                'intensity': emotion_intensity,
                'key_moments': key_moments
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """分析语音情感"""
    try:
        audio_data = request.files['audio']

        # 语音特征提取
        features = voice_analyzer.extract_features(audio_data)

        # 情感识别（语调、音量、语速）
        emotion_metrics = voice_analyzer.analyze_emotions(features)

        # 计算情感强度
        intensity = voice_analyzer.calculate_intensity(emotion_metrics)

        return jsonify({
            'status': 'success',
            'data': {
                'pitch': emotion_metrics['pitch'],
                'volume': emotion_metrics['volume'],
                'speed': emotion_metrics['speed'],
                'emotion': emotion_metrics['emotion'],
                'intensity': intensity
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """分析文本情感"""
    try:
        text = request.json['text']

        # 深度语义分析
        semantic_analysis = text_analyzer.analyze_semantics(text)

        # 提取关键词情感极性
        keyword_emotions = text_analyzer.extract_keyword_emotions(text)

        # 构建情感向量
        emotion_vector = text_analyzer.build_emotion_vector(semantic_analysis)

        return jsonify({
            'status': 'success',
            'data': {
                'semantic_analysis': semantic_analysis,
                'keywords': keyword_emotions,
                'emotion_vector': emotion_vector.tolist()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/evaluate/comprehensive', methods=['POST'])
def comprehensive_evaluation():
    """综合心理状态评估"""
    try:
        data = request.json

        # 融合多模态分析结果
        integrated_data = psych_evaluator.integrate_multimodal_data(
            data.get('face_data'),
            data.get('voice_data'),
            data.get('text_data')
        )

        # 构建心理状态雷达图数据
        radar_data = psych_evaluator.build_psychological_radar(integrated_data)

        # 识别潜在心理障碍风险
        psychological_risks = risk_assessor.identify_psychological_risks(integrated_data)

        # 评估沟通障碍可能性
        communication_barriers = risk_assessor.assess_communication_barriers(integrated_data)

        # 生成干预建议
        interventions = psych_evaluator.generate_interventions(
            psychological_risks,
            communication_barriers
        )

        return jsonify({
            'status': 'success',
            'data': {
                'radar_chart': radar_data,
                'psychological_risks': psychological_risks,
                'communication_barriers': communication_barriers,
                'interventions': interventions,
                'emotion_intensity_index': integrated_data['overall_intensity'],
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@socketio.on('real_time_analysis')
def handle_real_time_analysis(data):
    """实时分析WebSocket处理"""
    try:
        analysis_type = data.get('type')

        if analysis_type == 'face':
            result = face_analyzer.analyze_realtime(data['frame'])
        elif analysis_type == 'voice':
            result = voice_analyzer.analyze_realtime(data['audio'])

        emit('analysis_result', {
            'type': analysis_type,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('analysis_error', {'error': str(e)})


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
