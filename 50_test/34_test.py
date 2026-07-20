'''
    【程序34】
    题目：输入3个数a,b,c，按大小顺序输出。
    1.程序分析：利用指针方法。
'''
def sort_three(a, b, c):
    if a > b:
        a, b = b, a
    if a > c:
        a, c = c, a
    if b > c:
        b, c = c, b
    return a, b, c

if __name__ == '__main__':
    a = int(input("请输入第一个数a: "))
    b = int(input("请输入第二个数b: "))
    c = int(input("请输入第三个数c: "))
    x, y, z = sort_three(a, b, c)
    print(f"按大小顺序输出: {x} {y} {z}")
