'''
    【程序30】
    题目：有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中。
    1.   程序分析：首先判断此数是否大于最后一个数，然后再考虑插入中间的数的情况，插入后此元素之后的数，依次后移一个位置。
'''
def insert_sorted(arr, num):
    result = arr.copy()
    result.append(num)
    for i in range(len(result) - 1, 0, -1):
        if result[i] < result[i - 1]:
            result[i], result[i - 1] = result[i - 1], result[i]
        else:
            break
    return result

if __name__ == '__main__':
    sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
    print("原有序数组:", sorted_arr)
    num = int(input("请输入要插入的数: "))
    new_arr = insert_sorted(sorted_arr, num)
    print("插入后的数组:", new_arr)
