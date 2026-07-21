'''
    【程序39】  
    题目：编写一个函数，输入n为偶数时，调用函数求1/2+1/4+...+1/n,当输入n为奇数时，调用函数1/1+1/3+...+1/n(利用指针函数)  
'''
# 偶数求和函数
def even_sum(n):
    s = 0.0
    i = 2
    while i <= n:
        s += 1 / i
        i += 2
    return s

# 奇数求和函数
def odd_sum(n):
    s = 0.0
    i = 1
    while i <= n:
        s += 1 / i
        i += 2
    return s

n = int(input("请输入整数n："))
if n % 2 == 0:
    res = even_sum(n)
else:
    res = odd_sum(n)
print(f"求和结果 = {res:.6f}")