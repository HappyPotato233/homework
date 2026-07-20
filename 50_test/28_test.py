'''
    【程序28】
    题目：对10个数进行排序
    1.程序分析：可以利用选择法，即从后9个比较过程中，选择一个最小的与第一个元素交换，   下次类推，即用第二个元素与后8个进行比较，并进行交换。
'''
def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

if __name__ == '__main__':
    numbers = []
    for i in range(10):
        num = int(input(f"请输入第{i+1}个数: "))
        numbers.append(num)
    print("排序前:", numbers)
    sorted_numbers = selection_sort(numbers)
    print("排序后:", sorted_numbers)
