# -*- coding: utf-8 -*-
"""
自动跑 4 次实验，累积改进：每次在上一次基础上再改一个参数
report1 = 基线
report2 = report1 + imgsz 960
report3 = report2 + lr0 0.0005
report4 = report3 + optimizer SGD
report5 = report4 + epochs 200
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import train as T

# 基线配置（与 report1 一致）
BASELINE = {
    "epochs": 100,
    "batch": 4,
    "imgsz": 640,
    "device": "0",
    "workers": 0,
    "patience": 50,
    "optimizer": "AdamW",
    "lr0": 0.001,
    "lrf": 0.01,
    "project": T.PT_DIR,
    "name": "exp",
    "exist_ok": True,
    "save": True,
    "save_period": 10,
    "plots": True,
    "verbose": True,
}

# 累积改进：每步只改一个参数，但保留之前的改动
CHANGES = [
    {"imgsz": 960},          # report2: 提高分辨率
    {"lr0": 0.0005},         # report3: 降低学习率
    {"optimizer": "SGD"},   # report4: 换优化器
    {"epochs": 200},         # report5: 增加训练轮数
]


def run_experiments():
    cumulative_config = dict(BASELINE)

    for i, change in enumerate(CHANGES):
        # 累积应用改动
        cumulative_config.update(change)

        T.TRAIN_CONFIG = dict(cumulative_config)

        print("\n" + "#" * 60)
        print(f"# 实验 report{i+2}: 本轮改动 {change}")
        print(f"# 累积配置: imgsz={cumulative_config['imgsz']}, "
              f"lr0={cumulative_config['lr0']}, "
              f"optimizer={cumulative_config['optimizer']}, "
              f"epochs={cumulative_config['epochs']}")
        print("#" * 60 + "\n")

        T.train()

    print("\n全部 4 次实验完成！")


if __name__ == "__main__":
    run_experiments()
