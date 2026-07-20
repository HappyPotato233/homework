'''
    【程序27】
    题目：求100之内的素数
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
    for num in range(2, 101):
        if is_prime(num):
            primes.append(num)
    print(f"100以内的素数共有 {len(primes)} 个")
    print("素数列表:", primes)
