# 1. 使用 SecretFlow 官方镜像作为基础环境（使用国内阿里云镜像加速）这个有点大 大概5G，后面下了精简版的镜像，大小1.6G
FROM secretflow-registry.cn-hangzhou.cr.aliyuncs.com/secretflow/secretflow-anolis8:latest
#docker run -it secretflow-registry.cn-hangzhou.cr.aliyuncs.com/secretflow/secretflow-lite-anolis8:latest
#FROM secretflow-registry.cn-hangzhou.cr.aliyuncs.com/secretflow/secretflow-lite-anolis8:latest


# 2. 清空基础镜像的 ENTRYPOINT（关键！）



#基础镜像可能设置了默认的 ENTRYPOINT（比如启动时打印欢迎信息），这会导致你传入的命令被忽略。
#我们用 ENTRYPOINT [] 把它清空，这样你传入的命令（如 python /app/app.py）就能正常执行。
#情况	结果
#不清空	容器启动时先执行基础镜像的欢迎脚本，然后你的命令可能被忽略
#清空	容器启动时直接执行你传入的命令

ENTRYPOINT []

# 3. 把当前目录下的所有文件复制到镜像内的 /app   目录
COPY ./7-21/demo.py /app/
# 🔑 把 ray 装进镜像里
RUN pip install --no-cache-dir ray -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 设置工作目录
WORKDIR /app

# 5. 默认启动 Bash（方便你进去手动执行命令）
CMD ["/bin/bash"]