import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
import pickle
D=d90(); globals().update(D)
defs=pickle.load(open('agents/qc_scripts/defs.pkl','rb'))
cs=co.set_index('third_party_id').su
elig=set(cs[cs+pd.Timedelta(days=120)<=pd.Timestamp('2026-11-01')].index)
B=X[(X.dd>=90)&(X.dd<120)&X.id.isin(elig)]; br=B.groupby('id').rev.sum(); TB=br.sum()
for k in [0,1,4]:
    v=br.reindex([x for x in defs[k] if x in elig],fill_value=0).sort_values(ascending=False)
    print('def',k,'top1/top3 share of its next ₹',round(v.iloc[0]/v.sum()*100,1),round(v.iloc[:3].sum()/v.sum()*100,1),'ex-top3 share of all',round(v.iloc[3:].sum()/TB*100,1))
# (c)
s=D['s']; f=D['f']
fno=set(f.loc[f.order_status.eq('EXECUTED'),'third_party_id'])
ss=s[s.order_status.eq('SUCCESS')]
sp=ss.groupby('third_party_id').rev.sum(); nf=sp[~sp.index.isin(fno)].sort_values(ascending=False)
print('non-F&O stock users',len(nf),round(nf.sum()),'>=500',(nf>=500).sum())
below=nf[nf<500]; t170=below.iloc[:170]
print('170 range',round(t170.min(),1),round(t170.max(),1),'median',round(t170.median(),1))
g1=(500-t170).sum(); med=nf[nf>=500].median(); g2=(med-t170).sum()
print('lift to 500',round(g1),round(g1/310386*100,1),'| median of 500+',round(med,1),'lift',round(g2),round(g2/310386*100,1),'| vs 3.1L',round(g1/310000*100,1),round(g2/310000*100,1))
# context: tenure of these 170 & distribution
uu=u.set_index('third_party_id'); su=ts(uu.signup_ts)
ten=((pd.Timestamp('2026-10-31')-su[t170.index]).dt.days); ten5=((pd.Timestamp('2026-10-31')-su[nf[nf>=500].index]).dt.days)
print('tenure days median 170',ten.median(),'500+ group',ten5.median())
print('signup month 170',su[t170.index].dt.to_period('M').value_counts().sort_index().to_dict())
print('signup month 500+',su[nf[nf>=500].index].dt.to_period('M').value_counts().sort_index().to_dict())
# per-month rate: rev / months since first stock order
ss2=ss.assign(t=ts(ss.created_at)); first=ss2.groupby('third_party_id').t.min()
mon=lambda ix: ((pd.Timestamp('2026-11-01')-first[ix]).dt.days/30.44)
print('₹/month 170 median',round((t170/mon(t170.index)).median(),1),'500+ median',round((nf[nf>=500]/mon(nf[nf>=500].index)).median(),1))
# observed natural movement: users in ₹99-498 range by end-Aug who crossed 500 by end-Oct
cut=pd.Timestamp('2026-09-01')
a=ss2[ss2.t<cut].groupby('third_party_id').rev.sum(); a=a[~a.index.isin(fno)]
b=nf
band=a[(a>=99)&(a<500)]; crossed=(b.reindex(band.index)>=500).sum()
print('natural: non-F&O users with ₹99-499 by 31 Aug',len(band),'crossed ₹500 by 31 Oct',crossed,round(crossed/len(band)*100,1),'their extra ₹ Sep-Oct',round((b.reindex(band.index)-band).sum()))
# imputed share in this pool
imp=ss[ss.blank&ss.third_party_id.isin(t170.index)].rev.sum(); print('imputed share of 170 group revenue',round(imp/t170.sum()*100,1))
