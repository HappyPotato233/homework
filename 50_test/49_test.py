'''
【程序49】  
题目：计算字符串中子串出现的次数  
'''

def count_substring(s, sub):
    count = 0
    sub_len = len(sub)
    s_len = len(s)
    if sub_len == 0 or sub_len > s_len:
        return 0
    for i in range(s_len - sub_len + 1):
        if s[i:i+sub_len] == sub:
            count += 1
    return count

if __name__ == '__main__':
    assert count_substring("abababa", "aba") == 3
    assert count_substring("hello world", "o") == 2
    assert count_substring("test", "t") == 2
    assert count_substring("aaaaa", "aa") == 4
    assert count_substring("python", "java") == 0
    print("测试用例:")
    print(f"count_substring('abababa', 'aba') = {count_substring('abababa', 'aba')}")
    print(f"count_substring('hello world', 'o') = {count_substring('hello world', 'o')}")
    print(f"count_substring('aaaaa', 'aa') = {count_substring('aaaaa', 'aa')}")
    print("所有测试用例通过！")
