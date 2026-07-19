'''
【程序45】  
题目：判断一个素数能被几个9整除  
'''

import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def count_nine_divisions(n):
    count = 0
    while n % 9 == 0:
        count += 1
        n = n // 9
    return count

if __name__ == '__main__':
    num = int(input("请输入一个整数: "))
    if is_prime(num):
        print(f"{num} 是素数")
        if num % 9 == 0:
            print(f"{num} 能被9整除")
        else:
            print(f"{num} 不能被9整除")
    else:
        print(f"{num} 不是素数")
    print(f"{num} 能被9整除 {count_nine_divisions(num)} 次")
