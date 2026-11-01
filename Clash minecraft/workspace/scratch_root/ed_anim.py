"""electro dragon: animations from the baby dragon (same bones) + sparks around the mouth only while attacking"""
import sys, json, copy; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
src = json.load(open('newmodels3/clash_baby_dragon.bbmodel'))
p = 'newmodels3/clash_electro_dragon.bbmodel'; d, n = load(p)
anims = []
for a in src['animations']:
    a = copy.deepcopy(a)
    out = {}
    for v in a['animators'].values():
        nm = v['name'] if v['name'] in n else v['name'].replace('ts_', 'x_')
        if nm in n:
            v['name'] = nm; out[n[nm]] = v
    a['animators'] = out
    anims.append(a)
d['animations'] = anims
Z = [0.01, 0.01, 0.01]
for a in d['animations']:
    L = a['length']
    if a['name'] == 'attack':
        setk(d, n, 'attack', 'zap', 'scale', [(0, Z), (L * 0.25, [1, 1, 1]), (L * 0.4, [1.3, 0.8, 1.3]), (L * 0.55, [0.9, 1.3, 0.9]), (L * 0.75, [1, 1, 1]), (L * 0.9, Z), (L, Z)])
    else:
        setk(d, n, a['name'], 'zap', 'scale', [(0, Z), (L, Z)])
json.dump(d, open(p, 'w'))
print([a['name'] for a in d['animations']])
