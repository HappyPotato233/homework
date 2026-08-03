from pydantic import BaseModel, Field
from typing import Optional


class TrainRequest(BaseModel):
    """训练请求体：POST /model/train

    1. models: 可选，null=训练全部三算法；可传 ["xgboost"] 子集
    2. test_size: 测试集比例，默认 0.2
    3. random_state: 随机种子，默认 42
    4. params: 按模型名覆盖超参，如 {"xgboost": {"n_estimators": 200}}
    """
    models: Optional[list[str]] = None
    test_size: float = Field(0.2, gt=0, lt=1)
    random_state: int = 42
    params: Optional[dict] = None


class PredictRequest(BaseModel):
    """预测请求体：POST /model/predict

    1. model_name: 可选，缺省用最佳模型
    """
    model_config = {"protected_namespaces": ()}  # 允许 model_ 前缀字段名
    model_name: Optional[str] = None
