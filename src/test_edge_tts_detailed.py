#!/usr/bin/env python3
# Edge TTS 详细测试脚本（含网络诊断）

import edge_tts
import asyncio
import os
import winsound
import time
import socket
import requests
import traceback

def test_network_connection():
    """测试网络连接状态"""
    print("====================================")
    print("    网络连接诊断")
    print("====================================")
    
    # 测试基本网络连接
    try:
        # 测试 DNS 解析
        print("测试 DNS 解析...")
        socket.gethostbyname("api-edge-tts.microsoft.com")
        print("✅ DNS 解析成功")
        
        # 测试网络连接
        print("测试网络连接...")
        response = requests.get("https://api-edge-tts.microsoft.com", timeout=5)
        print(f"✅ 网络连接成功，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        print("可能的原因:")
        print("1. 防火墙阻止了连接")
        print("2. 网络连接不稳定")
        print("3. 系统 TLS 配置问题")
        return False

def test_edge_tts_fallback():
    """测试 Edge TTS 或使用备用方案"""
    print("\n====================================")
    print("    语音合成测试")
    print("====================================")
    
    # 测试文本
    test_text = "这是语音合成测试，您应该能听到清晰的语音。"
    
    # 尝试 Edge TTS
    print("\n尝试使用 Edge TTS...")
    
    async def try_edge_tts():
        try:
            # 使用不同的语音尝试
            voices = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]
            
            for voice in voices:
                print(f"\n测试语音: {voice}")
                temp_file = f"test_{voice.replace('-', '_')}.wav"
                
                try:
                    communicate = edge_tts.Communicate(test_text, voice=voice)
                    await communicate.save(temp_file)
                    print("✅ Edge TTS 生成成功")
                    
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        print("正在播放语音...")
                        winsound.PlaySound(temp_file, winsound.SND_FILENAME)
                        time.sleep(len(test_text) / 10 + 2)  # 等待播放完成
                        print("✅ 语音播放完成")
                        os.remove(temp_file)
                        return True
                    else:
                        print("⚠️ 音频文件为空")
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            
                except Exception as e:
                    print(f"❌ 语音 {voice} 测试失败: {e}")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Edge TTS 初始化失败: {e}")
            traceback.print_exc()
            return False
    
    # 运行 Edge TTS 测试
    edge_tts_success = asyncio.run(try_edge_tts())
    
    if not edge_tts_success:
        print("\n⚠️ Edge TTS 测试失败，尝试使用 pyttsx3 作为备用...")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 0.8)
            print("✅ pyttsx3 初始化成功")
            print("正在播放 pyttsx3 语音...")
            engine.say(test_text)
            engine.runAndWait()
            print("✅ pyttsx3 语音播放完成")
            return True
        except Exception as e:
            print(f"❌ pyttsx3 测试失败: {e}")
            return False
    
    return edge_tts_success

def main():
    """主测试函数"""
    print("====================================")
    print("    Edge TTS 详细测试")
    print("====================================")
    
    # 测试网络连接
    network_ok = test_network_connection()
    
    # 测试语音合成
    voice_success = test_edge_tts_fallback()
    
    print("\n====================================")
    print("    测试结果汇总")
    print("====================================")
    print(f"网络连接: {'✅ 正常' if network_ok else '❌ 异常'}")
    print(f"语音合成: {'✅ 成功' if voice_success else '❌ 失败'}")
    
    if not network_ok:
        print("\n建议解决方案:")
        print("1. 检查防火墙设置，确保允许 Python 访问网络")
        print("2. 尝试连接不同的网络环境")
        print("3. 检查系统 TLS 配置问题")
    
    if not voice_success:
        print("\n语音合成失败原因:")
        print("1. 网络连接问题")
        print("2. Edge TTS API 访问限制")
        print("3. 系统安全设置阻止")
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")

if __name__ == "__main__":
    main()
