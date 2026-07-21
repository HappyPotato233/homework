'''
    【程序43】  
    题目：求0—7所能组成的奇数个数。 
'''
def func(nums, number, res):
    # number存储已经拼接的数字列表
    if number:
        num = int(''.join(map(str,number)))
        if num % 2 == 1:
            res.append(num)
    if len(number) == 8:
        return
    for num in nums:
        if num == 0 and len(number) == 0:
            continue
        if num in number:
            continue
        func(nums, number + [num], res)

if __name__ == '__main__':
    digits = [0,1,2,3,4,5,6,7]
    res = []
    func(digits, [], res)
    print(f"总数为:{len(res)}")
