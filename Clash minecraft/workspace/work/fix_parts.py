"""대포 카트: 앞/뒤 바퀴를 각자 본으로 나눠서 제자리에서 굴러가게 (원래는 한 본이라 바퀴가 같이 공전).
엘릭서 정제소: 밸브 바퀴 본의 회전 중심을 바퀴 가운데로 옮기고 계속 한 방향으로 돌게."""
import json, sys, uuid, copy
sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import kf
D = sys.argv[1]
def find(t, n, par=None):
    for c in t:
        if isinstance(c, dict):
            if c['name'] == n: return c, par
            r = find(c['children'], n, c)
            if r: return r
p = D + '/clash_cannon_cart.bbmodel'; d = json.load(open(p)); em = {e['uuid']: e for e in d['elements']}
if not find(d['outliner'], 'wheel_rf'):
    new_bones = {}
    for side in ('r', 'l'):
        g, par = find(d['outliner'], 'wheel_' + side)
        keep = []
        subs = {}
        for c in g['children']:
            if isinstance(c, str):
                e = em[c]; zc = (e['from'][2] + e['to'][2]) / 2
                if abs(e['to'][2] - e['from'][2]) > 10: keep.append(c); continue      # 축은 그대로
                key = 'f' if zc < 0 else 'b'
                subs.setdefault(key, []).append(c)
            else:
                keep.append(c)
        for key, ids in subs.items():
            z = -6.0 if key == 'f' else 6.0
            ng = copy.deepcopy({k: v for k, v in g.items() if k != 'children'})
            ng['uuid'] = str(uuid.uuid4()); ng['name'] = 'wheel_%s%s' % (side, key); ng['origin'] = [g['origin'][0], 3.2, z]; ng['children'] = ids
            keep.append(ng); new_bones[ng['name']] = ng['uuid']
        g['children'] = keep
        g['wheel_old'] = True
    for a in d['animations']:
        for side in ('r', 'l'):
            old = [u for u, x in a['animators'].items() if x['name'] == 'wheel_' + side]
            for u in old:
                an = a['animators'].pop(u)
                for key in ('f', 'b'):
                    nm = 'wheel_%s%s' % (side, key)
                    if nm in new_bones:
                        c = copy.deepcopy(an); c['name'] = nm
                        for k in c['keyframes']: k['uuid'] = str(uuid.uuid4())
                        a['animators'][new_bones[nm]] = c
    for g in [find(d['outliner'], 'wheel_r')[0], find(d['outliner'], 'wheel_l')[0]]:
        g.pop('wheel_old', None)
    json.dump(d, open(p, 'w')); print('cannon cart wheels split', list(new_bones))
p = D + '/clash_elixir_collector.bbmodel'; d = json.load(open(p))
g, _ = find(d['outliner'], 'lever')
g['origin'] = [17.2, 12.6, 0.0]
for a in d['animations']:
    for u, x in list(a['animators'].items()):
        if x['name'] == 'lever':
            L = a['length']
            if a['name'] in ('idle', 'walk'):
                x['keyframes'] = [kf(0, [0, 0, 0]), kf(L / 3, [-120, 0, 0]), kf(2 * L / 3, [-240, 0, 0]), kf(L, [-360, 0, 0])]
            else:
                a['animators'].pop(u)
json.dump(d, open(p, 'w')); print('collector valve fixed')
