"""Q4 check: does MTF revenue come from the same F&O-trader pocket (like commodity)?"""
import pandas as pd
r = pd.read_pickle('analysis/rev_orders.pkl')
fno_users = set(r[(r.instr == 'fno') & (r.rev > 0)].third_party_id)
stk = r[r.instr == 'stocks']
mtf = stk[stk['product'] == 'MTF']
mtf_users = set(mtf.third_party_id)
cnc_users = set(stk[stk['product'] == 'CNC'].third_party_id)
print('F&O users', len(fno_users), '| MTF users', len(mtf_users), '| delivery (CNC) traders', len(cnc_users))
print('MTF revenue', round(mtf.rev.sum()), '| imputed share', round(mtf[mtf.imputed].rev.sum() / mtf.rev.sum() * 100, 1))

ov = mtf_users & fno_users
mtf_rev_fno = mtf[mtf.third_party_id.isin(fno_users)].rev.sum()
print(f'MTF users who also trade F&O: {len(ov)} of {len(mtf_users)} ({len(ov)/len(mtf_users)*100:.1f}%)')
print(f'MTF revenue from F&O users: {mtf_rev_fno:,.0f} of {mtf.rev.sum():,.0f} ({mtf_rev_fno/mtf.rev.sum()*100:.1f}%)')
# robustness: concentration inside MTF
pu = mtf.groupby('third_party_id').rev.sum().sort_values(ascending=False)
print('top1 / top5 / top10 share of MTF revenue', [round(pu.head(k).sum() / pu.sum() * 100, 1) for k in (1, 5, 10)])
print('MTF users excl. F&O: n', len(mtf_users - fno_users), 'rev', round(pu[~pu.index.isin(fno_users)].sum()),
      'median per user', round(pu[~pu.index.isin(fno_users)].median()), '| F&O-overlap median', round(pu[pu.index.isin(fno_users)].median()))

# adoption among delivery traders, split by F&O status
for lab, grp in [('F&O traders', cnc_users & fno_users), ('non-F&O', cnc_users - fno_users)]:
    k = len(grp & mtf_users)
    print(f'MTF adoption among delivery traders who are {lab}: {k} of {len(grp)} ({k/len(grp)*100:.1f}%)')
# MTF users who are not CNC traders
print('MTF users without any CNC order', len(mtf_users - cnc_users))
# comparison: commodity and all stocks
com = r[r.instr == 'commodity']
print('commodity rev from F&O users %', round(com[com.third_party_id.isin(fno_users)].rev.sum() / com.rev.sum() * 100, 1))
print('all stock rev from F&O users %', round(stk[stk.third_party_id.isin(fno_users)].rev.sum() / stk.rev.sum() * 100, 1))
nonmtf = stk[stk['product'] != 'MTF']
print('non-MTF stock rev from F&O users %', round(nonmtf[nonmtf.third_party_id.isin(fno_users)].rev.sum() / nonmtf.rev.sum() * 100, 1))
