import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
pd.set_option('display.width',200)
u,s,f,m,i,c,R=build()
END=pd.Timestamp('2026-10-31')
fe=f[f.order_status.eq('EXECUTED')].copy(); fe['t']=ts(fe.order_created_at); fe['d']=fe.t.dt.normalize()
fno=set(fe.third_party_id)
# stock rows with product
ss=s[s.order_status.eq('SUCCESS')&(s.rev>0)].copy(); ss['t']=ts(ss.created_at)
R=R[R.rev>0].copy(); R['d']=R.t.dt.normalize()
RF=R[R.id.isin(fno)]
print('1: users stock',RF[RF.inst=='stocks'].id.nunique(),'comm',RF[RF.inst=='commodity'].id.nunique())
sf=ss[ss.third_party_id.isin(fno)]
print(sf.groupby('product').agg(users=('third_party_id','nunique'),rev=('rev','sum'),orders=('rev','size')).round(0))
print(RF.groupby('inst').rev.sum().round(0).to_dict())
def st(x,l):
    x=x.sort_values(ascending=False); print(l,'n',len(x),'mean',round(x.mean(),1),'median',round(x.median(),1),'top5',round(x.iloc[:5].sum()/x.sum()*100,1))
st(RF[RF.inst=='stocks'].groupby('id').rev.sum(),'2 stocks'); st(RF[RF.inst=='commodity'].groupby('id').rev.sum(),'2 comm')
first=RF.groupby(['id','inst']).t.min().unstack()
for k in ['commodity','stocks']:
    b=first[first[k].notna()&first.fno.notna()]
    print('3',k,len(b),'other first',(b[k]<b.fno).sum(),'fno first',(b.fno<b[k]).sum(),'tie',(b.fno==b[k]).sum())
# stoppers
g=fe.groupby('third_party_id').agg(n=('d','size'),last=('d','max'),first=('d','min'))
stop=g[(g.n>=5)&(g.last<=END-pd.Timedelta(days=60))].copy()
print('stoppers',len(stop))
S=R[R.id.isin(stop.index)].merge(stop[['last']],left_on='id',right_index=True)
aft=S[S.d>S['last']]; bef=S[S.d<=S['last']]
print('4 any after',aft.id.nunique(),'stocks',aft[aft.inst=='stocks'].id.nunique(),round(aft[aft.inst=='stocks'].rev.sum()),
 'comm',aft[aft.inst=='commodity'].id.nunique(),round(aft[aft.inst=='commodity'].rev.sum()),
 'mf/ipo only',(aft.groupby('id').inst.apply(lambda x:set(x)<= {'mf','ipo'})).sum(), 'fno after (should 0)',(aft.inst=='fno').sum())
print('after by inst',aft.groupby('inst').rev.sum().to_dict())
bu={k:set(bef[bef.inst==k].id) for k in ['stocks','commodity']}; au={k:set(aft[aft.inst==k].id) for k in ['stocks','commodity']}
print('5 before stocks',len(bu['stocks']),'comm',len(bu['commodity']),'new stocks after',len(au['stocks']-bu['stocks']),'new comm after',len(au['commodity']-bu['commodity']))
for lo in [59,60]:
    w=S[(S.d>S['last']-pd.Timedelta(days=lo))&(S.d<=S['last'])]
    print('6 window lo',lo,'fno',w[w.inst=='fno'].rev.sum(),'stk',w[w.inst=='stocks'].rev.sum(),'comm',w[w.inst=='commodity'].rev.sum())
print('6 after stk+comm',aft[aft.inst.isin(['stocks','commodity'])].rev.sum())
stop['obs']=(END-stop['last']).dt.days
print('median days after',stop.obs.median(),'min',stop.obs.min(),'max',stop.obs.max())
# 7
for lo in [59,60]:
    w=S[(S.d>S['last']-pd.Timedelta(days=lo))&(S.d<=S['last'])]
    for k in [['stocks','commodity'],['stocks'],['commodity']]:
        b=w[w.inst.isin(k)].rev.sum()/2
        a=aft[aft.inst.isin(k)].groupby('id').rev.sum().reindex(stop.index,fill_value=0)
        ar=(a/stop.obs*30).sum()
        print('7 lo',lo,k,'before/30d',round(b),'after/30d',round(ar), 'pooled after',round(a.sum()/stop.obs.sum()*30*len(stop)))
stop.to_pickle('agents/qc_scripts/stoppers.pkl')
# 8 economics
RF2=RF.copy()
sp=ss[ss.third_party_id.isin(fno)][['third_party_id','product','rev','t']].rename(columns={'third_party_id':'id'})
sp['inst']='stk_'+sp['product']; sp['d']=sp.t.dt.normalize()
E=pd.concat([RF2[RF2.inst.isin(['fno','commodity'])][['id','inst','rev','d']],sp[['id','inst','rev','d']]])
e=E.groupby('inst').agg(orders=('rev','size'),rev=('rev','sum'))
e['per_order']=e.rev/e.orders
e['udays']=E.drop_duplicates(['id','inst','d']).groupby('inst').size()
e['per_day']=e.rev/e.udays; print(e.round(1))
# 9 expiry
fe['exp']=ts(fe.contracts_expiry_date).dt.normalize()
fe['on_exp']=fe.d.eq(fe.exp)
print('9 on expiry share',fe.on_exp.mean(), 'exp NaT',fe.exp.isna().sum())
pu=fe.groupby('third_party_id').agg(sh=('on_exp','mean'),rev=('brokerage_inr','sum'))
h=pu[pu.sh>=0.5]; print('users >=50%',len(h),'rev share',h.rev.sum()/pu.rev.sum())
print('contract types',fe.contract_type.value_counts(normalize=True).round(3).to_dict())
