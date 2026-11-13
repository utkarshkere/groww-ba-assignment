import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
G=pickle.load(open('agents/qc_scripts/groups.pkl','rb')); HV=G['HV']
uu=u.set_index('third_party_id'); C=uu.loc[co.third_party_id].copy()
ch=C.acquisition_channel; sub=C.acquisition_subchannel
grp=pd.Series('other',index=C.index)
grp[ch=='apple search ads']='ASA'; grp[ch=='organic']='Organic'; grp[ch=='google adwords']='Google'
grp[ch=='referral']='Referral'; grp[ch=='zee']='Zee'; grp[ch.isin(['hindustantin956','hindustan7bj_int'])]='HT'
grp[(ch=='ad partner')&(sub=='ndtvconverin157')]='NDTV'; grp[ch.isin(['timesinternet','timesinternetint'])]='Times'
grp[ch=='newsnationin592']='NewsNation'
grp[(ch=='google adwords')&(sub=='uac_android_v3_all_fid_troas')]='Google main'
rr=r.reindex(C.index)
def row(ix,lab):
    x=rr[ix].sort_values(ascending=False); n=len(x)
    print(f'{lab:12s} n={n:5d} ₹/signup={x.mean():6.1f} w/o top={x.iloc[1:].mean():6.1f} w/o top2={x.iloc[2:].mean():6.1f} w/o top3={x.iloc[3:].mean():6.1f} top share={x.iloc[0]/x.sum()*100:4.0f}% top3={x.iloc[:3].sum()/x.sum()*100:3.0f}% HV={len(set(ix)&HV)} earning={(x>0).mean()*100:4.1f}% median earner={x[x>0].median():.1f}')
for g in ['ASA','NewsNation','Referral','HT','Zee','Google main','Organic','Times','NDTV']:
    row(grp[grp==g].index,g)
gix=C.index[ch=='google adwords']; row(gix,'Google all')
oth=C.index[(ch=='google adwords')&(sub!='uac_android_v3_all_fid_troas')]; row(oth,'Google other')
for sc,x in rr[oth].groupby(sub[oth]): print('   ',sc,len(x),round(x.mean(),1),len(set(x.index)&HV))
print('overall',rr.mean(),'HV rate',len(HV)/len(C))
from scipy.stats import fisher_exact, mannwhitneyu
a=grp[grp=='ASA'].index; o=grp[grp=='Organic'].index
print('ASA HV fisher p',fisher_exact([[len(set(a)&HV),len(a)-len(set(a)&HV)],[len(set(o)&HV),len(o)-len(set(o)&HV)]])[1])
xa=rr[a][rr[a]>0]; xo=rr[o][rr[o]>0]; print('median earner MWU p',mannwhitneyu(xa,xo).pvalue)
for g in ['HT','Zee']:
    ix=grp[grp==g].index; e1=(rr[ix]>0).sum(); e2=(rr[o]>0).sum()
    print(g,'earning fisher p',fisher_exact([[e1,len(ix)-e1],[e2,len(o)-e2]])[1],'HV p',fisher_exact([[len(set(ix)&HV),len(ix)-len(set(ix)&HV)],[len(set(o)&HV),len(o)-len(set(o)&HV)]])[1])
# trimmed top 1% of users overall
cut=rr.quantile(0.99); 
for g in ['HT','Zee','Organic']:
    ix=grp[grp==g].index; print(g,'trim top1% overall cutoff',round(rr[ix].clip(upper=cut).mean(),1),'drop>cut',round(rr[ix][rr[ix]<=cut].mean(),1))
# 30-day all signups
u['su']=ts(u.signup_ts); X30=X[(X.dd>=0)&(X.dd<30)]; r30=X30.groupby('id').rev.sum().reindex(u.third_party_id,fill_value=0)
ua=u.set_index('third_party_id'); g30=pd.Series('x',index=ua.index)
g30[ua.acquisition_channel=='apple search ads']='ASA'; g30[ua.acquisition_channel=='organic']='Organic'; g30[ua.acquisition_channel=='google adwords']='Google'; g30[ua.acquisition_channel=='referral']='Referral'
g30[(ua.acquisition_channel=='ad partner')&(ua.acquisition_subchannel=='ndtvconverin157')]='NDTV'
print('30d all signups',r30.groupby(g30.reindex(r30.index)).mean().round(1).to_dict())
import math
for g in ['HT','Zee','Organic']:
    ix=grp[grp==g].index; x=rr[ix].sort_values(ascending=False); k=math.ceil(len(x)*0.01); k2=round(len(x)*0.01); k3=int(len(x)*0.01)
    print(g,'own top1% removed ceil',round(x.iloc[k:].mean(),1),'round',round(x.iloc[k2:].mean(),1),'floor',round(x.iloc[k3:].mean(),1), 'winsor own p99',round(x.clip(upper=x.quantile(.99)).mean(),1))
