'''
【程序36】  
题目：有n个整数，使其前面各数顺序向后移m个位置，最后m个数变成最前面的m个数  
'''
def func(m):
    lst = [1,2,3,4,5,6,7,8,9,10]
    lst = lst[-m:] + lst[:-m]
    print(lst)
    return lst
func(3)
