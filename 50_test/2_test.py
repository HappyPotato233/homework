'''
    【程序2】  
    题目：判断101-200之间有多少个素数，并输出所有素数。  
    1.程序分析：判断素数的方法：用一个数分别去除2到sqrt(这个数)，如果能被整除， 则表明此数不是素数，反之是素数。 
'''
import math

def is_prime():
    primes = []
    for i in range(101, 201):
        for j in range(2, int(math.sqrt(i)) + 1):
            if i % j == 0:
                break
        else: 
            primes.append(i)
    return primes


primes = is_prime()
print(f"101-200之间共有 {len(primes)} 个素数")
print("素数列表:", primes)
