#!/usr/bin/env python3
# Edge TTS 测试脚本

import edge_tts
import asyncio
import os
import winsound
import time

def test_edge_tts():
    """测试 Edge TTS 语音合成功能"""
    print("====================================")
    print("    Edge TTS 语音测试")
    print("====================================")
    print("正在生成测试语音...")
    print("使用语音: zh-CN-XiaoxiaoNeural (中文女声)")
    
    async def generate_and_play():
        # 测试文本
        test_texts = [
            "这是 Edge TTS 的测试语音，声音质量应该比 pyttsx3 更好。",
            "智能面试模拟系统欢迎您，祝您面试成功！",
            "请注意保持良好的面试姿态，展现您的专业形象。"
        ]
        
        for i, text in enumerate(test_texts):
            print(f"\n测试 {i+1}/{len(test_texts)}:")
            print(f"文本: {text}")
            
            # 生成语音
            communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
            temp_file = f"test_edge_tts_{i+1}.wav"
            
            try:
                # 保存语音文件
                await communicate.save(temp_file)
                print("✅ Edge TTS 生成成功")
                
                # 检查文件是否存在且不为空
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    print("正在播放语音...")
                    # 播放音频
                    winsound.PlaySound(temp_file, winsound.SND_FILENAME)
                    
                    # 等待播放完成
                    estimated_duration = len(text) / 160 * 60 + 2
                    time.sleep(estimated_duration)
                    print("✅ 语音播放完成")
                else:
                    print("⚠️ 音频文件不存在或为空")
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"已清理临时文件: {temp_file}")
    
    # 运行异步测试
    asyncio.run(generate_and_play())
    print("\n====================================")
    print("    测试完成")
    print("====================================")
    print("如果您听到了清晰自然的语音，说明 Edge TTS 工作正常！")
    print("如果没有听到语音或出现错误，请检查网络连接和 Edge TTS 安装。")

if __name__ == "__main__":
    test_edge_tts()
