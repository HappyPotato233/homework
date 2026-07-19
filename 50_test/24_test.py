'''
【程序24】  
题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数字。  
'''
count = 0
def func(n):
    if n == 0:
        return
    print(n % 10)
    global count
    count += 1
    func(n // 10)
func(12345)
print(f"这是一个{count}位数")
