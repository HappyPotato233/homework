# goods/fruit_tea.py - 果茶子类
# 继承BaseDrink，实现果茶专属优惠：全场折扣基础上额外95折

#重写打印小票方法：显示果茶专属优惠信息

#测试代码


import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from goods.base_drink import BaseDrink
# 果茶类
class FruitTea(BaseDrink):
    fruit_tea_discount = 0.95
    # 类变量：饮品类型
    type = "果茶"
    '''
        构造函数
        参数：
            name: 商品名称
            price: 商品价格
    '''
    def __init__(self, name: str, price: float):
        super().__init__(name, price)

    '''
        实现果茶专属优惠，全场折扣基础上95折
        参数：
            buy_num: 购买数量
    '''
    def get_final_price(self, buy_num: int)->float:
        # 计算原价价格
        origin = self.price * buy_num
        # 优惠价格
        final = origin * BaseDrink.shop_discount * FruitTea.fruit_tea_discount # 实现全场折扣基础上额外95折
        return round(final, 2) # round 是保留2位小数的意思
    
    def print_ticket(self, buy_num: int)-> str:
        '''
            打印小票
        '''
        # 获取最终价格
        final = self.get_final_price(buy_num)
        # 获取商品名称
        name = self.name
        # 获取商品数量
        num = buy_num
        # 获取商品单价格
        price = self.price
        print( f"======================小票=====================\n" \
               f" 商品名称:            {name}\n" \
               f" 单价:{self.price}*全场折扣:{BaseDrink.shop_discount}*果茶优惠折扣:{FruitTea.fruit_tea_discount}*杯数:{buy_num}\n" \
               f" 商品总价:{final}\n" \
               f" 优惠信息:全场5折，果茶额外95折\n" \
               f"===============================================\n"
        )
# if __name__ == "__main__":
#     # 创建对象
#     fruit_tea = Fruit_tea("鲜果茶", 5.5)
#     # 测试打印小票
#     fruit_tea.sell(2)
#     # 测试获取最终价格
#     print(fruit_tea.get_final_price(2))