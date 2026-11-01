"""bbmodel 을 X/Z 방향으로만 늘리기 (발 밑 원점 기준). 큐브·본 원점·위치 키프레임"""
import json, sys
src, kx, kz = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
d = json.load(open(src, encoding='utf-8'))
f = lambda v: [v[0] * kx, v[1], v[2] * kz]
for e in d['elements']:
    e['from'], e['to'] = f(e['from']), f(e['to'])
    if 'origin' in e: e['origin'] = f(e['origin'])
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
                    for ax, kk in (('x', kx), ('z', kz)):
                        try: dp[ax] = '%g' % (float(dp[ax]) * kk)
                        except (ValueError, TypeError): pass
json.dump(d, open(src, 'w', encoding='utf-8'), ensure_ascii=False)
