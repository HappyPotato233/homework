'''
【程序7】  
题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。  
1.程序分析：利用while语句,条件为输入的字符不为 '\n '. 
'''

inputs = input("请输入一行字符:")
letter, space, digit, other = 0, 0, 0, 0
i = 0
inputs = inputs + '\n'
while inputs[i] != '\n':
    if inputs[i].isalpha():
        letter +=1
    elif inputs[i].isspace():
        space +=1
    elif inputs[i].isdigit():
        digit +=1
    else:
        other +=1
    i +=1

print(f"字母个数:{letter}")
print(f"空格个数:{space}")
print(f"数字个数:{digit}")
print(f"其它字符个数:{other}")
