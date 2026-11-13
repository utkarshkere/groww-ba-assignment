import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV,LAP,TOP=G['HV'],G['LAP'],G['TOP']
T=r.sum(); N=len(co)
cs=co.set_index('third_party_id').su
wk=(cs.dt.normalize()-pd.to_timedelta(cs.dt.weekday,unit='D'))
print('weeks',wk.nunique(),'first',wk.min(),'last',wk.max())
hvw=wk[list(HV)].value_counts().reindex(sorted(wk.unique()),fill_value=0)
print('HV per week',hvw.values.tolist(),'mean',round(hvw.mean(),2),'min',hvw.min(),'max',hvw.max(),'signups/week',round(N/wk.nunique(),1))
jw=pd.Timestamp('2026-07-06'); print('6-12 Jul signups',(wk==jw).sum(),'HV',hvw.get(jw))
w1=W[W.dd<7].groupby('id').rev.sum()
silent=[x for x in HV if w1.get(x,0)==0]; print('HV silent wk1',len(silent))
# placed no order in week1 (any status, any product)
def frame(df,tcol):
    x=df[['third_party_id',tcol]].copy(); x.columns=['id','t']; x['t']=ts(x.t); return x
A=pd.concat([frame(s,'created_at'),frame(f,'order_created_at'),frame(c,'created_at'),frame(m,'created_at'),frame(i,'created_at')])
A=A.merge(cs.rename('su'),left_on='id',right_index=True); A['dd']=(A.t-A.su).dt.total_seconds()/86400
o1=set(A[(A.dd>=0)&(A.dd<7)].id)
print('silent with no order wk1',len([x for x in silent if x not in o1]))
zero=set(co.third_party_id)-set(w1[w1>0].index); print('base rate HV among wk1-zero',round(len(set(silent))/len(zero)*100,3))
# bracket ranges
cum=r.cumsum()/T
def rng(a,b): x=r.iloc[a:b]; return (len(x),round(x.min(),1),round(x.max(),1))
print('brackets',[rng(0,23),rng(23,56),rng(56,70),rng(70,127),rng(127,228),rng(228,728),rng(728,1673),rng(1673,N)])
print('avg 90d per user',T/N,'1247/avg',1247/(T/N), '58.6% per pick', .586*T/360)
