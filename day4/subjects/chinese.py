from subjects.base_exam import BaseExam
class ChineseExam(BaseExam):
    """语文学科子类"""
    def __init__(self, subject_name: str, max_score: float, student_name: str, essay_score: float = 0):
        super().__init__(subject_name, max_score, student_name)
        self.essay_score = essay_score

    def get_grade(self, score) -> str:
        if score >= 135:
            return "优秀"
        elif score >= 120:
            return "良好"
        elif score >= 90:
            return "及格"
        else:
            return "不及格"
