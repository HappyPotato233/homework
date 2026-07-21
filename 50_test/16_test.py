'''
    【程序16】  
    题目：输出9*9乘法口诀表。  
    1.程序分析：分行与列考虑，共9行9列，i控制行，j控制列。 
'''
def func():
    for i in range(1, 10):
        for j in range(1, i + 1):
            print(f"{j}*{i}={i*j}", end="\t")
        print()


func()
