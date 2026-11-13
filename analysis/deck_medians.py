"""Item 5: medians vs means for HV / lapsed / other revenue users, first 90 days."""
import pandas as pd
r = pd.read_pickle('analysis/rev_orders.pkl')
u = pd.read_csv('data/users.csv', usecols=['third_party_id', 'signup_ts'])
u['signup_ts'] = pd.to_datetime(u.signup_ts, format='ISO8601')
coh = u[u.signup_ts < pd.Timestamp('2026-08-03')].set_index('third_party_id')
t = r[r.rev > 0].merge(coh.reset_index(), on='third_party_id')
t['d'] = (t.ts - t.signup_ts).dt.total_seconds() / 86400
w = t[(t.d >= 0) & (t.d < 90)]
rev90 = w.groupby('third_party_id').rev.sum().reindex(coh.index, fill_value=0).sort_values(ascending=False)
top = rev90.iloc[:127]
m3 = set(w[w.d >= 60].third_party_id)
HV = [x for x in top.index if x in m3]
LP = [x for x in top.index if x not in m3]
OT = [x for x in rev90.index if rev90[x] > 0 and x not in set(top.index)]
tr = w[w.instr.isin(['fno', 'stocks', 'commodity'])]
orders_all = w.groupby('third_party_id').size()
orders_tr = tr.groupby('third_party_id').size()
days_tr = tr.assign(day=tr.ts.dt.normalize()).groupby('third_party_id').day.nunique()
prods = w.groupby('third_party_id').instr.nunique()
for name, g in [('HV', HV), ('Lapsed', LP), ('Other', OT)]:
    def mm(sr):
        x = sr.reindex(g, fill_value=0)
        return f'mean {x.mean():.1f} median {x.median():.1f}'
    print(f'{name} n={len(g)} | revenue orders (all products) {mm(orders_all)} | trading orders {mm(orders_tr)} | trading days {mm(days_tr)} | products {mm(prods)} | rev/month mean {rev90.reindex(g).mean()/3:.0f} median {rev90.reindex(g).median()/3:.0f}')
print('HV monthly revenue total', round(rev90.reindex(HV).sum() / 3))
