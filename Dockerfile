# 使用官方的Python基础镜像
FROM python:3.8

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录中
COPY ./tmp /app/
COPY ./app.py /app/
COPY ./requirements.txt /app/

# 使用pip安装指定的依赖
RUN pip install -r requirements.txt

# 指定容器启动后执行的命令
CMD ["python", "app.py"]
