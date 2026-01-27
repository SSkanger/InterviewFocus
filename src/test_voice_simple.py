#!/usr/bin/env python3
# 简单语音测试脚本

import os
import time
import winsound
import requests
import socket

def test_sound_playback():
    """测试声音播放功能"""
    print("测试基本声音播放...")
    try:
        # 播放系统默认声音
        winsound.MessageBeep()
        print("✅ 系统声音播放成功")
        return True
    except Exception as e:
        print(f"❌ 声音播放失败: {e}")
        return False

def test_network():
    """测试网络连接"""
    print("测试网络连接...")
    test_urls = [
        "https://www.baidu.com",
        "https://api-edge-tts.microsoft.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} 连接成功，状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} 连接失败: {e}")

def test_edge_tts_direct():
    """直接测试 Edge TTS"""
    print("\n测试 Edge TTS...")
    
    try:
        import edge_tts
        import asyncio
        
        async def main():
            text = "这是 Edge TTS 测试语音"
            voice = "zh-CN-XiaoxiaoNeural"
            
            print(f"使用语音: {voice}")
            print(f"测试文本: {text}")
            
            # 创建通信对象
            communicate = edge_tts.Communicate(text, voice)
            
            # 保存音频文件
            output_file = "test_edge_tts_direct.wav"
            await communicate.save(output_file)
            
            print(f"✅ 音频文件生成成功: {output_file}")
            print(f"文件大小: {os.path.getsize(output_file)} 字节")
            
            # 播放音频
            print("正在播放音频...")
            winsound.PlaySound(output_file, winsound.SND_FILENAME)
            print("✅ 音频播放完成")
            
            # 清理文件
            os.remove(output_file)
            print(f"✅ 临时文件已清理")
            
            return True
        
        return asyncio.run(main())
        
    except ImportError:
        print("❌ Edge TTS 未安装")
        return False
    except Exception as e:
        print(f"❌ Edge TTS 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pyttsx3():
    """测试 pyttsx3 备用方案"""
    print("\n测试 pyttsx3 备用方案...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.8)
        
        print("✅ pyttsx3 初始化成功")
        print("正在播放 pyttsx3 语音...")
        
        engine.say("这是 pyttsx3 测试语音")
        engine.runAndWait()
        
        print("✅ pyttsx3 语音播放完成")
        return True
        
    except ImportError:
        print("❌ pyttsx3 未安装")
        return False
    except Exception as e:
        print(f"❌ pyttsx3 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("====================================")
    print("    语音功能综合测试")
    print("====================================")
    
    # 测试声音播放
    sound_ok = test_sound_playback()
    
    # 测试网络连接
    test_network()
    
    # 测试 Edge TTS
    edge_ok = test_edge_tts_direct()
    
    # 测试 pyttsx3
    pyttsx3_ok = test_pyttsx3()
    
    print("\n====================================")
    print("    测试结果")
    print("====================================")
    print(f"声音播放: {'✅ 正常' if sound_ok else '❌ 异常'}")
    print(f"Edge TTS: {'✅ 正常' if edge_ok else '❌ 异常'}")
    print(f"pyttsx3: {'✅ 正常' if pyttsx3_ok else '❌ 异常'}")
    
    if not sound_ok:
        print("\n🔧 声音播放问题解决方案:")
        print("1. 检查系统音量是否开启")
        print("2. 检查扬声器是否正常工作")
        print("3. 尝试以管理员身份运行脚本")
    
    if not edge_ok:
        print("\n🔧 Edge TTS 问题解决方案:")
        print("1. 检查网络连接是否稳定")
        print("2. 尝试使用较低版本的 edge-tts")
        print("3. 检查防火墙是否阻止连接")
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")

if __name__ == "__main__":
    main()
