#docker network create secretflow-net
#docker run -d --name alice-node --network secretflow-net -p 6379:6379 -p 9100:9100 -v $(pwd)/7-22:/app -w /app my_sf_app sleep infinity
#docker run -d --name bob-node --network secretflow-net -p 9200:9200 -v $(pwd)/7-22:/app -w /app my_sf_app sleep infinity
# docker exec alice-node ray start --head --node-ip-address="alice-node" --port="6379" --resources='{"alice": 16}' --include-dashboard=False --disable-usage-stats
#docker exec bob-node ray start --address="alice-node:6379" --resources='{"bob": 16}' --disable-usage-stats

import spu
import secretflow as sf
import numpy as np
import socket
import os

print("=" * 60)
print("SecretFlow Multi-Container Demo")
print("=" * 60)

# 显示当前代码运行在哪个节点
print(f"\n📍 Python 代码运行在: {socket.gethostname()}")
print(f"📍 容器 ID: {os.uname().nodename}")

# 1. 连接到 Ray 集群（主节点在 alice-node）
print("\n[1] 连接到 Ray 集群...")
print("    主节点地址: alice-node:6379")

sf.init(
    parties=['alice', 'bob'], 
    address='alice-node:6379'
)
print("✅ 连接成功！")

# 2. 配置 SPU
print("\n[2] 配置 SPU 网络...")
print("    Alice SPU: alice-node:9100")
print("    Bob SPU:   bob-node:9200")

cluster_def = {
    'nodes': [
        {
            'party': 'alice',
            'address': 'alice-node:9100',
            'listen_addr': '0.0.0.0:9100'
        },
        {
            'party': 'bob',
            'address': 'bob-node:9200',
            'listen_addr': '0.0.0.0:9200'
        },
    ],
    'runtime_config': {
        'protocol': spu.ProtocolKind.SEMI2K,
        'field': spu.FieldType.FM128,
    }
}

spu_device = sf.SPU(cluster_def=cluster_def)
print("✅ SPU 创建成功！")

# 3. 创建参与方
print("\n[3] 创建参与方设备...")
alice = sf.PYU('alice')
bob = sf.PYU('bob')
print("✅ Alice 和 Bob 设备创建成功")

# ============================================================
# 关键部分：明确显示任务在哪个节点执行
# ============================================================

print("\n" + "=" * 60)
print("【验证】任务执行位置")
print("=" * 60)

# 测试1：在 alice 上执行任务
print("\n[测试1] 在 Alice 设备上执行任务...")
alice_test = alice(lambda: f" 这个任务执行在: {socket.gethostname()}")()
alice_result = sf.reveal(alice_test)
print(f"   结果: {alice_result}")

# 测试2：在 bob 上执行任务
print("\n[测试2] 在 Bob 设备上执行任务...")
bob_test = bob(lambda: f" 这个任务执行在: {socket.gethostname()}")()
bob_result = sf.reveal(bob_test)
print(f"   结果: {bob_result}")

# 4. 准备私有数据（分别在各自节点上执行）
print("\n" + "=" * 60)
print("【数据准备】")
print("=" * 60)

print("\n[4] 准备私有数据...")
print("    Alice 数据: [1, 2, 3, 4, 5] (私有)")
print("    Bob 数据:   [6, 7, 8, 9, 10] (私有)")

# alice 准备数据（在 alice 节点执行）
alice_data = alice(lambda: np.array([1, 2, 3, 4, 5]))()
print(f"   ✅ Alice 数据已准备 (执行节点: alice-node)")

# bob 准备数据（在 bob 节点执行）
bob_data = bob(lambda: np.array([6, 7, 8, 9, 10]))()
print(f"   ✅ Bob 数据已准备 (执行节点: bob-node)")

# 5. 执行安全计算（SPU 会同时在两个节点上执行）
print("\n" + "=" * 60)
print("【安全计算】")
print("=" * 60)

print("\n[5] 执行安全计算 (密态加法)...")
print("   ⚡ SPU 将在 alice 和 bob 两个节点上同时执行密态计算")
sum_result = spu_device(lambda x, y: x + y)(alice_data, bob_data)

# 6. 解密结果（在 alice 节点执行）
print("\n[6] 解密结果...")
result = sf.reveal(sum_result)
print(f"✅ 秘密求和结果: {result}")
print(f"   期望结果: [7, 9, 11, 13, 15]")

print("\n" + "=" * 60)
print("【执行摘要】")
print("=" * 60)
print(f"""
📊 任务执行分布:
   - Python 主程序: {socket.gethostname()}
   - Alice 数据准备: alice-node
   - Bob 数据准备: bob-node
   - SPU 密态计算: alice-node + bob-node (多方协同)
   - 结果解密: alice-node

✅ 所有任务成功完成！
""")
print("=" * 60)