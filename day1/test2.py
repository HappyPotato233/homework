import time
from datetime import datetime
import threading

lock = threading.Lock()
# 全局存储结果
records = []
# 模型列表
model_list = ["EA", "育碧", "steam", "potato"]

# 模拟推理函数
def func(model_name, seconds):
    start = datetime.now()
    print(f"{model_name} 开始推理")
    time.sleep(seconds)  # 模拟推理耗时
    end = datetime.now()
    print(f"{model_name} 结束推理")

    cost = (end - start).total_seconds()
    data = {
        "model": model_name,
        "start": start.strftime("%Y年%m月%d日,%H:%M:%S"),
        "end": end.strftime("%Y年%m月%d日,%H:%M:%S"),
        "cost": f"{cost:.2f}"
    }
    lock.acquire()
    records.append(data)
    lock.release()

# 创建并启动线程
threads = []
for model in model_list:
    t = threading.Thread(target=func, args=(model, 1))
    threads.append(t)

for t in threads:
    t.start()

# 等待所有线程执行完毕
for t in threads:
    t.join()
    
# 打印所有结果
print("\n==== 推理记录汇总 ====")
for item in records:
    print(item)