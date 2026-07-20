'''
    【程序9】
    题目：一个数如果恰好等于它的因子之和，这个数就称为 "完数 "。例如6=1＋2＋3.编程   找出1000以内的所有完数。
'''
def is_perfect(n):
    if n <= 1:
        return False
    total = 1
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
    return total == n

if __name__ == '__main__':
    import math
    perfect_numbers = []
    for num in range(2, 1001):
        if is_perfect(num):
            perfect_numbers.append(num)
    print("1000以内的完数:", perfect_numbers)
