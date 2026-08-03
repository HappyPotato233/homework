from pydantic import BaseModel, Field
from typing import Optional


class EmailGenerateRequest(BaseModel):
    """生成邮件请求体：POST /email/generate

    1. customer_ids: 可选，指定客户；缺省自动取 top
    2. limit: 自动取 top N（customer_ids 为空时生效），默认 5
    """
    customer_ids: Optional[list[int]] = None
    limit: int = Field(5, ge=1, le=100)


class PromptUpdateRequest(BaseModel):
    """更新 Prompt 模板请求体：PUT /email/prompt

    1. content: 模板内容，须含占位符，至少 10 个字符
    """
    content: str = Field(..., min_length=10)


class EmailRecordUpdateRequest(BaseModel):
    """更新邮件记录请求体：PUT /email/records/{record_id}

    1. email_subject: 可选，邮件主题
    2. email_content: 可选，邮件正文
    """
    email_subject: Optional[str] = None
    email_content: Optional[str] = None


class EmailStatusRequest(BaseModel):
    """更新邮件状态请求体：PATCH /email/records/{record_id}

    1. status: 状态值（如 sent/failed）
    """
    status: str = Field(..., min_length=1)


class EmailBatchDeleteRequest(BaseModel):
    """批量删除邮件请求体：DELETE /email/records

    1. record_ids: 要删除的记录 ID 列表，至少 1 条
    """
    record_ids: list[int] = Field(..., min_length=1)
