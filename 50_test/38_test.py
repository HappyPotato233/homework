'''
    【程序38】  
    题目：写一个函数，求一个字符串的长度，在main函数中输入字符串，并输出其长度。  
'''
def get_length(s):
    count = 0
    i = 0
    while True:
        try:
            s[i]
            count += 1
            i += 1
        except IndexError:
            break
    return count


str1 = input("输入字符串：")
print("长度：", get_length(str1))
