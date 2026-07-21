
'''
    【程序22】  
    题目：利用递归方法求5!。 
'''
def func(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * func(n - 1)



print(f"5! = {func(5)}")
