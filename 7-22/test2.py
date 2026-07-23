import secretflow as sf

# 关键：连接到正确的 Ray Head 地址
sf.init(
    address='127.0.0.1:9001',  # 必须与 Ray 启动时的地址一致
    parties=['alice', 'bob'],
    cluster_config={
        'parties': {
            'alice': {
                'address': '127.0.0.1:9002',
                'listen_addr': '0.0.0.0:9002'
            },
            'bob': {
                'address': '127.0.0.1:9003',
                'listen_addr': '0.0.0.0:9003'
            }
        },
        'self_party': 'alice'
    }
)

# 测试代码
alice = sf.PYU('alice')
bob = sf.PYU('bob')
print("✅ 连接成功！")