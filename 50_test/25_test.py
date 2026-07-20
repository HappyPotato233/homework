'''
    【程序25】
    题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同。
'''
def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

if __name__ == '__main__':
    n = int(input("请输入一个5位数: "))
    if is_palindrome(n):
        print(f"{n} 是回文数")
    else:
        print(f"{n} 不是回文数")
