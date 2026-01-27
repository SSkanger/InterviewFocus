#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

# 获取cosyvoice自带的Python可执行文件路径
cosyvoice_python = os.path.join(os.path.dirname(__file__), '..', 'cosyvoice-rainfall', 'python', 'python.exe')
# 获取生成语音的脚本路径
generate_script = os.path.join(os.path.dirname(__file__), 'cosyvoice_generate_simple.py')

# 测试文本
test_text = "你好，我是中文女声，这是一个测试语音。"

print(f"使用cosyvoice自带的Python环境: {cosyvoice_python}")
print(f"测试文本: {test_text}")

# 构建命令
command = [cosyvoice_python, generate_script, test_text]

print(f"执行命令: {' '.join(command)}")

# 执行命令
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')

print(f"返回码: {result.returncode}")
print(f"标准输出: {result.stdout}")
print(f"标准错误: {result.stderr}")

if result.returncode == 0:
    print("测试成功!")
else:
    print("测试失败!")
