'''
    【程序37】  
    题目：有n个人围成一圈，顺序排号。从第一个人开始报数（从1到3报数），凡报到3的人退出圈子，问最后留下的是原来第几号的那位。 
'''
def last_person(n):
    people = list(range(1, n + 1))
    count = 0   # 报数计数器
    index = 0   # 当前下标
    while len(people) > 1:
        count += 1
        # 报到3，此人退出
        if count == 3:
            people.pop(index)
            count = 0    # 计数器清零
        else:
            index += 1
        # 循环取模，围成一圈
        index = index % len(people)
    return people[0]

# 测试
num = int(input("请输入人数n："))
res = last_person(num) 
print(f"最后留下的是原来第{res}号")