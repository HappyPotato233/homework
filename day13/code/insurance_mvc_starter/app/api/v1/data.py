"""数据模块路由

【MVC 归属】表现层（Controller）--接收请求、参数校验、调业务逻辑、返回响应
【思路】
1. upload: 取文件 -> 校验大小 -> parse_excel 解析 -> bulk_create 清空旧数据批量导入 -> 返回质量报告
2. customers: 分页查询，支持 gender/age_min/age_max/previously_insured/keyword 过滤
3. statistics: 数据概览统计（总数/性别分布/响应分布/年龄统计）
4. quality: 数据质量报告（从数据库重新计算）

风格对齐 auth.py：用 BizException 抛业务错误 + json() 返回统一响应
"""
from flask import Blueprint, request
from sqlalchemy import func
from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import login_required, get_current_user
from app.models.customers import Customer
from app.utils.data_processor import parse_excel
from app.utils.visualizer import generate_chart, VALID_CHART_TYPES

bp = Blueprint("data", __name__)

# 上传文件大小限制：10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """上传 Excel：取文件 -> 校验大小 -> 解析 -> 清空旧数据批量导入 -> 返回质量报告

    逐字思路：
    1. request.files 取 file，没有 -> BizException(1001)
    2. seek 判断文件大小，超 10MB -> BizException(1001)
    3. parse_excel 解析（失败内部抛 BizException(2002)）
    4. Customer.bulk_create 清空旧数据 + 批量插入
    5. 返回 imported_count + quality_report
    """
    file = request.files.get("file")
    if not file:
        raise BizException(1001, "未上传文件，请选择Excel文件", 400)

    # 校验文件扩展名（API 文档要求 .xlsx/.xls）
    filename = file.filename or ""
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise BizException(1001, "文件格式不支持，仅接受 .xlsx/.xls 文件", 400)

    # 检查文件大小：seek 到末尾拿位置，再 seek 回来
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise BizException(1001, "文件大小超过10MB限制", 400)

    user = get_current_user()
    db = get_db()

    rows, quality_report = parse_excel(file)
    imported_count = Customer.bulk_create(db, rows, user.id)

    return json({
        "imported_count": imported_count,
        "quality_report": quality_report,
    })


@bp.route("/customers", methods=["GET"])
@login_required
def customers():
    """分页查询客户列表

    查询参数：page(默认1) / per_page(默认50) / gender / age_min / age_max /
              previously_insured / keyword(按id搜索)
    """
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
    result = Customer.paginate(db, page, per_page, filters)
    return json(result)


@bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    """数据概览统计：总数 / 性别分布 / 响应分布 / 年龄统计

    逐字思路：
    1. count() 查总数
    2. group_by(gender) 查性别分布
    3. group_by(response) 查响应分布（0:未响应 1:响应）
    4. min/max/avg 聚合查年龄统计
    """
    db = get_db()
    total = Customer.count(db)

    # 性别分布
    gender_dist = {}
    for row in db.query(Customer.gender, func.count()).group_by(Customer.gender).all():
        gender_dist[row[0]] = row[1]

    # 响应分布（key 转字符串，符合 API 文档 {"0": n, "1": n}）
    response_dist = {}
    for row in db.query(Customer.response, func.count()).group_by(Customer.response).all():
        response_dist[str(row[0])] = row[1]

    # 年龄统计
    age_row = db.query(
        func.min(Customer.age),
        func.max(Customer.age),
        func.avg(Customer.age),
    ).first()

    return json({
        "total": total,
        "gender_distribution": gender_dist,
        "response_distribution": response_dist,
        "age_stats": {
            "min": age_row[0],
            "max": age_row[1],
            "avg": round(age_row[2], 1) if age_row[2] else 0,
        },
    })


@bp.route("/quality", methods=["GET"])
@login_required
def quality():
    """数据质量报告：从数据库重新计算（独立于上传时的报告）

    逐字思路：
    1. 先查总数，无数据 -> BizException(2001)
    2. 逐列查 NULL 数量（缺失值）
    3. 返回 total_rows / total_cols / missing_values / duplicates / dtypes
    """
    db = get_db()
    total = Customer.count(db)
    if total == 0:
        raise BizException(2001, "暂无数据，请先上传", 404)

    # 逐列查缺失值
    columns = [
        Customer.gender, Customer.age, Customer.driving_license,
        Customer.region_code, Customer.previously_insured, Customer.vehicle_age,
        Customer.vehicle_damage, Customer.annual_premium, Customer.policy_sales_channel,
        Customer.vintage, Customer.response,
    ]
    missing_values = {}
    for col in columns:
        null_count = db.query(func.count()).filter(col.is_(None)).scalar()
        missing_values[col.name] = null_count

    return json({
        "total_rows": total,
        "total_cols": len(columns),
        "missing_values": missing_values,
        "duplicates": 0,  # 覆盖导入策略下不做去重
        "dtypes": {col.name: str(col.type) for col in columns},
    })


@bp.route("/visualization/<chart_type>", methods=["GET"])
@login_required
def visualization(chart_type: str):
    """EDA 可视化：生成指定类型的图表，返回 base64 PNG

    路径参数 chart_type ∈ response_distribution / gender_response /
                         age_distribution / premium_distribution
    响应 data: {chart_type, image_base64, format: "png"}
    未知类型 -> BizException(1001)
    """
    if chart_type not in VALID_CHART_TYPES:
        raise BizException(1001, f"未知图表类型: {chart_type}，支持: {', '.join(VALID_CHART_TYPES)}", 400)

    db = get_db()
    result = generate_chart(db, chart_type)
    return json(result)
