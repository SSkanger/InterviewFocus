import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_utils import VoiceFeedback

# 测试语音API功能
if __name__ == "__main__":
    print("测试CosyVoice API语音生成功能")
    print("=" * 50)
    
    # 初始化语音反馈系统
    voice = VoiceFeedback()
    
    # 测试语音生成
    test_text = "这是一个测试，测试CosyVoice API的语音生成功能"
    print(f"\n测试文本: {test_text}")
    print("正在调用CosyVoice API...")
    
    success = voice.speak(test_text, urgent=False, cooldown=0)
    
    if success:
        print("✅ 语音生成和播放成功")
    else:
        print("❌ 语音生成或播放失败")
    
    print("\n" + "=" * 50)
    print("测试完成")
