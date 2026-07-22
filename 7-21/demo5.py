import secretflow as sf
import numpy as np
import time

# 获取角色
self_party = 'alice'  # 运行 alice 时改成 'alice'，运行 bob 时改成 'bob'

# 集群配置
cluster_config = {
    'parties': {
        'alice': {'address': 'alice-node:9001', 'listen_addr': '0.0.0.0:9001'},
        'bob': {'address': 'bob-node:9002', 'listen_addr': '0.0.0.0:9002'},
    },
    'self_party': self_party
}

# 初始化
sf.init(address='alice-node:9003', cluster_config=cluster_config)
print(f"✅ {self_party} 初始化完成")

if self_party == 'alice':
    # Alice 创建数据并计算
    alice = sf.PYU('alice')
    bob = sf.PYU('bob')
    
    # 生成数据
    @alice
    def data_alice():
        return np.array([10.0])
    
    @bob
    def data_bob():
        return np.array([20.0])
    
    a = data_alice()
    b = data_bob()
    
    # 创建 SPU
    spu = sf.SPU(
        cluster_def={
            'nodes': [
                {'party': 'alice', 'address': 'alice-node:9001'},
                {'party': 'bob', 'address': 'bob-node:9002'},
            ],
            'runtime_config': {'protocol': 'CHEETAH', 'field': 'FM64'},
        }
    )
    
    # 加密计算
    a_spu = a.to(spu)
    b_spu = b.to(spu)
    result = spu(lambda x, y: (x + y) / 2)(a_spu, b_spu)
    
    # 解密输出
    print(f"🎯 结果: {sf.reveal(result)}")
    
    sf.shutdown()
else:
    # Bob 保持运行
    while True:
        time.sleep(1)