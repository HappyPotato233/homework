﻿'''
    【程序31】  
    题目：将一个数组逆序输出。  
    1.程序分析：用第一个与最后一个交换。  
'''

def func(arr):
    for i in range(len(arr) // 2):
        arr[i], arr[-i - 1] = arr[-i - 1], arr[i]
    return arr
arr = [1,3,5,2,4,6,9,10,7,8]
print("逆序后的结果:", func(arr))
