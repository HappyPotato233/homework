'''
    【程序35】
    题目：输入数组，最大的与第一个元素交换，最小的与最后一个元素交换，输出数组。
'''
def swap_max_min(arr):
    max_idx = arr.index(max(arr))
    min_idx = arr.index(min(arr))
    if max_idx == min_idx:
        return arr
    
    arr[0], arr[max_idx] = arr[max_idx], arr[0]
    arr[-1], arr[min_idx] = arr[min_idx], arr[-1]
    return arr

if __name__ == '__main__':
    n = int(input("请输入数组元素个数: "))
    arr = []
    for i in range(n):
        num = int(input(f"请输入第{i+1}个数: "))
        arr.append(num)
    print("原数组:", arr)
    result = swap_max_min(arr)
    print("处理后的数组:", result)
