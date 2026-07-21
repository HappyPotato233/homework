'''
【程序35】  
题目：输入数组，最大的与第一个元素交换，最小的与最后一个元素交换，输出数组。  
'''
def swap_max_min(arr):
    # 查找最大、最小值索引
    max_idx = 0
    min_idx = 0
    n = len(arr)
    
    for i in range(n):
        if arr[i] > arr[max_idx]:
            max_idx = i
        if arr[i] < arr[min_idx]:
            min_idx = i

    # 交换最大值和第一个元素
    arr[0], arr[max_idx] = arr[max_idx], arr[0]

    if min_idx == 0:
        min_idx = max_idx

    # 最小值和最后一个元素交换
    arr[-1], arr[min_idx] = arr[min_idx], arr[-1]
    return arr



nums = [8, 2, 5, 1, 9, 3]
print("原数组：", nums)
new_nums = swap_max_min(nums)
print("处理后：", new_nums)

