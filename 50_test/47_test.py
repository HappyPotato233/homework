'''
    【程序47】
    题目：读取7个数（1—50）的整数值，每读取一个值，程序打印出该值个数的＊。
'''
def print_stars(n):
    print('*' * n)

if __name__ == '__main__':
    for i in range(7):
        while True:
            num = int(input(f"请输入第{i+1}个整数（1-50）: "))
            if 1 <= num <= 50:
                break
            print("输入范围错误，请输入1-50之间的数")
        print_stars(num)
