import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from shop_tools import check_positive

class BaseDrink(ABC):
    """
    抽象类，所有饮料的基类
    """
    shop_discount = 1.0
    # 构造函数
    def __init__(self, name: str, price: float):
        '''
            构造函数
            参数：
                name: 饮料名称
                price: 饮料价格
        '''
        self.name = name
        self.price = price
        
        # 私有库存 指明外部不能直接访问
        self.__stock = 50

    # ========1.实例方法=========
    # 获取库存数量
    def get_stock(self)-> int:
        '''
            获取库存数量
            返回：
                库存数量
        '''
        return self.__stock
    # 获取最终价格
    def sell(self,num: int)-> str:
        '''
            卖商品
            参数：
                num: 卖出数量
            返回：
                实际卖出数量
        '''
        if not check_positive(num) or num > self.__stock:
            raise ValueError("数量非法或库存不足")
        self.__stock -= num
        return f"售出{num}杯{self.name},剩余{self.__stock}杯"
    def print_ticket(self, buy_num: int)-> str:
        '''
            打印票据
            返回：
                票据信息
        '''
        total = self.get_final_price(buy_num)
        return f"{self.name} {self.price}元/杯"

    # ========2.类方法========
    @classmethod
    def set_shop_discount(cls,discount)-> float:
        '''
            设置当前折扣
            返回：
                折扣
        '''
        # 检测输入折扣是否合法
        if not check_positive(discount):
            raise ValueError("折扣非法")
        cls.shop_discount = discount
        return cls.shop_discount
    # ========3.静态方法========
    @staticmethod
    def check_drink_name(name: str)-> bool:
        '''
            检查输入的饮料名称是否合法
            参数：
                name: 饮料名称
            返回：
                True/False
        '''
        if not name or name.isspace():
            raise ValueError("名称非法")
        return name
    # ========4.抽象方法========
    @abstractmethod
    def get_final_price(self, buy_num: int)-> float:
        '''
            获取最终价格
            返回：
                最终价格
        '''
        pass

if __name__ == "__main__":
    print("===== 测试静态方法 check_drink_name =====")
    # 正常合法名称
    try:
        res1 = BaseDrink.check_drink_name("珍珠奶茶")
        print(f"合法名称测试1: {res1}, 预期返回字符串")
    except Exception as e:
        print(f"异常：{e}")

    # 全空格名称（预期抛异常）
    try:
        BaseDrink.check_drink_name("   ")
    except ValueError as e:
        print(f"空格名称异常捕获：{e}")

    # 空字符串（预期抛异常）
    try:
        BaseDrink.check_drink_name("")
    except ValueError as e:
        print(f"空名称异常捕获：{e}")