'''
【程序40】  
题目：字符串排序。  
'''

def func(s):
    s_list = list(s)
    for i in range(len(s_list)):
        for j in range(i+1, len(s_list)):
            if s_list[i] > s_list[j]:
                s_list[i], s_list[j] = s_list[j], s_list[i]
    print(''.join(s_list))

def main():
    s = input("请输入字符串：")
    func(s)

main()