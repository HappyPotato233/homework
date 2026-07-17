# 初始化力量、智力、敏捷角色字典；
# 装饰器实现双倍伤害特效；
# lambda 计算基础伤害；
# 生成器产出魔法 Buff；
# 列表推导式限制合法加点 0~10；
# 加点函数判断点数合法性，返回结果；
# 捕获非数字输入异常，程序不崩溃；
# 菜单循环选择加点 / 退出，退出自动保存角色数据到本地文件；
# 加点成功且点数大于 4 时领取 Buff，实时展示双倍技能伤害。
from enum import Enum
import json
import random  # 每次打怪结束都声称随机奖励，随机1~10个点数

# 加点属性类型
class AttributeAdd(Enum):
    POWER = 1
    INTELLIGENCE = 2
    AGILE = 3

# 存档/加载存档
class OperateType(Enum):
    LOAD = 1
    SAVE = 2

# 1.字典初始化角色属性
dict_attr = {"power": 0, "intelligence": 0, "agile": 0}

# 2.装饰器：双倍伤害挂件
def double_damage(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) * 2
    return wrapper

# 3.lambda基础伤害计算
def attack(type):
    base_damage = 5
    match type:
        case "1":  # 普通攻击，把基础攻击力（设置为5）加上力量值
            # 利用lambda函数计算普通伤害
            normal = lambda base_damage, power_value: base_damage + power_value
            normal_damage = normal(base_damage, dict_attr["power"])
            print(f"普通攻击，造成伤害为基础伤害：{base_damage}+力量{dict_attr['power']}={normal_damage}")
        case "2":  # 技能攻击，把力量值乘上两倍
            s_damage = skill_damage(base_damage + dict_attr["power"])
            print(f"技能攻击，造成伤害为(基础伤害：{base_damage}+力量：{dict_attr['power']})*2={s_damage}")

# 4.生成器：批量产出buff效果，每次轮询一次
def generator_buff():
    buffs = ["力量+5", "智力+3", "敏捷+4"]
    for buff in buffs:
        yield buff

# 5.列表推导式，生成合法加点范围
def legal_attr():
    return [x for x in range(11)]

# 6.通用属性加点函数
def add_attr(attr, add_num, remain_point):
    # 判断加点数是否合法0~10
    if add_num not in legal_attr():
        print("点数超出正常范围0~10")
        return False
    # 判断加点不能超过剩余可用点数
    if add_num > remain_point:
        print("加点数量不能超过当前剩余点数！")
        return False
    # 判断加点哪个属性
    match attr:
        case AttributeAdd.POWER.value:
            dict_attr["power"] += add_num
        case AttributeAdd.INTELLIGENCE.value:
            dict_attr["intelligence"] += add_num
        case AttributeAdd.AGILE.value:
            dict_attr["agile"] += add_num
    return True

# 7.绑定装饰器的技能伤害函数
@double_damage
def skill_damage(damage_number):
    return damage_number

# 8.with实现角色数据存档/读档
def save_and_load(opt):
    match opt:
        # 存档
        case OperateType.SAVE:
            with open("role_data.json", "w") as f:
                json.dump(dict_attr, f, ensure_ascii=False, indent=2)
                print("角色数据保存成功")
        # 读档 补充实现加载逻辑
        case OperateType.LOAD:
            try:
                with open("role_data.json", "r", encoding="utf-8") as f:
                    global dict_attr
                    dict_attr = json.load(f)
                    print("读取存档成功！")
            except FileNotFoundError:
                print("未找到存档文件，使用初始属性")

# 菜单循环加点
def menu_add_attr(total_num):
    print(f"您当前有{total_num[0]}个点数,请先开始您的加点")
    buff_flag = False  # 标记本次加点是否加点成功，用于判断是否领Buff
    # 菜单进行加点
    # 限定10个点数，将得到的输入传给add_attr函数
    while True:
        # 如果点数小于等于0，直接退出循环
        if total_num[0] <= 0:
            print("没有可用点数，退出加点")
            return buff_flag

        # 显示当前各属性的值
        print(f"您当前的属性为\n力量：{dict_attr['power']}\n智力：{dict_attr['agile']}\n敏捷：{dict_attr['agile']}\n")
        try:
            # 获取用户输入属性
            attr = int(input("请输入您要加点的属性：\n加点力量请输入1\n加点智力请输入2\n加点敏捷请输入3\n退出加点请按0\n:"))
        # 捕获输入无法转为数字的异常（非数字输入）
        except ValueError:
            print("输入错误！请输入数字，重新选择属性。")
            continue
        
        match attr:
            case 1:
                attr = AttributeAdd.POWER.value
            case 2:
                attr = AttributeAdd.INTELLIGENCE.value
            case 3:
                attr = AttributeAdd.AGILE.value
            case 0:
                print("退出加点，自动保存角色数据")
                save_and_load(OperateType.SAVE)
                return buff_flag
            case _:
                print("请选择正确的属性")
                continue
        
        try:
            # 获取用户所加属性的加点数
            add_num = int(input(f"请输入您当前要加的点数，您当前拥有的可用点数{total_num[0]}\n:"))
        # 捕获加点数非数字异常
        except ValueError:
            print("输入错误！加点点数必须输入数字。")
            continue
        
        # 调用add_attr函数，传入剩余点数校验
        flag = add_attr(attr, add_num, total_num[0])
        # 显示加点结果，失败则提示输入不合法
        if flag == True:
            buff_flag = True
            print(f"加点成功！当前属性为：\n力量{dict_attr['power']}\n智力{dict_attr['intelligence']}\n敏捷{dict_attr['agile']}\n")
            total_num[0] -= add_num
        else:
            print("输入的点数不合法")

# 9.主函数：交互菜单
def main():
    print("===============欢迎进入游戏================")
    print("现在为您初始化你的角色\n")
    total_num = [10];
    # 加点返回标记：本次是否加点成功
    add_success = menu_add_attr(total_num)
    # 获取生成器
    g = generator_buff()
    while True:
        print("=====================================")
        print("现在开始游戏，本游戏会无限制刷怪供您进行攻击")        
        # 选择攻击方式进行攻击                
        attack_type = input("请选择攻击方式：\n1.普通攻击\n2.技能攻击\n:")
        attack(attack_type)

        # 打怪成功后获得经验
        print("=====================================")
        print(f"恭喜你，打怪成功，获得新的点数")
        # 随机获取点数
        random_num = random.randint(1, 10)
        print(f"本次随机到的点数为{random_num}")
        # 更新总点数
        total_num[0] += random_num
        print(f"您当前可用点数{total_num[0]}")
        
        # 是否进行加点
        try:
            add_attr_flag = input("是否进行加点：\n1.是\n2.否\n:")
            if add_attr_flag == "1":
                add_success = menu_add_attr(total_num)
        except Exception as e:
            print(f"输入发生未知异常：{e}")
        
        # 加点成功后进行获取buffpandua
        if add_success and total_num[0] >= 4:
            print("=====================================")
            print("加点成功且剩余点数≥4，领取新Buff")
            try:
                buff = next(g)
            # 生成器Buff耗尽捕获StopIteration异常
            except StopIteration:
                print("所有Buff已领取完毕，重置Buff列表！")
                g = generator_buff()
                buff = next(g)
            print(f"您已获得{buff}，并且减去4点可用点数")
            total_num[0] -= 4
            print(f"您当前可用点数{total_num[0]}")
            print("=====================================")
            add_success = False  # 重置标记，下次加点成功才可再次领取
        
        print("=====================================")
        try:
            # 是否结束游戏
            end = input("是否结束游戏：\n1.是\n2.否\n:")
            if end == "1":
                save_and_load(OperateType.SAVE)
                print("游戏退出，存档已保存")
                break
        except Exception as e:
            print(f"退出选择发生未知异常：{e}")

if __name__ == "__main__":
        main()