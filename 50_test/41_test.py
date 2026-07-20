'''
    【程序41】
    题目：海滩上有一堆桃子，五只猴子来分。第一只猴子把这堆桃子凭据分为五份，多了一个，这只猴子把多的一个扔入海中，拿走了一份。第二只猴子把剩下的桃子又平均分成五份，又多了一个，它同样把多的一个扔入海中，拿走了一份，第三、第四、第五只猴子都是这样做的，问海滩上原来最少有多少个桃子？
'''
def monkey_peach_problem():
    peach = 1
    while True:
        temp = peach
        valid = True
        for i in range(5):
            if (temp - 1) % 5 != 0:
                valid = False
                break
            temp = (temp - 1) // 5 * 4
        if valid:
            return peach
        peach += 1

if __name__ == '__main__':
    print(f"海滩上原来最少有 {monkey_peach_problem()} 个桃子")
