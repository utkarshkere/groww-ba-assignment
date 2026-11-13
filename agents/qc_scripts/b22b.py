import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
u,s,f,m,i,c,R=build()
ss=s[s.order_status.eq('SUCCESS')].copy()
ss['ob']=pd.to_numeric(ss.original_brokerage,errors='coerce'); ss['t']=pd.to_numeric(ss.turnover_inr)
r=ss[ss.ob.notna()]
imp=np.where(r['product'].eq('MTF'),0.001*r.t,np.minimum(20,np.minimum(np.maximum(5,0.001*r.t),0.025*r.t)))
d=(r.ob-imp).abs()
print('rule fit on recorded: within 0.01',(d<0.01).mean(), 'by product', r.assign(ok=d<0.01).groupby('product').ok.mean().to_dict())
print('blank-share of SUCCESS by month', ss.assign(mo=ts(ss.created_at).dt.to_period('M')).groupby('mo').ob.apply(lambda x:x.isna().mean()).round(3).to_dict())
print('imputed share of total rev', s.loc[s.blank,'rev'].sum()/R.rev.sum())
