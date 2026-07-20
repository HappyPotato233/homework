'''
    【程序13】
    题目：一个整数，它加上100后是一个完全平方数，再加上168又是一个完全平方数，请问该数是多少？
    1.程序分析：在10万以内判断，先将该数加上100后再开方，再将该数加上268后再开方，如果开方后的结果满足如下条件，即是结果。请看具体分析：
'''
import math

def find_number():
    result = []
    for n in range(1, 100000):
        x = int(math.sqrt(n + 100))
        y = int(math.sqrt(n + 268))
        if x * x == n + 100 and y * y == n + 268:
            result.append(n)
    return result

if __name__ == '__main__':
    numbers = find_number()
    print("满足条件的数:", numbers)
