# YOLO 训练报告 #3

生成时间: 2026-08-19 21:59:04

## 1. 超参数配置

| 参数 | 值 |
|------|----|
| 预训练模型 | d:\实习\day19\code\test5\yolo11n.pt |
| 训练轮数 | 100 |
| 批大小 | 4 |
| 图像尺寸 | 640 |
| 设备 | 0 |
| 优化器 | AdamW |
| 初始学习率 | 0.0005 |
| 最终学习率比例 | 0.01 |
| 早停轮数 | 50 |
| 数据加载线程 | 2 |

## 2. 训练时间

| 项目 | 值 |
|------|----|
| 总耗时 | 0:11:26 |

## 3. 评估指标

### 总体指标

| 指标 | 值 |
|------|----|
| mAP50-95 | 0.0265 |
| mAP50 | 0.0661 |
| mAP75 | 0.0228 |
| 精确率 (P) | 0.0879 |
| 召回率 (R) | 0.1047 |

### 各类别指标

| 类别 | 精确率 | 召回率 | mAP50 |
|------|--------|--------|-------|
| anti_collision_bucket (防撞桶) | 0.0000 | 0.0000 | 0.0000 |
| anti_collision_pier (防撞墩) | 0.0000 | 0.0000 | 0.0000 |
| anti_glare_board (防眩板) | 0.0000 | 0.0000 | 0.0000 |
| bridge_bearing (桥梁支座) | 0.0000 | 0.0000 | 0.0000 |
| central_plant (中央植物) | 0.1300 | 0.4133 | 0.0630 |
| culvert (涵洞) | 0.4125 | 0.6586 | 0.5310 |
| drainage_ditch (排水沟) | 0.0000 | 0.0000 | 0.0000 |
| emergency_phone (紧急电话) | 0.0000 | 0.0000 | 0.0000 |
| etc_antenna (ETC天线) | 0.1234 | 0.7661 | 0.6463 |
| fire_box (消防箱) | 0.0000 | 0.0000 | 0.0000 |
| fire_pool (消防水池) | 1.0000 | 0.0182 | 0.0150 |
| gore_area_plant (三角区植物) | 0.0000 | 0.0000 | 0.0000 |
| lane_indicator (车道指示器) | 0.0001 | 0.0147 | 0.0000 |
| lane_sign (车道标志) | 0.0000 | 0.0000 | 0.0000 |
| led_screen (LED屏幕) | 0.0000 | 0.0000 | 0.0000 |
| monitoring_equipment (监控设备) | 0.0000 | 0.0000 | 0.0000 |
| parking (停车区) | 0.0039 | 0.1189 | 0.0014 |
| pipeline (管道) | 0.0000 | 0.0000 | 0.0000 |
| road_marking (路面标线) | 0.0000 | 0.0000 | 0.0000 |
| roadside_plant (路侧植物) | N/A | N/A | N/A |
| slope (边坡) | N/A | N/A | N/A |
| sound_barrier (声屏障) | N/A | N/A | N/A |
| toll_bar (收费栏杆) | N/A | N/A | N/A |
| toll_booth (收费亭) | N/A | N/A | N/A |
| toll_display (收费显示屏) | N/A | N/A | N/A |
| truck_scale (卡车地磅) | N/A | N/A | N/A |
| tunnel_body (隧道主体) | N/A | N/A | N/A |
| tunnel_entrance (隧道入口) | N/A | N/A | N/A |
| tunnel_fan (隧道风机) | N/A | N/A | N/A |
| tunnel_lighting (隧道照明) | N/A | N/A | N/A |
| warning_sign (警告标志) | N/A | N/A | N/A |
| wave_guardrail (波形护栏) | N/A | N/A | N/A |
| zhuixingtong (锥形桶) | N/A | N/A | N/A |

## 4. 可视化图像

### 训练曲线

- ![Loss 曲线](loss_curve.png)
- ![学习率曲线](lr_curve.png)
- ![YOLO 训练总览](results.png)

### 评估图像

- ![混淆矩阵](confusion_matrix.png)
- ![归一化混淆矩阵](confusion_matrix_normalized.png)
- ![PR 曲线](PR_curve.png)
- ![F1 曲线](F1_curve.png)
- ![P 曲线](P_curve.png)
- ![R 曲线](R_curve.png)

### 训练样本

- ![训练批次 0](train_batch0.jpg)
- ![验证预测 0](val_batch0_pred.jpg)
