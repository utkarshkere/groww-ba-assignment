import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
HV=pickle.load(open('agents/qc_scripts/groups.pkl','rb'))['HV']
T=r.sum(); N=len(co); cs=co.set_index('third_party_id').su
Wc=W[W.id.isin(set(co.third_party_id))]
elig=set(cs[cs+pd.Timedelta(days=120)<=pd.Timestamp('2026-11-01')].index); print('eligible',len(elig))
B=X[(X.dd>=90)&(X.dd<120)&X.id.isin(elig)]; br=B.groupby('id').rev.sum(); TB=br.sum()
print('all eligible ₹',round(TB),'earn %',round(len(br[br>0])/len(elig)*100,1))
top=list(r.index[:127]); m3=set(Wc[Wc.dd>=60].id)
act={k:set(Wc[(Wc.dd>=lo)&(Wc.dd<hi)].id) for k,(lo,hi) in {'m1':(0,30),'m2':(30,60),'m3':(60,90)}.items()}
cum=r.cumsum()/T
mr=Wc[Wc.dd>=60].groupby('id').rev.sum().reindex(co.third_party_id,fill_value=0).sort_values(ascending=False,kind='mergesort')
all3=act['m1']&act['m2']&act['m3']; r3=r[r.index.isin(all3)].sort_values(ascending=False,kind='mergesort')
Wd=Wc.assign(d=Wc.t.dt.normalize()); tdays=Wd.drop_duplicates(['id','d']).groupby('id').size(); npr=Wc.groupby('id').inst.nunique()
# def8: HV minus F&O users with loss > 5x brokerage (90d)
f=D['f']; fe=f[f.order_status.eq('EXECUTED')&f.third_party_id.isin(HV)].copy(); fe['t']=ts(fe.order_created_at)
fe=fe.merge(cs.rename('su'),left_on='third_party_id',right_index=True); fe=fe[((fe.t-fe.su).dt.total_seconds()/86400).between(0,90,inclusive='left')]
fe['pnl']=pd.to_numeric(fe.pnl,errors='coerce'); pu=fe.groupby('third_party_id').agg(p=('pnl','sum'),b=('brokerage_inr','sum'))
heavy=set(pu.index[(-pu.p/pu.b)>5])
defs={0:list(HV),1:top,2:list(r.index[:int((cum<0.8).sum())+1]),3:[x for x in r.index if r[x]>=1000 and x in m3],
 4:list(mr.index[:127]),5:list(r3.index[:127]),6:[x for x in r.index if tdays.get(x,0)>=20 and r[x]>=300],
 7:[x for x in r.index if npr.get(x,0)>=2 and r[x]>=500],8:[x for x in HV if x not in heavy],
 9:[x for x in top if x in act['m1']],10:[x for x in top if x in act['m2']],11:[x for x in top if x in act['m2'] and x in act['m3']],12:[x for x in top if x in all3]}
for k,G in defs.items():
    e=[x for x in G if x in elig]; v=br.reindex(e,fill_value=0)
    print(f'def{k}: n={len(G)} rev90={r[G].sum()/T*100:.1f}% elig={len(e)} next ₹{v.sum():,.0f} share={v.sum()/TB*100:.1f}% avg={v.mean():.0f} median={v.median():.0f} earning={int((v>0).sum())}')
# overlap def0 vs def4 eligible
e0=set(defs[0])&elig; e4=set(defs[4])&elig
print('def4 elig overlap with ours',len(e0&e4),'def4-only',len(e4-e0),'their next ₹',round(br.reindex(list(e4-e0),fill_value=0).sum()),'ours-only',len(e0-e4),round(br.reindex(list(e0-e4),fill_value=0).sum()))
print('non-elig HV',len(HV)-len(e0))
pickle.dump(defs,open('agents/qc_scripts/defs.pkl','wb'))
