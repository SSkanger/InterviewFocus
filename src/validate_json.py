import json

# 读取并验证JSON文件
try:
    with open('d:/PycharmProject/pywork/src/data/interview_questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('JSON文件格式正确，共包含', len(data['职业大类']), '个职业大类')
    
    # 检查每个职业大类的问题数量
    for category, questions in data['职业大类'].items():
        print(f'{category}: 共 {len(questions)} 个问题')
        
except json.JSONDecodeError as e:
    print(f'JSON文件格式错误: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'读取文件时发生错误: {e}')
    import traceback
    traceback.print_exc()