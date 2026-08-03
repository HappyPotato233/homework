"""EDA 可视化工具

【MVC 归属】工具层 --纯函数，不依赖业务层
【思路】
1. 用 matplotlib（Agg 后端）+ seaborn 生成图表
2. 4 种图表：response_distribution / gender_response / age_distribution / premium_distribution
3. 图表转 base64 PNG 返回，前端可直接 <img src="data:image/png;base64,..."> 显示
4. 生成后关闭 figure 防止内存泄漏

为什么用 Agg 后端？
  Agg 是非交互式后端，不弹窗、不依赖 GUI，适合服务端渲染图片。
"""
import base64
import io
import matplotlib
matplotlib.use("Agg")  # 必须在 import pyplot 之前设置
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session
from app.models.customers import Customer

# 支持的图表类型
VALID_CHART_TYPES = {
    "response_distribution",
    "gender_response",
    "age_distribution",
    "premium_distribution",
}

# 全局样式（sns.set_theme 会重置 rcParams，必须在其之后配置中文字体）
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "DejaVu Sans"]  # Windows/Linux 兼容
plt.rcParams["axes.unicode_minus"] = False    # 解决负号"-"显示方块问题


def generate_chart(db: Session, chart_type: str) -> dict:
    """生成指定类型的图表，返回 {chart_type, image_base64, format}

    逐字思路：
    1. 查数据（id/gender/age/annual_premium/response 四列够画全部图）
    2. 按 chart_type 分发到对应的绘图函数
    3. 保存到内存 BytesIO -> base64 编码
    4. 关闭 figure 防泄漏
    """
    rows = db.query(
        Customer.id, Customer.gender, Customer.age,
        Customer.annual_premium, Customer.response,
    ).all()

    if not rows:
        # 无数据画一个空图提示
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "暂无数据，请先上传", ha="center", va="center", fontsize=16)
        ax.set_axis_off()
        return _fig_to_base64(fig, chart_type)

    # 拆列
    genders = [r[1] for r in rows]
    ages = [r[2] for r in rows if r[2] is not None]
    premiums = [r[3] for r in rows if r[3] is not None]
    responses = [r[4] for r in rows if r[4] is not None]

    if chart_type == "response_distribution":
        fig = _draw_response_distribution(responses)
    elif chart_type == "gender_response":
        fig = _draw_gender_response(genders, responses)
    elif chart_type == "age_distribution":
        fig = _draw_age_distribution(ages)
    elif chart_type == "premium_distribution":
        fig = _draw_premium_distribution(premiums)
    else:
        # 不会走到这里，路由层已校验
        raise ValueError(f"未知图表类型: {chart_type}")

    return _fig_to_base64(fig, chart_type)


def _draw_response_distribution(responses: list) -> plt.Figure:
    """响应分布饼图：0（未响应）vs 1（响应）"""
    fig, ax = plt.subplots(figsize=(8, 6))
    counts = {"0": responses.count(0), "1": responses.count(1)}
    labels = [f"未响应 (0)\n{counts['0']}", f"响应 (1)\n{counts['1']}"]
    colors = ["#5B9BD5", "#ED7D31"]
    ax.pie(counts.values(), labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax.set_title("客户响应分布 (Response Distribution)", fontsize=14)
    return fig


def _draw_gender_response(genders: list, responses: list) -> plt.Figure:
    """性别 x 响应 分组柱状图"""
    fig, ax = plt.subplots(figsize=(8, 6))
    # 统计交叉表
    data = {"Male": {"0": 0, "1": 0}, "Female": {"0": 0, "1": 0}}
    for g, r in zip(genders, responses):
        if g in data and r in (0, 1):
            data[g][str(r)] += 1

    x = list(data.keys())
    no_vals = [data[g]["0"] for g in x]
    yes_vals = [data[g]["1"] for g in x]
    width = 0.35
    x_pos = range(len(x))

    ax.bar([i - width / 2 for i in x_pos], no_vals, width, label="未响应 (0)", color="#5B9BD5")
    ax.bar([i + width / 2 for i in x_pos], yes_vals, width, label="响应 (1)", color="#ED7D31")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x)
    ax.set_ylabel("人数")
    ax.set_title("性别与响应关系 (Gender vs Response)", fontsize=14)
    ax.legend()
    return fig


def _draw_age_distribution(ages: list) -> plt.Figure:
    """年龄分布直方图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(ages, bins=30, color="#70AD47", edgecolor="white", alpha=0.8)
    ax.set_xlabel("年龄")
    ax.set_ylabel("人数")
    ax.set_title("客户年龄分布 (Age Distribution)", fontsize=14)
    return fig


def _draw_premium_distribution(premiums: list) -> plt.Figure:
    """年保费分布直方图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(premiums, bins=40, color="#FFC000", edgecolor="white", alpha=0.8)
    ax.set_xlabel("年保费 (Annual Premium)")
    ax.set_ylabel("人数")
    ax.set_title("年保费分布 (Premium Distribution)", fontsize=14)
    return fig


def _fig_to_base64(fig: plt.Figure, chart_type: str) -> dict:
    """Figure 转 base64 PNG，返回 API 响应格式"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)  # 关闭 figure 防止内存泄漏
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return {
        "chart_type": chart_type,
        "image_base64": image_base64,
        "format": "png",
    }
