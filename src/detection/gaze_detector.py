import cv2
import numpy as np
from .face_detector import FaceDetector


class GazeDetector:
    """视线检测器 - 检测用户是否看向摄像头"""
    
    def __init__(self, offset_threshold=0.15):
        """初始化视线检测器
        
        Args:
            offset_threshold: 视线偏移阈值（相对于画面中心的比例）
        """
        self.face_detector = FaceDetector()
        self.offset_threshold = offset_threshold
        
        # 状态跟踪
        self.gaze_history = []  # 用于平滑视线状态
        self.history_size = 5   # 历史记录大小
        
        print("✅ 视线检测器已初始化")
    
    def detect_gaze(self, frame, draw_annotations=True):
        """检测视线方向
        
        Args:
            frame: 输入图像帧
            draw_annotations: 是否绘制标注（默认True）
            
        Returns:
            tuple: (是否看向摄像头, 偏移比例, 带标注的图像)
        """
        # 使用面部检测器获取关键点
        has_face, landmarks, annotated_frame = self.face_detector.detect(frame, draw_annotations)
        
        if not has_face:
            return False, 1.0, annotated_frame
        
        # 获取眼部关键点
        left_eye, right_eye = self.face_detector.get_eye_landmarks(landmarks)
        
        if not left_eye or not right_eye:
            return False, 1.0, annotated_frame
        
        # 计算双眼中心
        left_center = self.face_detector.calculate_eye_center(left_eye)
        right_center = self.face_detector.calculate_eye_center(right_eye)
        
        # 计算双眼整体中心
        eye_center_x = (left_center[0] + right_center[0]) // 2
        eye_center_y = (left_center[1] + right_center[1]) // 2
        
        # 获取画面中心
        h, w = frame.shape[:2]
        frame_center_x = w // 2
        
        # 计算偏移比例
        offset_ratio = abs(eye_center_x - frame_center_x) / (w // 2)
        
        # 判断是否看向摄像头
        is_looking = offset_ratio < self.offset_threshold
        
        # 添加到历史记录
        self.gaze_history.append(is_looking)
        if len(self.gaze_history) > self.history_size:
            self.gaze_history.pop(0)
        
        # 平滑结果（如果历史记录中多数时间看向摄像头，则认为当前看向摄像头）
        smoothed_is_looking = sum(self.gaze_history) / len(self.gaze_history) > 0.6
        
        # 在画面上绘制眼部中心和视线指示
        cv2.circle(annotated_frame, (eye_center_x, eye_center_y), 5, (0, 255, 0), -1)
        cv2.line(annotated_frame, (eye_center_x, eye_center_y), 
                (frame_center_x, eye_center_y), 
                (0, 255, 0) if smoothed_is_looking else (0, 0, 255), 2)
        
        # 绘制画面中心线
        cv2.line(annotated_frame, (frame_center_x, 0), 
                (frame_center_x, h), (255, 255, 255), 1)
        
        return smoothed_is_looking, offset_ratio, annotated_frame
    
    def get_gaze_status_text(self, is_looking, offset_ratio):
        """获取视线状态文本
        
        Args:
            is_looking: 是否看向摄像头
            offset_ratio: 偏移比例
            
        Returns:
            str: 状态文本
        """
        if is_looking:
            return "正常"
        elif offset_ratio < 0.3:
            return "轻微偏移"
        elif offset_ratio < 0.5:
            return "明显偏移"
        else:
            return "严重偏移"
    
    def close(self):
        """释放资源"""
        self.face_detector.close()