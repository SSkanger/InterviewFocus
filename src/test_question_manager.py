# test_question_manager.py - 测试问题管理器
from question_manager import QuestionManager

# 初始化问题管理器
qm = QuestionManager()

# 测试获取Python开发工程师的问题
print("测试 Python 开发工程师的问题:")
questions = qm.get_questions_for_position('Python开发工程师')
print('获取到 8 个问题:')
for i, q in enumerate(questions, 1):
    print(f' {i}. {q["question"]}')
    print(f'    类别: {q["category"]}')
    print(f'    难度: {q["difficulty"]}')

# 测试获取其他职业的问题
print("\n测试 DevOps工程师 的问题:")
questions = qm.get_questions_for_position('DevOps工程师')
print('获取到 8 个问题:')
for i, q in enumerate(questions, 1):
    print(f' {i}. {q["question"]}')
    print(f'    类别: {q["category"]}')
    print(f'    难度: {q["difficulty"]}')
