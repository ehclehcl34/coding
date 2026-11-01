"""소환 모션(deploy)이 키우는 본은 idle/walk/attack 등에도 크기 1 키프레임을 넣어서, 소환 모션이 중간에 멈춰도 작아진 채로 남지 않게."""
import json, sys, copy, uuid, glob
for p in sys.argv[1:]:
    d = json.load(open(p))
    an = {a['name']: a for a in d.get('animations', [])}
    dep = an.get('deploy')
    if not dep: continue
    sc = {u: x for u, x in dep['animators'].items() if any(k['channel'] == 'scale' for k in x['keyframes'])}
    n = 0
    for a in d['animations']:
        if a['name'] in ('deploy', 'death', 'spawn'): continue
        for u, x in sc.items():
            tgt = a.setdefault('animators', {}).get(u)
            if tgt is None:
                tgt = a['animators'][u] = {k: copy.deepcopy(v) for k, v in x.items() if k != 'keyframes'}
                tgt['keyframes'] = []
            if any(k['channel'] == 'scale' for k in tgt['keyframes']): continue
            k0 = copy.deepcopy([k for k in x['keyframes'] if k['channel'] == 'scale'][0])
            k0['time'] = 0; k0['uuid'] = str(uuid.uuid4()); k0['data_points'] = [{'x': '1', 'y': '1', 'z': '1'}]
            tgt['keyframes'].append(k0); n += 1
    json.dump(d, open(p, 'w'))
    if n: print(p.split('/')[-1], n)
