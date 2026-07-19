'''
【程序14】  
题目：输入某年某月某日，判断这一天是这一年的第几天？  
1.程序分析：以3月5日为例，应该先把前两个月的加起来，然后再加上5天即本年的第几天，特殊情况，闰年且输入月份大于3时需考虑多加一天。  
'''
def func(year: int, month: int, day: int) -> int:
    # 闰年判断
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return day + sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:month - 1])
    else:
        return day + sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:month - 1])
time = input("请输入日期，格式为yyyy-mm-dd:")
year, month, day = int(time.split("-")[0]), int(time.split("-")[1]), int(time.split("-")[2])
print(f"{year}年{month}月{day}日是这一年的第{func(year, month, day)}天")