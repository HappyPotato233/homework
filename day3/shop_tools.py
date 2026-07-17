import threading
from concurrent.futures import ThreadPoolExecutor
#全局共享库存（全局变量，所有线程都公用，必须提前定义）
stock_lock = threading.Lock()
global_stock =  {"珍珠奶茶": 50, "杨枝甘露": 30, "芝士葡萄": 40, "美式咖啡": 60}
price = {"珍珠奶茶": 12, "杨枝甘露": 16, "芝士葡萄": 15, "美式咖啡": 10}
# 检查数字是否合法
def check_positive(num)-> bool:
    """
    检查输入的数字是否为正数
    """
    if not isinstance(num, int) and not isinstance(num, float):
        raise TypeError("num必须是数字")
    return num > 0 

# 计算总的价格
def calc_total_price(price: float, num: int):
    # 返回总价
    return f"{price * num}"
# 保存订单
def save_order_with_with(oder_info:str):
    with open("order.txt", "a", encoding="utf-8") as f:
        f.write(oder_info + "\n")
    print("订单保存成功,文件已自动关闭")
# 读取所有订单
def read_all_orders():
    """
    读取所有订单
    """
    with open("order.txt", "r", encoding="utf-8") as f:
        content = f.readlines()
    return content

#输入({"珍珠奶茶": 12, "杨枝甘露": 16, "芝士葡萄": 15, "美式咖啡": 10},14)，返回['珍珠奶茶', '美式咖啡']
def get_cheap_drinks(drink_dict:list, limit:int) -> list:
    """
    获取价格低于等于limit的饮料
    """
    if not isinstance(drink_dict,dict):
        raise TypeError("drink_dict必须是字典类型")
    cheap_data = {name:p for name, p in drink_dict.items() if p <= limit}
    return list(cheap_data.keys())

#输入[("珍珠奶茶", 2, 24), ("杨枝甘露", 1, 16)]，每次返回"饮品：珍珠奶茶,数量：2, 总价：24"和"饮品：杨枝甘露,数量：1, 总价：16"
def order_record_generator(order_list:list):
    for order in order_list:
        yield f"饮品：{order[0]},数量：{order[1]}, 总价：{order[2]}"

# ==================== 多线程库存管理 ====================
def sell_drink_thread_safe(drink_name: str, sell_num: int): # drink_name:饮品名称，sell_num:销售数量
 # 需要将剩余库存信息保存到order.txt文件中
    with stock_lock:
        # 检测饮品名称是否存在于饮品列表中
        if drink_name not in global_stock.keys():
            raise ValueError("没有此商品")
        # 检测库存是否充足
        if sell_num > global_stock[drink_name]:
            raise ValueError("库存不足")
   
        # 扣除库存
        global_stock[drink_name] -= sell_num
        print(f"成功售出{drink_name}，剩余库存：{global_stock[drink_name]}")
        # 保存订单
        save_order_with_with(f"{drink_name},{sell_num},{sell_num * price[drink_name]}")

# 模拟线程操作
def multi_thread_sell():
    threads = []
    # 创建并开启线程
    for i in range(2):
        t = threading.Thread(target=sell_drink_thread_safe, args=('珍珠奶茶',2))
        threads.append(t)
        t.start()
    # 等待所有线程结束
    for t in threads:
        t.join()
    

       
# ==================== 模块测试代码 ====================
# 以下代码仅在直接运行 shop_tools.py 时执行（python shop_tools.py）
# 被其他文件导入时不会执行
if __name__ == "__main__":
    #1.测试文件操作
    # save_order_with_with("珍珠奶茶,2,24")
    # save_order_with_with("杨枝甘露,1,16")
    # orders = read_all_orders()
    # # print(orders)

    # #2.测试列表推导式
    # print(get_cheap_drinks({"珍珠奶茶": 12, "杨枝甘露": 16, "芝士葡萄": 15, "美式咖啡": 10},14))

    # #3.测试生成器
    # for record in order_record_generator([("珍珠奶茶", 2, 24), ("杨枝甘露", 1, 16)]):
    #     print(record)        
    # order_record_generator([("珍珠奶茶", 2, 24), ("杨枝甘露", 1, 16)])


    # 6. 测试线程锁
    print("\n--- 测试6：多线程安全售卖 ---")
    print(f"售卖前珍珠奶茶库存：{global_stock['珍珠奶茶']}")
    print(f"售卖前杨枝甘露库存：{global_stock['杨枝甘露']}")
    print(f"售卖前芝士葡萄库存：{global_stock['芝士葡萄']}")
    print(f"售卖前美式咖啡库存：{global_stock['美式咖啡']}")
    orders = [
        ("珍珠奶茶",2),
        ("杨枝甘露",1),
        ("芝士葡萄",4),
        ("美式咖啡",3)
    ]
    multi_thread_sell(orders)
    print(f"售卖后珍珠奶茶库存：{global_stock['珍珠奶茶']}")
    print(f"售卖后杨枝甘露库存：{global_stock['杨枝甘露']}")
    print(f"售卖后芝士葡萄库存：{global_stock['芝士葡萄']}")
    print(f"售卖后美式咖啡库存：{global_stock['美式咖啡']}")
