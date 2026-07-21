'''
    【程序44】  
    题目：一个偶数总能表示为两个素数之和 
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

def find_two_primes(n):
    for i in range(2, n):
        if is_prime(i) and is_prime(n - i):
            return i, n - i
    return None

if __name__ == '__main__':
    n = int(input("请输入一个偶数: "))
    if n % 2 != 0:
        print("请输入偶数!")
    else:
        result = find_two_primes(n)
        if result:
            print(f"{n} = {result[0]} + {result[1]}")
        else:
            print(f"未能找到两个素数之和等于{n}")
