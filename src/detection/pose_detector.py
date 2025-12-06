import cv2
import numpy as np
import math
from .face_detector import FaceDetector


class PoseDetector:
    """姿态检测器 - 检测头部姿态"""
    
    def __init__(self):
        """初始化姿态检测器"""
        self.face_detector = FaceDetector()
        
        # 定义用于姿态估计的关键点索引
        self.CHIN = 152  # 下巴
        self.LEFT_EYE_CORNER = 33  # 左眼角
        self.RIGHT_EYE_CORNER = 362  # 右眼角
        self.NOSE_TIP = 1  # 鼻尖
        self.FOREHEAD = 10  # 额头
        
        # 状态跟踪
        self.pose_history = []  # 用于平滑姿态状态
        self.history_size = 5   # 历史记录大小
        
        print("✅ 姿态检测器已初始化")
    
    def detect_pose(self, frame):
        """检测头部姿态
        
        Args:
            frame: 输入图像帧
            
        Returns:
            tuple: (姿态状态, 偏转角度, 带标注的图像)
        """
        # 使用面部检测器获取关键点
        has_face, landmarks, annotated_frame = self.face_detector.detect(frame)
        
        if not has_face:
            return "未检测到人脸", 0, annotated_frame
        
        # 获取关键点
        try:
            chin = landmarks[self.CHIN]
            left_eye_corner = landmarks[self.LEFT_EYE_CORNER]
            right_eye_corner = landmarks[self.RIGHT_EYE_CORNER]
            nose_tip = landmarks[self.NOSE_TIP]
            forehead = landmarks[self.FOREHEAD]
        except IndexError:
            return "关键点缺失", 0, annotated_frame
        
        # 计算头部偏转角度
        # 1. 计算水平偏转（左右转头）
        eye_center_x = (left_eye_corner[0] + right_eye_corner[0]) // 2
        nose_offset_x = nose_tip[0] - eye_center_x
        
        # 2. 计算垂直偏转（抬头/低头）
        eye_center_y = (left_eye_corner[1] + right_eye_corner[1]) // 2
        nose_offset_y = nose_tip[1] - eye_center_y
        
        # 3. 计算头部倾斜（歪头）
        eye_line_angle = math.degrees(math.atan2(
            right_eye_corner[1] - left_eye_corner[1],
            right_eye_corner[0] - left_eye_corner[0]
        ))
        
        # 判断姿态状态
        pose_status = self._evaluate_pose(nose_offset_x, nose_offset_y, eye_line_angle)
        
        # 添加到历史记录
        self.pose_history.append(pose_status)
        if len(self.pose_history) > self.history_size:
            self.pose_history.pop(0)
        
        # 平滑结果（取历史记录中最常见的状态）
        smoothed_pose_status = max(set(self.pose_history), key=self.pose_history.count)
        
        # 在画面上绘制关键点和姿态指示
        # 绘制关键点
        cv2.circle(annotated_frame, chin, 3, (0, 255, 255), -1)
        cv2.circle(annotated_frame, left_eye_corner, 3, (255, 0, 0), -1)
        cv2.circle(annotated_frame, right_eye_corner, 3, (255, 0, 0), -1)
        cv2.circle(annotated_frame, nose_tip, 3, (0, 0, 255), -1)
        cv2.circle(annotated_frame, forehead, 3, (0, 255, 0), -1)
        
        # 绘制连接线
        cv2.line(annotated_frame, left_eye_corner, right_eye_corner, (255, 0, 0), 1)
        cv2.line(annotated_frame, (eye_center_x, eye_center_y), (nose_tip[0], nose_tip[1]), (0, 0, 255), 1)
        
        # 显示角度信息
        cv2.putText(annotated_frame, f"倾斜: {eye_line_angle:.1f}°", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return smoothed_pose_status, eye_line_angle, annotated_frame
    
    def _evaluate_pose(self, nose_offset_x, nose_offset_y, eye_line_angle):
        """评估姿态状态
        
        Args:
            nose_offset_x: 鼻子水平偏移
            nose_offset_y: 鼻子垂直偏移
            eye_line_angle: 眼线角度
            
        Returns:
            str: 姿态状态
        """
        # 判断抬头/低头
        if nose_offset_y < -15:  # 鼻子在眼睛上方（抬头）
            if abs(eye_line_angle) > 10:
                return "歪头"
            else:
                return "抬头"
        elif nose_offset_y > 15:  # 鼻子在眼睛下方（低头）
            if abs(eye_line_angle) > 10:
                return "歪头"
            else:
                return "低头"
        
        # 判断歪头
        if abs(eye_line_angle) > 15:
            return "歪头"
        
        # 判断左右转头
        if abs(nose_offset_x) > 20:
            return "转头"
        
        return "正常"
    
    def get_pose_status_text(self, pose_status):
        """获取姿态状态文本
        
        Args:
            pose_status: 姿态状态
            
        Returns:
            str: 状态文本
        """
        status_map = {
            "正常": "良好",
            "抬头": "⚠️ 请勿频繁抬头",
            "低头": "⚠️ 请保持抬头挺胸",
            "歪头": "⚠️ 请保持头部正直",
            "转头": "⚠️ 请保持面向摄像头",
            "未检测到人脸": "未检测到人脸"
        }
        
        return status_map.get(pose_status, "未知状态")
    
    def close(self):
        """释放资源"""
        self.face_detector.close()