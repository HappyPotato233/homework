# goods/milk_cap.py - 奶盖茶子类
# 继承BaseDrink，实现奶盖茶专属优惠：购买2杯及以上立减3元
# 实例属性，__milk_cap_cost 
# get_milk_cap_cost()   -->获取奶盖的单杯价格

#测试代码

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from goods.base_drink import BaseDrink
# 果茶类
class MilkCapTea(BaseDrink):
    # ============1.实例方法==============
    type = "奶盖茶"
    '''
        构造函数
        参数：
            name: 商品名称
            price: 商品价格
    '''
    def __init__(self, name: str, price: float):
        super().__init__(name, price)
        self.__milk_cap_cost = price # 奶盖的单价
    
    '''
        实现奶盖茶专属优惠：购买2杯及以上立减3元
        参数：
            buy_num: 购买数量
    '''
    def get_final_price(self, buy_num: int)->float:
        # 计算原价价格
        origin = self.price * buy_num
        # 优惠价格
        if buy_num >=2: # 实现购买两杯以上立减3元
            origin -= 3
        final = origin * BaseDrink.shop_discount
        return round(max(final, 0), 2) # round 是保留2位小数的意思
    '''
        获取商品单价
    '''
    def get_milk_cap_cost(self)-> float:
        return self.__milk_cap_cost # 私有属性，通过方法访问
    '''
        打印小票
    '''
    def print_ticket(self, buy_num: int)-> str:

        # 获取最终价格
        final = self.get_final_price(buy_num)
        # 获取商品名称
        name = self.name
        # 获取商品数量
        num = buy_num
        # 获取商品单价格
        price = self.price
        return f"=============小票=============\n" \
               f" 商品名称:            {name}\n" \
               f"                      {price}*{buy_num}杯\n" \
               f" 商品总价:{final}\n" \
               f" 优惠信息:购买两杯奶盖以上，立减3元！\n" \
               f"============================="

if __name__ == "__main__":
    pass
    # 创建对象
    # fruit_tea = Milk_cap("茉莉奶盖", 5.5)
    # print("================1.测试新增功能=================")
    # # 测试打印小票
    # print(fruit_tea.print_ticket(2))
    # # 测试获取单杯价格
    # print(f"单杯价格:{fruit_tea.get_milk_cap_cost()}")
    # print("================2.测试优惠功能=================")
    # print(fruit_tea.get_final_price(2))