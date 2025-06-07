# 使用官方的 Python 镜像作为基础镜像
FROM python:3.13

# 设置工作目录
WORKDIR /app

# 复制项目的依赖文件
COPY ./requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建目标目录
RUN mkdir -p /app/SuperRich

# 复制项目文件
COPY . /app/SuperRich

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 应用
# 在 /app/backend 目录下执行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/backend"]