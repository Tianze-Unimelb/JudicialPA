const { createApp } = Vue;

createApp({
    data() {
        return {
            // 视图控制
            currentView: 'dashboard',

            // 仪表盘数据
            emotionIntensity: 65,
            intensityLevel: 'warning',
            intensityStatus: '情绪波动中等',

            emotionDistribution: {
                happy: 25,
                sad: 15,
                angry: 10,
                fear: 20,
                surprise: 5,
                neutral: 25
            },

            riskWarnings: [
                {
                    id: 1,
                    type: '焦虑风险',
                    description: '检测到轻度焦虑迹象，建议持续观察',
                    level: 'warning',
                    timestamp: new Date()
                }
            ],

            interventionSuggestions: {
                immediate: [
                    { action: '提供情绪支持和倾听', priority: 'high' },
                    { action: '创造安全舒适的环境', priority: 'high' }
                ],
                short_term: [
                    { action: '定期心理评估', priority: 'medium' },
                    { action: '压力管理技巧培训', priority: 'medium' }
                ]
            },

            // 分析数据
            cameraActive: false,
            isRecording: false,
            recordingTime: 0,
            textInput: '',

            faceEmotions: null,
            voiceAnalysis: null,
            textAnalysis: null,
            comprehensiveReport: null,

            // 设置
            settings: {
                emotionThreshold: 60,
                riskLevel: 'medium',
                anonymizeData: true,
                encryptStorage: false
            },

            // 图表实例
            gaugeChart: null,
            radarChart: null,

            // 音频相关
            mediaRecorder: null,
            audioChunks: [],
            audioData: null,
            recordingTimer: null
        };
    },

    mounted() {
        // 初始化图表
        this.$nextTick(() => {
            this.initCharts();
        });

        // 模拟数据更新
        this.startDataSimulation();
    },

    methods: {
        // 切换视图
        switchView(view) {
            this.currentView = view;
            if (view === 'dashboard') {
                this.$nextTick(() => {
                    this.initCharts();
                });
            }
        },

        // 初始化图表
        initCharts() {
            this.initGaugeChart();
            this.initRadarChart();
        },

        // 初始化仪表盘图表
        initGaugeChart() {
            if (this.$refs.gaugeChart) {
                const chartDom = this.$refs.gaugeChart;
                this.gaugeChart = echarts.init(chartDom);

                const option = {
                    series: [{
                        type: 'gauge',
                        startAngle: 180,
                        endAngle: 0,
                        min: 0,
                        max: 100,
                        splitNumber: 10,
                        axisLine: {
                            lineStyle: {
                                width: 20,
                                color: [
                                    [0.3, '#4facfe'],
                                    [0.7, '#fa709a'],
                                    [1, '#f5576c']
                                ]
                            }
                        },
                        pointer: {
                            itemStyle: {
                                color: '#667eea'
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
                            length: 20,
                            lineStyle: {
                                color: '#fff',
                                width: 3
                            }
                        },
                        axisLabel: {
                            color: 'auto',
                            distance: 35,
                            fontSize: 14
                        },
                        detail: {
                            valueAnimation: true,
                            formatter: '{value}',
                            color: 'auto',
                            fontSize: 24,
                            offsetCenter: [0, '-20%']
                        },
                        data: [{
                            value: this.emotionIntensity
                        }]
                    }]
                };

                this.gaugeChart.setOption(option);
            }
        },

        // 初始化雷达图
        initRadarChart() {
            if (this.$refs.radarChart) {
                const chartDom = this.$refs.radarChart;
                this.radarChart = echarts.init(chartDom);

                const option = {
                    radar: {
                        indicator: [
                            { name: '情绪稳定', max: 100 },
                            { name: '压力水平', max: 100 },
                            { name: '焦虑程度', max: 100 },
                            { name: '抑郁风险', max: 100 },
                            { name: '认知清晰', max: 100 },
                            { name: '社交适应', max: 100 }
                        ],
                        axisName: {
                            color: '#a0aec0'
                        },
                        splitLine: {
                            lineStyle: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        splitArea: {
                            areaStyle: {
                                color: ['rgba(102, 126, 234, 0.1)', 'rgba(102, 126, 234, 0.05)']
                            }
                        }
                    },
                    series: [{
                        type: 'radar',
                        data: [{
                            value: [80, 30, 40, 20, 90, 70],
                            name: '心理状态',
                            lineStyle: {
                                color: '#667eea',
                                width: 2
                            },
                            areaStyle: {
                                color: 'rgba(102, 126, 234, 0.3)'
                            }
                        }]
                    }]
                };

                this.radarChart.setOption(option);
            }
        },

        // 开始数据模拟
        startDataSimulation() {
            setInterval(() => {
                // 更新情感强度
                this.emotionIntensity = Math.floor(Math.random() * 30) + 50;
                this.updateIntensityStatus();

                // 更新情绪分布
                const emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'neutral'];
                emotions.forEach(emotion => {
                    this.emotionDistribution[emotion] = Math.floor(Math.random() * 40) + 10;
                });

                // 更新图表
                if (this.gaugeChart) {
                    this.gaugeChart.setOption({
                        series: [{
                            data: [{ value: this.emotionIntensity }]
                        }]
                    });
                }
            }, 3000);
        },

        // 更新强度状态
        updateIntensityStatus() {
            if (this.emotionIntensity < 30) {
                this.intensityLevel = 'success';
                this.intensityStatus = '情绪稳定';
            } else if (this.emotionIntensity < 70) {
                this.intensityLevel = 'warning';
                this.intensityStatus = '情绪波动中等';
            } else {
                this.intensityLevel = 'danger';
                this.intensityStatus = '情绪波动剧烈';
            }
        },

        // 翻译方法
        translateEmotion(emotion) {
            const translations = {
                'happy': '快乐',
                'sad': '悲伤',
                'angry': '愤怒',
                'fear': '恐惧',
                'surprise': '惊讶',
                'neutral': '平静'
            };
            return translations[emotion] || emotion;
        },

        translateInterventionType(type) {
            const translations = {
                'immediate': '立即干预',
                'short_term': '短期建议',
                'long_term': '长期规划'
            };
            return translations[type] || type;
        },

        // 摄像头控制
        async toggleCamera() {
            if (this.cameraActive) {
                this.stopCamera();
            } else {
                await this.startCamera();
            }
        },

        async startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = this.$refs.videoElement;
                video.srcObject = stream;
                this.cameraActive = true;
            } catch (error) {
                console.error('Camera error:', error);
                alert('无法访问摄像头');
            }
        },

        stopCamera() {
            const video = this.$refs.videoElement;
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }
            this.cameraActive = false;
        },

        captureFrame() {
            // 模拟捕获结果
            this.faceEmotions = {
                emotions: {
                    happy: 0.3,
                    sad: 0.1,
                    neutral: 0.5,
                    surprise: 0.1
                }
            };
        },

        // 录音控制
        async toggleRecording() {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                await this.startRecording();
            }
        },

        async startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.audioChunks = [];

                this.mediaRecorder.ondataavailable = (event) => {
                    this.audioChunks.push(event.data);
                };

                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.audioData = audioBlob;
                    // 模拟分析结果
                    this.voiceAnalysis = {
                        pitch: { type: '正常' },
                        volume: { level: '中等' },
                        speed: { type: '适中' }
                    };
                };

                this.mediaRecorder.start();
                this.isRecording = true;
                this.startRecordingTimer();

                // 音频可视化
                this.startAudioVisualization(stream);
            } catch (error) {
                console.error('Recording error:', error);
                alert('无法访问麦克风');
            }
        },

        stopRecording() {
            if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
                this.mediaRecorder.stop();
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            this.isRecording = false;
            this.stopRecordingTimer();
        },

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

        startAudioVisualization(stream) {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);
            const dataArray = new Uint8Array(analyser.frequencyBinCount);

            microphone.connect(analyser);

            const visualizer = this.$refs.audioVisualizer;
            const canvas = document.createElement('canvas');
            canvas.width = visualizer.offsetWidth;
            canvas.height = visualizer.offsetHeight;
            visualizer.innerHTML = '';
            visualizer.appendChild(canvas);

            const canvasCtx = canvas.getContext('2d');

            const draw = () => {
                if (!this.isRecording) {
                    visualizer.innerHTML = '';
                    return;
                }

                requestAnimationFrame(draw);

                analyser.getByteFrequencyData(dataArray);

                canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

                const barWidth = (canvas.width / dataArray.length) * 2.5;
                let barHeight;
                let x = 0;

                for (let i = 0; i < dataArray.length; i++) {
                    barHeight = dataArray[i] / 2;

                    const gradient = canvasCtx.createLinearGradient(0, 0, 0, canvas.height);
                    gradient.addColorStop(0, '#667eea');
                    gradient.addColorStop(1, '#f093fb');

                    canvasCtx.fillStyle = gradient;
                    canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

                    x += barWidth + 1;
                }
            };

            draw();
        },

        playbackAudio() {
            if (this.audioData) {
                const audio = new Audio(URL.createObjectURL(this.audioData));
                audio.play();
            }
        },

        // 文本分析
        analyzeText() {
            if (!this.textInput.trim()) return;

            // 模拟分析结果
            this.textAnalysis = {
                overall: { label: 'POSITIVE' },
                consistency: 0.85,
                keywords: [
                    { word: '积极', emotion: 'positive' },
                    { word: '努力', emotion: 'positive' },
                    { word: '希望', emotion: 'positive' }
                ]
            };
        },

        clearText() {
            this.textInput = '';
            this.textAnalysis = null;
        },

        // 生成报告
        generateReport() {
            this.comprehensiveReport = {
                id: 'RPT' + Date.now(),
                timestamp: new Date(),
                emotion_intensity_index: this.emotionIntensity,
                risk_level: this.intensityLevel,
                communication_assessment: '沟通良好',
                recommendations: [
                    { id: 1, priority: 'high', content: '建议进行定期心理健康评估' },
                    { id: 2, priority: 'medium', content: '提供压力管理技巧培训' },
                    { id: 3, priority: 'low', content: '鼓励参与团体活动' }
                ]
            };

            this.switchView('reports');
        },

        // 报告操作
        downloadReport() {
            // 实现下载功能
            alert('报告下载功能');
        },

        printReport() {
            window.print();
        },

        shareReport() {
            // 实现分享功能
            alert('报告分享功能');
        },

        // 设置操作
        saveSettings() {
            localStorage.setItem('jpa_settings', JSON.stringify(this.settings));
            alert('设置已保存');
        },

        resetSettings() {
            this.settings = {
                emotionThreshold: 60,
                riskLevel: 'medium',
                anonymizeData: true,
                encryptStorage: false
            };
        },

        // 格式化时间
        formatDateTime(date) {
            return new Date(date).toLocaleString('zh-CN');
        }
    }
}).mount('#app');
