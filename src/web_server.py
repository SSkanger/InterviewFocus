# src/web_server.py - Web服务器，连接前端和后端
from flask import Flask, render_template, Response, jsonify, request
import cv2
import json
import threading
import time
import base64
import numpy as np
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入面试助手
from main import InterviewCoachV2

app = Flask(__name__)

# 全局变量
coach = None
camera_thread = None
is_running = False
latest_frame = None
latest_data = {
    'attention_score': 80.0,
    'gaze_status': '正常',
    'pose_status': '良好',
    'gesture_status': '无小动作',
    'face_detected': False,
    'gaze_away_count': 0,
    'pose_issue_count': 0,
    'gesture_count': 0,
    'session_time': 0,
    'feedback': '系统运行中...'
}

def initialize_coach():
    """初始化面试助手"""
    global coach
    try:
        coach = InterviewCoachV2()
        print("✅ 面试助手初始化成功")
        return True
    except Exception as e:
        print(f"❌ 面试助手初始化失败: {e}")
        return False

def camera_loop():
    """摄像头循环，在后台线程中运行"""
    global is_running, latest_frame, latest_data, coach
    
    if not coach:
        print("❌ 面试助手未初始化")
        return
    
    # 打开摄像头
    if not coach.camera.open():
        print("❌ 无法打开摄像头")
        return
    
    start_time = None
    
    while is_running:
        # 读取摄像头帧
        ret, frame = coach.camera.read_frame()
        if not ret:
            print("❌ 无法读取摄像头画面")
            break
        
        # 更新检测
        if coach.is_running:
            coach._update_detection(frame)
            coach._update_feedback()
            
            # 更新数据
            latest_data = {
                'attention_score': coach.attention_score,
                'gaze_status': coach.gaze_status,
                'pose_status': coach.pose_status,
                'gesture_status': coach.gesture_status,
                'face_detected': coach.face_detected,
                'gaze_away_count': coach.gaze_away_count,
                'pose_issue_count': coach.pose_issue_count,
                'gesture_count': coach.gesture_count,
                'session_time': (datetime.now() - start_time).total_seconds() if start_time else 0,
                'feedback': coach.voice.get_latest_feedback() or "系统运行中..."
            }
        
        # 绘制UI
        frame = coach.draw_ui(frame)
        
        # 更新最新帧
        latest_frame = frame.copy()
        
        # 控制帧率
        time.sleep(0.033)  # 约30fps
    
    # 清理资源
    coach.camera.close()
    print("👋 摄像头线程已退出")

@app.route('/')
def index():
    """返回前端页面"""
    response = render_template('index.html')
    return response

@app.route('/api/start', methods=['POST'])
def start_interview():
    """开始面试"""
    global is_running, camera_thread, coach
    
    if not coach:
        if not initialize_coach():
            response = jsonify({'success': False, 'message': '面试助手初始化失败'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    
    # 如果已经在运行，先停止
    if is_running:
        stop_interview()
    
    # 开始面试
    coach.is_running = True
    coach.start_time = datetime.now()
    coach._reset_statistics()
    coach.voice.start_session()
    
    # 启动摄像头线程
    is_running = True
    camera_thread = threading.Thread(target=camera_loop)
    camera_thread.daemon = True
    camera_thread.start()
    
    print("⏺️ 面试已开始")
    response = jsonify({'success': True, 'message': '面试已开始'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/stop', methods=['POST'])
def stop_interview():
    """停止面试"""
    global is_running, coach
    
    if coach:
        coach.is_running = False
        coach.voice.end_session()
    
    is_running = False
    
    print("⏹️ 面试已停止")
    response = jsonify({'success': True, 'message': '面试已停止'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    response = jsonify({
        'is_running': is_running,
        'data': latest_data
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/video_feed')
def video_feed():
    """视频流"""
    def generate():
        global latest_frame
        
        while True:
            if latest_frame is None:
                # 如果没有帧，返回黑色画面
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
            else:
                frame = latest_frame.copy()
            
            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            # 转换为字节
            frame_bytes = buffer.tobytes()
            
            # 生成multipart响应
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # 控制帧率
            time.sleep(0.033)  # 约30fps
    
    response = Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/snapshot')
def snapshot():
    """获取当前帧的base64编码"""
    global latest_frame
    
    if latest_frame is None:
        # 如果没有帧，返回黑色画面
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
    else:
        frame = latest_frame.copy()
    
    # 编码为JPEG
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        response = jsonify({'success': False, 'message': '无法编码图像'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    # 转换为base64
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
    
    response = jsonify({
        'success': True,
        'image': f'data:image/jpeg;base64,{frame_base64}'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    print("=" * 60)
    print("智能面试模拟系统 - Web服务器")
    print("=" * 60)
    
    # 初始化面试助手
    if initialize_coach():
        print("✅ 服务器准备就绪")
        print("访问 http://localhost:5000 查看前端界面")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        print("❌ 服务器启动失败")