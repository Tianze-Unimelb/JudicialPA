// Vue 3 应用实例
const { createApp } = Vue;

createApp({
    data() {
        return {
            // 视图控制
            currentView: 'dashboard',
            currentTime: '',

            // 仪表盘数据
            emotionIntensity: 0,
            intensityLevel: 'low',
            intensityStatus: '情绪稳定',
            emotionDistribution: {
                happy: 0,
                sad: 0,
                angry: 0,
                fear: 0,
                surprise: 0,
                neutral: 0
            },
            riskWarnings: [],
            interventionSuggestions: {},

            // 实时分析数据
            cameraActive: false,
            isRecording: false,
            recordingTime: 0,
            textInput: '',

            // 分析结果
            faceEmotions: null,
            voiceAnalysis: null,
            textAnalysis: null,
            comprehensiveReport: null,

            // WebSocket连接
            socket: null,

            // 图表实例
            gaugeChart: null,
            radarChart: null,
            voiceChart: null,

            // 设置
            settings: {
                emotionThreshold: 60,
                riskLevel: 'medium',
                anonymizeData: true,
                encryptStorage: false
            },

            // 助手
            assistantExpanded: false,
            assistantMessages: [],
            assistantQuery: '',

            // 音频相关
            audioContext: null,
            mediaRecorder: null,
            audioChunks: [],
            audioData: null
        };
    },

    mounted() {
        // 初始化WebSocket连接
        this.initWebSocket();

        // 初始化图表
        this.initCharts();

        // 更新时间
        setInterval(this.updateTime, 1000);

        // 初始化音频上下文
        this.initAudioContext();
    },

    methods: {
        // 初始化WebSocket
        initWebSocket() {
            this.socket = io();

            this.socket.on('connect', () => {
                console.log('WebSocket connected');
            });

            this.socket.on('analysis_result', (data) => {
                this.handleRealtimeResult(data);
            });

            this.socket.on('analysis_error', (error) => {
                console.error('Analysis error:', error);
            });
        },

        // 初始化图表
        initCharts() {
            // 情感强度仪表盘
            this.$nextTick(() => {
                if (this.$refs.gaugeChart) {
                    this.initGaugeChart();
                }
                if (this.$refs.radarChart) {
                    this.initRadarChart();
                }
            });
        },

        // 初始化仪表盘图表
        initGaugeChart() {
            const chartDom = this.$refs.gaugeChart;
            this.gaugeChart = echarts.init(chartDom);

            const option = {
                series: [
                    {
                        type: 'gauge',
                        startAngle: 180,
                        endAngle: 0,
                        min: 0,
                        max: 100,
                        splitNumber: 10,
                        axisLine: {
                            lineStyle: {
                                width: 30,
                                color: [
                                    [0.3, '#48bb78'],
                                    [0.7, '#f6ad55'],
                                    [1, '#fc8181']
                                ]
                            }
                        },
                        pointer: {
                            itemStyle: {
                                color: '#00d4ff'
                            }
                        },
                        axisTick: {
                            distance: -30,
                            length: 8,
                            lineStyle: {
                                color: '#fff',
                                width: 2
                            }
                        },
                        splitLine: {
                            distance: -30,
                            length: 30,
                            lineStyle: {
                                color: '#fff',
                                width: 4
                            }
                        },
                        axisLabel: {
                            color: 'inherit',
                            distance: 40,
                            fontSize: 16
                        },
                        detail: {
                            valueAnimation: true,
                            formatter: '{value}',
                            color: 'inherit',
                            fontSize: 30
                        },
                        data: [
                            {
                                value: 0
                            }
                        ]
                    }
                ]
            };

            this.gaugeChart.setOption(option);
        },

        // 初始化雷达图
        initRadarChart() {
            const chartDom = this.$refs.radarChart;
            this.radarChart = echarts.init(chartDom);

            const option = {
                radar: {
                    indicator: [
                        { name: '情绪稳定性', max: 100 },
                        { name: '压力水平', max: 100 },
                        { name: '焦虑水平', max: 100 },
                        { name: '抑郁风险', max: 100 },
                        { name: '认知清晰度', max: 100 },
                        { name: '社会适应性', max: 100 },
                        { name: '自我控制', max: 100 },
                        { name: '心理韧性', max: 100 }
                    ],
                    axisName: {
                        color: '#a0aec0'
                    },
                    splitLine: {
                        lineStyle: {
                            color: '#2d3748'
                        }
                    },
                    splitArea: {
                        areaStyle: {
                            color: ['rgba(0, 212, 255, 0.05)', 'rgba(102, 126, 234, 0.05)']
                        }
                    }
                },
                series: [
                    {
                        type: 'radar',
                        data: [
                            {
                                value: [70, 30, 40, 20, 80, 75, 65, 85],
                                name: '心理状态',
                                symbol: 'circle',
                                symbolSize: 8,
                                lineStyle: {
                                    color: '#00d4ff',
                                    width: 2
                                },
                                itemStyle: {
                                    color: '#00d4ff'
                                },
                                areaStyle: {
                                    color: 'rgba(0, 212, 255, 0.3)'
                                }
                            }
                        ]
                    }
                ]
            };

            this.radarChart.setOption(option);
        },

        // 初始化音频上下文
        initAudioContext() {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        },

        // 更新时间
        updateTime() {
            const now = new Date();
            this.currentTime = now.toLocaleString('zh-CN');
        },

        // 切换摄像头
        async toggleCamera() {
            if (this.cameraActive) {
                this.stopCamera();
            } else {
                await this.startCamera();
            }
        },

        // 启动摄像头
        async startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = this.$refs.videoElement;
                video.srcObject = stream;
                this.cameraActive = true;

                // 开始实时分析
                this.startRealtimeFaceAnalysis();
            } catch (error) {
                console.error('Camera error:', error);
                alert('无法访问摄像头');
            }
        },

        // 停止摄像头
        stopCamera() {
            const video = this.$refs.videoElement;
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }
            this.cameraActive = false;
        },

        // 实时面部分析
        startRealtimeFaceAnalysis() {
            const video = this.$refs.videoElement;
            const canvas = this.$refs.canvasElement;
            const ctx = canvas.getContext('2d');

            const analyze = () => {
                if (!this.cameraActive) return;

                // 设置画布大小
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // 绘制视频帧
                ctx.drawImage(video, 0, 0);

                // 获取图像数据
                const imageData = canvas.toDataURL('image/jpeg', 0.8);

                // 发送到服务器分析
                this.socket.emit('real_time_analysis', {
                    type: 'face',
                    frame: imageData
                });

                // 继续下一帧
                requestAnimationFrame(analyze);
            };

            analyze();
        },

        // 捕获单帧
        async captureFrame() {
            const video = this.$refs.videoElement;
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            const imageData = canvas.toDataURL('image/jpeg');

            try {
                const response = await fetch('/api/analyze/face', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: imageData })
                });

                const result = await response.json();
                if (result.status === 'success') {
                    this.faceEmotions = result.data;
                    this.updateEmotionDistribution(result.data.emotions);
                    this.updateEmotionIntensity(result.data.intensity);
                }
            } catch (error) {
                console.error('Face analysis error:', error);
            }
        },

        // 切换录音
        async toggleRecording() {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                await this.startRecording();
            }
        },

        // 开始录音
        async startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.audioChunks = [];

                this.mediaRecorder.ondataavailable = (event) => {
                    this.audioChunks.push(event.data);
                };

                this.mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.audioData = audioBlob;
                    await this.analyzeAudio(audioBlob);
                };

                this.mediaRecorder.start();
                this.isRecording = true;

                // 开始计时
                this.startRecordingTimer();

                // 开始音频可视化
                this.startAudioVisualization(stream);
            } catch (error) {
                console.error('Recording error:', error);
                alert('无法访问麦克风');
            }
        },

        // 停止录音
        stopRecording() {
            if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
                this.mediaRecorder.stop();
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            this.isRecording = false;
            this.stopRecordingTimer();
        },

        // 录音计时
        startRecordingTimer() {
            this.recordingTime = 0;
            this.recordingTimer = setInterval(() => {
                this.recordingTime++;
            }, 1000);
        },

        stopRecordingTimer() {
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer);
                this.recordingTimer = null;
            }
        },

        // 音频可视化
        startAudioVisualization(stream) {
            const audioContext = this.audioContext;
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);
            const dataArray = new Uint8Array(analyser.frequencyBinCount);

            microphone.connect(analyser);

            const visualizer = this.$refs.audioVisualizer;
            const canvas = document.createElement('canvas');
            canvas.width = visualizer.offsetWidth;
            canvas.height = visualizer.offsetHeight;
            visualizer.appendChild(canvas);

            const canvasCtx = canvas.getContext('2d');

            const draw = () => {
                if (!this.isRecording) {
                    visualizer.innerHTML = '';
                    return;
                }

                requestAnimationFrame(draw);

                analyser.getByteFrequencyData(dataArray);

                canvasCtx.fillStyle = '#161b3d';
                canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

                const barWidth = (canvas.width / dataArray.length) * 2.5;
                let barHeight;
                let x = 0;

                for (let i = 0; i < dataArray.length; i++) {
                    barHeight = dataArray[i] / 2;

                    const gradient = canvasCtx.createLinearGradient(0, 0, 0, canvas.height);
                    gradient.addColorStop(0, '#00d4ff');
                    gradient.addColorStop(1, '#667eea');

                    canvasCtx.fillStyle = gradient;
                    canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

                    x += barWidth + 1;
                }
            };

            draw();
        },

        // 分析音频
        async analyzeAudio(audioBlob) {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            try {
                const response = await fetch('/api/analyze/voice', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                if (result.status === 'success') {
                    this.voiceAnalysis = result.data;
                    this.updateVoiceChart(result.data);
                }
            } catch (error) {
                console.error('Voice analysis error:', error);
            }
        },

        // 播放录音
        playbackAudio() {
            if (this.audioData) {
                const audio = new Audio(URL.createObjectURL(this.audioData));
                audio.play();
            }
        },

        // 分析文本
        async analyzeText() {
            if (!this.textInput.trim()) return;

            try {
                const response = await fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: this.textInput })
                });

                const result = await response.json();
                if (result.status === 'success') {
                    this.textAnalysis = result.data.semantic_analysis;
                    this.textAnalysis.keywords = result.data.keywords;
                }
            } catch (error) {
                console.error('Text analysis error:', error);
            }
        },

        // 清空文本
        clearText() {
            this.textInput = '';
            this.textAnalysis = null;
        },

        // 生成综合报告
        async generateReport() {
            // 收集所有分析数据
            const data = {
                face_data: this.faceEmotions ? {
                    intensity: this.emotionIntensity,
                    data: this.faceEmotions
                } : null,
                voice_data: this.voiceAnalysis ? {
                    intensity: this.voiceAnalysis.intensity,
                    data: this.voiceAnalysis
                } : null,
                text_data: this.textAnalysis ? {
                    data: {
                        semantic_analysis: this.textAnalysis,
                        emotion_vector: [0.5, 0.3, 0.7, 0.6, 0.4] // 示例向量
                    }
                } : null
            };

            try {
                const response = await fetch('/api/evaluate/comprehensive', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.status === 'success') {
                    this.comprehensiveReport = {
                        id: 'RPT' + Date.now(),
                        timestamp: result.data.timestamp,
                        emotion_intensity_index: result.data.emotion_intensity_index.toFixed(1),
                        risk_level: this.getRiskLevel(result.data.psychological_risks),
                        communication_assessment: this.getCommunicationAssessment(result.data.communication_barriers),
                        recommendations: this.formatRecommendations(result.data.interventions),
                        data: result.data
                    };

                    // 更新雷达图
                    if (result.data.radar_chart) {
                        this.updateRadarChart(result.data.radar_chart);
                    }

                    // 更新风险预警
                    if (result.data.psychological_risks) {
                        this.updateRiskWarnings(result.data.psychological_risks);
                    }

                    // 更新干预建议
                    if (result.data.interventions) {
                        this.interventionSuggestions = result.data.interventions;
                    }
                }
            } catch (error) {
                console.error('Report generation error:', error);
            }
        },

        // 处理实时分析结果
        handleRealtimeResult(data) {
            if (data.type === 'face' && data.result) {
                // 更新面部表情数据
                this.faceEmotions = data.result;
                if (data.result.emotions) {
                    this.updateEmotionDistribution(data.result.emotions);
                }
                if (data.result.intensity !== undefined) {
                    this.updateEmotionIntensity(data.result.intensity);
                }
            } else if (data.type === 'voice' && data.result) {
                // 更新语音数据
                this.voiceAnalysis = data.result;
            }
        },

        // 更新情绪分布
        updateEmotionDistribution(emotions) {
            for (const [emotion, value] of Object.entries(emotions)) {
                const mappedEmotion = this.mapEmotionKey(emotion);
                if (mappedEmotion in this.emotionDistribution) {
                    this.emotionDistribution[mappedEmotion] = Math.round(value * 100);
                }
            }
        },

        // 更新情感强度
        updateEmotionIntensity(intensity) {
            this.emotionIntensity = Math.round(intensity);

            // 更新强度等级和状态
            if (intensity < 30) {
                this.intensityLevel = 'low';
                this.intensityStatus = '情绪稳定';
            } else if (intensity < 70) {
                this.intensityLevel = 'medium';
                this.intensityStatus = '情绪波动中等';
            } else {
                this.intensityLevel = 'high';
                this.intensityStatus = '情绪波动剧烈';
            }

            // 更新仪表盘
            if (this.gaugeChart) {
                this.gaugeChart.setOption({
                    series: [{
                        data: [{ value: intensity }]
                    }]
                });
            }
        },

        // 更新雷达图
        updateRadarChart(radarData) {
            if (!this.radarChart) return;

            const values = [
                radarData.emotional_stability || 0,
                radarData.stress_level || 0,
                radarData.anxiety_level || 0,
                radarData.depression_risk || 0,
                radarData.cognitive_clarity || 0,
                radarData.social_adaptability || 0,
                radarData.self_control || 0,
                radarData.resilience || 0
            ];

            this.radarChart.setOption({
                series: [{
                    data: [{
                        value: values,
                        name: '心理状态'
                    }]
                }]
            });
        },

        // 更新语音图表
        updateVoiceChart(voiceData) {
            if (!this.$refs.voiceEmotionChart) return;

            const chartDom = this.$refs.voiceEmotionChart;
            const chart = echarts.init(chartDom);

            const option = {
                xAxis: {
                    type: 'category',
                    data: Object.keys(voiceData.emotion || {}),
                    axisLabel: {
                        color: '#a0aec0'
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        color: '#a0aec0'
                    }
                },
                series: [{
                    data: Object.values(voiceData.emotion || {}),
                    type: 'bar',
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#00d4ff' },
                            { offset: 1, color: '#667eea' }
                        ])
                    }
                }]
            };

            chart.setOption(option);
        },

        // 更新风险预警
        updateRiskWarnings(risks) {
            this.riskWarnings = risks.map(risk => ({
                id: 'WARN' + Date.now() + Math.random(),
                type: this.translateRiskType(risk.type),
                description: this.getRiskDescription(risk),
                level: risk.level,
                timestamp: risk.timestamp
            }));
        },
                // 辅助方法
        mapEmotionKey(emotion) {
            const mapping = {
                'happy': 'happy',
                'sad': 'sad',
                'angry': 'angry',
                'fear': 'fear',
                'fearful': 'fear',
                'surprise': 'surprise',
                'surprised': 'surprise',
                'neutral': 'neutral',
                'calm': 'neutral'
            };

            const key = emotion.toLowerCase().replace('face_', '');
            return mapping[key] || key;
        },

        translateEmotion(emotion) {
            const translations = {
                'happy': '快乐',
                'sad': '悲伤',
                'angry': '愤怒',
                'fear': '恐惧',
                'surprise': '惊讶',
                'neutral': '平静',
                'disgust': '厌恶'
            };
            return translations[emotion] || emotion;
        },

        translateMicroExpression(expression) {
            const translations = {
                'eye_movement': '眼部活动',
                'lip_tension': '嘴唇紧张',
                'brow_furrow': '眉头紧锁',
                'nostril_flare': '鼻翼扩张'
            };
            return translations[expression] || expression;
        },

        translateRiskType(type) {
            const translations = {
                'anxiety': '焦虑风险',
                'depression': '抑郁风险',
                'anger': '愤怒情绪',
                'trauma': '创伤应激',
                'overall_psychological_risk': '综合心理风险',
                'emotional_crisis': '情绪危机',
                'self_harm_risk': '自伤风险'
            };
            return translations[type] || type;
        },

        translateInterventionType(type) {
            const translations = {
                'immediate': '立即干预',
                'short_term': '短期建议',
                'long_term': '长期规划',
                'resources': '资源推荐'
            };
            return translations[type] || type;
        },

        getRiskDescription(risk) {
            const descriptions = {
                'high': '需要立即关注和专业介入',
                'medium': '建议密切监控并采取预防措施',
                'low': '风险可控，持续观察即可'
            };
            return descriptions[risk.level] || '需要进一步评估';
        },

        getRiskLevel(risks) {
            if (!risks || risks.length === 0) return 'low';

            const hasHigh = risks.some(r => r.level === 'high' || r.level === 'critical');
            const hasMedium = risks.some(r => r.level === 'medium');

            if (hasHigh) return 'high';
            if (hasMedium) return 'medium';
            return 'low';
        },

        getCommunicationAssessment(barriers) {
            if (!barriers || barriers.length === 0) return '沟通良好';

            const barrierCount = barriers.filter(b => b.present).length;

            if (barrierCount >= 3) return '存在明显沟通障碍';
            if (barrierCount >= 1) return '存在轻度沟通障碍';
            return '沟通良好';
        },

        formatRecommendations(interventions) {
            const recommendations = [];

            if (interventions.immediate) {
                interventions.immediate.forEach(item => {
                    recommendations.push({
                        id: 'REC' + Math.random(),
                        priority: 'high',
                        content: item.action
                    });
                });
            }

            if (interventions.short_term) {
                interventions.short_term.forEach(item => {
                    recommendations.push({
                        id: 'REC' + Math.random(),
                        priority: 'medium',
                        content: item.action
                    });
                });
            }

            if (interventions.long_term) {
                interventions.long_term.forEach(item => {
                    recommendations.push({
                        id: 'REC' + Math.random(),
                        priority: 'low',
                        content: item.action
                    });
                });
            }

            return recommendations;
        },

        getEmotionColor(emotion) {
            const colors = {
                'happy': '#48bb78',
                'sad': '#4299e1',
                'angry': '#fc8181',
                'fear': '#ed8936',
                'surprise': '#f6ad55',
                'neutral': '#a0aec0'
            };
            return colors[emotion] || '#718096';
        },

        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN');
        },

        formatDateTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-CN');
        },

        // 下载报告
        downloadReport() {
            if (!this.comprehensiveReport) return;

            // 生成PDF或Excel报告
            const reportContent = this.generateReportContent();
            const blob = new Blob([reportContent], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `心理评估报告_${this.comprehensiveReport.id}.html`;
            a.click();
            URL.revokeObjectURL(url);
        },

        generateReportContent() {
            // 生成HTML格式的报告
            return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>司法心理评估报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
        h1 { color: #00d4ff; text-align: center; }
        .section { margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .label { font-weight: bold; }
        .value { color: #00d4ff; font-size: 1.2em; }
        .recommendations { background: #e8f4f8; padding: 15px; border-left: 4px solid #00d4ff; }
        .timestamp { text-align: right; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>司法心理评估报告</h1>
    
    <div class="section">
        <h2>基本信息</h2>
        <div class="metric">
            <span class="label">报告编号：</span>
            <span class="value">${this.comprehensiveReport.id}</span>
        </div>
        <div class="metric">
            <span class="label">生成时间：</span>
            <span class="value">${this.formatDateTime(this.comprehensiveReport.timestamp)}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>评估结果</h2>
        <div class="metric">
            <span class="label">情感强度指数：</span>
            <span class="value">${this.comprehensiveReport.emotion_intensity_index}</span>
        </div>
        <div class="metric">
            <span class="label">心理风险等级：</span>
            <span class="value">${this.comprehensiveReport.risk_level}</span>
        </div>
        <div class="metric">
            <span class="label">沟通状态：</span>
            <span class="value">${this.comprehensiveReport.communication_assessment}</span>
        </div>
    </div>
    
    <div class="section recommendations">
        <h2>专业建议</h2>
        <ul>
            ${this.comprehensiveReport.recommendations.map(rec => 
                `<li>${rec.content}</li>`
            ).join('')}
        </ul>
    </div>
    
    <div class="timestamp">
        本报告由司法心理情感计算分析系统自动生成
    </div>
</body>
</html>
            `;
        },

        // 分享报告
        shareReport() {
            if (!this.comprehensiveReport) return;

            // 实现分享功能（例如生成分享链接）
            const shareUrl = `${window.location.origin}/report/${this.comprehensiveReport.id}`;

            if (navigator.share) {
                navigator.share({
                    title: '司法心理评估报告',
                    text: `报告编号：${this.comprehensiveReport.id}`,
                    url: shareUrl
                });
            } else {
                // 复制到剪贴板
                navigator.clipboard.writeText(shareUrl);
                alert('分享链接已复制到剪贴板');
            }
        },

        // 打印报告
        printReport() {
            if (!this.comprehensiveReport) return;

            const printWindow = window.open('', '_blank');
            printWindow.document.write(this.generateReportContent());
            printWindow.document.close();
            printWindow.print();
        },

        // 保存设置
        saveSettings() {
            localStorage.setItem('jpa_settings', JSON.stringify(this.settings));
            alert('设置已保存');
        },

        // 重置设置
        resetSettings() {
            this.settings = {
                emotionThreshold: 60,
                riskLevel: 'medium',
                anonymizeData: true,
                encryptStorage: false
            };
            this.saveSettings();
        },

        // 助手功能
        toggleAssistant() {
            this.assistantExpanded = !this.assistantExpanded;
            if (this.assistantExpanded && this.assistantMessages.length === 0) {
                this.assistantMessages.push({
                    id: 'MSG' + Date.now(),
                    type: 'bot',
                    text: '您好！我是您的智能助手，有什么可以帮助您的吗？',
                    timestamp: new Date()
                });
            }
        },

        sendAssistantQuery() {
            if (!this.assistantQuery.trim()) return;

            // 添加用户消息
            this.assistantMessages.push({
                id: 'MSG' + Date.now(),
                type: 'user',
                text: this.assistantQuery,
                timestamp: new Date()
            });

            // 模拟AI响应
            setTimeout(() => {
                const response = this.generateAssistantResponse(this.assistantQuery);
                this.assistantMessages.push({
                    id: 'MSG' + Date.now(),
                    type: 'bot',
                    text: response,
                    timestamp: new Date()
                });

                // 滚动到底部
                this.$nextTick(() => {
                    const messagesContainer = document.querySelector('.assistant-messages');
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                });
            }, 1000);

            this.assistantQuery = '';
        },

        generateAssistantResponse(query) {
            // 简单的关键词匹配响应
            const lowerQuery = query.toLowerCase();

            if (lowerQuery.includes('情感') || lowerQuery.includes('强度')) {
                return `当前情感强度指数为${this.emotionIntensity}，处于${this.intensityStatus}状态。这表明被分析者的情绪状态相对稳定。`;
            } else if (lowerQuery.includes('风险') || lowerQuery.includes('预警')) {
                return `系统检测到${this.riskWarnings.length}个风险预警。最需要关注的是${this.riskWarnings[0]?.type || '暂无风险'}。建议采取相应的干预措施。`;
            } else if (lowerQuery.includes('建议') || lowerQuery.includes('干预')) {
                return '基于当前的分析结果，系统建议：1) 保持定期的心理健康评估；2) 在情绪波动较大时及时介入；3) 提供必要的心理支持资源。';
            } else if (lowerQuery.includes('使用') || lowerQuery.includes('帮助')) {
                return '您可以通过以下步骤使用系统：1) 在实时分析页面采集多模态数据；2) 系统会自动分析并显示结果；3) 查看仪表盘了解整体状态；4) 生成综合报告获取专业建议。';
            } else {
                return '我理解您的问题。请您提供更多细节，或者询问关于情感分析、风险评估、干预建议等具体内容，我会为您提供更准确的帮助。';
            }
        }
    }
}).mount('#app');

