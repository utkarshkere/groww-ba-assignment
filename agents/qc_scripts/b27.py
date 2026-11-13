import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
from scipy.stats import fisher_exact
D=d90(); globals().update(D)
HV=pickle.load(open('agents/qc_scripts/groups.pkl','rb'))['HV']
uu=u.set_index('third_party_id'); uu['su']=ts(uu.signup_ts); uu['mo']=uu.su.dt.to_period('M')
ch=uu.acquisition_channel
asa=uu.index[ch=='apple search ads']
C=co.third_party_id
ac=[x for x in asa if x in set(C)]
print('ASA cohort',len(ac))
for mo,ix in uu.loc[ac].groupby('mo').groups.items():
    x=r.reindex(ix); print(mo,len(ix),round(x.sum(),1),(x>0).sum(),'HV',len(set(ix)&HV),'top user',round(x.max(),1),'w/o top ₹/signup',round((x.sum()-x.max())/len(ix),1))
WA=W[W.id.isin(ac)]; print('ASA mix',(WA.groupby('inst').rev.sum()/WA.rev.sum()*100).round(1).to_dict())
print('cohort mix',(W.groupby('inst').rev.sum()/W.rev.sum()*100).round(1).to_dict())
X30=X[(X.dd>=0)&(X.dd<30)]; r30=X30.groupby('id').rev.sum().reindex(uu.index,fill_value=0)
grp=pd.Series('other',index=uu.index); grp[ch=='apple search ads']='ASA'; grp[ch=='organic']='Organic'; grp[ch=='google adwords']='Google'
rows=[]
for (g,mo),ix in uu.groupby([grp,uu.mo]).groups.items():
    if g=='other': continue
    x=r30[ix]; rows.append(dict(g=g,mo=str(mo),n=len(ix),rev=round(x.sum(),1),earn=round((x>0).mean()*100,1),top=round(x.max(),1),per=round(x.mean(),1),per_wo_top=round((x.sum()-x.max())/len(ix),1),earners=int((x>0).sum())))
t=pd.DataFrame(rows); pd.set_option('display.width',200)
print(t.pivot(index='mo',columns='g',values=['n','per','per_wo_top','earn']))
print(t[t.g=='ASA'])
print('ASA overall 30d',r30[asa].mean())
# % earning per month ASA vs Organic fisher
for mo in sorted(t.mo.unique()):
    a=t[(t.g=='ASA')&(t.mo==mo)].iloc[0]; o=t[(t.g=='Organic')&(t.mo==mo)].iloc[0]
    p=fisher_exact([[a.earners,a.n-a.earners],[o.earners,o.n-o.earners]])[1]
    print(mo,'ASA',a.earn,'Org',o.earn,'p',round(p,3))
a=t[t.g=='ASA']; o=t[t.g=='Organic']
print('pooled earn ASA',a.earners.sum()/a.n.sum(),'Org',o.earners.sum()/o.n.sum(),'p',fisher_exact([[a.earners.sum(),a.n.sum()-a.earners.sum()],[o.earners.sum(),o.n.sum()-o.earners.sum()]])[1])
# ASA 90d revenue: who are top users, months; HV months; top 3 share
x=r.reindex(ac).sort_values(ascending=False); print('ASA 90d top5',x.head(5).round(0).tolist(),'months',[str(uu.mo[i]) for i in x.index[:5]])
print('ASA HV months',uu.loc[[i for i in ac if i in HV]].mo.astype(str).value_counts().to_dict())
# ASA 90d excluding Jun+Jul
nj=[i for i in ac if str(uu.mo[i]) not in ('2026-06','2026-07')]; print('ASA 90d ex Jun-Jul',len(nj),round(r.reindex(nj).mean(),1))
# Organic & Google 90d by month
for g in ['Organic','Google']:
    ix=[i for i in uu.index[grp==g] if i in set(C)]
    print(g,'90d by month',r.reindex(ix).groupby(uu.mo[ix].values).mean().round(1).to_dict())
# ASA subchannel split
sub=uu.acquisition_subchannel
print(pd.DataFrame({'n':r.reindex(ac).groupby(sub[ac].values).size(),'rev':r.reindex(ac).groupby(sub[ac].values).sum().round(0),'HV':pd.Series([i in HV for i in ac],index=ac).groupby(sub[ac].values).sum()}))
print(t[t.g!='ASA'][['g','mo','n','per','per_wo_top','earn','top']].to_string(index=False))
WA2=W[W.id.isin(set(C))]; print('cohort mix fixed',(WA2.groupby('inst').rev.sum()/WA2.rev.sum()*100).round(2).to_dict())
# ASA 30d excl Jun-Jul signups
nj=[i for i in asa if str(uu.mo[i]) not in ('2026-06','2026-07')]; print('ASA 30d ex Jun-Jul',len(nj),round(r30[nj].mean(),1),'earn',round((r30[nj]>0).mean()*100,1))
for g in ['Organic','Google']:
    ix=uu.index[grp==g]; nj2=[i for i in ix if str(uu.mo[i]) not in ('2026-06','2026-07')]; print(g,'30d ex Jun-Jul',round(r30[nj2].mean(),1))
# ASA HV users: subchannel & are top 3 HV?
print('ASA top3 HV?',[x.index[k] in HV for k in range(3)], 'top3 share',round(x.head(3).sum()/x.sum()*100,1))
