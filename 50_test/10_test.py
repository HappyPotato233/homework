'''
    【程序10】
    题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；再落下，求它在   第10次落地时，共经过多少米？第10次反弹多高？
'''
def calculate_distance_and_height(total_bounces):
    total_distance = 100
    current_height = 100 / 2
    for i in range(2, total_bounces + 1):
        total_distance += 2 * current_height
        current_height /= 2
    return total_distance, current_height

if __name__ == '__main__':
    distance, height = calculate_distance_and_height(10)
    print(f"第10次落地时共经过 {distance} 米")
    print(f"第10次反弹高度为 {height} 米")
