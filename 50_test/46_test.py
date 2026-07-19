'''
【程序46】  
题目：两个字符串连接程序  
'''

def concatenate(s1, s2):
    result = []
    for c in s1:
        result.append(c)
    for c in s2:
        result.append(c)
    return ''.join(result)

if __name__ == '__main__':
    assert concatenate("Hello", "World") == "HelloWorld"
    assert concatenate("", "Test") == "Test"
    assert concatenate("Test", "") == "Test"
    assert concatenate("a", "b") == "ab"
    print("测试用例:")
    print(f"concatenate('Hello', 'World') = '{concatenate('Hello', 'World')}'")
    print(f"concatenate('', 'Test') = '{concatenate('', 'Test')}'")
    print(f"concatenate('Test', '') = '{concatenate('Test', '')}'")
    print("所有测试用例通过！")
