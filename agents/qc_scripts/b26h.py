import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV=G['HV']
T=r.sum(); print('top127 exact share',r.iloc[:127].sum()/T*100,'top128',r.iloc[:128].sum()/T*100)
WF=W[W.inst=='fno']; rf=WF.groupby('id').rev.sum(); m3f=set(WF[WF.dd>=60].id)
drop=HV-set(x for x in rf.index if rf[x]>=733.8 and x in m3f)
cs=co.set_index('third_party_id').su
def frame(df,tcol,inst):
    x=df[['third_party_id',tcol]].copy(); x.columns=['id','t']; x['t']=ts(x.t); x['inst']=inst; return x
A=pd.concat([frame(s,'created_at','stocks'),frame(f,'order_created_at','fno'),frame(c,'created_at','commodity'),frame(m,'created_at','mf'),frame(i,'created_at','ipo')])
A=A[A.id.isin(drop)].merge(cs.rename('su'),left_on='id',right_index=True); A['dd']=(A.t-A.su).dt.total_seconds()/86400
A90=A[(A.dd>=0)&(A.dd<90)]
print('dropped33 median all orders any status 90d',A90.groupby('id').size().median(),'rev orders',W[W.id.isin(drop)].groupby('id').size().median(),
      'trading rev orders',W[W.id.isin(drop)&W.inst.isin(['fno','stocks','commodity'])].groupby('id').size().median(), 'all-time rev orders',R[R.id.isin(drop)&(R.rev>0)].groupby('id').size().median())
st=s[s.third_party_id.isin(drop)&s.order_status.eq('SUCCESS')].merge(cs.rename('su'),left_on='third_party_id',right_index=True)
st=st[((ts(st.created_at)-st.su).dt.total_seconds()/86400).between(0,90,inclusive='left')]
print('dropped33 using MIS',st[st['product']=='MIS'].third_party_id.nunique(),'MTF',st[st['product']=='MTF'].third_party_id.nunique())
