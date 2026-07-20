'''
    【程序18】
    题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，乙队为x,y,z三人。已抽签决定比赛名单。有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，请编程序找出三队赛手的名单。
'''
def find_match():
    a_partners = ['x', 'y', 'z']
    for a in a_partners:
        for b in a_partners:
            for c in a_partners:
                if len(set([a, b, c])) == 3:
                    if a != 'x' and c != 'x' and c != 'z':
                        return [('a', a), ('b', b), ('c', c)]
    return None

if __name__ == '__main__':
    matches = find_match()
    print("比赛名单:")
    for member, opponent in matches:
        print(f"{member} 对阵 {opponent}")
