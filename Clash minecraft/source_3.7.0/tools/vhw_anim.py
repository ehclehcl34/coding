"""valkyrie: faster spin (matches the instant whirl effect); hunter: modest muzzle flash; wizard: hand flames only while attacking"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
p = 'newmodels3/clash_valkyrie.bbmodel'; d, n = load(p)
setk(d, n, 'attack', 'root', 'rotation', [(0, [0, 0, 0]), (0.06, [0, 0, 0]), (0.12, [0, -90, 0]), (0.18, [0, -180, 0]), (0.24, [0, -270, 0]), (0.3, [0, -360, 0]), (0.8, [0, -360, 0])])
for b, v in (('arm_r', [0, 0, 82]), ('axe', [0, 0, -172]), ('arm_l', [0, 0, -70])):
    setk(d, n, 'attack', b, 'rotation', [(0, [0, 0, 0]), (0.06, v), (0.36, v), (0.55, [0, 0, 0])])
json.dump(d, open(p, 'w'))
p = 'newmodels3/clash_hunter.bbmodel'; d, n = load(p)
setk(d, n, 'attack', 'muzzle', 'scale', [(0, [1, 1, 1]), (0.18, [1, 1, 1]), (0.2, [2.0, 2.0, 2.0]), (0.25, [1.4, 1.4, 1.4]), (0.3, [1, 1, 1])])
json.dump(d, open(p, 'w'))
p = 'newmodels3/clash_wizard.bbmodel'; d, n = load(p)
Z = [0.01, 0.01, 0.01]
for a in d['animations']:
    for b in ('flame_r', 'flame_l'):
        if a['name'] == 'attack':
            setk(d, n, 'attack', b, 'scale', [(0, Z), (0.12, [1.2, 1.2, 1.2]), (0.2, [1.4, 1.4, 1.4]), (0.3, [2, 2, 2]), (0.36, [0.8, 0.8, 0.8]), (0.5, Z), (0.6, Z)])
        else:
            setk(d, n, a['name'], b, 'scale', [(0, Z), (a['length'], Z)])
json.dump(d, open(p, 'w'))
print('ok')
