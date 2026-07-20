'''
    【程序45】
    题目：判断一个素数能被几个9整除
'''
def count_nines_divisible(prime):
    if prime == 2 or prime == 5:
        return 0
    remainder = 0
    count = 0
    while True:
        remainder = (remainder * 10 + 9) % prime
        count += 1
        if remainder == 0:
            return count

if __name__ == '__main__':
    import math
    prime = int(input("请输入一个素数: "))
    count = count_nines_divisible(prime)
    print(f"素数 {prime} 能被 {count} 个9组成的数整除")
