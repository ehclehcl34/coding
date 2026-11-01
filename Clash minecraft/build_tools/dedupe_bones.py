"""본(그룹) 이름이 겹치면 BetterModel 이 큐브를 엉뚱한 본에 붙임 → 뒤에 나온 같은 이름 본에 _b, _c ... 붙여서 구분"""
import json, sys
for p in sys.argv[1:]:
    d = json.load(open(p)); seen = set(); n = 0
    def walk(o):
        global n
        for x in o:
            if isinstance(x, dict):
                nm = x['name']
                if nm in seen:
                    k = 0
                    while '%s_%s' % (nm, 'bcdefghij'[k]) in seen: k += 1
                    x['name'] = '%s_%s' % (nm, 'bcdefghij'[k]); n += 1
                seen.add(x['name'])
                walk(x.get('children', []))
    walk(d['outliner'])
    if n:
        json.dump(d, open(p, 'w')); print(p.split('/')[-1], 'renamed', n)
