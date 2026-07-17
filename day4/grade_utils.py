'''
    工具函数
'''
import threading
lock = threading.Lock()
# 全局字典(测试用例)
student_records = {}

def check_valid_grade(grade: float, max_score: float) -> bool:
    """检查成绩是否合法"""
    return 0 <= grade <= max_score

def calc_percentage(score: float, max_score: float) -> str:
    """计算得分率"""
    return f"{(score / max_score*100):.2f}%"    

def save_record():
    """保存成绩记录到文件"""
    with open("exam_records.txt","a",encoding='utf-8') as f:
        f.write(str(student_records))
        f.write("\n")

def read_all_records():
    """读取所有成绩记录"""
    with open("exam_records.txt","r",encoding='utf-8') as f:
        return f.readlines()

def get_excellent_students(score_dict, threshold):
    """获取优秀学生"""
    return [student for student, score in score_dict.items() if score >= threshold]

def report_card_generator(student_list):
    """生成成绩报告"""
    for student in student_list:
        yield f"{student}的成绩报告："
        for subject in student_records[student]:
            yield f"{subject}: {student_records[student][subject]}"

def input_score_safe(student_name, subject, score):
    """线程锁安全录入成绩"""
    with lock:
        if student_name not in student_records:
            student_records[student_name] = {}
        student_records[student_name][subject] = score
        save_record()
# 测试代码
def multi_thread_input_test():
    """多线程录入成绩测试"""
    student_record = [
        ("张三", "语文", 90),
        ("张三", "数学", 90),
        ("李四", "语文", 80),
        ("李四", "数学", 80),
    ]
    # 创建线程列表
    threads = []
    for record in student_record:
        student_name ,subject, score = record
        t = threading.Thread(target=input_score_safe, args=(student_name, subject, score))
        threads.append(t)
    # 启动所有线程
        t.start()
    # 等待所有线程完成
    for t in threads:
        t.join()
    


if __name__ == '__main__':
# 各科目满分
    subject_max_scores = {"语文": 150, "数学": 150, "英语": 100}
    multi_thread_input_test()