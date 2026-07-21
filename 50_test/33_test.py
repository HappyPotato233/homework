'''
【程序33】  
题目：打印出杨辉三角形（要求打印出10行如下图）  
1.程序分析：  
        1  
      1   1  
    1   2   1  
  1   3   3   1  
 1   4   6   4   1  
1   5   10   10   5   1  
'''
# 初始化10行杨辉三角
n = 10
triangle = []
for i in range(n):
    row = [1] * (i + 1)   # 每行先全部置1
    # 计算中间元素
    for j in range(1, i):
        row[j] = triangle[i-1][j-1] + triangle[i-1][j]
    triangle.append(row)

# 格式化输出，对齐展示
for line in triangle:
    # 控制空格实现居中效果
    print(" ".join(f"{num:2d}" for num in line).center(40))

