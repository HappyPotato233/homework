'''
    【程序50】
    题目：有五个学生，每个学生有3门课的成绩，从键盘输入以上数据（包括学生号，姓名，三门课成绩），计算出平均成绩，况原有的数据和计算出的平均分数存放在磁盘文件 "stud "中。
'''
def save_student_data():
    students = []
    for i in range(5):
        student_id = input(f"请输入第{i+1}个学生的学号: ")
        name = input(f"请输入第{i+1}个学生的姓名: ")
        scores = list(map(float, input(f"请输入第{i+1}个学生的三门课成绩（用空格分隔）: ").split()))
        avg_score = sum(scores) / 3
        students.append({
            'id': student_id,
            'name': name,
            'scores': scores,
            'avg': avg_score
        })
    
    with open('stud', 'w', encoding='utf-8') as f:
        for student in students:
            f.write(f"学号: {student['id']}
")
            f.write(f"姓名: {student['name']}
")
            f.write(f"成绩: {student['scores'][0]}, {student['scores'][1]}, {student['scores'][2]}
")
            f.write(f"平均分: {student['avg']}
")
            f.write("=" * 30 + "
")
    
    print("数据已保存到stud文件中")

if __name__ == '__main__':
    save_student_data()
