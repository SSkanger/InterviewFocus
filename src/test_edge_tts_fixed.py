#!/usr/bin/env python3
# 修复的 Edge TTS 测试脚本

import edge_tts
import asyncio
import os
import time

def test_edge_tts():
    """测试修复后的 Edge TTS"""
    print("====================================")
    print("    修复后的 Edge TTS 测试")
    print("====================================")
    print("请确保系统音量已开启！")
    print("====================================")
    
    async def generate_and_play():
        # 测试文本
        test_texts = [
            "这是 Edge TTS 测试语音，声音质量应该比 pyttsx3 更好。",
            "智能面试模拟系统欢迎您，祝您面试成功！",
            "请注意保持良好的面试姿态，展现您的专业形象。"
        ]
        
        # 测试语音
        voices = [
            "zh-CN-XiaoxiaoNeural",  # 中文女声
            "zh-CN-YunxiNeural",     # 中文女声
            "zh-CN-YunxiNeural"      # 中文女声
        ]
        
        for i, (text, voice) in enumerate(zip(test_texts, voices)):
            print(f"\n测试 {i+1}/{len(test_texts)}:")
            print(f"语音: {voice}")
            print(f"文本: {text}")
            
            # 生成语音
            communicate = edge_tts.Communicate(text, voice)
            
            # 保存为 MP3 文件（正确的格式）
            output_file = f"test_edge_tts_{i+1}.mp3"
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ 音频文件生成成功: {output_file}")
                print(f"文件大小: {file_size} 字节")
                
                # 使用系统默认播放器播放
                print("正在使用系统播放器播放 Edge TTS 语音...")
                print("请仔细聆听，这应该是 Edge TTS 的高质量语音！")
                
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_file)
                        print("✅ 系统播放器已启动")
                    else:  # 其他系统
                        import subprocess
                        subprocess.run(['xdg-open', output_file])
                        print("✅ 系统播放器已启动")
                    
                    # 等待播放完成（根据文本长度估算）
                    estimated_duration = len(text) / 5 + 2  # 每秒约5个汉字
                    print(f"等待 {estimated_duration:.1f} 秒让语音播放完成...")
                    time.sleep(estimated_duration)
                    
                except Exception as e:
                    print(f"❌ 播放失败: {e}")
                
                # 清理文件
                os.remove(output_file)
                print(f"✅ 临时文件已清理: {output_file}")
            else:
                print(f"❌ 音频文件生成失败")
    
    # 运行测试
    asyncio.run(generate_and_play())
    
    print("\n====================================")
    print("    测试完成")
    print("====================================")
    print("如果听到了清晰的语音，说明 Edge TTS 工作正常！")
    print("如果仍然没有听到，可能的原因:")
    print("1. 系统默认播放器无法播放 MP3 文件")
    print("2. 网络连接问题")
    print("3. Edge TTS API 访问限制")

def main():
    """主函数"""
    test_edge_tts()

if __name__ == "__main__":
    main()
