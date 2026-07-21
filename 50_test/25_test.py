'''
    【程序25】  
    题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同。 
'''
def func(n):
    s = str(n)
    return s == s[::-1]


num = int(input("请输入一个5位数: "))
if func(num):
    print(f"{num}是回文数")
else:
    print(f"{num}不是回文数")
