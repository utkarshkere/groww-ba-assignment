import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
def d90():
    u,s,f,m,i,c,R=build()
    u['su']=ts(u.signup_ts)
    co=u[u.su<pd.Timestamp('2026-08-03')].copy()
    X=R[R.rev>0].merge(u[['third_party_id','su']],left_on='id',right_on='third_party_id')
    X['dd']=(X.t-X.su).dt.total_seconds()/86400
    W=X[(X.dd>=0)&(X.dd<90)]
    r=W.groupby('id').rev.sum().reindex(co.third_party_id,fill_value=0).sort_values(ascending=False,kind='mergesort')
    top=list(r.index[:127])
    m3=set(W[W.dd>=60].id)
    hv=[x for x in top if x in m3]; lap=[x for x in top if x not in m3]
    return dict(u=u,s=s,f=f,m=m,i=i,c=c,R=R,co=co,X=X,W=W,r=r,top=top,hv=hv,lap=lap)
