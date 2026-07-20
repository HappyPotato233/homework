'''
    【程序37】
    题目：有n个人围成一圈，顺序排号。从第一个人开始报数（从1到3报数），凡报到3的人退出圈子，问最后留下的是原来第几号的那位。
'''
def josephus(n, m):
    people = list(range(1, n + 1))
    index = 0
    while len(people) > 1:
        index = (index + m - 1) % len(people)
        people.pop(index)
    return people[0]

if __name__ == '__main__':
    n = int(input("请输入人数n: "))
    print(f"最后留下的是原来第 {josephus(n, 3)} 号")
