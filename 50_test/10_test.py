'''
    【程序10】  
    题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；再落下，求它在第10次落地时，共经过多少米？第10次反弹多高？ 
'''
def func(bounce):
    a = 100
    b = 100 / 2
    for i in range(2, bounce + 1):
        a += 2 * b
        b /= 2
    return a ,b


distance, height = func(10)
print(f"第10次落地时共经过 {distance} 米")
print(f"第10次反弹高度为 {height} 米")
