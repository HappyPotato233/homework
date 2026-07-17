from subjects.base_exam import BaseExam


class EnglishExam(BaseExam):
    """英语学科子类"""
    def __init__(self, subject_name: str, max_score: float, student_name: str):
        super().__init__(subject_name, max_score, student_name)

    def get_grade(self, score) -> str:
        """英语等级评定：≥90优秀，≥75良好，≥60及格，<60不及格"""
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "及格"
        else:
            return "不及格"

    def print_report_card(self):
        """打印英语成绩单（含分项成绩标语）"""
        print("听力/阅读/写作分项成绩")
        super().print_report_card()
