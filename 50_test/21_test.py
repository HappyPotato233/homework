'''
    【程序21】
    题目：求1+2!+3!+...+20!的和
    1.程序分析：此程序只是把累加变成了累乘。
'''
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def sum_factorials(n):
    total = 0
    for i in range(1, n + 1):
        total += factorial(i)
    return total

if __name__ == '__main__':
    print(f"1+2!+3!+...+20! = {sum_factorials(20)}")
