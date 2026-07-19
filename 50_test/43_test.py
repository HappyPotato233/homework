'''
【程序43】  
题目：求0—7所能组成的奇数个数。  
'''

def count_odd_no_repeat():
    total = 0
    for n in range(1, 9):
        if n == 1:
            total += 4
        elif n == 8:
            total += 4 * 6 * 720
        else:
            total += 4 * 6 * 7 ** (n - 2)
    return total

def count_odd_with_repeat():
    total = 0
    for n in range(1, 9):
        total += 8 ** (n - 1) * 4
    return total

if __name__ == '__main__':
    print(f"不重复使用数字的奇数个数: {count_odd_no_repeat()}")
    print(f"允许重复使用数字的奇数个数: {count_odd_with_repeat()}")
