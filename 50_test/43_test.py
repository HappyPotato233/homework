'''
    【程序43】
    题目：求0—7所能组成的奇数个数。
'''
def count_odd_numbers():
    count = 0
    digits = [0, 1, 2, 3, 4, 5, 6, 7]
    
    for length in range(1, 8):
        if length == 1:
            for d in digits:
                if d % 2 == 1:
                    count += 1
        else:
            first_count = 7
            last_count = 4
            middle = 1
            for i in range(length - 2):
                middle *= 8
            count += first_count * middle * last_count
    
    return count

if __name__ == '__main__':
    print(f"0—7所能组成的奇数个数: {count_odd_numbers()}")
