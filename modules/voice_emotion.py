import librosa
import numpy as np
from scipy import signal
import io


class VoiceEmotionAnalyzer:
    def __init__(self):
        self.sample_rate = 16000
        self.emotion_categories = {
            'calm': 0,
            'happy': 1,
            'sad': 2,
            'angry': 3,
            'fearful': 4,
            'disgust': 5,
            'surprised': 6,
            'neutral': 7
        }

    def extract_features(self, audio_file):
        """提取语音特征"""
        # 读取音频
        audio_data = audio_file.read()
        y, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate)

        # 提取MFCC特征
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # 提取音调特征
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # 提取节奏特征
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # 提取能量特征
        energy = np.sum(y ** 2) / len(y)

        # 提取频谱特征
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

        return {
            'mfccs': mfccs,
            'pitch': self._extract_pitch_features(pitches, magnitudes),
            'tempo': tempo,
            'energy': energy,
            'spectral_centroids': np.mean(spectral_centroids),
            'spectral_rolloff': np.mean(spectral_rolloff)
        }

    def analyze_emotions(self, features):
        """分析语音情感"""
        # 分析语调变化
        pitch_analysis = self._analyze_pitch(features['pitch'])

        # 分析音量变化
        volume_analysis = self._analyze_volume(features['energy'])

        # 分析语速
        speed_analysis = self._analyze_speed(features['tempo'])

        # 综合判断情绪
        emotion = self._predict_emotion(features)

        return {
            'pitch': pitch_analysis,
            'volume': volume_analysis,
            'speed': speed_analysis,
            'emotion': emotion
        }

    def calculate_intensity(self, emotion_metrics):
        """计算语音情感强度"""
        # 基于各项指标计算综合强度
        pitch_intensity = emotion_metrics['pitch']['intensity']
        volume_intensity = emotion_metrics['volume']['intensity']
        speed_intensity = emotion_metrics['speed']['intensity']

        # 加权平均
        intensity = (pitch_intensity * 0.35 +
                     volume_intensity * 0.35 +
                     speed_intensity * 0.3)

        return min(100, max(0, intensity * 100))

    def _extract_pitch_features(self, pitches, magnitudes):
        """提取音调特征"""
        pitch_values = []

        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)

        if pitch_values:
            return {
                'mean': np.mean(pitch_values),
                'std': np.std(pitch_values),
                'max': np.max(pitch_values),
                'min': np.min(pitch_values),
                'range': np.max(pitch_values) - np.min(pitch_values)
            }
        else:
            return {'mean': 0, 'std': 0, 'max': 0, 'min': 0, 'range': 0}

    def _analyze_pitch(self, pitch_features):
        """分析音调"""
        # 计算音调变化程度
        variation = pitch_features['std'] / (pitch_features['mean'] + 1e-6)

        # 判断音调特征
        if pitch_features['mean'] > 250:  # 高音调
            pitch_type = 'high'
            intensity = 0.8
        elif pitch_features['mean'] < 150:  # 低音调
            pitch_type = 'low'
            intensity = 0.6
        else:
            pitch_type = 'normal'
            intensity = 0.4

        return {
            'type': pitch_type,
            'variation': variation,
            'intensity': intensity,
            'characteristics': pitch_features
        }

    def _analyze_volume(self, energy):
        """分析音量"""
        # 根据能量值判断音量
        if energy > 0.1:
            volume_level = 'loud'
            intensity = 0.9
        elif energy > 0.05:
            volume_level = 'normal'
            intensity = 0.5
        else:
            volume_level = 'quiet'
            intensity = 0.3

        return {
            'level': volume_level,
            'energy': energy,
            'intensity': intensity
        }

    def _analyze_speed(self, tempo):
        """分析语速"""
        # 根据节奏判断语速
        if tempo > 150:
            speed_type = 'fast'
            intensity = 0.8
        elif tempo < 100:
            speed_type = 'slow'
            intensity = 0.6
        else:
            speed_type = 'normal'
            intensity = 0.4

        return {
            'type': speed_type,
            'tempo': tempo,
            'intensity': intensity
        }

    def _predict_emotion(self, features):
        """预测情绪类别"""
        # 示例：基于特征的简单规则判断
        emotions_prob = {}

        for emotion in self.emotion_categories:
            emotions_prob[emotion] = np.random.random()

        # 归一化
        total = sum(emotions_prob.values())
        for emotion in emotions_prob:
            emotions_prob[emotion] /= total

        return emotions_prob
