'''
    【程序27】  
    题目：求100之内的素数  
'''
def func():
    primes = []
    for num in range(2, 101):
        if all(num % i != 0 for i in range(2, num)):
            primes.append(num)
    return primes


print("100以内的素数:", func())
