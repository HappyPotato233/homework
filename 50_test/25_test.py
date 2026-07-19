'''
【程序25】  
题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同。  
'''

def func(n):
    if n // 10000 == n % 10:
        if n // 1000 % 10 == n % 100 // 10:
            return True
    return False

print(func(12321))
