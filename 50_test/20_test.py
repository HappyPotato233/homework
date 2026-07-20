'''
    【程序20】
    题目：有一分数序列：2/1，3/2，5/3，8/5，13/8，21/13...求出这个数列的前20项之和。
    1.程序分析：请抓住分子与分母的变化规律。
'''
def sum_fraction_series(n):
    numerator = 2
    denominator = 1
    total = 0
    for i in range(n):
        total += numerator / denominator
        numerator, denominator = numerator + denominator, numerator
    return total

if __name__ == '__main__':
    result = sum_fraction_series(20)
    print(f"数列的前20项之和: {result}")
