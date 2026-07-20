'''
    【程序36】
    题目：有n个整数，使其前面各数顺序向后移m个位置，最后m个数变成最前面的m个数
'''
def rotate_array(arr, m):
    n = len(arr)
    m = m % n
    return arr[-m:] + arr[:-m]

if __name__ == '__main__':
    n = int(input("请输入整数个数n: "))
    m = int(input("请输入后移位置数m: "))
    arr = []
    for i in range(n):
        num = int(input(f"请输入第{i+1}个数: "))
        arr.append(num)
    print("原数组:", arr)
    result = rotate_array(arr, m)
    print("移动后的数组:", result)
