#!/usr/bin/env python3
# 简单语音测试脚本

import pyttsx3

def test_simple_voice():
    """测试简单语音功能"""
    print("开始简单语音测试...")
    
    try:
        # 创建引擎实例
        engine = pyttsx3.init()
        print("创建引擎成功")
        
        # 设置属性
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.8)
        print("设置引擎属性成功")
        
        # 测试播放欢迎语
        print("播放欢迎语...")
        engine.say("欢迎使用智能面试模拟系统")
        engine.runAndWait()
        print("欢迎语播放完成")
        
        # 测试播放面试问题
        print("\n播放面试问题...")
        engine.say("请介绍一下你自己")
        engine.runAndWait()
        print("面试问题播放完成")
        
        # 测试连续播放
        print("\n连续播放测试...")
        engine.say("这是第一个问题")
        engine.say("这是第二个问题")
        engine.say("这是第三个问题")
        engine.runAndWait()
        print("连续播放完成")
        
        return True
        
    except Exception as e:
        print(f"语音测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_voice()
    if success:
        print("\n✅ 语音测试通过！")
    else:
        print("\n❌ 语音测试失败！")
