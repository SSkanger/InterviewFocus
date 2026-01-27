import requests
import time
from datetime import datetime
import random
import threading
import os
import io
import winsound
import subprocess
import asyncio

# 尝试导入 pygame 用于后台播放 MP3
try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    print("⚠️ pygame 库不可用，将使用系统播放器")

# 尝试导入Edge TTS
try:
    import edge_tts
    edgetts_available = True
    print("✅ Edge TTS库可用，将作为首选语音合成方案")
except ImportError:
    edgetts_available = False
    print("⚠️ Edge TTS库不可用")

# 导入pyttsx3作为备用语音合成方案
try:
    import pyttsx3
    pyttsx3_available = True
    print("✅ pyttsx3库可用，将作为备用语音合成方案")
except ImportError:
    pyttsx3_available = False
    print("⚠️ pyttsx3备用方案不可用")


class VoiceFeedback:
    """语音反馈系统 - 提供智能语音反馈"""
    
    def __init__(self):
        """初始化语音反馈系统
        """
        # 存储当前正在播放语音的状态
        self.is_speaking = False
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
        
        # 初始化Edge TTS
        self.edgetts_available = edgetts_available
        
        # 初始化pyttsx3引擎（备用方案）
        self.pyttsx3_engine = None
        if pyttsx3_available:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', 160)
                self.pyttsx3_engine.setProperty('volume', 0.8)
                print("✅ pyttsx3引擎初始化成功")
            except Exception as e:
                print(f"⚠️ pyttsx3引擎初始化失败: {e}")
                self.pyttsx3_engine = None
        
        print("✅ 语音反馈系统已初始化")
        if self.edgetts_available:
            print(f"🔄 将使用Edge TTS生成语音")
        if self.pyttsx3_engine:
            print("🔧 已准备pyttsx3作为备用语音合成方案")
        else:
            print("⚠️ pyttsx3备用方案不可用")
        
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
    
    def stop_speaking(self):
        """停止当前正在播放的语音
        
        注意：CosyVoice API是异步的，无法直接停止正在播放的语音
        这里仅更新状态标记
        """
        with self.voice_lock:
            if self.is_speaking:
                print(f"⏹️  已标记语音播放为停止状态")
                self.is_speaking = False
    
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
        
        # 检查冷却时间
        if current_time - self.last_speak_time < actual_cooldown and not urgent:
            print(f"🔊 语音提示: 冷却时间内，跳过播放 '{text}'")
            return False
        
        print(f"🔊 语音提示: {text}")
        success = False
        
        # 停止当前正在播放的语音
        self.stop_speaking()
        
        try:
            with self.voice_lock:
                self.is_speaking = True
            
            # 优先使用Edge TTS
            if self.edgetts_available:
                print(f"🔄 使用Edge TTS生成语音，说话人: 中文女")
                temp_filename = None
                try:
                    # 创建临时文件
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_filename = temp_file.name
                    
                    # 生成语音
                    async def generate_and_play():
                        communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")  # 中文女声
                        await communicate.save(temp_filename)
                    
                    # 运行异步函数
                    asyncio.run(generate_and_play())
                    
                    # 播放音频文件
                    print("播放语音...")
                    try:
                        if temp_filename and os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                            # 确保文件存在且不为空
                            print(f"音频文件大小: {os.path.getsize(temp_filename)} 字节")
                            
                            # 优先使用 pygame 后台播放
                            if pygame_available:
                                print("使用 pygame 后台播放...")
                                try:
                                    # 初始化 pygame 混音器
                                    pygame.mixer.init()
                                    pygame.mixer.music.load(temp_filename)
                                    pygame.mixer.music.play()
                                    
                                    # 等待播放完成
                                    while pygame.mixer.music.get_busy():
                                        time.sleep(0.1)
                                    
                                    print("✅ pygame 后台播放完成")
                                    success = True
                                    print(f"✅ Edge TTS调用成功")
                                except Exception as pygame_e:
                                    print(f"⚠️ pygame 播放失败: {pygame_e}")
                                    # 回退到系统播放器
                                    if os.name == 'nt':
                                        os.startfile(temp_filename)
                                        print("✅ 系统播放器已启动")
                                        # 等待播放完成
                                        estimated_duration = len(text) / 5 + 2
                                        time.sleep(estimated_duration)
                                        success = True
                                        print(f"✅ Edge TTS调用成功")
                                    else:
                                        success = False
                            else:
                                # 使用系统默认播放器
                                print("使用系统播放器播放...")
                                if os.name == 'nt':
                                    os.startfile(temp_filename)
                                    print("✅ 系统播放器已启动")
                                    # 等待播放完成
                                    estimated_duration = len(text) / 5 + 2
                                    time.sleep(estimated_duration)
                                    success = True
                                    print(f"✅ Edge TTS调用成功")
                                else:
                                    success = False
                        else:
                            print(f"⚠️ 音频文件不存在或为空: {temp_filename}")
                            success = False
                    except Exception as play_e:
                        print(f"⚠️ 播放音频失败: {play_e}")
                        success = False
                except Exception as e:
                    print(f"⚠️ Edge TTS调用失败，切换到pyttsx3: {e}")
                    success = False
                finally:
                    # 删除临时文件
                    try:
                        if temp_filename and os.path.exists(temp_filename):
                            # 等待额外时间确保播放器已读取文件
                            time.sleep(1)
                            os.unlink(temp_filename)
                            print(f"✅ 临时文件已清理: {temp_filename}")
                    except Exception as del_e:
                        print(f"⚠️ 删除临时文件失败: {del_e}")
            else:
                print(f"⚠️ Edge TTS不可用，使用pyttsx3")
                success = False
            
            # 如果Edge TTS失败，使用pyttsx3作为备用方案
            if not success and self.pyttsx3_engine:
                print(f"🔄 尝试使用pyttsx3作为备用语音方案")
                try:
                    self.pyttsx3_engine.say(text)
                    self.pyttsx3_engine.runAndWait()
                    success = True
                    print(f"✅ pyttsx3语音播放成功")
                except Exception as pyttsx3_e:
                    print(f"⚠️ pyttsx3语音播放失败: {pyttsx3_e}")
                    success = False
            
            if not success:
                print(f"⚠️ 语音合成失败，跳过播放")
                success = False
        finally:
            with self.voice_lock:
                self.is_speaking = False
        
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
