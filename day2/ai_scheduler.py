from datetime import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# 父模型
class AIModel:
    # 构造方法
    # 参数，模型名称，模型类型
    def __init__(self, name, model_type):
        
        self.name = name
        self.model_type = model_type

    # 抽象方法，子类必须实现
    # 参数：输入数据
    def predict(self, input_data):
        raise NotImplementedError("子类必须实现predict推理方法")

# 文本生成模型
class TextModel(AIModel):
    # 构造方法
    # 参数，模型名称，模型类型
    def __init__(self, name, model_type):
        super().__init__(name, model_type)

    # 推理方法
    # 参数，
    def predict(self, input_data):
        # 开始计算推理时间
        start = datetime.now()
        time.sleep(1)
        # 结束计算推理时间
        end = datetime.now()
        # 计算消耗时间
        cost_time = (end - start).total_seconds()
        # 返回结果字典
        return {
            "模型名称": self.name,
            "推理结果": f"生成文本：{input_data}",
            "任务耗时": f"{cost_time:.2f}秒"
        }

# 图像生成模型
class ImageModel(AIModel):
    # 构造方法
    # 参数，模型名称，模型类型
    def __init__(self, name, model_type):
        super().__init__(name, model_type)

    # 推理方法
    # 参数，
    def predict(self, input_data):
        # 开始计算推理时间
        start = datetime.now()
        time.sleep(2)
        # 结束计算推理时间
        end = datetime.now()
        # 计算消耗时间
        cost_time = (end - start).total_seconds()
        # 返回结果字典
        return {
            "模型名称": self.name,
            "推理结果": f"生成图像：{input_data}",
            "任务耗时": f"{cost_time:.2f}秒"
        }

# 新增语音生成模型 AudioModel
# 构造方法
# 参数，模型名称，模型类型
class AudioModel(AIModel):
    def __init__(self, name, model_type):
        super().__init__(name, model_type)

    # 推理方法
    # 参数，
    def predict(self, input_data):
        # 开始计算推理时间
        start = datetime.now()
        time.sleep(1.5)
        # 结束计算推理时间
        end = datetime.now()
        # 计算消耗时间
        cost_time = (end - start).total_seconds()
        # 返回结果字典
        return {
            "模型名称": self.name,
            "推理结果": f"生成语音：{input_data}",
            "任务耗时": f"{cost_time:.2f}秒"
        }

# 静态工具类，调度器
class Scheduler:
    # 静态类属性：全局任务记录表、线程锁
    records = []
    lock = threading.Lock()

    # 静态方法：清空任务记录表
    @staticmethod
    def clear_records():
        Scheduler.records.clear()

    # 静态方法：执行单个任务，
    # 参数，元组（用户名，任务描述，模型实例）
    @staticmethod
    def _run_one(user, task_prompt, model):
        # 将任务送给模型推理，返回结果字典
        result = model.predict(task_prompt)
        # 在结果字典中添加用户字段
        result["用户名"] = user
        # 加锁并且添加任务记录
        with Scheduler.lock: # 利用with实现自动加锁解锁
            Scheduler.records.append(result)

    # 静态方法：串行执行全部任务
    # 参数，一个列表，列表内全是元组，每个元组都是一个任务（用户名，任务描述，模型实例）
    @staticmethod
    def run_serial(task_tuple_list):
        # 把每个任务都单个提取出来并且单个执行
        for task_info in task_tuple_list:
            username, prompt, model = task_info
            Scheduler._run_one(username, prompt, model)
    # 静态方法：多线程并发执行全部任务
    # 参数，一个列表，列表内全是元组，每个元组都是一个任务（用户名，任务描述，模型实例）
    @staticmethod
    def run_concurrent(task_tuple_list):
        threads = [] # 创建线程列表
        for task_info in task_tuple_list:
            username, prompt, model = task_info # 提取出任务中的每个信息
            t = threading.Thread(target=Scheduler._run_one, args=(username, prompt, model)) # 创建线程
            threads.append(t) # 添加到线程列表
        # 启动所有线程
        for t in threads:
            t.start()
        # 阻塞等待全部线程结束
        for t in threads:
            t.join()

    # 新增静态方法：基于ThreadPoolExecutor线程池实现并发任务执行
    # 参数，一个列表，列表内全是元组，每个元组都是一个任务（用户名，任务描述，模型实例）
    '''
        为什么要使用线程池？
        线程复用：线程创建后不会销毁，做完一个任务立刻接下一个任务，省去反复创建销毁的开销；
        控制并发上限：可设置 max_workers，限制同时运行的线程数量，防止并发爆炸；
        统一任务管理：所有任务提交到池子，自动分发、自动等待全部完成；
        自带异常捕获机制：通过 future.result() 能拿到任务内部抛出的异常。
    '''
    @staticmethod
    def run_thread_pool(task_tuple_list):
        # 创建线程池，最大线程数等于任务总数
        with ThreadPoolExecutor(max_workers=len(task_tuple_list)) as executor:
            task_futures = [] # 创建任务列表
            for task_info in task_tuple_list:
                username, prompt, model = task_info # 提取出任务中的每个信息
                # 提交任务到线程池
                future = executor.submit(Scheduler._run_one, username, prompt, model)
                task_futures.append(future)
            # 阻塞等待线程池内所有任务执行完成
            for future in task_futures:
                future.result()

    # 静态方法：格式化打印所有任务执行明细，含用户名字段
    @staticmethod
    def report():
        print("任务执行明细：")
        for item in Scheduler.records:
            print(
                f"用户：{item['用户名']} | 模型：{item['模型名称']} | 输出：{item['推理结果']} | 耗时：{item['任务耗时']}"
            )

    # 新增静态方法：将性能对比报表写入report.txt文件
    # 参数：系统当前时间、串行总耗时、并发总耗时、节省时长、加速比
    @staticmethod
    def write_performance_report(now_time, serial_total, concurrent_total, save_time, speedup):
        # 以追加写入模式打开report.txt，不存在则自动创建
        with open(".\\report.txt", "a", encoding="utf-8") as f:
            f.write("\n================性能对比报表===============\n")
            f.write(f"当前系统时间：{now_time}\n")
            f.write(f"串行全局总耗时：{serial_total:.2f} 秒\n")
            f.write(f"并发全局总耗时：{concurrent_total:.2f} 秒\n")
            f.write(f"并发节省时长：{save_time:.2f} 秒\n")
            f.write(f"并发加速比：{speedup:.2f} 倍\n")
            f.write("============================================\n")

# 主程序
# 1. 创建文本、图像模型，构造≥6 条混合用户任务
# 2. 分别运行串行、并发，用 datetime 统计全局总耗时
# 3. 输出对比报表：串行总耗时、并发总耗时、节省时长、加速比、当前系统时间
def main():
    # 初始化模型
    text_model = TextModel("GPT", "text")
    image_model = ImageModel("NanoBanana", "image")
    # 新增语音模型实例
    audio_model = AudioModel("VoiceTTS", "audio")

    # 构造元组任务列表：(用户名, 任务描述, 对应模型实例)
    # 扩充语音任务，总任务数量大于6条
    tasks = [
        ("小明", "生成一首诗", text_model),
        ("小红", "生成一段名人名言", text_model),
        ("小李", "生成一段小说结尾", text_model),
        ("小张", "生成一张图片", image_model),
        ("小王", "生成一副田园画", image_model),
        ("小赵", "生成一张苹果的图像", image_model),
        ("小周", "朗读一篇散文", audio_model),
        ("小陈", "生成短视频配音", audio_model),
        ("小吴", "制作歌曲人声", audio_model)
    ]
    # 串行执行所有任务
    print("======串行执行所有任务=====")
    Scheduler.clear_records()
    start_serial = datetime.now()
    Scheduler.run_serial(tasks)
    end_serial = datetime.now()
    serial_total = (end_serial - start_serial).total_seconds()
    Scheduler.report()

    # 并发执行所有任务（原生Thread多线程）
    print("======并发执行所有任务=====")
    Scheduler.clear_records()
    start_concurrent = datetime.now()
    Scheduler.run_concurrent(tasks)
    end_conc = datetime.now()
    concurrent_total = (end_conc - start_concurrent).total_seconds()
    Scheduler.report()

    # 线程池执行所有任务
    print("======线程池ThreadPoolExecutor执行所有任务=====")
    Scheduler.clear_records()
    start_pool = datetime.now()
    Scheduler.run_thread_pool(tasks)
    end_pool = datetime.now()
    pool_total = (end_pool - start_pool).total_seconds()
    Scheduler.report()

    # 性能对比
    save_time = serial_total - concurrent_total # 计算节省时间
    try:
        speedup = serial_total / concurrent_total  # 计算加速比
    except Exception as e:
        print(f"计算出错，并发执行的时间为：{concurrent_total}, 串行执行的时间为：{serial_total}")
        speedup = 0 # 加速比为0
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n================性能对比报表================")
    print(f"当前系统时间：{now_time}")
    print(f"串行全局总耗时：{serial_total:.2f} 秒")
    print(f"并发全局总耗时：{concurrent_total:.2f} 秒")
    print(f"线程池全局总耗时：{pool_total:.2f} 秒")
    print(f"并发节省时长：{save_time:.2f} 秒")
    print(f"并发加速比：{speedup:.2f} 倍")
    print("============================================")

    # 调用静态方法，将性能报表写入report.txt文件
    Scheduler.write_performance_report(now_time, serial_total, concurrent_total, save_time, speedup)
    print("\n性能报表已写入 report.txt 文件！")


if __name__ == "__main__":
    main()