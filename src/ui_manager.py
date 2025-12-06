# UI管理模块 - 提供用户界面功能

import cv2
import numpy as np
from datetime import datetime


class UIManager:
    """UI管理器 - 负责所有用户界面元素的绘制和更新"""
    
    def __init__(self, window_name="Interview Coach", window_size=(1280, 720)):
        """初始化UI管理器
        
        Args:
            window_name: 窗口名称
            window_size: 窗口大小 (width, height)
        """
        self.window_name = window_name
        self.width = window_size[0]
        self.height = window_size[1]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5  # 减小字体大小
        self.font_thickness = 1  # 减小字体粗细
        self.line_thickness = 1
        
        # 颜色定义
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'cyan': (255, 255, 0),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'dark_gray': (50, 50, 50),
            'orange': (0, 165, 255),
            'purple': (128, 0, 128),
            'transparent_black': (0, 0, 0, 180),  # 半透明黑色
            'transparent_white': (255, 255, 255, 100)  # 半透明白色
        }
        
        # UI元素位置和尺寸 - 调整为适应640x480分辨率
        self.top_bar_height = 40
        self.bottom_bar_height = 60
        self.side_panel_width = 150
        
        # 主内容区域 - 保留大部分画面给摄像头
        self.content_x = 10
        self.content_y = self.top_bar_height + 10
        self.content_width = self.width - 20
        self.content_height = self.height - self.top_bar_height - self.bottom_bar_height - 20
        
        print("✅ UI管理器已初始化")
    
    def create_window(self):
        """创建并配置窗口"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        print(f"✅ 窗口 '{self.window_name}' 已创建")
    
    def draw_top_bar(self, frame, title="Interview Coach"):
        """绘制顶部状态栏 - 半透明覆盖层
        
        Args:
            frame: 视频帧
            title: 标题文本
        """
        # 创建半透明覆盖层
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.top_bar_height), (0, 0, 0), -1)
        
        # 应用半透明效果
        alpha = 0.7
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 添加标题
        title_size = cv2.getTextSize(title, self.font, 0.6, 1)[0]
        title_x = (self.width - title_size[0]) // 2
        title_y = int(self.top_bar_height * 0.7)
        cv2.putText(frame, title, (title_x, title_y), self.font, 0.6, 
                   self.colors['white'], 1)
        
        # 添加时间戳
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_size = cv2.getTextSize(current_time, self.font, 0.4, 1)[0]
        cv2.putText(frame, current_time, (self.width - time_size[0] - 10, title_y), 
                   self.font, 0.4, self.colors['white'], 1)
        
        return frame
    
    def draw_side_panel(self, frame, status_info):
        """绘制右侧信息面板 - 半透明覆盖层
        
        Args:
            frame: 视频帧
            status_info: 状态信息字典
        """
        panel_x = self.width - self.side_panel_width
        panel_y = self.top_bar_height
        
        # 创建半透明覆盖层
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (self.width, self.height - self.bottom_bar_height), 
                     (0, 0, 0), -1)
        
        # 应用半透明效果
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 绘制面板边框
        cv2.rectangle(frame, (panel_x, panel_y), 
                     (self.width, self.height - self.bottom_bar_height), 
                     self.colors['cyan'], 1)
        
        # 添加状态信息
        y_offset = panel_y + 20
        
        # 标题
        cv2.putText(frame, "Status", (panel_x + 5, y_offset), self.font, 
                   0.5, self.colors['cyan'], 1)
        y_offset += 20
        
        # 状态指示器
        status_text = status_info.get('status', 'Unknown')
        status_color = self.colors['green'] if status_text == '正常' else self.colors['red']
        cv2.putText(frame, f"St: {status_text}", (panel_x + 5, y_offset), 
                   self.font, 0.4, status_color, 1)
        y_offset += 18
        
        # 注意力分数
        attention_score = status_info.get('attention_score', 0)
        cv2.putText(frame, f"Attn: {attention_score}%", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['white'], 1)
        y_offset += 18
        
        # 视线方向
        gaze_direction = status_info.get('gaze_direction', 'Unknown')
        cv2.putText(frame, f"Gaze: {gaze_direction}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['white'], 1)
        y_offset += 18
        
        # 姿态
        posture = status_info.get('posture', 'Unknown')
        cv2.putText(frame, f"Pos: {posture}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['white'], 1)
        y_offset += 18
        
        # 手势
        gesture = status_info.get('gesture', 'None')
        cv2.putText(frame, f"Ges: {gesture}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['white'], 1)
        y_offset += 18
        
        # 统计信息
        y_offset += 10
        cv2.putText(frame, "Stats", (panel_x + 5, y_offset), self.font, 
                   0.5, self.colors['cyan'], 1)
        y_offset += 20
        
        # 离开次数
        look_away_count = status_info.get('look_away_count', 0)
        cv2.putText(frame, f"Away: {look_away_count}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['yellow'], 1)
        y_offset += 18
        
        # 不良姿态次数
        bad_posture_count = status_info.get('bad_posture_count', 0)
        cv2.putText(frame, f"BadPos: {bad_posture_count}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['yellow'], 1)
        y_offset += 18
        
        # 手势次数
        gesture_count = status_info.get('gesture_count', 0)
        cv2.putText(frame, f"GestCnt: {gesture_count}", (panel_x + 5, y_offset), 
                   self.font, 0.4, self.colors['yellow'], 1)
        
        return frame
    
    def draw_bottom_bar(self, frame, feedback_text="System running..."):
        """绘制底部信息栏 - 半透明覆盖层
        
        Args:
            frame: 视频帧
            feedback_text: 反馈文本
        """
        bar_y = self.height - self.bottom_bar_height
        
        # 创建半透明覆盖层
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, bar_y), (self.width, self.height), (0, 0, 0), -1)
        
        # 应用半透明效果
        alpha = 0.7
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 绘制边框
        cv2.line(frame, (0, bar_y), (self.width, bar_y), 
                self.colors['cyan'], 1)
        
        # 添加反馈文本
        text_size = cv2.getTextSize(feedback_text, self.font, 0.5, 1)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = bar_y + 25
        cv2.putText(frame, feedback_text, (text_x, text_y), self.font, 
                   0.5, self.colors['white'], 1)
        
        # 添加提示信息
        hint_text = "Press 'q' to exit | 's' to start/stop | 't' to test voice"
        hint_size = cv2.getTextSize(hint_text, self.font, 0.35, 1)[0]
        hint_x = (self.width - hint_size[0]) // 2
        hint_y = bar_y + 45
        cv2.putText(frame, hint_text, (hint_x, hint_y), self.font, 
                   0.35, self.colors['light_gray'], 1)
        
        return frame
    
    def draw_attention_meter(self, frame, attention_score, x=10, y=70):
        """绘制注意力仪表盘 - 半透明背景
        
        Args:
            frame: 视频帧
            attention_score: 注意力分数 (0-100)
            x, y: 仪表盘位置
        """
        # 绘制半透明背景
        overlay = frame.copy()
        cv2.rectangle(overlay, (x-5, y-25), (x+155, y+35), (0, 0, 0), -1)
        
        # 应用半透明效果
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 绘制边框
        cv2.rectangle(frame, (x-5, y-25), (x+155, y+35), self.colors['cyan'], 1)
        
        # 绘制标题
        cv2.putText(frame, "Attention", (x, y-8), self.font, 
                   0.4, self.colors['cyan'], 1)
        
        # 绘制进度条背景
        cv2.rectangle(frame, (x, y), (x+150, y+15), 
                     self.colors['dark_gray'], -1)
        
        # 根据分数确定颜色
        if attention_score >= 80:
            color = self.colors['green']
        elif attention_score >= 60:
            color = self.colors['yellow']
        else:
            color = self.colors['red']
        
        # 绘制进度条
        bar_width = int((attention_score / 100) * 150)
        cv2.rectangle(frame, (x, y), (x+bar_width, y+15), color, -1)
        
        # 绘制边框
        cv2.rectangle(frame, (x, y), (x+150, y+15), 
                     self.colors['white'], 1)
        
        # 显示分数
        score_text = f"{attention_score}%"
        score_size = cv2.getTextSize(score_text, self.font, 0.4, 1)[0]
        score_x = x + (150 - score_size[0]) // 2
        cv2.putText(frame, score_text, (score_x, y+12), self.font, 
                   0.4, self.colors['white'], 1)
        
        return frame
    
    def draw_face_landmarks(self, frame, landmarks, color=(0, 255, 0), radius=2):
        """绘制面部关键点
        
        Args:
            frame: 视频帧
            landmarks: 面部关键点坐标
            color: 颜色
            radius: 点的半径
        """
        if landmarks is None:
            return frame
            
        for point in landmarks:
            if point:
                x, y = int(point[0]), int(point[1])
                cv2.circle(frame, (x, y), radius, color, -1)
                
        return frame
    
    def draw_gaze_direction(self, frame, gaze_direction, eye_center, length=50):
        """绘制视线方向指示器
        
        Args:
            frame: 视频帧
            gaze_direction: 视线方向 (x, y)
            eye_center: 眼部中心点
            length: 指示器长度
        """
        if gaze_direction is None or eye_center is None:
            return frame
            
        # 计算终点坐标
        end_x = int(eye_center[0] + gaze_direction[0] * length)
        end_y = int(eye_center[1] + gaze_direction[1] * length)
        
        # 绘制视线方向
        cv2.arrowedLine(frame, (int(eye_center[0]), int(eye_center[1])), 
                       (end_x, end_y), self.colors['yellow'], 3)
        
        return frame
    
    def draw_pose_skeleton(self, frame, pose_landmarks):
        """绘制姿态骨架
        
        Args:
            frame: 视频帧
            pose_landmarks: 姿态关键点
        """
        if pose_landmarks is None:
            return frame
            
        # 定义连接关系
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 7),  # 头部和颈部
            (0, 4), (4, 5), (5, 6), (6, 8),  # 左臂
            (0, 9), (9, 10), (10, 11), (11, 12),  # 右臂
            (0, 13), (13, 14), (14, 15), (15, 16),  # 左腿
            (0, 17), (17, 18), (18, 19), (19, 20)  # 右腿
        ]
        
        # 绘制连接线
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(pose_landmarks) and end_idx < len(pose_landmarks):
                start_point = pose_landmarks[start_idx]
                end_point = pose_landmarks[end_idx]
                
                if start_point and end_point:
                    start_x, start_y = int(start_point[0]), int(start_point[1])
                    end_x, end_y = int(end_point[0]), int(end_point[1])
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), 
                            self.colors['cyan'], 2)
        
        # 绘制关键点
        for point in pose_landmarks:
            if point:
                x, y = int(point[0]), int(point[1])
                cv2.circle(frame, (x, y), 3, self.colors['magenta'], -1)
                
        return frame
    
    def add_timestamp(self, frame, position=(10, 30)):
        """添加时间戳
        
        Args:
            frame: 视频帧
            position: 时间戳位置 (x, y)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, position, self.font, 
                   0.5, self.colors['white'], 1)
        
        return frame
    
    def add_warning(self, frame, warning_text, position=None):
        """添加警告信息
        
        Args:
            frame: 视频帧
            warning_text: 警告文本
            position: 警告位置 (x, y)，默认为画面中央
        """
        if position is None:
            # 计算文本大小和位置
            text_size = cv2.getTextSize(warning_text, self.font, 0.8, 2)[0]
            position = ((self.width - text_size[0]) // 2, 
                       (self.height - text_size[1]) // 2)
        
        # 绘制半透明背景
        overlay = frame.copy()
        text_bg_x1 = position[0] - 10
        text_bg_y1 = position[1] - 30
        text_bg_x2 = position[0] + text_size[0] + 10
        text_bg_y2 = position[1] + 10
        
        cv2.rectangle(overlay, (text_bg_x1, text_bg_y1), 
                     (text_bg_x2, text_bg_y2), (0, 0, 255), -1)
        
        # 应用半透明效果
        alpha = 0.7
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 绘制警告文本
        cv2.putText(frame, warning_text, position, self.font, 
                   0.8, self.colors['white'], 2)
        
        return frame
    
    def draw_help_overlay(self, frame):
        """绘制帮助覆盖层
        
        Args:
            frame: 视频帧
        """
        # 创建半透明背景
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        
        # 应用半透明效果
        alpha = 0.8
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # 添加帮助标题
        title = "Interview Coach - Help"
        title_size = cv2.getTextSize(title, self.font, 1.0, 2)[0]
        title_x = (self.width - title_size[0]) // 2
        title_y = 100
        cv2.putText(frame, title, (title_x, title_y), self.font, 
                   1.0, self.colors['cyan'], 2)
        
        # 添加帮助内容
        help_items = [
            "Press 'q' - Exit program",
            "Press 's' - Save current frame screenshot",
            "Press 'h' - Show/Hide this help interface",
            "Press 'r' - Reset statistics",
            "Press 'm' - Toggle microphone",
            "Press 'c' - Switch camera"
        ]
        
        y_offset = title_y + 60
        for item in help_items:
            item_size = cv2.getTextSize(item, self.font, 0.7, 1)[0]
            item_x = (self.width - item_size[0]) // 2
            cv2.putText(frame, item, (item_x, y_offset), self.font, 
                       0.7, self.colors['white'], 1)
            y_offset += 40
        
        # 添加提示
        hint = "Press any key to continue..."
        hint_size = cv2.getTextSize(hint, self.font, 0.6, 1)[0]
        hint_x = (self.width - hint_size[0]) // 2
        hint_y = self.height - 100
        cv2.putText(frame, hint, (hint_x, hint_y), self.font, 
                   0.6, self.colors['yellow'], 1)
        
        return frame
    
    def _get_attention_color(self, score):
        """根据注意力分数获取颜色
        
        Args:
            score: 注意力分数 (0-100)
            
        Returns:
            颜色元组 (B, G, R)
        """
        if score >= 80:
            return self.colors['green']
        elif score >= 60:
            return self.colors['yellow']
        else:
            return self.colors['red']
