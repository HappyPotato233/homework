'''
    【程序8】  
    题目：求s=a+aa+aaa+aaaa+aa...a的值，其中a是一个数字。例如2+22+222+2222+22222(此时共有5个数相加)，几个数相加有键盘控制。 
    1.程序分析：关键是计算出每一项的值。 
'''
def func(a, n):
    total = 0
    current = 0
    for _ in range(n):
        current = current * 10 + a
        total += current
    return total


a = int(input("请输入数字a: "))
n = int(input("请输入相加的项数n: "))
result = func(a, n)
print(f"结果: {result}")
