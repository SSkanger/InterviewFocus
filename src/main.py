# src/main.py - 面试助手v0.2
import cv2
import pyttsx3
import numpy as np
import time
from datetime import datetime

# 导入自定义模块
from camera_utils import CameraManager
from voice_utils import VoiceFeedback
from ui_manager import UIManager

# 导入检测模块
try:
    from detection.face_detector import FaceDetector
    from detection.gaze_detector import GazeDetector
    from detection.pose_detector import PoseDetector
    from detection.gesture_detector import GestureDetector
    DETECTION_MODULES_AVAILABLE = True
    print("✅ 检测模块加载成功")
except ImportError as e:
    DETECTION_MODULES_AVAILABLE = False
    print(f"⚠️ 检测模块加载失败: {e}")
    print("将使用模拟数据运行")

class InterviewCoachV2:
    """面试助手 - 版本2.0（集成检测功能）"""

    def __init__(self, use_ui=True):
        # 初始化摄像头管理器
        self.camera = CameraManager(camera_id=0, resolution=(640, 480), fps=30)
        
        # 初始化语音反馈系统
        self.voice = VoiceFeedback(rate=160, volume=0.8)
        # 保存语音引擎的引用，方便直接使用
        self.engine = self.voice.engine
        
        # 初始化UI管理器 - 仅在非Web环境下使用
        self.ui = None
        if use_ui:
            # 初始化UI管理器 - 窗口尺寸与摄像头分辨率匹配
            self.ui = UIManager(window_name="Interview Coach", window_size=(640, 480))
        
        # 初始化检测器（如果模块可用）
        self.detection_enabled = DETECTION_MODULES_AVAILABLE
        if self.detection_enabled:
            self.face_detector = FaceDetector()
            self.gaze_detector = GazeDetector()
            self.pose_detector = PoseDetector()
            self.gesture_detector = GestureDetector()
            print("✅ 所有检测器已初始化")
        else:
            print("⚠️ 检测器不可用，将使用模拟数据")

        # 状态变量
        self.is_running = False
        self.start_time = None
        self.frame_count = 0
        self.last_speak_time = 0
        
        # 检测状态
        self.face_detected = False
        self.gaze_status = "正常"
        self.pose_status = "正常"
        self.gesture_status = "无"
        self.attention_score = 100.0  # 初始分数设为满分
        
        # 统计数据
        self.gaze_away_count = 0
        self.pose_issue_count = 0
        self.gesture_count = 0

        print("✅ 面试助手v2.0已初始化")
        print("Tips: Press 's' to start/stop, 'q' to exit, 't' to test voice")

    def speak(self, text, urgent=False):
        """语音输出（带冷却时间）"""
        current_time = datetime.now().timestamp()

        # 冷却时间：紧急提示2秒，普通提示4秒
        cooldown = 2.0 if urgent else 4.0

        if current_time - self.last_speak_time > cooldown:
            print(f"🔊 语音提示: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            self.last_speak_time = current_time
            return True
        return False

    def draw_ui(self, frame):
        """绘制UI界面
        
        Args:
            frame: 视频帧
            
        Returns:
            带UI的视频帧
        """
        # 如果UI未初始化，直接返回原始帧
        if not self.ui:
            return frame
            
        # 绘制顶部状态栏
        frame = self.ui.draw_top_bar(frame)
        
        # 绘制右侧信息面板
        status_info = {
            'status': '正常' if self.attention_score >= 70 else '注意力不集中',
            'attention_score': int(self.attention_score),
            'gaze_direction': self.gaze_status,
            'posture': self.pose_status,
            'gesture': self.gesture_status,
            'look_away_count': self.gaze_away_count,
            'bad_posture_count': self.pose_issue_count,
            'gesture_count': self.gesture_count
        }
        frame = self.ui.draw_side_panel(frame, status_info)
        
        # 绘制底部信息栏
        feedback_text = self.voice.get_latest_feedback() or "系统运行中..."
        frame = self.ui.draw_bottom_bar(frame, feedback_text)
        
        # 绘制注意力仪表盘
        frame = self.ui.draw_attention_meter(frame, self.attention_score)
        
        # 如果检测到面部，绘制关键点和视线方向
        if self.face_detected and self.detection_enabled:
            # 获取面部关键点
            has_face, landmarks, _ = self.face_detector.detect(frame)
            if has_face and landmarks:
                frame = self.ui.draw_face_landmarks(frame, landmarks)
            
            # 获取视线检测结果
            is_looking, offset_ratio, annotated_frame = self.gaze_detector.detect_gaze(frame)
            if is_looking is not None:
                # 使用带标注的图像
                frame = annotated_frame
        
        # 添加时间戳
        frame = self.ui.add_timestamp(frame)
        
        # 如果注意力分数过低，添加警告
        if self.attention_score < 50:
            frame = self.ui.add_warning(frame, "注意力不集中，请集中精神！")
        
        return frame

    def run(self):
        """主循环"""
        print("▶️ Starting main loop...")
        
        # 打开摄像头
        if not self.camera.open():
            print("❌ 无法打开摄像头")
            return
        
        # 创建UI窗口
        self.ui.create_window()
        
        # 主循环
        while True:
            # 读取摄像头帧
            ret, frame = self.camera.read_frame()
            if not ret:
                print("❌ 无法读取摄像头画面")
                break
            
            self.frame_count += 1
            
            # 如果正在运行，进行检测和更新
            if self.is_running:
                self._update_detection(frame)
                self._update_feedback()
            
            # 获取会话时间和FPS
            session_time = 0
            fps = self.camera.fps_actual
            if self.start_time:
                session_time = (datetime.now() - self.start_time).total_seconds()
            
            # 绘制UI
            frame = self.draw_ui(frame)
            
            # 显示画面
            cv2.imshow(self.ui.window_name, frame)
            
            # 键盘监听
            key = cv2.waitKey(1) & 0xFF
            
            # 's'键：开始/停止
            if key == ord('s'):
                self.is_running = not self.is_running
                if self.is_running:
                    self.start_time = datetime.now()
                    self._reset_statistics()
                    self.voice.start_session()
                    print("⏺️ Started recording...")
                else:
                    self.voice.end_session()
                    print("⏹️ Stopped recording")
            
            # 't'键：测试语音
            elif key == ord('t'):
                self.voice.test_voice()
            
            # 'q'键：退出
            elif key == ord('q'):
                self.voice.end_session()
                break
        
        # 清理资源
        self.camera.close()
        self.ui.destroy_window()
        print("👋 Program exited")
    
    def _update_detection(self, frame):
        """更新检测结果
        
        Args:
            frame: 图像帧
        """
        if not self.detection_enabled:
            # 模拟检测数据
            self._simulate_detection()
            return
        
        # 面部检测 - 禁用绘制以提高性能
        has_face, landmarks, _ = self.face_detector.detect(frame, draw_annotations=False)
        self.face_detected = has_face
        
        # 检查面部检测结果和关键点
        if not self.face_detected or landmarks is None:
            # 没有检测到面部或关键点无效，重置其他检测状态
            self.gaze_status = "未检测到面部"
            self.pose_status = "未检测到面部"
            self.gesture_status = "未检测到面部"
            self.attention_score = max(0, self.attention_score - 2)
            return
        
        try:
            # 视线检测（需要有效的面部关键点）- 禁用绘制
            is_looking, offset_ratio, _ = self.gaze_detector.detect_gaze(frame, draw_annotations=False)
            self.gaze_status = self.gaze_detector.get_gaze_status_text(is_looking, offset_ratio)
            if self.gaze_status != "正常":
                self.gaze_away_count += 1
        except Exception as e:
            print(f"视线检测失败: {e}")
            self.gaze_status = "检测失败"
        
        try:
            # 姿态检测 - 禁用绘制
            pose_status, pose_angle, _ = self.pose_detector.detect_pose(frame, draw_annotations=False)
            self.pose_status = self.pose_detector.get_pose_status_text(pose_status)
            if self.pose_status != "良好":
                self.pose_issue_count += 1
        except Exception as e:
            print(f"姿态检测失败: {e}")
            self.pose_status = "检测失败"
        
        try:
            # 手势检测 - 禁用绘制
            gesture_type, confidence, _ = self.gesture_detector.detect_gestures(frame, draw_annotations=False)
            self.gesture_status = self.gesture_detector.get_gesture_status_text(gesture_type, confidence)
            if self.gesture_status != "无小动作":
                self.gesture_count += 1
        except Exception as e:
            print(f"手势检测失败: {e}")
            self.gesture_status = "检测失败"
        
        # 计算注意力分数
        self._calculate_attention_score()
    
    def _simulate_detection(self):
        """模拟检测结果（当检测模块不可用时）"""
        import random
        
        # 只在每30帧更新一次模拟数据（约1秒更新一次，假设30fps）
        if self.frame_count % 30 != 0:
            return
        
        # 模拟面部检测（95%概率成功）
        self.face_detected = random.random() < 0.95
        
        if not self.face_detected:
            self.gaze_status = "未检测到面部"
            self.pose_status = "未检测到面部"
            self.gesture_status = "未检测到面部"
            self.attention_score = max(0, self.attention_score - random.uniform(10, 20))
            return
        
        # 模拟视线检测（80%概率正常）
        if random.random() < 0.8:
            self.gaze_status = "正常"
        else:
            self.gaze_status = "视线偏离"
            self.gaze_away_count += 1
        
        # 模拟姿态检测（85%概率正常）
        if random.random() < 0.85:
            self.pose_status = "良好"
        else:
            self.pose_status = random.choice(["⚠️ 请勿频繁抬头", "⚠️ 请保持抬头挺胸", "⚠️ 请保持头部正直", "⚠️ 请保持面向摄像头"])
            self.pose_issue_count += 1
        
        # 模拟手势检测（90%概率无小动作）
        if random.random() < 0.9:
            self.gesture_status = "无小动作"
        else:
            self.gesture_status = random.choice(["⚠️ 请避免摸脸", "⚠️ 请避免摸下巴", "⚠️ 请避免摸头发", "⚠️ 请避免托腮"])
            self.gesture_count += 1
        
        # 计算注意力分数
        self._calculate_attention_score()
    
    def _calculate_attention_score(self):
        """计算注意力分数"""
        # 基础分数
        score = 100.0  # 从满分开始，根据问题扣分
        
        # 根据检测结果调整分数
        if not self.face_detected:
            score -= 40  # 没有检测到面部扣分更多
        else:
            if self.gaze_status != "正常":
                score -= 25  # 视线不正常扣分较多
            if self.pose_status != "良好":
                score -= 20  # 姿态不好扣分中等
            if self.gesture_status != "无小动作":
                score -= 15  # 有小动作扣分较少
        
        # 添加随机波动，使分数更自然
        import random
        score += random.uniform(-5, 5)
        
        # 限制分数范围
        self.attention_score = max(0, min(100, score))
    
    def _update_feedback(self):
        """更新语音反馈"""
        # 如果没有检测到面部，提醒用户
        if not self.face_detected:
            self.voice.speak("请调整位置，确保面部在摄像头范围内", urgent=True)
            return
        
        # 根据视线状态提供反馈
        if self.gaze_status != "正常":
            self.voice.give_gaze_feedback(urgent=True)
        
        # 根据姿态状态提供反馈
        if self.pose_status != "良好":
            self.voice.give_pose_feedback(self.pose_status, urgent=True)
        
        # 根据手势状态提供反馈
        if self.gesture_status != "无小动作":
            self.voice.give_gesture_feedback(self.gesture_status, urgent=True)
        
        # 如果注意力分数较高，提供鼓励
        if self.attention_score >= 85 and self.frame_count % 300 == 0:  # 每10秒一次
            self.voice.give_encouragement(urgent=False)
    
    def get_session_time(self):
        """获取会话时间"""
        if not self.start_time:
            return 0
        return (datetime.now() - self.start_time).total_seconds()
    
    def process_frame(self, frame):
        """处理单帧图像，用于Web API
        
        Args:
            frame: 图像帧
            
        Returns:
            检测结果字典
        """
        # 更新检测结果
        self._update_detection(frame)
        
        # 返回检测结果
        return {
            'attention_score': self.attention_score,
            'gaze_status': self.gaze_status,
            'pose_status': self.pose_status,
            'gesture_status': self.gesture_status,
            'face_detected': self.face_detected,
            'gaze_away_count': self.gaze_away_count,
            'pose_issue_count': self.pose_issue_count,
            'gesture_count': self.gesture_count,
            'session_time': self.get_session_time()
        }
    
    def _reset_statistics(self):
        """重置统计数据"""
        self.gaze_away_count = 0
        self.pose_issue_count = 0
        self.gesture_count = 0
        self.attention_score = 100.0  # 初始分数设为满分
        print("Statistics have been reset")


def main():
    """程序入口"""
    print("=" * 60)
    print("Interview Coach - Attention Monitor v0.2")
    print("=" * 60)
    print("\nFeatures:")
    print("1. Real-time face detection and keypoint extraction")
    print("2. Gaze direction detection and reminder")
    print("3. Head posture analysis and feedback")
    print("4. Small gesture detection and prompts")
    print("5. Intelligent voice feedback system")
    print("\nCurrent Version: Integrated Detection (v0.2)")
    print("-" * 60)

    # 创建助手实例
    coach = InterviewCoachV2()

    # 运行主程序
    try:
        coach.run()
    except KeyboardInterrupt:
        print("\nUser interrupted the program")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        import traceback
        traceback.print_exc()

    print("\nThank you for using!")


if __name__ == "__main__":
    main()