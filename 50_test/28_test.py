'''
【程序28】  
题目：对10个数进行排序  
1.程序分析：可以利用选择法，即从后9个比较过程中，选择一个最小的与第一个元素交换，   下次类推，即用第二个元素与后8个进行比较，并进行交换。  
'''

def func(arr):
    for i in range(10):
        for j in range(i + 1, 10):
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
    print(arr)
arr = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
func(arr)
