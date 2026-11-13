import sys; sys.path.insert(0,'agents/qc_scripts')
from qc_base import *
u,s,f,m,i,c,R=build()
fno=set(f.loc[f.order_status.eq('EXECUTED'),'third_party_id'])
print('fno users',len(fno))
ss=s[s.order_status.eq('SUCCESS')].copy()
ss['t']=ts(ss.created_at); ss['mo']=ss.t.dt.to_period('M')
mtf=ss[ss['product'].eq('MTF')]
mtfu=set(mtf.third_party_id); cncu=set(ss.loc[ss['product'].eq('CNC'),'third_party_id'])
print('1: mtf users',len(mtfu),'rev',mtf.rev.sum(),'imputed share',mtf.loc[mtf.blank,'rev'].sum()/mtf.rev.sum(),'imputed orders',mtf.blank.sum(),'of',len(mtf))
print('2: delivery',len(cncu),'mtf no cnc',len(mtfu-cncu))
fm=mtf[mtf.third_party_id.isin(fno)]
print('3: mtf&fno',len(mtfu&fno),len(mtfu&fno)/len(mtfu),'rev',fm.rev.sum(),fm.rev.sum()/mtf.rev.sum())
def conc(x,label):
    x=x.sort_values(ascending=False); T=x.sum()
    print(label,'n',len(x),'sum',round(T,1),'mean',round(x.mean(),1),'median',round(x.median(),2),
      'top1',round(x.iloc[:1].sum()/T*100,1),'top5',round(x.iloc[:5].sum()/T*100,1),'top10',round(x.iloc[:10].sum()/T*100,1),
      'mean_ex5',round(x.iloc[5:].mean(),1),'>=500',(x>=500).sum(),'max',round(x.iloc[0],1))
pu=mtf.groupby('third_party_id').rev.sum()
conc(pu,'4: all mtf'); top=pu.idxmax(); print('top in fno',top in fno)
conc(pu[~pu.index.isin(fno)],'5: nonfno mtf'); conc(pu[pu.index.isin(fno)],'5: fno mtf')
d_f=cncu&fno; d_n=cncu-fno
print('6: fno delivery',len(d_f),'mtf',len(d_f&mtfu),len(d_f&mtfu)/len(d_f),'| nonfno',len(d_n),len(d_n&mtfu),len(d_n&mtfu)/len(d_n))
ce=c[c.order_status.eq('EXECUTED')]
print('7: commodity',ce[ce.third_party_id.isin(fno)].brokerage_inr.sum()/ce.brokerage_inr.sum(),
  'stock',ss[ss.third_party_id.isin(fno)].rev.sum()/ss.rev.sum(),
  'stock exMTF',ss[ss.third_party_id.isin(fno)&~ss['product'].eq('MTF')].rev.sum()/ss[~ss['product'].eq('MTF')].rev.sum())
sp=ss.groupby('third_party_id').rev.sum()
nf=sp[~sp.index.isin(fno)]
conc(nf,'8: nonfno stock (all succ users)'); conc(nf[nf>0],'8: nonfno stock rev>0')
print('stock users with succ but 0 rev', (sp==0).sum())
# 9
g=mtf.groupby('mo').agg(rev=('rev','sum'),users=('third_party_id','nunique'),orders=('rev','size'),
   rec=('rev_recorded','sum'),blank=('blank','mean'),turn=('turnover_inr','sum'))
g['rev_per_user']=g.rev/g.users; g['rev_per_turn_bps']=g.rev/g.turn*1e4
print(g.round(2))
po=mtf.groupby('third_party_id').agg(n=('rev','size'),turn=('turnover_inr','sum'))
print('9: total turnover',mtf.turnover_inr.sum(),'median orders',po.n.median(),'median turn',po.turn.median())
# cumulative signups by month & mtf first-use month
u['su']=ts(u.signup_ts).dt.to_period('M')
print('cum signups',u.su.value_counts().sort_index().cumsum().to_dict())
fu=mtf.groupby('third_party_id').t.min().dt.to_period('M').value_counts().sort_index()
print('new mtf users by month',fu.to_dict())
# monthly rev excluding top user / top5
top5=pu.sort_values(ascending=False).index[:5]
print('ex top5 monthly',mtf[~mtf.third_party_id.isin(top5)].groupby('mo').rev.sum().round(0).to_dict())
print('top1 monthly',mtf[mtf.third_party_id.eq(top)].groupby('mo').rev.sum().round(0).to_dict())
# non-MTF stock monthly for comparison
nm=ss[~ss['product'].eq('MTF')]
print('nonMTF stock monthly rev',nm.groupby('mo').rev.sum().round(0).to_dict())
print('nonMTF users',nm.groupby('mo').third_party_id.nunique().to_dict())
# Sizing check: 550 * 567
print('550*567',550*567,'550*median',550*pu.median(),'550*mean_ex5',550*pu.sort_values(ascending=False).iloc[5:].mean())
# per-user revenue normalised by active months for MTF vs nonfno stock
