import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
pd.set_option('display.width',200)
u,s,f,m,i,c,R=build()
fno=set(f.loc[f.order_status.eq('EXECUTED'),'third_party_id'])
ss=s[s.order_status.eq('SUCCESS')].copy(); ss['t']=ts(ss.created_at); ss['mo']=ss.t.dt.to_period('M')
mtf=ss[ss['product'].eq('MTF')]
g=mtf.groupby('mo').agg(rev=('rev','sum'),rec=('rev_recorded','sum'),blank_ord=('blank','sum'),orders=('rev','size'),users=('third_party_id','nunique'))
g['imp']=g.rev-g.rec; print(g.round(0))
nf=mtf[~mtf.third_party_id.isin(fno)]
print('nonfno mtf monthly',nf.groupby('mo').agg(rev=('rev','sum'),users=('third_party_id','nunique')).round(0).to_dict())
# per-user per-active-month comparison, non-F&O users
def pm(df,label):
    a=df.groupby('third_party_id').agg(rev=('rev','sum'),months=('mo','nunique'),first=('t','min'))
    a['tenure_m']=((pd.Timestamp('2026-11-01')-a['first']).dt.days/30.44)
    a['rpm']=a.rev/a.tenure_m
    x=a.rev.sort_values(ascending=False)
    print(label,'n',len(a),'mean',round(a.rev.mean(),1),'median',round(a.rev.median(),1),'mean_ex_top5',round(x.iloc[5:].mean(),1),
          'rev/tenure-month mean',round(a.rev.sum()/a.tenure_m.sum(),1),'median rpm',round(a.rpm.median(),2),'median tenure m',round(a.tenure_m.median(),1))
nfs=ss[~ss.third_party_id.isin(fno)]
pm(nfs[nfs['product'].eq('MTF')],'nonFnO MTF-product rev')
pm(nfs[~nfs['product'].eq('MTF')],'nonFnO nonMTF stock rev')
# MTF users (non-fno): their total stock revenue incl CNC/MIS vs non-MTF non-fno stock users
mu=set(mtf.third_party_id)
pm(nfs[nfs.third_party_id.isin(mu)],'nonFnO MTF users ALL stock rev')
pm(nfs[~nfs.third_party_id.isin(mu)],'nonFnO non-MTF users ALL stock rev')
# recorded-only versions of MTF
mtf2=mtf.copy(); 
print('recorded-only MTF total',mtf.rev_recorded.sum(),'users w/ recorded',mtf.loc[~mtf.blank,'third_party_id'].nunique())
