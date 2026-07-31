"""Excel 解析工具

【MVC 归属】工具层 --纯函数，不依赖业务层
【思路】
1. parse_excel: pandas 读 Excel -> 校验列名 -> 逐行转 dict -> 返回 (rows, quality_report)
2. build_quality_report: 基于 DataFrame 计算质量报告（缺失值/重复行/类型）
3. 解析失败抛 BizException(2002)

为什么用 pandas 而不是 openpyxl 直接读？
  pandas.read_excel 底层也是调 openpyxl，但封装了 DataFrame 结构，
  统计缺失值/重复行/类型只需一行代码，教学场景更简洁。
"""
import io
import pandas as pd
from werkzeug.datastructures import FileStorage
from app.core.response import BizException

# Excel 列名 -> 数据库字段名映射
# 解析时保留原始列名（Gender/Age 等），入库时统一转小写下划线
COLUMN_MAP = {
    "id": "id",
    "Gender": "gender",
    "Age": "age",
    "Driving_License": "driving_license",
    "Region_Code": "region_code",
    "Previously_Insured": "previously_insured",
    "Vehicle_Age": "vehicle_age",
    "Vehicle_Damage": "vehicle_damage",
    "Annual_Premium": "annual_premium",
    "Policy_Sales_Channel": "policy_sales_channel",
    "Vintage": "vintage",
    "Response": "response",
}

# 必须存在的列（缺一不可）
REQUIRED_COLUMNS = list(COLUMN_MAP.keys())


def parse_excel(file_storage: FileStorage) -> tuple[list[dict], dict]:
    """解析 Excel 文件 -> 返回 (rows, quality_report)

    逐字思路：
    1. 用 pandas.read_excel 读文件到 DataFrame
    2. 校验列名是否齐全（缺列抛 BizException(2002)）
    3. 逐行转 dict，列名转小写下划线（通过 COLUMN_MAP 映射）
    4. 计算 quality_report（缺失值/重复行/类型）
    5. 解析失败抛 BizException(2002)
    """
    try:
        df = pd.read_excel(io.BytesIO(file_storage.read()))
    except Exception as e:
        raise BizException(2002, f"Excel解析失败: {e}", 400)

    # 校验列名：必须包含所有 REQUIRED_COLUMNS
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise BizException(
            2002,
            f"Excel缺少必要列: {', '.join(missing_cols)}",
            400,
        )

    # 计算质量报告（基于原始 DataFrame）
    quality_report = build_quality_report(df)

    # 逐行转 dict，列名映射为数据库字段名
    rows = []
    for _, row in df.iterrows():
        item = {}
        for excel_col, db_col in COLUMN_MAP.items():
            val = row[excel_col]
            # pandas 的 NaN 统一转 None 入库
            if pd.isna(val):
                item[db_col] = None
            else:
                # numpy 类型转 Python 原生类型
                item[db_col] = val.item() if hasattr(val, "item") else val
        rows.append(item)

    return rows, quality_report


def build_quality_report(df: pd.DataFrame) -> dict:
    """基于 DataFrame 计算数据质量报告

    逐字思路：
    1. total_rows: len(df) 总行数
    2. total_cols: len(df.columns) 总列数
    3. missing_values: 各列 isna().sum() 缺失数
    4. duplicates: duplicated().sum() 重复行数
    5. dtypes: 各列数据类型字符串
    """
    return {
        "total_rows": int(len(df)),
        "total_cols": int(len(df.columns)),
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "duplicates": int(df.duplicated().sum()),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }
