#离线模式必须在所有 import 之前设置
import os
# os.environ["HF_HUB_OFFLINE"] = "1"        # 禁止 Hub 联网
# os.environ["HF_DATASETS_OFFLINE"] = "1"    # 禁止数据集联网
# os.environ["TRANSFORMERS_OFFLINE"] = "1"   # 兼容旧版标志
# 调用本地缓存  而不是从网络下载
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, DataCollatorWithPadding, TrainerCallback
import evaluate
import numpy as np
import json
import time
from datetime import datetime

#本次迭代标志(每次迭代修改)
ITERATION_NAME = "V3"
#超参数
MODEL_NAME = "bert-base-uncased"
TRAIN_SAMPLE_RATIO = 0.05 # 训练集比例
TEST_SAMPLE_RATIO = 0.05 # 测试集比例
MAX_LENGTH = 128 # 最大输入长度
BATCH_SIZE = 32 # 每次训练的数据数量
EPOCHS = 2 # 训练轮数
LEARNING_RATE = 3e-5 # 学习率
WEIGHT_DECAY = 0.01 # L2正则化系数
WARMUP_RATIO = 0.1 # 线性预热比例
OUTPUT_DIR = "code/Bert/bert_yelp_output"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_FILE = os.path.join(BASE_DIR, "yelp_train.json")
TEST_FILE = os.path.join(BASE_DIR, "yelp_test.json")
RECORD_FILE = os.path.join(BASE_DIR, "模型迭代优化记录.txt")

#1.加载数据集
dataset = load_dataset("json", data_files={"train": TRAIN_FILE})
small_data = dataset["train"].select(range(int(len(dataset["train"]) * TRAIN_SAMPLE_RATIO)))
split_data = small_data.train_test_split(train_size=0.8, seed=42)
dataset["train"] = split_data["train"]
dataset["validation"] = split_data["test"]

print("训练数据量：", len(dataset["train"]))
print("验证数据量：", len(dataset["validation"]))

#2.加载分词器和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2) # 使用二分类模型，输出2个类别


# 3. 数据预处理
def tokenize_fn(examples):
    #yelp 数据是 text 字段,直接分词;label 字段原样保留作为标签
    tokenized = tokenizer(examples["text"], truncation=True, max_length=MAX_LENGTH)
    tokenized["labels"] = examples["label"]
    return tokenized

tokenized_dataset = dataset.map(tokenize_fn, batched=True)

# 4.评估函数
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")
precision_metric = evaluate.load("precision")
recall_metric = evaluate.load("recall")
def compute_metrics(eval_pred):
    #情感分类:对 logits 取 argmax 得到预测类别,再算 accuracy/f1/precision/recall
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=preds, references=labels)["f1"]
    prec = precision_metric.compute(predictions=preds, references=labels, zero_division=0)["precision"]
    rec = recall_metric.compute(predictions=preds, references=labels, zero_division=0)["recall"]
    return {"accuracy": acc, "f1": f1, "precision": prec, "recall": rec}

# 5.训练参数
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    num_train_epochs=EPOCHS,
    eval_strategy="epoch",
    learning_rate=LEARNING_RATE,
    logging_steps=10,
    save_strategy="no",
    weight_decay=WEIGHT_DECAY,
    warmup_ratio=WARMUP_RATIO,
    report_to="none",                  #不启用 tensorboard(避免卡住)
)

# 5.开始训练
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)  #动态填充批次数据

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)
start_time = time.time()
train_result = trainer.train()
elapsed = time.time() - start_time
train_loss = train_result.training_loss if train_result.training_loss else 0.0

# 7.评估验证集
eval_metrics = trainer.evaluate()
print("\n" + "="*50)
print("训练完成")
print("="*50)
print("训练 loss    :", round(train_loss, 6))
print("验证 loss    :", eval_metrics.get("eval_loss", "N/A"))
print("验证 accuracy:", eval_metrics.get("eval_accuracy", "N/A"))
print("验证 f1      :", eval_metrics.get("eval_f1", "N/A"))
print("验证 precision:", eval_metrics.get("eval_precision", "N/A"))
print("验证 recall  :", eval_metrics.get("eval_recall", "N/A"))
print("训练时长     : %.1f 秒 (%.2f 分钟)" % (elapsed, elapsed/60))

#6.写入迭代记录
ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
separator = "=" * 70
block = []
block.append(separator)
block.append("【迭代#%s】 时间: %s" % (ITERATION_NAME, ts))
block.append(separator)
block.append("【超参数】")
block.append("  - 模型名称        : %s" % MODEL_NAME)
block.append("  - 训练采样比例    : %s" % TRAIN_SAMPLE_RATIO)
block.append("  - 测试集比例      : %s" % TEST_SAMPLE_RATIO)
block.append("  - max_length      : %s" % MAX_LENGTH)
block.append("  - batch_size      : %s" % BATCH_SIZE)
block.append("  - epochs          : %s" % EPOCHS)
block.append("  - learning_rate   : %s" % LEARNING_RATE)
block.append("  - weight_decay    : %s" % WEIGHT_DECAY)
block.append("  - warmup_ratio    : %s" % WARMUP_RATIO)
block.append("")
block.append("【训练结果】")
block.append("  - 训练数据量      : %s" % len(dataset["train"]))
block.append("  - 验证数据量      : %s" % len(dataset["validation"]))
block.append("  - 训练总时长      : %.1f 秒 (%.2f 分钟)" % (elapsed, elapsed/60))
block.append("  - 训练平均 loss   : %.6f" % train_loss)
block.append("  - 验证 loss       : %s" % eval_metrics.get("eval_loss", "N/A"))
block.append("  - 验证 accuracy   : %s" % eval_metrics.get("eval_accuracy", "N/A"))
block.append("  - 验证 f1         : %s" % eval_metrics.get("eval_f1", "N/A"))
block.append("  - 验证 precision  : %s" % eval_metrics.get("eval_precision", "N/A"))
block.append("  - 验证 recall     : %s" % eval_metrics.get("eval_recall", "N/A"))
block.append("")
block.append("【备注】")
block.append("  (在此填写本次迭代思路/改动)")
block.append("")
block.append("")
with open(RECORD_FILE, "a", encoding="utf-8") as f:
    f.write("\n".join(block))
print("\n✓ 迭代记录已写入:", RECORD_FILE)