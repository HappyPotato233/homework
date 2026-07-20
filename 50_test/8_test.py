'''
    【程序8】
    题目：求s=a+aa+aaa+aaaa+aa...a的值，其中a是一个数字。例如2+22+222+2222+22222(此时共有5个数相加)，几个数相加有键盘控制。
    1.程序分析：关键是计算出每一项的值。
'''
def sum_series(a, n):
    total = 0
    term = 0
    for i in range(n):
        term = term * 10 + a
        total += term
    return total

if __name__ == '__main__':
    a = int(input("请输入数字a: "))
    n = int(input("请输入相加的个数n: "))
    result = sum_series(a, n)
    print(f"s = {result}")
