#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CosyVoice语音生成脚本
使用cosyvoice自带的Python环境运行，确保依赖完整
"""
import sys
import os
import torch
import torchaudio
import io
import winsound
from datetime import datetime

# 添加cosyvoice路径
cosyvoice_path = "D:\PycharmProject\pywork\cosyvoice-rainfall"
sys.path.append(cosyvoice_path)

# 修复whisper库问题
try:
    import ctypes
    original_cdll = ctypes.CDLL
    
    def patched_cdll(name, *args, **kwargs):
        if name is None:
            class MockCDLL:
                def __getattr__(self, attr):
                    return lambda *args, **kwargs: None
            return MockCDLL()
        return original_cdll(name, *args, **kwargs)
    
    ctypes.CDLL = patched_cdll
except Exception as e:
    print(f"⚠️ 修复whisper库时出错: {e}")

# 导入CosyVoice模型
from cosyvoice.cli.cosyvoice import AutoModel

def generate_voice(text, voice_id="中文女", speed=1.0, temp_file=None):
    """
    生成语音并保存到临时文件
    
    Args:
        text: 要生成的文本
        voice_id: 语音ID，默认为"中文女"
        speed: 语速，默认为1.0
        temp_file: 临时文件路径，不提供则自动生成
    
    Returns:
        str: 生成的音频文件路径
    """
    try:
        # 加载模型
        model_dir = os.path.join(cosyvoice_path, "models", "CosyVoice3-0.5B")
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"模型目录不存在: {model_dir}")
        
        print(f"🔄 加载CosyVoice模型: {model_dir}")
        model = AutoModel(model_dir=model_dir, fp16=False)
        sample_rate = model.sample_rate
        print(f"✅ 模型加载成功，采样率: {sample_rate}")
        
        # 生成音频
        print(f"🔊 生成语音: {text}")
        audio_chunks = []
        for output in model.inference_sft(
            tts_text=text,
            spk_id=voice_id,
            stream=False,
            speed=speed
        ):
            audio = output['tts_speech']
            audio_chunks.append(audio)
        
        if not audio_chunks:
            raise ValueError("未生成音频数据")
        
        # 拼接音频
        audio = torch.cat(audio_chunks, dim=1)
        
        # 保存到临时文件
        if temp_file is None:
            temp_file = f"temp_tts_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        
        torchaudio.save(temp_file, audio.cpu(), sample_rate=sample_rate, format="wav")
        print(f"✅ 音频已保存到: {temp_file}")
        
        return temp_file
        
    except Exception as e:
        print(f"❌ 生成语音失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def play_audio(file_path):
    """
    播放音频文件
    
    Args:
        file_path: 音频文件路径
    
    Returns:
        bool: 是否播放成功
    """
    try:
        if os.path.exists(file_path):
            print(f"🔊 播放音频: {file_path}")
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
            print("✅ 音频播放成功")
            return True
        else:
            print(f"❌ 音频文件不存在: {file_path}")
            return False
    except Exception as e:
        print(f"❌ 播放音频失败: {e}")
        return False

def main():
    """
    主函数
    用法: python cosyvoice_generate.py "要生成的文本" [语音ID] [语速]
    """
    if len(sys.argv) < 2:
        print('用法: python cosyvoice_generate.py "要生成的文本" [语音ID] [语速]')
        sys.exit(1)
    
    text = sys.argv[1]
    voice_id = sys.argv[2] if len(sys.argv) > 2 else "中文女"
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    # 生成语音
    temp_file = generate_voice(text, voice_id, speed)
    
    if temp_file:
        # 播放语音
        play_audio(temp_file)
        
        # 清理临时文件
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️  已删除临时文件: {temp_file}")
        except Exception as e:
            print(f"⚠️ 删除临时文件失败: {e}")
    else:
        print("❌ 生成语音失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
