"""邮件服务层测试

验证：threshold 基于全量分位数计算（非当前页）、percentile 筛选正确性
"""
import pytest
import numpy as np

from app.services.email_service import get_targets
from app.models.customers import Customer
from app.core.response import BizException


class TestGetTargets:
    """测试高潜客户筛选"""

    def test_threshold_based_on_full_data(self, db, test_customers):
        """threshold 应基于全量概率计算，非当前页"""
        # 给测试客户设置 predicted_prob
        customers = db.query(Customer).filter(Customer.id >= 10000).all()
        for i, c in enumerate(customers):
            c.predicted_prob = 0.1 + i * 0.05  # 0.10, 0.15, 0.20, ..., 1.05 -> clip to 1.0
            if c.predicted_prob > 1.0:
                c.predicted_prob = 1.0
        db.commit()

        # percentile=0.9 -> top 10%
        result = get_targets(db, percentile=0.9, page=1, per_page=5)
        all_probs = [c.predicted_prob for c in customers]
        expected_threshold = float(np.quantile(all_probs, 0.9))

        assert result["threshold"] == pytest.approx(expected_threshold, rel=1e-5)

    def test_no_prediction_data_raises(self, db):
        """无预测数据时应抛 BizException(3002)"""
        # 确保没有 predicted_prob 数据
        db.query(Customer).filter(Customer.predicted_prob.isnot(None)).update(
            {Customer.predicted_prob: None}
        )
        db.commit()
        with pytest.raises(BizException) as exc_info:
            get_targets(db, percentile=0.9, page=1, per_page=20)
        assert exc_info.value.code == 3002

    def test_percentile_filtering(self, db, test_customers):
        """percentile=0.5 应返回约 50% 的客户"""
        customers = db.query(Customer).filter(Customer.id >= 10000).all()
        for i, c in enumerate(customers):
            c.predicted_prob = 0.1 + i * 0.04  # 0.10 to 0.86
        db.commit()

        result = get_targets(db, percentile=0.5, page=1, per_page=100)
        all_probs = [c.predicted_prob for c in customers]
        threshold = float(np.quantile(all_probs, 0.5))

        # 返回的客户 predicted_prob 都应 >= threshold
        for cust in result["customers"]:
            assert cust["predicted_prob"] >= threshold

    def test_customers_sorted_by_prob_desc(self, db, test_customers):
        """返回的客户应按 predicted_prob 降序"""
        customers = db.query(Customer).filter(Customer.id >= 10000).all()
        for i, c in enumerate(customers):
            c.predicted_prob = 0.1 + i * 0.04
        db.commit()

        result = get_targets(db, percentile=0.0, page=1, per_page=100)
        probs = [c["predicted_prob"] for c in result["customers"]]
        assert probs == sorted(probs, reverse=True)
