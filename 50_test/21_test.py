'''
    【程序21】  
    题目：求1+2!+3!+...+20!的和 
'''

def func(n):
    sum = 0
    for i in range(1,n+1):
        total = 1
        while i != 0:
            total *= i
            i -= 1 
        sum += total
    return sum


result = func(20)
print(f"1+2!+3!+...+20! = {result}")
