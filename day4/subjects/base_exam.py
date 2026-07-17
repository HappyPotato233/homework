import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from grade_utils import calc_percentage

class BaseExam(ABC):
    """基础考试类"""
    # 类属性：及格率（60%）
    passing_rate = 0.6  # 及格率（60%）

    def __init__(self, subject_name: str, max_score: float, student_name: str):
        self.subject_name = subject_name
        self.max_score = max_score
        self.student_name = student_name
        self.__score = 0  # 私有成绩，默认0

    def get_score(self) -> float:
        """获取成绩"""
        return self.__score

    def input_score(self, score):
        """录入成绩"""
        self.__score = score
    
    @classmethod
    def set_passing_rate(cls, rate):
        """设置及格率"""
        cls.passing_rate = rate

    @staticmethod
    def check_student_name(name) -> bool:
        """检查学生姓名是否合法"""
        return name.strip() != ""

    @abstractmethod
    def get_grade(self, score) -> str:
        """获取成绩"""
        raise NotImplementedError("子类必须实现get_grade方法")

    def calc_weighted_score(self, weight) -> float:
        """计算加权成绩"""
        return self.__score * weight

    def print_report_card(self):
        """打印成绩报告"""
        print(f"{self.student_name}的成绩报告：")
        print(f"总成绩为:{self.get_grade(self.__score)}")
        print(f"加权成绩为：{self.calc_weighted_score(0.5):.2f}")
        print(f"得分率为：{calc_percentage(self.__score, self.max_score)}")
