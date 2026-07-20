'''
    【程序31】
    题目：将一个数组逆序输出。
    1.程序分析：用第一个与最后一个交换。
'''
def reverse_array(arr):
    return arr[::-1]

if __name__ == '__main__':
    n = int(input("请输入数组元素个数: "))
    arr = []
    for i in range(n):
        num = int(input(f"请输入第{i+1}个数: "))
        arr.append(num)
    print("原数组:", arr)
    reversed_arr = reverse_array(arr)
    print("逆序输出:", reversed_arr)
