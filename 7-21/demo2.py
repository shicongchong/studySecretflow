import os
import secretflow as sf

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

alice = sf.PYU('alice')
bob = sf.PYU('bob')

alice_data = alice(lambda: 10)()
bob_data = bob(lambda: 20)()

alice_value = sf.reveal(alice_data)
bob_value = sf.reveal(bob_data)

print(f"📊 Alice: {alice_value}")
print(f"📊 Bob: {bob_value}")
print(f"🎯 平均值: {(alice_value + bob_value) / 2}")