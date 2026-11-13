import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
END=pd.Timestamp('2026-10-31 23:59:59.999')
print('rows',len(s),len(f),len(m),len(i),len(c),'sum',len(s)+len(f)+len(m)+len(i)+len(c),'users',len(u))
T=r.sum(); N=len(co); m3=set(W[W.dd>=60].id)
HV=set(hv); LAP=set(lap); TOP=set(top)
other=set(r[r>0].index)-TOP; allc=set(co.third_party_id)
print('HV',len(hv),'lap',len(lap),'HV share',r[hv].sum()/T)
def grp(G): return W[W.id.isin(G)]
for lab,G in [('HV',HV),('LAP',LAP),('OTHER',other),('ALL',allc)]:
    g=grp(G); n=len(G)
    rv=g.rev.sum()
    m1=g[g.dd<30].id.nunique()/n; m2=g[(g.dd>=30)&(g.dd<60)].id.nunique()/n
    ords=len(g)/n; days=g.assign(d=g.t.dt.normalize()).drop_duplicates(['id','d']).shape[0]/n
    prods=g.groupby('id').inst.nunique().reindex(list(G),fill_value=0)
    pr_mean=prods[prods>0].mean() if lab!='ALL' else np.nan
    wk1=g[g.dd<7].id.nunique()/n
    print(f'{lab} n={n} rev/month={rv/n/3:.1f} rev/order={rv/len(g):.2f} m1={m1:.3f} m2={m2:.3f} orders={ords:.1f} tdays={days:.1f} products={pr_mean:.2f} firstrev_wk1={wk1:.3f}')
# earned after day 90 (any time to END)
A=X[X.dd>=90]
for lab,G in [('HV',HV),('LAP',LAP),('OTHER',other),('ALL',allc)]:
    print(lab,'earned after d90',round(A[A.id.isin(G)].id.nunique()/len(G),3))
# days 90-120 among users with >=30d observed after day 90  (su+120d <= END)
cs=co.set_index('third_party_id').su
elig=set(cs[cs+pd.Timedelta(days=120)<=END].index)
B=X[(X.dd>=90)&(X.dd<120)]
br=B.groupby('id').rev.sum()
def d120(G,lab):
    G=set(G)&elig; e=br.reindex(list(G),fill_value=0)
    print(f'{lab}: {int((e>0).sum())} of {len(G)} ({(e>0).mean()*100:.1f}%) median {e.median():.0f} mean {e.mean():.0f}')
d120(allc,'ALL base'); d120(HV,'0 ours'); d120(LAP,'lapsed'); d120(TOP,'1 top1%')
cum=r.cumsum()/T; p80=list(r.index[:int((cum<0.8).sum())+1])
print('def2 n',len(p80),'share',r[p80].sum()/T,'lapsed in it',len(set(p80)-m3),'misses ours',len(HV-set(p80))); d120(p80,'2 pareto80')
d3=[x for x in r.index if r[x]>=1000 and x in m3]; print('def3',len(d3),r[d3].sum()/T); d120(d3,'3 >=1000+m3')
mr=W[W.dd>=60].groupby('id').rev.sum().reindex(co.third_party_id,fill_value=0).sort_values(ascending=False,kind='mergesort')
d4=list(mr.index[:127]); print('def4',len(d4),r[d4].sum()/T); d120(d4,'4 top m3 rev')
act={k:set(W[(W.dd>=lo)&(W.dd<hi)].id) for k,(lo,hi) in {'m1':(0,30),'m2':(30,60),'m3':(60,90)}.items()}
all3=act['m1']&act['m2']&act['m3']; r3=r[r.index.isin(all3)].sort_values(ascending=False,kind='mergesort'); d5=list(r3.index[:127])
print('def5 pool',len(all3),len(d5),r[d5].sum()/T); d120(d5,'5')
W2=W.assign(d=W.t.dt.normalize())
tdays=W2.drop_duplicates(['id','d']).groupby('id').size()
d6=[x for x in r.index if tdays.get(x,0)>=20 and r[x]>=300]; print('def6',len(d6),r[d6].sum()/T); d120(d6,'6')
np_=W.groupby('id').inst.nunique()
d7=[x for x in r.index if np_.get(x,0)>=2 and r[x]>=500]; print('def7',len(d7),r[d7].sum()/T); d120(d7,'7')
for k,lab in [(['m1'],'9'),(['m2'],'10'),(['m2','m3'],'11'),(['m1','m2','m3'],'12')]:
    G=[x for x in top if all(x in act[j] for j in k)]; print('def'+lab,len(G),round(r[G].sum()/T*100,1)); d120(G,lab)
print('top1 not active m1',len([x for x in top if x not in act['m1']]))
firstd=W.groupby('id').dd.min(); print('HV started after d60',sum(firstd[x]>=60 for x in hv))
print('top5% bar (k=round(.05N))',r.iloc[int(round(N*.05))-1],'k=637',r.iloc[636])
# HV mix/main product
g=grp(HV); print('HV mix',(g.groupby('inst').rev.sum()/g.rev.sum()).round(3).to_dict())
print('HV main product',g.groupby(['id','inst']).rev.sum().unstack().fillna(0).idxmax(axis=1).value_counts().to_dict())
fnoHV=set(g[g.inst=='fno'].id); print('HV with F&O',len(fnoHV),'share of 90d rev',r[list(fnoHV)].sum()/T,'drops',len(HV-fnoHV), 'HV rev lost share',r[list(HV-fnoHV)].sum()/r[hv].sum())
gn=grp(HV-fnoHV); print('non-F&O HV median orders',gn.groupby('id').size().median())
pickle.dump(dict(HV=HV,LAP=LAP,TOP=TOP,other=other),open('agents/qc_scripts/groups.pkl','wb'))
