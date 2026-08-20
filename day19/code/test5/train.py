# -*- coding: utf-8 -*-
"""
YOLO 训练脚本
训练数据：data/train/
测试数据：data/test/
权重保存：pt/
测试报告：report/reportN/
"""

import os
import time
import json
import shutil
import csv
from datetime import timedelta
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_YAML = os.path.join(BASE_DIR, "data", "data.yaml")
PT_DIR = os.path.join(BASE_DIR, "pt")
REPORT_DIR = os.path.join(BASE_DIR, "report")
os.makedirs(PT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# 预训练模型（使用本地权重，无需下载）
PRETRAINED = os.path.join(BASE_DIR, "yolo11n.pt")

# 训练配置
TRAIN_CONFIG = {
    "epochs": 100,
    "batch": 4,       # 显存/RAM 不足可改为 2
    "imgsz": 640,
    "device": "0",       # GPU: "0", CPU: "cpu"
    "workers": 2,        # 减少内存占用
    "patience": 50,      # 早停轮数
    "optimizer": "AdamW",
    "lr0": 0.0005,
    "lrf": 0.01,
    "project": PT_DIR,
    "name": "exp",
    "exist_ok": True,
    "save": True,
    "save_period": 10,
    "plots": True,
    "verbose": True,
}


def get_next_report_dir():
    """获取下一个报告目录 report/report1, report/report2, ..."""
    existing = []
    for name in os.listdir(REPORT_DIR):
        if name.startswith("report"):
            try:
                num = int(name.replace("report", ""))
                existing.append(num)
            except ValueError:
                continue
    next_num = max(existing) + 1 if existing else 1
    report_path = os.path.join(REPORT_DIR, f"report{next_num}")
    os.makedirs(report_path, exist_ok=True)
    return report_path, next_num


def generate_report(report_path, report_num, train_time, metrics=None):
    """生成测试报告：超参、训练时间、评估指标、可视化图像"""
    run_dir = os.path.join(PT_DIR, "exp")

    # 1. 复制 YOLO 自动生成的可视化图
    plot_files = [
        "results.png", "confusion_matrix.png", "confusion_matrix_normalized.png",
        "PR_curve.png", "F1_curve.png", "P_curve.png", "R_curve.png",
        "labels.jpg", "labels_correlogram.jpg",
        "train_batch0.jpg", "train_batch1.jpg", "train_batch2.jpg",
        "val_batch0_pred.jpg", "val_batch1_pred.jpg",
    ]
    for fname in plot_files:
        src = os.path.join(run_dir, fname)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(report_path, fname))

    # 2. 从 results.csv 绘制 loss 和学习率曲线
    results_csv = os.path.join(run_dir, "results.csv")
    loss_plot_path = os.path.join(report_path, "loss_curve.png")
    lr_plot_path = os.path.join(report_path, "lr_curve.png")

    if os.path.exists(results_csv):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            epochs, lr_list = [], []
            box_loss, cls_loss, dfl_loss = [], [], []
            train_box_loss, train_cls_loss, train_dfl_loss = [], [], []

            with open(results_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # YOLO results.csv 列名可能带空格
                    def get(key):
                        for k in row:
                            if k.strip() == key:
                                return float(row[k])
                        return None

                    epochs.append(int(get("epoch")))
                    lr_list.append(get("lr") or get("lr/pg0") or 0)

                    # 验证 loss
                    box_loss.append(get("val/box_loss") or 0)
                    cls_loss.append(get("val/cls_loss") or 0)
                    dfl_loss.append(get("val/dfl_loss") or 0)
                    # 训练 loss
                    train_box_loss.append(get("train/box_loss") or 0)
                    train_cls_loss.append(get("train/cls_loss") or 0)
                    train_dfl_loss.append(get("train/dfl_loss") or 0)

            # Loss 曲线
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            for ax, title, train_vals, val_vals in [
                (axes[0], "Box Loss", train_box_loss, box_loss),
                (axes[1], "Cls Loss", train_cls_loss, cls_loss),
                (axes[2], "DFL Loss", train_dfl_loss, dfl_loss),
            ]:
                ax.plot(epochs, train_vals, label="train", color="blue")
                ax.plot(epochs, val_vals, label="val", color="orange")
                ax.set_title(title)
                ax.set_xlabel("Epoch")
                ax.set_ylabel("Loss")
                ax.legend()
                ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(loss_plot_path, dpi=150)
            plt.close()
            print(f"  Loss 曲线已保存: {loss_plot_path}")

            # 学习率曲线
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(epochs, lr_list, color="green", linewidth=2)
            ax.set_title("Learning Rate")
            ax.set_xlabel("Epoch")
            ax.set_ylabel("LR")
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(lr_plot_path, dpi=150)
            plt.close()
            print(f"  学习率曲线已保存: {lr_plot_path}")
        except Exception as e:
            print(f"  绘制曲线失败: {e}")

    # 3. 生成报告文件
    report_file = os.path.join(report_path, "report.md")
    train_time_str = str(timedelta(seconds=int(train_time)))

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# YOLO 训练报告 #{report_num}\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 1. 超参数配置\n\n")
        f.write("| 参数 | 值 |\n|------|----|\n")
        f.write(f"| 预训练模型 | {PRETRAINED} |\n")
        f.write(f"| 训练轮数 | {TRAIN_CONFIG['epochs']} |\n")
        f.write(f"| 批大小 | {TRAIN_CONFIG['batch']} |\n")
        f.write(f"| 图像尺寸 | {TRAIN_CONFIG['imgsz']} |\n")
        f.write(f"| 设备 | {TRAIN_CONFIG['device']} |\n")
        f.write(f"| 优化器 | {TRAIN_CONFIG['optimizer']} |\n")
        f.write(f"| 初始学习率 | {TRAIN_CONFIG['lr0']} |\n")
        f.write(f"| 最终学习率比例 | {TRAIN_CONFIG['lrf']} |\n")
        f.write(f"| 早停轮数 | {TRAIN_CONFIG['patience']} |\n")
        f.write(f"| 数据加载线程 | {TRAIN_CONFIG['workers']} |\n\n")

        f.write("## 2. 训练时间\n\n")
        f.write(f"| 项目 | 值 |\n|------|----|\n")
        f.write(f"| 总耗时 | {train_time_str} |\n\n")

        f.write("## 3. 评估指标\n\n")
        if metrics:
            f.write("### 总体指标\n\n")
            f.write("| 指标 | 值 |\n|------|----|\n")
            f.write(f"| mAP50-95 | {metrics.box.map:.4f} |\n")
            f.write(f"| mAP50 | {metrics.box.map50:.4f} |\n")
            f.write(f"| mAP75 | {metrics.box.map75:.4f} |\n")
            f.write(f"| 精确率 (P) | {metrics.box.mp:.4f} |\n")
            f.write(f"| 召回率 (R) | {metrics.box.mr:.4f} |\n\n")

            f.write("### 各类别指标\n\n")
            f.write("| 类别 | 精确率 | 召回率 | mAP50 |\n")
            f.write("|------|--------|--------|-------|\n")
            num_classes = len(metrics.box.p)
            for i, name in metrics.names.items():
                if i < num_classes:
                    f.write(f"| {name} | {metrics.box.p[i]:.4f} | {metrics.box.r[i]:.4f} | {metrics.box.ap50[i]:.4f} |\n")
                else:
                    f.write(f"| {name} | N/A | N/A | N/A |\n")
        else:
            f.write("（未执行验证，无评估指标）\n")
        f.write("\n")

        f.write("## 4. 可视化图像\n\n")
        f.write("### 训练曲线\n\n")
        f.write("- ![Loss 曲线](loss_curve.png)\n")
        f.write("- ![学习率曲线](lr_curve.png)\n")
        f.write("- ![YOLO 训练总览](results.png)\n\n")
        f.write("### 评估图像\n\n")
        f.write("- ![混淆矩阵](confusion_matrix.png)\n")
        f.write("- ![归一化混淆矩阵](confusion_matrix_normalized.png)\n")
        f.write("- ![PR 曲线](PR_curve.png)\n")
        f.write("- ![F1 曲线](F1_curve.png)\n")
        f.write("- ![P 曲线](P_curve.png)\n")
        f.write("- ![R 曲线](R_curve.png)\n\n")
        f.write("### 训练样本\n\n")
        f.write("- ![训练批次 0](train_batch0.jpg)\n")
        f.write("- ![验证预测 0](val_batch0_pred.jpg)\n")

    print(f"  报告已保存: {report_file}")
    return report_file


def train():
    """训练模型并生成报告"""
    print("=" * 60)
    print("开始训练 YOLO 模型")
    print("=" * 60)

    # 将 data.yaml 中的 path 设为绝对路径
    with open(DATA_YAML, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(DATA_YAML, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip().startswith("path:"):
                f.write(f"path: {BASE_DIR}\n")
            else:
                f.write(line)

    model = YOLO(PRETRAINED)

    print(f"数据集配置: {DATA_YAML}")
    print(f"权重保存到: {PT_DIR}")
    print("-" * 60)

    # 记录训练开始时间
    start_time = time.time()

    model.train(data=DATA_YAML, **TRAIN_CONFIG)

    train_time = time.time() - start_time

    # 复制 best.pt 到 pt/ 根目录
    best_pt = os.path.join(PT_DIR, "exp", "weights", "best.pt")
    target_pt = os.path.join(PT_DIR, "best.pt")
    if os.path.exists(best_pt):
        shutil.copy(best_pt, target_pt)
        print(f"\n最佳权重已复制到: {target_pt}")

    print("=" * 60)
    print("训练完成！开始生成报告...")
    print("=" * 60)

    # 验证并获取指标
    metrics = None
    try:
        val_model = YOLO(target_pt)
        metrics = val_model.val(
            data=DATA_YAML,
            imgsz=TRAIN_CONFIG["imgsz"],
            device=TRAIN_CONFIG["device"],
        )
        print(f"mAP50-95: {metrics.box.map:.4f}")
        print(f"mAP50:    {metrics.box.map50:.4f}")
        print(f"精确率:   {metrics.box.mp:.4f}")
        print(f"召回率:   {metrics.box.mr:.4f}")
    except Exception as e:
        print(f"验证失败: {e}")

    # 生成报告
    report_path, report_num = get_next_report_dir()
    print(f"\n生成第 {report_num} 次测试报告...")
    generate_report(report_path, report_num, train_time, metrics)
    print(f"\n报告目录: {report_path}")

    print("=" * 60)
    print("全部完成！")
    print("=" * 60)
    return model


def validate(model_path=None):
    """验证模型"""
    if model_path is None:
        model_path = os.path.join(PT_DIR, "best.pt")

    print("=" * 60)
    print("验证模型性能")
    print("=" * 60)

    model = YOLO(model_path)
    metrics = model.val(
        data=DATA_YAML,
        imgsz=TRAIN_CONFIG["imgsz"],
        device=TRAIN_CONFIG["device"],
    )

    print(f"\nmAP50-95: {metrics.box.map:.4f}")
    print(f"mAP50:    {metrics.box.map50:.4f}")
    print(f"精确率:   {metrics.box.mp:.4f}")
    print(f"召回率:   {metrics.box.mr:.4f}")

    # 各类别指标
    print("\n各类别详细指标:")
    for i, name in model.names.items():
        print(f"  {name}: P={metrics.box.p[i]:.4f} R={metrics.box.r[i]:.4f} mAP50={metrics.box.ap50[i]:.4f}")

    return metrics


def predict(image_path, model_path=None):
    """推理测试"""
    if model_path is None:
        model_path = os.path.join(PT_DIR, "best.pt")

    print("=" * 60)
    print("模型推理")
    print("=" * 60)
    print(f"模型: {model_path}")
    print(f"图片: {image_path}")

    model = YOLO(model_path)
    results = model.predict(
        source=image_path,
        save=True,
        project=os.path.join(BASE_DIR, "output"),
        name="pred",
        exist_ok=True,
    )

    for result in results:
        if result.boxes is not None:
            print(f"\n检测到 {len(result.boxes)} 个目标:")
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                print(f"  {model.names[cls]}: {conf:.2f} ({x1:.0f},{y1:.0f}-{x2:.0f},{y2:.0f})")
        print(f"结果已保存到: {result.save_dir}")

    return results


if __name__ == "__main__":
    print("YOLO 训练脚本")
    print("1. 训练模型（训练+验证+生成报告）")
    print("2. 验证模型")
    print("3. 推理测试")

    choice = input("\n请输入选项 (1-3): ").strip()

    if choice == "1":
        train()
    elif choice == "2":
        validate()
    elif choice == "3":
        image_path = input("图片路径: ").strip()
        if os.path.exists(image_path):
            predict(image_path)
        else:
            print(f"图片不存在: {image_path}")
    else:
        print("无效选项")
