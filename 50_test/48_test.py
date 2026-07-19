'''
【程序48】  
题目：某个公司采用公用电话传递数据，数据是四位的整数，在传递过程中是加密的，加密规则如下：每位数字都加上5,然后用和除以10的余数代替该数字，再将第一位和第四位交换，第二位和第三位交换。  
'''

def encrypt(num):
    if not (1000 <= num <= 9999):
        return None
    digits = list(map(int, str(num)))
    for i in range(4):
        digits[i] = (digits[i] + 5) % 10
    digits[0], digits[3] = digits[3], digits[0]
    digits[1], digits[2] = digits[2], digits[1]
    return int(''.join(map(str, digits)))

if __name__ == '__main__':
    test_cases = [1234, 5678, 9999, 1000]
    for num in test_cases:
        print(f"{num} → {encrypt(num)}")
    assert encrypt(1234) == 9876
    assert encrypt(5678) == 3210
    assert encrypt(9999) == 4444
    assert encrypt(1000) == 5556
    print("所有测试用例通过！")
