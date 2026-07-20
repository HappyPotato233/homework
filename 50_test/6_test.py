'''
    【程序6】
    题目：输入两个正整数m和n，求其最大公约数和最小公倍数。
    1.程序分析：利用辗除法。
'''
# def gcd(m, n):
#     while n != 0:
#         m, n = n, m % n
#     return m

# def lcm(m, n):
#     return m * n // gcd(m, n)

def gcd():
    while n!=0:
        m, n = n, m % n
def lcm():
    return m * n // gcd(m ,n)

if __name__ == '__main__':
    m = int(input("请输入第一个正整数m: "))
    n = int(input("请输入第二个正整数n: "))
    print(f"最大公约数: {gcd(m, n)}")
    print(f"最小公倍数: {lcm(m, n)}")
