"""数据模块路由

【MVC 归属】表现层（Controller）--接收请求、参数校验、调业务层、返回响应
【思路】
1. upload: 取文件 -> 调 data_service.upload_customers
2. customers: 分页查询 -> 调 data_service.get_customers
3. statistics: 数据概览 -> 调 data_service.get_statistics
4. quality: 质量报告 -> 调 data_service.get_quality_report
5. visualization: EDA 图表 -> 调 visualizer 工具
"""
from flask import Blueprint, request
from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import login_required, get_current_user
from app.utils.visualizer import generate_chart, VALID_CHART_TYPES
from app.services.data_service import (
    upload_customers, get_customers, get_statistics, get_quality_report,
)

bp = Blueprint("data", __name__)


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """上传 Excel：取文件 -> 调 data_service -> 返回质量报告"""
    file = request.files.get("file")
    user = get_current_user()
    db = get_db()
    data = upload_customers(db, user, file)
    return json(data)


@bp.route("/customers", methods=["GET"])
@login_required
def customers():
    """分页查询客户列表"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    filters = {
        "gender": request.args.get("gender"),
        "age_min": request.args.get("age_min", type=int),
        "age_max": request.args.get("age_max", type=int),
        "previously_insured": request.args.get("previously_insured", type=int),
        "keyword": request.args.get("keyword"),
    }
    db = get_db()
    result = get_customers(db, page, per_page, filters)
    return json(result)


@bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    """数据概览统计"""
    db = get_db()
    data = get_statistics(db)
    return json(data)


@bp.route("/quality", methods=["GET"])
@login_required
def quality():
    """数据质量报告"""
    db = get_db()
    data = get_quality_report(db)
    return json(data)


@bp.route("/visualization/<chart_type>", methods=["GET"])
@login_required
def visualization(chart_type: str):
    """EDA 可视化：生成指定类型的图表，返回 base64 PNG"""
    if chart_type not in VALID_CHART_TYPES:
        raise BizException(1001, f"未知图表类型: {chart_type}，支持: {', '.join(VALID_CHART_TYPES)}", 400)

    db = get_db()
    result = generate_chart(db, chart_type)
    return json(result)
