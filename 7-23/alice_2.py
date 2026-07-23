#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import secretflow as sf
import numpy as np
import pandas as pd
import os

# ========== 1. 配置 ==========
ALICE_IP = "172.20.0.10"
BOB_IP = "172.20.0.20"

# ========== 2. 初始化 ==========
sf.init(
    parties=['alice', 'bob'],
    address=f'{ALICE_IP}:8085'
)
print("✅ SecretFlow 初始化成功")

alice = sf.PYU('alice')
bob = sf.PYU('bob')
print("✅ PYU 设备创建成功")


# ========== 3. ⭐ Alice 从本地文件读取数据 ==========
def get_alice_data():
    """在 Alice 节点执行，读取 Alice 的本地文件"""
    import pandas as pd
    print("🔵 Alice 正在读取本地文件...")
    
    # 这个路径只在 Alice 节点存在！
    data = pd.read_csv('/alice_data/private.csv')
    print(f"🔵 Alice 读取了 {len(data)} 条数据")
    return data['value'].values


# ========== 4. ⭐ Bob 从本地文件读取数据 ==========
def get_bob_data():
    """在 Bob 节点执行，读取 Bob 的本地文件"""
    import pandas as pd
    print("🟢 Bob 正在读取本地文件...")
    
    # 这个路径只在 Bob 节点存在！
    data = pd.read_csv('/bob_data/private.csv')
    print(f"🟢 Bob 读取了 {len(data)} 条数据")
    return data['value'].values


# ========== 5. ⭐ 从本地文件读取数据并上传到 SPU ==========
def load_and_upload_to_spu(data_path, party):
    """通用函数：在指定节点读取本地文件并上传到 SPU"""
    import pandas as pd
    data = pd.read_csv(data_path)
    return data['value'].values


# ========== 6. 执行 ==========
print("\n" + "=" * 60)
print("开始从各参与方本地读取数据...")
print("=" * 60)

# 在 Alice 节点执行
alice_data = alice(get_alice_data)()
print(f"🔵 Alice 数据: {alice_data}")

# 在 Bob 节点执行
bob_data = bob(get_bob_data)()
print(f"🟢 Bob 数据: {bob_data}")

print("\n✅ 数据读取成功！")


# ========== 7. SPU ==========
cluster_def = {
    'nodes': [
        {'party': 'alice', 'address': f'{ALICE_IP}:8087'},
        {'party': 'bob', 'address': f'{BOB_IP}:8087'},
    ],
    'runtime_config': {
        'protocol': 'CHEETAH',
        'field': 'FM64',
    }
}
spu = sf.SPU(cluster_def=cluster_def)
print("✅ SPU 创建成功")


# ========== 8. 上传到 SPU ==========
print("\n📤 上传数据到 SPU...")
alice_spu = alice_data.to(spu)
bob_spu = bob_data.to(spu)
print("✅ 数据上传成功")


# ========== 9. 计算 ==========
print("\n🔄 执行密态计算...")

def spu_sum(a, b):
    return np.sum(a) + np.sum(b)

result = spu(spu_sum)(alice_spu, bob_spu)
total_sum = sf.reveal(result)
print(f"✅ 全局总和: {total_sum}")

def spu_mean(a, b):
    total = np.sum(a) + np.sum(b)
    count = len(a) + len(b)
    return total / count

result = spu(spu_mean)(alice_spu, bob_spu)
mean_value = sf.reveal(result)
print(f"✅ 全局均值: {mean_value:.2f}")


print("\n" + "=" * 60)
print("✅ 所有计算完成！数据未离开各自节点")
print("=" * 60)