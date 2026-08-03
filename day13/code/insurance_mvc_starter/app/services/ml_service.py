"""ML 训练/预测/评估服务

【MVC 归属】业务层（Service）--编排 ML 训练、预测、模型管理流程
【思路】
1. 特征工程：Gender/Vehicle_Age/Vehicle_Damage 类别编码 + StandardScaler 标准化
2. 训练：LR/RF/XGBoost 三算法（含不平衡处理），计算 5 个指标，model+scaler 绑定存盘，记录实验
3. 预测：加载 model+scaler bundle，predict_proba 回写 customers.predicted_prob
4. 上传预测：解析 Excel，预测后直接返回结果不入库
"""
import os
import json
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, confusion_matrix,
)
from xgboost import XGBClassifier
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.response import BizException
from app.models.customers import Customer
from app.models.experiment import Experiment


# 三种算法名 -> 模型类映射
MODEL_ALGORITHMS = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "xgboost": XGBClassifier,
}

# 默认超参（含不平衡处理：LR/RF 用 class_weight=balanced，XGBoost 动态算 scale_pos_weight）
DEFAULT_PARAMS = {
    "logistic_regression": {"max_iter": 1000, "random_state": 42, "class_weight": "balanced"},
    "random_forest": {"n_estimators": 100, "random_state": 42, "class_weight": "balanced"},
    "xgboost": {"n_estimators": 100, "random_state": 42, "eval_metric": "logloss"},
}

# 特征列
FEATURE_COLS = [
    "gender", "age", "driving_license", "region_code",
    "previously_insured", "vehicle_age", "vehicle_damage",
    "annual_premium", "policy_sales_channel", "vintage",
]


def get_model_path(model_name: str) -> str:
    """返回模型文件路径"""
    return os.path.join(settings.MODEL_DIR, f"{model_name}.joblib")


def load_model(model_name: str) -> dict:
    """加载 joblib 模型文件，返回 {"model": model, "scaler": scaler} bundle

    向后兼容：若加载的是旧格式裸 model，包装为 {"model": model, "scaler": None}
    文件不存在抛 BizException(3002)
    """
    path = get_model_path(model_name)
    if not os.path.exists(path):
        raise BizException(3002, f"模型文件不存在: {model_name}", 400)
    obj = load(path)
    # 新格式：dict bundle {"model": ..., "scaler": ...}
    if isinstance(obj, dict) and "model" in obj:
        return obj
    # 旧格式：裸 model，包装为 bundle（scaler=None 表示跳过标准化）
    return {"model": obj, "scaler": None}


def _encode_features(df: pd.DataFrame):
    """特征工程：类别编码（不标准化，标准化由 StandardScaler 在训练/预测时处理）

    Gender -> 0/1 (Male=0, Female=1)  -- 对齐 AI技术方案 2.3
    Vehicle_Age -> 0/1/2 (Ordinal: < 1 Year=0, 1-2 Year=1, > 2 Years=2)
    Vehicle_Damage -> 0/1 (Yes=1, No=0)

    返回 (X, y)，X 为编码后但未标准化的特征矩阵，y 为 Response 标签
    """
    df = df.copy()
    # 类别编码
    df["gender"] = df["gender"].map({"Male": 0, "Female": 1}).fillna(0).astype(int)
    df["vehicle_age"] = df["vehicle_age"].map({"< 1 Year": 0, "1-2 Year": 1, "> 2 Years": 2}).fillna(0).astype(int)
    df["vehicle_damage"] = df["vehicle_damage"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    # 填充缺失值
    for col in FEATURE_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    X = df[FEATURE_COLS].values
    y = df["response"].values if "response" in df.columns else None
    return X, y


# 保留旧名称兼容 model_visualizer.py 的导入
_prepare_features = _encode_features


def _load_customers_df(db: Session) -> pd.DataFrame:
    """从 customers 表读取数据到 DataFrame"""
    customers = db.query(Customer).all()
    if not customers:
        raise BizException(2001, "无客户数据，请先上传数据", 400)
    data = []
    for c in customers:
        data.append({
            "id": c.id,
            "gender": c.gender,
            "age": c.age,
            "driving_license": c.driving_license,
            "region_code": c.region_code or 0,
            "previously_insured": c.previously_insured or 0,
            "vehicle_age": c.vehicle_age or "",
            "vehicle_damage": c.vehicle_damage or "",
            "annual_premium": c.annual_premium or 0,
            "policy_sales_channel": c.policy_sales_channel or 0,
            "vintage": c.vintage or 0,
            "response": c.response or 0,
        })
    return pd.DataFrame(data)


def _apply_scaler(scaler, X):
    """若有 scaler 则 transform，否则原样返回"""
    if scaler is not None:
        return scaler.transform(X)
    return X


def train_models(db: Session, models: list[str] = None, test_size: float = 0.2,
                 random_state: int = 42, params: dict = None) -> dict:
    """训练模型

    流程：
    1. 读数据 -> 类别编码 -> StandardScaler 标准化 -> train_test_split(stratify)
    2. 遍历算法训练（含不平衡处理）-> 计算 5 个指标 + 评估可视化数据
    3. model+scaler 绑定存盘为 .joblib
    4. 批量记录实验（params 含 ROC/混淆矩阵/特征重要性），自动标记 best
    5. 返回 {best_model, results}
    异常时抛 BizException(3001)
    """
    try:
        df = _load_customers_df(db)
        X, y = _encode_features(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=y if len(set(y)) > 1 else None,
        )

        # StandardScaler：训练集 fit_transform，测试集 transform（防数据泄漏）
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # 确定训练哪些模型
        model_names = models if models else list(MODEL_ALGORITHMS.keys())
        # 校验模型名
        for name in model_names:
            if name not in MODEL_ALGORITHMS:
                raise BizException(1001, f"未知模型名: {name}", 400)

        # 确保模型存储目录存在
        os.makedirs(settings.MODEL_DIR, exist_ok=True)

        # XGBoost 动态计算 scale_pos_weight（不平衡处理）
        xgb_spw = None
        if "xgboost" in model_names:
            n_neg = int((y_train == 0).sum())
            n_pos = int((y_train == 1).sum())
            xgb_spw = n_neg / n_pos if n_pos > 0 else 1

        results = []
        for name in model_names:
            # 合并默认参数和自定义参数
            model_params = DEFAULT_PARAMS.get(name, {}).copy()
            if params and name in params:
                model_params.update(params[name])

            # XGBoost 加入动态 scale_pos_weight
            if name == "xgboost" and xgb_spw is not None:
                model_params["scale_pos_weight"] = xgb_spw

            # 训练
            model = MODEL_ALGORITHMS[name](**model_params)
            model.fit(X_train, y_train)

            # 预测
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

            # 计算 5 个指标（roc_auc 在只有一个类别时可能为 nan，设为 0.0）
            auc = float(roc_auc_score(y_test, y_prob)) if len(set(y_test)) > 1 else 0.0
            if np.isnan(auc):
                auc = 0.0

            # 评估可视化数据：ROC 坐标 + 混淆矩阵 + 特征重要性
            viz_data = {
                "hyperparams": model_params,
                "roc": {},
                "confusion_matrix": [],
            }
            if len(set(y_test)) > 1:
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                viz_data["roc"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
            cm = confusion_matrix(y_test, y_pred)
            viz_data["confusion_matrix"] = cm.tolist()
            if hasattr(model, "feature_importances_"):
                viz_data["feature_importances"] = model.feature_importances_.tolist()
                viz_data["feature_names"] = FEATURE_COLS

            metrics = {
                "model_name": name,
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
                "roc_auc": auc,
                "params": json.dumps(viz_data),
                "model_path": get_model_path(name),
            }

            # 保存模型文件：model + scaler 绑定存盘
            dump({"model": model, "scaler": scaler}, get_model_path(name))
            results.append(metrics)

        # 批量记录实验，自动标记 best
        Experiment.bulk_create(db, results)

        # 找出 best_model
        best = max(results, key=lambda r: r["roc_auc"])
        return {
            "best_model": best["model_name"],
            "results": {r["model_name"]: {
                "accuracy": r["accuracy"],
                "precision": r["precision"],
                "recall": r["recall"],
                "f1_score": r["f1_score"],
                "roc_auc": r["roc_auc"],
            } for r in results},
        }
    except BizException:
        raise
    except Exception as e:
        raise BizException(3001, f"训练失败: {str(e)}", 500)


def predict_all(db: Session, model_name: str = None) -> dict:
    """全量预测：回写 customers.predicted_prob

    流程：
    1. model_name 缺省时查最佳模型
    2. 加载 model+scaler bundle
    3. 读 customers 全表，类别编码
    4. scaler.transform 标准化 -> predict_proba 取正类概率
    5. 回写 predicted_prob
    6. 返回 {model_name, predicted_count}
    异常时抛 BizException(3002)
    """
    try:
        # 确定使用哪个模型
        if not model_name:
            best = Experiment.find_best(db)
            if not best:
                raise BizException(3002, "无最佳模型，请先训练", 400)
            model_name = best.model_name

        # 加载 model+scaler bundle
        bundle = load_model(model_name)
        model = bundle["model"]
        scaler = bundle["scaler"]

        # 读数据 + 类别编码
        df = _load_customers_df(db)
        customer_ids = df["id"].values
        X, _ = _encode_features(df)

        # 标准化（复用训练时的 scaler）
        X = _apply_scaler(scaler, X)

        # 预测概率
        probs = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)

        # 回写 predicted_prob（cid 转 int 避免 numpy 类型与 SQLAlchemy 不匹配）
        for cid, prob in zip(customer_ids, probs):
            customer = db.query(Customer).filter(Customer.id == int(cid)).first()
            if customer:
                customer.predicted_prob = float(prob)
        db.commit()

        return {"model_name": model_name, "predicted_count": len(customer_ids)}
    except BizException:
        raise
    except Exception as e:
        raise BizException(3002, f"预测失败: {str(e)}", 500)


def predict_upload(db: Session, file_storage, model_name: str = None) -> dict:
    """上传数据预测：不入库，直接返回预测结果

    流程：
    1. model_name 缺省时查最佳模型
    2. 加载 model+scaler bundle
    3. 解析上传的 Excel
    4. 类别编码 + scaler.transform 标准化
    5. predict_proba 预测
    6. 返回 {model_name, total_count, statistics, predictions}
    """
    from app.utils.data_processor import parse_excel

    try:
        # 确定使用哪个模型
        if not model_name:
            best = Experiment.find_best(db)
            if not best:
                raise BizException(3002, "无最佳模型，请先训练", 400)
            model_name = best.model_name

        # 加载 model+scaler bundle
        bundle = load_model(model_name)
        model = bundle["model"]
        scaler = bundle["scaler"]

        # 解析 Excel
        rows, _ = parse_excel(file_storage)

        # 转 DataFrame 并特征工程
        df = pd.DataFrame(rows)
        X, _ = _encode_features(df)

        # 标准化（复用训练时的 scaler）
        X = _apply_scaler(scaler, X)

        # 预测概率
        probs = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)
        predictions_class = model.predict(X)

        # 构建预测结果
        predictions = []
        positive_count = 0
        for i, (prob, pred) in enumerate(zip(probs, predictions_class)):
            prob_val = float(prob)
            pred_val = int(pred)
            if pred_val == 1:
                positive_count += 1
            predictions.append({
                "id": int(df.iloc[i].get("id", i + 1)),
                "predicted_prob": prob_val,
                "prediction": pred_val,
            })

        return {
            "model_name": model_name,
            "total_count": len(predictions),
            "statistics": {
                "positive_count": positive_count,
                "negative_count": len(predictions) - positive_count,
                "avg_prob": float(np.mean(probs)),
            },
            "predictions": predictions,
        }
    except BizException:
        raise
    except Exception as e:
        raise BizException(3002, f"预测失败: {str(e)}", 500)
