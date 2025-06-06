from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
from datetime import datetime
import json
import os
import base64
import io
from werkzeug.utils import secure_filename
import cv2
from PIL import Image

# 导入分析模块
from modules.face_emotion import FaceEmotionAnalyzer
from modules.voice_emotion import VoiceEmotionAnalyzer
from modules.text_emotion import TextEmotionAnalyzer
from modules.psychological_evaluator import PsychologicalEvaluator
from modules.risk_assessor import RiskAssessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化分析器
face_analyzer = FaceEmotionAnalyzer()
voice_analyzer = VoiceEmotionAnalyzer()
text_analyzer = TextEmotionAnalyzer()
psych_evaluator = PsychologicalEvaluator()
risk_assessor = RiskAssessor()

# 存储会话数据
sessions = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze/face', methods=['POST'])
def analyze_face():
    """分析面部表情 - 支持实时和视频"""
    try:
        data = request.json

        if 'image' in data:
            # 实时图像分析
            image_data = data['image']
            # 移除 data URL 前缀
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)

            # 转换为 OpenCV 格式
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)

            # 面部情感分析
            emotion_data = face_analyzer.analyze(image_np)

        elif 'video' in request.files:
            # 视频文件分析
            video = request.files['video']
            video_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                      secure_filename(video.filename))
            video.save(video_path)

            # 分析视频中的情感
            emotion_data = face_analyzer.analyze_video(video_path)

            # 清理临时文件
            os.remove(video_path)
        else:
            return jsonify({'status': 'error', 'message': '未提供图像或视频数据'}), 400

        # 计算情感强度指数
        emotion_intensity = face_analyzer.calculate_intensity(emotion_data)

        # 检测微表情
        micro_expressions = face_analyzer.detect_micro_expressions(emotion_data)

        # 标记关键情感波动
        key_moments = face_analyzer.detect_emotion_peaks(emotion_data)

        return jsonify({
            'status': 'success',
            'data': {
                'emotions': emotion_data,
                'intensity': emotion_intensity,
                'micro_expressions': micro_expressions,
                'key_moments': key_moments,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """分析语音情感"""
    try:
        if 'audio' not in request.files:
            return jsonify({'status': 'error', 'message': '未提供音频文件'}), 400

        audio_file = request.files['audio']

        # 保存临时文件
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                  secure_filename(audio_file.filename))
        audio_file.save(audio_path)

        # 语音特征提取
        with open(audio_path, 'rb') as f:
            features = voice_analyzer.extract_features(f)

        # 情感识别（语调、音量、语速）
        emotion_metrics = voice_analyzer.analyze_emotions(features)

        # 计算情感强度
        intensity = voice_analyzer.calculate_intensity(emotion_metrics)

        # 清理临时文件
        os.remove(audio_path)

        return jsonify({
            'status': 'success',
            'data': {
                'pitch': emotion_metrics['pitch'],
                'volume': emotion_metrics['volume'],
                'speed': emotion_metrics['speed'],
                'emotion': emotion_metrics['emotion'],
                'intensity': intensity,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """分析文本情感"""
    try:
        data = request.json

        if 'text' not in data:
            return jsonify({'status': 'error', 'message': '未提供文本内容'}), 400

        text = data['text']

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
                'emotion_vector': emotion_vector.tolist(),
                'timestamp': datetime.now().isoformat()
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

        # 生成评估报告ID
        report_id = f"JPA_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return jsonify({
            'status': 'success',
            'data': {
                'report_id': report_id,
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


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """开始新的分析会话"""
    try:
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d%H%M%S')}_{np.random.randint(1000, 9999)}"

        sessions[session_id] = {
            'id': session_id,
            'start_time': datetime.now().isoformat(),
            'face_data': [],
            'voice_data': [],
            'text_data': [],
            'events': []
        }

        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': '会话已创建'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/session/<session_id>/data', methods=['GET'])
def get_session_data(session_id):
    """获取会话数据"""
    try:
        if session_id not in sessions:
            return jsonify({'status': 'error', 'message': '会话不存在'}), 404

        return jsonify({
            'status': 'success',
            'data': sessions[session_id]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/report/generate/<report_id>', methods=['GET'])
def generate_report_pdf(report_id):
    """生成PDF格式报告"""
    try:
        # 这里应该实现PDF生成逻辑
        # 暂时返回模拟数据
        return jsonify({
            'status': 'success',
            'download_url': f'/api/report/download/{report_id}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': '连接成功'})


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('start_realtime_analysis')
def handle_start_realtime(data):
    """开始实时分析"""
    session_id = data.get('session_id')
    analysis_type = data.get('type')

    emit('realtime_started', {
        'session_id': session_id,
        'type': analysis_type,
        'message': f'{analysis_type}实时分析已启动'
    })


@socketio.on('realtime_frame')
def handle_realtime_frame(data):
    """处理实时帧数据"""
    try:
        session_id = data.get('session_id')
        frame_type = data.get('type')
        frame_data = data.get('data')

        result = None

        if frame_type == 'face':
            # 处理面部数据
            image_data = frame_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)

            result = face_analyzer.analyze_realtime(image_np)

        elif frame_type == 'voice':
            # 处理语音数据
            audio_data = base64.b64decode(frame_data)
            result = voice_analyzer.analyze_realtime(audio_data)

        # 存储到会话
        if session_id in sessions and result:
            sessions[session_id][f'{frame_type}_data'].append({
                'timestamp': datetime.now().isoformat(),
                'data': result
            })

        # 发送分析结果
        emit('analysis_result', {
            'type': frame_type,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        emit('analysis_error', {'error': str(e)})


@socketio.on('stop_realtime_analysis')
def handle_stop_realtime(data):
    """停止实时分析"""
    session_id = data.get('session_id')
    analysis_type = data.get('type')

    emit('realtime_stopped', {
        'session_id': session_id,
        'type': analysis_type,
        'message': f'{analysis_type}实时分析已停止'
    })


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
