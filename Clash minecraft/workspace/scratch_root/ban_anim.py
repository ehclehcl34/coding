"""bandit: the hood (bone 'ponytail') only sways a little, so it never flips over the face or bares the crown"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
p = 'newmodels3/clash_bandit.bbmodel'; d, n = load(p)
for a in d['animations']:
    for x in a['animators'].values():
        if x['name'] == 'ponytail':
            for k in x['keyframes']:
                if k['channel'] == 'rotation':
                    for c in ('x', 'z'):
                        v = float(k['data_points'][0][c])
                        k['data_points'][0][c] = str(max(-3.0, min(3.0, v)))     # hood barely sways (big swings bared the crown)
json.dump(d, open(p, 'w'))
