'''
    【程序15】  
    题目：输入三个整数x,y,z，请把这三个数由小到大输出。  
'''
def func(x, y, z):
    return sorted([x, y, z])


x = int(input("请输入第一个整数: "))
y = int(input("请输入第二个整数: "))
z = int(input("请输入第三个整数: "))
sorted_nums = func(x, y, z)
print(f"由小到大排列: {sorted_nums[0]}, {sorted_nums[1]}, {sorted_nums[2]}")
