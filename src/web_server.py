# src/web_server.py - Web服务器，连接前端和后端
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
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

# 配置CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 全局变量
coach = None
camera_thread = None
is_running = False
latest_frame = None
raw_frame = None  # 原始摄像头帧，不包含UI
latest_data = {
    'attention_score': 100.0,
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
        # 在Web环境下初始化时不使用UI
        coach = InterviewCoachV2(use_ui=False)
        print("✅ 面试助手初始化成功")
        return True
    except Exception as e:
        print(f"❌ 面试助手初始化失败: {e}")
        return False

def camera_loop():
    """摄像头循环线程"""
    global latest_data, is_running, coach, raw_frame, latest_frame
    
    print("摄像头线程已启动")
    
    # 检查摄像头是否可用
    camera_available = False
    try:
        print("正在尝试打开摄像头...")
        camera_available = coach.camera.open()
        print(f"摄像头打开结果: {camera_available}")
    except Exception as e:
        print(f"摄像头打开异常: {e}")
        camera_available = False
    
    if not camera_available:
        print("摄像头不可用，将使用模拟数据")
    
    frame_count = 0  # 帧计数器，用于控制检测频率
    
    try:
        while is_running:
            try:
                frame = None
                if camera_available:
                    try:
                        ret, frame_data = coach.camera.read_frame()
                        if ret and frame_data is not None:
                            frame = frame_data
                            # 更新全局变量raw_frame，用于视频流
                            raw_frame = frame.copy()
                        else:
                            print("读取到空帧，尝试重新打开摄像头")
                            camera_available = coach.camera.open()
                            if camera_available:
                                ret, frame_data = coach.camera.read_frame()
                                if ret and frame_data is not None:
                                    frame = frame_data
                                    # 更新全局变量raw_frame，用于视频流
                                    raw_frame = frame.copy()
                                else:
                                    frame = None
                            else:
                                print("摄像头重新打开失败，继续使用模拟数据")
                                frame = None
                    except Exception as e:
                        print(f"读取摄像头帧失败: {e}")
                        # 尝试重新打开摄像头
                        try:
                            camera_available = coach.camera.open()
                            if camera_available:
                                ret, frame_data = coach.camera.read_frame()
                                if ret and frame_data is not None:
                                    frame = frame_data
                                    # 更新全局变量raw_frame，用于视频流
                                    raw_frame = frame.copy()
                                else:
                                    frame = None
                        except Exception as e2:
                            print(f"重新打开摄像头失败: {e2}")
                            frame = None
                
                # 处理帧或使用模拟数据
                if frame is not None and len(frame.shape) > 0:
                    # 每5帧进行一次检测，提高视频帧率
                    if frame_count % 5 == 0:
                        # 使用真实帧进行检测
                        results = coach.process_frame(frame)
                        # 更新全局数据
                        latest_data.update({
                            'attention_score': coach.attention_score,
                            'gaze_status': coach.gaze_status,
                            'pose_status': coach.pose_status,
                            'gesture_status': coach.gesture_status,
                            'face_detected': coach.face_detected,
                            'gaze_away_count': coach.gaze_away_count,
                            'pose_issue_count': coach.pose_issue_count,
                            'gesture_count': coach.gesture_count,
                            'session_time': coach.get_session_time(),
                            'feedback': coach.voice.get_latest_feedback() or "系统运行中..."
                        })
                        # 更新latest_frame，用于快照
                        latest_frame = frame.copy()
                else:
                    # 使用模拟数据
                    print("使用模拟数据更新状态")
                    latest_data.update({
                        'attention_score': coach.attention_score,
                        'gaze_status': coach.gaze_status,
                        'pose_status': coach.pose_status,
                        'gesture_status': coach.gesture_status,
                        'face_detected': False,
                        'gaze_away_count': coach.gaze_away_count,
                        'pose_issue_count': coach.pose_issue_count,
                        'gesture_count': coach.gesture_count,
                        'session_time': coach.get_session_time(),
                        'feedback': coach.voice.get_latest_feedback() or "系统运行中..."
                    })
                    # 如果没有真实帧，创建一个黑色帧用于视频流
                    if raw_frame is None:
                        raw_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # 增加帧计数
                frame_count += 1
                
                # 添加小延迟，控制CPU占用
                time.sleep(0.01)  # 约100 FPS的上限
            except Exception as e:
                print(f"处理帧时发生错误: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)  # 出错时稍作等待
    finally:
        # 清理资源
        print("摄像头线程结束，清理资源")
        try:
            if camera_available:
                coach.camera.close()
        except Exception as e:
            print(f"关闭摄像头时发生错误: {e}")

@app.route('/')
def index():
    """返回前端页面"""
    response = render_template('index.html')
    return response

@app.route('/api/start', methods=['POST'])
def start_interview():
    """开始面试"""
    global is_running, camera_thread, coach, latest_data
    
    print("收到开始面试请求")
    
    try:
        if not coach:
            print("面试助手未初始化，正在初始化...")
            if not initialize_coach():
                print("面试助手初始化失败")
                response = jsonify({'success': False, 'message': '面试助手初始化失败'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            else:
                print("面试助手初始化成功")
        
        # 如果已经在运行，先停止
        if is_running:
            print("面试已在运行，先停止当前面试")
            stop_interview()
            # 等待线程结束
            if camera_thread and camera_thread.is_alive():
                camera_thread.join(timeout=2)
        
        # 开始面试
        print("开始面试流程...")
        coach.is_running = True
        coach.start_time = datetime.now()
        coach._reset_statistics()
        
        print("正在启动语音会话...")
        try:
            # 在单独的线程中播放语音，避免阻塞
            def play_welcome():
                try:
                    coach.voice.start_session()
                    print("语音会话已启动")
                except Exception as e:
                    print(f"语音会话启动失败: {e}")
            
            voice_thread = threading.Thread(target=play_welcome)
            voice_thread.daemon = True
            voice_thread.start()
        except Exception as e:
            print(f"语音会话启动失败: {e}")
            # 继续执行，不中断面试
        
        # 立即更新状态数据，确保初始分数正确
        latest_data.update({
            'attention_score': coach.attention_score,
            'gaze_status': coach.gaze_status,
            'pose_status': coach.pose_status,
            'gesture_status': coach.gesture_status,
            'face_detected': coach.face_detected,
            'gaze_away_count': coach.gaze_away_count,
            'pose_issue_count': coach.pose_issue_count,
            'gesture_count': coach.gesture_count,
            'session_time': 0,
            'feedback': coach.voice.get_latest_feedback() or "系统运行中..."
        })
        
        # 启动摄像头线程
        print("启动摄像头线程...")
        is_running = True
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.daemon = True
        camera_thread.start()
        
        print("⏺️ 面试已开始")
        response = jsonify({'success': True, 'message': '面试已开始'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"开始面试时发生错误: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'开始面试失败: {str(e)}'})
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
    global is_running, latest_data
    
    # 添加调试日志
    print(f"获取状态请求: is_running={is_running}, latest_data={latest_data}")
    
    # 记录请求来源
    print(f"请求来源: {request.remote_addr}")
    print(f"请求头: {dict(request.headers)}")
    
    response = jsonify({
        'is_running': is_running,
        'data': latest_data
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(f"响应数据: {response.get_json()}")
    return response

@app.route('/api/video_feed')
def video_feed():
    """视频流"""
    def generate():
        global raw_frame
        
        while True:
            if raw_frame is None:
                # 如果没有帧，返回黑色画面
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
            else:
                frame = raw_frame.copy()
            
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
    
    try:
        # 初始化面试助手
        if initialize_coach():
            print("✅ 服务器准备就绪")
            print("访问 http://localhost:5000 查看前端界面")
            print("正在启动Flask服务器...")
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        else:
            print("❌ 服务器启动失败")
    except Exception as e:
        print(f"❌ 服务器启动时发生异常: {e}")
        import traceback
        traceback.print_exc()
        print("按任意键退出...")
        input()