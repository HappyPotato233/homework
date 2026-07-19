'''
【程序9】  
题目：一个数如果恰好等于它的因子之和，这个数就称为 "完数 "。例如6=1＋2＋3.编程   找出1000以内的所有完数。
'''
def func()-> list:
    lst = []
    for i in range(1, 1001):
        s = 0
        for j in range(1, i //2 + 1):
            if i % j ==0:
                s += j
                if s == i:
                    lst.append(i)
    return lst

print(func())