import pandas as pd, numpy as np
D='data/'
def load():
    u=pd.read_csv(D+'users.csv',low_memory=False)
    s=pd.read_csv(D+'stocks_orders.csv',low_memory=False)
    f=pd.read_csv(D+'fno_orders.csv',low_memory=False)
    m=pd.read_csv(D+'mf_orders.csv',low_memory=False)
    i=pd.read_csv(D+'ipo_orders.csv',low_memory=False)
    c=pd.read_csv(D+'commodity_orders.csv',low_memory=False)
    return u,s,f,m,i,c
def ts(x): return pd.to_datetime(x,format='ISO8601',errors='coerce')
def stock_rev(s):
    s=s.copy()
    succ=s.order_status.eq('SUCCESS')
    ob=pd.to_numeric(s.original_brokerage,errors='coerce')
    t=pd.to_numeric(s.turnover_inr,errors='coerce').fillna(0)
    imp_cm=np.minimum(20,np.minimum(np.maximum(5,0.001*t),0.025*t))
    imp=np.where(s['product'].eq('MTF'),0.001*t,imp_cm)
    s['blank']=succ&ob.isna()
    s['rev']=np.where(~succ,0,np.where(ob.notna(),ob,imp))
    s['rev_recorded']=np.where(succ&ob.notna(),ob,0)
    return s
def build():
    u,s,f,m,i,c=load()
    s=stock_rev(s)
    rows=[]
    rows.append(pd.DataFrame({'id':s.third_party_id,'inst':'stocks','rev':s.rev,'t':ts(s.created_at)}))
    fe=f[f.order_status.eq('EXECUTED')]
    rows.append(pd.DataFrame({'id':fe.third_party_id,'inst':'fno','rev':pd.to_numeric(fe.brokerage_inr),'t':ts(fe.order_created_at)}))
    ce=c[c.order_status.eq('EXECUTED')]
    rows.append(pd.DataFrame({'id':ce.third_party_id,'inst':'commodity','rev':pd.to_numeric(ce.brokerage_inr),'t':ts(ce.created_at)}))
    me=m[m.order_status.eq('COMPLETED')]
    rows.append(pd.DataFrame({'id':me.third_party_id,'inst':'mf','rev':pd.to_numeric(me.brokerage_inr),'t':ts(me.created_at)}))
    ib=pd.to_numeric(i.brokerage_inr,errors='coerce')
    ie=i[ib>0]
    rows.append(pd.DataFrame({'id':ie.third_party_id,'inst':'ipo','rev':ib[ib>0],'t':ts(ie.created_at)}))
    R=pd.concat(rows,ignore_index=True)
    return u,s,f,m,i,c,R
