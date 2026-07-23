#不同容器不同ip不同集群部署
import secretflow as sf
import numpy as np

cluster_config={
    'parties':{
        'alice':{
            'address':'172.20.0.10:8086',
            'listen_addr':'0.0.0.10:8086'
        },
        'bob':{
            'address':'172.20.0.20:8086',
            'listen_addr':'0.0.0.20:8086'
        },
    
    },
    'self_party':'bob'
}
cluster_def={
    'nodes':[
        {'party':'alice', 'address':'172.20.0.10:8087'},
        {'party':'bob', 'address':'172.20.0.20:8087'},
    ],
    'runtime_config':{
        'protocol':'CHEETAH',
        'field':'FM64',
    }
}
ray_addr = '172.20.0.20:8085'

def get_bob_data():
    """返回 bob 的私有数据"""
    print("   🔵 Bob 正在返回自己的数据...")
    return np.array([1, 2, 3, 4, 5], dtype=np.float32)

def get_alice_data():
    """Alice 的数据函数（占位符，实际在 Alice 那边实现）"""
    raise NotImplementedError("This should be called on Alice's side")

alice=sf.PYU('alice')
bob=sf.PYU('bob')
print("✅ Alice 和 Bob 设备创建成功")
sf.init(address=ray_addr, cluster_config=cluster_config)
alice_data=alice(get_alice_data)()
bob_data=bob(get_bob_data)()
spu=sf.SPU(cluster_def=cluster_def)
print("✅ SPU 创建成功！")
alice_spu=alice_data.to(spu)
bob_spu=bob_data.to(spu)
print("✅ Alice 和 Bob 数据传输到 SPU 成功！")
def sum_data(a, b):
    """在 SPU 上计算 a + b"""
    return a + b

sum_result=spu(sum_data)(alice_spu, bob_spu)
print("✅ SPU 上计算 Alice 和 Bob 数据的和成功！")
sum_result_revealed=sf.reveal(sum_result)
print(f"✅ SPU 上计算结果揭示成功！结果为: {sum_result_revealed}")
