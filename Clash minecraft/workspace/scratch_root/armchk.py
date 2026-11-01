import sys,json,numpy as np;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools');import bbrender
from bbrender import rot_matrix
d=json.load(open('newmodels3/clash_lumberjack.bbmodel'));par=bbrender.element_parents(d)
P=bbrender.sample(d,'idle',0)
def corners(e):
  f,t=np.array(e['from']),np.array(e['to'])
  pts=[np.array([x,y,z]) for x in (f[0],t[0]) for y in (f[1],t[1]) for z in (f[2],t[2])]
  out=[]
  for p in pts:
    Re=np.array(rot_matrix(*e.get('rotation',[0,0,0]))); p=Re@(p-np.array(e['origin']))+np.array(e['origin'])
    for (bo,br,_,_,bu) in par[e['uuid']]:
      r=list(br or [0,0,0])
      if bu in P: ar=P[bu][0]; r=[r[0]-ar[0],r[1]-ar[1],r[2]+ar[2]]
      if any(r): p=np.array(rot_matrix(*r))@(p-np.array(bo))+np.array(bo)
    out.append(p)
  o=np.array(out); return o.min(0).round(1),o.max(0).round(1)
for e in d['elements']:
  n=par[e['uuid']][0][2]
  if n in ('arm_l','flask'): print(n,*corners(e))
