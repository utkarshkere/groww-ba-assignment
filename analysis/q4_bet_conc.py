"""Concentration inside each candidate bet base (Apr-Oct)."""
import pandas as pd
r = pd.read_pickle('rev_orders.pkl')
fno = set(r[(r.instr=='fno')&(r.rev>0)].third_party_id)
stk = r[r.instr=='stocks']
def prof(pu, lab):
    pu = pu[pu>0].sort_values(ascending=False); n=len(pu); T=pu.sum()
    print(f"{lab}: n={n} total={T:,.0f} mean={T/n:,.0f} median={pu.median():,.1f} "
          f"top1={pu.iloc[0]/T*100:.1f}% top5={pu.head(5).sum()/T*100:.1f}% top10={pu.head(10).sum()/T*100:.1f}% "
          f"mean_excl_top5={pu.iloc[5:].mean():,.0f}  users>=Rs500={(pu>=500).sum()}")
mtf = stk[stk['product']=='MTF']
prof(mtf.groupby('third_party_id').rev.sum(), 'MTF all')
m_nf = mtf[~mtf.third_party_id.isin(fno)]
prof(m_nf.groupby('third_party_id').rev.sum(), 'MTF non-F&O users')
m_f = mtf[mtf.third_party_id.isin(fno)]
prof(m_f.groupby('third_party_id').rev.sum(), 'MTF F&O users')
nf = stk[~stk.third_party_id.isin(fno)]
prof(nf.groupby('third_party_id').rev.sum(), 'All stock rev, non-F&O users')
pu = mtf.groupby('third_party_id').rev.sum().sort_values(ascending=False)
print('top 10 MTF users: rev, is F&O'); print(pd.DataFrame({'rev':pu.head(10).round(0),'fno':pu.head(10).index.isin(fno)}).reset_index(drop=True))
# MTF turnover & orders
mt = mtf.groupby('third_party_id').agg(orders=('rev','size'), turnover=('turnover_inr','sum'))
print('MTF orders per user median', mt.orders.median(), '| turnover median', round(mt.turnover.median()), '| total MTF turnover', round(mt.turnover.sum()))
# monthly MTF revenue
print(mtf.groupby(mtf.ts.dt.to_period('M')).agg(rev=('rev','sum'), users=('third_party_id','nunique')).round(0))
