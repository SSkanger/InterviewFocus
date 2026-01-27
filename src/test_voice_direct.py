#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试直接导入CosyVoice模型的语音生成功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入voice_utils模块
import voice_utils

# 创建VoiceFeedback实例
print("初始化语音反馈系统...")
voice = voice_utils.VoiceFeedback()

# 测试语音功能
print("\n测试语音生成...")
test_text = "你好，我是中文女声，这是一个测试语音。"
result = voice.speak(test_text)

print(f"\n测试结果: {'成功' if result else '失败'}")

# 测试面试问题功能
print("\n测试面试问题功能...")
question = "请介绍一下你自己"
position = "Python开发工程师"
result = voice.ask_question(question, position)

print(f"\n测试结果: {'成功' if result else '失败'}")

print("\n测试完成！")
