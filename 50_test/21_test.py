'''
【程序21】  
题目：求1+2!+3!+...+20!的和  
1.程序分析：此程序只是把累加变成了累乘。  
'''

def func():
    sum = 0
    a = 1
    for i in range(1, 21):
        for j in range(1, i + 1):
            a *= j
        sum += a
        a = 1
    print(sum)
func()