"""긴 무기(프린스 랜스 등): 본 원점에서 멀리 떨어진 큐브를 큐브 가운데를 원점으로 하는 자식 본으로 옮겨 BetterModel 에서 떨어져 보이지 않게.
usage: fix_split.py model.bbmodel threshold_px bone1,bone2"""
import json, sys, uuid
p, TH, names = sys.argv[1], float(sys.argv[2]), set(sys.argv[3].split(','))
d = json.load(open(p)); em = {e['uuid']: e for e in d['elements']}; n = [0]
def walk(ns):
    for g in ns:
        if not isinstance(g, dict): continue
        walk(g.get('children', []))
        if g['name'] not in names: continue
        o = g['origin']; out = []
        for c in g['children']:
            if isinstance(c, str):
                e = em[c]
                if max(max(abs(e['from'][i] - o[i]), abs(e['to'][i] - o[i])) for i in range(3)) > TH:
                    n[0] += 1
                    out.append({'name': '%s_p%d' % (g['name'], n[0]), 'origin': [(e['from'][i] + e['to'][i]) / 2 for i in range(3)], 'color': 0,
                                'uuid': str(uuid.uuid4()), 'export': True, 'mirror_uv': False, 'isOpen': False, 'locked': False, 'visibility': True,
                                'autouv': 0, 'rotation': [0, 0, 0], 'children': [c]})
                    continue
            out.append(c)
        g['children'] = out
walk(d['outliner'])
json.dump(d, open(p, 'w'))
print(p.split('/')[-1], 'split', n[0])
