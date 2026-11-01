"""bbmodel 전체 크기 키우기 (발 밑 원점 기준): 큐브·본 원점·위치 키프레임 ×K"""
import json, sys
src, dst, K = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = json.load(open(src, encoding='utf-8'))
f = lambda v: [x * K for x in v]
for e in d['elements']:
    e['from'], e['to'] = f(e['from']), f(e['to'])
    if 'origin' in e:
        e['origin'] = f(e['origin'])
    if 'inflate' in e:
        e['inflate'] = e['inflate'] * K
def walk(ns):
    for n in ns:
        if isinstance(n, dict):
            n['origin'] = f(n['origin']); walk(n.get('children', []))
walk(d['outliner'])
for a in d.get('animations', []):
    for an in a.get('animators', {}).values():
        for k in an.get('keyframes', []):
            if k['channel'] == 'position':
                for dp in k['data_points']:
                    for ax in 'xyz':
                        try: dp[ax] = '%g' % (float(dp[ax]) * K)
                        except (ValueError, TypeError): pass
# 본 원점에서 46px 넘게 벗어난 큐브는 큐브 가운데를 원점으로 하는 자식 본으로 옮김 (BetterModel 크기 제한)
import uuid as _u
els0 = {e['uuid']: e for e in d['elements']}
cnt = [0]
def split(ns, org, pname):
    out = []
    for n in ns:
        if isinstance(n, dict):
            n['children'] = split(n.get('children', []), n['origin'], n['name']); out.append(n)
        else:
            e = els0[n]
            if max(max(abs(e['from'][i] - org[i]), abs(e['to'][i] - org[i])) for i in range(3)) > 46:
                cnt[0] += 1
                c = [(e['from'][i] + e['to'][i]) / 2 for i in range(3)]
                out.append({'name': '%s_p%d' % (pname, cnt[0]), 'origin': c, 'color': 0, 'uuid': str(_u.uuid4()), 'export': True,
                            'mirror_uv': False, 'isOpen': False, 'locked': False, 'visibility': True, 'autouv': 0, 'rotation': [0, 0, 0], 'children': [n]})
            else:
                out.append(n)
    return out
d['outliner'] = split(d['outliner'], [0, 0, 0], 'root')
print('split', cnt[0])
json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
# check bone limit
els = {e['uuid']: e for e in d['elements']}; worst = [0]
def chk(ns, org):
    for n in ns:
        if isinstance(n, dict): chk(n.get('children', []), n['origin'])
        else:
            e = els[n]
            for i in range(3): worst[0] = max(worst[0], abs(e['from'][i] - org[i]), abs(e['to'][i] - org[i]))
chk(d['outliner'], [0, 0, 0])
mn = min(e['from'][1] for e in d['elements']); mx = max(e['to'][1] for e in d['elements'])
print('worst', round(worst[0], 1), 'height px', round(mx - mn, 1))
