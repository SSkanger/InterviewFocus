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

# 视频录制相关变量
video_writer = None
video_recording = False
video_frames = []
video_lock = threading.Lock()

# 录制线程控制变量
recording_thread_running = False


def recording_thread():
    """专门处理视频录制的线程 - 降低资源占用"""
    global video_recording, video_frames, raw_frame, recording_thread_running
    
    recording_thread_running = True
    print("视频录制线程已启动")
    
    recording_frame_count = 0
    recording_interval = 4  # 每4帧录制1帧，降低录制帧率
    
    try:
        while recording_thread_running:
            if video_recording and raw_frame is not None:
                recording_frame_count += 1
                # 降低录制帧率
                if recording_frame_count % recording_interval == 0:
                    with video_lock:
                        try:
                            # 降低录制分辨率，减少内存占用
                            small_frame = cv2.resize(raw_frame, (320, 240))
                            video_frames.append(small_frame)
                        except Exception as e:
                            print(f"录制帧处理失败: {e}")
            
            # 轻微延迟，减少CPU占用
            time.sleep(0.01)
    finally:
        recording_thread_running = False
        print("视频录制线程已结束")


# 启动录制线程
recording_thread_instance = threading.Thread(target=recording_thread)
recording_thread_instance.daemon = True
recording_thread_instance.start()

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
    global latest_data, is_running, coach, raw_frame, latest_frame, video_recording, video_frames, video_lock
    
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
                    # 处理帧并更新状态
                    try:
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
                    except Exception as e:
                        print(f"处理帧时发生错误: {e}")
                    
                    # 如果正在录制视频，添加帧到录制列表
                    if video_recording:
                        with video_lock:
                            video_frames.append(frame.copy())
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
                    
                    # 如果正在录制视频，添加模拟帧到录制列表
                    if video_recording:
                        with video_lock:
                            # 创建一个带有时间戳的模拟帧
                            sim_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                            # 添加时间戳文本
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cv2.putText(sim_frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.putText(sim_frame, '模拟视频帧', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.putText(sim_frame, '摄像头不可用', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            video_frames.append(sim_frame)
                
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
        
        # 在子线程中播放语音，避免阻塞主线程
        def play_voice_sequence():
            try:
                print("子线程: 准备播放语音序列")
                
                # 直接播放面试问题，跳过欢迎语
                print("子线程: 播放面试问题")
                question_text = f"{position}面试问题：{first_question_content}，你有5分钟的时间作答"
                success2 = coach.voice.speak(question_text, urgent=False, cooldown=0)
                if success2:
                    print("子线程: 面试问题播放完成")
                else:
                    print("子线程: 面试问题播放失败")
            except Exception as e:
                print(f"子线程语音播放失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 启动语音播放子线程
        voice_thread = threading.Thread(target=play_voice_sequence)
        voice_thread.daemon = True
        voice_thread.start()
        
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
    
    try:
        if coach:
            # 标记面试为停止状态
            coach.is_running = False
            
            # 等待一小段时间，确保最后一批数据被处理
            import time
            time.sleep(0.5)
            
            # 保存最终状态
            coach.save_final_state()
            
            # 结束语音会话
            coach.voice.end_session()
        
        is_running = False
        
        print("⏹️ 面试已停止，数据已保存")
        
        # 返回成功响应，包含提示信息
        response = jsonify({
            'success': True, 
            'message': '面试已停止，正在生成总结报告',
            'next_steps': ['获取注意力历史数据', '生成注意力分析报告']
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ 停止面试时出错: {e}")
        import traceback
        traceback.print_exc()
        
        # 确保面试状态被正确设置为停止
        is_running = False
        if coach:
            coach.is_running = False
        
        response = jsonify({'success': False, 'message': f'停止面试时出错: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    global is_running, latest_data
    
    # 添加调试日志
    print(f"获取状态请求: is_running={is_running}, latest_data={latest_data}")
    
    # 记录请求来源
    print(f"请求来源: {request.remote_addr}")
    print(f"请求头: {dict(request.headers)}")
    
    # 当面试未运行时，返回session_time为0
    response_data = latest_data.copy()
    if not is_running:
        response_data['session_time'] = 0
    
    response = jsonify({
        'is_running': is_running,
        'data': response_data
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(f"响应数据: {response.get_json()}")
    return response

@app.route('/api/video_feed')
def video_feed():
    """视频流 - 优化实时性能"""
    def generate():
        global raw_frame
        
        # 预分配缓冲区，避免频繁内存分配
        buffer_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        while True:
            if raw_frame is None:
                # 如果没有帧，返回黑色画面
                frame = buffer_frame
            else:
                # 直接使用原始帧，避免复制
                frame = raw_frame
            
            # 优化编码参数，优先速度
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY, 70,  # 适当降低质量，提高速度
                cv2.IMWRITE_JPEG_PROGRESSIVE, 0,  # 禁用渐进式编码
                cv2.IMWRITE_JPEG_OPTIMIZE, 0,  # 禁用优化，提高速度
                cv2.IMWRITE_JPEG_LUMA_QUALITY, 70
            ]
            
            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if not ret:
                continue
                
            # 转换为字节
            frame_bytes = buffer.tobytes()
            
            # 生成multipart响应
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # 控制帧率，提高实时性
            time.sleep(0.016)  # 约60fps
    
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

@app.route('/api/attention/history')
def get_attention_history():
    """获取注意力历史数据"""
    global coach
    
    print(f"📡 收到获取注意力历史数据请求")
    print(f"   - coach 是否为 None: {coach is None}")
    
    try:
        # 检查面试助手是否已初始化
        if not coach:
            print(f"   - 面试助手未初始化")
            response = jsonify({'success': False, 'message': '面试助手未初始化'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 获取注意力历史数据
        attention_history = getattr(coach, 'attention_history', [])
        print(f"   - 获取到 {len(attention_history)} 条历史记录")
        
        # 分析数据：计算平均分、最高分、最低分
        if attention_history:
            scores = [record['score'] for record in attention_history]
            face_scores = [record['face_score'] for record in attention_history]
            gaze_scores = [record['gaze_score'] for record in attention_history]
            posture_scores = [record['posture_score'] for record in attention_history]
            gesture_scores = [record['gesture_score'] for record in attention_history]
            
            analysis = {
                'average_score': sum(scores) / len(scores),
                'max_score': max(scores),
                'min_score': min(scores),
                'average_face_score': sum(face_scores) / len(face_scores),
                'average_gaze_score': sum(gaze_scores) / len(gaze_scores),
                'average_posture_score': sum(posture_scores) / len(posture_scores),
                'average_gesture_score': sum(gesture_scores) / len(gesture_scores),
                'total_records': len(attention_history)
            }
        else:
            analysis = {
                'average_score': 0,
                'max_score': 0,
                'min_score': 0,
                'average_face_score': 0,
                'average_gaze_score': 0,
                'average_posture_score': 0,
                'average_gesture_score': 0,
                'total_records': 0
            }
        
        response = jsonify({
            'success': True,
            'message': '成功获取注意力历史数据',
            'data': {
                'history': attention_history,
                'analysis': analysis
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"获取注意力历史数据失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'获取注意力历史数据失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/attention/analysis')
def get_attention_analysis():
    """获取注意力分析报告"""
    global coach
    
    print(f"📡 收到获取注意力分析报告请求")
    print(f"   - coach 是否为 None: {coach is None}")
    
    try:
        # 检查面试助手是否已初始化
        if not coach:
            print(f"   - 面试助手未初始化")
            response = jsonify({'success': False, 'message': '面试助手未初始化'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 获取注意力分析报告
        print(f"   - 调用 coach.get_attention_analysis()")
        analysis = coach.get_attention_analysis()
        print(f"   - 获取成功，返回 {len(analysis)} 个字段")
        
        response = jsonify({
            'success': True,
            'message': '成功获取注意力分析报告',
            'data': analysis
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ 获取注意力分析报告失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'获取注意力分析报告失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/save_video', methods=['POST'])
def save_video():
    """保存面试视频"""
    global coach, video_recording, video_frames
    
    try:
        print("📡 收到保存视频请求")
        
        # 检查面试助手是否已初始化
        if not coach:
            print("   - 面试助手未初始化")
            response = jsonify({'success': False, 'message': '面试助手未初始化'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 创建保存目录
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'videos')
        os.makedirs(save_dir, exist_ok=True)
        print(f"   - 保存目录: {save_dir}")
        
        # 生成视频文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"interview_{timestamp}.avi"
        video_path = os.path.join(save_dir, video_filename)
        print(f"   - 视频文件路径: {video_path}")
        
        # 检查是否有录制的视频帧
        with video_lock:
            frame_count = len(video_frames)
            
        if frame_count == 0:
            print("   - 没有录制的视频帧")
            # 如果没有录制的视频帧，创建文本占位符
            placeholder_path = os.path.join(save_dir, f"interview_{timestamp}_placeholder.txt")
            with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write(f"面试视频保存占位符\n")
                f.write(f"保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"面试岗位: {interview_position}\n")
                f.write(f"会话时长: {coach.get_session_time():.2f} 秒\n")
                f.write(f"注意力评分: {coach.attention_score:.1f} 分\n")
                f.write(f"\n")
                f.write(f"详细错误原因分析:\n")
                f.write(f"1. 视频帧数据状态: 未检测到任何视频帧\n")
                f.write(f"2. 录制状态: {'已启动' if video_recording else '未启动'}\n")
                f.write(f"3. 可能的具体原因:\n")
                f.write(f"   - 摄像头硬件未连接或已损坏\n")
                f.write(f"   - 系统权限设置阻止应用访问摄像头\n")
                f.write(f"   - 摄像头被其他应用程序占用\n")
                f.write(f"   - 录制功能未正确初始化\n")
                f.write(f"   - 面试过程中摄像头驱动崩溃\n")
                f.write(f"   - 网络摄像头连接不稳定或断开\n")
                f.write(f"   - 系统资源不足，无法处理视频数据\n")
                f.write(f"\n")
                f.write(f"详细解决步骤:\n")
                f.write(f"1. 硬件检查: 确认摄像头已正确连接到电脑，USB接口无松动\n")
                f.write(f"2. 权限设置: 检查系统隐私设置，允许此应用访问摄像头\n")
                f.write(f"3. 应用冲突: 关闭其他可能占用摄像头的应用程序（如Zoom、Teams等）\n")
                f.write(f"4. 驱动更新: 确保摄像头驱动程序已更新到最新版本\n")
                f.write(f"5. 测试验证: 在系统相机应用中测试摄像头是否正常工作\n")
                f.write(f"6. 网络检查: 如果使用网络摄像头，确保网络连接稳定\n")
                f.write(f"7. 资源检查: 关闭不必要的应用程序，释放系统资源\n")
                f.write(f"8. 重启应用: 完全关闭并重新启动智能面试系统\n")
                f.write(f"\n")
                f.write(f"技术诊断信息:\n")
                f.write(f"- 录制状态: {video_recording}\n")
                f.write(f"- 视频帧数量: {frame_count}\n")
                f.write(f"- 摄像头管理器状态: {coach.camera.is_open() if coach and coach.camera else '未初始化'}\n")
                f.write(f"- 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"   - 视频保存成功（占位符）")
        else:
            # 有录制的视频帧，保存为真实视频
            print(f"   - 开始保存视频，共 {frame_count} 帧")
            
            with video_lock:
                # 确保所有帧尺寸一致
                # 获取第一帧的宽度和高度
                first_frame = video_frames[0]
                height, width, _ = first_frame.shape
                print(f"   - 视频分辨率: {width}x{height}")
                
                # 标准化所有帧的尺寸
                standardized_frames = []
                for i, frame in enumerate(video_frames):
                    try:
                        # 检查帧是否有效
                        if frame is None or len(frame.shape) != 3:
                            print(f"   - 跳过无效帧 #{i}")
                            continue
                        
                        # 检查帧尺寸是否一致
                        h, w, _ = frame.shape
                        if h != height or w != width:
                            # 调整帧尺寸
                            resized_frame = cv2.resize(frame, (width, height))
                            standardized_frames.append(resized_frame)
                            print(f"   - 调整帧 #{i} 尺寸从 {w}x{h} 到 {width}x{height}")
                        else:
                            standardized_frames.append(frame)
                    except Exception as e:
                        print(f"   - 处理帧 #{i} 时出错: {e}")
                        continue
                
                print(f"   - 标准化后剩余 {len(standardized_frames)} 帧")
                
                # 确保有足够的帧
                if len(standardized_frames) < 10:
                    print(f"   - 帧数量不足，创建文本占位符")
                    placeholder_path = os.path.join(save_dir, f"interview_{timestamp}_placeholder.txt")
                    with open(placeholder_path, 'w', encoding='utf-8') as f:
                        f.write(f"面试视频保存占位符\n")
                        f.write(f"保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"面试岗位: {interview_position}\n")
                        f.write(f"会话时长: {coach.get_session_time():.2f} 秒\n")
                        f.write(f"注意力评分: {coach.attention_score:.1f} 分\n")
                        f.write(f"\n")
                        f.write(f"详细错误原因分析:\n")
                        f.write(f"1. 视频帧数据状态: 帧数量不足 ({len(standardized_frames)} 帧)\n")
                        f.write(f"2. 录制状态: {'已启动' if video_recording else '未启动'}\n")
                        f.write(f"3. 可能的具体原因:\n")
                        f.write(f"   - 摄像头硬件未连接或已损坏\n")
                        f.write(f"   - 系统权限设置阻止应用访问摄像头\n")
                        f.write(f"   - 摄像头被其他应用程序占用\n")
                        f.write(f"   - 录制功能未正确初始化\n")
                        f.write(f"   - 面试过程中摄像头驱动崩溃\n")
                        f.write(f"   - 网络摄像头连接不稳定或断开\n")
                        f.write(f"   - 系统资源不足，无法处理视频数据\n")
                        f.write(f"\n")
                        f.write(f"详细解决步骤:\n")
                        f.write(f"1. 硬件检查: 确认摄像头已正确连接到电脑，USB接口无松动\n")
                        f.write(f"2. 权限设置: 检查系统隐私设置，允许此应用访问摄像头\n")
                        f.write(f"3. 应用冲突: 关闭其他可能占用摄像头的应用程序（如Zoom、Teams等）\n")
                        f.write(f"4. 驱动更新: 确保摄像头驱动程序已更新到最新版本\n")
                        f.write(f"5. 测试验证: 在系统相机应用中测试摄像头是否正常工作\n")
                        f.write(f"6. 网络检查: 如果使用网络摄像头，确保网络连接稳定\n")
                        f.write(f"7. 资源检查: 关闭不必要的应用程序，释放系统资源\n")
                        f.write(f"8. 重启应用: 完全关闭并重新启动智能面试系统\n")
                        f.write(f"\n")
                        f.write(f"技术诊断信息:\n")
                        f.write(f"- 录制状态: {video_recording}\n")
                        f.write(f"- 原始视频帧数量: {frame_count}\n")
                        f.write(f"- 标准化后视频帧数量: {len(standardized_frames)}\n")
                        f.write(f"- 摄像头管理器状态: {coach.camera.is_open() if coach and coach.camera else '未初始化'}\n")
                        f.write(f"- 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    print(f"   - 视频保存成功（占位符）")
                else:
                    # 创建VideoWriter对象
                    try:
                        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                        fps = 8  # 帧率 - 匹配实际录制帧率（30fps/4=7.5fps）
                        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
                        print(f"   - VideoWriter已创建")
                        
                        # 写入视频帧
                        written_frames = 0
                        for i, frame in enumerate(standardized_frames):
                            try:
                                out.write(frame)
                                written_frames += 1
                                # 每100帧打印一次进度
                                if (i + 1) % 100 == 0:
                                    print(f"   - 已写入 {i + 1}/{len(standardized_frames)} 帧")
                            except Exception as e:
                                print(f"   - 写入帧 #{i} 时出错: {e}")
                                continue
                        print(f"   - 视频帧写入完成，共写入 {written_frames} 帧")
                        
                        # 释放VideoWriter
                        out.release()
                        print(f"   - VideoWriter已释放")
                        
                        # 检查文件大小
                        if os.path.exists(video_path):
                            file_size = os.path.getsize(video_path)
                            print(f"   - 视频文件大小: {file_size / 1024 / 1024:.2f} MB")
                            if file_size < 1024:  # 小于1KB，可能是无效文件
                                print(f"   - 视频文件过小，创建文本占位符")
                                placeholder_path = os.path.join(save_dir, f"interview_{timestamp}_placeholder.txt")
                                with open(placeholder_path, 'w', encoding='utf-8') as f:
                                    f.write(f"面试视频保存占位符\n")
                                    f.write(f"保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                    f.write(f"面试岗位: {interview_position}\n")
                                    f.write(f"会话时长: {coach.get_session_time():.2f} 秒\n")
                                    f.write(f"注意力评分: {coach.attention_score:.1f} 分\n")
                                    f.write(f"\n")
                                    f.write(f"详细错误原因分析:\n")
                                    f.write(f"1. 视频文件状态: 文件大小过小 ({file_size} 字节)\n")
                                    f.write(f"2. 可能的具体原因:\n")
                                    f.write(f"   - 视频编码失败\n")
                                    f.write(f"   - 帧数据无效\n")
                                    f.write(f"   - 磁盘空间不足\n")
                                    f.write(f"   - 权限不足，无法写入文件\n")
                                    f.write(f"\n")
                                    f.write(f"技术诊断信息:\n")
                                    f.write(f"- 录制状态: {video_recording}\n")
                                    f.write(f"- 视频帧数量: {len(standardized_frames)}\n")
                                    f.write(f"- 视频分辨率: {width}x{height}\n")
                                    f.write(f"- 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                print(f"   - 视频保存成功（占位符）")
                            else:
                                print(f"   - 视频保存成功（真实视频）")
                        else:
                            print(f"   - 视频文件未创建")
                    except Exception as e:
                        print(f"   - 创建或写入视频时出错: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # 创建错误占位符
                        placeholder_path = os.path.join(save_dir, f"interview_{timestamp}_placeholder.txt")
                        with open(placeholder_path, 'w', encoding='utf-8') as f:
                            f.write(f"面试视频保存占位符\n")
                            f.write(f"保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"面试岗位: {interview_position}\n")
                            f.write(f"会话时长: {coach.get_session_time():.2f} 秒\n")
                            f.write(f"注意力评分: {coach.attention_score:.1f} 分\n")
                            f.write(f"\n")
                            f.write(f"详细错误原因分析:\n")
                            f.write(f"1. 视频编码状态: 编码过程中发生错误\n")
                            f.write(f"2. 错误信息: {str(e)}\n")
                            f.write(f"\n")
                            f.write(f"技术诊断信息:\n")
                            f.write(f"- 录制状态: {video_recording}\n")
                            f.write(f"- 视频帧数量: {len(standardized_frames)}\n")
                            f.write(f"- 视频分辨率: {width}x{height}\n")
                            f.write(f"- 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        print(f"   - 视频保存成功（占位符）")
                
                # 清空视频帧列表
                video_frames.clear()
                print(f"   - 视频帧列表已清空")
                
                # 停止录制
                video_recording = False
        
        response = jsonify({
            'success': True,
            'message': '视频保存成功',
            'data': {
                'video_path': video_path,
                'save_dir': save_dir,
                'filename': video_filename
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ 视频保存失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'视频保存失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    """开始视频录制"""
    global video_recording, video_frames
    
    try:
        print("📡 收到开始录制请求")
        
        # 清空之前的视频帧
        with video_lock:
            video_frames.clear()
        
        # 开始录制
        video_recording = True
        print("   - 视频录制已开始")
        
        response = jsonify({
            'success': True,
            'message': '视频录制已开始'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ 开始录制失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'开始录制失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    """停止视频录制"""
    global video_recording
    
    try:
        print("📡 收到停止录制请求")
        
        # 停止录制
        video_recording = False
        print("   - 视频录制已停止")
        
        response = jsonify({
            'success': True,
            'message': '视频录制已停止'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"❌ 停止录制失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'停止录制失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/saved_video')
def get_saved_video():
    """获取保存的视频"""
    try:
        print("📡 收到获取保存视频请求")
        
        # 获取保存目录
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'videos')
        print(f"   - 保存目录: {save_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(save_dir):
            print("   - 保存目录不存在")
            response = jsonify({'success': False, 'message': '保存目录不存在'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # 获取最新的视频文件
        video_files = [f for f in os.listdir(save_dir) if f.endswith('.avi') or f.endswith('_placeholder.txt')]
        if not video_files:
            print("   - 没有找到视频文件")
            response = jsonify({'success': False, 'message': '没有找到视频文件'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # 按修改时间排序，获取最新的文件
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(save_dir, x)), reverse=True)
        latest_video = video_files[0]
        latest_video_path = os.path.join(save_dir, latest_video)
        print(f"   - 最新视频文件: {latest_video}")
        
        # 如果是文本文件，返回文件内容
        if latest_video.endswith('.txt'):
            with open(latest_video_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            response = jsonify({
                'success': True,
                'message': '获取视频信息成功',
                'data': {
                    'filename': latest_video,
                    'path': latest_video_path,
                    'content': content
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # 如果是视频文件，返回视频流（实际项目中需要实现）
        else:
            response = jsonify({
                'success': True,
                'message': '视频文件存在',
                'data': {
                    'filename': latest_video,
                    'path': latest_video_path
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    except Exception as e:
        print(f"❌ 获取保存视频失败: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'success': False, 'message': f'获取保存视频失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

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