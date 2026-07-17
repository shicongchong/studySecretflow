# 1. 使用 SecretFlow 官方镜像作为基础环境（使用国内阿里云镜像加速）这个有点大 大概5G，后面下了精简版的镜像，大小1.6G
# FROM secretflow-registry.cn-hangzhou.cr.aliyuncs.com/secretflow/secretflow-anolis8:latest
#docker run -it secretflow-registry.cn-hangzhou.cr.aliyuncs.com/secretflow/secretflow-lite-anolis8:latest

# 2. 清空基础镜像的 ENTRYPOINT（关键！）
ENTRYPOINT []

# 3. 把当前目录下的所有文件复制到镜像内的 /app 目录
COPY . /app

# 4. 设置工作目录
WORKDIR /app

# 5. 默认启动 Bash（方便你进去手动执行命令）
CMD ["/bin/bash"]