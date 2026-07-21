'''
    【程序40】  
    题目：字符串排序。  
'''
def sort_string(s):
    s_list = list(s)
    for i in range(len(s_list)):
        for j in range(i+1, len(s_list)):
            if s_list[i] > s_list[j]:
                s_list[i], s_list[j] = s_list[j], s_list[i]
    return ''.join(s_list)

if __name__ == '__main__':
    s = input("请输入一个字符串: ")
    print(f"排序后的字符串: {sort_string(s)}")
