from subjects.base_exam import BaseExam


class MathExam(BaseExam):
    """数学学科子类"""
    def __init__(self, subject_name: str, max_score: float, student_name: str):
        super().__init__(subject_name, max_score, student_name)
        self.__bonus_points = 0  # 私有属性：附加分
    
    def get_bonus_points(self):
        """获取附加分"""
        return self.__bonus_points
    
    def set_bonus_points(self, points):
        """设置附加分"""
        self.__bonus_points = points
    
    def get_grade(self, score) -> str:
        """数学等级评定：≥140优秀，≥120良好，≥90及格，<90不及格"""
        if score >= 140:
            return "优秀"
        elif score >= 120:
            return "良好"
        elif score >= 90:
            return "及格"
        else:
            return "不及格"
    
    def calc_weighted_score(self, weight) -> float:
        """数学加权分计算包含附加分"""
        base_score = super().calc_weighted_score(weight)
        return base_score + self.__bonus_points