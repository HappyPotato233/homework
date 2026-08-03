"""pytest 全局配置：测试用临时数据库 + Flask test client + 测试数据"""
import os
import tempfile

# 在导入 app 之前设置测试环境变量（pydantic-settings 读 env var 覆盖 .env）
_test_db = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db}"

_test_model_dir = tempfile.mkdtemp(prefix="test_models_")
os.environ["MODEL_DIR"] = _test_model_dir

import pytest
from app import create_app
from app.core.database import SessionLocal, Base, engine


@pytest.fixture(scope="session")
def app():
    """创建 Flask 应用（session 级，整个测试会话共用）"""
    app = create_app()
    yield app
    # 清理：先释放引擎连接再删除测试数据库
    engine.dispose()
    try:
        if os.path.exists(_test_db):
            os.remove(_test_db)
    except PermissionError:
        pass  # Windows 下文件可能仍被占用，忽略


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def db(app):
    """每个测试用独立的 DB session"""
    with app.app_context():
        session = SessionLocal()
        yield session
        session.close()


@pytest.fixture
def test_customers(db):
    """插入测试客户数据（含正负样本），测试后清理"""
    from app.models.customers import Customer

    customers = []
    for i in range(20):
        c = Customer(
            id=10000 + i,
            gender="Male" if i % 2 == 0 else "Female",
            age=20 + i % 30,
            driving_license=1,
            region_code=10.0 + i,
            previously_insured=i % 2,
            vehicle_age="< 1 Year" if i % 3 == 0 else ("1-2 Year" if i % 3 == 1 else "> 2 Years"),
            vehicle_damage="Yes" if i % 2 == 0 else "No",
            annual_premium=10000.0 + i * 1000,
            policy_sales_channel=100.0 + i,
            vintage=10 + i,
            response=0 if i < 14 else 1,  # 14 个负样本，6 个正样本（~30% 正样本）
        )
        db.add(c)
        customers.append(c)
    db.commit()
    yield customers
    # 清理
    db.query(Customer).filter(Customer.id >= 10000).delete()
    db.commit()
