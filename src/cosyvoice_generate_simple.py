#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import numpy as np
import wave
import winsound

# 设置系统编码为UTF-8，防止Unicode编码错误
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 修补ctypes.CDLL，解决whisper库在Windows上的导入问题
import ctypes
original_cdll = ctypes.CDLL
def patched_cdll(name, *args, **kwargs):
    if name is None:
        return None
    return original_cdll(name, *args, **kwargs)
ctypes.CDLL = patched_cdll

# 添加cosyvoice模块路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cosyvoice-rainfall')))

from cosyvoice.cli.cosyvoice import CosyVoice

def generate_and_play(text):
    # 加载模型
    model_path = os.path.join(os.path.dirname(__file__), '..', 'cosyvoice-rainfall', 'models', 'CosyVoice3-0.5B')
    model = CosyVoice(model_path)
    
    # 生成语音
    print(f"生成语音: {text}")
    wav = model.inference_sft(text, "中文女")
    
    # 播放语音
    if wav is not None:
        print("播放语音...")
        # 确保音频数据在有效范围内
        wav = np.clip(wav, -1.0, 1.0)
        
        # 将音频数据转换为16位整数
        wav_int = (wav * 32767).astype(np.int16)
        
        # 创建临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # 写入WAV文件
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(1)  # 单声道
            wf.setsampwidth(2)  # 16位
            wf.setframerate(24000)  # 采样率
            wf.writeframes(wav_int.tobytes())
        
        # 播放WAV文件
        winsound.PlaySound(temp_filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        # 等待播放完成
        import time
        time.sleep(len(wav) / 24000 + 0.5)  # 估算播放时间
        
        # 删除临时文件
        try:
            os.unlink(temp_filename)
        except:
            pass
        
        print("播放完成")
        return True
    else:
        print("语音生成失败")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
        generate_and_play(text)
    else:
        # 测试文本
        test_text = "你好，我是中文女声，这是一个测试语音。"
        generate_and_play(test_text)
