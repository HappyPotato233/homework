'''
    【程序1】  
    题目：古典问题：有一对兔子，从出生后第3个月起每个月都生一对兔子，小兔子长到第三个月后每个月又生一对兔子，假如兔子都不死，问每个月的兔子总数为多少？  
    1.程序分析： 兔子的规律为数列1,1,2,3,5,8,13,21.... 
'''
# 求第n个月有几只兔子
def febonaci(n)->int:
    if n == 0:
        raise ValueError("不可输入零")
    if n == 1 or n == 2:
        return 1
    a, b = 1, 1
    
    for _ in range(3,n + 1):
        a, b = b, a + b
    return b
if __name__ == '__main__':
    i = input("请输入月数:")
    n = int(i)
    if not isinstance(n, int):
        raise ValueError
    print(2*febonaci(n))