'''
    【程序36】  
    题目：有n个整数，使其前面各数顺序向后移m个位置，最后m个数变成最前面的m个数   
'''
def move(arr, m):
    n = len(arr)
    m = m % n  
    return arr[-m:] + arr[:-m]

nums = [1,2,3,4,5,6]
m = 2
res = move(nums, m)
print("移动后：", res)

