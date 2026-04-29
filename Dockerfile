FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（libpq-dev 是 psycopg2 必需的）
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（显式装 psycopg2-binary 确保不失败）
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade psycopg2-binary pymysql

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
