import numpy as np
import secretflow as sf
sf.init(['alice', 'bob', 'charlie'], address="local", log_to_driver=True)
spu = sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob']))
alice, bob, charlie = sf.PYU('alice'), sf.PYU('bob'), sf.PYU('charlie')
all_data=np.load("mnist.npz")
print(all_data.files)
alice_train_x = all_data["x_train"][:30000]
alice_test_x = all_data["x_test"][:30000]
alice_train_y = all_data["y_train"][:30000]
alice_test_y = all_data["y_test"][:30000]

bob_train_x = all_data["x_train"][30000:]
bob_test_x = all_data["x_test"][30000:]
bob_train_y = all_data["y_train"][30000:]
bob_test_y = all_data["y_test"][30000:]
from pathlib import Path
current_parent_path=Path(__file__).parent


alice_path=current_parent_path/"alice_mnist.npz"
bob_path=current_parent_path/"bob_mnist.npz"


np.savez(
    alice_path,
    train_x=alice_train_x,
    test_x=alice_test_x,
    train_y=alice_train_y,
    test_y=alice_test_y,
)
np.savez(
    bob_path,
    train_x=bob_train_x,
    test_x=bob_test_x,
    train_y=bob_train_y,
    test_y=bob_test_y,
)
np.save(current_parent_path/"alice_mnist_train_x.npy",alice_train_x)
np.save(current_parent_path/"bob_mnist_train_x.npy",bob_train_x)
alice_path_npz=str(current_parent_path/"alice_mnist.npz")
bob_path_npz=str(current_parent_path/"alice_mnist.npz")
from secretflow.data.ndarray import load
from secretflow.data.split import train_test_split
fed_npz=load({alice:alice_path_npz,bob:bob_path_npz},allow_pickle=True)
print(type(fed_npz["train_x"]))

alice_path_npy=str(current_parent_path/"alice_mnist_train_x.npy")
bob_path_npy=str(current_parent_path/"bob_mnist_train_x.npy")
fed_ndarry=load({alice:alice_path_npy,bob:bob_path_npy},allow_pickle=True)
print(type(fed_ndarry))
print("执行完毕")
