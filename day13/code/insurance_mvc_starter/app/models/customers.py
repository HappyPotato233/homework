"""客户模型

【MVC 归属】数据层（Model）--定义 customers 表结构 + 数据操作类方法
【思路】
1. 定义 Customer ORM 模型，字段对齐 API 文档数据模块
2. 类方法封装所有数据操作：批量导入 / 分页查询 / 计数 / 高潜筛选
3. predicted_prob 字段初始为 NULL，模型预测后回写
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, func, ForeignKey, desc
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    driving_license: Mapped[int] = mapped_column(Integer, default=0)
    region_code: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    previously_insured: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vehicle_age: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    vehicle_damage: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    annual_premium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    policy_sales_channel: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vintage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response: Mapped[int] = mapped_column(Integer, default=0)
    predicted_prob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def bulk_create(cls, db: Session, rows: list[dict], user_id: int) -> int:
        """清空旧数据 + 批量导入，返回入库行数

        教学版覆盖策略：每次上传先 DELETE 全表再批量 INSERT。
        使用 bulk_insert_mappings 分批 5000 条 commit，防 38 万行锁库（NFR-PERF-001）。
        """
        db.query(cls).delete()
        db.commit()
        for row in rows:
            row["uploaded_by"] = user_id
        batch_size = 5000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            db.bulk_insert_mappings(cls, batch)
            db.commit()
        return len(rows)

    @classmethod
    def paginate(cls, db: Session, page: int, per_page: int, filters: dict) -> dict:
        """分页查询，返回 {items, total, page, per_page, pages}

        filters 支持: gender / age_min / age_max / previously_insured / keyword
        逐字思路：
        1. 基础 query 全表
        2. 按 filters 逐个 .filter() 叠加条件
        3. count() 算总数
        4. order_by + offset + limit 取当前页数据
        5. 向上取整算总页数
        """
        query = db.query(cls)
        if filters.get("gender"):
            query = query.filter(cls.gender == filters["gender"])
        if filters.get("age_min") is not None:
            query = query.filter(cls.age >= filters["age_min"])
        if filters.get("age_max") is not None:
            query = query.filter(cls.age <= filters["age_max"])
        if filters.get("previously_insured") is not None:
            query = query.filter(cls.previously_insured == filters["previously_insured"])
        if filters.get("keyword"):
            # keyword 按 id 搜索（数字字符串转 int 匹配）
            try:
                keyword_id = int(filters["keyword"])
                query = query.filter(cls.id == keyword_id)
            except (ValueError, TypeError):
                pass  # 非数字 keyword 不做过滤，返回空

        total = query.count()
        items = query.order_by(cls.id).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if per_page else 0

        return {
            "items": [_to_dict(c) for c in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    @classmethod
    def count(cls, db: Session) -> int:
        """返回客户总数"""
        return db.query(cls).count()

    @classmethod
    def find_high_potential(cls, db: Session, top_percent: float = 0.9) -> list:
        """查高潜客户（predicted_prob >= top_percent 分位数）

        数据模块阶段 predicted_prob 全为 NULL，返回空列表。
        模型预测后回写 predicted_prob，此方法自动生效。
        逐字思路：
        1. 先查 predicted_prob 非空的总数，为 0 直接返回空列表
        2. 按 top_percent 算取多少条（top 10% = 1 - 0.9）
        3. 按 predicted_prob 降序取前 N 条
        """
        total = db.query(cls).filter(cls.predicted_prob.isnot(None)).count()
        if total == 0:
            return []
        limit = max(1, int(total * (1 - top_percent)))
        return db.query(cls).filter(
            cls.predicted_prob.isnot(None)
        ).order_by(desc(cls.predicted_prob)).limit(limit).all()


def _to_dict(c: Customer) -> dict:
    """Customer 对象转字典（用于 API 响应）"""
    return {
        "id": c.id,
        "gender": c.gender,
        "age": c.age,
        "driving_license": c.driving_license,
        "region_code": c.region_code,
        "previously_insured": c.previously_insured,
        "vehicle_age": c.vehicle_age,
        "vehicle_damage": c.vehicle_damage,
        "annual_premium": c.annual_premium,
        "policy_sales_channel": c.policy_sales_channel,
        "vintage": c.vintage,
        "response": c.response,
        "predicted_prob": c.predicted_prob,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
