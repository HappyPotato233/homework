'''
    【程序29】
    题目：求一个3*3矩阵对角线元素之和
    1.程序分析：利用双重for循环控制输入二维数组，再将a累加后输出。
'''
def diagonal_sum(matrix):
    total = 0
    for i in range(3):
        total += matrix[i][i]
    return total

if __name__ == '__main__':
    matrix = []
    for i in range(3):
        row = list(map(int, input(f"请输入第{i+1}行的3个数（用空格分隔）: ").split()))
        matrix.append(row)
    print(f"对角线元素之和: {diagonal_sum(matrix)}")
