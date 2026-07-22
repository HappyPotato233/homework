'''
    【程序45】  
    题目：判断一个素数能被几个9整除 
'''
import math
def is_prime(num)-> bool:
    if num <= 1:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def func(num)-> int:
    count = 0
    times = 1
    if not is_prime(num):
        print(f"{num}不是素数")
        return 0
    while True:
        if num % (9*times) == 0:
            count +=1
            break
        else:
            times +=1
    return count
num = int(input("请输入一个素数："))
print(func(num))