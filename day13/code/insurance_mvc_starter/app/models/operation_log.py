"""操作日志模型

【MVC 归属】数据层（Model）--定义 operation_logs 表结构 + 数据操作类方法
【思路】
1. 记录关键操作（训练/预测/邮件生成等），用于审计
2. action 枚举值对齐 API 文档 5.1：
   model_training / prediction / model_import
   email_generation / email_update / email_mark / email_delete
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def create(cls, db: Session, user_id: int, action: str, details: str = None) -> "OperationLog":
        """创建操作日志记录"""
        log = cls(user_id=user_id, action=action, details=details)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def paginate(cls, db: Session, page: int, per_page: int,
                 user_id: int = None, action: str = None) -> dict:
        """分页查询操作日志，返回 {items, total, page, per_page, pages}

        filters 支持: user_id（精确过滤）/ action（操作类型过滤）
        """
        query = db.query(cls)
        if user_id:
            query = query.filter(cls.user_id == user_id)
        if action:
            query = query.filter(cls.action == action)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if per_page else 0
        return {
            "items": [_to_dict(log) for log in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }


def _to_dict(log: OperationLog) -> dict:
    """OperationLog 对象转字典（用于 API 响应）"""
    return {
        "id": log.id,
        "user_id": log.user_id,
        "action": log.action,
        "details": log.details,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }
