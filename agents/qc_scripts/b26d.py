import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV,LAP,other=G['HV'],G['LAP'],G['other']
Wd=W.assign(d=W.t.dt.normalize())
for lab,Gs in [('HV',HV),('LAP',LAP),('OTHER',other)]:
    x=Wd[Wd.id.isin(Gs)]; tr=x[x.inst.isin(['fno','stocks','commodity'])]
    per=tr.drop_duplicates(['id','d']).groupby('id').size().reindex(list(Gs),fill_value=0)
    wk=tr[tr.d.dt.weekday<5].drop_duplicates(['id','d']).groupby('id').size().reindex(list(Gs),fill_value=0)
    fs=x[x.inst.isin(['fno','stocks'])].drop_duplicates(['id','d']).groupby('id').size().reindex(list(Gs),fill_value=0)
    print(lab,'trading mean',round(per.mean(),1),'median',per.median(),'weekday-only mean',round(wk.mean(),1),'F&O+stocks only',round(fs.mean(),1))
uu=u.set_index('third_party_id'); C=uu.loc[co.third_party_id]; onb=C[C.stock_onboarding_ts.notna()]
inc=lambda d: d.income.dropna().astype(str).str[0].isin(list('cdefgh')).mean()
hvd=uu.loc[list(HV)]
print('income>=5L (of stated) HV',round(inc(hvd),3),'onboarded',round(inc(onb),3),'non-HV onb',round(inc(onb.drop(list(HV))),3),'cohort',round(inc(C),3))
print('income stated HV',hvd.income.notna().mean(),'onb',onb.income.notna().mean())
inc2=lambda d: d.income.astype(str).str[0].isin(list('cdefgh')).mean()
print('income>=5L (of all) HV',round(inc2(hvd),3),'onb',round(inc2(onb),3))
print('age median HV',hvd.age.median(),'non-HV cohort',C.drop(list(HV)).age.median(),'non-HV onboarded',onb.drop(list(HV)).age.median())
