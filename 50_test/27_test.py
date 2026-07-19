'''
【程序27】  
题目：求100之内的素数  
'''
import math
def func():
    for i in range(2, 100):
        for j in range(2, int(math.sqrt(i)) + 1):
            if i % j == 0:
                break
        else:
            print(i)
func()