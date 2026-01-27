import requests
import json

# 测试获取Python开发工程师的问题
url = 'http://localhost:5000/api/questions/position'
headers = {'Content-Type': 'application/json'}
data = {'position': 'Python开发工程师'}

response = requests.post(url, headers=headers, data=json.dumps(data))
print('Status Code:', response.status_code)
print('Response:', response.text)

# 解析响应
if response.status_code == 200:
    try:
        result = response.json()
        if result['success']:
            questions = result['data']['questions']
            print(f'\n获取到 {len(questions)} 个问题:')
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q['question']}")
                print(f"   类别: {q['category']}")
                print(f"   难度: {q['difficulty']}")
        else:
            print('Error:', result['message'])
    except Exception as e:
        print('解析响应失败:', e)
