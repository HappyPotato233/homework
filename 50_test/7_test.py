'''
    【程序7】
    题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。
    1.程序分析：利用while语句,条件为输入的字符不为 '\n '.
'''
def count_chars(s):
    letters = 0
    space = 0
    digit = 0
    others = 0
    for c in s:
        if c.isalpha():
            letters += 1
        elif c.isspace():
            space += 1
        elif c.isdigit():
            digit += 1
        else:
            others += 1
    return letters, space, digit, others

if __name__ == '__main__':
    s = input("请输入一行字符: ")
    letters, space, digit, others = count_chars(s)
    print(f"英文字母: {letters} 个")
    print(f"空格: {space} 个")
    print(f"数字: {digit} 个")
    print(f"其它字符: {others} 个")
