"""LLM 邮件生成服务

【MVC 归属】业务层（Service）--调用 LLM 生成营销邮件内容
【思路】
1. 反编码桥梁：将客户原始字段转为自然语言画像（ML编码 -> LLM自然语言）
2. 模块级单例 client（非每次新建），未配置 LLM_API_KEY 时 client=None
3. 调用 OpenAI 兼容 API（temperature=0.7），正则清理 ```json 包裹 + json.loads 解析
4. 调用失败降级为 status=failed，不抛异常拖垮业务
"""
import re
import json
from app.core.config import settings


# 反编码映射表：ML编码值 -> LLM自然语言（对齐 AI技术方案 4.1 + PRD 6.2）
REVERSE_ENCODE_MAP = {
    "gender": {"Male": "性别男", "Female": "性别女"},
    "driving_license": {0: "暂无驾照", 1: "持有驾照"},
    "vehicle_age": {"< 1 Year": "车龄不满1年", "1-2 Year": "车龄1-2年", "> 2 Years": "车龄超过2年"},
    "vehicle_damage": {"Yes": "车辆曾受损", "No": "车辆未受损"},
    "previously_insured": {0: "未投过保", 1: "已投过保"},
}

# 模块级单例 client
_client = None


def is_llm_configured() -> bool:
    """检查 LLM_API_KEY 是否非空"""
    return bool(settings.LLM_API_KEY)


def _get_client():
    """获取单例 OpenAI client，未配置时返回 None"""
    global _client
    if _client is None and is_llm_configured():
        from openai import OpenAI
        _client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE)
    return _client


def _build_customer_profile(customer: dict) -> dict:
    """将客户原始字段转为自然语言画像（反编码桥梁）

    对齐 AI技术方案 4.1 + PRD 6.2：ML用0/1编码训练，LLM看自然语言
    """
    return {
        "gender": REVERSE_ENCODE_MAP["gender"].get(customer.get("gender"), ""),
        "age": customer.get("age", ""),
        "driving_license": REVERSE_ENCODE_MAP["driving_license"].get(customer.get("driving_license"), ""),
        "vehicle_age": REVERSE_ENCODE_MAP["vehicle_age"].get(customer.get("vehicle_age"), ""),
        "vehicle_damage": REVERSE_ENCODE_MAP["vehicle_damage"].get(customer.get("vehicle_damage"), ""),
        "previously_insured": REVERSE_ENCODE_MAP["previously_insured"].get(customer.get("previously_insured"), ""),
        "annual_premium": customer.get("annual_premium", ""),
    }


def generate_email_content(customer: dict, prompt_template: str) -> dict:
    """生成邮件内容

    1. 反编码：将客户字段转为自然语言画像
    2. 用 str.format 注入 prompt_template 占位符
    3. 若 is_llm_configured()=False，返回 {subject: "", content: filled_prompt, status: "failed"}
    4. 若已配置，调用 OpenAI 兼容 API（temperature=0.7）
    5. 正则清理 ```json 包裹 + json.loads 解析 subject + content
    6. 调用失败降级返回 status=failed

    返回 {subject, content, status}
    """
    # 反编码 + 填充模板占位符
    profile = _build_customer_profile(customer)
    filled = prompt_template.format(**profile)

    if not is_llm_configured():
        return {"subject": "", "content": filled, "status": "failed"}

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": filled}],
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()
        # 正则清理 markdown 包裹（```json ... ```）
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        parsed = json.loads(text)
        return {
            "subject": parsed.get("subject", ""),
            "content": parsed.get("content", ""),
            "status": "generated",
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "LLM 邮件生成失败: %s: %s", type(e).__name__, e
        )
        return {"subject": "", "content": filled, "status": "failed"}
