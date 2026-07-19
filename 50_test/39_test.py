'''
【程序39】  
题目：编写一个函数，输入n为偶数时，调用函数求1/2+1/4+...+1/n,当输入n为奇数时，调用函数1/1+1/3+...+1/n(利用指针函数)  
'''

def func1(n):
    sum = 0
    for i in range(2,n+1,2):
        sum += 1/i
    print(sum)
def func2(n):
    sum = 0
    for i in range(1,n+1,2):
        sum += 1/i
    print(sum)

def main():
    n = int(input("请输入一个整数："))
    if n % 2 == 0:
        func1(n)
    else:
        func2(n)
main()