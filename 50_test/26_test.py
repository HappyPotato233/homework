'''
    【程序26】
    题目：请输入星期几的第一个字母来判断一下是星期几，如果第一个字母一样，则继续   判断第二个字母。
    1.程序分析：用情况语句比较好，如果第一个字母一样，则判断用情况语句或if语句判断第二个字母。
'''
def what_day():
    first = input("请输入星期几的第一个字母: ").lower()
    if first == 'm':
        return "星期一"
    elif first == 't':
        second = input("请输入第二个字母: ").lower()
        if second == 'u':
            return "星期二"
        elif second == 'h':
            return "星期四"
    elif first == 'w':
        return "星期三"
    elif first == 'f':
        return "星期五"
    elif first == 's':
        second = input("请输入第二个字母: ").lower()
        if second == 'a':
            return "星期六"
        elif second == 'u':
            return "星期日"
    return "输入有误"

if __name__ == '__main__':
    print(what_day())
