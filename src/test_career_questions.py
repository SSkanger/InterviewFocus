# 测试不同职业的问题获取
from question_manager import QuestionManager

# 初始化问题管理器
qm = QuestionManager()

# 测试1: 有专门问题的职业 - Python开发工程师
print("=== 测试1: Python开发工程师（有专门问题） ===")
python_questions = qm.get_questions_for_position("Python开发工程师")
print(f"问题数量: {len(python_questions)}")
print(f"第一个问题: {python_questions[0]['question']}")
print()

# 测试2: 没有专门问题但有大类的职业 - 后端开发工程师
print("=== 测试2: 后端开发工程师（无专门问题，有大类） ===")
backend_questions = qm.get_questions_for_position("后端开发工程师")
print(f"问题数量: {len(backend_questions)}")
print(f"第一个问题: {backend_questions[0]['question']}")
print()

# 测试3: 另一个没有专门问题的职业 - 产品运营
print("=== 测试3: 产品运营（无专门问题，有大类） ===")
product_ops_questions = qm.get_questions_for_position("产品运营")
print(f"问题数量: {len(product_ops_questions)}")
print(f"第一个问题: {product_ops_questions[0]['question']}")
print()

# 测试4: 医疗类职业 - 护士
print("=== 测试4: 护士（无专门问题，有大类） ===")
nurse_questions = qm.get_questions_for_position("护士")
print(f"问题数量: {len(nurse_questions)}")
print(f"第一个问题: {nurse_questions[0]['question']}")
print()

# 测试5: 教育类职业 - 小学教师
print("=== 测试5: 小学教师（无专门问题，有大类） ===")
primary_teacher_questions = qm.get_questions_for_position("小学教师")
print(f"问题数量: {len(primary_teacher_questions)}")
print(f"第一个问题: {primary_teacher_questions[0]['question']}")
print()

print("所有测试完成！")