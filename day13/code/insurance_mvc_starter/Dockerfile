# ===== 基础镜像 =====
FROM docker.1ms.run/library/python:3.12-slim

# ===== 系统依赖 =====
# fonts-wqy-zenhei: matplotlib 中文渲染（Linux 容器无 SimHei）
# 切换阿里云 apt 源（加速国内构建）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
        fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

# ===== 工作目录 =====
WORKDIR /app

# ===== 先装依赖（利用 Docker 层缓存） =====
# 切换清华 PyPI 源（加速国内构建）
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
        -r requirements.txt gunicorn==22.0.0

# ===== 复制项目代码 =====
COPY . .

# ===== 创建数据目录 =====
RUN mkdir -p /app/instance /app/data/models

# ===== 端口映射 =====
EXPOSE 5000

# ===== 生产模式启动（gunicorn） =====
# 开发模式可用：docker-compose.yml 中覆盖 command 为 python run.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]
