'''
【程序6】  
题目：输入两个正整数m和n，求其最大公约数和最小公倍数。  
1.程序分析：利用辗除法。  
'''
# 递归版
def func1(a, b):
    if b == 0:
        return a
    return func1(b, a%b)

a, b = 12, 16
# 循环版
def func2(a, b):
    while b !=0 :
        a, b = b, a%b
    return a

print(f"{a}和{b}的最大公约数:{func1(a, b)}")
print(f"{a}和{b}的最小公倍数:{a*b//func1(a, b)}")

print(f"{a}和{b}的最大公约数:{func2(a, b)}")
print(f"{a}和{b}的最小公倍数:{a*b//func2(a, b)}")