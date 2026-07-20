'''
    【程序24】
    题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数字。
'''
def analyze_number(n):
    s = str(n)
    digits = len(s)
    reversed_s = s[::-1]
    return digits, reversed_s

if __name__ == '__main__':
    n = int(input("请输入一个不多于5位的正整数: "))
    digits, reversed_s = analyze_number(n)
    print(f"这是一个 {digits} 位数")
    print(f"逆序打印: {reversed_s}")
