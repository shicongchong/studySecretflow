import secretflow as sf
import numpy as np
import pandas as pd
import os
from sklearn.datasets import load_iris
from pathlib import Path
data,target=load_iris(return_X_y=True,as_frame=True)
data['uid']=np.arange(len(data)).astype('str')
data['month']=['Jan']*75+['Febb']*75
da,db,dc=data.sample(frac=0.9),data.sample(frac=0.8),data.sample(frac=0.7)
current_par=Path(__file__).parent.absolute()
os.makedirs(os.path.join(current_par,'.data'))
da.to_csv(os.path.join(current_par,'.data/alice.csv'))
db.to_csv(os.path.join(current_par,'.data/bob.csv'))
sf.init(['alice','bob','carol'],address='local')
spu=sf.SPU(sf.utils.testing.cluster_def(['alice','bob']))
alice,bob=sf.PYU('alice'),sf.PYU('bob')
input_path={
    alice.party:os.path.join(current_par,'.data/alice.csv'),
    bob.party:os.path.join(current_par,'.data/bob.csv')
    }
out_path={
    alice.party:os.path.join(current_par,'alice_psi.csv'),
    bob.party:os.path.join(current_par,'bob_psi.csv')
}
spu.psi({alice.party:['uid'],bob.party:['uid']},input_path,out_path,'alice',table_keys_duplicated={alice.party:False,bob.party:False},disable_alignment=True)
da_psi=pd.read_csv(out_path[alice.party])
db_psi=pd.read_csv(out_path[bob.party])
da_psi['uid']=da_psi['uid'].astype('int64')
db_psi['uid']=db_psi['uid'].astype('int64')
df:pd.DataFrame=da_psi.join(db_psi.set_index('uid'),on='uid',how='inner',rsuffix='_bob',sort=True)
expected=df[da.columns].astype({'uid':'int64'}).sort_values('uid').reset_index(drop=True)
pd.testing.assert_frame_equal(da_psi, expected)
pd.testing.assert_frame_equal(db_psi, expected)
print("PSI test passed successfully!")
