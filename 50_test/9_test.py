'''
    【程序9】  
    题目：一个数如果恰好等于它的因子之和，这个数就称为“完数”。例如6=1＋2＋3.编程找出1000以内的所有完数。 
'''
import math
def func():
    result = []
    for i in range (2, 1000):
        factor = []
        for j in range(1, math.sqrt(i) + 1):
            if i % j == 0:
                factor.append(j)
        if i == sum(factor):
            result.append(i)
    return result


perfect_numbers = func() 
print("1000以内的完数:", perfect_numbers)
