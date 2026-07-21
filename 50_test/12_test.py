'''
    【程序12】  
    题目：企业发放的奖金根据利润提成。利润(I)低于或等于10万元时，奖金可提10%；
    利润高于10万元，低于20万元时，低于10万元的部分按10%提成，高于10万元的部分，可提成7.5%
    ；20万到40万之间时，高于20万元的部分，可提成5%
    ；40万到60万之间时高于40万元的部分，可提成3%
    ；60万到100万之间时，高于60万元的部分，可提成1.5%，高于100万元时，超过100万元的部分按1%提成，从键盘输入当月利润I，求应发放奖金总数？ 
    1.程序分析：请利用数轴来分界，定位。注意定义时需把奖金定义成长整型。 
'''
def func(profit):
    period = [
        (100000, 0.1),
        (200000, 0.075),
        (400000, 0.05),
        (600000, 0.03),
        (1000000, 0.015),
        (float("inf"), 0.001)
    ]
    previous_point = 0
    bonus = 0
    for p, rate in period:
        if profit > p:
            bonus += (p - previous_point) * rate
            previous_point = p
        else:
            # 只计算剩余部分
            bonus += (profit - previous_point) * rate
            break
    
    return bonus

profit = float(input("请输入当月利润(元): "))
bonus = func(profit)
print(f"应发放奖金总数: {bonus} 元")
