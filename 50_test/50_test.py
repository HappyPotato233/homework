'''
【程序50】  
题目：有五个学生，每个学生有3门课的成绩，从键盘输入以上数据（包括学生号，姓名，三门课成绩），计算出平均成绩，况原有的数据和计算出的平均分数存放在磁盘文件 "stud "中。  
'''

def input_students():
    students = []
    for i in range(5):
        print(f"\n请输入第{i+1}个学生的信息:")
        student_id = input("学生号: ")
        name = input("姓名: ")
        score1 = float(input("成绩1: "))
        score2 = float(input("成绩2: "))
        score3 = float(input("成绩3: "))
        average = (score1 + score2 + score3) / 3
        students.append({
            'id': student_id,
            'name': name,
            'scores': [score1, score2, score3],
            'average': average
        })
    return students

def save_students(students, filename="stud"):
    with open(filename, 'w', encoding='utf-8') as f:
        for s in students:
            f.write(f"学号: {s['id']}\n")
            f.write(f"姓名: {s['name']}\n")
            f.write(f"成绩1: {s['scores'][0]}\n")
            f.write(f"成绩2: {s['scores'][1]}\n")
            f.write(f"成绩3: {s['scores'][2]}\n")
            f.write(f"平均分: {s['average']:.2f}\n")
            f.write("-" * 30 + "\n")
    print(f"数据已保存到文件: {filename}")

def load_students(filename="stud"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            print("文件内容:")
            print(content)
            return content
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
        return None

if __name__ == '__main__':
    test_students = [
        {'id': '001', 'name': '张三', 'scores': [85, 90, 95], 'average': (85+90+95)/3},
        {'id': '002', 'name': '李四', 'scores': [78, 82, 88], 'average': (78+82+88)/3},
        {'id': '003', 'name': '王五', 'scores': [92, 88, 90], 'average': (92+88+90)/3},
        {'id': '004', 'name': '赵六', 'scores': [70, 75, 80], 'average': (70+75+80)/3},
        {'id': '005', 'name': '钱七', 'scores': [88, 92, 96], 'average': (88+92+96)/3},
    ]
    save_students(test_students)
    load_students()
