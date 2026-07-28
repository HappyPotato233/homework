'''
练习任务1: 房价预测

**任务描述**: 使用加州房价数据集,完成以下任务:

1. 加载数据并进行探索性分析
2. 进行特征工程(标准化、特征选择)
3. 使用线性回归、决策树、随机森林分别训练模型
4. 比较三种模型的性能(MSE、R²)
5. 输出特征重要性排序
'''
import numpy as np # 数值计算库
import pandas as pd # 数据处理库
import matplotlib.pyplot as plt # 绘图库
import seaborn as sns # 统计可视化库
from sklearn.datasets import fetch_california_housing # 加州房价数据集
from sklearn.model_selection import train_test_split # 数据集划分
from sklearn.preprocessing import StandardScaler # 标准化模型
from sklearn.linear_model import LinearRegression # 线性回归模型
from sklearn.tree import DecisionTreeRegressor # 决策树回归模型
from sklearn.ensemble import RandomForestRegressor # 随机森林回归模型
from sklearn.metrics import mean_squared_error, r2_score # 评估指标：均方误差、R2

plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置中文显示字体
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# ================1. 加载数据===============
housing = fetch_california_housing() # 加载加州房价数据集
df = pd.DataFrame(housing.data, columns=housing.feature_names) # 将特征转换为DataFrame，列名为特征名
df['MedHouseVal'] = housing.target # 添加目标变量（房价中位数）

# 特征数据集
X = df.loc[:, df.columns != "MedHouseVal"] # 选取除目标变量外的所有列作为特征
# 标签数据集
y = df['MedHouseVal'] # 目标变量：房价中位数

# ================2. 数据探索性分析===============
# 绘制热力图
plt.figure(figsize=(10, 8))
corr = df.corr() # 计算各特征之间的相关系数矩阵
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f') # annot=True显示数值，cmap配色方案，fmt保留两位小数
plt.title('特征相关性热力图')
plt.tight_layout() # 自动调整子图间距

# ================3. 特征工程（标准化、特征选择）===============
# 划分训练集（特征训练集、标签训练集），测试集（特征测试集、标签测试集）
# X：特征数据集，y：标签数据集，test_size：测试集占比，random_state：随机种子保证可复现
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# X_train：特征训练集，y_train：标签训练集，X_test：特征测试集，y_test：标签测试集

# 标准化（线性回归对特征尺度敏感，决策树和随机森林不受影响，但统一处理便于对比）
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train) # 对训练集拟合标准化器并转换
X_test_scaled = scaler.transform(X_test) # 为什么不是fit_transform？因为测试集应使用训练集的统计量进行标准化，避免数据泄露

# ====================== 4.初始化并训练三类模型 ======================
models = {
    "线性回归": LinearRegression(), # 线性回归模型
    "决策树": DecisionTreeRegressor(random_state=42), # 决策树回归模型
    "随机森林": RandomForestRegressor(n_estimators=100, random_state=42), # 随机森林回归模型，n_estimators树的数量
}

results = {} # 存储各模型评估结果
plt.figure(figsize=(12, 8)) # 创建绘图画布

for name, model in models.items():
    # 线性回归使用标准化后的数据，树模型使用原始数据也可以，这里统一用标准化后的数据
    model.fit(X_train_scaled, y_train) # 训练模型：输入训练集特征和标签
    y_pred = model.predict(X_test_scaled) # 模型预测：输入测试集特征，得到预测结果

    # 评估指标
    mse = mean_squared_error(y_test, y_pred) # 均方误差：预测值与真实值差的平方的均值，越小越好
    r2 = r2_score(y_test, y_pred) # R2：决定系数，衡量模型对数据的拟合程度，越接近1越好
    results[name] = {"mse": mse, "r2": r2} # 保存评估结果

    print("=" * 40)
    print(f"【{name}】")
    print(f"均方误差 MSE: {mse:.4f}")
    print(f"R2 决定系数: {r2:.4f}")

    # 特征重要性排序
    print("特征重要性排序（从高到低）:")
    if name == "随机森林":
        # 随机森林通过feature_importances_获取特征重要性
        feature_importance = model.feature_importances_
        importance_df = pd.DataFrame({'特征': X.columns, '重要性': feature_importance})
        importance_df = importance_df.sort_values('重要性', ascending=False) # 按重要性降序排列
        print(importance_df.to_string(index=False)) # 不显示索引列
    elif name == "决策树":
        # 决策树也有feature_importances_
        feature_importance = model.feature_importances_
        importance_df = pd.DataFrame({'特征': X.columns, '重要性': feature_importance})
        importance_df = importance_df.sort_values('重要性', ascending=False)
        print(importance_df.to_string(index=False))
    else:
        # 线性回归使用系数（coef_）的绝对值衡量特征重要性
        # 因为数据已标准化，系数大小可直接反映特征对目标的影响程度
        feature_coef = model.coef_
        importance_df = pd.DataFrame({'特征': X.columns, '系数': feature_coef, '系数绝对值': np.abs(feature_coef)})
        importance_df = importance_df.sort_values('系数绝对值', ascending=False) # 按绝对值降序排列
        print(importance_df[['特征', '系数', '系数绝对值']].to_string(index=False))

    # 绘制特征重要性柱状图
    if name == "随机森林":
        plt.subplot(2, 2, 1)
        sns.barplot(x='重要性', y='特征', data=importance_df, hue='特征', palette='viridis', legend=False)
        plt.title('随机森林 - 特征重要性')
        plt.xlabel('重要性')
    elif name == "决策树":
        plt.subplot(2, 2, 2)
        sns.barplot(x='重要性', y='特征', data=importance_df, hue='特征', palette='viridis', legend=False)
        plt.title('决策树 - 特征重要性')
        plt.xlabel('重要性')
    else:
        plt.subplot(2, 2, 3)
        sns.barplot(x='系数绝对值', y='特征', data=importance_df, hue='特征', palette='viridis', legend=False)
        plt.title('线性回归 - 特征系数绝对值')
        plt.xlabel('系数绝对值')

# 绘制模型性能对比图
plt.subplot(2, 2, 4)
model_names = list(results.keys())
mse_values = [results[name]['mse'] for name in model_names]
r2_values = [results[name]['r2'] for name in model_names]

x = np.arange(len(model_names))
width = 0.35

# 双Y轴图：左轴MSE，右轴R2
ax1 = plt.gca()
ax2 = ax1.twinx()
bars1 = ax1.bar(x - width/2, mse_values, width, label='MSE', color='salmon', alpha=0.7)
bars2 = ax2.bar(x + width/2, r2_values, width, label='R2', color='steelblue', alpha=0.7)

ax1.set_xlabel('模型')
ax1.set_ylabel('均方误差 MSE', color='salmon')
ax2.set_ylabel('R2 决定系数', color='steelblue')
ax1.set_xticks(x)
ax1.set_xticklabels(model_names)
ax1.tick_params(axis='y', labelcolor='salmon')
ax2.tick_params(axis='y', labelcolor='steelblue')

# 添加图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
plt.title('模型性能对比')

plt.tight_layout()

# 输出汇总表格
print("\n" + "=" * 50)
print("====================模型指标汇总====================")
print(f"{'模型':<8} | {'MSE':<10} | {'R2':<10}")
print("-" * 40)
for name, res in results.items():
    print(f"{name:<8} | {res['mse']:<10.4f} | {res['r2']:<10.4f}")
print("=" * 50)
print("\n结论：随机森林模型表现最好，因为它通过多棵决策树的集成学习，")
print("能够捕捉特征之间的非线性关系和交互作用，具有更强的拟合能力和泛化能力。")

# 显示所有图像（放在最后，避免阻塞打印输出）
plt.show()
