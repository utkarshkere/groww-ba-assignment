import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
HV=pickle.load(open('agents/qc_scripts/groups.pkl','rb'))['HV']
uu=u.set_index('third_party_id'); C=uu.loc[co.third_party_id].copy()
C['su']=ts(C.signup_ts); C['so']=ts(C.stock_onboarding_ts)
w1=W[W.dd<7]; rv=w1.groupby('id').rev.sum().reindex(C.index,fill_value=0)
w1d=w1.assign(d=w1.t.dt.normalize())
sig={
 'stock setup':((C.so-C.su).dt.total_seconds()/3600<168)&C.so.notna(),
 '₹200+':rv>=200, '₹50-200':(rv>=50)&(rv<200), 'F&O':C.index.isin(w1[w1.inst=='fno'].id),
 '2+ days':C.index.isin((w1d.drop_duplicates(['id','d']).groupby('id').size()>=2).loc[lambda x:x].index),
 'rev d3-6':C.index.isin(w1[w1.dd>=3].id), 'KYC registry':C.kra_flag.eq('kra_verified'),
 '₹1-50 only':(rv>0)&(rv<50), '2+ products':C.index.isin((w1.groupby('id').inst.nunique()>=2).loc[lambda x:x].index)}
ish=C.index.isin(list(HV))
for k,v in sig.items():
    v=pd.Series(np.asarray(v),index=C.index)
    print(f'{k:14s} n={v.sum():5d} %HV={v[ish].mean()*100:5.1f} %oth={v[~ish].mean()*100:5.2f} with={ish[v.values].mean()*100:5.2f} without={ish[~v.values].mean()*100:5.2f}')
t=w1d[w1d.inst.isin(['fno','stocks','commodity'])]
v=C.index.isin((t.drop_duplicates(['id','d']).groupby('id').size()>=2).loc[lambda x:x].index)
print('2+ trading days',v.sum(),round(v[ish].mean()*100,1),round(v[~ish].mean()*100,2),round(ish[v].mean()*100,1),round(ish[~v].mean()*100,2))
ss=s[s.order_status.eq('SUCCESS')&s['product'].isin(['MIS','MTF'])].merge(C[['su']],left_on='third_party_id',right_index=True)
ss=ss[((ts(ss.created_at)-ss.su).dt.total_seconds()/86400).between(0,7,inclusive='left')]
v=C.index.isin(ss.third_party_id); print('intraday/margin',v.sum(),round(v[ish].mean()*100,1),round(v[~ish].mean()*100,2),round(ish[v].mean()*100,1),round(ish[~v].mean()*100,2))
