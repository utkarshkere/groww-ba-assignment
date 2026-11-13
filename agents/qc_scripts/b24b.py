import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
pd.set_option('display.width',200)
u,s,f,m,i,c,R=build()
END=pd.Timestamp('2026-10-31')
fe=f[f.order_status.eq('EXECUTED')].copy(); fe['t']=ts(fe.order_created_at); fe['d']=fe.t.dt.normalize()
fno=set(fe.third_party_id)
R=R[R.rev>0].copy(); R['d']=R.t.dt.normalize()
stop=pd.read_pickle('agents/qc_scripts/stoppers.pkl')
S=R[R.id.isin(stop.index)].merge(stop[['last']],left_on='id',right_index=True)
S['rel']=(S.d-S['last']).dt.days
# (a) fixed symmetric windows: 60d before (rel in -59..0) vs 60d after (1..60), all 82 have >=60 obs
for k in [['stocks','commodity'],['stocks'],['commodity']]:
    b=S[S.inst.isin(k)&S.rel.between(-59,0)]; a=S[S.inst.isin(k)&S.rel.between(1,60)]
    print('fixed60',k,'before ₹',round(b.rev.sum()),'users',b.id.nunique(),'| after ₹',round(a.rev.sum()),'users',a.id.nunique())
# all-instrument activity after: did stoppers churn from platform?
a=S[S.rel>0]; print('any rev after',a.id.nunique(),'of',len(stop))
# stopper profile
stop['span']=(stop['last']-stop['first']).dt.days
print('stopper F&O orders median',stop.n.median(),'span median',stop.span.median(),'n>=20',(stop.n>=20).sum())
uu=u.set_index('third_party_id'); su=ts(uu.signup_ts)
stop['su']=su.reindex(stop.index).values
print('signup month of stoppers',pd.Series(pd.to_datetime(stop.su).dt.to_period('M')).value_counts().sort_index().to_dict())
print('last F&O month',stop['last'].dt.to_period('M').value_counts().sort_index().to_dict())
# Continuers comparison: non-stoppers with >=5 orders active after Sep 1
g=fe.groupby('third_party_id').agg(n=('d','size'),last=('d','max'),first=('d','min'))
cont=g[(g.n>=5)&(g.last>END-pd.Timedelta(days=60))]
print('continuers >=5',len(cont),'with <5 orders (excluded)',(g.n<5).sum())
# (b) pnl
fe['pnl']=pd.to_numeric(fe.pnl,errors='coerce')
print('pnl non-null share',fe.pnl.notna().mean())
pp=fe.groupby('third_party_id').pnl.sum(min_count=1)
for lab,ix in [('stoppers',stop.index),('continuers5+',cont.index)]:
    x=pp.reindex(ix)
    print(lab,'n',len(ix),'pnl known',x.notna().sum(),'median pnl',round(x.median()),'share net loss',round((x<0).mean(),3),'sum',round(x.sum()))
# pnl in last 30d before stop
fe2=fe.merge(stop[['last']],left_on='third_party_id',right_index=True)
l30=fe2[(fe2.d>fe2['last']-pd.Timedelta(days=30))].groupby('third_party_id').pnl.sum(min_count=1)
print('stoppers last-30d pnl median',round(l30.median()),'share loss',round((l30<0).mean(),3))
# (c) commodity selection: F&O intensity of commodity adopters vs not
fr=fe.groupby('third_party_id').agg(orders=('d','size'),days=('d','nunique'),rev=('brokerage_inr','sum'))
cu=set(R[(R.inst=='commodity')].id)&fno; su_=set(R[(R.inst=='stocks')].id)&fno
for lab,ix in [('comm adopters',cu),('non-comm',fno-cu),('stock adopters',su_),('non-stock',fno-su_)]:
    x=fr.reindex(list(ix)); print(lab,len(ix),'F&O median orders',x.orders.median(),'median days',x.days.median(),'mean rev',round(x.rev.mean()),'rev/day',round(x.rev.sum()/x.days.sum(),1))
ce=c[c.order_status.eq('EXECUTED')&c.third_party_id.isin(fno)]
print('commodity options share',ce.future_option.value_counts(normalize=True).round(3).to_dict())
# within-user: users with both commodity & MIS/CNC: ₹/active day
ss=s[s.order_status.eq('SUCCESS')&(s.rev>0)].copy(); ss['d']=ts(ss.created_at).dt.normalize()
both=cu&su_
cc=R[(R.inst=='commodity')&R.id.isin(both)]; st=ss[ss.third_party_id.isin(both)]
print('both users',len(both),'comm ₹/uday',round(cc.rev.sum()/len(cc.drop_duplicates(['id','d'])),1),
      'stock ₹/uday',round(st.rev.sum()/len(st.drop_duplicates(['third_party_id','d'])),1),
      'stock exMTF ₹/uday',round(st[st['product']!='MTF'].rev.sum()/len(st[st['product']!='MTF'].drop_duplicates(['third_party_id','d'])),1))
# fno ₹/day same set
fb=fe[fe.third_party_id.isin(both)]; print('same users F&O ₹/uday',round(fb.brokerage_inr.sum()/len(fb.drop_duplicates(['third_party_id','d'])),1))
# overlap days: share of commodity active days that are also F&O active days
fd=set(zip(fe.third_party_id,fe.d)); cdays=R[(R.inst=='commodity')&R.id.isin(fno)].drop_duplicates(['id','d'])
print('commodity days that are also F&O days',round(np.mean([(a,b) in fd for a,b in zip(cdays.id,cdays.d)]),3))
sdays=ss[ss.third_party_id.isin(fno)].drop_duplicates(['third_party_id','d'])
print('stock days that are also F&O days',round(np.mean([(a,b) in fd for a,b in zip(sdays.third_party_id,sdays.d)]),3))
# stoppers commodity: did commodity stop at same time? last commodity date vs last F&O
cl=R[(R.inst=='commodity')&R.id.isin(stop.index)].groupby('id').d.max()
sl=R[(R.inst=='stocks')&R.id.isin(stop.index)].groupby('id').d.max()
print('stopper comm users',len(cl),'last comm within ±7d of last F&O',int(((cl-stop['last'].reindex(cl.index)).dt.days.abs()<=7).sum()),'comm after F&O',int((cl>stop['last'].reindex(cl.index)).sum()))
print('stopper stock users',len(sl),'stock after F&O',int((sl>stop['last'].reindex(sl.index)).sum()))
# expiry NaT check & robustness w/ pt
fe['exp']=ts(fe.contracts_expiry_date).dt.normalize()
fe['pt_d']=pd.to_datetime(fe.pt).dt.normalize()
print('pt==created date share',(fe.pt_d==fe.d).mean(),'on exp via pt',(fe.pt_d==fe.exp).mean())
