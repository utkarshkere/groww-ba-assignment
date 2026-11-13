"""90-day trading revenue Pareto for the cohort (signup <= 2 Aug 2026); reproduce HV numbers; export curve points."""
import pandas as pd, numpy as np, json
r = pd.read_pickle('analysis/rev_orders.pkl')
u = pd.read_csv('data/users.csv', usecols=['third_party_id', 'signup_ts'])
u['signup_ts'] = pd.to_datetime(u.signup_ts, format='ISO8601')
coh = u[u.signup_ts < pd.Timestamp('2026-08-03')]
print('cohort', len(coh))
t = r[r.instr.isin(['fno', 'stocks', 'commodity'])].merge(coh, on='third_party_id')
t['d'] = (t.ts - t.signup_ts).dt.total_seconds() / 86400
t = t[(t.d >= 0) & (t.d < 90)]
pu = t.groupby('third_party_id').rev.sum().reindex(coh.third_party_id, fill_value=0).sort_values(ascending=False)
T = pu.sum(); N = len(pu)
print('D90 trading revenue', round(T), 'users with >0', (pu > 0).sum())
top127 = pu.iloc[:127]; bar = top127.min()
print('top 1% =127 users share', round(top127.sum() / T * 100, 1), 'bar', round(bar, 1))
m3 = t[(t.d >= 60) & (t.rev > 0)].third_party_id.unique()
hv = top127[top127.index.isin(m3)]
print('HV', len(hv), 'share', round(hv.sum() / T * 100, 1), '| lapsed', 127 - len(hv), round((top127.sum() - hv.sum()) / T * 100, 1))
cs = pu.cumsum() / T
# marks
for mk in [0.5, 0.8, 0.9, 0.95, 0.99]:
    k = int((cs < mk).sum()) + 1
    print(f'{int(mk*100)}% mark: {k} users = {k/N*100:.2f}% of signups, smallest {pu.iloc[k-1]:.1f}')
# curve points: x = % of signups (top-ranked first), y = % revenue; sample densely in first 5%
xs = sorted(set([0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 13.1, 15, 20, 100]))
pts = []
for x in xs:
    k = max(1, int(round(N * x / 100)))
    pts.append([x, round(float(cs.iloc[k - 1]) * 100, 1)])
print(json.dumps(pts))
print('share of signups with any D90 trading revenue', round((pu > 0).mean() * 100, 1))
