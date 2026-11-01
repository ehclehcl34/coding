"""hunter: both arms hold the scattergun (archer-like ready pose) in every animation; small recoil on attack"""
import json, uuid
p = 'newmodels3/clash_hunter.bbmodel'; d = json.load(open(p))
names = {}
def w(t):
    for c in t:
        if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
w(d['outliner'])
AL, AR = [-50, 10, 36], [-63, -28, 3]
ALA = [-57, 22, 24]
GD = [20, -45, 0]
kf = lambda t, v: {'channel': 'rotation', 'data_points': [{'x': str(v[0]), 'y': str(v[1]), 'z': str(v[2])}], 'uuid': str(uuid.uuid4()), 'time': t, 'color': -1, 'interpolation': 'linear'}
for a in d['animations']:
    L = a['length']
    if a['name'] == 'attack':
        seq = lambda v: [kf(0, v), kf(0.12, ALA if v is AL else v), kf(0.2, [(ALA if v is AL else v)[0] - 8, (ALA if v is AL else v)[1], (ALA if v is AL else v)[2]]), kf(0.4, ALA if v is AL else v), kf(L, v)]
    else:
        seq = lambda v: [kf(0, v), kf(round(L / 2, 3), [v[0] - 2, v[1], v[2]]), kf(L, v)]
    for nm, v in (('arm_l', AL), ('arm_r', AR)):
        a['animators'][names[nm]] = {'name': nm, 'type': 'bone', 'keyframes': seq(v)}
    if a['name'] == 'attack':                                                     # swing the barrels up level, fire, recoil, lower again
        gk = [kf(0, GD), kf(0.12, [0, -45, 0]), kf(0.2, [-12, -45, 0]), kf(0.4, [0, -45, 0]), kf(L, GD)]
    else:
        gk = [kf(0, GD), kf(L, GD)]
    a['animators'][names['gun']] = {'name': 'gun', 'type': 'bone', 'keyframes': gk}
json.dump(d, open(p, 'w'))
print('hunter arms posed')
