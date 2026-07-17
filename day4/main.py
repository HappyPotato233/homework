from subjects import BaseExam, ChineseExam, MathExam, EnglishExam
from grade_utils import *

def main():
    # 1. 基础得分率计算测试
    print("=" * 50)
    print("1. 基础得分率计算测试")
    print("=" * 50)
    score = 120
    max_score = 150
    percentage = calc_percentage(score, max_score)
    print(f"得分率: {score}/{max_score} = {percentage}")
    print()

    # 2. 成绩保存与读取测试
    print("=" * 50)
    print("2. 成绩保存与读取测试")
    print("=" * 50)
    save_record()
    records = read_all_records()
    print(f"已保存记录: {records}")
    print()

    # 3. 多线程录入测试
    print("=" * 50)
    print("3. 多线程录入测试")
    print("=" * 50)
    multi_thread_input_test()
    records = read_all_records()
    print(f"已保存记录: {records}")
    student_records.clear()
    print()

    # 4. 设置及格率为 0.65
    print("=" * 50)
    print("4. 设置及格率为 0.65")
    print("=" * 50)
    BaseExam.set_passing_rate(0.65)
    print(f"当前及格率: {BaseExam.passing_rate}")
    print()

    # 5. 语文测试
    print("=" * 50)
    print("5. 语文测试")
    print("=" * 50)
    chinese = ChineseExam("语文", 150, "张三", 50)
    chinese.input_score(135)
    print(f"成绩: {chinese.get_score()}")
    print(f"作文分: {chinese.essay_score}")
    print(f"等级: {chinese.get_grade(chinese.get_score())}")
    chinese.print_report_card()
    input_score_safe(chinese.student_name, chinese.subject_name, chinese.get_score())
    save_record()
    print()

    # 6. 数学测试
    print("=" * 50)
    print("6. 数学测试")
    print("=" * 50)
    math = MathExam("数学", 150, "李四")
    math.input_score(140)
    print(f"成绩: {math.get_score()}")
    math.set_bonus_points(5)
    print(f"附加分: {math.get_bonus_points()}")
    weighted = math.calc_weighted_score(0.7)
    print(f"加权分(0.7): {weighted}")
    print(f"等级: {math.get_grade(math.get_score())}")
    math.print_report_card()
    input_score_safe(math.student_name, math.subject_name, math.get_score())
    save_record()
    print()

    # 7. 英语测试
    print("=" * 50)
    print("7. 英语测试")
    print("=" * 50)
    english = EnglishExam("英语", 100, "王五")
    english.input_score(85)
    print(f"成绩: {english.get_score()}")
    english.print_report_card()
    print(f"等级: {english.get_grade(english.get_score())}")
    input_score_safe(english.student_name, english.subject_name, english.get_score())
    save_record()
    print()

    # 8. 优秀学生筛选测试
    print("=" * 50)
    print("8. 优秀学生筛选测试")
    print("=" * 50)
    # 测试用例
    score_dict = {"张三": 135, "李四": 120, "王五": 85, "赵六": 95}#
    threshold = 120
    excellent = get_excellent_students(score_dict, threshold)
    print(f"成绩字典: {score_dict}")
    print(f"优秀阈值: {threshold}")
    print(f"优秀学生: {excellent}")
    print()

    # 9. 成绩单生成器测试
    print("=" * 50)
    print("9. 成绩单生成器测试")
    print("=" * 50)
    students = ["张三", "李四", "王五"]
    generator = report_card_generator(students)
    for report in generator:
        print(report)
    print()

    # 10. 批量统计多态测试
    print("=" * 50)
    print("10. 批量统计多态测试")
    print("=" * 50)
    exams = [
        ChineseExam("语文", 150, "张三"),
        MathExam("数学", 150, "李四"),
        EnglishExam("英语", 100, "王五")
    ]
    exams[0].input_score(130)
    exams[1].input_score(145)
    exams[2].input_score(90)
    
    weight = 0.7
    print(f"使用权重: {weight}")
    for exam in exams:
        weighted_score = exam.calc_weighted_score(weight)
        print(f"{exam.subject_name} ({exam.student_name}): 原始分={exam.get_score()}, 加权分={weighted_score}")
    print()

if __name__ == "__main__":
    main()
