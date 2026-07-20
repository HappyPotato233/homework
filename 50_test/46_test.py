'''
    【程序46】
    题目：两个字符串连接程序
'''
def string_concat(s1, s2):
    return s1 + s2

if __name__ == '__main__':
    s1 = input("请输入第一个字符串: ")
    s2 = input("请输入第二个字符串: ")
    result = string_concat(s1, s2)
    print(f"连接后的字符串: {result}")
