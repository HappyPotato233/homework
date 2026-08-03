"""ML 服务层测试

验证：特征编码、不平衡处理参数、model+scaler 绑定、experiments.params 可视化数据、预测使用 scaler
"""
import json
import os
import pytest
import pandas as pd
import numpy as np
from joblib import load

from app.services.ml_service import (
    _encode_features, DEFAULT_PARAMS, FEATURE_COLS,
    train_models, predict_all, load_model, get_model_path,
)
from app.models.experiment import Experiment


class TestEncodeFeatures:
    """测试特征编码正确性"""

    def test_gender_encoding(self):
        """Gender: Male=0, Female=1（对齐 AI技术方案 2.3）"""
        df = pd.DataFrame({
            "gender": ["Male", "Female", "Male"],
            "age": [25, 30, 40],
            "driving_license": [1, 1, 0],
            "region_code": [10.0, 20.0, 30.0],
            "previously_insured": [0, 1, 0],
            "vehicle_age": ["< 1 Year", "1-2 Year", "> 2 Years"],
            "vehicle_damage": ["Yes", "No", "Yes"],
            "annual_premium": [10000, 20000, 30000],
            "policy_sales_channel": [100, 200, 300],
            "vintage": [10, 20, 30],
            "response": [0, 1, 0],
        })
        X, y = _encode_features(df)
        # Male=0, Female=1
        assert X[0][0] == 0  # Male -> 0
        assert X[1][0] == 1  # Female -> 1

    def test_vehicle_age_ordinal(self):
        """Vehicle_Age: Ordinal 编码 < 1 Year=0, 1-2 Year=1, > 2 Years=2"""
        df = pd.DataFrame({
            "gender": ["Male"] * 3,
            "age": [25] * 3,
            "driving_license": [1] * 3,
            "region_code": [10.0] * 3,
            "previously_insured": [0] * 3,
            "vehicle_age": ["< 1 Year", "1-2 Year", "> 2 Years"],
            "vehicle_damage": ["No"] * 3,
            "annual_premium": [10000] * 3,
            "policy_sales_channel": [100] * 3,
            "vintage": [10] * 3,
            "response": [0, 1, 0],
        })
        X, _ = _encode_features(df)
        # vehicle_age 是 FEATURE_COLS 第 6 个（index 5）
        assert X[0][5] == 0  # < 1 Year -> 0
        assert X[1][5] == 1  # 1-2 Year -> 1
        assert X[2][5] == 2  # > 2 Years -> 2

    def test_vehicle_damage_encoding(self):
        """Vehicle_Damage: Yes=1, No=0"""
        df = pd.DataFrame({
            "gender": ["Male"] * 2,
            "age": [25] * 2,
            "driving_license": [1] * 2,
            "region_code": [10.0] * 2,
            "previously_insured": [0] * 2,
            "vehicle_age": ["< 1 Year"] * 2,
            "vehicle_damage": ["Yes", "No"],
            "annual_premium": [10000] * 2,
            "policy_sales_channel": [100] * 2,
            "vintage": [10] * 2,
            "response": [1, 0],
        })
        X, _ = _encode_features(df)
        # vehicle_damage 是 FEATURE_COLS 第 7 个（index 6）
        assert X[0][6] == 1  # Yes -> 1
        assert X[1][6] == 0  # No -> 0


class TestDefaultParams:
    """测试不平衡处理参数"""

    def test_lr_has_class_weight_balanced(self):
        """LogisticRegression 必须有 class_weight=balanced"""
        assert DEFAULT_PARAMS["logistic_regression"].get("class_weight") == "balanced"

    def test_rf_has_class_weight_balanced(self):
        """RandomForest 必须有 class_weight=balanced"""
        assert DEFAULT_PARAMS["random_forest"].get("class_weight") == "balanced"

    def test_xgboost_no_class_weight(self):
        """XGBoost 不用 class_weight，用 scale_pos_weight（动态计算）"""
        assert "class_weight" not in DEFAULT_PARAMS["xgboost"]


class TestTrainModels:
    """测试训练流程"""

    def test_train_saves_model_scaler_bundle(self, db, test_customers):
        """训练后 joblib 文件应包含 {"model": ..., "scaler": ...}"""
        result = train_models(db, models=["logistic_regression"])
        path = get_model_path("logistic_regression")
        assert os.path.exists(path)
        bundle = load(path)
        assert isinstance(bundle, dict)
        assert "model" in bundle
        assert "scaler" in bundle
        assert bundle["scaler"] is not None

    def test_train_records_experiment_with_viz_data(self, db, test_customers):
        """experiments.params 应包含 ROC/混淆矩阵可视化数据"""
        train_models(db, models=["logistic_regression"])
        exp = db.query(Experiment).filter(
            Experiment.model_name == "logistic_regression"
        ).order_by(Experiment.id.desc()).first()
        assert exp is not None
        params = json.loads(exp.params)
        assert "roc" in params
        assert "confusion_matrix" in params
        assert "hyperparams" in params

    def test_train_xgboost_has_scale_pos_weight(self, db, test_customers):
        """XGBoost 训练后 params 应含 scale_pos_weight"""
        train_models(db, models=["xgboost"])
        exp = db.query(Experiment).filter(
            Experiment.model_name == "xgboost"
        ).order_by(Experiment.id.desc()).first()
        params = json.loads(exp.params)
        assert "scale_pos_weight" in params["hyperparams"]
        assert params["hyperparams"]["scale_pos_weight"] > 0

    def test_train_returns_best_model(self, db, test_customers):
        """训练返回 best_model 和 results"""
        result = train_models(db)
        assert "best_model" in result
        assert "results" in result
        assert len(result["results"]) == 3
        for name in ["logistic_regression", "random_forest", "xgboost"]:
            assert name in result["results"]
            assert "roc_auc" in result["results"][name]


class TestPredictAll:
    """测试全量预测"""

    def test_predict_writes_predicted_prob(self, db, test_customers):
        """预测后 predicted_prob 应非空且在 [0, 1] 范围"""
        train_models(db, models=["logistic_regression"])
        result = predict_all(db, "logistic_regression")
        assert result["predicted_count"] == 20
        # 检查 predicted_prob 已回写
        from app.models.customers import Customer
        customers = db.query(Customer).filter(Customer.id >= 10000).all()
        for c in customers:
            assert c.predicted_prob is not None
            assert 0.0 <= c.predicted_prob <= 1.0

    def test_load_model_returns_bundle(self, db, test_customers):
        """load_model 应返回 dict bundle"""
        train_models(db, models=["logistic_regression"])
        bundle = load_model("logistic_regression")
        assert isinstance(bundle, dict)
        assert "model" in bundle
        assert "scaler" in bundle
