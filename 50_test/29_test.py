'''
【程序29】  
题目：求一个3*3矩阵对角线元素之和  
1.程序分析：利用双重for循环控制输入二维数组，再将a累加后输出。  
'''
def func()-> list:
    arr = [
        [0,0,0], 
        [0,0,0], 
        [0,0,0]
    ]
    sum = 0
    for i in range(3):
        for j in range(3):
                if i==j:
                    num = int(input("请输入一个数字:"))
                    sum+=num
                    arr[i][j] = num
    return arr,sum
arr, sum = func()
print(arr)
print(sum)