import sys
import os
#
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from goods.base_drink import BaseDrink

class Coffee(BaseDrink):
    # 类属性
    # 咖啡折扣
    coffee_discount = 0.88
    def __init__(self, name: str, price: float):
        super().__init__(name, price)
    
    def get_final_price(self, buy_num: int)->float:
        '''
            计算咖啡的最终价格
        '''
        origin = self.price * buy_num
        final = origin * self.shop_discount * self.coffee_discount
        return round(final, 2) # round 是保留2位小数的意思
    
        