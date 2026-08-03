"""邮件业务服务

【MVC 归属】业务层（Service）--编排高潜客户筛选、邮件生成流程
【思路】
1. get_targets: 按预测概率分位数筛选高潜客户（threshold 基于全量概率计算）
2. generate_emails: 取客户->模板->LLM生成->入库->记录日志
3. 路由层仅做参数提取 + 调本服务 + 返回响应
"""
import numpy as np
from sqlalchemy.orm import Session

from app.core.response import BizException
from app.models.customers import Customer
from app.models.email_record import EmailRecord
from app.models.prompt_template import PromptTemplate
from app.models.operation_log import OperationLog
from app.services.llm_service import generate_email_content


def get_targets(db: Session, percentile: float = 0.9,
                page: int = 1, per_page: int = 20) -> dict:
    """筛选高潜客户（按预测概率分位数）

    threshold = np.quantile(all_probs, percentile)，基于全量概率计算（非当前页）
    返回 {threshold, total, customers: [...]}
    """
    all_customers = db.query(Customer).filter(
        Customer.predicted_prob.isnot(None)
    ).all()

    if not all_customers:
        raise BizException(3002, "无预测数据，请先进行预测", 400)

    # threshold 基于全量概率计算
    all_probs = [c.predicted_prob for c in all_customers]
    threshold = float(np.quantile(all_probs, percentile))

    # 筛选 >= threshold 的客户，按概率降序
    targets = sorted(all_customers, key=lambda c: c.predicted_prob, reverse=True)
    targets = [c for c in targets if c.predicted_prob >= threshold]

    # 手动分页
    total = len(targets)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = targets[start:end]

    return {
        "threshold": threshold,
        "total": total,
        "customers": [{
            "id": c.id,
            "gender": c.gender,
            "age": c.age,
            "annual_premium": c.annual_premium,
            "predicted_prob": c.predicted_prob,
        } for c in page_items],
    }


def generate_emails(db: Session, user, customer_ids: list[int] = None,
                    limit: int = 5) -> dict:
    """生成营销邮件

    1. 确定目标客户（指定 / top N）
    2. 获取 Prompt 模板
    3. 传递完整客户画像（含反编码字段）给 LLM
    4. 逐条生成邮件并入库
    5. 记录操作日志
    返回 {generated_count, failed_count, records}
    """
    # 取客户列表
    if customer_ids:
        customers = db.query(Customer).filter(Customer.id.in_(customer_ids)).all()
    else:
        # 自动取 top limit 条（按 predicted_prob 降序）
        all_customers = db.query(Customer).filter(
            Customer.predicted_prob.isnot(None)
        ).order_by(Customer.predicted_prob.desc()).limit(limit).all()
        customers = all_customers
        if not customers:
            raise BizException(3002, "无预测数据，请先进行预测", 400)

    # 获取 Prompt 模板
    template = PromptTemplate.get_active(db)
    prompt_content = template.content if template else ""

    # 遍历生成邮件
    generated_count = 0
    failed_count = 0
    records = []
    for c in customers:
        # 传递完整客户画像（llm_service 内部做反编码）
        customer_data = {
            "gender": c.gender,
            "age": c.age,
            "driving_license": c.driving_license,
            "vehicle_age": c.vehicle_age,
            "vehicle_damage": c.vehicle_damage,
            "previously_insured": c.previously_insured,
            "annual_premium": c.annual_premium,
        }
        result = generate_email_content(customer_data, prompt_content)
        EmailRecord.create(
            db, c.id, result["subject"], result["content"], result["status"], user.id
        )
        if result["status"] == "generated":
            generated_count += 1
        else:
            failed_count += 1
        records.append({
            "customer_id": c.id,
            "status": result["status"],
            "subject": result["subject"],
        })

    OperationLog.create(db, user.id, "email_generation",
                        f'{{"generated": {generated_count}, "failed": {failed_count}}}')
    return {
        "generated_count": generated_count,
        "failed_count": failed_count,
        "records": records,
    }
