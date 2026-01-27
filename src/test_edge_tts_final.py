#!/usr/bin/env python3
# 最终版 Edge TTS 测试脚本

import edge_tts
import asyncio
import os
import time

def test_edge_tts():
    """最终版 Edge TTS 测试"""
    print("====================================")
    print("    最终版 Edge TTS 测试")
    print("====================================")
    print("请确保系统音量已开启并调至合适大小！")
    print("====================================")
    print("\n提示：系统将自动打开播放器播放 Edge TTS 语音")
    print("请仔细聆听，这应该是高质量的 Edge TTS 语音！")
    print("\n按 Enter 键开始测试...")
    input()
    
    async def generate_and_play():
        # 测试文本
        test_text = "这是 Edge TTS 测试语音，声音质量应该比 pyttsx3 更好。智能面试模拟系统欢迎您，祝您面试成功！"
        voice = "zh-CN-XiaoxiaoNeural"  # 中文女声
        
        print(f"\n测试语音: {voice}")
        print(f"测试文本: {test_text}")
        
        # 生成语音
        print("正在生成 Edge TTS 语音...")
        communicate = edge_tts.Communicate(test_text, voice)
        
        # 保存为 MP3 文件
        output_file = "test_edge_tts_final.mp3"
        await communicate.save(output_file)
        
        # 检查文件
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 音频文件生成成功: {output_file}")
            print(f"文件大小: {file_size} 字节")
            
            # 使用系统默认播放器播放
            print("\n正在打开系统播放器播放 Edge TTS 语音...")
            print("请仔细聆听，这应该是 Edge TTS 的高质量语音！")
            
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_file)
                    print("✅ 系统播放器已启动")
                    print("\n🎵 正在播放 Edge TTS 语音...")
                    print("请仔细聆听，这是 Microsoft Edge TTS 的高质量语音！")
                    print("\n如果你听到了清晰自然的语音，说明 Edge TTS 工作正常！")
                    print("如果没有听到，请检查系统音量和播放器设置。")
                else:
                    import subprocess
                    subprocess.run(['xdg-open', output_file])
                    print("✅ 系统播放器已启动")
                
                # 等待足够时间让用户听到语音
                estimated_duration = len(test_text) / 4 + 5  # 每秒约4个汉字，加5秒缓冲
                print(f"\n等待 {estimated_duration:.1f} 秒让语音播放完成...")
                print("请在此期间仔细聆听 Edge TTS 的语音质量！")
                time.sleep(estimated_duration)
                
                # 询问用户是否听到了语音
                print("\n====================================")
                print("    测试反馈")
                print("====================================")
                heard = input("你听到 Edge TTS 的语音了吗？(y/n): ").strip().lower()
                
                if heard == 'y':
                    print("✅ 太好了！Edge TTS 工作正常！")
                    print("你现在听到的是 Microsoft Edge TTS 的高质量语音。")
                else:
                    print("❌ 你没有听到 Edge TTS 的语音。")
                    print("可能的原因:")
                    print("1. 系统音量太低")
                    print("2. 系统播放器有问题")
                    print("3. 音频文件生成有问题")
                
            except Exception as e:
                print(f"❌ 播放失败: {e}")
                print("请手动打开文件播放:", output_file)
            
        else:
            print(f"❌ 音频文件生成失败")
    
    # 运行测试
    asyncio.run(generate_and_play())
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")
    print("测试文件已保留在: test_edge_tts_final.mp3")
    print("你可以手动打开这个文件再次聆听 Edge TTS 的语音。")

def main():
    """主函数"""
    test_edge_tts()

if __name__ == "__main__":
    main()
