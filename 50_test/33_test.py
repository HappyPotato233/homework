'''
【程序33】  
题目：打印出杨辉三角形（要求打印出10行如下图）
1
1   1
1   2   1
1   3   3   1
1   4   6   4   1
1   5   10   10   5   1  
'''
def func(n=10):
    lst = []
    for i in range(n):
        row = [1] * (i + 1)
        # 计算中间元素
        for j in range(1, i):
            row[j] = lst[i-1][j-1] + lst[i-1][j]
        lst.append(row)
        # 打印当前行，空格分隔
        for item in row:
            print(item,end='   ')
        print() 

# 打印10行杨辉三角
func(10)
