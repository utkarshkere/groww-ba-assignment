import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
u,s,f,m,i,c,R=build()
u['su']=ts(u.signup_ts)
co=u[u.su<pd.Timestamp('2026-08-03')][['third_party_id','su']]
print('cohort',len(co),'(<=2 Aug 23:59:59 same?)',(u.su<=pd.Timestamp('2026-08-02 23:59:59.999')).sum(),'su NaT',u.su.isna().sum())
X=R.merge(co,left_on='id',right_on='third_party_id')
X['dd']=(X.t-X.su).dt.total_seconds()/86400
W=X[(X.dd>=0)&(X.dd<90)]
print('neg-day rev rows',((X.dd<0)&(X.rev>0)).sum())
def run(W,label):
    r=W.groupby('id').rev.sum().reindex(co.third_party_id,fill_value=0).sort_values(ascending=False,kind='mergesort')
    N=len(r); T=r.sum(); cs=r.cumsum()/T
    print('\n==',label,'total',round(T,1),'users>0',(r>0).sum(),round((r>0).mean()*100,2))
    top=r.iloc[:127]; print('top127 share',round(top.sum()/T*100,2),'bar',round(top.iloc[-1],2),'128th',round(r.iloc[127],2),'ties at bar',(r==top.iloc[-1]).sum())
    late=set(W[(W.dd>=60)&(W.dd<90)&(W.rev>0)].id)
    hv=[x for x in top.index if x in late]
    print('HV',len(hv),round(r[hv].sum()/T*100,2),'other',127-len(hv),round(r[[x for x in top.index if x not in late]].sum()/T*100,2))
    for p in [.5,.8,.9,.95,.99]:
        k=int((cs<p).sum())+1; print(f'{p}: k={k} ({k/N*100:.2f}%) min ₹{r.iloc[k-1]:.1f}')
    pts=[0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.75,1,1.25,1.5,2,2.5,3,4,5,6,8,10,15]
    print([(x,round(cs.iloc[int(round(N*x/100))-1]*100,1)) for x in pts])
    return r,hv
rA,hvA=run(W,'ALL instruments')
Wt=W[W.inst.isin(['fno','stocks','commodity'])]
rT,hvT=run(Wt,'trading only')
print('\ninstrument mix of 90d rev (all users):',(W.groupby('inst').rev.sum()/W.rev.sum()*100).round(2).to_dict())
top=set(rA.index[:127]); Wtop=W[W.id.isin(top)]
print('mix within top127:',(Wtop.groupby('inst').rev.sum()/Wtop.rev.sum()*100).round(2).to_dict())
print('top127 overlap all vs trading',len(top&set(rT.index[:127])),'HV overlap',len(set(hvA)&set(hvT)))
print('min/max dd in W', W.dd.min(), W.dd.max())
lateA=set(W[(W.dd>=60)&(W.rev>0)].id); topT=list(rT.index[:127])
h=[x for x in topT if x in lateA]; print('trading rank + any-instrument late activity HV',len(h),round(rT[h].sum()/rT.sum()*100,2))
d=set(rA.index[:127])^set(topT); print('symmetric diff',[(x,round(rA[x],1),round(rT[x],1)) for x in d])
