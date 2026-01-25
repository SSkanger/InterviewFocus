# 直接测试pyttsx3语音引擎
import pyttsx3
import time

print("开始测试pyttsx3语音引擎")

# 测试1: 简单语音输出
try:
    print("测试1: 简单语音输出")
    engine = pyttsx3.init()
    engine.say("这是一个直接的语音测试，不经过任何封装")
    engine.runAndWait()
    print("测试1成功：语音已播放")
    time.sleep(1)
except Exception as e:
    print(f"测试1失败：{e}")

# 测试2: 设置不同的语音属性
try:
    print("\n测试2: 设置不同的语音属性")
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)  # 语速
    engine.setProperty('volume', 0.8)  # 音量
    engine.say("这是一个设置了语速和音量的语音测试")
    engine.runAndWait()
    print("测试2成功：语音已播放")
    time.sleep(1)
except Exception as e:
    print(f"测试2失败：{e}")

# 测试3: 连续播放两条语音
try:
    print("\n测试3: 连续播放两条语音")
    engine = pyttsx3.init()
    engine.say("这是第一条连续语音")
    engine.say("这是第二条连续语音")
    engine.runAndWait()
    print("测试3成功：两条语音已连续播放")
except Exception as e:
    print(f"测试3失败：{e}")

# 测试4: 获取可用的语音引擎
try:
    print("\n测试4: 获取可用的语音引擎")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"可用语音数量：{len(voices)}")
    for i, voice in enumerate(voices):
        print(f"语音 {i+1}: ID={voice.id}, Name={voice.name}, Languages={voice.languages}")
        # 测试使用不同的语音
        engine.setProperty('voice', voice.id)
        engine.say(f"这是使用{voice.name}的语音测试")
        engine.runAndWait()
        time.sleep(1)
except Exception as e:
    print(f"测试4失败：{e}")

# 测试5: 测试runAndWait的工作原理
try:
    print("\n测试5: 测试runAndWait的工作原理")
    engine = pyttsx3.init()
    print("准备播放第一条语音")
    engine.say("第一条语音")
    engine.runAndWait()
    print("第一条语音播放完成")
    
    print("准备播放第二条语音")
    engine.say("第二条语音")
    engine.runAndWait()
    print("第二条语音播放完成")
except Exception as e:
    print(f"测试5失败：{e}")

print("\n所有测试完成！")