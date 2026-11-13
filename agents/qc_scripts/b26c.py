import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV,LAP,TOP,other=G['HV'],G['LAP'],G['TOP'],G['other']
T=r.sum(); cs=co.set_index('third_party_id').su
cum=r.cumsum()/T; p80=list(r.index[:int((cum<0.8).sum())+1]); m3=set(W[W.dd>=60].id)
print('def2',len(p80),round(r[p80].sum()/T*100,1),'lapsed',len(set(p80)-m3),'misses',len(HV-set(p80)))
# F&O-only dropped composition
WF=W[W.inst=='fno']; rf=WF.groupby('id').rev.sum(); m3f=set(WF[WF.dd>=60].id)
Bset=set(x for x in rf.index if rf[x]>=733.8 and x in m3f); drop=HV-Bset
gd=W[W.id.isin(drop)]
print('dropped',len(drop),'no F&O at all',len(drop-set(WF.id)),'median orders',gd.groupby('id').size().median(),'main',gd.groupby(['id','inst']).rev.sum().unstack().fillna(0).idxmax(axis=1).value_counts().to_dict())
# all-order timing frames (any status) for trading days
def frame(df,tcol,inst,okcol=None):
    x=df[['third_party_id',tcol]].copy(); x.columns=['id','t']; x['t']=ts(x.t); x['inst']=inst; return x
sd=s.copy(); sd['ok']=sd.order_status.eq('SUCCESS')
A=pd.concat([frame(s,'created_at','stocks'),frame(f,'order_created_at','fno'),frame(c,'created_at','commodity'),frame(m,'created_at','mf'),frame(i,'created_at','ipo')])
A=A.merge(cs.rename('su'),left_on='id',right_index=True); A['dd']=(A.t-A.su).dt.total_seconds()/86400
A90=A[(A.dd>=0)&(A.dd<90)]; A90['d']=A90.t.dt.normalize()
Wd=W.assign(d=W.t.dt.normalize())
for lab,Gs in [('HV',HV),('LAP',LAP),('OTHER',other)]:
    n=len(Gs)
    trd=Wd[Wd.id.isin(Gs)&Wd.inst.isin(['fno','stocks','commodity'])]
    print(lab,'rev-days all inst',round(Wd[Wd.id.isin(Gs)].drop_duplicates(['id','d']).shape[0]/n,1),
          'rev-days trading only',round(trd.drop_duplicates(['id','d']).shape[0]/n,1),
          'rev-days trading only among users w/ trading',round(trd.drop_duplicates(['id','d']).shape[0]/max(1,trd.id.nunique()),1),
          'any-order days',round(A90[A90.id.isin(Gs)].drop_duplicates(['id','d']).shape[0]/n,1),
          'all orders any status',round(len(A90[A90.id.isin(Gs)])/n,1),
          'rev orders',round(len(W[W.id.isin(Gs)])/n,1))
    # median stock turnover among stock traders
    st=s[s.third_party_id.isin(Gs)&s.order_status.eq('SUCCESS')].copy(); st['t']=ts(st.created_at)
    st=st.merge(cs.rename('su'),left_on='third_party_id',right_index=True); st=st[((st.t-st.su).dt.total_seconds()/86400).between(0,90,inclusive='left')]
    print('   median stock turnover',round(st.groupby('third_party_id').turnover_inr.sum().median()),'MTF users share',round(st[st['product'].eq('MTF')].third_party_id.nunique()/n,3))
    fr=f[f.third_party_id.isin(Gs)&f.order_status.eq('REJECTED')].copy(); fr['t']=ts(fr.order_created_at)
    fr=fr.merge(cs.rename('su'),left_on='third_party_id',right_index=True); fr=fr[((fr.t-fr.su).dt.total_seconds()/86400).between(0,90,inclusive='left')]
    print('   F&O rejections',len(fr),'margin share',round(fr.error_reasons_cleaned.fillna('').str.contains('Margin',case=False).mean(),3))
    fe=f[f.third_party_id.isin(Gs)&f.order_status.eq('EXECUTED')].copy(); fe['t']=ts(fe.order_created_at)
    fe=fe.merge(cs.rename('su'),left_on='third_party_id',right_index=True); fe=fe[((fe.t-fe.su).dt.total_seconds()/86400).between(0,90,inclusive='left')]
    fe['pnl']=pd.to_numeric(fe.pnl,errors='coerce')
    pu=fe.groupby('third_party_id').agg(p=('pnl','sum'),b=('brokerage_inr','sum'))
    print('   F&O users',len(pu),'median loss per ₹1',round((-pu.p/pu.b).median(),2),'net losers',round((pu.p<0).mean(),3),'total pnl',round(pu.p.sum()))
# demographics & KRA
uu=u.set_index('third_party_id'); C=uu.loc[co.third_party_id]
onb=C[C.stock_onboarding_ts.notna()]
print('onboarded in cohort',len(onb))
hvd=uu.loc[list(HV)]
print('median age HV',hvd.age.median(),'onboarded',onb.age.median(),'cohort',C.age.median(),'non-HV onboarded',onb.drop(list(HV),errors='ignore').age.median())
inc=lambda d: d.income.dropna().astype(str).str[0].isin(list('defgh')).mean()
print('income values',sorted(uu.income.dropna().unique()))
print('income>=5L HV',round(inc(hvd),3),'onboarded',round(inc(onb),3),'non-HV onb',round(inc(onb.drop(list(HV),errors='ignore')),3))
print('HV kra_verified',round((hvd.kra_flag=='kra_verified').mean(),3),'onboarded',round((onb.kra_flag=='kra_verified').mean(),3))
print('HV onboarded',hvd.stock_onboarding_ts.notna().sum())
kv=onb[onb.kra_flag=='kra_verified']; ko=onb[onb.kra_flag!='kra_verified']
print('HV rate kra_verified',round(kv.index.isin(list(HV)).mean()*100,2),'others',round(ko.index.isin(list(HV)).mean()*100,2))
# lapsed: any order at all in m3
print('lapsed any order (any status) in d60-90',A90[A90.id.isin(LAP)&(A90.dd>=60)].id.nunique())
