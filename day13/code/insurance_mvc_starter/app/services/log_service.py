"""日志查询业务层

【MVC 归属】业务层（Service）--编排日志查询流程
【思路】封装分页查询逻辑，供路由层调用
"""
from sqlalchemy.orm import Session
from app.models.operation_log import OperationLog


def query_logs(db: Session, page: int, per_page: int,
               user_id: int = None, action: str = None) -> dict:
    """分页查询操作日志，返回 {items, total, page, per_page, pages}"""
    return OperationLog.paginate(db, page, per_page, user_id, action)
