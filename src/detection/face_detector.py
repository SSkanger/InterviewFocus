import cv2
import mediapipe as mp
import numpy as np


class FaceDetector:
    """面部检测器 - 使用MediaPipe实现人脸检测和关键点提取"""
    
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """初始化面部检测器
        
        Args:
            min_detection_confidence: 人脸检测的最小置信度阈值
            min_tracking_confidence: 关键点跟踪的最小置信度阈值
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # 初始化人脸网格检测器
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # 定义关键特征点索引
        self.LEFT_EYE_INDICES = [33, 133, 159, 145, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 263, 386, 374, 380, 373]
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 340, 346, 347, 348, 349, 350, 451, 452, 453, 464, 435, 410, 287, 273, 335, 321, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
        
        print("✅ 面部检测器已初始化")
    
    def detect(self, frame, draw_annotations=True):
        """检测人脸并返回关键点
        
        Args:
            frame: 输入图像帧
            draw_annotations: 是否绘制标注（默认True）
            
        Returns:
            tuple: (是否有脸, 关键点列表, 带标注的图像)
        """
        # 转换为RGB格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像
        results = self.face_mesh.process(rgb_frame)
        
        # 创建副本用于绘制
        annotated_frame = frame.copy()
        
        # 初始化关键点列表
        landmarks = []
        
        # 检查是否检测到人脸
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 提取所有关键点坐标
                h, w = frame.shape[:2]
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks.append((x, y))
                
                # 仅在需要时绘制标注
                if draw_annotations:
                    # 绘制人脸网格
                    self.mp_drawing.draw_landmarks(
                        image=annotated_frame,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
                    
                    # 绘制轮廓
                    self.mp_drawing.draw_landmarks(
                        image=annotated_frame,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                    )
        
        # 返回结果
        has_face = len(landmarks) > 0
        return has_face, landmarks, annotated_frame
    
    def get_eye_landmarks(self, landmarks):
        """获取眼部关键点
        
        Args:
            landmarks: 所有关键点列表
            
        Returns:
            tuple: (左眼关键点, 右眼关键点)
        """
        if not landmarks:
            return [], []
        
        left_eye = [landmarks[i] for i in self.LEFT_EYE_INDICES if i < len(landmarks)]
        right_eye = [landmarks[i] for i in self.RIGHT_EYE_INDICES if i < len(landmarks)]
        
        return left_eye, right_eye
    
    def get_face_oval(self, landmarks):
        """获取面部轮廓关键点
        
        Args:
            landmarks: 所有关键点列表
            
        Returns:
            list: 面部轮廓关键点
        """
        if not landmarks:
            return []
        
        return [landmarks[i] for i in self.FACE_OVAL if i < len(landmarks)]
    
    def calculate_eye_center(self, eye_landmarks):
        """计算眼部中心点
        
        Args:
            eye_landmarks: 眼部关键点列表
            
        Returns:
            tuple: 眼部中心坐标 (x, y)
        """
        if not eye_landmarks:
            return (0, 0)
        
        x = sum(point[0] for point in eye_landmarks) // len(eye_landmarks)
        y = sum(point[1] for point in eye_landmarks) // len(eye_landmarks)
        
        return (x, y)
    
    def draw_eye_region(self, frame, eye_landmarks, color=(0, 255, 0), thickness=2):
        """在眼部区域绘制轮廓
        
        Args:
            frame: 输入图像
            eye_landmarks: 眼部关键点
            color: 绘制颜色
            thickness: 线条粗细
            
        Returns:
            带眼部轮廓的图像
        """
        if not eye_landmarks:
            return frame
        
        # 转换为numpy数组
        points = np.array(eye_landmarks, dtype=np.int32)
        
        # 绘制凸包
        cv2.polylines(frame, [points], True, color, thickness)
        
        return frame
    
    def close(self):
        """释放资源"""
        self.face_mesh.close()