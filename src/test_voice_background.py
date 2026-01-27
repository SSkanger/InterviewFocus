#!/usr/bin/env python3
# 后台语音播放测试脚本

import os
import sys
import time

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_utils import VoiceFeedback

def test_edge_tts_background():
    """测试 Edge TTS 后台播放"""
    print("====================================")
    print("    Edge TTS 后台播放测试")
    print("====================================")
    print("请确保系统音量已开启！")
    print("====================================")
    print("\n测试目标:")
    print("1. Edge TTS 在后台播放（不打开系统播放器）")
    print("2. 只播放 Edge TTS 的声音，不播放 pyttsx3 的声音")
    print("\n按 Enter 键开始测试...")
    input()
    
    # 初始化语音系统
    voice_system = VoiceFeedback()
    
    # 测试文本
    test_text = "这是 Edge TTS 后台播放测试，你应该只听到一次清晰的语音，并且不会打开系统播放器。"
    
    print(f"\n测试文本: {test_text}")
    print("正在播放 Edge TTS 语音...")
    print("请仔细聆听，应该听到清晰的 Edge TTS 语音，并且不会打开系统播放器窗口。")
    
    # 播放语音
    start_time = time.time()
    success = voice_system.speak(test_text)
    end_time = time.time()
    
    print(f"\n播放结果: {'✅ 成功' if success else '❌ 失败'}")
    print(f"播放耗时: {end_time - start_time:.1f} 秒")
    
    # 询问用户
    print("\n====================================")
    print("    测试反馈")
    print("====================================")
    
    # 问题1
    heard = input("你听到 Edge TTS 的语音了吗？(y/n): ").strip().lower()
    if heard == 'y':
        print("✅ 很好！你听到了 Edge TTS 的语音。")
    else:
        print("❌ 你没有听到 Edge TTS 的语音。")
    
    # 问题2
    player_opened = input("系统播放器窗口打开了吗？(y/n): ").strip().lower()
    if player_opened == 'n':
        print("✅ 很好！系统播放器没有打开，实现了后台播放。")
    else:
        print("⚠️ 系统播放器打开了，后台播放功能未完全实现。")
    
    # 问题3
    double_play = input("你听到了两次语音吗？(y/n): ").strip().lower()
    if double_play == 'n':
        print("✅ 很好！只听到了一次语音，没有同时播放 pyttsx3 的声音。")
    else:
        print("❌ 你听到了两次语音，说明同时播放了 Edge TTS 和 pyttsx3 的声音。")
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")

if __name__ == "__main__":
    test_edge_tts_background()
