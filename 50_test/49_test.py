'''
    【程序49】
    题目：计算字符串中子串出现的次数
'''
def count_substring(s, sub):
    count = 0
    start = 0
    while True:
        pos = s.find(sub, start)
        if pos == -1:
            break
        count += 1
        start = pos + 1
    return count

if __name__ == '__main__':
    s = input("请输入字符串: ")
    sub = input("请输入子串: ")
    count = count_substring(s, sub)
    print(f"子串出现的次数: {count}")
