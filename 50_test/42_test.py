'''
【程序42】  
题目：809*??=800*??+9*??+1   其中??代表的两位数,8*??的结果为两位数，9*??的结果为3位数。求??代表的两位数，及809*??后的结果。  
'''

def find_number():
    for n in range(10, 100):
        if 10 <= 8 * n <= 99 and 100 <= 9 * n <= 999:
            if 809 * n == 800 * n + 9 * n + 1:
                return n, 809 * n
    return None

if __name__ == '__main__':
    result = find_number()
    if result:
        n, product = result
        print(f"??代表的两位数是: {n}")
        print(f"809*{n}的结果是: {product}")
    else:
        print("未找到符合条件的两位数")
