# src/question_manager.py - 面试问题管理器
import json
import os
import random
from typing import List, Dict, Optional


class QuestionManager:
    """面试问题管理器 - 用于加载和管理面试问题"""
    
    # 职业到大类的映射，基于InterviewSimulation.tsx中的careerCategories数据
    CAREER_TO_CATEGORY = {
        # 计算机/互联网类
        "Python开发工程师": "计算机/互联网类",
        "Java开发工程师": "计算机/互联网类",
        "前端开发工程师": "计算机/互联网类",
        "后端开发工程师": "计算机/互联网类",
        "全栈开发工程师": "计算机/互联网类",
        "数据分析师": "计算机/互联网类",
        "机器学习工程师": "计算机/互联网类",
        "算法工程师": "计算机/互联网类",
        "测试工程师": "计算机/互联网类",
        "DevOps工程师": "计算机/互联网类",
        "网络工程师": "计算机/互联网类",
        "系统运维工程师": "计算机/互联网类",
        "数据库管理员": "计算机/互联网类",
        "区块链工程师": "计算机/互联网类",
        "游戏开发工程师": "计算机/互联网类",
        "大数据工程师": "计算机/互联网类",
        "云计算工程师": "计算机/互联网类",
        "信息安全工程师": "计算机/互联网类",
        "嵌入式开发工程师": "计算机/互联网类",
        
        # 产品/设计/运营类
        "产品经理": "产品/设计/运营类",
        "运营专员": "产品/设计/运营类",
        "市场专员": "产品/设计/运营类",
        "用户研究员": "产品/设计/运营类",
        "UI设计师": "产品/设计/运营类",
        "UX设计师": "产品/设计/运营类",
        "视觉设计师": "产品/设计/运营类",
        "交互设计师": "产品/设计/运营类",
        "产品运营": "产品/设计/运营类",
        "内容运营": "产品/设计/运营类",
        "用户运营": "产品/设计/运营类",
        "社群运营": "产品/设计/运营类",
        "活动运营": "产品/设计/运营类",
        "数据运营": "产品/设计/运营类",
        "新媒体运营": "产品/设计/运营类",
        "SEO专员": "产品/设计/运营类",
        "SEM专员": "产品/设计/运营类",
        "品牌专员": "产品/设计/运营类",
        "广告策划": "产品/设计/运营类",
        
        # 金融/经济类
        "金融分析师": "金融/经济类",
        "投资顾问": "金融/经济类",
        "银行柜员": "金融/经济类",
        "保险经纪人": "金融/经济类",
        "财务会计": "金融/经济类",
        "审计师": "金融/经济类",
        "税务师": "金融/经济类",
        "资产评估师": "金融/经济类",
        "证券分析师": "金融/经济类",
        "基金经理": "金融/经济类",
        "风险管理师": "金融/经济类",
        "理财顾问": "金融/经济类",
        "信贷专员": "金融/经济类",
        "外汇交易员": "金融/经济类",
        "期货交易员": "金融/经济类",
        "保险精算师": "金融/经济类",
        "投资银行分析师": "金融/经济类",
        "经济研究员": "金融/经济类",
        "财务经理": "金融/经济类",
        "会计主管": "金融/经济类",
        
        # 销售/市场/公关类
        "销售代表": "销售/市场/公关类",
        "销售经理": "销售/市场/公关类",
        "客户经理": "销售/市场/公关类",
        "区域销售经理": "销售/市场/公关类",
        "渠道销售": "销售/市场/公关类",
        "电话销售": "销售/市场/公关类",
        "网络销售": "销售/市场/公关类",
        "市场经理": "销售/市场/公关类",
        "市场策划": "销售/市场/公关类",
        "市场调研": "销售/市场/公关类",
        "品牌经理": "销售/市场/公关类",
        "公关专员": "销售/市场/公关类",
        "公关经理": "销售/市场/公关类",
        "媒介专员": "销售/市场/公关类",
        "广告客户经理": "销售/市场/公关类",
        "商务拓展": "销售/市场/公关类",
        "客户成功经理": "销售/市场/公关类",
        "销售总监": "销售/市场/公关类",
        "市场总监": "销售/市场/公关类",
        "公关总监": "销售/市场/公关类",
        
        # 教育/培训类
        "小学教师": "教育/培训类",
        "中学教师": "教育/培训类",
        "高中教师": "教育/培训类",
        "大学教师": "教育/培训类",
        "培训机构讲师": "教育/培训类",
        "教育咨询师": "教育/培训类",
        "课程设计师": "教育/培训类",
        "教育行政人员": "教育/培训类",
        "班主任": "教育/培训类",
        "辅导教师": "教育/培训类",
        "留学顾问": "教育/培训类",
        "语言培训师": "教育/培训类",
        "职业培训师": "教育/培训类",
        "教育产品经理": "教育/培训类",
        "教育技术专员": "教育/培训类",
        "早教教师": "教育/培训类",
        "特殊教育教师": "教育/培训类",
        "在线教育讲师": "教育/培训类",
        "教育研究员": "教育/培训类",
        "教务管理": "教育/培训类",
        
        # 医疗/健康类
        "医生": "医疗/健康类",
        "护士": "医疗/健康类",
        "药剂师": "医疗/健康类",
        "营养师": "医疗/健康类",
        "心理咨询师": "医疗/健康类",
        "康复治疗师": "医疗/健康类",
        "医学检验师": "医疗/健康类",
        "影像科医师": "医疗/健康类",
        "麻醉科医师": "医疗/健康类",
        "外科医生": "医疗/健康类",
        "内科医生": "医疗/健康类",
        "儿科医生": "医疗/健康类",
        "妇产科医生": "医疗/健康类",
        "皮肤科医生": "医疗/健康类",
        "眼科医生": "医疗/健康类",
        "耳鼻喉科医生": "医疗/健康类",
        "口腔科医生": "医疗/健康类",
        "精神科医生": "医疗/健康类",
        "健康管理师": "医疗/健康类",
        "医疗器械销售": "医疗/健康类",
        
        # 法律/法务类
        "律师": "法律/法务类",
        "法务专员": "法律/法务类",
        "法律顾问": "法律/法务类",
        "法官": "法律/法务类",
        "检察官": "法律/法务类",
        "律师助理": "法律/法务类",
        "知识产权律师": "法律/法务类",
        "公司法务": "法律/法务类",
        "刑事律师": "法律/法务类",
        "民事律师": "法律/法务类",
        "行政律师": "法律/法务类",
        "婚姻家庭律师": "法律/法务类",
        "房产律师": "法律/法务类",
        "合同律师": "法律/法务类",
        "劳动法律师": "法律/法务类",
        "税务律师": "法律/法务类",
        "国际律师": "法律/法务类",
        "律师事务所合伙人": "法律/法务类",
        "法律研究员": "法律/法务类",
        "法律翻译": "法律/法务类",
        
        # 行政/人事/财务类
        "行政专员": "行政/人事/财务类",
        "行政经理": "行政/人事/财务类",
        "人事专员": "行政/人事/财务类",
        "人事经理": "行政/人事/财务类",
        "招聘专员": "行政/人事/财务类",
        "培训专员": "行政/人事/财务类",
        "薪酬福利专员": "行政/人事/财务类",
        "绩效考核专员": "行政/人事/财务类",
        "HRBP": "行政/人事/财务类",
        "人力资源总监": "行政/人事/财务类",
        "行政总监": "行政/人事/财务类",
        "办公室主任": "行政/人事/财务类",
        "秘书": "行政/人事/财务类",
        "助理": "行政/人事/财务类",
        "前台接待": "行政/人事/财务类",
        "财务助理": "行政/人事/财务类",
        "出纳": "行政/人事/财务类",
        "财务主管": "行政/人事/财务类",
        "财务总监": "行政/人事/财务类",
        "审计主管": "行政/人事/财务类",
        
        # 工程/制造类
        "机械工程师": "工程/制造类",
        "电气工程师": "工程/制造类",
        "电子工程师": "工程/制造类",
        "自动化工程师": "工程/制造类",
        "土木工程师": "工程/制造类",
        "建筑工程师": "工程/制造类",
        "结构工程师": "工程/制造类",
        "给排水工程师": "工程/制造类",
        "暖通工程师": "工程/制造类",
        "环境工程师": "工程/制造类",
        "化工工程师": "工程/制造类",
        "材料工程师": "工程/制造类",
        "质量工程师": "工程/制造类",
        "工艺工程师": "工程/制造类",
        "生产工程师": "工程/制造类",
        "设备工程师": "工程/制造类",
        "研发工程师": "工程/制造类",
        "工程监理": "工程/制造类",
        "项目经理": "工程/制造类",
        "工厂经理": "工程/制造类",
        
        # 服务/零售类
        "服务员": "服务/零售类",
        "收银员": "服务/零售类",
        "导购员": "服务/零售类",
        "店长": "服务/零售类",
        "店员": "服务/零售类",
        "客服专员": "服务/零售类",
        "客服经理": "服务/零售类",
        "酒店前台": "服务/零售类",
        "酒店经理": "服务/零售类",
        "厨师": "服务/零售类",
        "餐厅经理": "服务/零售类",
        "咖啡师": "服务/零售类",
        "调酒师": "服务/零售类",
        "美容师": "服务/零售类",
        "美发师": "服务/零售类",
        "美甲师": "服务/零售类",
        "健身教练": "服务/零售类",
        "瑜伽教练": "服务/零售类",
        "保洁员": "服务/零售类",
        "保安": "服务/零售类"
    }
    
    def __init__(self, question_file: str = "data/interview_questions.json"):
        """初始化问题管理器
        
        Args:
            question_file: 问题文件路径
        """
        self.question_file = question_file
        self.questions = self._load_questions()
        self.current_question_index = 0
        self.current_questions: List[Dict] = []
        
        print(f"✅ 面试问题管理器已初始化，加载了 {len(self.questions)} 个职业的问题")
    
    def _load_questions(self) -> Dict[str, List[Dict]]:
        """加载面试问题
        
        Returns:
            Dict[str, List[Dict]]: 职业到问题列表的映射
        """
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建完整的文件路径
            full_path = os.path.join(current_dir, self.question_file)
            
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 构建职业到问题列表的映射
            questions_map = {}
            
            # 添加通用问题
            general_questions = data.get("通用问题", [])
            if general_questions:
                questions_map["通用问题"] = general_questions
            
            # 处理职业大类
            career_categories = data.get("职业大类", {})
            for category_name, category_questions in career_categories.items():
                questions_map[category_name] = category_questions
            
            # 处理具体职业
            specific_careers = data.get("具体职业", {})
            for career_name, career_questions in specific_careers.items():
                questions_map[career_name] = career_questions
            
            print(f"✅ 成功加载面试问题，共 {len(questions_map)} 个职业/大类")
            return questions_map
        except FileNotFoundError:
            print(f"❌ 问题文件未找到: {self.question_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 问题文件解析错误: {e}")
            return {}
    
    def get_questions_for_position(self, position: str) -> List[Dict]:
        """获取指定职业的面试问题
        
        Args:
            position: 职业名称
            
        Returns:
            List[Dict]: 该职业的面试问题列表，如果没有则返回通用问题
        """
        # 默认通用问题列表
        default_general_questions = [
            {"question": "请简单介绍一下您自己。", "category": "通用问题", "difficulty": "简单", "answer_key": "包含个人基本信息、教育背景、工作经验、技能特长等"},
            {"question": "您以前有什么相关工作经验？", "category": "通用问题", "difficulty": "简单", "answer_key": "详细描述与岗位相关的工作经验，包括具体职责、成果等"},
            {"question": "您为什么对这个职位感兴趣？", "category": "通用问题", "difficulty": "中等", "answer_key": "结合个人职业规划和公司特点进行回答"},
            {"question": "您认为自己最大的优势是什么？", "category": "通用问题", "difficulty": "中等", "answer_key": "突出与岗位相关的技能和特质"},
            {"question": "您如何看待团队合作？", "category": "通用问题", "difficulty": "中等", "answer_key": "强调团队合作的重要性，分享自己的团队合作经验"},
            {"question": "您对未来的职业规划是什么？", "category": "通用问题", "difficulty": "中等", "answer_key": "结合职位和公司特点，描述短期和长期职业目标"}
        ]
        
        # 获取通用问题，如果不存在或为空则使用默认通用问题
        general_questions = default_general_questions
        # 只有当通用问题存在且不为空时，才使用文件中的通用问题
        if "通用问题" in self.questions and self.questions["通用问题"]:
            general_questions = self.questions["通用问题"]
        
        # 确保通用问题列表不为空
        if not general_questions:
            general_questions = default_general_questions
        
        # 1. 首先检查是否有该职业的专门问题
        if position in self.questions:
            # 获取职业问题
            career_questions = self.questions[position]
        else:
            # 2. 如果没有专门问题，使用预定义的职业到大类映射
            career_questions = []
            if position in self.CAREER_TO_CATEGORY:
                # 获取该职业对应的大类
                category_name = self.CAREER_TO_CATEGORY[position]
                # 获取该大类的问题
                career_questions = self.questions.get(category_name, [])
        
        # 3. 构建最终问题列表：前两个是默认通用问题，然后是职业/大类问题
        total_needed = 8
        final_questions = []
        
        # 确保前2个是默认通用问题（专业性质不强的大类问题）
        final_questions.extend(default_general_questions[:2])
        
        # 合并剩余的默认通用问题和职业问题
        remaining_questions = default_general_questions[2:] + career_questions
        
        # 随机打乱剩余问题的顺序
        if remaining_questions:
            random.shuffle(remaining_questions)
            # 添加需要的数量，确保总问题数为8个
            final_questions.extend(remaining_questions[:6])  # 6个问题 + 前2个通用问题 = 8个问题
        
        # 如果问题不够，重复填充
        while len(final_questions) < total_needed:
            final_questions.append(final_questions[len(final_questions) % len(final_questions)])
        
        # 确保只返回8个问题
        fixed_questions = final_questions[:total_needed]
        
        print(f"✅ 为{position}生成面试问题，共{len(fixed_questions)}个，前2个为通用问题")
        self.current_questions = fixed_questions
        self.current_question_index = 0
        return fixed_questions
    
    def get_next_question(self) -> Optional[Dict]:
        """获取下一个面试问题
        
        Returns:
            Optional[Dict]: 下一个面试问题，如果没有则返回None
        """
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            self.current_question_index += 1
            return question
        else:
            return None
    
    def get_current_question(self) -> Optional[Dict]:
        """获取当前面试问题
        
        Returns:
            Optional[Dict]: 当前面试问题，如果没有则返回None
        """
        if self.current_question_index > 0 and self.current_question_index <= len(self.current_questions):
            return self.current_questions[self.current_question_index - 1]
        else:
            return None
    
    def reset_questions(self) -> None:
        """重置问题索引"""
        self.current_question_index = 0
    
    def has_more_questions(self) -> bool:
        """是否还有更多问题
        
        Returns:
            bool: 是否还有更多问题
        """
        return self.current_question_index < len(self.current_questions)
    
    def get_question_count(self) -> int:
        """获取当前职业的问题总数
        
        Returns:
            int: 问题总数
        """
        return len(self.current_questions)
    
    def get_remaining_question_count(self) -> int:
        """获取剩余问题数量
        
        Returns:
            int: 剩余问题数量
        """
        return len(self.current_questions) - self.current_question_index


# 测试代码
if __name__ == "__main__":
    # 初始化问题管理器
    qm = QuestionManager()
    
    # 测试获取Python开发工程师的问题
    python_questions = qm.get_questions_for_position("Python开发工程师")
    print(f"Python开发工程师问题数量: {len(python_questions)}")
    
    # 测试获取下一个问题
    print("\n获取下一个问题:")
    question = qm.get_next_question()
    if question:
        print(f"问题: {question['question']}")
        print(f"类别: {question['category']}")
        print(f"难度: {question['difficulty']}")
        print(f"参考答案要点: {question['answer_key']}")
    
    # 测试获取下一个问题
    print("\n获取下一个问题:")
    question = qm.get_next_question()
    if question:
        print(f"问题: {question['question']}")
        print(f"类别: {question['category']}")
    
    # 测试获取当前问题
    print("\n获取当前问题:")
    current_question = qm.get_current_question()
    if current_question:
        print(f"当前问题: {current_question['question']}")
    
    # 测试是否还有更多问题
    print(f"\n是否还有更多问题: {qm.has_more_questions()}")
    print(f"剩余问题数量: {qm.get_remaining_question_count()}")
    print(f"问题总数: {qm.get_question_count()}")
