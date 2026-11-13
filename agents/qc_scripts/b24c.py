import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
u,s,f,m,i,c,R=build()
fe=f[f.order_status.eq('EXECUTED')].copy(); fe['d']=ts(fe.order_created_at).dt.normalize()
dd=fe.drop_duplicates(['third_party_id','d']).sort_values(['third_party_id','d'])
dd['gap']=dd.groupby('third_party_id').d.diff().dt.days
n=fe.groupby('third_party_id').size()
g5=dd[dd.third_party_id.isin(n[n>=5].index)]
print('users >=5 orders',(n>=5).sum(),'with a >=60d gap then resumed',g5[g5.gap>=60].third_party_id.nunique(),
      'gap>=30',g5[g5.gap>=30].third_party_id.nunique())
