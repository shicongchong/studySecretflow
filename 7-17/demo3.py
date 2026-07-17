from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer
from jax import numpy as jnp
import numpy as np
from jax import grad

def breast_cancer(party_id:None,train:bool=True)->tuple[np.ndarray,np.ndarray]:
    x,y=load_breast_cancer(return_X_y=True)
    x=(x-np.min(x))/(np.max(x)-np.min(x))
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)
    if train:
        if party_id:
           if party_id==1:
               return x_train[:,:15]
           else:
               return x_train[:,15:],y_train

        else:
            return x_train,y_train


    else:
        return x_test,y_test

def sigmoid(x):
    return 1/(1+jnp.exp(-x))
def predict(W,b,inputs):
    return sigmoid(jnp.dot(inputs,W)+b)
def loss(W,b,inputs,targets):
    preds=predict(W,b,inputs)
    lable_prob=preds*targets+(1-preds)*(1-targets)
    return -jnp.mean(jnp.mean(jnp.log(lable_prob)))
def train_step(W,b,x1,x2,y,learning_rate):
    x=jnp.concatenate([x1,x2],axis=1)
    grads=grad(loss,(0,1))(W,b,x,y)
    W-=learning_rate*grads[0]
    b-=learning_rate*grads[1]
    return W,b
def fit(W,b,x1,x2,y,epochs,learning_rate):
    for _ in range(epochs):
        W,b=train_step(W,b,x1,x2,y,learning_rate=learning_rate)
    
    return W,b

def validate_model(W,b,x_test,y_test):
    preds=predict(W,b,x_test)
    return roc_auc_score(y_test,preds)

W=jnp.zeros((30,))
b=0.0
epochs=10
learning_rate=1e-2
x1=breast_cancer(party_id=1,train=True)
print(f"x1.shape={x1.shape}")
x2,y=breast_cancer(party_id=2,train=True)
print(f"x2.shape={x2.shape}")
print(x2)
X_test,y_test=breast_cancer(party_id=None,train=False)

W,b=fit(W,b,x1,x2,y,epochs=10,learning_rate=learning_rate)
auc=validate_model(W,b,X_test,y_test)
print("*"*50)
print(f"auc={auc}")
print("*"*50)
