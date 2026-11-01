import json
o=json.load(open('mk_anims_src.bbmodel')); n=json.load(open('newmodels3/clash_mega_knight.bbmodel'))
names={}
def w(t):
  for c in t:
    if isinstance(c,dict): names[c['name']]=c['uuid']; w(c.get('children',[]))
w(n['outliner'])
for a in o['animations']:
  a['animators']={names[v['name']]:v for v in a['animators'].values() if v['name'] in names}
n['animations']=o['animations']; json.dump(n,open('newmodels3/clash_mega_knight.bbmodel','w'))
