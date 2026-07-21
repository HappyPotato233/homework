'''
    【程序28】  
    题目：对10个数进行排序  
1.程序分析：可以利用选择法，即从后9个比较过程中，选择一个最小的与第一个元素交换，   下次类推，即用第二个元素与后8个进行比较，并进行交换。 
'''

def func(arr):
    for i in range(n - 1):
        # 最小值下标
        min_index = i
        # 找更小值
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        # 找到最小值，交换位置
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr
arr = [1,3,5,2,4,6,9,10,7,8]
print("排序后的结果:", func(arr))
