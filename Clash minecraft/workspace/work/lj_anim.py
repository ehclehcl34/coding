"""lumberjack: left arm hoists the rage bottle overhead in every animation"""
import json, uuid
p = 'newmodels3/clash_lumberjack.bbmodel'; d = json.load(open(p))
names = {}
def w(t):
    for c in t:
        if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
w(d['outliner'])
U = names['arm_l']
for a in d['animations']:
    L = a['length']
    kf = lambda t, v: {'channel': 'rotation', 'data_points': [{'x': str(v[0]), 'y': str(v[1]), 'z': str(v[2])}], 'uuid': str(uuid.uuid4()), 'time': t, 'color': -1, 'interpolation': 'linear'}
    a['animators'][U] = {'name': 'arm_l', 'type': 'bone', 'keyframes': [kf(0, [0, 0, -150]), kf(round(L / 2, 3), [-3, 0, -147]), kf(L, [0, 0, -150])]}
json.dump(d, open(p, 'w'))
print('arm_l raised in', [a['name'] for a in d['animations']])
