'''
【程序34】  
题目：输入3个数a,b,c，按大小顺序输出。  
1.程序分析：利用指针方法。  
'''

def func():
    a = int(input("请输入a："))
    b = int(input("请输入b："))
    c = int(input("请输入c："))
    # 保证 a >= b
    if a < b:
        temp = a
        a = b
        b = temp
    # 保证 a >= c
    if a < c:
        temp = a
        a = c
        c = temp
    # 保证 b >= c
    if b < c:
        temp = b
        b = c
        c = temp
    print(f"从大到小：{a} {b} {c}")

func()
