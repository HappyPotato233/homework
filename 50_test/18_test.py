'''
【程序18】  
题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，乙队为x,y,z三人。已抽签决定比赛名单。有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，请编程序找出三队赛手的名单。  
'''
'''
    a->y, z
    c->y
    a->z
    b->x
'''

# 用0=x，1=y，2=z简化循环
for a in range(3):
    for b in range(3):
        for c in range(3):
            # 三人对手不能重复
            if a != b and a != c and b != c:
                # a不和x(0)比，c不和x(0)、z(2)比
                if a != 0 and c != 0 and c != 2:
                    dic = {0:'x', 1:'y', 2:'z'}
                    print(f"a 对战 {dic[a]}")
                    print(f"b 对战 {dic[b]}")
                    print(f"c 对战 {dic[c]}")