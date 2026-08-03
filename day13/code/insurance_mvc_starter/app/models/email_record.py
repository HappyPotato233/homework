"""邮件记录模型

【MVC 归属】数据层（Model）--定义 email_records 表结构 + 数据操作类方法
【思路】
1. 每条记录关联一个客户（customer_id）和一个创建人（created_by）
2. status 标记邮件状态：generated / failed / sent
3. 普通用户只能查看自己生成的记录，admin 可查看全部
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, func, ForeignKey, desc
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class EmailRecord(Base):
    """邮件记录模型"""
    __tablename__ = "email_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @classmethod
    def create(cls, db: Session, customer_id: int, subject: str, content: str,
               status: str, created_by: int) -> "EmailRecord":
        """创建邮件记录"""
        record = cls(
            customer_id=customer_id,
            subject=subject,
            content=content,
            status=status,
            created_by=created_by,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def find_by_id(cls, db: Session, record_id: int) -> Optional["EmailRecord"]:
        """按 id 查单条"""
        return db.query(cls).filter(cls.id == record_id).first()

    @classmethod
    def paginate(cls, db: Session, page: int, per_page: int,
                 status: str = None, user_id: int = None, is_admin: bool = False) -> dict:
        """分页查询邮件记录

        - 普通用户只看自己生成的（user_id 过滤）
        - admin 看全部并附 created_by_username
        - 支持 status 过滤
        """
        query = db.query(cls)
        if not is_admin and user_id is not None:
            query = query.filter(cls.created_by == user_id)
        if status:
            query = query.filter(cls.status == status)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # admin 附 created_by_username
        result_items = []
        for record in items:
            item = _to_dict(record)
            if is_admin:
                from app.models.user import User
                user = db.query(User).filter(User.id == record.created_by).first()
                item["created_by_username"] = user.username if user else None
            result_items.append(item)

        pages = (total + per_page - 1) // per_page if per_page else 0
        return {
            "items": result_items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    @classmethod
    def update(cls, db: Session, record_id: int, subject: str = None,
               content: str = None) -> Optional["EmailRecord"]:
        """更新邮件主题/正文"""
        record = cls.find_by_id(db, record_id)
        if not record:
            return None
        if subject is not None:
            record.subject = subject
        if content is not None:
            record.content = content
        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def update_status(cls, db: Session, record_id: int, status: str) -> Optional["EmailRecord"]:
        """更新邮件状态"""
        record = cls.find_by_id(db, record_id)
        if not record:
            return None
        record.status = status
        db.commit()
        db.refresh(record)
        return record

    @classmethod
    def delete_by_id(cls, db: Session, record_id: int) -> bool:
        """删除单条邮件记录"""
        record = cls.find_by_id(db, record_id)
        if not record:
            return False
        db.delete(record)
        db.commit()
        return True

    @classmethod
    def bulk_delete(cls, db: Session, record_ids: list[int]) -> int:
        """批量删除邮件记录，返回删除条数"""
        count = db.query(cls).filter(cls.id.in_(record_ids)).delete(synchronize_session=False)
        db.commit()
        return count


def _to_dict(e: EmailRecord) -> dict:
    """EmailRecord 对象转字典（用于 API 响应）"""
    return {
        "id": e.id,
        "customer_id": e.customer_id,
        "subject": e.subject,
        "content": e.content,
        "status": e.status,
        "created_by": e.created_by,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
