import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp
from collections import deque
import threading
import time


class FaceEmotionAnalyzer:
    def __init__(self):
        # 初始化MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

        # 情绪类别
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

        # 微表情检测参数
        self.micro_expression_buffer = deque(maxlen=30)  # 1秒缓冲（30fps）
        self.emotion_history = deque(maxlen=150)  # 5秒历史

    def analyze(self, image):
        """分析单张图像"""
        try:
            # 使用DeepFace进行情绪识别
            result = DeepFace.analyze(
                img_path=image,
                actions=['emotion'],
                enforce_detection=False
            )

            emotions = result[0]['emotion'] if isinstance(result, list) else result['emotion']

            # 归一化情绪值
            total = sum(emotions.values())
            normalized_emotions = {k: v / total for k, v in emotions.items()}

            return normalized_emotions

        except Exception as e:
            print(f"Face analysis error: {e}")
            return {emotion: 0 for emotion in self.emotion_labels}

    def analyze_realtime(self, frame):
        """实时分析视频帧"""
        try:
            # 检测人脸
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                return None

            # 获取面部关键点
            landmarks = results.multi_face_landmarks[0]

            # 分析情绪
            emotions = self.analyze(frame)

            # 检测微表情
            micro_expressions = self.detect_micro_expressions(landmarks, emotions)

            # 更新历史
            self.emotion_history.append(emotions)

            return {
                'emotions': emotions,
                'micro_expressions': micro_expressions,
                'face_detected': True
            }

        except Exception as e:
            print(f"Realtime analysis error: {e}")
            return None

    def analyze_video(self, video_path):
        """分析视频文件"""
        cap = cv2.VideoCapture(video_path)

        frame_emotions = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 每隔几帧分析一次（提高效率）
            if frame_count % 5 == 0:
                result = self.analyze_realtime(frame)
                if result:
                    frame_emotions.append({
                        'frame': frame_count,
                        'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS),
                        'data': result
                    })

            frame_count += 1

        cap.release()

        # 汇总分析结果
        if frame_emotions:
            avg_emotions = self._calculate_average_emotions(frame_emotions)
            key_moments = self._find_key_moments(frame_emotions)

            return {
                'average_emotions': avg_emotions,
                'key_moments': key_moments,
                'total_frames': frame_count,
                'analyzed_frames': len(frame_emotions)
            }

        return None

    def detect_micro_expressions(self, landmarks, current_emotions):
        """检测微表情"""
        # 提取关键面部特征
        features = self._extract_facial_features(landmarks)

        # 存储当前特征
        self.micro_expression_buffer.append(features)

        if len(self.micro_expression_buffer) < 10:
            return {}

        # 分析特征变化
        micro_expressions = {
            'eye_movement': self._analyze_eye_movement(),
            'lip_tension': self._analyze_lip_tension(),
            'brow_furrow': self._analyze_brow_furrow(),
            'nostril_flare': self._analyze_nostril_flare()
        }

        return micro_expressions

    def _extract_facial_features(self, landmarks):
        """提取面部特征点"""
        # 提取关键点坐标
        points = []
        for landmark in landmarks.landmark:
            points.append([landmark.x, landmark.y, landmark.z])

        return np.array(points)

    def _analyze_eye_movement(self):
        """分析眼部运动"""
        if len(self.micro_expression_buffer) < 2:
            return 0

        # 计算眼部区域的运动幅度
        recent_features = list(self.micro_expression_buffer)[-10:]
        eye_indices = [33, 133, 157, 158, 159, 160, 161, 163]  # 眼部关键点

        movements = []
        for i in range(1, len(recent_features)):
            prev_eyes = recent_features[i - 1][eye_indices]
            curr_eyes = recent_features[i][eye_indices]
            movement = np.mean(np.abs(curr_eyes - prev_eyes))
            movements.append(movement)

        return min(1.0, np.mean(movements) * 100)

    def _analyze_lip_tension(self):
        """分析嘴唇紧张度"""
        if len(self.micro_expression_buffer) < 2:
            return 0

        # 计算嘴唇区域的变化
        recent_features = list(self.micro_expression_buffer)[-10:]
        lip_indices = [61, 291, 39, 269, 0, 17, 18, 200]  # 嘴唇关键点

        tensions = []
        for features in recent_features:
            lip_points = features[lip_indices]
            # 计算嘴唇的紧张度（基于点之间的距离变化）
            distances = []
            for i in range(len(lip_points)):
                for j in range(i + 1, len(lip_points)):
                    dist = np.linalg.norm(lip_points[i] - lip_points[j])
                    distances.append(dist)
            tensions.append(np.std(distances))

        return min(1.0, np.mean(tensions) * 10)

    def _analyze_brow_furrow(self):
        """分析眉头紧锁程度"""
        if len(self.micro_expression_buffer) < 2:
            return 0

        # 分析眉毛区域
        recent_features = list(self.micro_expression_buffer)[-10:]
        brow_indices = [70, 63, 105, 66, 107]  # 眉毛关键点

        furrows = []
        for features in recent_features:
            brow_points = features[brow_indices]
            # 计算眉毛的垂直位置变化
            vertical_pos = np.mean(brow_points[:, 1])
            furrows.append(vertical_pos)

        # 计算变化幅度
        furrow_intensity = np.std(furrows)
        return min(1.0, furrow_intensity * 20)

    def _analyze_nostril_flare(self):
        """分析鼻翼扩张"""
        if len(self.micro_expression_buffer) < 2:
            return 0

        # 分析鼻子区域
        recent_features = list(self.micro_expression_buffer)[-10:]
        nose_indices = [1, 2, 5, 4, 6, 19, 20, 94, 125]  # 鼻子关键点

        flares = []
        for features in recent_features:
            nose_points = features[nose_indices]
            # 计算鼻翼宽度
            width = np.max(nose_points[:, 0]) - np.min(nose_points[:, 0])
            flares.append(width)

        # 计算扩张程度
        flare_intensity = np.std(flares)
        return min(1.0, flare_intensity * 50)

    def calculate_intensity(self, emotions):
        """计算情感强度"""
        if not emotions:
            return 0

        # 计算非中性情绪的强度
        intensity = 0
        for emotion, value in emotions.items():
            if emotion != 'neutral':
                # 不同情绪的权重
                weight = {
                    'angry': 1.2,
                    'disgust': 1.0,
                    'fear': 1.3,
                    'happy': 0.8,
                    'sad': 1.1,
                    'surprise': 0.9
                }.get(emotion, 1.0)

                intensity += value * weight

        return min(100, intensity * 100)

    def detect_emotion_peaks(self, emotions):
        """检测情绪峰值"""
        if len(self.emotion_history) < 30:
            return []

        peaks = []
        history = list(self.emotion_history)

        for i in range(15, len(history) - 15):
            for emotion in self.emotion_labels:
                if emotion == 'neutral':
                    continue

                # 获取当前值和周围值
                current = history[i].get(emotion, 0)
                before = np.mean([h.get(emotion, 0) for h in history[i - 15:i]])
                after = np.mean([h.get(emotion, 0) for h in history[i + 1:i + 16]])

                # 检测峰值
                # 检测峰值
                if current > before * 1.5 and current > after * 1.5 and current > 0.3:
                    peaks.append({
                        'emotion': emotion,
                        'intensity': current,
                        'frame_index': i,
                        'timestamp': datetime.now().isoformat()
                    })

            return peaks

            def _calculate_average_emotions(self, frame_emotions):
                """计算平均情绪"""
                emotion_sums = {emotion: 0 for emotion in self.emotion_labels}

                for frame_data in frame_emotions:
                    emotions = frame_data['data'].get('emotions', {})
                    for emotion, value in emotions.items():
                        emotion_sums[emotion] += value

                # 计算平均值
                count = len(frame_emotions)
                return {emotion: value / count for emotion, value in emotion_sums.items()}

            def _find_key_moments(self, frame_emotions):
                """查找关键时刻"""
                key_moments = []

                for i, frame_data in enumerate(frame_emotions):
                    emotions = frame_data['data'].get('emotions', {})

                    # 查找强烈情绪
                    for emotion, value in emotions.items():
                        if emotion != 'neutral' and value > 0.7:
                            key_moments.append({
                                'frame': frame_data['frame'],
                                'timestamp': frame_data['timestamp'],
                                'emotion': emotion,
                                'intensity': value
                            })

                return key_moments
