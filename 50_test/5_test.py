'''
    【程序5】  
    题目：利用条件运算符的嵌套来完成此题：学习成绩>=90分的同学用A表示，60-89分之间的用B表示，60分以下的用C表示。  
    程序分析：(a>b)?a:b这是条件运算符的基本例子。 
'''
def get_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 60:
        return 'B'
    else:
        return 'C'


score = int(input("请输入成绩: "))
grade = get_grade(score)
print(f"成绩等级: {grade}")
