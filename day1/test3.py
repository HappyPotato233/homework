import time
from datetime import datetime
import threading

class AIModel:
    # 构造方法
    def __init__(self, name, model_type):
        self.name = name
        self.model_type = model_type
    # 推理
    def predict(self, input_data):
        raise NotImplementedError("子类必须实现predict方法")
        print(f"{self.name}模型收到输入：{input_data}，但具体推理逻辑由子类实现")
        return "父类默认结果"

class TextModel(AIModel):
    # 构造方法
    def __init__(self, name, model_type):
        super().__init__(name,model_type)
    
    # 重写方法
    def predict(self, input_data):
        start = datetime.now()
        print(f"文本模型{self.name}正在生成文本...")
        time.sleep(1)
        end = datetime.now()
        return f"{input_data}的生成结果"

class ImageModel(AIModel):
    # 构造方法
    def __init__(self, name, model_type):
        super().__init__(name,model_type)
    
    # 重写方法
    def predict(self, input_data):
        start = datetime.now()
        print(f"图像模型{self.name}正在识别图像...")
        time.sleep(1)
        end = datetime.now()
        return f"{input_data}的生成结果"

# 定义记录列表
records = []
# 定义锁
lock = threading.Lock()


def user_request(user_name, model, input_data):
    start = datetime.now()
    result = model.predict(input_data)
    end = datetime.now()
    cost = (end-start).total_seconds()

    lock.acquire()
    records.append({
        "user":user_name,
        "model":model.name,
        "cost":cost,
        "result":result
    })
    lock.release()

text_model = TextModel("GPT小助手","文本生成")
image_model = ImageModel("NanoBanana","图像生成")

total_start = datetime.now()
threads = [
    threading.Thread(target=user_request,args=("用户A",text_model,"写首诗")),
    threading.Thread(target=user_request,args=("用户B",text_model,"写文案")),
    threading.Thread(target=user_request,args=("用户C",image_model,"生成苹果")),
    threading.Thread(target=user_request,args=("用户D",image_model,"生成香蕉"))
    ]

for t in threads:
    t.start()
for t in threads:
    t.join()
total_end = datetime.now()

print("\n")
for r in records:
    print(f"{r['user']}->{r['model']},耗时:[{r['cost']}]秒,结果:[{r['result']}]")

print(f"\n总并发耗时:[{(total_end-total_start).total_seconds():.2f}]秒")