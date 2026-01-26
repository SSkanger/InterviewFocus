import pyttsx3
import time
from datetime import datetime
import random
import threading


class VoiceFeedback:
    """语音反馈系统 - 提供智能语音反馈"""
    
    def __init__(self, rate=160, volume=0.8):
        """初始化语音反馈系统
        
        Args:
            rate: 语速（默认160）
            volume: 音量（默认0.8）
        """
        # 兼容旧版本代码的engine属性
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # 存储当前正在播放语音的引擎实例
        self.current_engine = None
        self.voice_lock = threading.Lock()
        
        # 冷却时间设置
        self.last_speak_time = 0
        self.default_cooldown = 4.0  # 默认冷却时间4秒
        self.urgent_cooldown = 2.0   # 紧急提示冷却时间2秒
        
        # 反馈历史记录
        self.feedback_history = []
        self.max_history = 10
        
        # 面试问题相关
        self.current_question = None
        self.question_start_time = None
        self.question_duration = 300  # 5分钟，单位秒
        self.question_feedback = [
            "回答得很好，继续下一个问题",
            "你的回答很清晰，继续努力",
            "思路不错，让我们继续",
            "很好，接下来是下一个问题",
            "回答得很全面，继续下一个问题"
        ]
        
        # 预设反馈语料
        self.gaze_feedback = [
            "请保持眼神交流，注视摄像头",
            "面试时请看着摄像头，展现自信",
            "保持眼神接触，这很重要",
            "请看着摄像头，与面试官保持交流"
        ]
        
        self.pose_feedback = {
            "抬头": "请保持头部正直，避免频繁抬头",
            "低头": "请保持抬头挺胸的姿态",
            "歪头": "请保持头部正直，避免歪头",
            "转头": "请保持面向摄像头，展现专注"
        }
        
        self.gesture_feedback = {
            "摸脸": "请避免摸脸，保持专业形象",
            "摸下巴": "请避免摸下巴，保持自信姿态",
            "摸头发": "请避免摸头发，保持专业形象",
            "托腮": "请避免托腮，保持专注姿态"
        }
        
        self.encouragement_feedback = [
            "做得很好，继续保持",
            "你的表现很棒，继续保持专注",
            "很好，你的状态越来越好了",
            "继续保持，你做得很好"
        ]
        
        print("✅ 语音反馈系统已初始化")
        
    def ask_question(self, question, position=""):
        """根据职业提问
        
        Args:
            question: 问题文本
            position: 面试岗位（可选）
            
        Returns:
            bool: 是否成功播放语音
        """
        # 设置当前问题和开始时间
        self.current_question = question
        self.question_start_time = datetime.now().timestamp()
        
        # 构建问题文本
        question_text = f"{question}，你有5分钟的时间作答"
        if position:
            question_text = f"{position}面试问题：{question_text}"
        
        # 播放问题
        result = self.speak(question_text, urgent=False, cooldown=0)  # 提问时无冷却
        
        # 启动5分钟倒计时线程
        self._start_question_timer()
        
        return result
        
    def _start_question_timer(self):
        """启动问题倒计时计时器
        """
        def timer_thread():
            # 等待5分钟
            time.sleep(self.question_duration)
            
            # 5分钟后给出反馈
            self._give_question_feedback()
        
        # 创建并启动线程
        thread = threading.Thread(target=timer_thread)
        thread.daemon = True
        thread.start()
        
    def _give_question_feedback(self):
        """给出问题反馈
        """
        # 随机选择一个反馈
        feedback = random.choice(self.question_feedback)
        self.speak(feedback, urgent=False, cooldown=0)
        
    def get_remaining_time(self):
        """获取当前问题的剩余时间
        
        Returns:
            float: 剩余时间（秒），如果没有当前问题则返回0
        """
        if not self.question_start_time:
            return 0
        
        elapsed = datetime.now().timestamp() - self.question_start_time
        remaining = max(0, self.question_duration - elapsed)
        return remaining
        
    def is_question_active(self):
        """检查当前是否有活跃的问题
        
        Returns:
            bool: 是否有活跃的问题
        """
        return self.current_question is not None and self.get_remaining_time() > 0
    
    def stop_speaking(self):
        """停止当前正在播放的语音
        """
        with self.voice_lock:
            if self.current_engine:
                try:
                    # 停止当前引擎的语音播放
                    self.current_engine.stop()
                    print(f"⏹️  已停止当前语音播放")
                except Exception as e:
                    print(f"❌ 停止语音播放失败: {e}")
                finally:
                    self.current_engine = None
    
    def speak(self, text, urgent=False, cooldown=None):
        """语音输出（带冷却时间）
        
        Args:
            text: 要说的文本
            urgent: 是否为紧急提示（影响冷却时间）
            cooldown: 自定义冷却时间（覆盖默认值）
            
        Returns:
            bool: 是否成功播放语音
        """
        current_time = datetime.now().timestamp()
        
        # 确定冷却时间
        if cooldown is not None:
            actual_cooldown = cooldown
        elif urgent:
            actual_cooldown = self.urgent_cooldown
        else:
            actual_cooldown = self.default_cooldown
        
        # 打印调试信息
        print(f"🔊 语音调试: 准备播放 '{text}'")
        print(f"🔊 语音调试: 当前时间 {current_time}, 上次说话时间 {self.last_speak_time}")
        print(f"🔊 语音调试: 冷却时间设置 {actual_cooldown}, 时间差 {current_time - self.last_speak_time}")
        
        # 无论冷却时间如何，强制播放语音（仅用于面试开始场景）
        # 因为这是面试开始的关键语音，必须确保播放
        print(f"🔊 语音提示: {text}")
        success = False
        
        # 停止当前正在播放的语音
        self.stop_speaking()
        
        # 使用新的engine实例，确保线程安全
        try:
            with self.voice_lock:
                # 每次调用都创建一个新的engine实例，避免线程冲突
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.8)
                self.current_engine = engine
                
            engine.say(text)
            engine.runAndWait()
            
            with self.voice_lock:
                if self.current_engine == engine:
                    self.current_engine = None
            
            success = True
            print(f"✅ 语音播放成功")
        except Exception as e:
            print(f"❌ 语音播放失败: {e}")
            with self.voice_lock:
                self.current_engine = None
            
            # 尝试使用备用方法
            try:
                # 再次尝试，可能是临时问题
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.8)
                engine.say(text)
                engine.runAndWait()
                print("🔧 语音播放成功（备用方法）")
                success = True
            except Exception as retry_error:
                print(f"❌ 语音播放再次失败: {retry_error}")
                success = False
        
        if success:
            # 更新最后说话时间
            self.last_speak_time = current_time
            
            # 记录反馈历史
            self.feedback_history.append({
                'time': current_time,
                'text': text,
                'urgent': urgent
            })
            
            # 限制历史记录大小
            if len(self.feedback_history) > self.max_history:
                self.feedback_history.pop(0)
        
        return success
    
    def give_gaze_feedback(self, urgent=True):
        """提供视线反馈
        
        Args:
            urgent: 是否为紧急提示
            
        Returns:
            bool: 是否成功播放语音
        """
        # 随机选择一个反馈语
        feedback = random.choice(self.gaze_feedback)
        return self.speak(feedback, urgent=urgent)
    
    def give_pose_feedback(self, pose_type, urgent=True):
        """提供姿态反馈
        
        Args:
            pose_type: 姿态类型（抬头、低头、歪头、转头）
            urgent: 是否为紧急提示
            
        Returns:
            bool: 是否成功播放语音
        """
        # 获取对应的反馈语
        feedback = self.pose_feedback.get(pose_type, "请保持正确姿势")
        return self.speak(feedback, urgent=urgent)
    
    def give_gesture_feedback(self, gesture_type, urgent=True):
        """提供手势反馈
        
        Args:
            gesture_type: 手势类型（摸脸、摸下巴、摸头发、托腮）
            urgent: 是否为紧急提示
            
        Returns:
            bool: 是否成功播放语音
        """
        # 获取对应的反馈语
        feedback = self.gesture_feedback.get(gesture_type, "请避免不必要的小动作")
        return self.speak(feedback, urgent=urgent)
    
    def give_encouragement(self, urgent=False):
        """提供鼓励反馈
        
        Args:
            urgent: 是否为紧急提示
            
        Returns:
            bool: 是否成功播放语音
        """
        # 随机选择一个鼓励语
        feedback = random.choice(self.encouragement_feedback)
        return self.speak(feedback, urgent=urgent)
    
    def start_session(self, position="Python开发工程师"):
        """开始会话的欢迎语
        
        Args:
            position: 面试岗位
            
        Returns:
            bool: 是否成功播放语音
        """
        return self.speak(f"{position}面试练习开始，请保持专业姿态", urgent=False, cooldown=0)
    
    def end_session(self):
        """结束会话的结束语
        
        Returns:
            bool: 是否成功播放语音
        """
        return self.speak("面试练习结束，感谢您的使用", urgent=False)
    
    def test_voice(self):
        """测试语音功能
        
        Returns:
            bool: 是否成功播放语音
        """
        return self.speak("这是语音测试，系统工作正常", urgent=False)
    
    def get_feedback_count(self, time_window=300):
        """获取指定时间窗口内的反馈次数
        
        Args:
            time_window: 时间窗口（秒），默认5分钟
            
        Returns:
            dict: 各类反馈的次数
        """
        current_time = datetime.now().timestamp()
        recent_feedback = [
            f for f in self.feedback_history 
            if current_time - f['time'] <= time_window
        ]
        
        count = {
            'total': len(recent_feedback),
            'urgent': len([f for f in recent_feedback if f['urgent']]),
            'normal': len([f for f in recent_feedback if not f['urgent']])
        }
        
        return count
    
    def set_cooldown(self, default=None, urgent=None):
        """设置冷却时间
        
        Args:
            default: 默认冷却时间（秒）
            urgent: 紧急提示冷却时间（秒）
        """
        if default is not None:
            self.default_cooldown = default
        if urgent is not None:
            self.urgent_cooldown = urgent
        
        print(f"语音冷却时间已更新: 默认{self.default_cooldown}秒, 紧急{self.urgent_cooldown}秒")
    
    def get_latest_feedback(self):
        """获取最新的反馈内容
        
        Returns:
            str: 最新的反馈文本，如果没有则返回None
        """
        if self.feedback_history:
            return self.feedback_history[-1]['text']
        return None