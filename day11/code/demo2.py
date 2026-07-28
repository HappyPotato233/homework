'''
任务描述**: 构建一个二分类模型,预测客户是否会流失。

1. 生成模拟客户数据(年龄、消费金额、使用时长、是否流失)
2. 进行数据预处理(标准化、处理类别特征)
3. 使用逻辑回归、SVM、随机森林训练模型
4. 输出分类报告、混淆矩阵、ROC曲线
5. 分析哪个模型效果最好,为什么
'''
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression # 逻辑回归模型
from sklearn.svm import SVC # SVM模型
from sklearn.ensemble import RandomForestClassifier # 随机森林模型
from sklearn.preprocessing import StandardScaler # 标准化模型
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1.生成模拟客户数据
np.random.seed(42)
n_samples = 1000
data = pd.DataFrame({
    '年龄': np.random.randint(18, 65, n_samples),
    '月消费金额': np.random.exponential(200, n_samples),
    '使用时长_月': np.random.randint(1, 60, n_samples),
    '投诉次数': np.random.poisson(0.5, n_samples),
    '是否流失': np.zeros(n_samples, dtype=int)
})

# 2.进行数据预处理（标准化、处理类别特征）
# ====================== 2.数据预处理 & 划分数据集 ======================
risk_score = -data['使用时长_月'] / 12 + data['投诉次数'] * 3 - data['月消费金额'] / 300 # 风险分
churn_prob = 1 / (1 + np.exp(-risk_score)) # 客户流失概率
data['是否流失'] = np.random.binomial(1, churn_prob, n_samples) # 客户流失标签（0：不流失，1：流失）
feature_cols = ['年龄', '月消费金额', '使用时长_月', '投诉次数']
X = data[feature_cols]
y = data['是否流失']  
# =========================================
# 划分训练集、测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y) # X特征标签数据集，y标签数据集，test_size测试集占比，stratify使训练集和测试集中客户流失比例相同
# X_train：训练集特征 X_test：测试集特征 y_train：训练集标签 y_test：测试集标签
# 标准化（逻辑回归、SVM必须标准化；随机森林不受影响，但统一处理） 
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train) # 标准化
X_test_scaled = scaler.transform(X_test) # 为什么不是fit_transform？因为应该使用同一套标准进行
# ====================== 3.初始化并训练三类模型 ======================
models = {
    "逻辑回归": LogisticRegression(random_state=42),
    "线性SVM": SVC(kernel='linear', probability=True, random_state=42),
    "随机森林": RandomForestClassifier(n_estimators=100, random_state=42)
}
plt.figure(figsize=(8, 6))
results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train) # 训练模型
    y_pred = model.predict(X_test_scaled) # 模型预测，输入特征数据测试集预测标签，得到预测结果列表，列表中每一个元素都是是否流失的标签
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] # predict_proba返回[样本号,[不流失,流失]], 取流失概率就是[:,1]

    # 评估指标
    acc = accuracy_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba) # 计算ROC曲线
    roc_auc = auc(fpr, tpr)
    results[name] = {"acc": acc, "auc": roc_auc}

    print("=" * 40)
    print(f"【{name}】")
    print(f"准确率: {acc:.2%}")
    print(f"AUC: {roc_auc:.4f}")
    print("混淆矩阵：")
    print(confusion_matrix(y_test, y_pred))
    print("分类报告：")
    print(classification_report(y_test, y_pred))

    # 绘制ROC曲线
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.4f})")

# 绘制随机猜测基准线
plt.plot([0, 1], [0, 1], "k--", lw=1)
plt.xlabel("假正率 FPR")
plt.ylabel("真正率 TPR")
plt.title("客户流失预测模型ROC曲线对比")
plt.legend()
plt.show()

# 输出汇总表格
print("\\n====================模型指标汇总====================")
for name, res in results.items():
    print(f"{name:8s} | ACC:{res['acc']:.2%} | AUC:{res['auc']:.4f}")
