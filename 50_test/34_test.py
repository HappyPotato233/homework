﻿'''
【程序34】  
题目：输入3个数a,b,c，按大小顺序输出。  
1.程序分析：利用指针方法。 
'''
def func(a, b, c):
    if a < b and a < c:
        print(a, b, c)
    elif b < a and b < c:
        print(b, a, c)
    else:
        print(c, a, b)



func(1, 2, 3)
