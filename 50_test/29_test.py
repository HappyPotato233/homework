'''
    【程序29】  
    题目：求一个3*3矩阵对角线元素之和  
1.程序分析：利用双重for循环控制输入二维数组，再将a累加后输出。  
'''

def func(matrix):
    return matrix[0][0] + matrix[1][1] + matrix[2][2] + matrix[0][2] + matrix[2][0]


matrix = []
print("请输入3*3矩阵:")
for i in range(3):
    row = []
    for j in range(3):
        row.append(int(input(f"请输入第{i+1}行第{j+1}列元素:")))
    matrix.append(row)
print(f"对角线元素之和: {func(matrix)}")
