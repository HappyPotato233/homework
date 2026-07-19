'''
【程序44】  
题目：一个偶数总能表示为两个素数之和。  
'''

import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def find_two_primes(even_num):
    if even_num % 2 != 0:
        return None
    for i in range(2, even_num // 2 + 1):
        if is_prime(i) and is_prime(even_num - i):
            return (i, even_num - i)
    return None

if __name__ == '__main__':
    num = int(input("请输入一个偶数: "))
    result = find_two_primes(num)
    if result:
        print(f"{num} = {result[0]} + {result[1]}")
    else:
        print(f"未找到两个素数之和等于{num}")
