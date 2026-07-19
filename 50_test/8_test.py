'''
【程序8】  
题目：求s=a+aa+aaa+aaaa+aa...a的值，其中a是一个数字。例如2+22+222+2222+22222(此时共有5个数相加)，几个数相加由键盘控制。  
1.程序分析：关键是计算出每一项的值。 
'''

def func(a:SyntaxWarning,n:int)-> int:
    s = 0
    str = ''
    lst = []
    for i in range(n):
        str += a
        lst.append(int(str))
    for i in lst:
        s += int(i)
    return s

n = input("请输入一个相加数字的个数:")
a = int(input("请输入a的值:"))
print(func(a,int(n)))
