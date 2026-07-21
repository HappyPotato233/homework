'''
    【程序11】  
    题目：有1、2、3、4个数字，能组成多少个互不相同且无重复数字的三位数？都是多少？ 
    1.程序分析：可填在百位、十位、个位的数字都是1、2、3、4。组成所有的排列后再去 掉不满足条件的排列。 
'''
def func():
    results = []
    for x in range(1, 5):
        for y in range(1, 5):
            for z in range(1, 5):
                if x != y and y != z and x != z:
                    results.append(x * 100 + y * 10 + z)
    return results


numbers = func()
print(f"共有 {len(numbers)} 个互不相同且无重复数字的三位数")
print("它们是:", numbers)
