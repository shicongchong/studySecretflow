import os
import secretflow as sf
import numpy as np

self_party = os.environ.get('SELF_PARTY', 'alice')
ray_port = os.environ.get('RAY_PORT', '9001')

print(f"🚀 启动节点: {self_party}，连接 Ray 端口: {ray_port}")

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

sf.init(address=f'127.0.0.1:{ray_port}', cluster_config=cluster_config)

print(f"✅ 当前节点: {self_party}")

# 定义 PYU 函数
alice = sf.PYU('alice')
bob = sf.PYU('bob')

@alice
def gen_alice():
    return np.array([10.0])

@bob
def gen_bob():
    return np.array([20.0])

# 生成数据（明文）
alice_data = gen_alice()
bob_data = gen_bob()

print(f"📊 Alice 原始数据: {sf.reveal(alice_data)}")
print(f"📊 Bob 原始数据: {sf.reveal(bob_data)}")

# 创建 SPU 设备
spu = sf.SPU(
    cluster_def={
        'nodes': [
            {'party': 'alice', 'address': '127.0.0.1:9002'},
            {'party': 'bob', 'address': '127.0.0.1:9004'},
        ],
        'runtime_config': {
            'protocol': 'CHEETAH',  # 或者 'SEMI2K'
            'field': 'FM64',
        },
    }
)

# 将数据传输到 SPU（转为密文）
alice_spu = alice_data.to(spu)
bob_spu = bob_data.to(spu)

# 在 SPU 上执行密文计算
def compute_avg(x, y):
    return (x + y) / 2

avg_spu = spu(compute_avg)(alice_spu, bob_spu)

# 解密结果并输出
result = sf.reveal(avg_spu.to(alice))
print(f"🎯 平均值（SPU 密文计算）: {result[0]}")

sf.shutdown()