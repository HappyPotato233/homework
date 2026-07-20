'''
    【程序3】
    题目：打印出所有的 "水仙花数 "，所谓 "水仙花数 "是指一个三位数，其各位数字立方和等于该数本身。例如：153是一个 "水仙花数 "，因为153=1的三次方＋5的三次方＋3的三次方。
    1.程序分析：利用for循环控制100-999个数，每个数分解出个位，十位，百位。
'''
def is_narcissistic(n):
    hundreds = n // 100
    tens = (n // 10) % 10
    units = n % 10
    return hundreds**3 + tens**3 + units**3 == n

if __name__ == '__main__':
    narcissistic_numbers = []
    for num in range(100, 1000):
        if is_narcissistic(num):
            narcissistic_numbers.append(num)
    print("水仙花数:", narcissistic_numbers)
