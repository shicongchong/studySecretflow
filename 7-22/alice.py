#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import secretflow as sf
import numpy as np
import time
import warnings
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')


# ========== ⭐ Alice 的数据 ==========
alice_private_data = np.array([1, 2, 3, 4, 5], dtype=np.float32)


# ========== ⭐ Alice 的数据返回函数 ==========
def get_alice_data():
    """返回 Alice 的私有数据"""
    print("   🔵 Alice 正在返回自己的数据...")
    return alice_private_data


# ========== ⭐ 添加：Bob 函数的占位符 ==========
# 这个函数在 Alice 这边只是"占位"，让 Python 能找到这个名字
# 真正的实现在 Bob 那边
def get_bob_data():
    """Bob 的数据函数（占位符，实际在 Bob 那边实现）"""
    raise NotImplementedError("This should be called on Bob's side")


def main():
    # ========== 1. 初始化 ==========
    ray_addr = '172.20.0.2:8085'
    cluster_config = {
        'parties': {
            'alice': {
                'address': '172.20.0.2:8086',
                'listen_addr': '0.0.0.0:8086'
            },
            'bob': {
                'address': '172.20.0.3:8086',
                'listen_addr': '0.0.0.0:8086'
            },
        },
        'self_party': 'alice'
    }

    print("=" * 60)
    print("🔵 Alice 节点启动...")
    sf.init(address=ray_addr, cluster_config=cluster_config)
    print("✅ Alice 初始化成功！\n")

    # ========== 2. 创建 SPU ==========
    spu = sf.SPU(
        cluster_def={
            'nodes': [
                {'party': 'alice', 'address': '172.20.0.2:8087'},
                {'party': 'bob', 'address': '172.20.0.3:8087'},
            ],
            'runtime_config': {
                'protocol': 'CHEETAH',
                'field': 'FM64',
            }
        }
    )
    print("✅ SPU 设备创建成功\n")

    # ========== 3. 创建 PYU ==========
    alice_pyu = sf.PYU('alice')
    bob_pyu = sf.PYU('bob')

    # ========== 4. Alice 获取自己的数据 ==========
    alice_local = alice_pyu(get_alice_data)()
    print(f"🔵 Alice 数据: {alice_local}")

    # ========== 5. Alice 远程请求 Bob 的数据 ==========
    print("📡 Alice 正在请求 Bob 的数据...")
    bob_local = bob_pyu(get_bob_data)()  # ✅ 现在能找到 get_bob_data 了！
    print(f"🟢 Bob 数据: {bob_local}\n")

    # ========== 6. 上传到 SPU ==========
    print("📤 正在上传数据到 SPU...")
    alice_spu = alice_local.to(spu)
    bob_spu = bob_local.to(spu)
    print("✅ 数据已上传\n")

    # ========== 7. 计算 ==========
    print("🔄 执行密态计算...")

    def spu_add(a, b):
        return a + b
    add_result = spu(spu_add)(alice_spu, bob_spu)
    print("   ✓ 加法完成")

    def spu_sum(a, b):
        return np.sum(a) + np.sum(b)
    sum_result = spu(spu_sum)(alice_spu, bob_spu)
    print("   ✓ 求和完成")

    print("\n📊 结果：")
    print(f"  加法: {sf.reveal(add_result)}")
    print(f"  求和: {sf.reveal(sum_result)}")

    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)

    try:
        time.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 退出")
        sf.shutdown()


if __name__ == '__main__':
    main()