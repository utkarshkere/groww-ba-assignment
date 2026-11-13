"""Q4 bet 2: if F&O traders stop F&O (regulation), where do they go — stocks or commodity?
Lenses: (1) what F&O traders already trade, (2) what F&O 'stoppers' did after their last F&O trade,
(3) revenue economics per trader / per active day, (4) who is most exposed (expiry-day share)."""
import pandas as pd, numpy as np
W = 'analysis/'
r = pd.read_pickle(W + 'rev_orders.pkl')
r = r[r.rev > 0].copy()
r['d'] = r.ts.dt.normalize()
END = pd.Timestamp('2026-10-31')
fno = r[r.instr == 'fno']
F = set(fno.third_party_id)
print('F&O traders', len(F))

# ---------- (1) what F&O traders already trade (Apr-Oct)
rf = r[r.third_party_id.isin(F)]
stk = rf[rf.instr == 'stocks']
print('\n(1) F&O traders who also earn in: stocks', stk.third_party_id.nunique(),
      '| commodity', rf[rf.instr == 'commodity'].third_party_id.nunique())
for p in ['MIS', 'CNC', 'MTF']:
    print(f'   stocks {p}: users', stk[stk['product'] == p].third_party_id.nunique(), 'rev', round(stk[stk['product'] == p].rev.sum()))
print('   revenue from F&O traders by instr:', rf.groupby('instr').rev.sum().round(0).to_dict())
# per user among those who use it
for ins in ['stocks', 'commodity']:
    pu = rf[rf.instr == ins].groupby('third_party_id').rev.sum()
    print(f'   {ins} per F&O trader using it: mean {pu.mean():.0f} median {pu.median():.0f} top5 share {pu.nlargest(5).sum()/pu.sum()*100:.0f}%')

# sequence: did commodity / stocks start before or after first F&O?
first = r.groupby(['third_party_id', 'instr']).ts.min().unstack()
both_c = first.loc[first.index.isin(F) & first.commodity.notna()]
print('   F&O+commodity users: commodity first', (both_c.commodity < both_c.fno).sum(), '| F&O first', (both_c.commodity >= both_c.fno).sum())
both_s = first.loc[first.index.isin(F) & first.stocks.notna()]
print('   F&O+stocks users: stocks first', (both_s.stocks < both_s.fno).sum(), '| F&O first', (both_s.stocks >= both_s.fno).sum())

# ---------- (2) natural experiment: F&O stoppers
last_f = fno.groupby('third_party_id').d.max()
first_f = fno.groupby('third_party_id').d.min()
n_f = fno.groupby('third_party_id').size()
GAP = 60
stop = last_f[(last_f <= END - pd.Timedelta(days=GAP))].index  # >=60 days with no F&O to 31 Oct
stop = [u for u in stop if n_f[u] >= 5]  # were real F&O traders (>=5 executed orders)
cont = [u for u in F if last_f[u] > END - pd.Timedelta(days=GAP) and n_f[u] >= 5 and first_f[u] <= END - pd.Timedelta(days=GAP)]
print(f'\n(2) F&O stoppers (>=5 executed F&O orders, no F&O in last {GAP}+ days to 31 Oct): {len(stop)}; continuers (same min orders, started F&O >= {GAP}d before end): {len(cont)}')
rows = []
for u in stop:
    x = r[r.third_party_id == u]; L = last_f[u]
    after = x[(x.d > L)]
    before = x[(x.d <= L) & (x.d > L - pd.Timedelta(days=60))]
    rows.append(dict(u=u, last=L, fno_rev_before60=before[before.instr == 'fno'].rev.sum(),
                     stk_before60=before[before.instr == 'stocks'].rev.sum(), com_before60=before[before.instr == 'commodity'].rev.sum(),
                     stk_after=after[after.instr == 'stocks'].rev.sum(), com_after=after[after.instr == 'commodity'].rev.sum(),
                     mf_ipo_after=after[after.instr.isin(['mf', 'ipo'])].rev.sum(),
                     days_after=(END - L).days,
                     used_stk_before=(x[(x.d <= L)].instr == 'stocks').any(), used_com_before=(x[(x.d <= L)].instr == 'commodity').any()))
S = pd.DataFrame(rows)
S['any_after'] = (S.stk_after + S.com_after + S.mf_ipo_after) > 0
print('   any revenue after stopping F&O:', S.any_after.sum(), 'of', len(S))
print('   stocks after:', (S.stk_after > 0).sum(), 'users, ₹', round(S.stk_after.sum()),
      '| commodity after:', (S.com_after > 0).sum(), 'users, ₹', round(S.com_after.sum()),
      '| MF/IPO only after:', ((S.mf_ipo_after > 0) & (S.stk_after == 0) & (S.com_after == 0)).sum())
print('   of stoppers: used stocks before stop', S.used_stk_before.sum(), '| used commodity before stop', S.used_com_before.sum())
print('   NEW to stocks after stop (never before):', ((S.stk_after > 0) & ~S.used_stk_before).sum(),
      '| NEW to commodity after stop:', ((S.com_after > 0) & ~S.used_com_before).sum())
print('   F&O revenue in their last 60d before stop ₹', round(S.fno_rev_before60.sum()),
      '-> replaced after stop by stocks+commodity ₹', round(S.stk_after.sum() + S.com_after.sum()),
      f'(over median {S.days_after.median():.0f} days after)')
# monthly-rate comparison: before (last 60d, all non-F&O) vs after, per 30 days
S['nonfno_before_30'] = (S.stk_before60 + S.com_before60) / 2
S['nonfno_after_30'] = (S.stk_after + S.com_after) / S.days_after * 30
print('   non-F&O revenue per 30 days, stoppers: before', round(S.nonfno_before_30.sum()), 'after', round(S.nonfno_after_30.sum()))
print('   per 30d stocks before/after', round((S.stk_before60/2).sum()), round((S.stk_after/S.days_after*30).sum()),
      '| commodity before/after', round((S.com_before60/2).sum()), round((S.com_after/S.days_after*30).sum()))
S.to_csv(W + 'q4_fno_stoppers.csv', index=False)

# ---------- (3) economics per order and per active trading day, F&O traders only
print('\n(3) Revenue per order / per active day (F&O traders)')
for ins, sub in [('fno', rf[rf.instr == 'fno']), ('commodity', rf[rf.instr == 'commodity']),
                 ('stocks MIS', stk[stk['product'] == 'MIS']), ('stocks CNC', stk[stk['product'] == 'CNC']), ('stocks MTF', stk[stk['product'] == 'MTF'])]:
    days = sub.groupby('third_party_id').d.nunique().sum()
    print(f'   {ins:11s} orders {len(sub):6d}  ₹/order {sub.rev.mean():5.1f}  active user-days {days:5d}  ₹/active day {sub.rev.sum()/days:6.1f}')

# ---------- (4) exposure: expiry-day trading (one weekly expiry per exchange etc.)
f_raw = pd.read_csv('data/fno_orders.csv', low_memory=False, usecols=['third_party_id', 'order_status', 'order_created_at', 'contracts_expiry_date'])
f_raw = f_raw[f_raw.order_status == 'EXECUTED']
f_raw['exp_day'] = pd.to_datetime(f_raw.order_created_at, format='ISO8601').dt.date == pd.to_datetime(f_raw.contracts_expiry_date, format='ISO8601').dt.date
share = f_raw.groupby('third_party_id').exp_day.mean()
print('\n(4) executed F&O orders on expiry day:', f'{f_raw.exp_day.mean()*100:.1f}%')
heavy = share[share >= 0.5].index
print('   F&O traders with >=50% of orders on expiry day:', len(heavy), 'share of F&O revenue', f"{fno[fno.third_party_id.isin(heavy)].rev.sum()/fno.rev.sum()*100:.1f}%")
