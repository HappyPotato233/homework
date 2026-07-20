'''
    【程序40】
    题目：字符串排序。
'''
def string_sort(strings):
    return sorted(strings)

if __name__ == '__main__':
    n = int(input("请输入字符串个数: "))
    strings = []
    for i in range(n):
        s = input(f"请输入第{i+1}个字符串: ")
        strings.append(s)
    print("排序前:", strings)
    sorted_strings = string_sort(strings)
    print("排序后:", sorted_strings)
