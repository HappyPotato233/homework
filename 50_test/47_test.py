'''
【程序47】  
题目：读取7个数（1—50）的整数值，每读取一个值，程序打印出该值个数的＊。  
'''

def print_stars(numbers):
    for i, num in enumerate(numbers):
        if 1 <= num <= 50:
            print(f"第{i+1}个数: {'*' * num}")
        else:
            print(f"第{i+1}个数: 输入值不在1-50范围内")

if __name__ == '__main__':
    test_input = [3, 5, 7, 2, 10, 1, 4]
    print_stars(test_input)
