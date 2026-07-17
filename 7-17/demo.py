import sys
sys.stdout.write(">>> 0. DEMO.PY 开始执行\n")
sys.stdout.flush()
print(">>> 1. demo.py 开始加载", flush=True)
from sklearn.datasets import load_breast_cancer
import numpy as np
from sklearn.model_selection import train_test_split
from jax import numpy as jnp
from jax import grad
from sklearn.metrics import roc_auc_score

def breast_cancer(party_id=None, train=True):
    x, y = load_breast_cancer(return_X_y=True)
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    if train:
        if party_id:
            if party_id == 1:
                return x_train[:, :15]
            else:
                return x_train[:, 15:], y_train
        else:
            return x_train, y_train
    else:
        return x_test, y_test

def sigmoid(x):
    return 1 / (1 + jnp.exp(-x))

def predict(W, b, inputs):
    return sigmoid(jnp.dot(inputs, W) + b)

def loss(W, b, inputs, targets):
    preds = predict(W, b, inputs)
    label_probs = preds * targets + (1 - preds) * (1 - targets)
    return -jnp.mean(jnp.log(label_probs))

def train_step(W, b, x1, x2, y, learning_rate):
    x = jnp.concatenate([x1, x2], axis=1)
    grads = grad(loss, (0, 1))(W, b, x, y)
    W -= learning_rate * grads[0]
    b -= learning_rate * grads[1]
    return W, b

def fit(W, b, x1, x2, y, epochs, learning_rate=1e-2):
    for _ in range(epochs):
        W, b = train_step(W, b, x1, x2, y, learning_rate)
    return W, b

def validate_model(W, b, X_test, y_test):
    preds = predict(W, b, X_test)
    print(f"preds type: {type(preds)}")
    print(f"preds shape: {preds.shape}")
    print(f"preds has NaN: {jnp.isnan(preds).any()}")
    print(f"preds min: {jnp.min(preds)}, max: {jnp.max(preds)}")
    print(f"y_test has NaN: {jnp.isnan(y_test).any()}")
    if hasattr(preds, '__array__'):
        preds = np.array(preds)
    return roc_auc_score(y_test, preds)

if __name__ == "__main__":
    print(">>> 开始训练和评估...", flush=True)
    
    x1 = breast_cancer(party_id=1, train=True)
    x2, y = breast_cancer(party_id=2, train=True)
    W = jnp.zeros((30,))
    b = 0.0
    epochs = 10
    W, b = fit(W, b, x1, x2, y, epochs=epochs, learning_rate=1e-2)
    x_test, y_test = breast_cancer(party_id=None, train=False)
    auc = validate_model(W, b, x_test, y_test)
    
    print("*" * 50)
    print(f"auc = {auc:.6f}")
    print("*" * 50)