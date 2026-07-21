'''
【程序26】  
题目：请输入星期几的第一个字母来判断一下是星期几，如果第一个字母一样，则继续   判断第二个字母。  
1.程序分析：用情况语句比较好，如果第一个字母一样，则判断用情况语句或if语句判断第二个字母。  
'''
def get_day(letter):
    letter = letter.lower()
    if letter[0] == 'm':
        return '星期一'
    elif letter[0] == 't':
        if len(letter) > 1 and letter[1] == 'u':
            return '星期二'
        else:
            return '星期四'
    elif letter[0] == 'w':
        return '星期三'
    elif letter[0] == 'f':
        return '星期五'
    elif letter[0] == 's':
        if len(letter) > 1 and letter[1] == 'a':
            return '星期六'
        else:
            return '星期日'
    else:
        return '输入错误'

letter = input("请输入星期几的第一个字母: ")
print(get_day(letter))