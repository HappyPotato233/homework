﻿'''
    【程序49】  
    题目：计算字符串中子串出现的次数。 
'''
def func(s, sub):
    count = 0
    for i in range(len(s) - len(sub) + 1):
        if s[i:i+len(sub)] == sub:
            count += 1
    return count


s = input("请输入字符串: ")
sub = input("请输入子串: ")
print(f"子串'{sub}'在字符串中出现了 {func(s, sub)} 次")
