'''
    【程序38】
    题目：写一个函数，求一个字符串的长度，在main函数中输入字符串，并输出其长度。
'''
def str_length(s):
    count = 0
    for _ in s:
        count += 1
    return count

if __name__ == '__main__':
    s = input("请输入一个字符串: ")
    print(f"字符串长度为: {str_length(s)}")
