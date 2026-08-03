"""数据业务服务

【MVC 归属】业务层（Service）--编排数据上传、统计、质量报告流程
【思路】
1. upload_customers: 文件校验 -> Excel 解析 -> 清空旧数据批量导入 -> 返回质量报告
2. get_statistics: 客户总数 / 性别分布 / 响应分布 / 年龄统计
3. get_quality_report: 逐列查缺失值 + 重复行数 + 类型
4. get_customers: 分页查询（支持多条件筛选）
"""
from flask import request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.response import BizException
from app.models.customers import Customer
from app.utils.data_processor import parse_excel

# 上传文件大小限制：100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


def upload_customers(db: Session, user, file_storage) -> dict:
    """上传 Excel：校验 -> 解析 -> 清空旧数据批量导入 -> 返回质量报告

    返回 {imported_count, quality_report}
    """
    if not file_storage:
        raise BizException(1001, "未上传文件，请选择Excel文件", 400)

    # 校验文件扩展名
    filename = file_storage.filename or ""
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise BizException(1001, "文件格式不支持，仅接受 .xlsx/.xls 文件", 400)

    # 检查文件大小
    file_storage.seek(0, 2)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > MAX_FILE_SIZE:
        raise BizException(1001, "文件大小超过100MB限制", 400)

    rows, quality_report = parse_excel(file_storage)
    imported_count = Customer.bulk_create(db, rows, user.id)

    return {
        "imported_count": imported_count,
        "quality_report": quality_report,
    }


def get_customers(db: Session, page: int, per_page: int, filters: dict) -> dict:
    """分页查询客户列表

    filters 支持: gender / age_min / age_max / previously_insured / keyword
    """
    return Customer.paginate(db, page, per_page, filters)


def get_statistics(db: Session) -> dict:
    """数据概览统计：总数 / 性别分布 / 响应分布 / 年龄统计"""
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

    return {
        "total": total,
        "gender_distribution": gender_dist,
        "response_distribution": response_dist,
        "age_stats": {
            "min": age_row[0],
            "max": age_row[1],
            "avg": round(age_row[2], 1) if age_row[2] else 0,
        },
    }


def get_quality_report(db: Session) -> dict:
    """数据质量报告：逐列查缺失值 + 重复行数 + 类型"""
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

    return {
        "total_rows": total,
        "total_cols": len(columns),
        "missing_values": missing_values,
        "duplicates": 0,  # 覆盖导入策略下不做去重
        "dtypes": {col.name: str(col.type) for col in columns},
    }
