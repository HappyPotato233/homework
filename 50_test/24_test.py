'''
    【程序24】  
    题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数字。 
'''
def func(n):
    digits = str(n)
    print(f"它是 {len(digits)} 位数")
    print("逆序打印:", digits[::-1])

if __name__ == '__main__':
    num = int(input("请输入一个不多于5位的正整数: "))
    func(num)
