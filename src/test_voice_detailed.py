#!/usr/bin/env python3
# 详细语音测试脚本

import os
import time
import winsound
import subprocess
import wave
import edge_tts
import asyncio
import pyttsx3

def check_audio_file(file_path):
    """检查音频文件是否有效"""
    if not os.path.exists(file_path):
        print(f"❌ 音频文件不存在: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    print(f"文件大小: {file_size} 字节")
    
    if file_size < 1000:
        print(f"⚠️ 音频文件可能为空或损坏: {file_size} 字节")
        return False
    
    try:
        with wave.open(file_path, 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            nframes = wf.getnframes()
            duration = nframes / float(framerate)
            
            print(f"音频信息:")
            print(f"  声道: {channels}")
            print(f"  采样宽度: {sample_width} 字节")
            print(f"  采样率: {framerate} Hz")
            print(f"  帧数: {nframes}")
            print(f"  时长: {duration:.2f} 秒")
            return True
    except Exception as e:
        print(f"❌ 音频文件检查失败: {e}")
        return False

def play_audio(file_path):
    """播放音频文件，使用多种方法"""
    print("\n尝试播放音频...")
    
    # 方法1: winsound
    print("方法1: 使用 winsound 播放")
    try:
        winsound.PlaySound(file_path, winsound.SND_FILENAME)
        print("✅ winsound 播放完成")
    except Exception as e:
        print(f"❌ winsound 播放失败: {e}")
    
    time.sleep(1)
    
    # 方法2: 系统默认播放器
    print("\n方法2: 使用系统默认播放器")
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
            print("✅ 系统播放器已启动")
            time.sleep(3)  # 等待播放
        else:
            print("⚠️ 非 Windows 系统，跳过系统播放器测试")
    except Exception as e:
        print(f"❌ 系统播放器启动失败: {e}")
    
    time.sleep(1)

def test_edge_tts():
    """测试 Edge TTS"""
    print("\n====================================")
    print("    Edge TTS 详细测试")
    print("====================================")
    
    test_texts = [
        "这是 Edge TTS 测试语音，声音质量应该比 pyttsx3 更好。",
        "智能面试模拟系统欢迎您，祝您面试成功！",
        "请注意保持良好的面试姿态，展现您的专业形象。"
    ]
    
    voices = [
        "zh-CN-XiaoxiaoNeural",  # 中文女声
        "zh-CN-YunxiNeural",     # 另一个中文女声
        "zh-CN-YunxiNeural"      # 中文男声
    ]
    
    for i, (text, voice) in enumerate(zip(test_texts, voices)):
        print(f"\n测试 {i+1}/{len(test_texts)}:")
        print(f"语音: {voice}")
        print(f"文本: {text}")
        
        output_file = f"test_edge_tts_{i+1}.wav"
        
        try:
            # 生成语音
            communicate = edge_tts.Communicate(text, voice)
            asyncio.run(communicate.save(output_file))
            print("✅ Edge TTS 生成成功")
            
            # 检查音频文件
            if check_audio_file(output_file):
                # 播放音频
                play_audio(output_file)
            
        except Exception as e:
            print(f"❌ Edge TTS 测试失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理文件
            if os.path.exists(output_file):
                os.remove(output_file)
                print(f"✅ 临时文件已清理: {output_file}")

def test_pyttsx3():
    """测试 pyttsx3"""
    print("\n====================================")
    print("    pyttsx3 测试")
    print("====================================")
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)  # 最大音量
        
        print("✅ pyttsx3 初始化成功")
        print("正在播放 pyttsx3 语音...")
        
        engine.say("这是 pyttsx3 测试语音，你应该能听到这个声音。")
        engine.runAndWait()
        
        print("✅ pyttsx3 语音播放完成")
        return True
        
    except Exception as e:
        print(f"❌ pyttsx3 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("====================================")
    print("    详细语音测试")
    print("====================================")
    print("请确保系统音量已开启并调至合适大小！")
    print("====================================")
    
    # 测试 Edge TTS
    test_edge_tts()
    
    # 测试 pyttsx3
    test_pyttsx3()
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")
    print("如果只听到 pyttsx3 的语音，可能的原因:")
    print("1. Edge TTS 音频文件生成有问题")
    print("2. 网络连接问题导致 Edge TTS 失败")
    print("3. 音频播放设备设置问题")

if __name__ == "__main__":
    main()
