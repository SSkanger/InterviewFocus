import cv2
import numpy as np
import time
from datetime import datetime
import os


class CameraManager:
    """摄像头管理器 - 处理摄像头操作和图像处理"""
    
    def __init__(self, camera_id=0, resolution=(640, 480), fps=30):
        """初始化摄像头管理器
        
        Args:
            camera_id: 摄像头ID（默认0）
            resolution: 分辨率（默认640x480）
            fps: 帧率（默认30）
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.fps = fps
        self.cap = None
        self.is_opened = False
        self.frame_count = 0
        self.start_time = None
        self.last_frame_time = 0
        
        # 性能统计
        self.fps_actual = 0
        self.frame_times = []
        self.max_frame_times = 30
        
        # 图像处理参数
        self.flip_horizontal = True  # 水平翻转（镜像效果）
        self.brightness = 0          # 亮度调整
        self.contrast = 1.0          # 对比度调整
        
        print(f"✅ 摄像头管理器已初始化 (ID: {camera_id}, 分辨率: {resolution}, FPS: {fps})")
    
    def open(self):
        """打开摄像头
        
        Returns:
            bool: 是否成功打开摄像头
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ 无法打开摄像头 {self.camera_id}")
                return False
            
            # 设置分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # 设置帧率
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_opened = True
            self.start_time = time.time()
            
            # 获取实际参数
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ 摄像头已打开 (实际分辨率: {actual_width}x{actual_height}, 实际FPS: {actual_fps})")
            return True
            
        except Exception as e:
            print(f"❌ 打开摄像头时出错: {e}")
            return False
    
    def close(self):
        """关闭摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print("✅ 摄像头已关闭")
    
    def read_frame(self):
        """读取一帧图像
        
        Returns:
            tuple: (是否成功读取, 图像帧)
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret:
                print("❌ 无法读取摄像头帧")
                return False, None
            
            # 更新帧计数
            self.frame_count += 1
            current_time = time.time()
            
            # 计算实际FPS
            if self.frame_count > 1:
                self.frame_times.append(current_time)
                if len(self.frame_times) > self.max_frame_times:
                    self.frame_times.pop(0)
                
                if len(self.frame_times) >= 2:
                    time_diff = self.frame_times[-1] - self.frame_times[0]
                    self.fps_actual = (len(self.frame_times) - 1) / time_diff
            
            self.last_frame_time = current_time
            
            # 应用图像处理
            frame = self._process_frame(frame)
            
            return True, frame
            
        except Exception as e:
            print(f"❌ 读取帧时出错: {e}")
            return False, None
    
    def _process_frame(self, frame):
        """处理图像帧
        
        Args:
            frame: 原始图像帧
            
        Returns:
            numpy.ndarray: 处理后的图像帧
        """
        # 水平翻转（镜像效果）
        if self.flip_horizontal:
            frame = cv2.flip(frame, 1)
        
        # 亮度和对比度调整
        if self.brightness != 0 or self.contrast != 1.0:
            frame = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness)
        
        return frame
    
    def get_camera_info(self):
        """获取摄像头信息
        
        Returns:
            dict: 摄像头信息
        """
        info = {
            'camera_id': self.camera_id,
            'resolution': self.resolution,
            'fps': self.fps,
            'is_opened': self.is_opened,
            'frame_count': self.frame_count,
            'fps_actual': round(self.fps_actual, 1)
        }
        
        if self.is_opened and self.start_time:
            elapsed_time = time.time() - self.start_time
            info['elapsed_time'] = round(elapsed_time, 1)
            info['average_fps'] = round(self.frame_count / elapsed_time, 1) if elapsed_time > 0 else 0
        
        return info
    
    def set_flip_horizontal(self, flip):
        """设置水平翻转
        
        Args:
            flip: 是否水平翻转
        """
        self.flip_horizontal = flip
        print(f"水平翻转已设置为: {flip}")
    
    def set_brightness(self, brightness):
        """设置亮度
        
        Args:
            brightness: 亮度值（-100到100）
        """
        self.brightness = max(-100, min(100, brightness))
        print(f"亮度已设置为: {self.brightness}")
    
    def set_contrast(self, contrast):
        """设置对比度
        
        Args:
            contrast: 对比度值（0.1到3.0）
        """
        self.contrast = max(0.1, min(3.0, contrast))
        print(f"对比度已设置为: {self.contrast}")
    
    def save_frame(self, frame, filename=None, directory="captures"):
        """保存当前帧
        
        Args:
            frame: 要保存的图像帧
            filename: 文件名（如果为None，则自动生成）
            directory: 保存目录
            
        Returns:
            str: 保存的文件路径，如果失败则返回None
        """
        try:
            # 创建目录（如果不存在）
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # 生成文件名
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
            
            filepath = os.path.join(directory, filename)
            
            # 保存图像
            cv2.imwrite(filepath, frame)
            print(f"✅ 帧已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 保存帧时出错: {e}")
            return None
    
    def test_camera(self, duration=5):
        """测试摄像头
        
        Args:
            duration: 测试持续时间（秒）
            
        Returns:
            bool: 测试是否成功
        """
        print(f"开始测试摄像头（持续{duration}秒）...")
        
        if not self.open():
            return False
        
        start_time = time.time()
        test_frames = 0
        
        while time.time() - start_time < duration:
            ret, frame = self.read_frame()
            if ret:
                test_frames += 1
                
                # 显示测试画面
                cv2.imshow('Camera Test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cv2.destroyAllWindows()
        self.close()
        
        actual_duration = time.time() - start_time
        actual_fps = test_frames / actual_duration if actual_duration > 0 else 0
        
        print(f"摄像头测试完成: {test_frames}帧, 实际FPS: {actual_fps:.1f}")
        return test_frames > 0
    
    def list_available_cameras(self, max_cameras=5):
        """列出可用的摄像头
        
        Args:
            max_cameras: 最大测试摄像头数量
            
        Returns:
            list: 可用摄像头的ID列表
        """
        available_cameras = []
        
        print("正在检测可用摄像头...")
        
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                    print(f"✅ 摄像头 {i} 可用")
                cap.release()
            else:
                print(f"❌ 摄像头 {i} 不可用")
        
        print(f"共找到 {len(available_cameras)} 个可用摄像头")
        return available_cameras