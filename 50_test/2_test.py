import math
'''
【程序2】  
题目：判断101-200之间有多少个素数，并输出所有素数。  
1.程序分析：判断素数的方法：用一个数分别去除2到sqrt(这个数)，如果能被整除，  
则表明此数不是素数，反之是素数。
'''
def is_prime()-> int:
    count = 0
    primes = []
    for num in range(101,201):
        for n in range(2, int(math.sqrt(num)) + 1):
            if num % n == 0:
                break
        else:
            primes.append(num)
            count += 1
    print("所有素数:", primes)
    return count

if __name__ == '__main__':
    print(f"101-200之间有{is_prime()}个素数")