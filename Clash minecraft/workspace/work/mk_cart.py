import sys, json, uuid, copy
sys.path.insert(0, 'pkg340/ClashMC_v3.4.0/source/model_tools')
from bbgen2 import Model
def cb(b, x, y, z, w, h, d, mat, **kw):
    return b.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)
BROKEN = len(sys.argv) > 1 and sys.argv[1] == 'broken'
NAME = 'clash_cannon_cart_broken' if BROKEN else 'clash_cannon_cart'
m = Model(NAME, density=1.0); m.round = False
m.mats_({'wood': ('#a86a3a', 'wood', {'planks': True}), 'wood_d': ('#7a4a26', 'wood'), 'steel': ('#9aa2aa', 'metal'), 'plate': ('#8a9096', 'metal')})
root = m.bone('root', [0, 0, 0])
def bed(parent, y0, tilt=None):
    ro = dict(rot=tilt, rot_origin=[0, y0, 0]) if tilt else {}
    cb(parent, 0, y0 + 0.4, 0, 13.0, 3.4, 20.0, 'wood', decals={f: [('rect', 0, 0.5, 1, 0.54, '#7a4a26')] for f in ('east', 'west', 'north', 'south')}, **ro)
    cb(parent, 0, y0 + 3.8, 0, 10.0, 1.0, 12.0, 'plate', **ro)
    for sz in (1, -1):
        cb(parent, 0, y0, sz * 10.6, 15.0, 3.0, 1.6, 'wood_d', **ro)
        for sx in (1, -1):
            cb(parent, sx * 5.4, y0 + 3.0, sz * 9.0, 1.4, 0.8, 1.4, 'steel', **ro)
        cb(parent, 0, y0 + 1.0, sz * 12.2, 6.0, 0.8, 0.8, 'steel', **ro)
        for dx in (-2.6, 2.6):
            cb(parent, dx, y0 + 1.0, sz * 11.6, 0.8, 0.8, 1.6, 'steel', **ro)
def wheel(parent, x, y, z, sx, rot2=None):
    for rot in (None, ('x', 45)):
        cb(parent, x, y - 2.8, z, 1.8, 5.6, 2.3, 'wood', rot=rot, rot_origin=[x, y, z])
        cb(parent, x, y - 1.15, z, 1.8, 2.3, 5.6, 'wood', rot=rot, rot_origin=[x, y, z])
    cb(parent, x + sx * 1.1, y - 0.8, z, 0.6, 1.6, 1.6, 'steel')
if not BROKEN:
    cart = m.bone('cart', [0, 4, 0], root)
    bed(cart, 4.0)
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wheel_' + side, [sx * 7.2, 3.2, 0], root)
        for sz in (1, -1):
            wheel(w, sx * 7.2, 3.2, sz * 6.0, sx)
        cb(w, sx * 6.6, 2.8, 0, 1.0, 0.8, 13.0, 'steel')
    PLATE = 8.8
    m.bone('barrel', [0, 12, 0], cart)
else:
    base = m.bone('base', [0, 0, 0], root)
    bc = m.bone('base_cart', [0, 0, 0], base)
    bed(bc, 1.0)                                                                       # bed dropped onto the ground
    cb(bc, 4.0, 0.0, 9.0, 4.0, 1.4, 2.0, 'wood_d', rot=('y', 22.5))                     # splinters
    cb(bc, -6.0, 0.0, -9.6, 3.0, 1.0, 1.6, 'wood', rot=('y', -22.5))
    bw = m.bone('base_wheels', [0, 0, 0], base)
    wheel(bw, 8.6, 1.0, -7.0, 1)                                                       # wheels knocked off, lying flat-ish
    cb(bw, -9.0, 0, 6.5, 1.8, 2.6, 5.4, 'wood', rot=('z', 22.5), rot_origin=[-9.0, 1.3, 6.5])
    cb(bw, -6.6, 0, 3.0, 1.0, 0.8, 9.0, 'steel', rot=('y', 22.5))                       # bent axle
    PLATE = 5.8
    m.bone('top', [0, 8, 0], root)
m.hitbox(1.4, 2.1)
L = 0.6
if not BROKEN:
    spin = {k: {'rotation': [(0, [0, 0, 0]), (L / 2, [-180, 0, 0]), (L, [-360, 0, 0])]} for k in ('wheel_r', 'wheel_l')}
    m.anim('idle', 2.0, 'loop', {'barrel': {'rotation': [(0, [0, 0, 0]), (1.0, [-2, 0, 0]), (2.0, [0, 0, 0])]}})
    m.anim('walk', L, 'loop', dict(spin, cart={'position': [(0, [0, 0, 0]), (0.3, [0, 0.3, 0]), (0.6, [0, 0, 0])]}), interp='linear')
    m.anim('attack', 0.5, 'once', {'barrel': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 2.5]), (0.5, [0, 0, 0])]},
                                   'cart': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.0]), (0.5, [0, 0, 0])]}})
    m.anim('spawn', 0.5, 'once', {'root': {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])], 'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', {'cart': {'position': [(0, [0, 0, 0]), (0.1, [0, 0, 1.2]), (0.3, [0, 0, 0])]}})
else:
    m.anim('idle', 2.0, 'loop', {'top': {'rotation': [(0, [0, 0, 0]), (1.0, [-2, 0, 0]), (2.0, [0, 0, 0])]}})
    m.anim('attack', 0.5, 'once', {'top': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 2.5]), (0.5, [0, 0, 0])]}})
    m.anim('deploy', 0.5, 'once', {'base_wheels': {'position': [(0, [0, 4, 0]), (0.3, [0, 0, 0])]}, 'top': {'position': [(0, [0, 3, 0]), (0.25, [0, -0.8, 0]), (0.5, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'base': {'position': [(0, [0, 0, 0]), (0.1, [0.6, 0, 0]), (0.3, [0, 0, 0])]}})
m.anim('death', 0.9, 'hold', {'root': {'scale': [(0, [1, 1, 1]), (0.6, [1.05, 0.6, 1.05]), (0.9, [1.1, 0.05, 1.1])]}})
m.sculpt(); m.fit(48)
out = 'newmodels3/%s.bbmodel' % NAME
m.export(out)
# ---- inject the user's cannon barrel (top subtree) + pedestal, turned 90deg so the muzzle faces -Z
src = json.load(open('pkg342/ClashMC_v3.4.2/models/base/clash_cannon.bbmodel')); tgt = json.load(open(out))
ti = len(tgt['textures']); tex = copy.deepcopy(src['textures'][0]); tex['uuid'] = str(uuid.uuid4()); tex['id'] = str(ti); tex['name'] = 'clash_cannon_src.png'
tgt['textures'].append(tex)
S, CUT = 0.6, -99.0
lowest = 11.3
OY = PLATE - lowest * S
T = lambda v: [-v[2] * S, v[1] * S + OY, v[0] * S]                                 # (x,y,z) -> (-z, y, x): -X muzzle -> -Z
FM = {'north': 'east', 'south': 'west', 'east': 'south', 'west': 'north', 'up': 'up', 'down': 'down'}
E = {e['uuid']: e for e in src['elements']}
def find(o, name):
    for c in o:
        if isinstance(c, dict):
            if c['name'] == name: return c
            r = find(c.get('children', []), name)
            if r: return r
def conv(g):
    ng = copy.deepcopy(g); ng['uuid'] = str(uuid.uuid4()); ng['origin'] = T(g['origin'])
    if 'rotation' in g: r = g['rotation']; ng['rotation'] = [-r[2], r[1], r[0]]
    kids = []
    for c in g['children']:
        if isinstance(c, str):
            if E[c]['to'][1] < CUT:                                                    # skip the old wooden legs/yoke
                continue
            e = copy.deepcopy(E[c]); e['uuid'] = str(uuid.uuid4())
            f, t = T(e['from']), T(e['to'])
            e['from'] = [min(f[i], t[i]) for i in range(3)]; e['to'] = [max(f[i], t[i]) for i in range(3)]
            if 'origin' in e: e['origin'] = T(e['origin'])
            if 'rotation' in e: r = e['rotation']; e['rotation'] = [-r[2], r[1], r[0]]
            e['faces'] = {FM[k]: v for k, v in e['faces'].items()}
            for fv in e['faces'].values():
                if fv.get('texture') is not None: fv['texture'] = ti
            tgt['elements'].append(e); kids.append(e['uuid'])
        else:
            kids.append(conv(c))
    ng['children'] = kids
    return ng
dst = find(tgt['outliner'], 'top' if BROKEN else 'barrel')
top = conv(find(src['outliner'], 'top')); top['name'] = 'top_barrel' if BROKEN else 'barrel_top'
dst['children'] += [top]
zs = [e['from'][2] for e in tgt['elements'] if e['uuid'] in json.dumps(top)]
mz = min(zs)
dst['children'].append({'name': 'top_muzzle' if BROKEN else 'muzzle', 'uuid': str(uuid.uuid4()), 'origin': [0, 21.0 * S + OY, mz], 'rotation': [0, 0, 0], 'children': [], 'export': True, 'visibility': True, 'isOpen': False})
for nm in (() if BROKEN else ('shield', 'tc_pennant')):
    dst['children'].append({'name': nm, 'uuid': str(uuid.uuid4()), 'origin': [0, 12, 0], 'rotation': [0, 0, 0], 'children': [], 'export': True, 'visibility': True, 'isOpen': False})
json.dump(tgt, open(out, 'w'))
print('ok', len(tgt['elements']), 'muzzle z', round(mz, 1))
