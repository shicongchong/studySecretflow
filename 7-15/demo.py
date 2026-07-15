import secretflow as sf
import numpy as np
import pandas as pd
from pathlib import Path 
from sklearn.datasets import load_iris
sf.init(['alice', 'bob', 'carol'], address='local')
data, target = load_iris(return_X_y=True, as_frame=True)
data['uid'] = np.arange(len(data)).astype('str')
data['month'] = ['Jan'] * 75 + ['Feb'] * 75
current_par=Path(__file__).parent.absolute()
import os
os.makedirs(os.path.join(current_par, '.data'), exist_ok=True)
da,db,dc = data.sample(frac=0.9), data.sample(frac=0.8), data.sample(frac=0.7)
da.to_csv(os.path.join(current_par, '.data/alice.csv'), index=False)
db.to_csv(os.path.join(current_par, '.data/bob.csv'), index=False)
dc.to_csv(os.path.join(current_par, '.data/carol.csv'), index=False)
alice,bob=sf.PYU('alice'), sf.PYU('bob')
spu=sf.SPU(sf.utils.testing.cluster_def(['alice', 'bob']))
input_path={alice.party:os.path.join(current_par, '.data/alice.csv'), bob.party:os.path.join(current_par, '.data/bob.csv')}
output_path={alice.party:os.path.join(current_par, '.data/alice_psi.csv'), bob.party:os.path.join(current_par, '.data/bob_psi.csv')}
spu.psi({alice.party:["uid"], bob.party: ["uid"]}, input_path, output_path, 'alice',   table_keys_duplicated={alice.party: False, bob.party: False} ,  disable_alignment=True)
df:pd.DataFrame = da.join(db.set_index('uid'), on='uid', how='inner', rsuffix='_bob',sort=True)
expected=df[da.columns].astype({'uid':'int64'}).sort_values('uid').reset_index(drop=True)
da_psi=pd.read_csv(os.path.join(current_par, '.data/alice_psi.csv')).sort_values('uid').reset_index(drop=True)
db_psi=pd.read_csv(os.path.join(current_par, '.data/bob_psi.csv')).sort_values('uid').reset_index(drop=True)
pd.testing.assert_frame_equal(da_psi, expected)
pd.testing.assert_frame_equal(db_psi, expected)
print("PSI test passed successfully!")