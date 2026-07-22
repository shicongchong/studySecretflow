import spu
import secretflow as sf
import numpy as np

# 1. 仍然需要先初始化Ray集群
sf.init(parties=['alice', 'bob'], address='192.168.200.1:6379')

# 2. 定义这个“虚拟大脑”SPU的网络拓扑结构
cluster_def = {
    'nodes': [
        {
            'party': 'alice',
            # 阿里这边SPU服务的地址，注意端口不能和Ray的9001冲突
            'address': '192.168.200.1:9100',
            'listen_addr': '0.0.0.0:9100'
        },
        {
            'party': 'bob',
            # 百度这边SPU服务的地址
            'address': '192.168.200.1:9200', # 注意：因为是一台电脑模拟，IP相同但端口不同
            'listen_addr': '0.0.0.0:9200'
        },
    ],
    'runtime_config': {
        'protocol': spu.ProtocolKind.SEMI2K, # 使用的安全协议
        'field': spu.FieldType.FM128,
    }
}

# 3. 创建这个“虚拟大脑”的实例
spu_device = sf.SPU(cluster_def=cluster_def)

# 4. 现在，我们让阿里和百度的数据，在这个“虚拟大脑”里进行秘密计算
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# 假设阿里有数据 [1, 2, 3, 4, 5]
alice_data = alice(lambda: np.array([1, 2, 3, 4, 5]))()
# 假设百度有数据 [6, 7, 8, 9, 10]
bob_data = bob(lambda: np.array([6, 7, 8, 9, 10]))()

# 我们将两个数据放到SPU设备上，进行求和运算
# 整个过程，阿里和百度都不知道对方的具体数据，但能得到正确结果
sum_result = spu_device(lambda x, y: x + y)(alice_data, bob_data)

# 5. 解密并打印最终结果
print(f"阿里和百度数据秘密求和的结果是：{sf.reveal(sum_result)}")
# 输出: [ 7  9 11 13 15]