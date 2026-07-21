'''
    【程序20】  
    题目：有一分数序列：2/1，3/2，5/3，8/5，13/8，21/13...求出这个数列的前20项之和。 
'''
def func(n):
    total = 0
    a, b = 2, 1
    for _ in range(n):
        total += a / b
        a, b = a + b, a
    return total



result = func(20)
print(f"前20项之和: {result}")
