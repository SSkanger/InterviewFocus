import { Video, Settings, HelpCircle, Mic, MicOff, Camera, CameraOff, Volume2, VolumeX, User, Clock, Activity, MessageSquare, Circle, CircleStop, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useRef, useEffect } from "react";
import { useInterview } from "@/hooks/use-interview";
import { useVoice } from "@/hooks/use-voice";
import { api, InterviewStatus, AttentionAnalysis } from "@/services/api";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import InterviewSummary from "@/components/InterviewSummary";


export default function InterviewSimulation() {
  // 问题时间配置
  const QUESTION_TIME_LIMIT = 300; // 每个问题5分钟，单位秒
  
  const [micEnabled, setMicEnabled] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [pausedDevices, setPausedDevices] = useState({ micEnabled: false, cameraEnabled: false, audioEnabled: false, isRecording: false });
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isResizing, setIsResizing] = useState(false);
  const [isTakingSnapshot, setIsTakingSnapshot] = useState(false);
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [pausedSessionTime, setPausedSessionTime] = useState(0);
  const [pausedQuestionTime, setPausedQuestionTime] = useState(QUESTION_TIME_LIMIT);
  const [pausedStatus, setPausedStatus] = useState<InterviewStatus['data'] | null>(null);
  const [interviewPosition, setInterviewPosition] = useState("");
  const [showPositionModal, setShowPositionModal] = useState(true);
  const [isInterviewEnded, setIsInterviewEnded] = useState(false); // 添加面试结束标志
  const [finalSessionTime, setFinalSessionTime] = useState(0); // 保存面试结束时的会话时间
  const videoRef = useRef<HTMLVideoElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);
  
  // 使用面试状态Hook
  const { isRunning, isPaused, status, attentionAnalysis, startInterview, stopInterview, pauseInterview, resumeInterview, resetInterview, error, isLoading, videoSaved, videoUrl } = useInterview();
  
  // 使用语音合成Hook
  const { speak, stopSpeaking, isSpeaking, error: voiceError } = useVoice();
  
  // 问题相关状态
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState<string[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [questionTimeLeft, setQuestionTimeLeft] = useState<number>(QUESTION_TIME_LIMIT); // 每个问题默认5分钟
  const [isQuestionAnswered, setIsQuestionAnswered] = useState<boolean>(false);
  const questionTimerRef = useRef<NodeJS.Timeout | null>(null);
  const hasSpokenRef = useRef(false); // 移到顶层，用于确保语音只播报一次
  
  // 初始化问题列表
  useEffect(() => {
    if (isRunning && interviewPosition) {
      // 从后端API获取与职业相关的问题
      const fetchQuestions = async () => {
        try {
          console.log('开始获取职业问题:', interviewPosition);
          const response = await api.getQuestionsForPosition(interviewPosition);
          
          if (response.success && response.data.questions.length > 0) {
            console.log('成功获取职业问题，共', response.data.questions.length, '个');
            // 提取问题文本
            const questionsList = response.data.questions.map((q: any) => q.question);
            setQuestions(questionsList);
            setCurrentQuestionIndex(0);
            setCurrentQuestion(questionsList[0]);
            setQuestionTimeLeft(QUESTION_TIME_LIMIT);
            setIsQuestionAnswered(false);
          } else {
            console.warn('获取职业问题失败或没有问题，使用默认问题');
            // 当没有获取到问题时，使用默认问题
            const defaultQuestions = [
              "请简单介绍一下您自己。",
              "为什么您对这个职位感兴趣？",
              "您认为自己最大的优势是什么？",
              "请分享一个您解决过的最具挑战性的问题。",
              "您如何看待团队合作？",
              "您对未来的职业规划是什么？",
              "您为什么选择离开上一家公司？",
              "您对我们公司了解多少？"
            ];
            setQuestions(defaultQuestions);
            setCurrentQuestionIndex(0);
            setCurrentQuestion(defaultQuestions[0]);
            setQuestionTimeLeft(QUESTION_TIME_LIMIT);
            setIsQuestionAnswered(false);
          }
        } catch (error) {
          console.error('获取职业问题时发生错误:', error);
          // 错误时使用默认问题
          const defaultQuestions = [
            "请简单介绍一下您自己。",
            "为什么您对这个职位感兴趣？",
            "您认为自己最大的优势是什么？",
            "请分享一个您解决过的最具挑战性的问题。",
            "您如何看待团队合作？",
            "您对未来的职业规划是什么？",
            "您为什么选择离开上一家公司？",
            "您对我们公司了解多少？"
          ];
          setQuestions(defaultQuestions);
          setCurrentQuestionIndex(0);
          setCurrentQuestion(defaultQuestions[0]);
          setQuestionTimeLeft(QUESTION_TIME_LIMIT);
          setIsQuestionAnswered(false);
        }
      };
      
      fetchQuestions();
    }
  }, [isRunning, interviewPosition]);
  
  // 当面试开始时，启动第一个问题的计时器（不播报语音，由后端处理）
  useEffect(() => {
    if (isRunning && interviewPosition && currentQuestion && !hasSpokenRef.current) {
      hasSpokenRef.current = true;
      
      const startInterviewWithVoice = async () => {
        console.log('面试开始，启动计时器');
        // 启动第一个问题的计时器
        startQuestionTimer();
      };
      
      startInterviewWithVoice();
    }
    
    // 面试结束时重置标志和清除计时器
    return () => {
      if (!isRunning) {
        hasSpokenRef.current = false;
        // 清除计时器
        if (questionTimerRef.current) {
          clearInterval(questionTimerRef.current);
          questionTimerRef.current = null;
        }
      }
    };
  }, [isRunning, interviewPosition, currentQuestion]);

  
  // 问题计时器函数
  const startQuestionTimer = () => {
    console.log('启动问题计时器');
    // 清除之前的计时器
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
      questionTimerRef.current = null;
    }
    
    // 启动新的计时器
    questionTimerRef.current = setInterval(() => {
      setQuestionTimeLeft(prevTime => {
        if (prevTime <= 1) {
          // 时间到，自动切换到下一个问题
          if (questionTimerRef.current) {
            clearInterval(questionTimerRef.current);
            questionTimerRef.current = null;
          }
          handleNextQuestion();
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);
  };
  
  // 处理下一个问题
  const handleNextQuestion = async () => {
    console.log('处理下一个问题');
    // 清除当前问题的计时器
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
      questionTimerRef.current = null;
    }
    
    // 检查是否还有下一个问题
    if (currentQuestionIndex < questions.length - 1) {
      // 进入下一个问题
      const nextIndex = currentQuestionIndex + 1;
      const nextQuestion = questions[nextIndex];
      setCurrentQuestionIndex(nextIndex);
      setCurrentQuestion(nextQuestion);
      setIsQuestionAnswered(false);
      
      // 立即将计时器重置为5分钟，但不启动计时
      console.log('将计时器重置为5分钟');
      setQuestionTimeLeft(QUESTION_TIME_LIMIT);
      
      // 调用后端API播放下一个问题的语音
      console.log('调用后端API播放下一个问题的语音:', nextQuestion);
      try {
        const response = await api.nextQuestion(nextQuestion);
        if (response.success) {
          console.log('✅ 后端已开始播放下一个问题的语音');
        } else {
          console.error('❌ 后端播放下一个问题语音失败:', response.message);
        }
      } catch (err) {
        console.error('❌ 调用后端API失败:', err);
      }
      
      // 启动计时器
      console.log('启动计时器');
      startQuestionTimer();
    } else {
      // 所有问题已结束
      console.log('所有问题已结束，调用后端API处理面试结束');
      try {
        // 调用后端API处理面试结束
        const response = await api.nextQuestion();
        if (response.success) {
          console.log('✅ 后端已处理面试结束');
        }
      } catch (err) {
        console.error('❌ 调用后端API失败:', err);
      }
      // 清除问题计时器
      if (questionTimerRef.current) {
        clearInterval(questionTimerRef.current);
        questionTimerRef.current = null;
      }
      // 保存面试结束时的会话时间
      setFinalSessionTime(status?.session_time || 0);
      // 停止语音播放
      stopSpeaking();
      // 自动停止面试
      await stopInterview();

      setIsInterviewEnded(true);
    }
  };
  
  // 处理当前问题回答完成
  const handleQuestionAnswered = async () => {
    setIsQuestionAnswered(true);
    console.log('当前问题回答完成，3秒后自动进入下一个问题');
    // 延迟3秒后自动进入下一个问题
    setTimeout(() => {
      handleNextQuestion();
    }, 3000);
  };
  
  // 组件卸载时清除计时器
  useEffect(() => {
    return () => {
      if (questionTimerRef.current) {
        clearInterval(questionTimerRef.current);
        questionTimerRef.current = null;
      }
    };
  }, []);

  // 职业分类数据类型定义
  type CareerCategories = {
    [key: string]: string[];
  };

  // 职业分类数据 - 覆盖常见所有职业
  const careerCategories: CareerCategories = {
    "计算机/互联网类": [
      "Python开发工程师",
      "Java开发工程师",
      "前端开发工程师",
      "后端开发工程师",
      "全栈开发工程师",
      "数据分析师",
      "机器学习工程师",
      "算法工程师",
      "测试工程师",
      "DevOps工程师",
      "网络工程师",
      "系统运维工程师",
      "数据库管理员",
      "区块链工程师",
      "游戏开发工程师",
      "大数据工程师",
      "云计算工程师",
      "信息安全工程师",
      "嵌入式开发工程师"
    ],
    "产品/设计/运营类": [
      "产品经理",
      "运营专员",
      "市场专员",
      "用户研究员",
      "UI设计师",
      "UX设计师",
      "视觉设计师",
      "交互设计师",
      "产品运营",
      "内容运营",
      "用户运营",
      "社群运营",
      "活动运营",
      "数据运营",
      "新媒体运营",
      "SEO专员",
      "SEM专员",
      "品牌专员",
      "广告策划"
    ],
    "金融/经济类": [
      "金融分析师",
      "投资顾问",
      "银行柜员",
      "保险经纪人",
      "财务会计",
      "审计师",
      "税务师",
      "资产评估师",
      "证券分析师",
      "基金经理",
      "风险管理师",
      "理财顾问",
      "信贷专员",
      "外汇交易员",
      "期货交易员",
      "保险精算师",
      "投资银行分析师",
      "经济研究员",
      "财务经理",
      "会计主管"
    ],
    "销售/市场/公关类": [
      "销售代表",
      "销售经理",
      "客户经理",
      "区域销售经理",
      "渠道销售",
      "电话销售",
      "网络销售",
      "市场经理",
      "市场策划",
      "市场调研",
      "品牌经理",
      "公关专员",
      "公关经理",
      "媒介专员",
      "广告客户经理",
      "商务拓展",
      "客户成功经理",
      "销售总监",
      "市场总监",
      "公关总监"
    ],
    "教育/培训类": [
      "小学教师",
      "中学教师",
      "高中教师",
      "大学教师",
      "培训机构讲师",
      "教育咨询师",
      "课程设计师",
      "教育行政人员",
      "班主任",
      "辅导教师",
      "留学顾问",
      "语言培训师",
      "职业培训师",
      "教育产品经理",
      "教育技术专员",
      "早教教师",
      "特殊教育教师",
      "在线教育讲师",
      "教育研究员",
      "教务管理"
    ],
    "医疗/健康类": [
      "医生",
      "护士",
      "药剂师",
      "营养师",
      "心理咨询师",
      "康复治疗师",
      "医学检验师",
      "影像科医师",
      "麻醉科医师",
      "外科医生",
      "内科医生",
      "儿科医生",
      "妇产科医生",
      "皮肤科医生",
      "眼科医生",
      "耳鼻喉科医生",
      "口腔科医生",
      "精神科医生",
      "健康管理师",
      "医疗器械销售"
    ],
    "法律/法务类": [
      "律师",
      "法务专员",
      "法律顾问",
      "法官",
      "检察官",
      "律师助理",
      "知识产权律师",
      "公司法务",
      "刑事律师",
      "民事律师",
      "行政律师",
      "婚姻家庭律师",
      "房产律师",
      "合同律师",
      "劳动法律师",
      "税务律师",
      "国际律师",
      "律师事务所合伙人",
      "法律研究员",
      "法律翻译"
    ],
    "行政/人事/财务类": [
      "行政专员",
      "行政经理",
      "人事专员",
      "人事经理",
      "招聘专员",
      "培训专员",
      "薪酬福利专员",
      "绩效考核专员",
      "HRBP",
      "人力资源总监",
      "行政总监",
      "办公室主任",
      "秘书",
      "助理",
      "前台接待",
      "财务助理",
      "出纳",
      "财务主管",
      "财务总监",
      "审计主管"
    ],
    "工程/制造类": [
      "机械工程师",
      "电气工程师",
      "电子工程师",
      "自动化工程师",
      "土木工程师",
      "建筑工程师",
      "结构工程师",
      "给排水工程师",
      "暖通工程师",
      "环境工程师",
      "化工工程师",
      "材料工程师",
      "质量工程师",
      "工艺工程师",
      "生产工程师",
      "设备工程师",
      "研发工程师",
      "工程监理",
      "项目经理",
      "工厂经理"
    ],
    "服务/零售类": [
      "服务员",
      "收银员",
      "导购员",
      "店长",
      "店员",
      "客服专员",
      "客服经理",
      "酒店前台",
      "酒店经理",
      "厨师",
      "餐厅经理",
      "咖啡师",
      "调酒师",
      "美容师",
      "美发师",
      "美甲师",
      "健身教练",
      "瑜伽教练",
      "保洁员",
      "保安"
    ]
  };

  // 职业选择状态
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedCareer, setSelectedCareer] = useState("");

  // 处理面试岗位设置
  const handleSetPosition = () => {
    if (selectedCareer.trim()) {
      setInterviewPosition(selectedCareer);
      setShowPositionModal(false);
    }
  };

  // 当分类改变时，重置职业选择
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setSelectedCareer("");
  };
  
  // 移除自动关闭模态框的逻辑，确保用户必须明确点击按钮才能关闭
  // useEffect(() => {
  //   if (interviewPosition.trim()) {
  //     setShowPositionModal(false);
  //   }
  // }, [interviewPosition]);
  
  // 根据面试状态自动控制设备
  useEffect(() => {
    if (isRunning) {
      // 开始面试时，全部开启
      setMicEnabled(true);
      setCameraEnabled(true);
      setAudioEnabled(true);
      setIsRecording(true);
    } else {
      // 停止面试时，全部关闭
      setMicEnabled(false);
      setCameraEnabled(false);
      setAudioEnabled(false);
      setIsRecording(false);
    }
  }, [isRunning]);
  
  // 30分钟时间用尽自动停止面试
  useEffect(() => {
    if (isRunning && status && !isInterviewEnded && status.session_time >= 1800) {
      // 30分钟时间已到
      const endMessage = `面试时间已达30分钟，面试结束。感谢您的参与！`;
      speak(endMessage);
      // 保存面试结束时的会话时间
      setFinalSessionTime(status?.session_time || 0);
      // 停止语音播放
      stopSpeaking();
      // 自动停止面试
      const stopAndSaveVideo = async () => {
        try {
          await stopInterview();
          // 开始保存，设置状态为null
          setVideoSaved(null);
          setVideoSaveError(null);
          // 保存面试视频
          console.log('开始保存面试视频...');
          const videoResponse = await api.saveInterviewVideo();
          if (videoResponse.success) {
            console.log('视频保存成功');
            setVideoSaved(true);
            setVideoSaveError(null);
          } else {
            console.error('视频保存失败:', videoResponse.message);
            setVideoSaved(false);
            setVideoSaveError(videoResponse.message || '视频保存失败');
          }
        } catch (error) {
          console.error('视频保存失败:', error);
          if (error instanceof Error) {
            setVideoSaveError('视频保存失败: ' + error.message);
          } else {
            setVideoSaveError('视频保存失败: 未知错误');
          }
          setVideoSaved(false);
        } finally {
          setIsInterviewEnded(true);
        }
      };
      stopAndSaveVideo();
    }
  }, [isRunning, status, isInterviewEnded, stopInterview, speak, stopSpeaking]);
  
  // 独立的录制状态控制
  const handleRecordingToggle = async () => {
    // 检查当前录制状态
    const currentRecordingState = isRecording;
    // 切换录制状态
    setIsRecording(prev => !prev);
    
    if (currentRecordingState) {
      // 如果当前是录制中，切换后会变为未录制，此时停止录制并保存视频
      try {
        console.log('录制已关闭，开始停止录制并保存视频片段...');
        // 停止录制
        const stopResponse = await api.stopRecording();
        if (stopResponse.success) {
          console.log('录制已停止');
        } else {
          console.error('停止录制失败:', stopResponse.message);
        }
        
        // 保存视频
        const videoResponse = await api.saveInterviewVideo();
        if (videoResponse.success) {
          console.log('视频片段保存成功');
          // 更新视频保存状态
          setVideoSaved(true);
          setVideoSaveError(null);
          // 这里可以添加一个提示，告诉用户视频已保存
        } else {
          console.error('视频片段保存失败:', videoResponse.message);
          // 更新视频保存状态
          setVideoSaved(false);
          setVideoSaveError(videoResponse.message || '视频保存失败');
        }
      } catch (error) {
        console.error('视频片段保存失败:', error);
        // 更新视频保存状态
        if (error instanceof Error) {
          setVideoSaveError('视频保存失败: ' + error.message);
        } else {
          setVideoSaveError('视频保存失败: 未知错误');
        }
        setVideoSaved(false);
      }
    } else {
      // 如果当前是未录制，切换后会变为录制中，此时开始录制
      try {
        console.log('录制已开启，开始录制视频...');
        const startResponse = await api.startRecording();
        if (startResponse.success) {
          console.log('录制已开始');
        } else {
          console.error('开始录制失败:', startResponse.message);
        }
      } catch (error) {
        console.error('开始录制失败:', error);
      }
    }
  };
  
  // 独立的设备控制状态更新
  const handleMicToggle = () => setMicEnabled(prev => !prev);
  const handleCameraToggle = () => setCameraEnabled(prev => !prev);
  const handleAudioToggle = () => setAudioEnabled(prev => !prev);
  
  // 暂停面试功能
  const handlePauseInterview = () => {
    // 保存当前设备状态
    setPausedDevices({ micEnabled, cameraEnabled, audioEnabled, isRecording });
    // 保存当前会话时间
    if (status) {
      setPausedSessionTime(status.session_time);
    }
    // 保存当前状态
    setPausedStatus(status);
    // 保存当前问题剩余时间
    setPausedQuestionTime(questionTimeLeft);
    // 暂停问题计时器
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
      questionTimerRef.current = null;
    }
    // 暂停设备
    setMicEnabled(false);
    setCameraEnabled(false);
    setAudioEnabled(false);
    setIsRecording(false);
    // 调用hook的暂停函数
    pauseInterview();
  };
  
  // 恢复面试功能
  const handleResumeInterview = () => {
    // 恢复设备状态
    setMicEnabled(pausedDevices.micEnabled);
    setCameraEnabled(pausedDevices.cameraEnabled);
    setAudioEnabled(pausedDevices.audioEnabled);
    setIsRecording(pausedDevices.isRecording);
    // 恢复问题计时器
    startQuestionTimer();
    // 调用hook的恢复函数
    resumeInterview();
    // 清除暂停状态
    setPausedStatus(null);
  };
  
  // 格式化显示时间，考虑暂停状态
  const formatDisplayTime = (seconds: number): string => {
    if (isPaused) {
      return formatTime(pausedSessionTime);
    }
    return formatTime(seconds);
  };
  
  // 获取剩余时间，考虑暂停状态
  const getRemainingTime = (sessionTime: number): string => {
    const currentTime = isPaused ? pausedSessionTime : sessionTime;
    return formatTime(Math.max(0, 1800 - currentTime));
  };
  
  // 获取进度百分比，考虑暂停状态
  const getProgressPercentage = (sessionTime: number): number => {
    const currentTime = isPaused ? pausedSessionTime : sessionTime;
    return Math.min(100, (currentTime / 1800) * 100);
  };

  // 处理拖动调整宽度
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 400) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  // 格式化时间
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 获取注意力分数颜色
  const getAttentionColor = (score: number): string => {
    if (score >= 70) return 'text-success';
    if (score >= 50) return 'text-warning';
    return 'text-destructive';
  };

  // 获取注意力条颜色
  const getAttentionBarColor = (score: number): string => {
    if (score >= 70) return 'bg-success';
    if (score >= 50) return 'bg-warning';
    return 'bg-destructive';
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {isInterviewEnded ? (
        // 面试结束，显示总结
        <div className="flex-1 p-8 overflow-y-auto">
          <InterviewSummary 
            interviewPosition={interviewPosition} 
            sessionTime={finalSessionTime || 0} 
            attentionAnalysis={attentionAnalysis || null}
            error={error}
            videoSaved={videoSaved}
            // 移除isLoading属性，避免与错误状态冲突
            onRetry={() => {
              console.log('重新获取面试总结...');
              fetchAttentionHistory();
              fetchAttentionAnalysis();
            }}
          />
          <div className="flex justify-center mt-8">
            <Button onClick={async () => {
              // 重置所有状态，重新开始
              await resetInterview();
              setIsInterviewEnded(false);
              setCurrentQuestionIndex(0);
              setQuestions([]);  // 重置问题数组
              setCurrentQuestion('');  // 重置当前问题
              setQuestionTimeLeft(QUESTION_TIME_LIMIT);
              setIsQuestionAnswered(false);
              setFinalSessionTime(0);
              setVideoSaved(false);
              setVideoSaveError(null);
              hasSpokenRef.current = false;
              // 清除问题计时器
              if (questionTimerRef.current) {
                clearInterval(questionTimerRef.current);
                questionTimerRef.current = null;
              }
            }}>
              重新开始面试
            </Button>
          </div>
        </div>
      ) : (
        // 面试进行中，显示正常界面
        <>
          {/* 顶部导航栏 - 60px */}
          <div className="h-[60px] bg-card border-b border-border flex items-center justify-between px-6 shrink-0">
            <div className="flex items-center gap-3">
              <Video className="w-6 h-6 text-primary" />
              <h1 className="text-xl font-semibold text-foreground">智能面试模拟系统</h1>
            </div>

          </div>
          
          {/* 错误提示 */}
          {(error || voiceError) && (
            <div className="px-6 py-2">
              <Alert variant="destructive">
                <AlertDescription>{error || voiceError}</AlertDescription>
              </Alert>
            </div>
          )}
          
          
          
          {/* 主内容区域 */}
          <div className="flex-1 flex overflow-hidden">
            {/* 左侧功能区 - 可调整宽度 */}
            {sidebarVisible && (
              <div 
                ref={sidebarRef}
                className="bg-card border-r border-border flex flex-col gap-4 shrink-0 overflow-y-auto relative"
                style={{ width: `${sidebarWidth}px` }}
              >
                <div className="p-4 flex flex-col gap-4">
                  {/* 隐藏按钮 */}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start"
                    onClick={() => setSidebarVisible(false)}
                  >
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    隐藏工具栏
                  </Button>
                  
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">设备控制</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div 
                        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${!isRunning ? 'cursor-not-allowed opacity-50 pointer-events-none bg-muted border border-border' : (micEnabled ? 'bg-success/10 border border-success/20 hover:bg-success/20' : 'bg-muted border border-border hover:bg-muted/80')}`}
                        onClick={() => isRunning && handleMicToggle()}
                      >
                        {micEnabled ? (
                          <Mic className="w-4 h-4 text-success" />
                        ) : (
                          <MicOff className="w-4 h-4 text-muted-foreground" />
                        )}
                        <span className={`text-sm ${micEnabled ? 'text-success' : 'text-muted-foreground'}`}>
                          麦克风{micEnabled ? '已开启' : '已关闭'}
                        </span>
                      </div>
                      <div 
                        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${!isRunning ? 'cursor-not-allowed opacity-50 pointer-events-none bg-muted border border-border' : (cameraEnabled ? 'bg-success/10 border border-success/20 hover:bg-success/20' : 'bg-muted border border-border hover:bg-muted/80')}`}
                        onClick={() => isRunning && handleCameraToggle()}
                      >
                        {cameraEnabled ? (
                          <Camera className="w-4 h-4 text-success" />
                        ) : (
                          <CameraOff className="w-4 h-4 text-muted-foreground" />
                        )}
                        <span className={`text-sm ${cameraEnabled ? 'text-success' : 'text-muted-foreground'}`}>
                          摄像头{cameraEnabled ? '已开启' : '已关闭'}
                        </span>
                      </div>
                      <div 
                        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${!isRunning ? 'cursor-not-allowed opacity-50 pointer-events-none bg-muted border border-border' : (audioEnabled ? 'bg-success/10 border border-success/20 hover:bg-success/20' : 'bg-muted border border-border hover:bg-muted/80')}`}
                        onClick={() => isRunning && handleAudioToggle()}
                      >
                        {audioEnabled ? (
                          <Volume2 className="w-4 h-4 text-success" />
                        ) : (
                          <VolumeX className="w-4 h-4 text-muted-foreground" />
                        )}
                        <span className={`text-sm ${audioEnabled ? 'text-success' : 'text-muted-foreground'}`}>
                          音频{audioEnabled ? '已开启' : '已关闭'}
                        </span>
                      </div>
                      <div 
                        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${!isRunning ? 'cursor-not-allowed opacity-50 pointer-events-none bg-muted border border-border' : (isRecording ? 'bg-success/10 border border-success/20 hover:bg-success/20' : 'bg-muted border border-border hover:bg-muted/80')}`}
                        onClick={handleRecordingToggle}
                      >
                        {isRecording ? (
                          <Circle className="w-4 h-4 text-success fill-success" />
                        ) : (
                          <CircleStop className="w-4 h-4 text-muted-foreground" />
                        )}
                        <span className={`text-sm ${isRecording ? 'text-success' : 'text-muted-foreground'}`}>
                          {isRecording ? '录制中' : '录制已停止'}
                        </span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">面试信息</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                      <div>
                        <div className="text-muted-foreground mb-1">面试岗位</div>
                        <div className="font-medium">{interviewPosition}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground mb-1">面试时长</div>
                        <div className="font-medium">30分钟</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground mb-1">当前状态</div>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-success animate-pulse' : 'bg-muted'}`} />
                          <span className={`${isRunning ? 'text-success' : 'text-muted-foreground'} font-medium`}>
                            {isRunning ? '进行中' : '未开始'}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">快捷操作</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Button 
                        variant="outline" 
                        className="w-full text-sm justify-start"
                        onClick={() => {
                          if (isRunning) {
                            // 保存面试结束时的会话时间
                            setFinalSessionTime(status?.session_time || 0);
                            // 停止语音播放
                            stopSpeaking();
                            // 停止面试
                            stopInterview();
                            setIsInterviewEnded(true);
                          } else {
                            startInterview(interviewPosition);
                          }
                        }}
                        disabled={isLoading || !interviewPosition.trim() || isInterviewEnded}
                      >
                        {isRunning ? '停止面试' : '开始面试'}
                      </Button>
                      <Button 
                        variant="outline" 
                        className="w-full text-sm justify-start"
                        onClick={isPaused ? handleResumeInterview : handlePauseInterview}
                        disabled={!isRunning || isInterviewEnded}
                      >
                        {isPaused ? '继续面试' : '暂停面试'}
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* 拖动手柄 */}
                <div 
                  className="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-primary/50 transition-colors group"
                  onMouseDown={() => setIsResizing(true)}
                >
                  <div className="absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2 w-4 h-12 bg-border group-hover:bg-primary/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-0.5 h-6 bg-background rounded-full" />
                  </div>
                </div>
              </div>
            )}

            {/* 显示工具栏按钮 */}
            {!sidebarVisible && (
              <div className="relative">
                <Button 
                  variant="outline" 
                  size="icon"
                  className="absolute top-4 left-4 z-10"
                  onClick={() => setSidebarVisible(true)}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}

            {/* 中间内容区 - 垂直布局：视频 + 问题控制 */}
            <div className="flex-1 flex flex-col overflow-y-auto">
              {/* 视频区 */}
              <div className="p-6 flex justify-center">
                {/* 面试者视频 - 横向宽屏显示 */}
                <Card className="w-full max-w-5xl">
                  <CardContent className="p-0">
                    <div className="w-full aspect-video bg-muted rounded-lg flex items-center justify-center relative overflow-hidden">
                      {/* 视频流 */}
                      {isRunning ? (
                        cameraEnabled ? (
                          <img 
                            src={api.getVideoStreamUrl()} 
                            alt="面试视频" 
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <>
                            <div className="absolute inset-0 bg-gradient-to-br from-muted/50 to-muted/70" />
                            <div className="relative z-10 flex flex-col items-center gap-4">
                              <div className="w-40 h-40 rounded-full bg-muted/50 flex items-center justify-center">
                                <CameraOff className="w-20 h-20 text-muted-foreground" />
                              </div>
                              <div className="text-center">
                                <div className="text-2xl font-semibold mb-2">摄像头已关闭</div>
                                <div className="text-base text-muted-foreground">点击设备控制区的摄像头图标开启</div>
                              </div>
                            </div>
                          </>
                        )
                      ) : (
                        <>
                          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-primary/10" />
                          <div className="relative z-10 flex flex-col items-center gap-4">
                            <div className="w-40 h-40 rounded-full bg-primary/20 flex items-center justify-center">
                              <User className="w-20 h-20 text-primary" />
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-semibold mb-2">您的视频画面</div>
                              <div className="text-base text-muted-foreground">请注意您的表情和仪态</div>
                            </div>
                          </div>
                        </>
                      )}
                      <div className="absolute top-4 left-4 bg-card/90 backdrop-blur-sm px-4 py-2 rounded-lg text-base font-medium">
                        我的视频
                      </div>
                      <div className={`absolute top-4 right-4 ${isRecording ? 'bg-success/90' : 'bg-muted/90'} backdrop-blur-sm px-4 py-2 rounded-lg text-base font-medium ${isRecording ? 'text-success-foreground' : 'text-muted-foreground'} flex items-center gap-2`}>
                        <div className={`w-2.5 h-2.5 rounded-full ${isRecording ? 'bg-success-foreground animate-pulse' : 'bg-muted'}`} />
                        {isRecording ? '录制中' : '未录制'}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* 视频下方的问题控制区 - 紧凑布局 */}
              <div className="p-2 pb-6">
                <Card className="w-full max-w-5xl mx-auto">
                  <CardContent className="p-2">
                    {/* 横排布局容器 - 均匀排布 */}
                    <div className="flex items-center justify-around gap-4 flex-wrap">
                      {/* 当前问题 - 左侧 */}
                      <div className="flex-1 min-w-[200px] flex flex-col items-center text-center">
                        <div className="text-xs font-medium text-muted-foreground">当前问题</div>
                        <div className="text-base font-semibold">
                          {currentQuestion || "系统运行中..."}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          问题 {currentQuestionIndex + 1}/{questions.length}
                        </div>
                      </div>
                      
                      {/* 问题计时 - 中间 */}
                      <div className="flex-1 min-w-[300px] flex flex-col items-center gap-1">
                        <div className="flex items-center gap-3">
                          <div className="text-xs font-medium text-muted-foreground">问题计时</div>
                          <div className="text-2xl font-bold text-primary">
                            {Math.floor(questionTimeLeft / 60)}:{(questionTimeLeft % 60).toString().padStart(2, '0')}
                          </div>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2.5">
                          <div 
                            className={`h-2.5 rounded-full transition-all duration-300 ${questionTimeLeft > 120 ? 'bg-success' : questionTimeLeft > 60 ? 'bg-warning' : 'bg-destructive'}`} 
                            style={{ width: `${(questionTimeLeft / QUESTION_TIME_LIMIT) * 100}%` }} 
                          />
                        </div>
                      </div>
                      
                      {/* 问题控制 - 右侧 */}
                      <div className="flex-1 min-w-[150px] flex justify-center">
                        <Button 
                          variant="outline" 
                          className="px-6 py-1.5 text-sm"
                          onClick={handleNextQuestion}
                          disabled={!isRunning}
                        >
                          下一个问题
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* 右侧数据面板 - 320px */}
            <div className="w-[320px] bg-card border-l border-border p-4 flex flex-col gap-4 shrink-0 overflow-y-auto">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    面试进度
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-muted-foreground">已用时间</span>
                      <span className="font-medium">{status ? formatDisplayTime(status.session_time) : "00:00"}</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full" 
                        style={{ width: status ? `${getProgressPercentage(status.session_time)}%` : '0%' }} 
                      />
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    剩余时间：{status ? getRemainingTime(status.session_time) : "30:00"}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    注意力评分
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">当前分数</span>
                      <span className={`font-medium ${(isPaused ? pausedStatus : status) ? getAttentionColor((isPaused ? pausedStatus : status)!.attention_score) : 'text-muted-foreground'}`}>
                        {(isPaused ? pausedStatus : status) ? Math.round((isPaused ? pausedStatus : status)!.attention_score) : '无数据'}
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-4 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${(isPaused ? pausedStatus : status) ? getAttentionBarColor((isPaused ? pausedStatus : status)!.attention_score) : 'bg-muted'}`} 
                        style={{ width: (isPaused ? pausedStatus : status) ? `${(isPaused ? pausedStatus : status)!.attention_score}%` : '0%' }} 
                      />
                    </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    实时状态
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">面部检测</span>
                      <span className={`font-medium ${(isPaused ? pausedStatus : status) && (isPaused ? pausedStatus : status)!.face_detected ? 'text-success' : 'text-error'}`}>
                        {(isPaused ? pausedStatus : status) && (isPaused ? pausedStatus : status)!.face_detected ? '已检测' : '未检测'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">视线状态</span>
                      <span className={`font-medium ${(isPaused ? pausedStatus : status) && (isPaused ? pausedStatus : status)!.gaze_status === '正常' ? 'text-success' : 'text-warning'}`}>
                        {(isPaused ? pausedStatus : status) ? (isPaused ? pausedStatus : status)!.gaze_status : '正常'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">姿态状态</span>
                      <span className={`font-medium ${(isPaused ? pausedStatus : status) && (isPaused ? pausedStatus : status)!.pose_status === '良好' ? 'text-success' : 'text-warning'}`}>
                        {(isPaused ? pausedStatus : status) ? (isPaused ? pausedStatus : status)!.pose_status : '良好'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">小动作</span>
                      <span className={`font-medium ${(isPaused ? pausedStatus : status) && (isPaused ? pausedStatus : status)!.gesture_status === '无小动作' ? 'text-success' : 'text-warning'}`}>
                        {(isPaused ? pausedStatus : status) ? (isPaused ? pausedStatus : status)!.gesture_status : '无小动作'}
                      </span>
                    </div>
                </CardContent>
              </Card>

              <Card className="flex-1">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    系统反馈
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                      {(isPaused ? pausedStatus : status) ? (isPaused ? pausedStatus : status)!.feedback : "系统运行中..."}
                    </div>
                </CardContent>
              </Card>
            </div>
          </div>
          
          {/* 底部状态栏 - 40px */}
          <div className="h-[40px] bg-card border-t border-border flex items-center justify-between px-6 shrink-0 text-sm">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${error ? 'bg-error' : 'bg-success'}`} />
                <span className="text-muted-foreground">{error ? '系统异常' : '系统运行正常'}</span>
              </div>
              <div className="text-muted-foreground">
                面试ID: <span className="font-mono">IV-2024-001</span>
              </div>
            </div>

          </div>
        </>
      )}

      {/* 面试岗位输入模态框 */}
      <Dialog 
        open={showPositionModal} 
        onOpenChange={(open) => {
          // 只有在确定选择了职业后才允许关闭模态框
          if (open === false && selectedCareer.trim()) {
            setShowPositionModal(false);
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>设置面试岗位</DialogTitle>
            <DialogDescription>
              请输入您要模拟面试的职业，以便系统为您提供更精准的反馈。
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* 职业大类选择 */}
            <div className="space-y-2">
              <label htmlFor="career-category" className="text-sm font-medium">
                职业大类
              </label>
              <Select value={selectedCategory} onValueChange={handleCategoryChange}>
                <SelectTrigger id="career-category">
                  <SelectValue placeholder="请选择职业大类" />
                </SelectTrigger>
                <SelectContent>
                  {Object.keys(careerCategories).map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 具体职业选择 */}
            <div className="space-y-2">
              <label htmlFor="career-position" className="text-sm font-medium">
                具体职业
              </label>
              <Select value={selectedCareer} onValueChange={setSelectedCareer}>
                <SelectTrigger id="career-position">
                  <SelectValue placeholder="请选择具体职业" />
                </SelectTrigger>
                <SelectContent>
                  {selectedCategory && careerCategories[selectedCategory].map((career: string) => (
                    <SelectItem key={career} value={career}>
                      {career}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={handleSetPosition}
              disabled={!selectedCareer.trim()}
              className="w-full"
            >
              开始面试准备
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
