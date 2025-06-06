from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import jieba
from collections import Counter


class TextEmotionAnalyzer:
    def __init__(self):
        # 初始化情感分析模型
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="uer/chinese_roberta_L-12_H-768"
        )

        # 加载中文分词
        jieba.initialize()

        # 情感词典
        self.emotion_lexicon = self._load_emotion_lexicon()

    def analyze_semantics(self, text):
        """深度语义分析"""
        # 分句
        sentences = self._split_sentences(text)

        # 逐句分析
        sentence_emotions = []
        for sentence in sentences:
            if sentence.strip():
                emotion = self.sentiment_analyzer(sentence)[0]
                sentence_emotions.append({
                    'text': sentence,
                    'label': emotion['label'],
                    'score': emotion['score']
                })

        # 整体情感分析
        overall_emotion = self._analyze_overall_emotion(sentence_emotions)

        # 语义一致性分析
        consistency = self._analyze_consistency(sentence_emotions)

        return {
            'sentences': sentence_emotions,
            'overall': overall_emotion,
            'consistency': consistency,
            'semantic_structure': self._analyze_semantic_structure(text)
        }

    def extract_keyword_emotions(self, text):
        """提取关键词情感极性"""
        # 分词
        words = jieba.lcut(text)

        # 提取关键词
        keywords = self._extract_keywords(words)

        # 分析每个关键词的情感
        keyword_emotions = []
        for keyword in keywords:
            emotion = self._get_word_emotion(keyword)
            keyword_emotions.append({
                'word': keyword,
                'emotion': emotion['polarity'],
                'intensity': emotion['intensity']
            })

        return keyword_emotions

    def build_emotion_vector(self, semantic_analysis):
        """构建多维情感向量"""
        # 定义情感维度
        dimensions = {
            'valence': 0,  # 效价（积极-消极）
            'arousal': 0,  # 唤醒度
            'dominance': 0,  # 支配度
            'certainty': 0,  # 确定性
            'expectancy': 0  # 期待性
        }

        # 基于语义分析结果计算各维度值
        overall = semantic_analysis['overall']

        # 计算效价
        if overall['label'] == 'POSITIVE':
            dimensions['valence'] = overall['score']
        else:
            dimensions['valence'] = -overall['score']

        # 计算其他维度（示例）
        dimensions['arousal'] = self._calculate_arousal(semantic_analysis)
        dimensions['dominance'] = self._calculate_dominance(semantic_analysis)
        dimensions['certainty'] = semantic_analysis['consistency']
        dimensions['expectancy'] = self._calculate_expectancy(semantic_analysis)

        # 转换为向量
        vector = np.array([dimensions[dim] for dim in dimensions])

        return vector

    def _load_emotion_lexicon(self):
        """加载情感词典"""
        # 示例词典
        return {
            '高兴': {'polarity': 'positive', 'intensity': 0.8},
            '悲伤': {'polarity': 'negative', 'intensity': 0.7},
            '愤怒': {'polarity': 'negative', 'intensity': 0.9},
            '恐惧': {'polarity': 'negative', 'intensity': 0.8},
            '平静': {'polarity': 'neutral', 'intensity': 0.3},
            '紧张': {'polarity': 'negative', 'intensity': 0.6},
            '兴奋': {'polarity': 'positive', 'intensity': 0.9}
        }

    def _split_sentences(self, text):
        """分句"""
        # 使用标点符号分句
        import re
        sentences = re.split('[。！？；]', text)
        return [s for s in sentences if s.strip()]

    def _analyze_overall_emotion(self, sentence_emotions):
        """分析整体情感"""
        if not sentence_emotions:
            return {'label': 'NEUTRAL', 'score': 0.5}

        # 统计各类情感
        positive_count = sum(1 for s in sentence_emotions if s['label'] == 'POSITIVE')
        negative_count = sum(1 for s in sentence_emotions if s['label'] == 'NEGATIVE')

        # 计算平均分数
        avg_score = np.mean([s['score'] for s in sentence_emotions])

        # 判断整体情感
        if positive_count > negative_count:
            return {'label': 'POSITIVE', 'score': avg_score}
        elif negative_count > positive_count:
            return {'label': 'NEGATIVE', 'score': avg_score}
        else:
            return {'label': 'NEUTRAL', 'score': 0.5}

    def _analyze_consistency(self, sentence_emotions):
        """分析情感一致性"""
        if len(sentence_emotions) < 2:
            return 1.0

        # 计算情感标签的一致性
        labels = [s['label'] for s in sentence_emotions]
        label_counts = Counter(labels)

        # 最常见标签的比例
        most_common_ratio = label_counts.most_common(1)[0][1] / len(labels)

        # 分数的标准差
        scores = [s['score'] for s in sentence_emotions]
        score_std = np.std(scores)

        # 综合计算一致性
        consistency = most_common_ratio * (1 - score_std)

        return min(1.0, max(0.0, consistency))

    def _extract_keywords(self, words):
        """提取关键词"""
        # 使用TF-IDF或TextRank算法
        # 这里简化为返回名词和形容词
        import jieba.posseg as pseg

        keywords = []
        for word, flag in pseg.lcut(''.join(words)):
            if flag.startswith('n') or flag.startswith('a'):
                keywords.append(word)

        return list(set(keywords))[:10]  # 返回前10个关键词

    def _get_word_emotion(self, word):
        """获取单词情感"""
        if word in self.emotion_lexicon:
            return self.emotion_lexicon[word]
        else:
            # 使用模型预测
            result = self.sentiment_analyzer(word)[0]
            return {
                'polarity': 'positive' if result['label'] == 'POSITIVE' else 'negative',
                'intensity': result['score']
            }

    def _analyze_semantic_structure(self, text):
        """分析语义结构"""
        # 提取主题、论点、论据等
        return {
            'themes': self._extract_themes(text),
            'arguments': self._extract_arguments(text),
            'coherence': self._calculate_coherence(text)
        }

    def _extract_themes(self, text):
        """提取主题"""
        # 使用LDA或其他主题模型
        # 这里简化返回
        return ['主题1', '主题2']

    def _extract_arguments(self, text):
        """提取论点"""
        # 识别因果关系、转折关系等
        return ['论点1', '论点2']

    def _calculate_coherence(self, text):
        """计算连贯性"""
        # 基于句子之间的语义相似度
        return 0.8

    def _calculate_arousal(self, semantic_analysis):
        """计算唤醒度"""
        # 基于情感强度和关键词
        scores = [s['score'] for s in semantic_analysis['sentences']]
        return np.mean(scores) if scores else 0.5

    def _calculate_dominance(self, semantic_analysis):
        """计算支配度"""
        # 基于语言的断言性和确定性
        return 0.6  # 示例值

    def _calculate_expectancy(self, semantic_analysis):
        """计算期待性"""
        # 基于未来时态和期望词汇
        return 0.5  # 示例值
