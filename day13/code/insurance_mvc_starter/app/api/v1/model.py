"""模型路由

【MVC 归属】表现层（Controller）--接收请求、调业务层、返回响应
【思路】
1. 8 个接口对齐 API 文档 3.1~3.8
2. train/export/import 仅 admin 可访问
3. 其他接口登录用户均可访问
"""
import os
from flask import Blueprint, request, send_file
from pydantic import ValidationError

from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import login_required, role_required, get_current_user
from app.models.experiment import Experiment
from app.models.operation_log import OperationLog
from app.schemas.model import TrainRequest, PredictRequest
from app.services import ml_service
from app.utils.model_visualizer import generate_model_chart, VALID_MODEL_CHART_TYPES

bp = Blueprint("model", __name__)


def _parse_body(model_cls):
    """解析 JSON 请求体并用 Pydantic 校验"""
    body = request.get_json(silent=True) or {}
    try:
        return model_cls(**body)
    except ValidationError:
        raise BizException(1001, "参数校验错误，请检查请求体字段", 400)


@bp.route("/train", methods=["POST"])
@role_required("admin")
def train():
    """3.1 训练模型（仅 admin）"""
    req = _parse_body(TrainRequest)
    db = get_db()
    user = get_current_user()
    result = ml_service.train_models(
        db, req.models, req.test_size, req.random_state, req.params
    )
    OperationLog.create(db, user.id, "model_training",
                        f'{{"best_model": "{result["best_model"]}"}}')
    return json(result)


@bp.route("/experiments", methods=["GET"])
@login_required
def experiments():
    """3.2 实验记录分页"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    model_name = request.args.get("model_name", None)
    db = get_db()
    data = Experiment.paginate(db, page, per_page, model_name)
    return json(data)


@bp.route("/best", methods=["GET"])
@login_required
def best():
    """3.3 获取最佳模型"""
    db = get_db()
    exp = Experiment.find_best(db)
    if not exp:
        raise BizException(3002, "无最佳模型，请先训练", 400)
    return json({
        "model_name": exp.model_name,
        "roc_auc": exp.roc_auc,
        "experiment_id": exp.id,
    })


@bp.route("/predict", methods=["POST"])
@login_required
def predict():
    """3.4 全量预测"""
    req = _parse_body(PredictRequest)
    db = get_db()
    user = get_current_user()
    result = ml_service.predict_all(db, req.model_name)
    OperationLog.create(db, user.id, "prediction",
                        f'{{"model_name": "{result["model_name"]}", "count": {result["predicted_count"]}}}')
    return json(result)


@bp.route("/predict_upload", methods=["POST"])
@login_required
def predict_upload():
    """3.5 上传数据预测（不入库）"""
    file = request.files.get("file")
    if not file:
        raise BizException(1001, "未上传文件，请选择Excel文件", 400)
    # 校验文件扩展名
    filename = file.filename or ""
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise BizException(1001, "文件格式不支持，仅接受 .xlsx/.xls 文件", 400)
    model_name = request.form.get("model", None)
    db = get_db()
    result = ml_service.predict_upload(db, file, model_name)
    return json(result)


@bp.route("/visualization/<chart_type>", methods=["GET"])
@login_required
def visualization(chart_type):
    """3.6 模型评估可视化"""
    if chart_type not in VALID_MODEL_CHART_TYPES:
        raise BizException(1001, f"未知图表类型: {chart_type}", 400)
    model_name = request.args.get("model", None)
    db = get_db()
    data = generate_model_chart(db, chart_type, model_name)
    return json(data)


@bp.route("/export/<model_name>", methods=["GET"])
@role_required("admin")
def export_model(model_name):
    """3.7 导出模型文件（仅 admin）"""
    path = ml_service.get_model_path(model_name)
    if not os.path.exists(path):
        raise BizException(3002, f"模型不存在: {model_name}", 400)
    db = get_db()
    user = get_current_user()
    OperationLog.create(db, user.id, "model_import",
                        f'{{"action": "export", "model": "{model_name}"}}')
    return send_file(path, as_attachment=True, download_name=f"{model_name}.joblib")


@bp.route("/import", methods=["POST"])
@role_required("admin")
def import_model():
    """3.8 导入模型文件（仅 admin）"""
    file = request.files.get("file")
    if not file:
        raise BizException(1001, "未上传文件", 400)
    filename = file.filename or ""
    if not filename.lower().endswith(".joblib"):
        raise BizException(1001, "文件格式不支持，仅接受 .joblib 文件", 400)
    # 从文件名提取模型名（去掉 .joblib 后缀）
    model_name = os.path.splitext(filename)[0]
    # 确保目录存在
    os.makedirs(ml_service.settings.MODEL_DIR, exist_ok=True)
    path = ml_service.get_model_path(model_name)
    file.save(path)
    db = get_db()
    user = get_current_user()
    OperationLog.create(db, user.id, "model_import",
                        f'{{"action": "import", "model": "{model_name}"}}')
    return json({"model_name": model_name, "path": path})
