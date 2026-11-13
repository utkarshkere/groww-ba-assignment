import sys; sys.path.insert(0,'agents/qc_scripts')
from d90 import *
D=d90(); globals().update(D)
T=r.sum(); HV=set(hv)
WF=W[W.inst=='fno']; rf=WF.groupby('id').rev.sum().reindex(co.third_party_id,fill_value=0).sort_values(ascending=False,kind='mergesort')
m3f=set(WF[WF.dd>=60].id); m3=set(W[W.dd>=60].id)
for lab,G in [('A top127 by F&O rev + F&O m3',[x for x in rf.index[:127] if x in m3f]),
              ('B F&O rev>=733.8 + F&O m3',[x for x in rf.index if rf[x]>=733.8 and x in m3f]),
              ('C F&O rev>=733.8 + any m3',[x for x in rf.index if rf[x]>=733.8 and x in m3]),
              ('D top127 by F&O + any m3',[x for x in rf.index[:127] if x in m3]),
              ('E HV with F&O in m3',[x for x in hv if x in m3f])]:
    print(lab,len(G),'share of total 90d rev (all-inst)',round(r[G].sum()/T*100,1),'(F&O-only rev)',round(rf[G].sum()/T*100,1),'overlap HV',len(set(G)&HV),'HV dropped',len(HV-set(G)),'HV rev dropped share',round(r[list(HV-set(G))].sum()/r[hv].sum()*100,1))
