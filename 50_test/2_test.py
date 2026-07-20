'''
    【程序2】
    题目：判断101-200之间有多少个素数，并输出所有素数。
    1.程序分析：判断素数的方法：用一个数分别去除2到sqrt(这个数)，如果能被整除，
    则表明此数不是素数，反之是素数。
'''
import math

def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

if __name__ == '__main__':
    primes = []
    for num in range(101, 201):
        if is_prime(num):
            primes.append(num)
    print(f"101-200之间共有 {len(primes)} 个素数")
    print("素数列表:", primes)
