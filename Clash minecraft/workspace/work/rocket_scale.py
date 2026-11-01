"""clash_rocket.bbmodel: 크기 키우기 + 회전 느리게"""
import json, sys, uuid
src, dst, K, SPIN = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
d = json.load(open(src, encoding='utf-8'))
P = [0.0, 8.8, 0.0]                       # 로켓 몸통 가운데 (spin 본) 기준으로 키움
f = lambda v: [P[i] + (v[i] - P[i]) * K for i in range(3)]
for e in d['elements']:
    e['from'], e['to'] = f(e['from']), f(e['to'])
    if 'origin' in e:
        e['origin'] = f(e['origin'])
    e['inflate'] = e.get('inflate', 0) * K
def walk(nodes):
    for n in nodes:
        if isinstance(n, dict):
            n['origin'] = f(n['origin'])
            walk(n.get('children', []))
walk(d['outliner'])
for a in d['animations']:
    L = SPIN
    a['length'] = L
    for an in a['animators'].values():
        kfs = an['keyframes']
        if an['name'] == 'spin':
            new = []
            for t, z in ((0, 0), (L / 4, 90), (L / 2, 180), (3 * L / 4, 270), (L, 360)):
                new.append({'channel': 'rotation', 'data_points': [{'x': '0', 'y': '0', 'z': '%g' % z}], 'uuid': str(uuid.uuid4()),
                            'time': round(t, 4), 'color': -1, 'interpolation': 'linear'})
            an['keyframes'] = new
        elif an['name'] == 'flame':        # 불꽃은 빠르게 깜빡임 유지 (0.25초 주기 반복)
            base = sorted([k for k in kfs if k['channel'] == 'scale'], key=lambda k: k['time'])
            new = []
            n = int(round(L / 0.25))
            for c in range(n):
                for k in base[:-1]:
                    nk = dict(k); nk['uuid'] = str(uuid.uuid4()); nk['time'] = round(c * 0.25 + k['time'] * 0.5, 4)
                    new.append(nk)
            last = dict(base[0]); last['uuid'] = str(uuid.uuid4()); last['time'] = L
            new.append(last)
            an['keyframes'] = new + [k for k in kfs if k['channel'] != 'scale']
        else:
            for k in kfs:
                if k['channel'] == 'position':
                    dp = k['data_points'][0]
                    for ax in 'xyz':
                        dp[ax] = '%g' % (float(dp[ax]) * K)
json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
el = d['elements']
mn = [min(e['from'][i] for e in el) for i in range(3)]; mx = [max(e['to'][i] for e in el) for i in range(3)]
print('size px', [round(mx[i] - mn[i], 1) for i in range(3)], 'y', round(mn[1], 1), round(mx[1], 1))
