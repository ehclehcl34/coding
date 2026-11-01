"""clash_wall_breaker = the original HQ clash_skeletons model (sword removed, both arms raised) + the generated keg
('bomb' group with 'spark') and team bandana ('tc_bandana') grafted on from newmodels3/clash_wall_breaker.bbmodel."""
import json, copy, uuid
base = json.load(open('pkg360/ClashMC_v3.6.0/models/base/clash_skeletons.bbmodel'))
gen = json.load(open('newmodels3/clash_wall_breaker.bbmodel'))
out = copy.deepcopy(base); out['name'] = 'clash_wall_breaker'
def find(o, name, parent=None):
    for c in o:
        if isinstance(c, dict):
            if c['name'] == name: return c, parent
            r = find(c.get('children', []), name, c)
            if r: return r
def elem_ids(g):
    ids = []
    for c in g['children']:
        if isinstance(c, str): ids.append(c)
        else: ids += elem_ids(c)
    return ids
# 1) drop the sword
sw, sp = find(out['outliner'], 'sword')
gone = set(elem_ids(sw)); sp['children'].remove(sw)
out['elements'] = [e for e in out['elements'] if e['uuid'] not in gone]
# 2) arms raised straight up (rest rotation on the arm groups)
for side, z in (('arm_r', -8), ('arm_l', 8)):
    g, _ = find(out['outliner'], side)
    g['rotation'] = [180, 0, z]
# 3) graft keg + bandana from the generated model (with its texture)
ti = len(out['textures']); tex = copy.deepcopy(gen['textures'][0]); tex['uuid'] = str(uuid.uuid4()); tex['id'] = str(ti); tex['name'] = 'wall_breaker_parts.png'
out['textures'].append(tex)
emap = {e['uuid']: e for e in gen['elements']}
def graft(name, parent_name, k, off):
    T = lambda v: [v[0] * k + off[0], v[1] * k + off[1], v[2] * k + off[2]]
    g, _ = find(gen['outliner'], name)
    def cp(grp):
        ng = copy.deepcopy({kk: vv for kk, vv in grp.items() if kk != 'children'}); ng['uuid'] = str(uuid.uuid4())
        ng['origin'] = T(grp['origin']); ng['children'] = []
        for c in grp['children']:
            if isinstance(c, str):
                e = copy.deepcopy(emap[c]); e['uuid'] = str(uuid.uuid4())
                e['from'], e['to'] = T(e['from']), T(e['to'])
                if 'origin' in e: e['origin'] = T(e['origin'])
                e['inflate'] = e.get('inflate', 0) * k
                for f in e['faces'].values():
                    if f.get('texture') is not None: f['texture'] = ti
                out['elements'].append(e); ng['children'].append(e['uuid'])
            else:
                ng['children'].append(cp(c))
        return ng
    par, _ = find(out['outliner'], parent_name) if parent_name else (None, None)
    (par['children'] if par else out['outliner']).append(cp(g))
graft('bomb', None, 0.75, (0, 7.7, 0)) if False else None
root, _ = find(out['outliner'], 'root')
T0 = None
graft('bomb', 'root', 0.95, (0, 3.4, 0))
graft('tc_bandana', 'head', 0.96, (0, 3.9, -0.2))
json.dump(out, open('newmodels3/clash_wall_breaker.bbmodel', 'w'))
print('wall breaker built:', len(out['elements']), 'cubes')
