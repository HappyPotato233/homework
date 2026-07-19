'''
【程序31】  
题目：将一个数组逆序输出。  
1.程序分析：用第一个与最后一个交换。  
'''

def func()-> list:
    arr = [1,2,3,4,5,6,7,8,9]
    for i in range(len(arr)//2):
        arr[i], arr[-i-1] = arr[-i-1], arr[i]
    return arr

arr = func()
print(arr)