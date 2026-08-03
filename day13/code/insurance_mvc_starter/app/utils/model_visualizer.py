"""模型评估可视化工具

【MVC 归属】工具层（Utils）--纯函数，生成模型评估图表
【思路】
1. 对齐现有 visualizer.py 风格：matplotlib Agg + seaborn + base64 PNG
2. 4 种图表：roc_curve / metrics_comparison / confusion_matrix / feature_importance
3. 优先从 experiments.params 反序列化评估数据画图，无可视化数据时 fallback 到重新计算
4. confusion_matrix 和 feature_importance 需要传入 model 参数
5. 返回 {chart_type, image_base64, format: "png"}
"""
import base64
import io
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from sqlalchemy.orm import Session

# 全局样式（sns.set_theme 会重置 rcParams，必须在其之后配置中文字体）
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "DejaVu Sans"]  # Windows/Linux 兼容
plt.rcParams["axes.unicode_minus"] = False    # 解决负号"-"显示方块问题

from app.core.response import BizException
from app.models.experiment import Experiment
from app.services.ml_service import load_model, _encode_features, _load_customers_df, _apply_scaler, MODEL_ALGORITHMS

# 合法图表类型
VALID_MODEL_CHART_TYPES = {
    "roc_curve", "metrics_comparison", "confusion_matrix", "feature_importance"
}


def _parse_viz_data(experiment: Experiment) -> dict:
    """从 experiment.params 反序列化可视化数据，失败返回空字典"""
    if not experiment or not experiment.params:
        return {}
    try:
        return json.loads(experiment.params)
    except (json.JSONDecodeError, TypeError):
        return {}


def generate_model_chart(db: Session, chart_type: str, model_name: str = None) -> dict:
    """生成模型评估图表

    chart_type: roc_curve / metrics_comparison / confusion_matrix / feature_importance
    model_name: confusion_matrix / feature_importance 必填
    """
    if chart_type not in VALID_MODEL_CHART_TYPES:
        raise BizException(1001, f"未知图表类型: {chart_type}", 400)

    if chart_type == "roc_curve":
        fig = _draw_roc_curve(db)
    elif chart_type == "metrics_comparison":
        fig = _draw_metrics_comparison(db)
    elif chart_type == "confusion_matrix":
        if not model_name:
            raise BizException(1001, "confusion_matrix 图表需要传入 model 参数", 400)
        fig = _draw_confusion_matrix(db, model_name)
    elif chart_type == "feature_importance":
        if not model_name:
            raise BizException(1001, "feature_importance 图表需要传入 model 参数", 400)
        fig = _draw_feature_importance(db, model_name)

    return _fig_to_base64(fig, chart_type)


def _draw_roc_curve(db: Session) -> plt.Figure:
    """画 ROC 曲线（用最佳模型）

    优先从 experiments.params 读取 ROC 坐标，无数据时 fallback 重新计算
    """
    best = Experiment.find_best(db)
    if not best:
        raise BizException(3002, "无最佳模型，请先训练", 400)

    # 尝试从 params 读取 ROC 数据
    viz_data = _parse_viz_data(best)
    roc_data = viz_data.get("roc", {})
    if roc_data and "fpr" in roc_data and "tpr" in roc_data:
        fpr = roc_data["fpr"]
        tpr = roc_data["tpr"]
        auc = best.roc_auc
    else:
        # fallback：加载 bundle 重新计算
        bundle = load_model(best.model_name)
        model = bundle["model"]
        scaler = bundle["scaler"]
        df = _load_customers_df(db)
        X, y = _encode_features(df)
        X = _apply_scaler(scaler, X)
        y_prob = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)
        fpr, tpr, _ = roc_curve(y, y_prob)
        auc = roc_auc_score(y, y_prob) if len(set(y)) > 1 else 0.0

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color="#5B9BD5", lw=2, label=f"{best.model_name} (AUC={auc:.4f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="随机分类器")
    ax.set_xlabel("假正率 (FPR)")
    ax.set_ylabel("真正率 (TPR)")
    ax.set_title("ROC 曲线")
    ax.legend(loc="lower right")
    return fig


def _draw_metrics_comparison(db: Session) -> plt.Figure:
    """画各模型指标对比柱状图"""
    experiments = db.query(Experiment).order_by(Experiment.id.desc()).all()
    if not experiments:
        raise BizException(3002, "无实验记录，请先训练", 400)

    # 取每个模型最新的一条记录
    seen = set()
    records = []
    for exp in experiments:
        if exp.model_name not in seen:
            seen.add(exp.model_name)
            records.append(exp)

    metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    x = np.arange(len(metrics))
    width = 0.8 / len(records)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#5B9BD5", "#ED7D31", "#70AD47"]
    for i, r in enumerate(records):
        values = [getattr(r, m) for m in metrics]
        ax.bar(x + i * width, values, width, label=r.model_name, color=colors[i % len(colors)])
    ax.set_xticks(x + width * (len(records) - 1) / 2)
    ax.set_xticklabels(["准确率", "精确率", "召回率", "F1", "ROC-AUC"])
    ax.set_ylabel("分数")
    ax.set_title("模型指标对比")
    ax.legend()
    ax.set_ylim(0, 1.05)
    return fig


def _draw_confusion_matrix(db: Session, model_name: str) -> plt.Figure:
    """画混淆矩阵热力图

    优先从 experiments.params 读取混淆矩阵，无数据时 fallback 重新计算
    """
    # 查该模型最新的实验记录
    exp = db.query(Experiment).filter(
        Experiment.model_name == model_name
    ).order_by(Experiment.id.desc()).first()

    # 尝试从 params 读取混淆矩阵
    cm = None
    if exp:
        viz_data = _parse_viz_data(exp)
        cm_list = viz_data.get("confusion_matrix")
        if cm_list:
            cm = np.array(cm_list)

    if cm is None:
        # fallback：加载 bundle 重新计算
        bundle = load_model(model_name)
        model = bundle["model"]
        scaler = bundle["scaler"]
        df = _load_customers_df(db)
        X, y = _encode_features(df)
        X = _apply_scaler(scaler, X)
        y_pred = model.predict(X)
        cm = confusion_matrix(y, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["未响应", "响应"], yticklabels=["未响应", "响应"])
    ax.set_xlabel("预测值")
    ax.set_ylabel("真实值")
    ax.set_title(f"混淆矩阵 - {model_name}")
    return fig


def _draw_feature_importance(db: Session, model_name: str) -> plt.Figure:
    """画特征重要度条形图

    优先从 experiments.params 读取特征重要性，无数据时 fallback 从 model 读取
    """
    importances = None
    feature_names = None

    # 查该模型最新的实验记录
    exp = db.query(Experiment).filter(
        Experiment.model_name == model_name
    ).order_by(Experiment.id.desc()).first()

    if exp:
        viz_data = _parse_viz_data(exp)
        if "feature_importances" in viz_data:
            importances = viz_data["feature_importances"]
            feature_names = viz_data.get("feature_names")

    if importances is None:
        # fallback：从 model 读取
        bundle = load_model(model_name)
        model = bundle["model"]
        if not hasattr(model, "feature_importances_"):
            raise BizException(1001, f"模型 {model_name} 不支持特征重要度", 400)
        importances = model.feature_importances_
        from app.services.ml_service import FEATURE_COLS
        feature_names = FEATURE_COLS

    indices = np.argsort(importances)[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(indices)), [importances[i] for i in indices][::-1], color="#70AD47")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices][::-1])
    ax.set_xlabel("重要度")
    ax.set_title(f"特征重要度 - {model_name}")
    return fig


def _fig_to_base64(fig: plt.Figure, chart_type: str) -> dict:
    """Figure 转 base64 PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return {"chart_type": chart_type, "image_base64": img_b64, "format": "png"}
