import { Video, Settings, HelpCircle, Mic, MicOff, Camera, CameraOff, Volume2, VolumeX, User, Clock, Activity, MessageSquare, Circle, CircleStop, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useRef, useEffect } from "react";
import { useInterview } from "@/hooks/use-interview";
import { api } from "@/services/api";
import { Alert, AlertDescription } from "@/components/ui/alert";



export default function InterviewSimulation() {
  const [micEnabled, setMicEnabled] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [pausedDevices, setPausedDevices] = useState({ micEnabled: false, cameraEnabled: false, audioEnabled: false, isRecording: false });
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isResizing, setIsResizing] = useState(false);
  const [isTakingSnapshot, setIsTakingSnapshot] = useState(false);
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [pausedSessionTime, setPausedSessionTime] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);
  
  // 使用面试状态Hook
  const { isRunning, status, startInterview, stopInterview, error, isLoading } = useInterview();
  
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
  
  // 独立的录制状态控制
  const handleRecordingToggle = () => setIsRecording(prev => !prev);
  
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
    // 暂停设备
    setMicEnabled(false);
    setCameraEnabled(false);
    setAudioEnabled(false);
    setIsRecording(false);
    // 设置暂停状态
    setIsPaused(true);
  };
  
  // 恢复面试功能
  const handleResumeInterview = () => {
    // 恢复设备状态
    setMicEnabled(pausedDevices.micEnabled);
    setCameraEnabled(pausedDevices.cameraEnabled);
    setAudioEnabled(pausedDevices.audioEnabled);
    setIsRecording(pausedDevices.isRecording);
    // 清除暂停状态
    setIsPaused(false);
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
      {/* 顶部导航栏 - 60px */}
      <div className="h-[60px] bg-card border-b border-border flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-3">
          <Video className="w-6 h-6 text-primary" />
          <h1 className="text-xl font-semibold text-foreground">智能面试模拟系统</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <HelpCircle className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
        </div>
      </div>
      
      {/* 错误提示 */}
      {error && (
        <div className="px-6 py-2">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
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
                    disabled={isLoading || !isRunning}
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
                    <div className="font-medium">Python开发工程师</div>
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
                    onClick={() => isRunning ? stopInterview() : startInterview()}
                    disabled={isLoading}
                  >
                    {isRunning ? '停止面试' : '开始面试'}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full text-sm justify-start"
                    onClick={isPaused ? handleResumeInterview : handlePauseInterview}
                  >
                    {isPaused ? '继续面试' : '暂停面试'}
                  </Button>
                  <Button variant="outline" className="w-full text-sm justify-start text-error hover:text-error">
                    结束面试
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

        {/* 中间视频区 - 灵活宽度 */}
        <div className="flex-1 p-6 flex flex-col justify-center overflow-y-auto">
          {/* 面试者视频 - 横向宽屏显示 */}
          <Card className="w-full max-w-5xl mx-auto">
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
                <span className={`font-medium ${status ? getAttentionColor(status.attention_score) : 'text-muted-foreground'}`}>
                  {status ? Math.round(status.attention_score) : '无数据'}
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-4 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-300 ${status ? getAttentionBarColor(status.attention_score) : 'bg-muted'}`} 
                  style={{ width: status ? `${status.attention_score}%` : '0%' }} 
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
                <span className={`font-medium ${status && status.face_detected ? 'text-success' : 'text-error'}`}>
                  {status && status.face_detected ? '已检测' : '未检测'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">视线状态</span>
                <span className={`font-medium ${status && status.gaze_status === '正常' ? 'text-success' : 'text-warning'}`}>
                  {status ? status.gaze_status : '正常'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">姿态状态</span>
                <span className={`font-medium ${status && status.pose_status === '良好' ? 'text-success' : 'text-warning'}`}>
                  {status ? status.pose_status : '良好'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">小动作</span>
                <span className={`font-medium ${status && status.gesture_status === '无小动作' ? 'text-success' : 'text-warning'}`}>
                  {status ? status.gesture_status : '无小动作'}
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
                {status ? status.feedback : "系统运行中..."}
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
        <div className="text-muted-foreground">
          2024 智能面试模拟系统
        </div>
      </div>
    </div>
  );
}