"""LLM 服务层测试

验证：反编码映射、未配置时降级、JSON 解析、markdown 清理
"""
import json
from unittest.mock import patch, MagicMock

from app.services.llm_service import (
    is_llm_configured, _build_customer_profile, generate_email_content,
    REVERSE_ENCODE_MAP,
)


class TestReverseEncode:
    """测试反编码桥梁"""

    def test_gender_mapping(self):
        """Gender 反编码：Male->性别男, Female->性别女"""
        assert REVERSE_ENCODE_MAP["gender"]["Male"] == "性别男"
        assert REVERSE_ENCODE_MAP["gender"]["Female"] == "性别女"

    def test_driving_license_mapping(self):
        """Driving_License 反编码：0->暂无驾照, 1->持有驾照"""
        assert REVERSE_ENCODE_MAP["driving_license"][0] == "暂无驾照"
        assert REVERSE_ENCODE_MAP["driving_license"][1] == "持有驾照"

    def test_vehicle_age_mapping(self):
        """Vehicle_Age 反编码"""
        assert REVERSE_ENCODE_MAP["vehicle_age"]["< 1 Year"] == "车龄不满1年"
        assert REVERSE_ENCODE_MAP["vehicle_age"]["1-2 Year"] == "车龄1-2年"
        assert REVERSE_ENCODE_MAP["vehicle_age"]["> 2 Years"] == "车龄超过2年"

    def test_vehicle_damage_mapping(self):
        """Vehicle_Damage 反编码"""
        assert REVERSE_ENCODE_MAP["vehicle_damage"]["Yes"] == "车辆曾受损"
        assert REVERSE_ENCODE_MAP["vehicle_damage"]["No"] == "车辆未受损"

    def test_previously_insured_mapping(self):
        """Previously_Insured 反编码"""
        assert REVERSE_ENCODE_MAP["previously_insured"][0] == "未投过保"
        assert REVERSE_ENCODE_MAP["previously_insured"][1] == "已投过保"

    def test_build_customer_profile(self):
        """_build_customer_profile 应将完整客户字段转为自然语言"""
        customer = {
            "gender": "Male",
            "age": 35,
            "driving_license": 1,
            "vehicle_age": "1-2 Year",
            "vehicle_damage": "Yes",
            "previously_insured": 0,
            "annual_premium": 25000,
        }
        profile = _build_customer_profile(customer)
        assert profile["gender"] == "性别男"
        assert profile["age"] == 35
        assert profile["driving_license"] == "持有驾照"
        assert profile["vehicle_age"] == "车龄1-2年"
        assert profile["vehicle_damage"] == "车辆曾受损"
        assert profile["previously_insured"] == "未投过保"
        assert profile["annual_premium"] == 25000


class TestGenerateEmailContent:
    """测试邮件生成"""

    def test_not_configured_returns_failed(self):
        """未配置 LLM_API_KEY 时应返回 status=failed"""
        with patch("app.services.llm_service.is_llm_configured", return_value=False):
            result = generate_email_content(
                {"gender": "Male", "age": 30, "annual_premium": 20000},
                "模板：{gender} {age} {annual_premium}"
            )
        assert result["status"] == "failed"
        assert result["subject"] == ""

    def test_json_parsing_success(self):
        """LLM 返回 JSON 时应正确解析 subject + content"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"subject": "车险优惠", "content": "<p>您好</p>"}'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.is_llm_configured", return_value=True), \
             patch("app.services.llm_service._get_client", return_value=mock_client):
            result = generate_email_content(
                {"gender": "Male", "age": 30, "driving_license": 1,
                 "vehicle_age": "1-2 Year", "vehicle_damage": "Yes",
                 "previously_insured": 0, "annual_premium": 20000},
                "客户：{gender}，{age}岁，{driving_license}，{vehicle_age}，{vehicle_damage}，{previously_insured}，{annual_premium}元"
            )
        assert result["status"] == "generated"
        assert result["subject"] == "车险优惠"
        assert result["content"] == "<p>您好</p>"

    def test_markdown_wrapped_json_parsing(self):
        """LLM 返回 ```json 包裹的 JSON 时应正确清理并解析"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"subject": "促销", "content": "<p>内容</p>"}\n```'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.is_llm_configured", return_value=True), \
             patch("app.services.llm_service._get_client", return_value=mock_client):
            result = generate_email_content(
                {"gender": "Female", "age": 25, "driving_license": 0,
                 "vehicle_age": "< 1 Year", "vehicle_damage": "No",
                 "previously_insured": 1, "annual_premium": 15000},
                "客户：{gender}，{age}岁，{driving_license}，{vehicle_age}，{vehicle_damage}，{previously_insured}，{annual_premium}元"
            )
        assert result["status"] == "generated"
        assert result["subject"] == "促销"
        assert result["content"] == "<p>内容</p>"

    def test_llm_call_failure_returns_failed(self):
        """LLM 调用异常时应降级返回 status=failed"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch("app.services.llm_service.is_llm_configured", return_value=True), \
             patch("app.services.llm_service._get_client", return_value=mock_client):
            result = generate_email_content(
                {"gender": "Male", "age": 30, "driving_license": 1,
                 "vehicle_age": "1-2 Year", "vehicle_damage": "Yes",
                 "previously_insured": 0, "annual_premium": 20000},
                "客户：{gender}，{age}岁"
            )
        assert result["status"] == "failed"

    def test_temperature_is_07(self):
        """LLM 调用应设置 temperature=0.7"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"subject": "s", "content": "c"}'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.is_llm_configured", return_value=True), \
             patch("app.services.llm_service._get_client", return_value=mock_client):
            generate_email_content(
                {"gender": "Male", "age": 30, "driving_license": 1,
                 "vehicle_age": "1-2 Year", "vehicle_damage": "Yes",
                 "previously_insured": 0, "annual_premium": 20000},
                "客户：{gender}，{age}岁，{driving_license}，{vehicle_age}，{vehicle_damage}，{previously_insured}，{annual_premium}元"
            )
        # 检查 create 调用的 temperature 参数
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.7
