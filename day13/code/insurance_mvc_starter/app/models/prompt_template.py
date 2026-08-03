"""Prompt 模板模型

【MVC 归属】数据层（Model）--定义 prompt_templates 表结构 + 数据操作类方法
【思路】
1. 存储邮件生成用的 Prompt 模板，content 含 {gender}/{age} 等占位符
2. is_active 标记当前激活的模板（同一时刻只有一个激活）
3. 首次启动时 seed 默认模板
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


# 默认 Prompt 模板（对齐 AI技术方案 3.3：角色设定 + 客户画像 + 任务要求 + JSON输出格式）
# {{ }} 转义为字面 {}，str.format 后保留 JSON 示例的花括号
DEFAULT_PROMPT_CONTENT = """你是保险营销文案专家。请根据以下客户画像生成一封个性化车险营销邮件。
客户画像：{gender}，年龄{age}岁，{driving_license}，{vehicle_age}，{vehicle_damage}，{previously_insured}，年保费{annual_premium}元。
要求：语气专业有温度，突出该客户画像的痛点与利益，包含行动号召(CTA)。
仅返回严格JSON，格式：{{"subject":"邮件主题","content":"HTML格式正文"}}"""


class PromptTemplate(Base):
    """Prompt 模板模型"""
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def get_active(cls, db: Session) -> Optional["PromptTemplate"]:
        """查 is_active=True 的模板"""
        return db.query(cls).filter(cls.is_active == True).first()

    @classmethod
    def update_content(cls, db: Session, content: str) -> Optional["PromptTemplate"]:
        """更新当前激活模板的内容"""
        template = cls.get_active(db)
        if not template:
            return None
        template.content = content
        db.commit()
        db.refresh(template)
        return template

    @classmethod
    def seed_default(cls, db: Session) -> "PromptTemplate":
        """首次启动时 seed 默认 Prompt 模板

        若模板已存在但内容与 DEFAULT_PROMPT_CONTENT 不一致（代码升级后），
        自动更新为新版内容，避免旧模板导致 LLM 无法按 JSON 格式输出。
        """
        existing = cls.get_active(db)
        if existing:
            if existing.content != DEFAULT_PROMPT_CONTENT:
                existing.content = DEFAULT_PROMPT_CONTENT
                db.commit()
                db.refresh(existing)
            return existing
        template = cls(
            name="默认营销邮件模板",
            content=DEFAULT_PROMPT_CONTENT,
            is_active=True,
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
