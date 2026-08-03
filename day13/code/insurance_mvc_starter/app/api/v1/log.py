"""日志路由

【MVC 归属】表现层（Controller）--接收请求、鉴权、参数校验、返回响应
【思路】
1. GET /api/v1/logs 查询操作日志（仅 admin）
2. 支持 page/per_page/user_id/action 查询参数
3. action 校验枚举值，非法值抛 1001
"""
from flask import Blueprint, request

from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import role_required
from app.services import log_service

bp = Blueprint("log", __name__)

# action 合法枚举值（对齐 API 文档 5.1）
VALID_ACTIONS = {
    "model_training", "prediction", "model_import",
    "email_generation", "email_update", "email_mark", "email_delete",
}


@bp.route("", methods=["GET"])
@role_required("admin")
def query():
    """5.1 操作日志查询（仅 admin）"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    # 校验分页参数
    if page < 1 or per_page < 1:
        raise BizException(1001, "参数校验错误，page和per_page必须大于0", 400)

    user_id = request.args.get("user_id", type=int)
    action = request.args.get("action")

    # 校验 action 枚举
    if action and action not in VALID_ACTIONS:
        raise BizException(1001, f"非法action值: {action}", 400)

    db = get_db()
    data = log_service.query_logs(db, page, per_page, user_id, action)
    return json(data)
