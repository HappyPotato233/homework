'''
    【程序7】  
    题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。  
'''
def func(s):
    letter = 0
    space = 0
    digit = 0
    other = 0
    for char in s:
        if char.isalpha():
            letter += 1
        elif char.isspace():
            space += 1
        elif char.isdigit():
            digit += 1
        else:
            other += 1
    return letter, space, digit, other


inputs = input("请输入一行字符:")
letter, space, digit, other = func(inputs)
print(f"字母个数: {letter}")
print(f"空格个数: {space}")
print(f"数字个数: {digit}")
print(f"其它字符个数: {other}")
