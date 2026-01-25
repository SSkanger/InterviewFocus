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

# 导入面试助手和问题管理器
from main import InterviewCoachV2
from question_manager import QuestionManager

app = Flask(__name__)

# 配置CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 全局变量
coach = None
camera_thread = None
is_running = False
latest_frame = None
raw_frame = None  # 原始摄像头帧，不包含UI
interview_position = "Python开发工程师"  # 面试岗位
question_manager = None  # 面试问题管理器

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
    'feedback': '系统运行中...',
    'interview_position': interview_position
}

def initialize_coach():
    """初始化面试助手"""
    global coach, question_manager
    try:
        # 在Web环境下初始化时不使用UI
        coach = InterviewCoachV2(use_ui=False)
        print("✅ 面试助手初始化成功")
        
        # 初始化问题管理器
        question_manager = QuestionManager()
        print("✅ 问题管理器初始化成功")
        
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
    global is_running, camera_thread, coach, latest_data, interview_position
    
    print("收到开始面试请求")
    
    try:
        # 获取请求数据
        request_data = request.get_json() or {}
        position = request_data.get('position', "")
        
        # 验证面试岗位是否为空
        if not position.strip():
            print("面试岗位为空，返回错误")
            response = jsonify({'success': False, 'message': '请先输入面试岗位'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        print(f"面试岗位: {position}")
        interview_position = position
        
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
        
        # 获取并播放第一个问题 - 使用主线程，确保问题能正确播放
        if question_manager:
            print(f"主线程: 准备获取{position}的问题")
            # 确保获取该职业的问题
            questions = question_manager.get_questions_for_position(position)
            print(f"主线程: 成功获取{position}的问题，共{len(questions)}个")
            
            # 获取第一个问题
            print(f"主线程: 准备获取第一个问题")
            first_question = question_manager.get_next_question()
            print(f"主线程: 获取到第一个问题 = {first_question}")
            
            # 保存第一个问题，用于后续播放
            first_question_content = first_question['question'] if first_question else "请介绍一下你自己"
            print(f"主线程: 准备播放欢迎语音")
        else:
            print(f"主线程: 问题管理器未初始化，使用默认问题")
            first_question_content = "请介绍一下你自己"
        
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
            'feedback': '系统运行中...',
            'interview_position': interview_position
        })
        
        # 启动摄像头线程
        print("启动摄像头线程...")
        is_running = True
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.daemon = True
        camera_thread.start()
        
        # 直接在主线程中播放语音，确保能看到完整日志
        try:
            print("主线程: 准备播放语音序列")
            import pyttsx3
            
            # 1. 先播放欢迎语
            print("主线程: 播放欢迎语")
            engine1 = pyttsx3.init()
            engine1.setProperty('rate', 160)
            engine1.setProperty('volume', 0.8)
            engine1.say(f"{position}面试练习开始，请保持专业姿态")
            engine1.runAndWait()
            print("主线程: 欢迎语播放完成")
            
            # 2. 直接播放面试问题
            print("主线程: 播放面试问题")
            engine2 = pyttsx3.init()
            engine2.setProperty('rate', 160)
            engine2.setProperty('volume', 0.8)
            engine2.say(f"{position}面试问题：{first_question_content}，你有5分钟的时间作答")
            engine2.runAndWait()
            print("主线程: 面试问题播放完成")
            
        except Exception as e:
            print(f"主线程语音播放失败: {e}")
            import traceback
            traceback.print_exc()
        
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

# 面试问题相关API
@app.route('/api/questions/position', methods=['POST'])
def get_questions_for_position():
    """获取指定职业的面试问题"""
    global question_manager
    
    try:
        # 获取请求数据
        request_data = request.get_json() or {}
        position = request_data.get('position', "")
        
        # 验证职业是否为空
        if not position.strip():
            return jsonify({'success': False, 'message': '职业不能为空'}), 400
        
        # 检查问题管理器是否已初始化
        if not question_manager:
            question_manager = QuestionManager()
        
        # 获取该职业的问题
        questions = question_manager.get_questions_for_position(position)
        
        response = jsonify({
            'success': True,
            'message': f'成功获取{position}的面试问题',
            'data': {
                'position': position,
                'total_questions': len(questions),
                'questions': questions
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"获取职业问题失败: {e}")
        response = jsonify({'success': False, 'message': f'获取职业问题失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/questions/next')
def get_next_question():
    """获取下一个面试问题"""
    global question_manager, coach
    
    try:
        # 检查问题管理器是否已初始化
        if not question_manager:
            return jsonify({'success': False, 'message': '问题管理器未初始化'}), 400
        
        # 获取下一个问题
        question = question_manager.get_next_question()
        
        if question:
            # 使用语音提问
            if coach and coach.voice:
                coach.voice.ask_question(question['question'], interview_position)
            
            response = jsonify({
                'success': True,
                'message': '成功获取下一个面试问题',
                'data': question
            })
        else:
            response = jsonify({
                'success': True,
                'message': '没有更多面试问题',
                'data': None
            })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"获取下一个问题失败: {e}")
        response = jsonify({'success': False, 'message': f'获取下一个问题失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/questions/ask', methods=['POST'])
def ask_question():
    """通过语音向用户提问"""
    global coach
    
    try:
        # 获取请求数据
        request_data = request.get_json() or {}
        question = request_data.get('question', "")
        position = request_data.get('position', interview_position)
        
        # 验证问题是否为空
        if not question.strip():
            return jsonify({'success': False, 'message': '问题不能为空'}), 400
        
        # 使用语音提问
        if coach and coach.voice:
            coach.voice.ask_question(question, position)
            response = jsonify({
                'success': True,
                'message': '成功通过语音提问',
                'data': {
                    'question': question,
                    'position': position
                }
            })
        else:
            response = jsonify({'success': False, 'message': '语音系统未初始化'}), 500
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"语音提问失败: {e}")
        response = jsonify({'success': False, 'message': f'语音提问失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/questions/current')
def get_current_question():
    """获取当前面试问题"""
    global question_manager
    
    try:
        # 检查问题管理器是否已初始化
        if not question_manager:
            return jsonify({'success': False, 'message': '问题管理器未初始化'}), 400
        
        # 获取当前问题
        question = question_manager.get_current_question()
        
        if question:
            response = jsonify({
                'success': True,
                'message': '成功获取当前面试问题',
                'data': question
            })
        else:
            response = jsonify({
                'success': True,
                'message': '当前没有正在进行的面试问题',
                'data': None
            })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"获取当前问题失败: {e}")
        response = jsonify({'success': False, 'message': f'获取当前问题失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/questions/reset')
def reset_questions():
    """重置问题索引"""
    global question_manager
    
    try:
        # 检查问题管理器是否已初始化
        if not question_manager:
            return jsonify({'success': False, 'message': '问题管理器未初始化'}), 400
        
        # 重置问题索引
        question_manager.reset_questions()
        
        response = jsonify({
            'success': True,
            'message': '问题索引已重置'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"重置问题索引失败: {e}")
        response = jsonify({'success': False, 'message': f'重置问题索引失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/questions/status')
def get_question_status():
    """获取问题状态"""
    global question_manager
    
    try:
        # 检查问题管理器是否已初始化
        if not question_manager:
            return jsonify({'success': False, 'message': '问题管理器未初始化'}), 400
        
        # 获取问题状态
        status = {
            'total_questions': question_manager.get_question_count(),
            'remaining_questions': question_manager.get_remaining_question_count(),
            'has_more_questions': question_manager.has_more_questions()
        }
        
        response = jsonify({
            'success': True,
            'message': '成功获取问题状态',
            'data': status
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"获取问题状态失败: {e}")
        response = jsonify({'success': False, 'message': f'获取问题状态失败: {str(e)}'})
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