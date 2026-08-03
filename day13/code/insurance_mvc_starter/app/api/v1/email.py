"""邮件路由

【MVC 归属】表现层（Controller）--接收请求、调业务层、返回响应
【思路】
1. 10 个接口对齐 API 文档 4.1~4.10
2. 所有接口需登录
3. 普通用户只能看自己的邮件记录，admin 看全部
4. 路由层仅做参数提取 + 调 email_service + 返回响应
"""
from flask import Blueprint, request
from pydantic import ValidationError

from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import login_required, get_current_user
from app.models.email_record import EmailRecord
from app.models.prompt_template import PromptTemplate
from app.models.operation_log import OperationLog
from app.schemas.email import (
    EmailGenerateRequest, PromptUpdateRequest,
    EmailRecordUpdateRequest, EmailStatusRequest, EmailBatchDeleteRequest,
)
from app.services.email_service import get_targets, generate_emails

bp = Blueprint("email", __name__)


def _parse_body(model_cls):
    """解析 JSON 请求体并用 Pydantic 校验"""
    body = request.get_json(silent=True) or {}
    try:
        return model_cls(**body)
    except ValidationError:
        raise BizException(1001, "参数校验错误，请检查请求体字段", 400)


@bp.route("/targets", methods=["GET"])
@login_required
def targets():
    """4.1 筛选高潜客户"""
    percentile = request.args.get("percentile", 0.9, type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    db = get_db()
    data = get_targets(db, percentile, page, per_page)
    return json(data)


@bp.route("/generate", methods=["POST"])
@login_required
def generate():
    """4.2 生成营销邮件"""
    req = _parse_body(EmailGenerateRequest)
    db = get_db()
    user = get_current_user()
    data = generate_emails(db, user, req.customer_ids, req.limit)
    return json(data)


@bp.route("/prompt", methods=["GET"])
@login_required
def get_prompt():
    """4.3 获取 Prompt 模板"""
    db = get_db()
    template = PromptTemplate.get_active(db)
    if not template:
        raise BizException(2001, "Prompt 模板不存在", 404)
    return json({"name": template.name, "content": template.content})


@bp.route("/prompt", methods=["PUT"])
@login_required
def update_prompt():
    """4.4 更新 Prompt 模板"""
    req = _parse_body(PromptUpdateRequest)
    db = get_db()
    template = PromptTemplate.update_content(db, req.content)
    if not template:
        raise BizException(2001, "Prompt 模板不存在", 404)
    return json({"name": template.name, "content": template.content})


@bp.route("/records", methods=["GET"])
@login_required
def records():
    """4.5 邮件记录列表"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    status = request.args.get("status", None)
    db = get_db()
    user = get_current_user()
    is_admin = user.role == "admin"
    data = EmailRecord.paginate(db, page, per_page, status, user.id, is_admin)
    return json(data)


@bp.route("/records/<int:record_id>", methods=["GET"])
@login_required
def record_detail(record_id):
    """4.6 邮件详情"""
    db = get_db()
    record = EmailRecord.find_by_id(db, record_id)
    if not record:
        raise BizException(2001, "邮件记录不存在", 404)
    return json({
        "id": record.id,
        "customer_id": record.customer_id,
        "subject": record.subject,
        "content": record.content,
        "status": record.status,
        "created_by": record.created_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })


@bp.route("/records/<int:record_id>", methods=["PUT"])
@login_required
def update_record(record_id):
    """4.7 更新邮件记录"""
    req = _parse_body(EmailRecordUpdateRequest)
    db = get_db()
    user = get_current_user()
    record = EmailRecord.update(db, record_id, req.email_subject, req.email_content)
    if not record:
        raise BizException(2001, "邮件记录不存在", 404)
    OperationLog.create(db, user.id, "email_update", f'{{"record_id": {record_id}}}')
    return json({
        "id": record.id,
        "subject": record.subject,
        "content": record.content,
        "status": record.status,
    })


@bp.route("/records/<int:record_id>", methods=["PATCH"])
@login_required
def mark_record(record_id):
    """4.8 标记邮件状态"""
    req = _parse_body(EmailStatusRequest)
    db = get_db()
    user = get_current_user()
    record = EmailRecord.update_status(db, record_id, req.status)
    if not record:
        raise BizException(2001, "邮件记录不存在", 404)
    OperationLog.create(db, user.id, "email_mark",
                        f'{{"record_id": {record_id}, "status": "{req.status}"}}')
    return json({"id": record.id, "status": record.status})


@bp.route("/records/<int:record_id>", methods=["DELETE"])
@login_required
def delete_record(record_id):
    """4.9 删除单条邮件"""
    db = get_db()
    user = get_current_user()
    success = EmailRecord.delete_by_id(db, record_id)
    if not success:
        raise BizException(2001, "邮件记录不存在", 404)
    OperationLog.create(db, user.id, "email_delete", f'{{"record_id": {record_id}}}')
    return json({"success": True})


@bp.route("/records", methods=["DELETE"])
@login_required
def bulk_delete_records():
    """4.10 批量删除邮件"""
    req = _parse_body(EmailBatchDeleteRequest)
    db = get_db()
    user = get_current_user()
    count = EmailRecord.bulk_delete(db, req.record_ids)
    OperationLog.create(db, user.id, "email_delete",
                        f'{{"record_ids": {req.record_ids}, "deleted": {count}}}')
    return json({"deleted_count": count})
