# 使用官方Python 3.10基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /usr/src/ploughmanai

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露Gradio默认端口
EXPOSE 7860

# 设置环境变量使Gradio监听所有网络接口
ENV GRADIO_SERVER_NAME="0.0.0.0"

# 启动应用
CMD ["python", "app.py"]