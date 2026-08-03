"""训练实验记录模型

【MVC 归属】数据层（Model）--定义 experiments 表结构 + 数据操作类方法
【思路】
1. 每次训练产生一条记录，含模型名、5 个评估指标、参数、模型路径
2. is_best 标记当前最佳模型（按 roc_auc 降序选第一）
3. 训练前清除旧 is_best 标记，保证同一时刻只有一个 best
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class Experiment(Base):
    """训练实验记录模型"""
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    roc_auc: Mapped[float] = mapped_column(Float, nullable=False)
    params: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_best: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def bulk_create(cls, db: Session, results: list[dict]) -> list["Experiment"]:
        """批量创建实验记录，自动标记 best（按 roc_auc 降序第一个 is_best=True）

        逐字思路：
        1. 先清除所有旧 is_best 标记
        2. 按 roc_auc 降序排序 results
        3. 第一条 is_best=True，其余 False
        4. 逐条构造 Experiment 对象 add 到会话
        5. 一次 commit 提交
        """
        cls.clear_best(db)
        sorted_results = sorted(results, key=lambda r: r["roc_auc"], reverse=True)
        experiments = []
        for i, r in enumerate(sorted_results):
            exp = cls(
                model_name=r["model_name"],
                accuracy=r["accuracy"],
                precision=r["precision"],
                recall=r["recall"],
                f1_score=r["f1_score"],
                roc_auc=r["roc_auc"],
                params=r.get("params"),
                model_path=r.get("model_path"),
                is_best=(i == 0),
            )
            db.add(exp)
            experiments.append(exp)
        db.commit()
        for exp in experiments:
            db.refresh(exp)
        return experiments

    @classmethod
    def paginate(cls, db: Session, page: int, per_page: int, model_name: str = None) -> dict:
        """分页查询实验记录，返回 {items, total, page, per_page, pages}

        filters 支持: model_name（可选过滤）
        """
        query = db.query(cls)
        if model_name:
            query = query.filter(cls.model_name == model_name)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if per_page else 0
        return {
            "items": [_to_dict(e) for e in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    @classmethod
    def find_best(cls, db: Session) -> Optional["Experiment"]:
        """查 is_best=True 的记录"""
        return db.query(cls).filter(cls.is_best == True).first()

    @classmethod
    def clear_best(cls, db: Session):
        """清除所有 is_best 标记（训练前重置）"""
        db.query(cls).filter(cls.is_best == True).update({cls.is_best: False})
        db.commit()

    @classmethod
    def find_by_model_name(cls, db: Session, model_name: str) -> list["Experiment"]:
        """按模型名查所有实验记录"""
        return db.query(cls).filter(cls.model_name == model_name).order_by(cls.id.desc()).all()


def _to_dict(e: Experiment) -> dict:
    """Experiment 对象转字典（用于 API 响应）"""
    return {
        "id": e.id,
        "model_name": e.model_name,
        "accuracy": e.accuracy,
        "precision": e.precision,
        "recall": e.recall,
        "f1_score": e.f1_score,
        "roc_auc": e.roc_auc,
        "params": e.params,
        "model_path": e.model_path,
        "is_best": e.is_best,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
