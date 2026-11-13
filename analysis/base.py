"""Rebuild revenue base (agreed rules) -> work/rev_orders.parquet; print totals vs handoff."""
import pandas as pd, numpy as np
D = 'data/'
W = 'analysis/'

# Stocks: SUCCESS only; blank brokerage on SUCCESS -> impute with pricing rule; recorded 0 kept
s = pd.read_csv(D + 'stocks_orders.csv', low_memory=False)
s = s[s.order_status == 'SUCCESS'].copy()
t = s.turnover_inr.astype(float)
rule = np.where(s['product'] == 'MTF', 0.001 * t,
                np.minimum(np.minimum(20, np.maximum(5, 0.001 * t)), 0.025 * t))
s['imputed'] = s.original_brokerage.isna()
s['rev'] = np.where(s.imputed, rule, s.original_brokerage)
s['ts'] = pd.to_datetime(s.created_at, format='ISO8601')
s['instr'] = 'stocks'
stk = s[['third_party_id', 'ts', 'rev', 'instr', 'product', 'imputed', 'turnover_inr']]

f = pd.read_csv(D + 'fno_orders.csv', low_memory=False)
f = f[f.order_status == 'EXECUTED']
fno = pd.DataFrame({'third_party_id': f.third_party_id, 'ts': pd.to_datetime(f.order_created_at, format='ISO8601'),
                    'rev': f.brokerage_inr.astype(float), 'instr': 'fno', 'product': f['product']})

c = pd.read_csv(D + 'commodity_orders.csv', low_memory=False)
c = c[c.order_status == 'EXECUTED']
com = pd.DataFrame({'third_party_id': c.third_party_id, 'ts': pd.to_datetime(c.created_at, format='ISO8601'),
                    'rev': c.brokerage_inr.astype(float), 'instr': 'commodity'})

m = pd.read_csv(D + 'mf_orders.csv', low_memory=False)
m = m[m.order_status == 'COMPLETED']
mf = pd.DataFrame({'third_party_id': m.third_party_id, 'ts': pd.to_datetime(m.created_at, format='ISO8601'),
                   'rev': m.brokerage_inr.astype(float), 'instr': 'mf'})

i = pd.read_csv(D + 'ipo_orders.csv', low_memory=False)
i = i[i.brokerage_inr > 0]
ipo = pd.DataFrame({'third_party_id': i.third_party_id, 'ts': pd.to_datetime(i.created_at, format='ISO8601'),
                    'rev': i.brokerage_inr.astype(float), 'instr': 'ipo'})

r = pd.concat([stk, fno, com, mf, ipo], ignore_index=True)
r.to_pickle(W + 'rev_orders.pkl')

g = r.groupby('instr').agg(rev=('rev', 'sum'), users=('third_party_id', lambda x: x[r.loc[x.index, 'rev'] > 0].nunique()))
g['share'] = g.rev / g.rev.sum() * 100
print(g.round(1))
print('TOTAL', round(r.rev.sum()), 'revenue users', r[r.rev > 0].third_party_id.nunique())
print('stocks raw (recorded only)', round(s.original_brokerage.fillna(0).sum()), 'blank SUCCESS', s.imputed.sum())
