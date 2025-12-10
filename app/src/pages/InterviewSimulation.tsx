import { Video, Settings, HelpCircle, Mic, MicOff, Camera, CameraOff, Volume2, VolumeX, User, Clock, Activity, MessageSquare, Circle, CircleStop, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useRef, useEffect } from "react";
import { useInterview } from "@/hooks/use-interview";
import { api } from "@/services/api";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function InterviewSimulation() {
  const [micEnabled, setMicEnabled] = useState(true);
  const [cameraEnabled, setCameraEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  
  // 使用面试状态Hook
  const { isRunning, status, startInterview, stopInterview, error, isLoading } = useInterview();

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
    return 'text-error';
  };

  // 获取注意力条颜色
  const getAttentionBarColor = (score: number): string => {
    if (score >= 70) return 'bg-success';
    if (score >= 50) return 'bg-warning';
    return 'bg-error';
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
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      micEnabled 
                        ? 'bg-success/10 border border-success/20 hover:bg-success/20' 
                        : 'bg-muted border border-border hover:bg-muted/80'
                    }`}
                    onClick={() => setMicEnabled(!micEnabled)}
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
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      cameraEnabled 
                        ? 'bg-success/10 border border-success/20 hover:bg-success/20' 
                        : 'bg-muted border border-border hover:bg-muted/80'
                    }`}
                    onClick={() => setCameraEnabled(!cameraEnabled)}
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
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      audioEnabled 
                        ? 'bg-success/10 border border-success/20 hover:bg-success/20' 
                        : 'bg-muted border border-border hover:bg-muted/80'
                    }`}
                    onClick={() => setAudioEnabled(!audioEnabled)}
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
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      isRunning 
                        ? 'bg-error/10 border border-error/20 hover:bg-error/20' 
                        : 'bg-muted border border-border hover:bg-muted/80'
                    }`}
                    onClick={() => isRunning ? stopInterview() : startInterview()}
                    disabled={isLoading}
                  >
                    {isRunning ? (
                      <Circle className="w-4 h-4 text-error fill-error" />
                    ) : (
                      <CircleStop className="w-4 h-4 text-muted-foreground" />
                    )}
                    <span className={`text-sm ${isRunning ? 'text-error' : 'text-muted-foreground'}`}>
                      {isRunning ? '录制中' : '录制已停止'}
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

              <Card className="flex-1">
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
                  <Button variant="outline" className="w-full text-sm justify-start">
                    暂停面试
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
                  <img 
                    src={api.getVideoStreamUrl()} 
                    alt="面试视频" 
                    className="w-full h-full object-cover"
                  />
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
                <div className={`absolute top-4 right-4 ${isRunning ? 'bg-success/90' : 'bg-muted/90'} backdrop-blur-sm px-4 py-2 rounded-lg text-base font-medium ${isRunning ? 'text-success-foreground' : 'text-muted-foreground'} flex items-center gap-2`}>
                  <div className={`w-2.5 h-2.5 rounded-full ${isRunning ? 'bg-success-foreground animate-pulse' : 'bg-muted'}`} />
                  {isRunning ? '录制中' : '未录制'}
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
                  <span className="font-medium">{status ? formatTime(status.session_time) : "00:00"}</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full" 
                    style={{ width: status ? `${Math.min(100, (status.session_time / 1800) * 100)}%` : '0%' }} 
                  />
                </div>
              </div>
              <div className="text-xs text-muted-foreground">
                剩余时间：{status ? formatTime(Math.max(0, 1800 - status.session_time)) : "30:00"}
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
                  {status ? Math.round(status.attention_score) : 80}
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${status ? getAttentionBarColor(status.attention_score) : 'bg-muted'}`} 
                  style={{ width: status ? `${status.attention_score}%` : '80%' }} 
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