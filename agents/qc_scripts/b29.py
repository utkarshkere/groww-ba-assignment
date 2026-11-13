import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV,LAP,other=G['HV'],G['LAP'],G['other']
cs=co.set_index('third_party_id').su
Wc=W[W.id.isin(set(co.third_party_id))].assign(d=lambda x:x.t.dt.normalize())
print('other n',len(other))
for lab,Gs in [('HV',HV),('LAP',LAP),('OTHER',other)]:
    ix=list(Gs); g=Wc[Wc.id.isin(Gs)]
    o=g.groupby('id').size().reindex(ix,fill_value=0)
    td=g[g.inst.isin(['fno','stocks','commodity'])].drop_duplicates(['id','d']).groupby('id').size().reindex(ix,fill_value=0)
    pr=g.groupby('id').inst.nunique().reindex(ix,fill_value=0)
    rm=(r.reindex(ix)/3)
    print(f'{lab}: orders {o.mean():.1f}/{o.median():.1f}  tdays {td.mean():.1f}/{td.median():.1f}  products {pr.mean():.2f}/{pr.median():.1f}  rev/month {rm.mean():.0f}/{rm.median():.0f}')
print('HV monthly total',round(r.reindex(list(HV)).sum()/3))
# Q2.2 stop rates
X2=X[X.id.isin(HV)]
any90=set(X2[X2.dd>=90].id); print('HV earned any time after d90',len(any90),round(len(any90)/94*100,1))
elig=set(cs[cs+pd.Timedelta(days=120)<=pd.Timestamp('2026-11-01')].index)
e=HV&elig; b=X2[(X2.dd>=90)&(X2.dd<120)]
earn=set(b.id)&e; print('HV eligible',len(e),'earned d90-120',len(earn),round(len(earn)/len(e)*100,1))
# observed window after d90 for HV
obs=(pd.Timestamp('2026-11-01')-cs[list(HV)]).dt.total_seconds()/86400-90
print('HV days observed after d90: min',round(obs.min(),1),'median',round(obs.median(),1),'<30d',(obs<30).sum(),'<7d',(obs<7).sum())
# revenue at risk: HV d90-120 revenue vs their monthly avg (eligible)
br=b.groupby('id').rev.sum().reindex(list(e),fill_value=0)
m_e=r.reindex(list(e))/3
print('eligible HV: avg monthly 0-90',round(m_e.sum()),'actual d90-120',round(br.sum()),'ratio',round(br.sum()/m_e.sum()*100,1))
stopped=[x for x in e if x not in earn]; print('stoppers monthly rev (their 0-90 avg)',round(m_e[stopped].sum()),'share of eligible HV monthly',round(m_e[stopped].sum()/m_e.sum()*100,1))
# decline among continuers
cont=[x for x in e if x in earn]; print('continuers monthly 0-90',round(m_e[cont].sum()),'d90-120',round(br[cont].sum()),'ratio',round(br[cont].sum()/m_e[cont].sum()*100,1))
# month-3 revenue as base
m3=Wc[(Wc.dd>=60)&Wc.id.isin(e)].groupby('id').rev.sum().reindex(list(e),fill_value=0)
print('eligible HV month-3 revenue',round(m3.sum()),'d90-120 vs m3',round(br.sum()/m3.sum()*100,1),'stoppers m3',round(m3[stopped].sum()))
print('Q2: 52/18',52/18,'52/360',52/360*100,'94/18',94/18,'52/94',52/94*100,'50/18',50/18,'23/18',23/18,'54/18',54/18,'75/18',75/18)
