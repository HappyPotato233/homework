'''
【程序30】  
题目：有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中。  
1.程序分析：首先判断此数是否大于最后一个数，然后再考虑插入中间的数的情况，插入后此元素之后的数，依次后移一个位置。4 
'''

def func()-> list:
    arr = [1,2,3,4,5,6,7,8,9]
    num = int(input("请输入一个数字:"))
    # 遍历找插入位置
    for i in range(len(arr)):
        if num < arr[i]:
            arr.insert(i, num)
            break
    else:
        arr.append(num)
    return arr

arr = func()
print(arr)
