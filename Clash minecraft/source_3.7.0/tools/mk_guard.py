"""clash_guard = the original HQ clash_skeletons model (sword removed) + bucket helm/plume, kite shield ('shield', hidden
by the plugin when it breaks) and spear grafted from newmodels3/clash_guard_parts.bbmodel; spear-thrust attack."""
import json, copy, uuid, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import kf
base = json.load(open('pkg360/ClashMC_v3.6.0/models/base/clash_skeletons.bbmodel'))
gen = json.load(open('newmodels3/clash_guard_parts.bbmodel'))
out = copy.deepcopy(base); out['name'] = 'clash_guard'
def find(o, name, parent=None):
    for c in o:
        if isinstance(c, dict):
            if c['name'] == name: return c, parent
            r = find(c.get('children', []), name, c)
            if r: return r
def elem_ids(g):
    ids = []
    for c in g['children']:
        ids += [c] if isinstance(c, str) else elem_ids(c)
    return ids
sw, sp = find(out['outliner'], 'sword')
gone = set(elem_ids(sw)); sp['children'].remove(sw)
out['elements'] = [e for e in out['elements'] if e['uuid'] not in gone]
ti = len(out['textures']); tex = copy.deepcopy(gen['textures'][0]); tex['uuid'] = str(uuid.uuid4()); tex['id'] = str(ti); tex['name'] = 'guard_parts.png'
out['textures'].append(tex)
emap = {e['uuid']: e for e in gen['elements']}
def graft(name, parent_name):
    g, _ = find(gen['outliner'], name)
    def cp(grp):
        ng = copy.deepcopy({k: v for k, v in grp.items() if k != 'children'}); ng['uuid'] = str(uuid.uuid4()); ng['children'] = []
        for c in grp['children']:
            if isinstance(c, str):
                e = copy.deepcopy(emap[c]); e['uuid'] = str(uuid.uuid4())
                for f in e['faces'].values():
                    if f.get('texture') is not None: f['texture'] = ti
                out['elements'].append(e); ng['children'].append(e['uuid'])
            else:
                ng['children'].append(cp(c))
        return ng
    par, _ = find(out['outliner'], parent_name)
    par['children'].append(cp(g))
graft('helmet', 'head'); graft('shield', 'arm_r'); graft('spear', 'arm_l')
names = {}
def w(t):
    for c in t:
        if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
w(out['outliner'])
# 창 찌르기: 팔을 뒤로 당겼다가 앞으로, 창끝이 앞을 보도록 창 본을 같이 돌림
for a in out['animations']:
    if a['name'] == 'attack':
        L = a['length']
        a['animators'] = {u: x for u, x in a['animators'].items() if x['name'] not in ('arm_l', 'arm_r', 'sword')}
        a['animators'][names['arm_l']] = {'name': 'arm_l', 'type': 'bone', 'keyframes': [kf(0, [-20, 0, 0]), kf(L * 0.35, [-40, 0, 0]), kf(L * 0.55, [-80, 0, 0]), kf(L * 0.75, [-75, 0, 0]), kf(L, [-20, 0, 0])]}
        a['animators'][names['spear']] = {'name': 'spear', 'type': 'bone', 'keyframes': [kf(0, [0, 0, 0]), kf(L * 0.35, [130, 0, 0]), kf(L * 0.55, [170, 0, 0]), kf(L * 0.75, [170, 0, 0]), kf(L, [0, 0, 0])]}
json.dump(out, open('newmodels3/clash_guard.bbmodel', 'w'))
print('guard built:', len(out['elements']), 'cubes', out['animations'][2]['name'])
