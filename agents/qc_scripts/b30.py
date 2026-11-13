import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
HV=pickle.load(open('agents/qc_scripts/groups.pkl','rb'))['HV']
N=len(co); T=r.sum()
print('HV mean 90d',round(r.reindex(list(HV)).mean(),1),'cohort mean',round(T/N,2),'ratio',round(r.reindex(list(HV)).mean()/(T/N),1))
uu=u.set_index('third_party_id'); C=uu.loc[co.third_party_id]
a=r.reindex(C.index[C.acquisition_channel=='apple search ads']).values; o=r.reindex(C.index[C.acquisition_channel=='organic']).values
print('ASA',len(a),round(a.sum()),round(a.mean(),1),'Org',len(o),round(o.mean(),1),'gap',round(a.mean()-o.mean(),1))
for seed in range(5):
    rng=np.random.default_rng(seed)
    ga=a[rng.integers(0,len(a),(10000,len(a)))].mean(1); go=np.array([o[rng.integers(0,len(o),len(o))].mean() for _ in range(10000)])
    d=ga-go; print('seed',seed,'5th',round(np.percentile(d,5),1),'95th',round(np.percentile(d,95),1),'share<=0',round((d<=0).mean()*100,2))
# 2+ days variants for '335'
w1=W[(W.dd<7)&W.id.isin(set(C.index))].assign(d=lambda x:x.t.dt.normalize())
cs=C.su if 'su' in C else ts(C.signup_ts)
def frame(df,tcol,inst):
    x=df[['third_party_id',tcol]].copy(); x.columns=['id','t']; x['t']=ts(x.t); x['inst']=inst; return x
A=pd.concat([frame(s,'created_at','stocks'),frame(f,'order_created_at','fno'),frame(c,'created_at','commodity'),frame(m,'created_at','mf'),frame(i,'created_at','ipo')])
A=A[A.id.isin(set(C.index))].merge(ts(C.signup_ts).rename('su'),left_on='id',right_index=True); A['dd']=(A.t-A.su).dt.total_seconds()/86400
A1=A[(A.dd>=0)&(A.dd<7)].assign(d=lambda x:x.t.dt.normalize())
def cnt(df): return (df.drop_duplicates(['id','d']).groupby('id').size()>=2).sum()
print('2+ days: rev any product',cnt(w1),'rev trading',cnt(w1[w1.inst.isin(['fno','stocks','commodity'])]),'any order any product',cnt(A1),'any order trading',cnt(A1[A1.inst.isin(['fno','stocks','commodity'])]))
# 12 of 82 within 60d vs whole
stop=pd.read_pickle('agents/qc_scripts/stoppers.pkl')
Rp=R[R.rev>0].assign(d=lambda x:x.t.dt.normalize()).merge(stop[['last']],left_on='id',right_index=True)
Rp['rel']=(Rp.d-Rp['last']).dt.days
st=Rp[Rp.inst=='stocks']
print('stoppers with stock rev after: any',st[st.rel>0].id.nunique(),'within 60d',st[st.rel.between(1,60)].id.nunique())
# F&O share on ASA cohort vs all users Apr-Oct
print('F&O share all users Apr-Oct',round(R[R.inst=='fno'].rev.sum()/R.rev.sum()*100,1))
# HV vs mean HV trades/day not recomputable; 
# MTF 3.9% context: non-F&O delivery traders
