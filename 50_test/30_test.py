'''
    【程序30】  
    有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中。  
1.   程序分析：首先判断此数是否大于最后一个数，然后再考虑插入中间的数的情况，插入后此元素之后的数，依次后移一个位置。 
'''
def func(arr, num):
    length = len(arr)
    pos = length  # 默认插到末尾
    for i in range(length):
        if num < arr[i]:
            pos = i
            break
    # 元素依次后移
    arr.append(0)  # 先扩容
    for j in range(length, pos, -1):
        arr[j] = arr[j-1]
    # 放入数字
    arr[pos] = num
    return arr

arr = [1, 3, 5, 7, 9]
print(f"原数组: {arr}")
num = int(input("请输入要插入的数: "))
result = func(arr, num)
print(f"插入后的数组: {result}")
