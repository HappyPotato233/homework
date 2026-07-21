'''
    【程序13】  
    题目：一个整数，它加上100后是一个完全平方数，再加上168又是一个完全平方数，请问该数是多少？ 
    1.程序分析：在10万以内判断，先将该数加上100后再开方，再将该数加上268后再开方，如果开方后的结果满足如下条件，即是结果。 
'''
import math

def func():
    results = []
    for i in range(100000):
        x = int(math.sqrt(i + 100))
        y = int(math.sqrt(i + 268))
        if x * x == i + 100 and y * y == i + 268:
            results.append(i)
    return results


numbers = func()
print("满足条件的数:", numbers)
