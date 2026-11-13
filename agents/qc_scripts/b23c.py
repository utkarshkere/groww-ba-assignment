import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
u,s,f,m,i,c,R=build()
fno=set(f.loc[f.order_status.eq('EXECUTED'),'third_party_id'])
ss=s[s.order_status.eq('SUCCESS')].copy(); ss['mo']=ts(ss.created_at).dt.to_period('M')
mtf=ss[ss['product'].eq('MTF')]
for lab,d in [('all',mtf),('nonfno',mtf[~mtf.third_party_id.isin(fno)])]:
    for mo,x in d.groupby('mo'):
        p=x.groupby('third_party_id').rev.sum().sort_values(ascending=False)
        print(lab,mo,'rev',round(p.sum()),'top1%',round(p.iloc[0]/p.sum()*100,1),'top3%',round(p.iloc[:3].sum()/p.sum()*100,1),'ex-top1',round(p.iloc[1:].sum()))
