'''
    【程序42】
    题目：809*??=800*??+9*??+1   其中??代表的两位数,8*??的结果为两位数，9*??的结果为3位数。求??代表的两位数，及809*??后的结果。
'''
def find_number():
    for x in range(10, 100):
        if 8 * x < 100 and 1000 >= 9 * x >= 100:
            if 809 * x == 800 * x + 9 * x + 1:
                return x, 809 * x
    return None

if __name__ == '__main__':
    result = find_number()
    if result:
        x, product = result
        print(f"??代表的两位数是: {x}")
        print(f"809*{x} = {product}")
