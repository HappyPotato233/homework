﻿'''
    【程序48】  
    题目：某个公司采用公用电话传递数据，数据是四位的整数，在传递过程中是加密的，加密规则如下：每位数字都加上5,然后用和除以10的余数代替该数字，再将第一位和第四位交换，第二位和第三位交换。 
'''
def func(n):
    digits = list(map(int, str(n)))
    for i in range(4):
        digits[i] = (digits[i] + 5) % 10
    digits[0], digits[3] = digits[3], digits[0]
    digits[1], digits[2] = digits[2], digits[1]
    return int(''.join(map(str, digits)))

num = int(input("请输入一个四位整数: "))
if num < 1000 or num > 9999:
    print("请输入四位整数!")
else:
    print(f"加密后的数字: {func(num)}")
