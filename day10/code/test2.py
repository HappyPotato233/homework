import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
tips = sns.load_dataset("tips")       # 餐饮小费数据
iris = sns.load_dataset("iris")       # 鸢尾花数据

# 创建输出目录
os.makedirs(r"image", exist_ok=True)

# 设置整体风格
sns.set_theme(style="whitegrid") # 可选：darkgrid, whitegrid, dark, ticks
# 设置中文字体（Windows 常用）
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示为方块的问题
# 创建画布和子图
fig, axes = plt.subplots(3, 3, figsize=(14, 10)) 
fig.tight_layout(h_pad=2.5, w_pad=1.5) # 调整子图间距
# =================绘制小费金额 (`tip`) 的分布直方图，要求包含核密度曲线，分箱数为 30====================
sns.histplot(data=tips, x="tip", bins=30, alpha=0.6, color="red", kde=True, ax=axes[0,0])
axes[0,0].set_title("小费金额分布直方图")
axes[0,0].set_xlabel("小费金额")
axes[0,0].set_ylabel("人数")
# =================绘制总账单 (`total_bill`) 的核密度图，按是否吸烟 (`smoker`) 分组对比====================
sns.kdeplot(data=tips, x="total_bill", hue="smoker", ax=axes[0,1], linewidth=2)
axes[0,1].set_title("总账单核密度图")
axes[0,1].set_xlabel("总账单金额")
axes[0,1].set_ylabel("核密度")
# =================绘制箱线图，X 轴为用餐时段 (`time`)，Y 轴为小费 (`tip`)，按性别 (`sex`) 分组颜色。
sns.boxplot(data=tips, x="time",y="tip", hue="sex", ax=axes[0,2], gap=0.2) # gap是箱间距
legend = axes[0,2].legend() # 获取图例对象
legend.get_frame().set_visible(False) # 隐藏图例框
axes[0,2].set_title("小费金额箱线图")
axes[0,2].set_xlabel("用餐时段")
axes[0,2].set_ylabel("小费金额")
# =================绘制小提琴图，X 轴为星期 (`day`)，Y 轴为小费 (`tip`)，按时段 (`time`) 分组并分割显示 (`split=True`)===============
sns.violinplot(data=tips, x="day", y="tip", hue="time", split=True, ax=axes[1,0])
axes[1,0].set_title("星期小费金额小提琴图")
axes[1,0].set_xlabel("星期")
axes[1,0].set_ylabel("小费金额")
# ================绘制柱状图，X 轴为星期 (`day`)，Y 轴为小费 (`tip`)，**不显示误差线**===============
sns.barplot(data=tips, x="day", y="tip", errorbar=None, ax=axes[1,1])
axes[1,1].set_title("星期小费金额柱状图")
axes[1,1].set_xlabel("星期")
axes[1,1].set_ylabel("小费金额")
# ================计算数值列的相关系数，绘制热力图，要求显示数值 (`annot=True`)，配色使用 `coolwarm`===============
corr = tips.select_dtypes(include=[np.number]).corr() # 先选取数值列，再根据数值列计算相关矩阵
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=axes[1,2])
axes[1,2].set_title("小费金额相关系数热力图")
axes[1,2].set_xlabel("小费金额")
axes[1,2].set_ylabel("总账单金额")
# ================绘制回归图，X 轴为账单，Y 轴为小费。要求按吸烟情况 (`smoker`) 分别画出两条回归线进行对比===============
# 选出只有吸烟情况的的表
smoker_tips = tips[tips["smoker"] != "No"]
no_smoker_tips = tips[tips["smoker"] == "No"]
sns.regplot(data=smoker_tips, x="total_bill", y="tip", ax=axes[2,0], color='red')
sns.regplot(data=no_smoker_tips, x="total_bill", y="tip", ax=axes[2,0], color='blue')
# 回归线图不提供分类属性，直接使用legend对该子图添加也只会读取前两个图像属性那就是吸烟者回归线图的数据点和拟合线。因此需要自己构造图例
legend_items = [
    Line2D([], [], marker='o', color='red', label='吸烟'),
    Line2D([], [], marker='o', color='blue', label='不吸烟'),
]
axes[2,0].legend(handles=legend_items, fontsize=9)
axes[2,0].set_title("账单金额与小费金额回归图")
axes[2,0].set_xlabel("账单金额")
axes[2,0].set_ylabel("小费金额")
# 隐藏多余的子图
axes[2,1].axis("off")
axes[2,2].axis("off")
fig.savefig("image/餐饮小费数据可视化图表.png", dpi=300)
# ================使用尾花数据 (`iris`)，选取 `sepal_length`, `sepal_width`, `petal_length` 和 `species` 字段，绘制配对散点矩阵 (`pairplot`)。===============
pairplot = sns.pairplot(data=iris,hue="species", height=2)
pairplot.fig.suptitle("鸢尾花数据配对散点矩阵", fontsize=16)
pairplot.fig.savefig("image/鸢尾花数据配对散点矩阵.png", dpi=300)

# ==================== 创建一个 2 行 1 列的子图画布 ====================
'''
    上图：账单密度的核密度图。下图：男女平均小费的柱状图。
'''
fig, axes = plt.subplots(2, 1, figsize=(10, 8))
fig.tight_layout(h_pad=2.5, w_pad=1) # 调整子图间距
sns.kdeplot(data=tips, x="total_bill", ax=axes[0])
axes[0].set_title("总账单核密度图")
axes[0].set_xlabel("总账单金额")
axes[0].set_ylabel("核密度")
sns.barplot(data=tips, x="sex", y="tip", ax=axes[1])
axes[1].set_title("男女平均小费金额柱状图")
axes[1].set_xlabel("性别")
axes[1].set_ylabel("小费金额")
fig.savefig("image/账单密度与性别小费对比图.png", dpi=300)
# ==================== 创建一个 1 行 2 列的子图画布 ====================
'''
* 左图：男女消费金额分布的小提琴图。
* 右图：一周每日平均消费的柱状图。
* 设置总标题为"餐饮消费综合可视化图表"。
'''
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
fig.tight_layout(w_pad=2.5) # 调整子图间距
sns.violinplot(
    data=tips,
    # x填固定常量，全部数据挤在同一个位置，实现单小提琴
    x=[0] * len(tips),
    y="total_bill",
    hue="sex",
    split=True,        # 左右对半分割
    hue_order=["Female", "Male"], # 顺序：左边女，右边男
    ax=axes[0]
)
axes[0].set_title("男女消费金额分布的小提琴图")
axes[0].set_xlabel("性别")
axes[0].set_ylabel("消费金额")
axes[0].set_xticks([-0.1, 0.1], labels=["男", "女"])
sns.barplot(data=tips, x="day", y="total_bill", errorbar=None, ax=axes[1])
axes[1].set_title("一周每日平均消费的柱状图")
axes[1].set_xlabel("星期")
axes[1].set_ylabel("消费金额")
axes[1].set_xticks([0, 1, 2, 3, 4, 5, 6], labels=["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
fig.savefig("image/餐饮消费数据可视化图表.png", dpi=300)
plt.show()