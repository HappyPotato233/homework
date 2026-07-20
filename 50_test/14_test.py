'''
    【程序14】
    题目：输入某年某月某日，判断这一天是这一年的第几天？
    1.程序分析：以3月5日为例，应该先把前两个月的加起来，然后再加上5天即本年的第几天，特殊情况，闰年且输入月份大于3时需考虑多加一天。
'''
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def day_of_year(year, month, day):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if is_leap_year(year):
        days_in_month[1] = 29
    
    total = 0
    for i in range(month - 1):
        total += days_in_month[i]
    total += day
    return total

if __name__ == '__main__':
    year = int(input("请输入年份: "))
    month = int(input("请输入月份: "))
    day = int(input("请输入日期: "))
    print(f"这一天是这一年的第 {day_of_year(year, month, day)} 天")
