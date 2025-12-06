import cv2
import numpy as np
import mediapipe as mp
from .face_detector import FaceDetector


class GestureDetector:
    """手势检测器 - 检测小动作（摸脸、摸头发等）"""
    
    def __init__(self, detection_threshold=0.5):
        """初始化手势检测器
        
        Args:
            detection_threshold: 手势检测置信度阈值
        """
        self.face_detector = FaceDetector()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=detection_threshold,
            min_tracking_confidence=0.5
        )
        
        # 状态跟踪
        self.gesture_history = []  # 用于平滑手势状态
        self.history_size = 10    # 历史记录大小
        self.last_gesture_time = 0  # 上次检测到手势的时间
        self.gesture_cooldown = 2  # 手势冷却时间（秒）
        
        print("✅ 手势检测器已初始化")
    
    def detect_gestures(self, frame, face_landmarks=None):
        """检测手势和小动作
        
        Args:
            frame: 输入图像帧
            face_landmarks: 面部关键点（可选，如果不提供会自动检测）
            
        Returns:
            tuple: (手势类型, 置信度, 带标注的图像)
        """
        # 如果没有提供面部关键点，则检测
        if face_landmarks is None:
            has_face, face_landmarks, _ = self.face_detector.detect(frame)
            if not has_face:
                return "无", 0, frame
        
        # 获取面部轮廓
        face_oval = self.face_detector.get_face_oval(face_landmarks)
        
        # 转换为RGB格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像检测手部
        results = self.hands.process(rgb_frame)
        
        # 创建副本用于绘制
        annotated_frame = frame.copy()
        
        # 初始化手势结果
        gesture_type = "无"
        confidence = 0
        
        # 检查是否检测到手部
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 绘制手部关键点
                self.mp_drawing = mp.solutions.drawing_utils
                self.mp_drawing.draw_landmarks(
                    annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # 获取手部关键点坐标
                h, w = frame.shape[:2]
                hand_points = []
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    hand_points.append((x, y))
                
                # 检测手势类型
                detected_gesture, conf = self._classify_gesture(hand_points, face_oval)
                
                # 如果检测到的手势置信度更高，则更新结果
                if conf > confidence:
                    gesture_type = detected_gesture
                    confidence = conf
        
        # 添加到历史记录
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        # 如果检测到非"无"的手势，且距离上次手势时间超过冷却时间
        if gesture_type != "无" and current_time - self.last_gesture_time > self.gesture_cooldown:
            self.gesture_history.append((gesture_type, current_time))
            self.last_gesture_time = current_time
            
            # 限制历史记录大小
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
        
        # 在画面上绘制检测结果
        if gesture_type != "无":
            cv2.putText(annotated_frame, f"手势: {gesture_type} ({confidence:.2f})", 
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return gesture_type, confidence, annotated_frame
    
    def _classify_gesture(self, hand_points, face_oval):
        """分类手势类型
        
        Args:
            hand_points: 手部关键点
            face_oval: 面部轮廓关键点
            
        Returns:
            tuple: (手势类型, 置信度)
        """
        if not hand_points or not face_oval:
            return "无", 0
        
        # 计算手部中心点
        hand_center_x = sum(point[0] for point in hand_points) / len(hand_points)
        hand_center_y = sum(point[1] for point in hand_points) / len(hand_points)
        
        # 计算面部中心点
        face_center_x = sum(point[0] for point in face_oval) / len(face_oval)
        face_center_y = sum(point[1] for point in face_oval) / len(face_oval)
        
        # 计算手部与面部的距离
        distance = np.sqrt((hand_center_x - face_center_x)**2 + (hand_center_y - face_center_y)**2)
        
        # 判断手势类型
        # 1. 摸脸/摸下巴：手部靠近面部
        if distance < 100:
            # 判断是摸脸还是摸下巴
            if hand_center_y > face_center_y:
                return "摸下巴", 0.8
            else:
                return "摸脸", 0.8
        
        # 2. 摸头发：手部在面部上方
        elif hand_center_y < face_center_y - 50 and abs(hand_center_x - face_center_x) < 100:
            return "摸头发", 0.7
        
        # 3. 托腮：手部在面部侧面
        elif abs(hand_center_y - face_center_y) < 50 and abs(hand_center_x - face_center_x) > 100:
            return "托腮", 0.7
        
        return "无", 0
    
    def get_gesture_status_text(self, gesture_type, confidence):
        """获取手势状态文本
        
        Args:
            gesture_type: 手势类型
            confidence: 置信度
            
        Returns:
            str: 状态文本
        """
        if gesture_type == "无" or confidence < 0.5:
            return "无小动作"
        
        status_map = {
            "摸脸": "⚠️ 请避免摸脸",
            "摸下巴": "⚠️ 请避免摸下巴",
            "摸头发": "⚠️ 请避免摸头发",
            "托腮": "⚠️ 请避免托腮"
        }
        
        return status_map.get(gesture_type, "检测到小动作")
    
    def close(self):
        """释放资源"""
        self.hands.close()
        self.face_detector.close()