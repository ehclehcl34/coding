"""프린세스 타워 (3.7.0): 타워 몸체 clash_princess_tower (3.4.2 원본 타워) + 꼭대기 프린세스 clash_princess_top (새 프린세스 1.5배).
프린세스는 따로 띄워서 공격할 때 적 쪽으로 몸을 돌림 (타워는 그대로)."""
import json, copy, uuid
T = json.load(open('pkg342/ClashMC_v3.4.2/models/base/clash_princess.bbmodel'))
T['name'] = 'clash_princess_tower'
for t in T['textures']:
    t['name'] = 'clash_princess_tower.png'
json.dump(T, open('newmodels3/clash_princess_tower.bbmodel', 'w'))
P = json.load(open('newmodels3/clash_princess.bbmodel'))
S = 1.15
f = lambda v: [x * S for x in v]
P['elements'] = [e for e in P['elements'] if e['name'] != 'hitbox']
for e in P['elements']:
    e['from'], e['to'] = f(e['from']), f(e['to'])
    if 'origin' in e: e['origin'] = f(e['origin'])
    if 'inflate' in e: e['inflate'] *= S
keep = {e['uuid'] for e in P['elements']}
def walk(g):
    g['origin'] = f(g['origin'])
    g['children'] = [c for c in g['children'] if isinstance(c, dict) or c in keep]
    for c in g['children']:
        if isinstance(c, dict): walk(c)
P['outliner'] = [o for o in P['outliner'] if isinstance(o, dict) and o['name'] == 'root']
walk(P['outliner'][0])
anims = []
for a in P['animations']:
    if a['name'] in ('idle', 'attack', 'hit'):
        for an in a.get('animators', {}).values():
            for k in an.get('keyframes', []):
                if k['channel'] == 'position':
                    for dp in k['data_points']:
                        for c in 'xyz':
                            try: dp[c] = '%g' % (float(dp[c]) * S)
                            except: pass
        anims.append(a)
P['animations'] = anims
P['name'] = 'clash_princess_top'
for t in P['textures']:
    t['name'] = 'clash_princess_top.png'
json.dump(P, open('newmodels3/clash_princess_top.bbmodel', 'w'))
print('tower + top', len(P['elements']))
