from traceback import print_list
'''
【程序10】  
题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；再落下，求它在   第10次落地时，共经过多少米？第10次反弹多高？  
'''
def func(count)-> list:
    lst = []
    for i in range(1, count +1):
        lst.append(100 / 2 ** i)
    return lst
print(f"第10次落地时，共经过{sum(func(10))}")
print(f"第10次反弹高度为{func(10)[9]:.2f}")
