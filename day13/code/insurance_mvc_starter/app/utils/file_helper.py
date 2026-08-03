"""文件读取工具

【MVC 归属】工具层（Utils）--纯函数，读取静态文件内容
"""
from pathlib import Path
from app.core.response import BizException

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def read_static_file(filename: str) -> str:
    """读取 app/static/ 下的文件内容

    文件缺失抛 BizException(5000)
    """
    path = BASE_DIR / "app" / "static" / filename
    if not path.exists():
        raise BizException(5000, "前端页面资源缺失", 500)
    return path.read_text(encoding="utf-8")
