'''
    【程序5】
    题目：利用条件运算符的嵌套来完成此题：学习成绩> =90分的同学用A表示，60-89分之间的用B表示，60分以下的用C表示。
    1.程序分析：(a> b)?a:b这是条件运算符的基本例子。
'''
def score_level(score):
    return 'A' if score >= 90 else ('B' if score >= 60 else 'C')

if __name__ == '__main__':
    score = int(input("请输入学习成绩: "))
    print(f"成绩等级为: {score_level(score)}")
