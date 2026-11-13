"""Extra numbers for deck v2: (a) HV per signup week, (b) Q1 definitions + total ₹ in days 90-120, (c) Q4 Part A scenario."""
import pandas as pd, numpy as np
r = pd.read_pickle('analysis/rev_orders.pkl')
u = pd.read_csv('data/users.csv', usecols=['third_party_id', 'signup_ts'])
u['signup_ts'] = pd.to_datetime(u.signup_ts, format='ISO8601')
coh = u[u.signup_ts < pd.Timestamp('2026-08-03')].set_index('third_party_id')
t = r[r.rev > 0].merge(coh.reset_index(), on='third_party_id')
t['d'] = (t.ts - t.signup_ts).dt.total_seconds() / 86400
w = t[(t.d >= 0) & (t.d < 90)]
ids = coh.index
rev90 = w.groupby('third_party_id').rev.sum().reindex(ids, fill_value=0)
T = rev90.sum()
rank = rev90.sort_values(ascending=False)
top = rank.iloc[:127]
act = lambda lo, hi: set(w[(w.d >= lo) & (w.d < hi)].third_party_id)
m1, m2, m3 = act(0, 30), act(30, 60), act(60, 90)
HV = [x for x in top.index if x in m3]

# (a) HV per signup week (Mon-Sun)
wk = (coh.signup_ts.dt.normalize() - pd.to_timedelta(coh.signup_ts.dt.weekday, unit='D'))
hvw = pd.Series(1, index=HV).groupby(wk.reindex(HV)).sum()
weeks = sorted(wk.unique())
print('(a) weeks', len(weeks), 'HV per week:', [int(hvw.get(k, 0)) for k in weeks], 'sum', int(hvw.sum()))

# (b) definitions; next-month window 90<=d<120 for users with signup+120d <= 31 Oct end
END = pd.Timestamp('2026-11-01')  # orders to end of 31 Oct
elig = set(coh[coh.signup_ts + pd.Timedelta(days=120) <= END].index)
nx = t[(t.d >= 90) & (t.d < 120)].groupby('third_party_id').rev.sum()
trading = w[w.instr.isin(['fno', 'stocks', 'commodity'])]
tdays = trading.assign(day=trading.ts.dt.normalize()).groupby('third_party_id').day.nunique().reindex(ids, fill_value=0)
ninstr = trading.groupby('third_party_id').instr.nunique().reindex(ids, fill_value=0)
m3rev = w[(w.d >= 60)].groupby('third_party_id').rev.sum().reindex(ids, fill_value=0)
# F&O gross pnl per ₹1 brokerage in 90 days
f = pd.read_csv('data/fno_orders.csv', low_memory=False, usecols=['third_party_id', 'order_status', 'order_created_at', 'pnl'])
f = f[f.order_status == 'EXECUTED'].merge(coh.reset_index(), on='third_party_id')
f['d'] = (pd.to_datetime(f.order_created_at, format='ISO8601') - f.signup_ts).dt.total_seconds() / 86400
f = f[(f.d >= 0) & (f.d < 90)]
fb = f.groupby('third_party_id').size() * 20
fp = f.groupby('third_party_id').pnl.sum()
ratio = (-fp / fb).reindex(ids)  # loss per ₹1 brokerage
cs = rank.cumsum() / T
par80 = list(rank.index[:int((cs < 0.8).sum()) + 1])
all3 = [x for x in ids if x in m1 and x in m2 and x in m3]
defs = {
    0: HV, 1: list(top.index), 2: par80,
    3: [x for x in ids if rev90[x] >= 1000 and x in m3],
    4: list(m3rev.sort_values(ascending=False).index[:127]),
    5: list(rev90[all3].sort_values(ascending=False).index[:127]),
    6: [x for x in ids if tdays[x] >= 20 and rev90[x] >= 300],
    7: [x for x in ids if ninstr[x] >= 2 and rev90[x] >= 500],
    8: [x for x in HV if not (ratio.get(x) is not None and ratio[x] > 5)],
    9: [x for x in top.index if x in m1], 10: [x for x in top.index if x in m2],
    11: [x for x in top.index if x in m2 and x in m3], 12: [x for x in top.index if x in m1 and x in m2 and x in m3]}
print('(b) eligible users', len(elig))
for k, v in defs.items():
    e = [x for x in v if x in elig]
    nr = nx.reindex(e, fill_value=0)
    print(f'  def {k:2d}: users {len(v):3d}  %rev {rev90[v].sum()/T*100:5.1f}  eligible {len(e):3d}  earning {(nr>0).sum():3d}  median {nr.median():6.0f}  mean {nr.mean():6.0f}  TOTAL d90-120 ₹{nr.sum():,.0f}')
allnx = nx.reindex(list(elig), fill_value=0)
print('  all eligible users: total d90-120 ₹', round(allnx.sum()), 'earning share', round((allnx > 0).mean() * 100, 1))

# (c) Part A scenario: non-F&O stock traders, Apr-Oct
fno_users = set(r[(r.instr == 'fno') & (r.rev > 0)].third_party_id)
s = r[(r.instr == 'stocks') & (r.rev > 0) & (~r.third_party_id.isin(fno_users))]
pu = s.groupby('third_party_id').rev.sum().sort_values(ascending=False)
print('(c) non-F&O stock traders', len(pu), 'rev', round(pu.sum()), '>=500:', (pu >= 500).sum())
below = pu[pu < 500]
k = int(round(len(pu) * 0.10))
nxt = below.iloc[:k]
gain = (500 - nxt).sum()
print(f'   lift the {k} highest users below ₹500 up to ₹500: +₹{gain:,.0f} = {gain/310000*100:.1f}% of ₹3.1L gap; their current median ₹{nxt.median():.0f}, range ₹{nxt.min():.0f}–{nxt.max():.0f}')
med500 = pu[pu >= 500].median()
gain2 = (med500 - nxt).sum()
print(f'   lift same {k} to the median of today\'s ₹500+ group (₹{med500:,.0f}): +₹{gain2:,.0f} = {gain2/310000*100:.1f}% of gap')

# variants for def 6 / 7 using all products
tdays_all = w.assign(day=w.ts.dt.normalize()).groupby('third_party_id').day.nunique().reindex(ids, fill_value=0)
ninstr_all = w.groupby('third_party_id').instr.nunique().reindex(ids, fill_value=0)
for lab, v in [('6 all-product days', [x for x in ids if tdays_all[x] >= 20 and rev90[x] >= 300]),
               ('7 all-product instruments', [x for x in ids if ninstr_all[x] >= 2 and rev90[x] >= 500])]:
    e = [x for x in v if x in elig]; nr = nx.reindex(e, fill_value=0)
    print(f'  def {lab}: users {len(v)} %rev {rev90[v].sum()/T*100:.1f} eligible {len(e)} earning {(nr>0).sum()} median {nr.median():.0f} mean {nr.mean():.0f} TOTAL ₹{nr.sum():,.0f}')
