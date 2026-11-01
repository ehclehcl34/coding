"""magic archer: archer-style bow hold (ready + aim), same values as the archer"""
import json, uuid, re
src = open('models_mc_b.py').read(); BOW_AIM = eval(re.search(r'^BOW_AIM = (.*)$', src, re.M).group(1))
p = 'newmodels3/clash_magic_archer.bbmodel'; d = json.load(open(p))
names = {}
def w(t):
    for c in t:
        if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
w(d['outliner'])
kf = lambda t, v, ch='rotation': {'channel': ch, 'data_points': [{'x': str(v[0]), 'y': str(v[1]), 'z': str(v[2])}], 'uuid': str(uuid.uuid4()), 'time': t, 'color': -1, 'interpolation': 'linear'}
ready = {'arm_l': [-40, 15, 0], 'arm_r': [-72, -40, 10], 'bow': [90, 60, -30]}
al, ar_ = [-90, 25, 0], [-90, -12, 0]
for a in d['animations']:
    L = a['length']
    if a['name'] == 'attack':
        tr = {'arm_l': [kf(0, ready['arm_l']), kf(L * 0.25, al), kf(L * 0.7, al), kf(L, ready['arm_l'])],
              'arm_r': [kf(0, ready['arm_r']), kf(L * 0.25, ar_), kf(L * 0.6, [-90, -18, 0]), kf(L * 0.68, [-86, -6, 0]), kf(L, ready['arm_r'])],
              'bow': [kf(0, ready['bow']), kf(L * 0.25, BOW_AIM), kf(L * 0.7, BOW_AIM), kf(L, ready['bow'])],
              'arrow_tip': [kf(0, [0, 0, 0], 'position'), kf(L * 0.6, [0, 0, 2.5], 'position'), kf(L * 0.62, [0, 0, 0], 'position'),
                            kf(0, [1, 1, 1], 'scale'), kf(L * 0.6, [1, 1, 1], 'scale'), kf(L * 0.62, [0, 0, 0], 'scale'), kf(L * 0.9, [0, 0, 0], 'scale'), kf(L, [1, 1, 1], 'scale')]}
    elif a['name'] in ('idle', 'walk'):
        tr = {k: [kf(0, v), kf(round(L / 2, 3), [v[0] - 2, v[1], v[2]] if k != 'bow' else v), kf(L, v)] for k, v in ready.items()}
    else:
        continue
    for k, ks in tr.items():
        a['animators'][names[k]] = {'name': k, 'type': 'bone', 'keyframes': ks}
json.dump(d, open(p, 'w')); print('magic archer posed')
