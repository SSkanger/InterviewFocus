#!/usr/bin/env python3
# 语音测试脚本

import pyttsx3
import time

def test_voice_basic():
    """测试基本语音功能"""
    print("开始测试基本语音功能...")
    
    try:
        # 创建engine实例
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.8)
        
        # 测试1: 简单文本
        print("测试1: 播放简单文本")
        engine.say("这是一个语音测试")
        engine.runAndWait()
        
        time.sleep(1)
        
        # 测试2: 长文本
        print("测试2: 播放长文本")
        engine.say("你好，欢迎使用智能面试模拟系统。我将为你播放面试问题，请仔细听。")
        engine.runAndWait()
        
        time.sleep(1)
        
        # 测试3: 带职业的问题
        print("测试3: 播放带职业的面试问题")
        engine.say("Python开发工程师面试问题：请介绍一下你对面向对象编程的理解，你有5分钟的时间作答。")
        engine.runAndWait()
        
        print("✅ 所有基本测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基本语音测试失败: {e}")
        return False

def test_voice_threading():
    """测试多线程语音功能"""
    print("\n开始测试多线程语音功能...")
    
    import threading
    
    def speak(text, delay=0):
        time.sleep(delay)
        print(f"线程 {threading.current_thread().name}: 准备播放 '{text}'")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.8)
        engine.say(text)
        engine.runAndWait()
        print(f"线程 {threading.current_thread().name}: 播放完成")
    
    try:
        # 创建两个线程，顺序播放
        t1 = threading.Thread(target=speak, args=("欢迎语：面试练习开始，请保持专业姿态",), name="欢迎线程")
        t2 = threading.Thread(target=speak, args=("面试问题：请介绍一下你自己", 2), name="问题线程")
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        print("✅ 多线程测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 多线程测试失败: {e}")
        return False

def test_voice_utils_integration():
    """测试与voice_utils的集成"""
    print("\n开始测试voice_utils集成...")
    
    try:
        from voice_utils import VoiceFeedback
        
        # 创建VoiceFeedback实例
        voice = VoiceFeedback()
        
        # 测试1: 欢迎语
        print("测试1: 播放欢迎语")
        voice.speak("面试练习开始，请保持专业姿态", cooldown=0)
        
        time.sleep(2)
        
        # 测试2: 面试问题
        print("测试2: 播放面试问题")
        voice.ask_question("请介绍一下你的项目经验", "Python开发工程师")
        
        print("✅ voice_utils集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ voice_utils集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("========================================================")
    print("语音功能测试脚本")
    print("========================================================")
    
    # 运行所有测试
    basic_result = test_voice_basic()
    threading_result = test_voice_threading()
    utils_result = test_voice_utils_integration()
    
    print("\n========================================================")
    print("测试结果汇总：")
    print(f"基本语音测试: {'✅ 通过' if basic_result else '❌ 失败'}")
    print(f"多线程测试: {'✅ 通过' if threading_result else '❌ 失败'}")
    print(f"voice_utils集成测试: {'✅ 通过' if utils_result else '❌ 失败'}")
    print("========================================================")
