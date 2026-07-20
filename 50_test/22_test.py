'''
    【程序22】
    题目：利用递归方法求5!。
    1.程序分析：递归公式：fn=fn_1*4!
'''
def factorial_recursive(n):
    if n == 1:
        return 1
    return n * factorial_recursive(n - 1)

if __name__ == '__main__':
    print(f"5! = {factorial_recursive(5)}")
