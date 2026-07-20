import os
import secretflow as sf

# 从环境变量读取身份
self_party = os.environ.get('SELF_PARTY', 'alice')
ray_port = os.environ.get('RAY_PORT', '9001')

print(f"🚀 启动节点: {self_party}，连接 Ray 端口: {ray_port}")

# 集群配置
cluster_config = {
    'parties': {
        'alice': {
            'address': '127.0.0.1:9002',
            'listen_addr': '0.0.0.0:9002'
        },
        'bob': {
            'address': '127.0.0.1:9004',
            'listen_addr': '0.0.0.0:9004'
        },
    },
    'self_party': self_party
}

# 初始化 SecretFlow
sf.init(address=f'127.0.0.1:{ray_port}', cluster_config=cluster_config)

print(f"✅ 当前节点: {self_party}")

# 创建 PYU 设备
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# 🔑 关键：使用 device 对象的 __call__ 方法
# 这样写：alice(lambda: 10)() 表示在 alice 设备上执行 lambda 函数
alice_data = alice(lambda: 10)()
bob_data = bob(lambda: 20)()

# 揭示结果
alice_value = sf.reveal(alice_data)
bob_value = sf.reveal(bob_data)

print(f"📊 Alice: {alice_value}")
print(f"📊 Bob: {bob_value}")
print(f"🎯 平均值: {(alice_value + bob_value) / 2}")

sf.shutdown()