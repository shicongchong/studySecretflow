import secretflow as sf
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from typing import Tuple
def breast_cancer(party_id:None,train:bool=True)->Tuple[np.ndarray,np.ndarray]:
     x,y=load_breast_cancer(return_X_y=True)
     x=(x-np.min(x))/(np.max(x)-np.min(x))
     x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=123)
     if train:
          if party_id:
               if party_id==1:
                     return x_train[:,:15],_
               else:
                     return x_train[:,15:],y_train
     else:
          return x_test,y_test
     
import jax.numpy as jnp
def sigmoid(x):
     return 1/(1+jnp.exp(-x))

def predict(W,b,inputs):
     return sigmoid(jnp.dot(inputs,W)+b)
def loss(W,b,inputs,targets):
     preds=predict(W,b,inputs)
     lable_probs=preds*targets+(1-preds)*(1-targets)
     return -jnp.mean(jnp.log(lable_probs))
def train_step(W,b,inputs,x1,x2,y,learning_rate):
     x=jnp.concatenate([x1,x2],axis=1)
     grads=grad(loss)(W,b,x,y)
     W-=learning_rate*grads[0]
     b-=learning_rate*grads[1]
     return W,b
def fit(W,b,x1,x2,y,epochs,learing_rate):
     for _ in range(epochs):
         W,b=train_step(W,b,x1,x2,y,learning_rate=learning_rate)
     return W,b
from jax import grad
W=jnp.zeros((30,))
b=0.0
epochs=10
learing_rate=1e-2
W,b=fit(W,b,x1,x2,y,epochs=10,learning_rate=learing_rate)