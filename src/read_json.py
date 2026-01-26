import json

# 读取完整的JSON文件
with open('d:/PycharmProject/pywork/src/data/interview_questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 将数据重新转换为JSON字符串，确保完整输出
print(json.dumps(data, ensure_ascii=False, indent=2))