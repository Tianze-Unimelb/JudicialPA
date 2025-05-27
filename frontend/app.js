const { useState, useEffect, useRef } = React;
const { Layout, Menu, Button, Space, Typography, message, notification } = antd;
const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

// 主应用组件
function App() {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [currentSession, setCurrentSession] = useState(null);
    const [systemStats, setSystemStats] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    
    const menuItems = [
        { key: 'dashboard', icon: '📊', label: '实时分析仪表盘' },
        { key: 'session-setup', icon: '⚙️', label: '会话设置' },
        { key: 'detailed-analysis', icon: '🔍', label: '详细分析' },
        { key: 'reports', icon: '📝', label: '分析报告' },
        { key: 'case-management', icon: '📁', label: '案件管理' }
    ];
    
    useEffect(() => {
        loadSystemStats();
        // 每30秒更新系统状态
        const interval = setInterval(loadSystemStats, 30000);
        return () => clearInterval(interval);
    }, []);
    
    const loadSystemStats = async () => {
        try {
            const response = await fetch('/api/system/stats');
            if (response.ok) {
                const stats = await response.json();
                setSystemStats(stats);
            }
        } catch (error) {
            console.error('加载系统状态失败:', error);
        }
    };
    
    const handleEmergencyStop = async () => {
        if (currentSession) {
            try {
                setIsLoading(true);
                // 这里可以调用紧急停止API
                notification.warning({
                    message: '紧急停止',
                    description: `会话 ${currentSession} 已被紧急停止`
                });
                setCurrentSession(null);
            } catch (error) {
                message.error('紧急停止失败');
            } finally {
                setIsLoading(false);
            }
        } else {
            message.info('当前没有活动会话');
        }
    };
    
    const renderContent = () => {
        switch (currentPage) {
            case 'dashboard':
                return React.createElement(Dashboard, { 
                    sessionId: currentSession 
                });
            case 'session-setup':
                return React.createElement(SessionSetup, {
                    onSessionStart: (sessionId) => {
                        setCurrentSession(sessionId);
                        setCurrentPage('dashboard');
                        message.success(`会话 ${sessionId} 已启动`);
                    }
                });
            case 'detailed-analysis':
                return React.createElement(DetailedAnalysis, {
                    sessionId: currentSession
                });
            case 'reports':
                return React.createElement(ReportView, {
                    sessionId: currentSession
                });
            case 'case-management':
                return React.createElement(CaseManagement);
            default:
                return React.createElement('div', {
                    className: 'p-8 text-center'
                }, '页面开发中...');
        }
    };
    
    return React.createElement(Layout, {
        className: 'min-h-screen'
    }, [
        React.createElement(Header, {
            key: 'header',
            className: 'bg-white shadow-md border-b flex items-center justify-between px-6'
        }, [
            React.createElement(Title, {
                key: 'title',
                level: 3,
                className: 'text-primary mb-0'
            }, '司法心理情感计算分析系统'),
            React.createElement(Space, {
                key: 'actions'
            }, [
                React.createElement(Text, {
                    key: 'session-info',
                    type: 'secondary'
                }, currentSession ? `会话: ${currentSession.slice(-8)}` : '无活动会话'),
                React.createElement(Text, {
                    key: 'system-status',
                    type: 'secondary'
                }, `活动会话: ${systemStats.active_sessions || 0}`),
                React.createElement(Button, {
                    key: 'emergency',
                    danger: true,
                    size: 'small',
                    loading: isLoading,
                    onClick: handleEmergencyStop
                }, '紧急停止')
            ])
        ]),
        React.createElement(Layout, {
            key: 'main-layout'
        }, [
            React.createElement(Sider, {
                key: 'sider',
                width: 250,
                className: 'bg-white shadow-md'
            }, 
                React.createElement(Menu, {
                    mode: 'inline',
                    selectedKeys: [currentPage],
                    className: 'h-full border-r-0',
                    items: menuItems.map(item => ({
                        key: item.key,
                        icon: React.createElement('span', {}, item.icon),
                        label: item.label,
                        onClick: () => setCurrentPage(item.key)
                    }))
                })
            ),
            React.createElement(Content, {
                key: 'content',
                className: 'bg-gray-50 overflow-auto'
            }, renderContent())
        ])
    ]);
}

// 仪表盘组件
function Dashboard({ sessionId }) {
    const [realTimeData, setRealTimeData] = useState(null);
    const [alerts, setAlerts] = useState([]);
    
    useEffect(() => {
        if (sessionId) {
            loadRealTimeData();
            loadAlerts();
            
            // 每2秒更新实时数据
            const interval = setInterval(() => {
                loadRealTimeData();
                loadAlerts();
            }, 2000);
            
            return () => clearInterval(interval);
        }
    }, [sessionId]);
    
    const loadRealTimeData = async () => {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/realtime`);
            if (response.ok) {
                const data = await response.json();
                setRealTimeData(data);
            }
        } catch (error) {
            console.error('加载实时数据失败:', error);
        }
    };
    
    const loadAlerts = async () => {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/alerts`);
            if (response.ok) {
                const data = await response.json();
                setAlerts(data);
            }
        } catch (error) {
            console.error('加载预警数据失败:', error);
        }
    };
    
    if (!sessionId) {
        return React.createElement('div', {
            className: 'p-8 text-center'
        }, [
            React.createElement('h2', { key: 'title' }, '请先启动分析会话'),
            React.createElement('p', { key: 'desc' }, '前往会话设置页面创建新的分析任务')
        ]);
    }
    
    return React.createElement('div', {
        className: 'p-6 space-y-6'
    }, [
        React.createElement(RealTimeAnalysis, { 
            key: 'realtime', 
            sessionId, 
            data: realTimeData 
        }),
        React.createElement('div', {
            key: 'charts-grid',
            className: 'grid grid-cols-1 lg:grid-cols-2 gap-6'
        }, [
            React.createElement(PsychologicalRadar, { 
                key: 'radar', 
                sessionId,
                data: realTimeData?.radar_data 
            }),
            React.createElement(EmotionIntensityChart, { 
                key: 'emotion', 
                sessionId 
            })
        ]),
        React.createElement(ModalityAnalysisSummary, { 
            key: 'modality', 
            sessionId 
        }),
        React.createElement(TimelineView, { 
            key: 'timeline', 
            sessionId 
        }),
        React.createElement(AlertPanel, { 
            key: 'alerts', 
            sessionId,
            alerts 
        })
    ]);
}

// 其他组件的基本实现
function RealTimeAnalysis({ sessionId, data }) {
    const { Card, Row, Col, Badge, Progress, Typography } = antd;
    const { Title, Text } = Typography;
    
    return React.createElement(Card, {
        title: '实时数据监控',
        className: 'shadow-md',
        extra: React.createElement(Badge, {
            status: 'success',
            text: '连接正常'
        })
    }, 
        React.createElement(Row, { gutter: [16, 16] }, [
            React.createElement(Col, { key: 'video', span: 8 },
                React.createElement(Card, { size: 'small', title: '视频流状态' },
                    React.createElement('div', { className: 'text-center' }, [
                        React.createElement('div', {
                            key: 'preview',
                            className: 'w-full h-32 bg-gray-200 mb-4 rounded flex items-center justify-center'
                        }, React.createElement(Text, { type: 'secondary' }, '视频预览区域')),
                        React.createElement(Badge, {
                            key: 'status',
                            status: 'success',
                            text: '正在采集'
                        })
                    ])
                )
            ),
            React.createElement(Col, { key: 'audio', span: 8 },
                React.createElement(Card, { size: 'small', title: '音频流状态' },
                    React.createElement('div', { className: 'text-center' }, [
                        React.createElement('div', {
                            key: 'wave',
                            className: 'w-full h-32 bg-gray-200 mb-4 rounded flex items-center justify-center'
                        }, React.createElement(Text, { type: 'secondary' }, '音频波形显示')),
                        React.createElement(Badge, {
                            key: 'status',
                            status: 'success',
                            text: '正在采集'
                        })
                    ])
                )
            ),
            React.createElement(Col, { key: 'metrics', span: 8 },
                React.createElement(Card, { size: 'small', title: '当前指标' },
                    React.createElement('div', { className: 'space-y-4' }, [
                        React.createElement('div', { key: 'intensity' }, [
                            React.createElement(Text, { strong: true }, '情感强度'),
                            React.createElement(Progress, {
                                percent: data?.current_intensity || 0,
                                status: (data?.current_intensity || 0) > 70 ? 'exception' : 'active'
                            })
                        ]),
                        React.createElement('div', { key: 'micro' }, [
                            React.createElement(Text, { type: 'secondary' }, '最近微表情: '),
                            React.createElement(Text, { strong: true }, data?.latest_microexpression || '无')
                        ]),
                        React.createElement('div', { key: 'speech' }, [
                            React.createElement(Text, { type: 'secondary' }, '语音情感: '),
                            React.createElement(Text, { strong: true }, data?.latest_speech_emotion || '无')
                        ])
                    ])
                )
            )
        ])
    );
}

function PsychologicalRadar({ sessionId, data }) {
    const { Card } = antd;
    const chartRef = useRef(null);
    
    useEffect(() => {
        if (chartRef.current && data) {
            initRadarChart();
        }
    }, [data]);
    
    const initRadarChart = () => {
        const chart = echarts.init(chartRef.current);
        
        const option = {
            title: {
                text: '心理状态雷达图',
                left: 'center'
            },
            tooltip: {},
            radar: {
                indicator: [
                    { name: '紧张度', max: 100 },
                    { name: '焦虑度', max: 100 },
                    { name: '合作意愿', max: 100 },
                    { name: '冷静度', max: 100 },
                    { name: '防御程度', max: 100 },
                    { name: '可信度', max: 100 }
                ]
            },
            series: [{
                type: 'radar',
                data: [{
                    value: data ? Object.values(data) : [50, 50, 50, 50, 50, 50],
                    name: '当前状态'
                }]
            }]
        };
        
        chart.setOption(option);
    };
    
    return React.createElement(Card, { 
        title: '心理状态评估', 
        className: 'shadow-md' 
    },
        React.createElement('div', {
            ref: chartRef,
            className: 'w-full h-80'
        })
    );
}

function EmotionIntensityChart({ sessionId }) {
    const { Card } = antd;
    const chartRef = useRef(null);
    
    useEffect(() => {
        if (chartRef.current && sessionId) {
            loadChartData();
        }
    }, [sessionId]);
    
    const loadChartData = async () => {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/results`);
            if (response.ok) {
                const data = await response.json();
                initChart(data.emotion_intensity_time_series || []);
            }
        } catch (error) {
            console.error('加载图表数据失败:', error);
            initChart([]);
        }
    };
    
    const initChart = (data) => {
        const chart = echarts.init(chartRef.current);
        
        const option = {
            title: {
                text: '情感强度时间序列',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis'
            },
            xAxis: {
                type: 'category',
                data: data.map(item => new Date(item.timestamp).toLocaleTimeString())
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 100
            },
            series: [{
                type: 'line',
                smooth: true,
                data: data.map(item => item.intensity)
            }]
        };
        
        chart.setOption(option);
    };
    
    return React.createElement(Card, { 
        title: '情感强度监控', 
        className: 'shadow-md' 
    },
        React.createElement('div', {
            ref: chartRef,
            className: 'w-full h-80'
        })
    );
}

function ModalityAnalysisSummary({ sessionId }) {
    const { Card, Row, Col, Tag } = antd;
    
    return React.createElement(Card, { 
        title: '多模态分析摘要', 
        className: 'shadow-md' 
    },
        React.createElement(Row, { gutter: [16, 16] }, [
            React.createElement(Col, { key: 'micro', span: 8 },
                React.createElement(Card, { 
                    size: 'small', 
                    title: '微表情分析',
                    className: 'h-full'
                },
                    React.createElement('div', { className: 'space-y-2' }, [
                        React.createElement('div', { key: '1' }, '最近检测: 惊讶'),
                        React.createElement('div', { key: '2' }, '总计事件: 8次'),
                        React.createElement('div', { key: '3' }, '平均强度: 0.72')
                    ])
                )
            ),
            React.createElement(Col, { key: 'speech', span: 8 },
                React.createElement(Card, { 
                    size: 'small', 
                    title: '语音情感分析',
                    className: 'h-full'
                },
                    React.createElement('div', { className: 'space-y-2' }, [
                        React.createElement('div', { key: '1' }, '当前情感: 紧张'),
                        React.createElement('div', { key: '2' }, '语调变化: 频繁'),
                        React.createElement('div', { key: '3' }, '语速: 偏快')
                    ])
                )
            ),
            React.createElement(Col, { key: 'text', span: 8 },
                React.createElement(Card, { 
                    size: 'small', 
                    title: '文本情感分析',
                    className: 'h-full'
                },
                    React.createElement('div', { className: 'space-y-2' }, [
                        React.createElement('div', { key: '1' }, '整体极性: 中性偏负'),
                        React.createElement('div', { key: '2' }, '关键词: 困难、担心'),
                        React.createElement('div', { key: '3' }, '置信度: 0.84')
                    ])
                )
            )
        ])
    );
}

function TimelineView({ sessionId }) {
    const { Card, Slider, Button, Space } = antd;
    const [currentTime, setCurrentTime] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    
    return React.createElement(Card, { 
        title: '时间轴整合视图', 
        className: 'shadow-md' 
    },
        React.createElement('div', { className: 'space-y-4' }, [
            React.createElement('div', { 
                key: 'controls',
                className: 'flex items-center justify-between' 
            }, [
                React.createElement(Space, { key: 'play-controls' }, [
                    React.createElement(Button, {
                        type: 'primary',
                        onClick: () => setIsPlaying(!isPlaying)
                    }, isPlaying ? '⏸️ 暂停' : '▶️ 播放'),
                    React.createElement(Button, {
                        onClick: () => setCurrentTime(0)
                    }, '⏮️ 重置')
                ]),
                React.createElement(Space, { key: 'tools' }, [
                    React.createElement(Button, { size: 'small' }, '🔍 缩放'),
                    React.createElement(Button, { size: 'small' }, '📝 标注')
                ])
            ]),
            React.createElement(Slider, {
                key: 'timeline',
                min: 0,
                max: 300,
                value: currentTime,
                onChange: setCurrentTime
            }),
            React.createElement('div', {
                key: 'info',
                className: 'bg-blue-50 p-4 rounded-lg'
            }, 
                React.createElement('h4', { className: 'font-semibold mb-2' }, 
                    `当前时间点信息 (${Math.floor(currentTime / 60)}:${(currentTime % 60).toString().padStart(2, '0')})`
                ),
                React.createElement('div', { className: 'grid grid-cols-3 gap-4 text-sm' }, [
                    React.createElement('div', { key: '1' }, '微表情: 平静'),
                    React.createElement('div', { key: '2' }, '语音情感: 中性'),
                    React.createElement('div', { key: '3' }, '情感强度: 42/100')
                ])
            )
        ])
    );
}

function AlertPanel({ sessionId, alerts }) {
    const { Card, Alert, List, Badge, Button, Space, Tag } = antd;
    
    const acknowledgeAlert = async (alertId) => {
        try {
            const response = await fetch(`/api/alerts/${alertId}/acknowledge`, {
                method: 'POST'
            });
            if (response.ok) {
                message.success('预警已确认');
                // 这里可以刷新alerts数据
            }
        } catch (error) {
            message.error('确认预警失败');
        }
    };
    
    return React.createElement(Card, {
        title: '预警与提示',
        className: 'shadow-md',
        extra: React.createElement(Badge, {
            count: alerts?.filter(a => a.status === 'active').length || 0
        }, React.createElement(Button, { size: 'small' }, '实时预警'))
    },
        React.createElement('div', { className: 'space-y-3' }, [
            React.createElement('div', {
                key: 'system-status',
                className: 'bg-green-50 p-3 rounded-lg border border-green-200'
            }, [
                React.createElement('div', { 
                    key: 'status-title',
                    className: 'flex items-center gap-2 mb-2' 
                }, [
                    React.createElement(Badge, { status: 'success' }),
                    React.createElement('span', { className: 'font-medium' }, '系统运行状态')
                ]),
                React.createElement('div', { 
                    key: 'status-info',
                    className: 'text-sm' 
                }, '数据连接正常 | 模型运行中 | 分析进度正常')
            ]),
            alerts && alerts.length > 0 
                ? React.createElement(List, {
                    key: 'alerts-list',
                    size: 'small',
                    dataSource: alerts,
                    renderItem: item => React.createElement(List.Item, {
                        className: `p-3 rounded-lg border ${
                            item.status === 'active' 
                                ? 'bg-white border-gray-200' 
                                : 'bg-gray-50 border-gray-100'
                        }`
                    }, 
                        React.createElement('div', { className: 'w-full' }, [
                            React.createElement('div', {
                                key: 'header',
                                className: 'flex items-start justify-between mb-2'
                            }, [
                                React.createElement('div', { 
                                    key: 'title',
                                    className: 'flex items-center gap-2' 
                                }, [
                                    React.createElement('span', {}, '⚠️'),
                                    React.createElement('div', {}, [
                                        React.createElement('div', { 
                                            className: 'font-medium' 
                                        }, item.title),
                                        React.createElement(Tag, { 
                                            color: item.level === 'high' ? 'red' : 'orange',
                                            size: 'small'
                                        }, `${item.level} 级别`)
                                    ])
                                ]),
                                React.createElement('div', { 
                                    key: 'time',
                                    className: 'text-xs text-gray-500' 
                                }, item.time)
                            ]),
                            React.createElement('div', {
                                key: 'description',
                                className: 'text-sm text-gray-600 mb-2'
                            }, item.description),
                            item.status === 'active' && React.createElement('div', {
                                key: 'action',
                                className: 'flex justify-end'
                            }, 
                                React.createElement(Button, {
                                    size: 'small',
                                    type: 'link',
                                    onClick: () => acknowledgeAlert(item.id)
                                }, '确认处理')
                            )
                        ])
                    )
                })
                : React.createElement('div', {
                    key: 'no-alerts',
                    className: 'text-center py-8 text-gray-400'
                }, '暂无预警信息')
        ])
    );
}

// 会话设置组件
function SessionSetup({ onSessionStart }) {
    const { Card, Form, Input, Select, Upload, Button, Steps, Typography, Row, Col, Radio, message } = antd;
    const { Title, Text } = Typography;
    const { Dragger } = Upload;
    const [currentStep, setCurrentStep] = useState(0);
    const [form] = Form.useForm();
    const [analysisType, setAnalysisType] = useState('upload');
    const [isStarting, setIsStarting] = useState(false);
    
    const steps = [
        { title: '基本信息', description: '输入案件和当事人信息' },
        { title: '数据源配置', description: '选择数据输入方式' },
        { title: '分析设置', description: '配置分析参数' }
    ];
    
    const handleNext = async () => {
        try {
            await form.validateFields();
            setCurrentStep(currentStep + 1);
        } catch (error) {
            message.error('请完善必填信息');
        }
    };
    
    const handleStartAnalysis = async () => {
        try {
            setIsStarting(true);
            const values = await form.validateFields();
            
            // 准备FormData
            const formData = new FormData();
            formData.append('case_id', values.case_id || 1);
            formData.append('subject_id', values.subject_id || 1);
            
            // 添加文件
            if (values.files && values.files.fileList) {
                values.files.fileList.forEach(file => {
                    if (file.originFileObj) {
                        formData.append('files', file.originFileObj);
                    }
                });
            }
            
            const response = await fetch('/api/sessions/start', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                onSessionStart(result.session_id);
            } else {
                throw new Error('启动分析失败');
            }
            
        } catch (error) {
            console.error('启动分析失败:', error);
            message.error('启动分析失败，请检查输入信息');
        } finally {
            setIsStarting(false);
        }
    };
    
    const renderStepContent = () => {
        switch (currentStep) {
            case 0:
                return React.createElement('div', { className: 'space-y-6' }, [
                    React.createElement(Row, { key: 'row1', gutter: 16 }, [
                        React.createElement(Col, { span: 12 },
                            React.createElement(Form.Item, {
                                label: '案件编号',
                                name: 'case_number',
                                rules: [{ required: true, message: '请输入案件编号' }]
                            }, React.createElement(Input, { placeholder: '例如：CASE-2024-001' }))
                        ),
                        React.createElement(Col, { span: 12 },
                            React.createElement(Form.Item, {
                                label: '当事人姓名',
                                name: 'subject_name',
                                rules: [{ required: true, message: '请输入当事人姓名' }]
                            }, React.createElement(Input, { placeholder: '请输入姓名' }))
                        )
                    ]),
                    React.createElement(Form.Item, {
                        key: 'title',
                        label: '案件标题',
                        name: 'case_title'
                    }, React.createElement(Input, { placeholder: '请输入案件标题' })),
                    React.createElement(Form.Item, {
                        key: 'role',
                        label: '当事人角色',
                        name: 'subject_role'
                    }, React.createElement(Select, { placeholder: '请选择当事人角色' }, [
                        React.createElement(Select.Option, { key: 'suspect', value: 'suspect' }, '犯罪嫌疑人'),
                        React.createElement(Select.Option, { key: 'witness', value: 'witness' }, '证人'),
                        React.createElement(Select.Option, { key: 'victim', value: 'victim' }, '受害人'),
                        React.createElement(Select.Option, { key: 'other', value: 'other' }, '其他')
                    ])),
                    React.createElement(Form.Item, {
                        key: 'description',
                        label: '备注说明',
                        name: 'description'
                    }, React.createElement(Input.TextArea, { 
                        rows: 3, 
                        placeholder: '请输入相关说明' 
                    }))
                ]);
                
            case 1:
                return React.createElement('div', { className: 'space-y-6' }, [
                    React.createElement(Form.Item, {
                        key: 'type',
                        label: '分析类型',
                        name: 'analysis_type'
                    }, React.createElement(Radio.Group, {
                        value: analysisType,
                        onChange: (e) => setAnalysisType(e.target.value)
                    }, [
                        React.createElement(Radio, { key: 'upload', value: 'upload' }, '上传文件分析'),
                        React.createElement(Radio, { key: 'realtime', value: 'realtime' }, '实时采集分析')
                    ])),
                    
                    analysisType === 'upload' && React.createElement(Form.Item, {
                        key: 'files',
                        label: '上传文件',
                        name: 'files'
                    }, React.createElement(Dragger, {
                        multiple: true,
                        accept: '.mp4,.avi,.wav,.mp3,.txt,.docx',
                        beforeUpload: () => false,
                        className: 'h-32'
                    }, [
                        React.createElement('p', { key: 'icon', className: 'text-4xl mb-2' }, '📁'),
                        React.createElement('p', { key: 'hint', className: 'text-base' }, '点击或拖拽文件到此区域上传'),
                        React.createElement('p', { key: 'desc', className: 'text-sm text-gray-500' }, '支持视频、音频、文本文件')
                    ])),
                    
                    analysisType === 'realtime' && React.createElement('div', {
                        key: 'devices',
                        className: 'bg-blue-50 p-4 rounded-lg'
                    }, [
                        React.createElement(Title, { key: 'title', level: 4 }, '设备检测'),
                        React.createElement('div', { key: 'list', className: 'space-y-3' }, [
                            React.createElement('div', { key: 'camera', className: 'flex items-center justify-between' }, [
                                React.createElement(Text, {}, '摄像头设备'),
                                React.createElement(Button, { size: 'small', type: 'link' }, '检测设备')
                            ]),
                            React.createElement('div', { key: 'audio', className: 'flex items-center justify-between' }, [
                                React.createElement(Text, {}, '音频设备'),
                                React.createElement(Button, { size: 'small', type: 'link' }, '检测设备')
                            ])
                        ])
                    ])
                ]);
                
            case 2:
                return React.createElement('div', { className: 'space-y-6' }, [
                    React.createElement(Row, { key: 'settings', gutter: 16 }, [
                        React.createElement(Col, { span: 12 },
                            React.createElement(Form.Item, {
                                label: '情感强度阈值',
                                name: 'intensity_threshold',
                                initialValue: 70
                            }, React.createElement(Select, {}, [
                                React.createElement(Select.Option, { value: 60 }, '60 (低敏感度)'),
                                React.createElement(Select.Option, { value: 70 }, '70 (中等敏感度)'),
                                React.createElement(Select.Option, { value: 80 }, '80 (高敏感度)')
                            ]))
                        ),
                        React.createElement(Col, { span: 12 },
                            React.createElement(Form.Item, {
                                label: '风险预警级别',
                                name: 'risk_level',
                                initialValue: 'medium'
                            }, React.createElement(Select, {}, [
                                React.createElement(Select.Option, { value: 'low' }, '仅高风险'),
                                React.createElement(Select.Option, { value: 'medium' }, '中高风险'),
                                React.createElement(Select.Option, { value: 'high' }, '全部风险')
                            ]))
                        )
                    ]),
                    React.createElement(Form.Item, {
                        key: 'modules',
                        label: '启用的分析模块',
                        name: 'analysis_modules',
                        initialValue: ['microexpression', 'speech', 'text']
                    }, React.createElement(Select, { 
                        mode: 'multiple', 
                        placeholder: '请选择分析模块' 
                    }, [
                        React.createElement(Select.Option, { value: 'microexpression' }, '微表情分析'),
                        React.createElement(Select.Option, { value: 'speech' }, '语音情感分析'),
                        React.createElement(Select.Option, { value: 'text' }, '文本情感分析'),
                        React.createElement(Select.Option, { value: 'physiology' }, '生理信号分析')
                    ])),
                    React.createElement('div', {
                        key: 'model-status',
                        className: 'bg-yellow-50 p-4 rounded-lg'
                    }, [
                        React.createElement(Title, { key: 'title', level: 4 }, '模型配置确认'),
                        React.createElement('div', { 
                            key: 'info',
                            className: 'grid grid-cols-2 gap-4 text-sm' 
                        }, [
                            React.createElement('div', { key: '1' }, '微表情模型: v2.1 (活跃)'),
                            React.createElement('div', { key: '2' }, '语音情感模型: v1.8 (活跃)'),
                            React.createElement('div', { key: '3' }, '文本分析模型: v3.2 (活跃)'),
                            React.createElement('div', { key: '4' }, '融合评估模型: v1.5 (活跃)')
                        ])
                    ])
                ]);
                
            default:
                return null;
        }
    };
    
    return React.createElement('div', { className: 'p-6 max-w-4xl mx-auto' },
        React.createElement(Card, { className: 'shadow-lg' }, [
            React.createElement('div', { key: 'header', className: 'mb-8' }, [
                React.createElement(Title, { 
                    level: 2, 
                    className: 'text-center mb-2' 
                }, '新建分析会话'),
                React.createElement(Text, { 
                    type: 'secondary',
                    className: 'block text-center' 
                }, '配置分析参数并启动心理情感计算分析')
            ]),
            React.createElement(Steps, { 
                key: 'steps',
                current: currentStep, 
                items: steps, 
                className: 'mb-8' 
            }),
            React.createElement(Form, {
                key: 'form',
                form: form,
                layout: 'vertical',
                className: 'min-h-96'
            }, renderStepContent()),
            React.createElement('div', { 
                key: 'actions',
                className: 'flex justify-between mt-8 pt-6 border-t border-gray-200' 
            }, [
                React.createElement('div', { key: 'prev' },
                    currentStep > 0 && React.createElement(Button, {
                        onClick: () => setCurrentStep(currentStep - 1)
                    }, '上一步')
                ),
                React.createElement('div', { key: 'next' },
                    currentStep < steps.length - 1 
                        ? React.createElement(Button, {
                            type: 'primary',
                            onClick: handleNext
                        }, '下一步')
                        : React.createElement(Button, {
                            type: 'primary',
                            size: 'large',
                            loading: isStarting,
                            onClick: handleStartAnalysis
                        }, '🚀 开始分析')
                )
            ])
        ])
    );
}

// 详细分析组件
function DetailedAnalysis({ sessionId }) {
    const { Card, Tabs, Typography } = antd;
    const { Title } = Typography;
    
    if (!sessionId) {
        return React.createElement('div', {
            className: 'p-8 text-center'
        }, [
            React.createElement('h2', { key: 'title' }, '请选择要分析的会话'),
            React.createElement('p', { key: 'desc' }, '先启动或选择一个分析会话')
        ]);
    }
    
    const tabItems = [
        {
            key: 'microexpression',
            label: '微表情详情',
            children: React.createElement('div', {},
                React.createElement('p', {}, '微表情分析详情内容开发中...')
            )
        },
        {
            key: 'speech',
            label: '语音情感详情', 
            children: React.createElement('div', {},
                React.createElement('p', {}, '语音情感分析详情内容开发中...')
            )
        },
        {
            key: 'text',
            label: '文本情感详情',
            children: React.createElement('div', {},
                React.createElement('p', {}, '文本情感分析详情内容开发中...')
            )
        }
    ];
    
    return React.createElement('div', { className: 'p-6' },
        React.createElement(Card, { className: 'shadow-md' }, [
            React.createElement(Title, { 
                key: 'title',
                level: 2, 
                className: 'm-0 mb-6' 
            }, '详细分析视图'),
            React.createElement(Tabs, {
                key: 'tabs',
                defaultActiveKey: 'microexpression',
                items: tabItems
            })
        ])
    );
}

// 报告视图组件
function ReportView({ sessionId }) {
    const { Card, Button, Space, Descriptions, Typography } = antd;
    const { Title, Paragraph, Text } = Typography;
    const [reportData, setReportData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    
    useEffect(() => {
        if (sessionId) {
            loadReport();
        }
    }, [sessionId]);
    
    const loadReport = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`/api/sessions/${sessionId}/report`);
            if (response.ok) {
                const data = await response.json();
                setReportData(data.report_data);
            }
        } catch (error) {
            console.error('加载报告失败:', error);
            message.error('加载报告失败');
        } finally {
            setIsLoading(false);
        }
    };
    
    if (!sessionId) {
        return React.createElement('div', {
            className: 'p-8 text-center'
        }, [
            React.createElement('h2', { key: 'title' }, '请选择要查看的会话'),
            React.createElement('p', { key: 'desc' }, '先启动或选择一个分析会话')
        ]);
    }
    
    if (isLoading) {
        return React.createElement('div', {
            className: 'p-8 text-center'
        }, '正在加载报告...');
    }
    
    if (!reportData) {
        return React.createElement('div', {
            className: 'p-8 text-center'
        }, [
            React.createElement('h2', { key: 'title' }, '报告生成中'),
            React.createElement('p', { key: 'desc' }, '请等待分析完成后查看报告'),
            React.createElement(Button, {
                key: 'refresh',
                type: 'primary',
                onClick: loadReport
            }, '刷新状态')
        ]);
    }
    
    return React.createElement('div', { className: 'p-6 max-w-6xl mx-auto space-y-6' }, [
        React.createElement(Card, { key: 'header', className: 'shadow-md' }, [
            React.createElement('div', {
                key: 'title-section',
                className: 'flex items-center justify-between mb-4'
            }, [
                React.createElement(Title, { level: 2, className: 'm-0' }, '司法心理情感分析报告'),
                React.createElement(Space, {}, [
                    React.createElement(Button, { type: 'primary', onClick: loadReport }, '刷新报告'),
                    React.createElement(Button, {}, '导出PDF')
                ])
            ]),
            reportData.header && React.createElement(Descriptions, {
                key: 'header-info',
                column: 2,
                bordered: true,
                size: 'small'
            }, [
                React.createElement(Descriptions.Item, { 
                    key: 'case',
                    label: '案件编号' 
                }, reportData.header.case_number),
                React.createElement(Descriptions.Item, { 
                    key: 'subject', 
                    label: '当事人' 
                }, reportData.header.subject_name),
                React.createElement(Descriptions.Item, { 
                    key: 'session',
                    label: '会话ID' 
                }, reportData.header.analysis_session_id),
                React.createElement(Descriptions.Item, { 
                    key: 'analyst',
                    label: '分析员' 
                }, reportData.header.analyst)
            ])
        ]),
        React.createElement(Card, { 
            key: 'summary',
            title: '整体心理状态摘要', 
            className: 'shadow-md' 
        }, 
            React.createElement(Paragraph, { 
                className: 'text-gray-700 leading-relaxed' 
            }, reportData.summary || '暂无摘要信息')
        ),
        React.createElement(Card, { 
            key: 'emotion-analysis',
            title: '情感强度分析', 
            className: 'shadow-md' 
        }, [
            React.createElement('div', {
                key: 'chart',
                className: 'h-64 bg-gray-100 rounded-lg flex items-center justify-center mb-4'
            }, React.createElement(Text, { type: 'secondary' }, '情感强度图表区域')),
            reportData.emotion_intensity_analysis && React.createElement('div', {
                key: 'stats',
                className: 'grid grid-cols-3 gap-4 text-sm'
            }, [
                React.createElement('div', { key: 'avg' }, 
                    `平均强度: ${reportData.emotion_intensity_analysis.average_intensity?.toFixed(1) || 'N/A'}`
                ),
                React.createElement('div', { key: 'peak' }, 
                    `峰值强度: ${reportData.emotion_intensity_analysis.peak_intensity?.toFixed(1) || 'N/A'}`
                ),
                React.createElement('div', { key: 'points' }, 
                    `数据点数: ${reportData.emotion_intensity_analysis.time_series_data?.length || 0}`
                )
            ])
        ]),
        React.createElement(Card, { 
            key: 'radar',
            title: '心理状态雷达图', 
            className: 'shadow-md' 
        },
            React.createElement('div', {
                className: 'h-64 bg-gray-100 rounded-lg flex items-center justify-center'
            }, React.createElement(Text, { type: 'secondary' }, '心理状态雷达图区域'))
        ),
        React.createElement(Card, { 
            key: 'disclaimer',
            className: 'shadow-md' 
        }, [
            React.createElement('h3', { 
                key: 'title',
                className: 'font-semibold mb-3' 
            }, '免责声明'),
            React.createElement(Paragraph, { 
                key: 'content',
                type: 'secondary', 
                className: 'text-sm' 
            }, reportData.disclaimer || '本报告仅供辅助决策参考，不能替代专业的司法判断和心理评估。')
        ])
    ]);
}

// 案件管理组件
function CaseManagement() {
    const { Card, Table, Button, Space, Typography } = antd;
    const { Title } = Typography;
    const [cases, setCases] = useState([]);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {
        loadCases();
    }, []);
    
    const loadCases = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/cases/');
            if (response.ok) {
                const data = await response.json();
                setCases(data);
            }
        } catch (error) {
            console.error('加载案件失败:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const columns = [
        {
            title: '案件编号',
            dataIndex: 'case_number',
            key: 'case_number'
        },
        {
            title: '案件标题',
            dataIndex: 'title',
            key: 'title'
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (text) => new Date(text).toLocaleString()
        },
        {
            title: '操作',
            key: 'action',
            render: (_, record) => React.createElement(Space, {}, [
                React.createElement(Button, { 
                    key: 'view',
                    type: 'link', 
                    size: 'small' 
                }, '查看'),
                React.createElement(Button, { 
                    key: 'edit',
                    type: 'link', 
                    size: 'small' 
                }, '编辑')
            ])
        }
    ];
    
    return React.createElement('div', { className: 'p-6' },
        React.createElement(Card, { className: 'shadow-md' }, [
            React.createElement('div', {
                key: 'header',
                className: 'flex items-center justify-between mb-6'
            }, [
                React.createElement(Title, { level: 2, className: 'm-0' }, '案件管理'),
                React.createElement(Button, { type: 'primary' }, '新建案件')
            ]),
            React.createElement(Table, {
                key: 'table',
                columns: columns,
                dataSource: cases,
                loading: loading,
                rowKey: 'id',
                pagination: { pageSize: 10 }
            })
        ])
    );
}

// 渲染主应用
ReactDOM.render(React.createElement(App), document.getElementById('root'));
