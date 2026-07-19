'''
【程序38】  
题目：写一个函数，求一个字符串的长度，在main函数中输入字符串，并输出其长度。  
'''

def func(str):
    count = 0
    str = str.strip()
    for i in str:
        if i !='\n':
            count += 1 
    return count

def main():
    str = input("请输入字符串：")
    print(func(str))
main()