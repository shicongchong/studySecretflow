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

# 创建 PYU 设备
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# 生成数据（使用 lambda）
alice_data = alice(lambda: np.array([10.0]))()
bob_data = bob(lambda: np.array([20.0]))()

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
            'protocol': 'CHEETAH',
            'field': 'FM64',
        },
    }
)

# 数据加密并传输到 SPU
alice_spu = alice_data.to(spu)
bob_spu = bob_data.to(spu)

# SPU 密文计算
avg_spu = spu(lambda x, y: (x + y) / 2)(alice_spu, bob_spu)

# 解密结果
result = sf.reveal(avg_spu.to(alice))
print(f"🎯 平均值（SPU 密文计算）: {result[0]}")

sf.shutdown()