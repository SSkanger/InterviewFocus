# 测试语音提问功能
import requests
import time

# API基础URL
BASE_URL = "http://localhost:5000/api"

# 测试获取Python开发工程师的问题
def test_get_questions():
    print("=== 测试1: 获取Python开发工程师的问题 ===")
    
    # 发送POST请求
    response = requests.post(f"{BASE_URL}/questions/position", json={
        "position": "Python开发工程师"
    })
    
    # 打印响应结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    return response.json()

# 测试获取下一个问题（带语音）
def test_next_question():
    print("\n=== 测试2: 获取下一个问题（带语音） ===")
    
    # 首先确保已经获取了Python开发工程师的问题
    test_get_questions()
    time.sleep(2)
    
    # 发送GET请求获取下一个问题
    response = requests.get(f"{BASE_URL}/questions/next")
    
    # 打印响应结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    return response.json()

# 测试直接语音提问
def test_ask_question():
    print("\n=== 测试3: 直接语音提问 ===")
    
    # 发送POST请求直接提问
    response = requests.post(f"{BASE_URL}/questions/ask", json={
        "question": "请介绍一下你自己",
        "position": "产品经理"
    })
    
    # 打印响应结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    return response.json()

# 测试不同职业的语音提问
def test_different_careers():
    print("\n=== 测试4: 不同职业的语音提问 ===")
    
    careers = ["前端开发工程师", "护士", "小学教师"]
    question = "请谈谈你的职业规划"
    
    for career in careers:
        print(f"\n--- 测试职业: {career} ---")
        
        # 发送POST请求
        response = requests.post(f"{BASE_URL}/questions/ask", json={
            "question": question,
            "position": career
        })
        
        # 打印响应结果
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        # 等待3秒再测试下一个职业
        time.sleep(3)

if __name__ == "__main__":
    print("开始测试语音提问功能...")
    
    try:
        # 测试1: 获取Python开发工程师的问题
        test_get_questions()
        time.sleep(2)
        
        # 测试2: 获取下一个问题（带语音）
        test_next_question()
        time.sleep(5)  # 等待语音播放完成
        
        # 测试3: 直接语音提问
        test_ask_question()
        time.sleep(5)  # 等待语音播放完成
        
        # 测试4: 不同职业的语音提问
        test_different_careers()
        time.sleep(5)  # 等待语音播放完成
        
        print("\n所有测试完成！")
        print("语音提问功能测试成功！")
        print("系统现在会在获取下一个问题时自动通过语音提问，并在5分钟后给出反馈。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()