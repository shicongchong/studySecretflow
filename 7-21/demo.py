import os
import secretflow as sf
import numpy as np
import time

self_party = os.environ.get('SELF_PARTY', 'alice')
ray_address = os.environ.get('RAY_ADDRESS', '127.0.0.1:9003')

print(f"🔵 当前节点角色: {self_party}")
print(f"📍 Ray 地址: {ray_address}")

cluster_config = {
    'parties': {
        'alice': {
            'address': 'alice-node:9001',
            'listen_addr': '0.0.0.0:9001'
        },
        'bob': {
            'address': 'bob-node:9002',
            'listen_addr': '0.0.0.0:9002'
        }
    },
    'self_party': self_party
}

if self_party == 'bob':
    # ===== Bob: 监听模式 =====
    print("🟩 Bob 初始化中...")
    sf.init(address=ray_address, cluster_config=cluster_config)
    print("✅ Bob 初始化完成")
    print("🟩 Bob: 已就绪，监听端口 9002，等待 Alice 发起连接...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🟩 Bob: 收到退出信号")
    finally:
        sf.shutdown()

else:
    # ===== Alice: 计算模式 =====
    print("🟦 Alice: 等待 Bob 启动...")
    time.sleep(5)  # 等待 Bob 先启动
    
    print("🟦 Alice 初始化中...")
    sf.init(address=ray_address, cluster_config=cluster_config)
    print("✅ Alice 初始化完成")
    print("🟦 Alice: 开始执行联邦学习任务...")
    
    alice = sf.PYU('alice')
    bob = sf.PYU('bob')
    
    spu = sf.SPU(
        cluster_def={
            'nodes': [
                {'party': 'alice', 'address': 'alice-node:9001'},
                {'party': 'bob', 'address': 'bob-node:9002'},
            ],
            'runtime_config': {
                'protocol': 'CHEETAH',
                'field': 'FM64',
            },
        }
    )
    
    @alice
    def gen_alice():
        return np.array([10.0])
    
    @bob
    def gen_bob():
        return np.array([5.0])
    
    print("📊 生成数据...")
    alice_data = gen_alice()
    bob_data = gen_bob()
    
    print("📤 传输数据到 SPU...")
    alice_spu = alice_data.to(spu)
    bob_spu = bob_data.to(spu)
    
    def compute_avg(x, y):
        return (x + y) / 2
    
    print("🧮 SPU 计算中...")
    avg_spu = spu(compute_avg)(alice_spu, bob_spu)
    
    print("🔓 解密结果...")
    result = sf.reveal(avg_spu.to(alice))
    print(f"✅ 平均值: {result[0]}")
    
    sf.shutdown()
    print("🟦 Alice: 任务完成！")