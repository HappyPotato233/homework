'''
【程序41】  
题目：海滩上有一堆桃子，五只猴子来分。第一只猴子把这堆桃子凭据分为五份，多了一个，这只猴子把多的一个扔入海中，拿走了一份。第二只猴子把剩下的桃子又平均分成五份，又多了一个，它同样把多的一个扔入海中，拿走了一份，第三、第四、第五只猴子都是这样做的，问海滩上原来最少有多少个桃子？  
'''

def find_peaches():
    x = 1
    while True:
        peaches = x
        valid = True
        for _ in range(5):
            if peaches % 4 != 0:
                valid = False
                break
            peaches = peaches // 4 * 5 + 1
        if valid:
            return peaches
        x += 1

if __name__ == '__main__':
    result = find_peaches()
    print(f"原来最少有 {result} 个桃子")
