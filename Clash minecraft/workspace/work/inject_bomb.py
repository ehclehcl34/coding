"""Inject the user's clash_bomb.bbmodel body (5 cubes + its texture) into a generated model's 'bomb' group.
usage: inject_bomb.py <target.bbmodel> <scale> <ox> <oy> <oz>   (bomb-model coords * scale + offset, px)"""
import json, sys, uuid, copy
tgt_p, k, ox, oy, oz = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
gname = sys.argv[6] if len(sys.argv) > 6 else 'bomb'
src = json.load(open('user_bomb.bbmodel')); tgt = json.load(open(tgt_p))
ti = len(tgt['textures']); tex = copy.deepcopy(src['textures'][0]); tex['uuid'] = str(uuid.uuid4()); tex['name'] = 'clash_bomb_src.png'
tex['id'] = str(ti); tgt['textures'].append(tex)
def grp(o, name):
    for c in o:
        if isinstance(c, dict):
            if c['name'] == name: return c
            r = grp(c.get('children', []), name)
            if r: return r
sb = grp(src['outliner'], 'bomb'); body_ids = [c for c in sb['children'] if isinstance(c, str)]
dst = grp(tgt['outliner'], gname)
T = lambda v: [v[0] * k + ox, v[1] * k + oy, v[2] * k + oz]
for e in src['elements']:
    if e['uuid'] not in body_ids: continue
    ne = copy.deepcopy(e); ne['uuid'] = str(uuid.uuid4())
    ne['from'], ne['to'] = T(e['from']), T(e['to'])
    if 'origin' in ne: ne['origin'] = T(e['origin'])
    ne['inflate'] = e.get('inflate', 0) * k
    for f in ne['faces'].values():
        if f.get('texture') is not None: f['texture'] = ti
    tgt['elements'].append(ne); dst['children'].insert(0, ne['uuid'])
json.dump(tgt, open(tgt_p, 'w'))
print('injected', len(body_ids), 'cubes into', tgt_p)
