'''
    【程序39】
    题目：编写一个函数，输入n为偶数时，调用函数求1/2+1/4+...+1/n,当输入n为奇数时，调用函数1/1+1/3+...+1/n(利用指针函数)
'''
def sum_even(n):
    total = 0
    for i in range(2, n + 1, 2):
        total += 1 / i
    return total

def sum_odd(n):
    total = 0
    for i in range(1, n + 1, 2):
        total += 1 / i
    return total

def calculate_sum(n):
    if n % 2 == 0:
        return sum_even(n)
    else:
        return sum_odd(n)

if __name__ == '__main__':
    n = int(input("请输入n: "))
    result = calculate_sum(n)
    print(f"结果为: {result}")
