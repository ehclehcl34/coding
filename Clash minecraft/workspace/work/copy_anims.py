"""copy animations from the original pkg360 model onto a regenerated model by bone name: copy_anims.py clash_sparky"""
import json, sys
nm = sys.argv[1]
o = json.load(open('pkg360/ClashMC_v3.6.0/models/base/%s.bbmodel' % nm)); n = json.load(open('newmodels3/%s.bbmodel' % nm))
names = {}
def w(t):
    for c in t:
        if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
w(n['outliner'])
alias = dict(x.split('=') for x in sys.argv[2:])          # newbone=srcbone: duplicate a source bone's tracks
import copy as _c
for a in o['animations']:
    out = {names[v['name']]: v for v in a['animators'].values() if v['name'] in names}
    for new, src in alias.items():
        for v in a['animators'].values():
            if v['name'] == src and new in names:
                nv = _c.deepcopy(v); nv['name'] = new; out[names[new]] = nv
    a['animators'] = out
n['animations'] = o['animations']; json.dump(n, open('newmodels3/%s.bbmodel' % nm, 'w'))
print('copied', [a['name'] for a in n['animations']])
