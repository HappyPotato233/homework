'''
【程序37】  
题目：有n个人围成一圈，顺序排号。从第一个人开始报数（从1到3报数），凡报到3的人退出圈子，问最后留下的是原来第几号的那位。  
'''

def func():
    num = int(input("请输入人数："))
    lst = list(range(1, num + 1))
    index = 0
    count = 0
    while len(lst) > 1:
        count +=1 
        if count == 3:
            lst.pop(index)
            count = 0
        else:
            index += 1
        index = index % len(lst)
    return lst[0]
print(func())




'''
    1,2,3,4,5
    2,4,5
    2,4
    2
'''