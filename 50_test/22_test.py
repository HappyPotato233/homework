'''
【程序22】  
题目：利用递归方法求5!。  
1.程序分析：递归公式：fn=fn_1*4!  
'''

def fn(n):
    if n == 1:
        return 1
    return fn(n-1) * n
print(fn(5))
