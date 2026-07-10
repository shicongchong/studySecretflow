# ============================================================
# 第1步：导入所有需要的工具包
# ============================================================

import tempfile      # 创建临时文件夹（下载的数据暂存这里）
import tensorflow as tf  # 用来下载花朵数据集
import os            # 处理文件路径
import glob          # 查找文件（找所有.jpg图片）
import numpy as np   # 把图片变成数字数组
import cv2           # 读取和处理图片（pip install opencv-python）

# ============================================================
# 第2步：下载花朵数据集
# ============================================================

# 创建一个临时文件夹（用完可以自动删除）
#_temp_dir = tempfile.mkdtemp()

# 从网上下载花朵数据集（5种花：雏菊、蒲公英、玫瑰、向日葵、郁金香）
'''
已经下载过，这里注释掉下载代码 
path_to_flower_dataset = tf.keras.utils.get_file(
    "flower_photos",  # 下载后的文件夹名字
    "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz",  # 下载链接
    untar=True,       # True表示自动解压（就像解压zip文件）
    cache_dir=_temp_dir,  # 存到临时文件夹
)
'''
path_to_flower_dataset="/tmp/tmp_flowers/datasets/flower_photos"
print(f"数据集下载位置: {path_to_flower_dataset}")

# ============================================================
# 第3步：定义花朵类别（5种花）
# ============================================================

root = path_to_flower_dataset  # 数据集根目录
classes = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']
# 索引对应关系：
# classes[0] = 'daisy'      → 标签 0（雏菊）
# classes[1] = 'dandelion'  → 标签 1（蒲公英）
# classes[2] = 'roses'      → 标签 2（玫瑰）
# classes[3] = 'sunflowers' → 标签 3（向日葵）
# classes[4] = 'tulips'     → 标签 4（郁金香）

# ============================================================
# 第4步：收集所有图片的路径和标签
# ============================================================

img_paths = []  # 空列表，用来存所有图片的路径
labels = []     # 空列表，用来存每张图片的标签（0,1,2,3,4）

# 循环处理每种花
for i, label in enumerate(classes):
    # i = 0,1,2,3,4
    # label = 'daisy', 'dandelion', 'roses', 'sunflowers', 'tulips'
    
    # 找到这种花文件夹下的所有.jpg图片
    # os.path.join(root, label, "*.jpg") 
    # 例如: flower_photos/daisy/*.jpg
    cls_img_paths = glob.glob(os.path.join(root, label, "*.jpg"))
    
    # 把这些图片路径加到总列表
    img_paths.extend(cls_img_paths)
    
    # 给这些图片打标签
    # [i] * len(cls_img_paths) 表示：如果有100张图片，就创建100个i
    # 比如雏菊(i=0)有100张，就创建100个0
    labels.extend([i] * len(cls_img_paths))

 # 假设 i = 0，有 3 张图片
# ❌ 错误写法：直接用 i
#labels.extend(i * 3)  
# TypeError: 'int' object is not iterable
# 报错！因为 i * 3 = 0，0 不能用来扩展列表
# ✅ 正确写法：用 [i]
#labels.extend([i] * 3)  
# [i] * 3 = [0, 0, 0]
# 可以扩展列表，结果是 [0, 0, 0]
# 把标签列表转成NumPy数组（计算机更喜欢这种格式）

labels = np.array(labels)

print(f"总共找到 {len(img_paths)} 张图片")
print(f"标签数量: {len(labels)}")

# ============================================================
# 第5步：把图片转成数字（NumPy数组）
# ============================================================

img_numpys = []  # 空列表，用来存所有图片的数字表示

# 循环处理每张图片
for img_path in img_paths:
    # 5.1 用OpenCV读取图片
    # cv2.imread() 把图片读成数字数组
    # 形状: (高度, 宽度, 3通道RGB)
    img_numpy = cv2.imread(img_path)
    
    # 5.2 缩放到统一大小 240×240
    # 不管原图多大，都变成240×240（方便批量处理）
    img_numpy = cv2.resize(img_numpy, (240, 240))
    
    # 5.3 改变形状，加一个维度
    # 从 (240, 240, 3) → (1, 240, 240, 3)
    # 前面的1表示"1张图片"
    img_numpy = np.reshape(img_numpy, (1, 240, 240, 3))
    
    # 5.4 存到列表
    img_numpys.append(img_numpy)

# 5.5 把所有图片拼在一起
# axis=0 表示在第1个维度拼接（增加图片数量）
# 假设有3670张图片，每张是(1,240,240,3)
# 拼接后变成 (3670, 240, 240, 3)
images = np.concatenate(img_numpys, axis=0)

print(f"所有图片的形状: {images.shape}")
print(f"所有标签的形状: {labels.shape}")
# 输出示例: (3670, 240, 240, 3) 和 (3670,)

# ============================================================
# 第6步：把数据分给 Alice 和 Bob（各50%）
# ============================================================

per = 0.5  # 每个人分50%

# 计算每个人应该分多少张
# int() 取整数（比如 3670 * 0.5 = 1835）
split_point = int(per * images.shape[0])

# Alice 拿前一半
alice_images = images[:split_point, :, :, :]
alice_label = labels[:split_point]

# Bob 拿后一半
bob_images = images[split_point:, :, :, :]
bob_label = labels[split_point:]

print("=" * 50)
print("数据分配结果:")
print(f"Alice 图片: {alice_images.shape}, 标签: {alice_label.shape}")
print(f"Bob 图片: {bob_images.shape}, 标签: {bob_label.shape}")
print("=" * 50)

# ============================================================
# 第7步：保存为 .npz 文件（NumPy压缩格式）
# ============================================================

# 保存 Alice 的数据
np.savez(
    "flower_alice.npz",  # 文件名
    image=alice_images,  # 键名'image'，值是图片数据
    label=alice_label    # 键名'label'，值是标签数据
)

# 保存 Bob 的数据
np.savez(
    "flower_bob.npz",
    image=bob_images,
    label=bob_label
)

print("✅ 数据保存成功！")
print("   - flower_alice.npz (Alice的数据)")
print("   - flower_bob.npz (Bob的数据)")

# ============================================================
# 第8步：导入 SecretFlow 并加载数据
# ============================================================

import secretflow as sf
from secretflow.data.ndarray import load

# 8.1 初始化 SecretFlow
# 告诉SecretFlow有2个参与方：alice 和 bob
sf.init(['alice', 'bob'], address='local')

# 8.2 创建参与方对象
alice = sf.PYU('alice')
bob = sf.PYU('bob')

# 8.3 加载联邦数据
# load() 函数会读取两个文件，在逻辑上合成一个数据集
fed_flower_npz = load(
    {
        alice: "./flower_alice.npz",  # Alice的文件
        bob: "./flower_bob.npz"       # Bob的文件
    },
    allow_pickle=True  # 允许加载pickle格式
)

print("=" * 50)
print("✅ 联邦数据加载成功！")
print(f"联邦数据中的键: {fed_flower_npz.keys()}")
#因为是分布式存储，所以 .shape 无法直接获取，需要用 .partition_shape()
#在 SecretFlow 中，永远用 .partition_shape() 代替 .shape 来查看数据形状！
print(f"图片形状: {fed_flower_npz['image'].partition_shape()}")
# 不要用 .shape，统一用 .partition_shape()
print(f"标签形状: {fed_flower_npz['label'].partition_shape()}")
print("=" * 50)

# ============================================================
# 第9步：验证数据（可选）
# ============================================================

# 9.1 检查数据是否正确
print("\n检查数据对应关系:")
print(f"第1张图片的标签: {fed_flower_npz['label'][0]}")
print(f"第1张图片的形状: {fed_flower_npz['image'][0].partition_shape()}")

# 9.2 显示一张图片看看（需要matplotlib）
# ============================================================
# 第9步：验证数据（从本地文件加载）
# ============================================================

try:
    import matplotlib.pyplot as plt
    import numpy as np
    
    # ✅ 从本地 .npz 文件加载（普通 NumPy 数据）
    alice_data = np.load('flower_alice.npz')
    
    # ✅ 取第一张图片和标签
    sample_image = alice_data['image'][0]   # 这是真正的 NumPy 数组！
    sample_label = alice_data['label'][0]   # 这是真正的数字！
    
    print(f"✅ 图片形状: {sample_image.shape}")
    print(f"✅ 图片标签: {sample_label} ({classes[sample_label]})")
    
    # ✅ 显示图片并保存（不弹窗卡死）
    plt.figure(figsize=(5, 5))
    plt.imshow(sample_image.astype(np.uint8))
    plt.title(f'title: {sample_label} ({classes[sample_label]})')
    plt.axis('off')
    
    # 保存为图片文件（推荐）
    plt.savefig('sample_flower.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("✅ 图片已保存为 sample_flower.png")
    print("💡 在 VS Code 文件管理器中双击打开查看")
    
except ImportError:
    print("⚠️ 没有 matplotlib，跳过图片显示")
except FileNotFoundError:
    print("⚠️ 找不到 flower_alice.npz 文件，请先运行前面的代码")
except Exception as e:
    print(f"⚠️ 显示图片失败: {e}")

print("\n🎉 全部完成！数据已准备好，可以开始联邦学习了！")