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
        
        # 注意力历史记录
        self.attention_history = []

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
        """计算注意力分数 - 采用加权综合评分机制"""
        # 权重配置（可根据实际需求调整）
        weights = {
            'face_detection': 0.3,    # 面部检测占30%
            'gaze_direction': 0.35,    # 视线方向占35%
            'posture': 0.2,            # 姿态占20%
            'gesture': 0.15            # 手势占15%
        }
        
        # 初始各项得分
        face_score = 100.0
        gaze_score = 100.0
        posture_score = 100.0
        gesture_score = 100.0
        
        # 面部检测评分
        if not self.face_detected:
            face_score = 0.0  # 未检测到面部直接0分
        
        # 视线方向评分
        if self.gaze_status == "正常":
            gaze_score = 100.0
        elif self.gaze_status == "轻微偏移":
            gaze_score = 70.0
        elif self.gaze_status == "明显偏移":
            gaze_score = 40.0
        else:  # 严重偏移或检测失败
            gaze_score = 10.0
        
        # 姿态评分
        if self.pose_status == "良好":
            posture_score = 100.0
        elif "抬头" in self.pose_status:
            posture_score = 75.0
        elif "低头" in self.pose_status:
            posture_score = 70.0
        elif "歪头" in self.pose_status:
            posture_score = 65.0
        elif "转头" in self.pose_status:
            posture_score = 60.0
        else:  # 检测失败
            posture_score = 50.0
        
        # 手势评分
        if self.gesture_status == "无小动作":
            gesture_score = 100.0
        else:  # 有小动作
            gesture_score = 70.0
        
        # 计算加权综合得分
        weighted_score = (
            face_score * weights['face_detection'] +
            gaze_score * weights['gaze_direction'] +
            posture_score * weights['posture'] +
            gesture_score * weights['gesture']
        )
        
        # 时间衰减因子（持续注意力奖励）
        # 如果注意力持续良好，分数会缓慢上升
        session_time = self.get_session_time()
        if session_time > 0:
            # 每10秒增加1分，最多增加10分
            time_bonus = min(10.0, session_time / 10.0)
            weighted_score = min(100.0, weighted_score + time_bonus)
        
        # 平滑分数变化（避免突然跳变）
        alpha = 0.8  # 平滑系数，0-1之间，越大越平滑
        self.attention_score = alpha * self.attention_score + (1 - alpha) * weighted_score
        
        # 限制分数范围
        self.attention_score = max(0, min(100, self.attention_score))
        
        # 记录历史分数（用于数据分析）
        current_time = datetime.now().timestamp()
        if not hasattr(self, 'attention_history'):
            self.attention_history = []
        self.attention_history.append({
            'timestamp': current_time,
            'score': self.attention_score,
            'face_score': face_score,
            'gaze_score': gaze_score,
            'posture_score': posture_score,
            'gesture_score': gesture_score
        })
        
        # 限制历史记录长度（最多保存1000条）
        if len(self.attention_history) > 1000:
            self.attention_history.pop(0)
    
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
        self.attention_history = []  # 重置历史记录
        self.attention_states = {
            'high': 0,  # 高度集中（85-100分）
            'medium': 0,  # 中等集中（60-84分）
            'low': 0,  # 注意力分散（0-59分）
            'face_missing': 0  # 未检测到面部
        }
        print("Statistics have been reset")
    
    def save_final_state(self):
        """保存最终状态，确保所有数据都已正确处理"""
        try:
            # 确保注意力历史记录已初始化
            if not hasattr(self, 'attention_history'):
                self.attention_history = []
            
            # 打印最终状态摘要
            print(f"📊 保存最终状态: ")
            print(f"   - 总记录数: {len(self.attention_history)}")
            print(f"   - 视线离开次数: {self.gaze_away_count}")
            print(f"   - 姿态问题次数: {self.pose_issue_count}")
            print(f"   - 手势次数: {self.gesture_count}")
            print(f"   - 面试时长: {self.get_session_time()}秒")
            
        except Exception as e:
            print(f"❌ 保存最终状态时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def get_attention_analysis(self):
        """获取注意力分析报告"""
        print(f"📊 get_attention_analysis 被调用")
        print(f"   - attention_history 存在: {hasattr(self, 'attention_history')}")
        if hasattr(self, 'attention_history'):
            print(f"   - attention_history 长度: {len(self.attention_history)}")
        
        # 初始化注意力状态分布
        attention_states = {
            'high': 0,  # 高度集中（85-100分）
            'medium': 0,  # 中等集中（60-84分）
            'low': 0,  # 注意力分散（0-59分）
            'face_missing': 0  # 未检测到面部
        }
        
        # 初始化统计数据
        total_records = 0
        avg_face = 0
        avg_gaze = 0
        avg_posture = 0
        avg_gesture = 0
        final_attention_score = self.attention_score
        
        # 统计注意力状态分布和计算平均值
        if hasattr(self, 'attention_history') and self.attention_history:
            attention_history = self.attention_history
            total_records = len(attention_history)
            print(f"   - 处理 {total_records} 条记录")
            
            # 统计注意力状态
            for record in attention_history:
                score = record['score']
                if score >= 85:
                    attention_states['high'] += 1
                elif score >= 60:
                    attention_states['medium'] += 1
                else:
                    attention_states['low'] += 1
                
                # 统计未检测到面部的情况
                if record['face_score'] == 0:
                    attention_states['face_missing'] += 1
            
            # 计算各项平均分
            face_scores = [record['face_score'] for record in attention_history]
            gaze_scores = [record['gaze_score'] for record in attention_history]
            posture_scores = [record['posture_score'] for record in attention_history]
            gesture_scores = [record['gesture_score'] for record in attention_history]
            
            # 避免除以零的异常
            avg_face = sum(face_scores) / len(face_scores) if len(face_scores) > 0 else 0
            avg_gaze = sum(gaze_scores) / len(gaze_scores) if len(gaze_scores) > 0 else 0
            avg_posture = sum(posture_scores) / len(posture_scores) if len(posture_scores) > 0 else 0
            avg_gesture = sum(gesture_scores) / len(gesture_scores) if len(gesture_scores) > 0 else 0
            
            # 重新计算最终注意力分数（基于所有数据的平均分）
            final_attention_score = sum([record['score'] for record in attention_history]) / len(attention_history) if len(attention_history) > 0 else self.attention_score
        else:
            print(f"   - 没有历史记录，使用默认数据")
        
        # 生成改进建议
        recommendations = []
        
        # 根据各项平均分数生成针对性建议
        if total_records > 0:
            # 基于平均分生成具体建议
            if avg_face < 80:
                recommendations.append("请确保面部始终在摄像头范围内，避免频繁离开画面。建议调整摄像头位置，使面部保持在画面中央。")
            if avg_gaze < 70:
                recommendations.append("请注意保持视线集中在摄像头方向，避免频繁看向其他地方。这有助于展现您的专注态度。")
            if avg_posture < 70:
                recommendations.append("请保持良好的坐姿，避免低头、抬头或歪头。保持背部挺直，有助于展现自信形象。")
            if avg_gesture < 80:
                recommendations.append("请尽量减少不必要的手部动作，保持专业姿态。适当的手势可以增强表达，但过度的动作会分散注意力。")
            
            # 基于注意力状态分布生成建议
            high_ratio = attention_states['high'] / total_records if total_records > 0 else 0
            low_ratio = attention_states['low'] / total_records if total_records > 0 else 0
            
            if high_ratio > 0.7:
                recommendations.append("您在面试过程中表现出高度的注意力集中，继续保持这种良好状态！")
            elif low_ratio > 0.3:
                recommendations.append("您在面试过程中注意力分散的时间较多，建议提前做好准备，减少外界干扰。")
        
        # 如果没有足够的数据，提供通用建议
        if not recommendations:
            recommendations = [
                "保持面部在摄像头范围内，确保清晰可见",
                "保持视线集中在摄像头方向，展现专注态度",
                "保持良好的坐姿，抬头挺胸，展现自信",
                "减少不必要的手部动作，保持专业形象"
            ]
        
        # 生成评分依据
        scoring_criteria = {
            'face_detection': {
                'weight': 0.3,
                'description': "面部检测 - 保持面部在摄像头范围内",
                'current_status': "检测到面部" if self.face_detected else "未检测到面部",
                'average_score': round(avg_face, 2)
            },
            'gaze_direction': {
                'weight': 0.35,
                'description': "视线方向 - 保持视线集中在摄像头",
                'current_status': self.gaze_status,
                'average_score': round(avg_gaze, 2)
            },
            'posture': {
                'weight': 0.2,
                'description': "姿态 - 保持良好的坐姿",
                'current_status': self.pose_status,
                'average_score': round(avg_posture, 2)
            },
            'gesture': {
                'weight': 0.15,
                'description': "手势 - 减少不必要的动作",
                'current_status': self.gesture_status,
                'average_score': round(avg_gesture, 2)
            }
        }
        
        # 生成详细的统计数据
        statistics = {
            'gaze_away_count': self.gaze_away_count,
            'pose_issue_count': self.pose_issue_count,
            'gesture_count': self.gesture_count,
            'session_time': self.get_session_time(),
            'total_records': total_records,
            'attention_state_ratios': {
                'high': round(attention_states['high'] / total_records * 100, 1) if total_records > 0 else 0,
                'medium': round(attention_states['medium'] / total_records * 100, 1) if total_records > 0 else 0,
                'low': round(attention_states['low'] / total_records * 100, 1) if total_records > 0 else 0,
                'face_missing': round(attention_states['face_missing'] / total_records * 100, 1) if total_records > 0 else 0
            }
        }
        
        # 生成面试总结
        interview_summary = ""
        if total_records > 0:
            # 计算注意力集中程度
            if final_attention_score >= 85:
                attention_level = "优秀"
            elif final_attention_score >= 60:
                attention_level = "良好"
            else:
                attention_level = "需要改进"
            
            # 生成总结
            interview_summary = f"您的面试注意力表现{attention_level}，最终得分为{round(final_attention_score, 1)}分。"\
                               f"在面试过程中，您高度集中注意力的时间占比{statistics['attention_state_ratios']['high']}%，"\
                               f"中等集中的时间占比{statistics['attention_state_ratios']['medium']}%，"\
                               f"注意力分散的时间占比{statistics['attention_state_ratios']['low']}%。"\
                               f"建议您重点关注{', '.join([crit['description'].split(' - ')[0] for crit in scoring_criteria.values() if crit['average_score'] < 70])}方面的改进。"
        else:
            interview_summary = "由于面试时间较短或数据不足，无法生成详细的注意力分析报告。建议您延长面试时间以获得更准确的分析结果。"
        
        return {
            'attention_score': round(final_attention_score, 2),
            'attention_states': attention_states,
            'scoring_criteria': scoring_criteria,
            'recommendations': recommendations,
            'statistics': statistics,
            'interview_summary': interview_summary,
            'status': 'success' if total_records > 0 else 'insufficient_data',
            'message': '成功生成注意力分析报告' if total_records > 0 else '数据不足，生成基础分析报告'
        }


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