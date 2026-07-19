'''
【程序35】  
题目：输入数组，最大的与第一个元素交换，最小的与最后一个元素交换，输出数组。  
'''

def func():
    lst = [1,2,3,4,5,6,7,8,9,10]
    max_index = lst.index(max(lst))
    min_index = lst.index(min(lst))
    if max_index == len(lst)-1 and min_index == 0:
        lst[0],lst[-1] = lst[-1],lst[0]
    else:
        lst[max_index],lst[0] = lst[0],lst[max_index]
        lst[min_index],lst[-1] = lst[-1],lst[min_index]
    print(lst)
func()