"""MC-style (vanilla mob look) models, letter F:
elixir golem / elixir golemite / elixir blob / goblin cage / x-bow / bomb tower.
Units px (16 = 1 block), front = north (-Z), origin = feet centre, 1 texel = 1 px (density 1), no bevels.
usage: python3 models_mc_f.py <model_tools dir> <out dir> [--cmp]"""
import sys, os, json, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
import numpy as np
import bbgen2
from bbgen2 import Model, hexrgb, clamp

# ------------------------------------------------------------------ vanilla-like pixel materials
_orig_paint = bbgen2.paint
_orig_decal = bbgen2.decal


def _nz(r, h, w, amt, levels=5):
    q = r.integers(0, levels, (h, w, 1)) / (levels - 1) * 2 - 1
    return 1.0 + q * amt


def mc_paint(kind, base, w, h, rng, face, opts):
    r = np.random.default_rng(rng.randrange(1 << 30))
    c = hexrgb(base)
    img = np.ones((h, w, 3)) * c
    vert = face not in ('up', 'down')
    edge = opts.get('edge', 0.8)
    if kind == 'px':                       # skin / cloth / generic: per-pixel dither + dark rim
        img *= _nz(r, h, w, opts.get('n', 0.05))
        if opts.get('weave'):
            yy, xx = np.mgrid[0:h, 0:w]
            img[((yy + xx) % 2) == 0] *= 0.95
        if edge < 1:
            bbgen2._border(img, edge)
    elif kind == 'planks':                 # oak/spruce planks (boards 4 px)
        vgrain = opts.get('v', False)
        H, W = (w, h) if vgrain else (h, w)
        t = np.ones((H, W, 1))
        bh = opts.get('bh', 4)
        for b0 in range(0, H, bh):
            t[b0:b0 + bh] *= r.uniform(0.9, 1.07)
            t[b0:b0 + 1] *= 0.68
            off = r.integers(0, 8)
            for x in range(off, W, 9):
                t[b0:b0 + bh, x:x + 1] *= 0.72
        for _ in range(max(1, H * W // 7)):
            y, x = r.integers(0, H), r.integers(0, W)
            t[y, x:x + r.integers(1, 4)] *= r.choice([0.86, 1.1])
        t *= _nz(r, H, W, 0.03)
        if vgrain:
            t = t.transpose(1, 0, 2)
        img *= t
        bbgen2._border(img, opts.get('edge', 0.85))
    elif kind == 'log':                    # bark (vertical) / rings on caps
        if vert:
            for x in range(w):
                img[:, x] *= (0.82 if (x + r.integers(0, 2)) % 3 == 0 else 1.0) * r.uniform(0.94, 1.06)
            img *= _nz(r, h, w, 0.06)
        else:
            inner = hexrgb(opts.get('core', '#b8945f'))
            img[:] = inner
            img *= _nz(r, h, w, 0.04)
            yy, xx = np.mgrid[0:h, 0:w]
            d = np.maximum(abs(xx - (w - 1) / 2), abs(yy - (h - 1) / 2))
            img[(d.astype(int) % 2) == 0] *= 0.88
            bbgen2._border(img, 0.0 + 1)
            img[0, :] = c; img[-1, :] = c; img[:, 0] = c; img[:, -1] = c
    elif kind == 'cobble':
        n = max(2, (w * h) // 7)
        pts = np.stack([r.uniform(0, h, n), r.uniform(0, w, n)], 1)
        yy, xx = np.mgrid[0:h, 0:w]
        dist = (yy[..., None] - pts[:, 0]) ** 2 + (xx[..., None] - pts[:, 1]) ** 2
        lab = dist.argmin(-1)
        f = r.uniform(0.78, 1.15, n)
        img *= f[lab][..., None]
        bd = np.zeros((h, w), bool)
        bd[1:, :] |= lab[1:, :] != lab[:-1, :]
        bd[:, 1:] |= lab[:, 1:] != lab[:, :-1]
        img[bd] *= 0.62
        img *= _nz(r, h, w, 0.04)
    elif kind == 'iron':                   # iron-block: light rim top/left, dark bottom/right
        img *= _nz(r, h, w, opts.get('n', 0.035))
        if h > 2 and w > 2:
            img[0, :] = clamp(img[0, :] * 1.18 + 10)
            img[:, 0] = clamp(img[:, 0] * 1.12 + 6)
            img[-1, :] *= 0.62
            img[:, -1] *= 0.72
        if opts.get('rivets') and w >= 5 and h >= 5:
            for (yy, xx) in ((1, 1), (1, w - 2), (h - 2, 1), (h - 2, w - 2)):
                img[yy, xx] = clamp(c * 0.55)
    elif kind == 'elixir':                 # translucent-looking jelly
        if vert:
            img *= np.linspace(1.12, 0.86, h).reshape(h, 1, 1)
        img *= _nz(r, h, w, 0.045)
        for _ in range(max(1, (w * h) // 22)):
            y, x = r.integers(0, h), r.integers(0, w)
            img[y, x] = clamp(img[y, x] * 1.22 + 28)       # bubbles
        for _ in range(max(1, (w * h) // 40)):
            y, x = r.integers(0, h), r.integers(0, w)
            img[y, x] *= 0.8
        bbgen2._border(img, 0.74)
        if vert and h >= 5 and w >= 5:                     # glossy streak (top-left)
            img[1:min(h - 1, 1 + h // 3), 1] = clamp(c * 1.45 + 40)
            img[1, 1:min(w - 1, 1 + w // 4)] = clamp(c * 1.45 + 40)
    elif kind == 'glowpx':
        img *= _nz(r, h, w, 0.03)
        img = clamp(img + 20)
    else:
        return _orig_paint(kind, base, w, h, rng, face, opts)
    if face == 'down':
        img *= 0.72
    elif face == 'up' and kind not in ('glowpx',):
        img *= 1.04
    return clamp(img)


def mc_decal(img, spec, rng):
    """extra absolute-pixel decals: ('R', x, y, w, h, col)  ('S', x, y, w, h, factor); negative x/y = from right/bottom"""
    h, w, _ = img.shape
    rest = []
    for it in spec:
        if it[0] in ('R', 'S'):
            _, x, y, ww, hh, v = it
            x = x if x >= 0 else w + x
            y = y if y >= 0 else h + y
            if it[0] == 'R':
                img[max(0, y):max(0, y + hh), max(0, x):max(0, x + ww)] = hexrgb(v)
            else:
                img[max(0, y):max(0, y + hh), max(0, x):max(0, x + ww)] *= v
        else:
            rest.append(it)
    return _orig_decal(img, rest, rng) if rest else img


bbgen2.paint = mc_paint
bbgen2.decal = mc_decal


# ------------------------------------------------------------------ helpers
def cb(bone, x, y, z, w, h, d, mat, **kw):
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def S(v):
    return [v, v, v]


def new(name):
    m = Model(name, density=1.0)
    m.round = False                     # vanilla look: no bevel stacks
    return m


def building_hit(m, bone='root', amp=1.0):
    m.anim('hit', 0.3, 'once', {bone: {'position': [(0, [0, 0, 0]), (0.05, [amp, 0, 0.4 * amp]), (0.1, [-amp, 0, -0.3 * amp]),
                                                    (0.16, [0.6 * amp, 0, 0]), (0.22, [-0.3 * amp, 0, 0]), (0.3, [0, 0, 0])]}})


def troop_tail(m, death, hit_bone='body'):
    m.anim('spawn', 0.5, 'once', {'root': {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, S(0.3)), (0.35, S(1.08)), (0.5, S(1))]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death)


ELX = {'elx': ('#d23fd6', 'elixir'), 'elx_d': ('#a224b0', 'elixir'), 'elx_l': ('#ec7cf0', 'elixir'),
       'mouth': ('#45104f', 'px', {'n': 0.04, 'edge': 1}), 'band': ('#efefef', 'px', {'n': 0.04, 'weave': True})}
ELX_EYE = '#ffe2ff'


# =================================================================== elixir golem / golemite
def elixir_golem(name='clash_elixir_golem', s=1.0, hb=(2.0, 2.8), mini=False):
    """Iron-golem rig made of elixir. s scales the whole thing (golemite = ~0.58)."""
    m = new(name)
    m.mats_(ELX)

    def c(bone, x, y, z, w, h, d, mat, **kw):
        return cb(bone, x * s, y * s, z * s, w * s, h * s, d * s, mat, **kw)

    def B(n, o, p):
        return m.bone(n, [v * s for v in o], p)

    root = B('root', [0, 0, 0], None)
    body = B('body', [0, 15, 0], root)
    c(body, 0, 15, 0, 11, 6, 7, 'elx_d')                                    # waist
    c(body, 0, 20, 0, 22, 13, 13, 'elx', decals={'north': [('S', 3, 4, 16, 6, 1.08), ('R', 9, 6, 4, 2, '#f39af5')],
                                                 'up': [('S', 2, 2, 18, 9, 1.05)]})
    for sx in (1, -1):                                                       # drippy shoulder lumps
        c(body, sx * 6, 33, 1, 7, 2, 8, 'elx_l')
    c(body, 0, 18, -3.6, 4, 3, 1, 'elx_l')                                   # drip down belly
    head = B('head', [0, 31, -4], body)
    face = [('R', 0, 2, 11, 2, '#8a1f99'),                                   # heavy brow
            ('R', 1, 4, 3, 2, ELX_EYE), ('R', 7, 4, 3, 2, ELX_EYE), ('R', 2, 4, 1, 1, '#ffffff'), ('R', 8, 4, 1, 1, '#ffffff'),
            ('R', 1, 7, 9, 3, '#45104f'), ('R', 2, 7, 7, 1, '#e8e0f0'),     # grin + teeth row
            ('R', 3, 7, 1, 2, '#c03bc8'), ('R', 6, 7, 1, 3, '#c03bc8'),     # drips over teeth
            ('R', 0, 10, 11, 1, '#9c2aa8')]
    c(head, 0, 29, -6, 11, 11, 10, 'elx', decals={'north': face})
    c(head, 0, 38.5, -6, 11, 2, 2.4, 'elx_d', decals={})                     # brow ledge (3D)
    c(head, 0, 40, -4, 5, 3, 7, 'elx_l')                                     # crest / peak
    c(head, 0, 42.5, -2.5, 3, 1.5, 4, 'elx_l')
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = B('arm_' + side, [sx * 13.5, 31, 0], body)
        c(arm, sx * 14.5, 8, 0, 6, 25, 7, 'elx')
        c(arm, sx * 14.5, 1.5, -0.5, 7.4, 7, 8, 'elx_l')                     # fist
        c(arm, sx * 14.5, 30, 0, 7, 3.5, 8, 'elx_d')                        # shoulder cap
        if not mini:
            tc = B('tc_collar_' + side, [sx * 14.5, 27, 0], arm)
            c(tc, sx * 14.5, 25.5, 0, 7.2, 3, 8.2, 'band', decals={f: [('S', 0, 0, 99, 1, 0.8)] for f in ('north', 'south', 'east', 'west')})
        leg = B('leg_' + side, [sx * 5, 15, 0], root)
        c(leg, sx * 5, 0, 0, 7, 15.5, 7, 'elx_d')
        c(leg, sx * 5, 0, -0.5, 7.6, 3, 8, 'elx')                            # foot blob
    if mini:
        tc = B('tc_collar', [0, 16, 0], body)
        c(tc, 0, 16, 0, 12.2, 3, 8.2, 'band', decals={f: [('S', 0, 0, 99, 1, 0.8)] for f in ('north', 'south', 'east', 'west')})
    m.hitbox(*hb)
    k = s
    idle = {'body': {'position': loop([[0, 0, 0], [0, -0.6 * k, 0]], 3.0)},
            'arm_r': {'rotation': loop([[0, 0, 2], [3, 0, 0]], 3.0)}, 'arm_l': {'rotation': loop([[0, 0, -2], [3, 0, 0]], 3.0)},
            'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 3.0)}}
    m.anim('idle', 3.0, 'loop', idle)
    L = 1.6 if not mini else 1.0
    m.anim('walk', L, 'loop', {
        'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], L)},
        'arm_r': {'rotation': loop([[-18, 0, 2], [18, 0, 2]], L)}, 'arm_l': {'rotation': loop([[18, 0, -2], [-18, 0, -2]], L)},
        'body': {'rotation': loop([[3, 0, 4], [3, 0, -4]], L), 'position': loop([[0, 0, 0], [0, 0.8 * k, 0], [0, 0, 0], [0, 0.8 * k, 0]], L)},
        'head': {'rotation': loop([[0, 0, -3], [0, 0, 3]], L)}})
    att = {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.4, [-165, 0, -8]), (0.55, [-10, 0, 0]), (0.62, [8, 0, 0]), (1.0, [0, 0, 0])]},
           'arm_l': {'rotation': [(0, [0, 0, 0]), (0.4, [-165, 0, 8]), (0.55, [-10, 0, 0]), (0.62, [8, 0, 0]), (1.0, [0, 0, 0])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.4, [-10, 0, 0]), (0.55, [16, 0, 0]), (0.75, [12, 0, 0]), (1.0, [0, 0, 0])],
                    'position': [(0, [0, 0, 0]), (0.4, [0, 1 * k, 0]), (0.55, [0, -2 * k, 0]), (1.0, [0, 0, 0])]},
           'head': {'rotation': [(0, [0, 0, 0]), (0.4, [-12, 0, 0]), (0.55, [8, 0, 0]), (1.0, [0, 0, 0])]}}
    m.anim('attack', 1.0, 'once', att)
    troop_tail(m, {'root': {'scale': [(0, S(1)), (0.2, [1.1, 0.9, 1.1]), (0.7, [1.5, 0.25, 1.5]), (0.9, [1.7, 0.05, 1.7])]},
                   'arm_r': {'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, 40])]}, 'arm_l': {'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, -40])]}})
    return m


def elixir_golemite():
    return elixir_golem('clash_elixir_golemite', s=0.58, hb=(1.3, 1.6), mini=True)


# =================================================================== elixir blob
def elixir_blob():
    m = new('clash_elixir_blob')
    m.mats_(ELX)
    m.mat('tooth', '#f4ecf6', 'px', n=0.03, edge=1)
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 0, 0], root)
    cb(body, 0, 0, 0, 10, 3, 10, 'elx_d', decals={'north': [('R', 1, 0, 8, 1, '#45104f'), ('R', 2, 0, 1, 1, '#f4ecf6'), ('R', 7, 0, 1, 1, '#f4ecf6')]})
    cb(body, 0, 2.6, 0, 7.6, 1.2, 7.6, 'mouth')                               # mouth inside (shows when biting)
    cb(body, 5.2, 0, 2, 1.5, 1.2, 3, 'elx_l')                                 # puddle drips
    cb(body, -5.2, 0, -1, 1.5, 1, 2, 'elx_l')
    head = m.bone('head', [0, 3, 5], body)
    face = [('R', 1, 1, 3, 2, ELX_EYE), ('R', 6, 1, 3, 2, ELX_EYE), ('R', 2, 2, 1, 1, '#45104f'), ('R', 7, 2, 1, 1, '#45104f'),
            ('R', 1, 4, 8, 1, '#45104f'), ('R', 2, 4, 1, 1, '#f4ecf6'), ('R', 7, 4, 1, 1, '#f4ecf6')]
    cb(head, 0, 3, 0, 10, 5, 10, 'elx', decals={'north': face})
    cb(head, 0, 8, 0.5, 7, 2, 7, 'elx_l')
    cb(head, 0.5, 10, 1, 3, 1, 3, 'elx_l')
    tc = m.bone('tc_ribbon', [0, 10, 0], head)
    cb(tc, -2, 10, 1, 2, 1.6, 1.6, 'band')
    cb(tc, -3.8, 10.2, 1, 2, 2, 1, 'band', rot=('z', 22.5))
    cb(tc, -0.2, 10.2, 1, 2, 2, 1, 'band', rot=('z', -22.5))
    m.hitbox(0.7, 0.7)
    m.anim('idle', 1.2, 'loop', {'body': {'scale': loop([[1, 1, 1], [1.07, 0.92, 1.07]], 1.2)},
                                 'tc_ribbon': {'rotation': loop([[0, 0, 6], [0, 0, -6]], 1.2)}})
    L = 0.5
    m.anim('walk', L, 'loop', {'body': {'position': [(0, [0, 0, 0]), (0.12, [0, 3, 0]), (0.25, [0, 4, 0]), (0.38, [0, 2, 0]), (0.5, [0, 0, 0])],
                                        'scale': [(0, [1.15, 0.85, 1.15]), (0.12, [0.92, 1.12, 0.92]), (0.38, [1, 1, 1]), (0.5, [1.15, 0.85, 1.15])]}})
    m.anim('attack', 0.6, 'once', {
        'head': {'rotation': [(0, [0, 0, 0]), (0.18, [-35, 0, 0]), (0.28, [4, 0, 0]), (0.38, [-6, 0, 0]), (0.6, [0, 0, 0])]},
        'body': {'position': [(0, [0, 0, 0]), (0.18, [0, 1, 1]), (0.28, [0, 0, -3]), (0.6, [0, 0, 0])],
                 'scale': [(0, S(1)), (0.18, [0.95, 1.1, 0.95]), (0.28, [1.12, 0.9, 1.12]), (0.6, S(1))]}})
    troop_tail(m, {'body': {'scale': [(0, S(1)), (0.2, [1.2, 0.8, 1.2]), (0.6, [1.8, 0.1, 1.8]), (0.9, [1.9, 0.02, 1.9])]}})
    return m


# =================================================================== goblin cage
def goblin_cage():
    m = new('clash_goblin_cage')
    m.mats_({'cobble': ('#8a8a8a', 'cobble'), 'floor': ('#9c7448', 'planks'), 'log': ('#5a3d22', 'log', {'core': '#a07a48'}),
             'bar': ('#a77d4a', 'planks', {'v': True, 'bh': 2, 'edge': 0.75}), 'roof': ('#7d5733', 'planks'),
             'iron': ('#c6c6c6', 'iron', {'rivets': True}), 'iron_d': ('#6d6d6d', 'iron'), 'lock': ('#e2b43c', 'iron'),
             'cloth': ('#efefef', 'px', {'n': 0.04, 'weave': True}),
             'skin': ('#82c22e', 'px', {'n': 0.04, 'edge': 0.88}), 'skin_d': ('#62a01e', 'px', {'n': 0.04}),
             'pants': ('#6b4a2b', 'px', {'n': 0.06}), 'belt': ('#3b2a1a', 'px', {'n': 0.05}), 'buckle': ('#d9b040', 'iron')})
    root = m.bone('root', [0, 0, 0])
    frame = m.bone('frame', [0, 0, 0], root)
    cb(frame, 0, 0, 0, 46, 4, 46, 'cobble')
    cb(frame, 0, 4, 0, 38, 1, 38, 'floor')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(frame, sx * 19, 4, sz * 19, 5, 35, 5, 'log')
            for y in (7, 31):
                cb(frame, sx * 19, y, sz * 19, 6, 2, 6, 'iron_d')
    tcp = m.bone('tc_plate', [0, 2, -23], frame)                             # team plate on stone base
    cb(tcp, 0, 0.5, -23.2, 16, 3, 0.8, 'cloth', decals={'north': [('S', 0, 0, 99, 1, 0.8), ('S', 0, -1, 99, 1, 0.8)]})
    # bars (4 sides) -----------------------------------------------------
    def bars(name, pivot, horiz_axis, plane, sign):
        b = m.bone(name, pivot, root)
        xs = (-11, -5, 5, 11) if name == 'bars_f' else (-11, -5.5, 0, 5.5, 11)
        for v in xs:
            if horiz_axis == 'x':
                cb(b, v, 5, plane, 2, 33, 2, 'bar')
            else:
                cb(b, plane, 5, v, 2, 33, 2, 'bar')
        for y in (10, 33):
            if horiz_axis == 'x':
                cb(b, 0, y, plane, 33, 2, 2, 'roof')
                cb(b, 0, y - 0.2, plane, 33.6, 0.6, 2.4, 'iron_d')
            else:
                cb(b, plane, y, 0, 2, 2, 33, 'roof')
                cb(b, plane, y - 0.2, 0, 2.4, 0.6, 33.6, 'iron_d')
        return b
    bf = bars('bars_f', [0, 5, -19], 'x', -19, -1)
    cb(bf, 0, 17, -19, 14, 2, 2.6, 'iron')                                    # latch bar
    cb(bf, 0, 12, -20.6, 4.5, 5, 2, 'lock', decals={'north': [('R', 2, 2, 1, 2, '#2a2a2a')]})   # padlock
    cb(bf, 0, 16.6, -20.6, 3, 1.6, 0.8, 'iron_d')
    bars('bars_b', [0, 5, 19], 'x', 19, 1)
    bars('bars_r', [19, 5, 0], 'z', 19, 1)
    bars('bars_l', [-19, 5, 0], 'z', -19, -1)
    # roof ---------------------------------------------------------------
    roof = m.bone('roof', [0, 38, 0], root)
    for sz in (1, -1):
        cb(roof, 0, 38, sz * 19, 44, 4, 5, 'roof')
        cb(roof, sz * 19, 38, 0, 5, 4, 34, 'roof')
    cb(roof, 0, 39, 0, 34, 2, 34, 'floor')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(roof, sx * 19, 37.5, sz * 19, 6.4, 5.5, 6.4, 'iron')
        cb(roof, 0, 41.8, sx * 8, 34, 0.6, 3, 'iron_d')                       # iron straps across roof
        fl = m.bone('tc_banner_' + ('r' if sx > 0 else 'l'), [sx * 22, 38, 0], roof)
        cb(fl, sx * 22, 28, 0, 0.8, 10, 12, 'cloth', decals={'east': [('S', 0, 0, 99, 1, 0.8), ('R', 5, 3, 2, 4, '#c8c8c8')],
                                                              'west': [('S', 0, 0, 99, 1, 0.8), ('R', 5, 3, 2, 4, '#c8c8c8')]})
        cb(fl, sx * 22, 37, 0, 1.4, 1.4, 14, 'log')
    # goblin brawler -----------------------------------------------------
    gz = -8
    gob = m.bone('gob', [0, 5, gz], root)
    for sx in (1, -1):
        cb(gob, sx * 3, 5, gz, 5, 10, 5, 'pants', decals={'north': [('R', 0, -2, 5, 2, '#3b2a1a')]})
    cb(gob, 0, 15, gz, 13, 3, 7, 'belt', decals={'north': [('R', 5, 0, 3, 3, '#d9b040'), ('R', 6, 1, 1, 1, '#3b2a1a')]})
    chest = [('R', 2, 3, 4, 1, '#5e9c1c'), ('R', 7, 3, 4, 1, '#5e9c1c'), ('R', 6, 4, 1, 4, '#5e9c1c'),
             ('R', 4, 6, 2, 1, '#6aaa22'), ('R', 7, 6, 2, 1, '#6aaa22'), ('R', 4, 8, 2, 1, '#6aaa22'), ('R', 7, 8, 2, 1, '#6aaa22')]
    cb(gob, 0, 18, gz, 13, 10, 7, 'skin', decals={'north': chest})
    tcs = m.bone('tc_strap', [0, 22, gz], gob)
    cb(tcs, 0, 16.5, gz, 3, 14, 7.6, 'cloth', rot=('z', -45), rot_origin=[0, 23, gz])
    head = m.bone('gob_head', [0, 28, gz], gob)
    gface = [('R', 0, 1, 9, 1, '#2f5a12'), ('R', 1, 2, 3, 1, '#2f5a12'), ('R', 5, 2, 3, 1, '#2f5a12'),
             ('R', 1, 3, 3, 2, '#f6f0c8'), ('R', 5, 3, 3, 2, '#f6f0c8'), ('R', 2, 3, 2, 2, '#e7b52c'), ('R', 5, 3, 2, 2, '#e7b52c'),
             ('R', 2, 4, 1, 1, '#151515'), ('R', 6, 4, 1, 1, '#151515'),
             ('R', 1, 6, 7, 3, '#4a1010'), ('R', 1, 6, 7, 1, '#ffffff'), ('R', 2, 8, 5, 1, '#c84a4a')]
    cb(head, 0, 28, gz - 0.5, 9, 9, 9, 'skin', decals={'north': gface, 'up': [('S', 0, 0, 99, 99, 0.95)]})
    cb(head, 0, 31.5, gz - 5.6, 3, 2.5, 2.2, 'skin_d')                          # big nose
    cb(head, 0, 36.6, gz - 1.5, 7, 1, 5, 'skin_d')                               # brow ridge/scalp bump
    for sx in (1, -1):                                                            # pointy ears
        cb(head, sx * 6.5, 32.5, gz, 4.5, 2, 1.5, 'skin', rot=('z', sx * 22.5))
        cb(head, sx * 9, 34, gz, 2, 1.5, 1.2, 'skin_d', rot=('z', sx * 22.5))
    for sx, side in ((1, 'r'), (-1, 'l')):                                        # arms reach forward to grip bars
        arm = m.bone('gob_arm_' + side, [sx * 9, 25, gz + 1], gob)
        cb(arm, sx * 9, 22.5, gz + 1, 5, 5, 6, 'skin')
        cb(arm, sx * 9.2, 22, gz - 5.5, 5, 5, 8, 'skin', decals={'up': [('R', 0, 2, 5, 1, '#6aaa22')]})
        cb(arm, sx * 9.8, 21.5, -19, 5.6, 5.8, 4.2, 'skin_d', decals={'north': [('R', 0, 2, 99, 1, '#4c8a14')]})
    m.hitbox(3.2, 2.6)
    # ---- animations
    L = 1.6
    idle = {'gob': {'position': loop([[0, 0, 0.0], [0, 0, 1.0], [0, 0, -0.3], [0, 0, 1.0], [0, 0, -0.3], [0, 0, 0.2], [0, 0, 0], [0, 0, 0]], L),
                    'rotation': loop([[0, 0, 0], [-3, 0, 2], [3, 0, -2], [-3, 0, 2], [3, 0, -2], [0, 0, 0], [0, 0, 0], [0, 0, 0]], L)},
            'bars_f': {'rotation': loop([[0, 0, 0], [-1.5, 0, 0.6], [1.2, 0, -0.6], [-1.5, 0, 0.6], [1.2, 0, -0.6], [0, 0, 0], [0, 0, 0], [0, 0, 0]], L)},
            'gob_head': {'rotation': loop([[0, 0, 0], [6, 0, 8], [-4, 0, -8], [6, 0, 8], [-4, 0, -8], [0, 12, 0], [0, -12, 0], [0, 0, 0]], L)},
            'tc_banner_r': {'rotation': loop([[0, 0, 4], [0, 0, -2]], L)}, 'tc_banner_l': {'rotation': loop([[0, 0, -4], [0, 0, 2]], L)}}
    m.anim('idle', L, 'loop', idle)
    m.anim('attack', 0.6, 'once', {
        'gob': {'position': [(0, [0, 0, 0]), (0.1, [0, 0.4, 1.6]), (0.2, [0, 0, -0.8]), (0.3, [0, 0.4, 1.6]), (0.4, [0, 0, -0.8]), (0.6, [0, 0, 0])]},
        'bars_f': {'rotation': [(0, [0, 0, 0]), (0.1, [-3, 0, 1]), (0.2, [3, 0, -1]), (0.3, [-3, 0, 1]), (0.4, [3, 0, -1]), (0.6, [0, 0, 0])]},
        'gob_head': {'rotation': [(0, [0, 0, 0]), (0.1, [-18, 0, 0]), (0.45, [-14, 0, 0]), (0.6, [0, 0, 0])]},
        'roof': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.6, 0]), (0.2, [0, 0, 0]), (0.35, [0, 0.6, 0]), (0.4, [0, 0, 0])]}})
    m.anim('spawn', 0.6, 'once', {'root': {'position': [(0, [0, 26, 0]), (0.28, [0, 0, 0]), (0.4, [0, 1.2, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, S(0.6)), (0.28, [1.1, 0.86, 1.1]), (0.4, [0.97, 1.04, 0.97]), (0.6, S(1))]}})
    building_hit(m)
    m.anim('death', 1.0, 'hold', {
        'bars_f': {'rotation': [(0, [0, 0, 0]), (0.1, [-6, 0, 0]), (0.3, [84, 0, 0]), (0.38, [76, 0, 0]), (0.45, [82, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.3, [0, -3, -1])]},
        'bars_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 4]), (0.34, [0, 0, -80]), (0.45, [0, 0, -74])], 'position': [(0, [0, 0, 0]), (0.34, [0, -3, 0])]},
        'bars_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -4]), (0.34, [0, 0, 80]), (0.45, [0, 0, 74])], 'position': [(0, [0, 0, 0]), (0.34, [0, -3, 0])]},
        'bars_b': {'rotation': [(0, [0, 0, 0]), (0.14, [4, 0, 0]), (0.36, [-80, 0, 0]), (0.46, [-74, 0, 0])], 'position': [(0, [0, 0, 0]), (0.36, [0, -3, 0])]},
        'roof': {'position': [(0, [0, 0, 0]), (0.2, [0, 8, 0]), (0.5, [0, -30, 3]), (0.6, [0, -32, 3])],
                 'rotation': [(0, [0, 0, 0]), (0.2, [-6, 0, 10]), (0.5, [-8, 0, 16]), (0.6, [-8, 0, 18])]},
        'gob': {'position': [(0, [0, 0, 0]), (0.12, [0, -2, 0]), (0.32, [0, 12, -16]), (0.5, [0, 0, -30])],
                'scale': [(0, S(1)), (0.32, S(1.1)), (0.5, S(1)), (0.56, S(0.01)), (1.0, S(0.01))]},
        'gob_arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-60, 0, 0]), (0.45, [-30, 0, 0])]},
        'gob_arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [-60, 0, 0]), (0.45, [-30, 0, 0])]},
        'gob_head': {'rotation': [(0, [0, 0, 0]), (0.12, [-20, 0, 0]), (0.3, [-10, 0, 0])]},
        'frame': {'rotation': [(0, [0, 0, 0]), (0.15, [0, 0, 2]), (0.3, [0, 0, -1]), (0.5, [0, 0, 0])]}})
    return m


# =================================================================== x-bow (turret)
def x_bow():
    m = new('clash_x_bow')
    m.mats_({'cobble': ('#8c8c8c', 'cobble'), 'stone': ('#9e9e9e', 'px', {'n': 0.06}),
             'iron': ('#c8c8c8', 'iron', {'rivets': True}), 'iron_d': ('#6f6f73', 'iron'), 'steel': ('#a9b0b8', 'iron'),
             'tip': ('#d8dde2', 'iron'), 'stock': ('#6b4426', 'planks'), 'limb': ('#9a6a3c', 'planks', {'bh': 3}),
             'string': ('#e8e0c8', 'px', {'n': 0.03, 'edge': 1}), 'cloth': ('#efefef', 'px', {'n': 0.04, 'weave': True}),
             'rope': ('#b49a6a', 'rope')})
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    cb(base, 0, 0, 0, 36, 5, 36, 'cobble')
    for sz in (1, -1):                                                         # iron rim
        cb(base, 0, 5, sz * 17, 36, 1.5, 2, 'iron_d')
        cb(base, sz * 17, 5, 0, 2, 1.5, 32, 'iron_d')
    cb(base, 0, 5, 0, 32, 0.8, 32, 'stone')
    tcb = m.bone('base_tc_plate', [0, 6, 0], base)
    for sx in (1, -1):
        for sz in (1, -1):
            cb(tcb, sx * 11.5, 6, sz * 11.5, 8, 5, 8, 'cloth', decals={f: [('S', 0, 0, 99, 1, 1.06), ('S', 0, -1, 99, 1, 0.78)] for f in ('north', 'south', 'east', 'west')})
        cb(tcb, sx * 18.4, 1, 0, 0.8, 3, 12, 'cloth')
        cb(tcb, 0, 1, sx * 18.4, 12, 3, 0.8, 'cloth')
    cb(base, 0, 5.5, 0, 13, 3, 13, 'iron')                                     # stand foot
    cb(base, 0, 8.5, 0, 8, 14, 8, 'steel', decals={f: [('R', 3, 2, 2, 10, '#7f868e')] for f in ('north', 'south', 'east', 'west')})
    cb(base, 0, 13, 0, 9, 1.5, 9, 'iron_d')
    cb(base, 0, 21.5, 0, 10, 2.5, 10, 'iron_d')
    Y = 24
    top = m.bone('top', [0, Y, 0], root)
    cb(top, 0, Y, 0, 13, 2.5, 13, 'iron')                                     # swivel plate
    for sx in (1, -1):
        cb(top, sx * 4.5, Y + 2.5, 0, 2, 6, 7, 'iron_d')                      # yoke cheeks
    by = Y + 6                                                               # stock bottom
    bow = m.bone('top_bow', [0, by + 2, 0], top)
    cb(bow, 0, by, 1, 6, 5, 32, 'stock', decals={'up': [('R', 2, 0, 2, 99, '#4a2e18')]})
    for z in (-11, 9):
        cb(bow, 0, by - 0.4, z, 7, 5.8, 2, 'iron_d')
    cb(bow, 0, by + 2.5, -13.5, 11, 4, 4, 'iron', decals={'north': [('R', 4, 1, 3, 2, '#3a3a3e')]})  # prod block
    cb(bow, 0, by - 1.5, 14, 4, 3, 4, 'iron_d')                               # trigger housing
    ly = by + 3                                                               # limbs bottom
    for sx, side in ((1, 'r'), (-1, 'l')):
        cr = m.bone('top_crank_' + side, [sx * 3.6, by + 2, 11], bow)
        cb(cr, sx * 3.6, by, 11, 1.2, 4.5, 4.5, 'iron_d')
        cb(cr, sx * 4.6, by + 3.5, 11, 1, 1, 3, 'iron')
        lb = m.bone('top_limb_' + side, [sx * 4, ly + 1.5, -13], bow)
        x1 = 4 + 10 * math.cos(math.radians(22.5)); z1 = -13 + 10 * math.sin(math.radians(22.5))
        x2 = x1 + 7 * math.cos(math.radians(45)); z2 = z1 + 7 * math.sin(math.radians(45))
        lb.box([min(sx * 4, sx * 14), ly, -14.5], [max(sx * 4, sx * 14), ly + 3, -11.5], 'limb',
               rot=('y', -sx * 22.5), rot_origin=[sx * 4, ly, -13])
        lb.box([min(sx * x1, sx * (x1 + 7.5)), ly + 0.25, z1 - 1.25], [max(sx * x1, sx * (x1 + 7.5)), ly + 2.75, z1 + 1.25], 'limb',
               rot=('y', -sx * 45), rot_origin=[sx * x1, ly, z1])
        tw = m.bone('top_tc_wrap_' + side, [sx * x1, ly + 1.5, z1], lb)
        tw.box([sx * x1 - 2, ly - 0.4, z1 - 2], [sx * x1 + 2, ly + 3.4, z1 + 2], 'cloth', rot=('y', -sx * 22.5), rot_origin=[sx * x1, ly, z1])
        cb(lb, sx * x2, ly - 0.5, z2, 2.2, 4, 2.2, 'iron')                    # limb tip cap
        L = (x2 - 0.5) / math.cos(math.radians(22.5))
        st = m.bone('top_string_' + side, [sx * x2, ly + 1.8, z2], lb)
        st.box([min(sx * x2, sx * (x2 - L)), ly + 1.5, z2 - 0.3], [max(sx * x2, sx * (x2 - L)), ly + 2.1, z2 + 0.3], 'string',
               rot=('y', sx * 22.5), rot_origin=[sx * x2, ly + 1.8, z2])
        nock_z = z2 + (x2 - 0.5) * math.tan(math.radians(22.5))
    bolt = m.bone('top_bolt', [0, ly + 2, -14], bow)
    cb(bolt, 0, ly + 1, (nock_z - 16) / 2, 2, 2, nock_z + 16, 'steel')
    cb(bolt, 0, ly + 1, -19, 6, 2, 6, 'tip', rot=('y', 45))                   # diamond arrowhead
    cb(bolt, 0, ly + 1.4, -16.5, 3, 1.2, 2, 'iron_d')
    fl = m.bone('top_tc_fletch', [0, ly + 2, nock_z - 3], bolt)
    cb(fl, 0, ly + 3, nock_z - 3, 0.6, 2.5, 5, 'cloth')
    cb(fl, 0, ly + 1.7, nock_z - 3, 5, 0.6, 5, 'cloth')
    m.hitbox(2.6, 2.4)
    # ---- animations
    m.anim('idle', 2.4, 'loop', {'top_bow': {'rotation': loop([[0, 0, 0], [-1.5, 0, 0]], 2.4)},
                                 'top_crank_r': {'rotation': loop([[0, 0, 0], [8, 0, 0]], 2.4)},
                                 'top_crank_l': {'rotation': loop([[0, 0, 0], [8, 0, 0]], 2.4)}})
    T = 0.3
    att = {'top_string_r': {'rotation': [(0, [0, 0, 0]), (0.03, [0, 22.5, 0]), (0.06, [0, 17, 0]), (0.1, [0, 21, 0]), (0.16, [0, 10, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_string_l': {'rotation': [(0, [0, 0, 0]), (0.03, [0, -22.5, 0]), (0.06, [0, -17, 0]), (0.1, [0, -21, 0]), (0.16, [0, -10, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_limb_r': {'rotation': [(0, [0, 0, 0]), (0.03, [0, -9, 0]), (0.06, [0, -5, 0]), (0.1, [0, -8, 0]), (0.16, [0, -4, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_limb_l': {'rotation': [(0, [0, 0, 0]), (0.03, [0, 9, 0]), (0.06, [0, 5, 0]), (0.1, [0, 8, 0]), (0.16, [0, 4, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_bolt': {'position': [(0, [0, 0, 0]), (0.03, [0, 0, -14]), (0.05, [0, 0, -18]), (0.06, [0, 0, 4]), (0.18, [0, 0, 4]), (0.26, [0, 0, 0]), (T, [0, 0, 0])],
                        'scale': [(0, S(1)), (0.05, S(1)), (0.055, S(0.01)), (0.17, S(0.01)), (0.26, S(1)), (T, S(1))]},
           'top_bow': {'position': [(0, [0, 0, 0]), (0.04, [0, 0.4, 2.6]), (0.12, [0, 0, 0.6]), (T, [0, 0, 0])],
                       'rotation': [(0, [0, 0, 0]), (0.04, [-4, 0, 0]), (0.14, [1, 0, 0]), (T, [0, 0, 0])]},
           'top_crank_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.27, [-180, 0, 0]), (T, [-180, 0, 0])]},
           'top_crank_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.27, [-180, 0, 0]), (T, [-180, 0, 0])]},
           'top': {'position': [(0, [0, 0, 0]), (0.04, [0, 0, 0.8]), (0.12, [0, 0, 0]), (T, [0, 0, 0])]}}
    m.anim('attack', T, 'once', att)
    m.anim('spawn', 0.8, 'once', {
        'base': {'scale': [(0, [1, 0.05, 1]), (0.3, [1.02, 1.08, 1.02]), (0.4, S(1)), (0.8, S(1))]},
        'top': {'scale': [(0, S(0.01)), (0.3, S(0.01)), (0.31, S(1)), (0.8, S(1))],
                'position': [(0, [0, 10, 0]), (0.3, [0, 10, 0]), (0.5, [0, -1, 0]), (0.6, [0, 0.5, 0]), (0.8, [0, 0, 0])]},
        'top_bow': {'rotation': [(0, [0, 0, 0]), (0.3, [-10, 0, 0]), (0.58, [3, 0, 0]), (0.8, [0, 0, 0])]}})
    building_hit(m)
    m.anim('death', 1.0, 'hold', {
        'base': {'scale': [(0, S(1)), (0.15, S(1.03)), (0.55, [1.05, 0.72, 1.05]), (0.9, [1.08, 0.58, 1.08])]},
        'top': {'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.6, [-5, -12, 2]), (0.8, [-7, -15, 2]), (1.0, [-7, -15, 2])],
                'rotation': [(0, [0, 0, 0]), (0.6, [10, 0, 35]), (0.8, [12, 0, 40])]},
        'top_string_r': {'rotation': [(0, [0, 0, 0]), (0.1, [0, 22.5, 0])]},
        'top_string_l': {'rotation': [(0, [0, 0, 0]), (0.1, [0, -22.5, 0])]},
        'top_bolt': {'position': [(0, [0, 0, 0]), (0.3, [0, -6, 2])], 'rotation': [(0, [0, 0, 0]), (0.3, [0, 0, 40])]}})
    return m


# =================================================================== bomb tower (turret)
def bomb_tower():
    m = new('clash_bomb_tower')
    m.mats_({'cobble': ('#868686', 'cobble'), 'wall': ('#b0814c', 'planks'), 'wall_d': ('#8a6036', 'planks'),
             'log': ('#5b3d22', 'log', {'core': '#a47c4a'}), 'iron': ('#c3c3c3', 'iron', {'rivets': True}), 'iron_d': ('#6c6c70', 'iron'),
             'rope': ('#c2a774', 'rope'), 'cloth': ('#efefef', 'px', {'n': 0.04, 'weave': True}),
             'bone': ('#e8e4d4', 'px', {'n': 0.05, 'edge': 0.82}), 'brass': ('#c08a3a', 'iron'), 'lens': ('#8fd8ff', 'px', {'n': 0.02, 'edge': 1}),
             'bomb': ('#2c2c34', 'iron'), 'fuse': ('#7a6040', 'px'), 'spark': ('#ffd84a', 'glowpx'),
             'leather': ('#6b4a2b', 'px', {'n': 0.06})})
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    tw = m.bone('base_tower', [0, 0, 0], base)
    cb(tw, 0, 0, 0, 30, 4, 22, 'cobble'); cb(tw, 0, 0, 0, 22, 4, 30, 'cobble')
    cb(tw, 0, 4, 0, 22, 26, 16, 'wall'); cb(tw, 0, 4, 0, 16, 26, 22, 'wall_d')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(tw, sx * 8.5, 4, sz * 8.5, 4.5, 26, 4.5, 'log')
    for y in (9, 22):                                                         # rope lashings
        cb(tw, 0, y, 0, 23, 1.2, 17, 'rope'); cb(tw, 0, y, 0, 17, 1.2, 23, 'rope')
        for sx in (1, -1):
            for sz in (1, -1):
                cb(tw, sx * 8.5, y, sz * 8.5, 5.2, 1.2, 5.2, 'rope')
    cb(tw, 0, 4, -11.2, 6, 9, 0.6, 'log', decals={'north': [('R', 2, 3, 1, 1, '#c3c3c3')]})   # little door
    tcs = m.bone('base_tc_stripe', [0, 15, 0], tw)
    cb(tcs, 0, 14, 0, 22.8, 3, 16.8, 'cloth'); cb(tcs, 0, 14, 0, 16.8, 3, 22.8, 'cloth')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(tcs, sx * 8.5, 14, sz * 8.5, 5.1, 3, 5.1, 'cloth')
    crown = m.bone('base_crown', [0, 30, 0], base)
    cb(crown, 0, 30, 0, 28, 3, 22, 'wall_d'); cb(crown, 0, 30, 0, 22, 3, 28, 'wall_d')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(crown, sx * 10, 29.5, sz * 10, 4, 4, 4, 'log')
    # steel rams: log beams poking out of the 4 sides, iron-capped
    for i, (dx, dz) in enumerate(((0, -1), (0, 1), (1, 0), (-1, 0))):
        rb = m.bone('base_ram_%d' % i, [dx * 11, 25, dz * 11], base)
        if dz:
            cb(rb, 0, 24, dz * 14, 3.5, 3.5, 8, 'log'); cb(rb, 0, 23.75, dz * 18.5, 4, 4, 2, 'iron')
            cb(rb, 0, 24.75, dz * 20, 2, 2, 1.6, 'iron_d')
        else:
            cb(rb, dx * 14, 24, 0, 8, 3.5, 3.5, 'log'); cb(rb, dx * 18.5, 23.75, 0, 2, 4, 4, 'iron')
            cb(rb, dx * 20, 24.75, 0, 1.6, 2, 2, 'iron_d')
    # rails on the platform
    for nm, (dx, dz) in (('n', (0, -1)), ('s', (0, 1)), ('e', (1, 0)), ('w', (-1, 0))):
        rb = m.bone('base_rail_' + nm, [dx * 12, 33, dz * 12], base)
        if dz:
            cb(rb, 0, 36, dz * 12.5, 22, 1.5, 1.5, 'log')
            for x in (-10, 10):
                cb(rb, x, 33, dz * 12.5, 2, 3.5, 2, 'log')
        else:
            cb(rb, dx * 12.5, 36, 0, 1.5, 1.5, 22, 'log')
    # ---- bomber (turret)
    Y0 = 33
    top = m.bone('top', [0, Y0, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('top_leg_' + side, [sx * 1.5, Y0 + 6, 0], top)
        cb(lg, sx * 1.5, Y0, 0, 2, 6.5, 2, 'bone')
        cb(lg, sx * 1.5, Y0, -0.5, 2.6, 1.6, 3.2, 'leather')
    body = m.bone('top_body', [0, Y0 + 6, 0], top)
    cb(body, 0, Y0 + 5.5, 0, 6, 2, 3.2, 'leather', decals={'north': [('R', 2, 0, 2, 2, '#c08a3a')]})
    ribs = [('R', 0, 1, 99, 1, '#4a4038'), ('R', 0, 3, 99, 1, '#4a4038'), ('R', 2, 0, 2, 99, '#e8e4d4')]
    cb(body, 0, Y0 + 7.5, 0, 6, 6, 3, 'bone', decals={'north': ribs, 'south': ribs})
    cb(body, 2, Y0 + 7, -1.8, 1, 6.6, 0.6, 'leather', rot=('z', -22.5))     # bandolier
    head = m.bone('top_head', [0, Y0 + 13.5, 0], body)
    skull = [('R', 1, 2, 2, 2, '#26221e'), ('R', 4, 2, 1, 2, '#26221e'), ('R', 4, 2, 1, 1, '#3a3530'),
             ('R', 3, 3, 1, 1, '#5a5048'), ('R', 1, 4, 4, 1, '#3a3530'), ('R', 2, 5, 1, 1, '#3a3530'), ('R', 4, 5, 1, 1, '#3a3530')]
    cb(head, 0, Y0 + 13.5, 0, 6, 6, 6, 'bone', decals={'north': skull})
    cb(head, 0, Y0 + 17, 0, 6.6, 1.4, 6.6, 'leather')                         # goggle strap
    for sx in (1, -1):
        cb(head, sx * 1.6, Y0 + 16.6, -3.4, 2.4, 2.2, 1, 'brass')
        cb(head, sx * 1.6, Y0 + 17, -3.95, 1.4, 1.4, 0.2, 'lens')
    cap = m.bone('top_tc_cap', [0, Y0 + 19.5, 0], head)
    cb(cap, 0, Y0 + 18.4, 0.3, 6.8, 2.2, 6.8, 'cloth', decals={'north': [('S', 0, -1, 99, 1, 0.8)]})
    cb(cap, 0, Y0 + 20.6, 0.6, 4, 1, 4, 'cloth')
    cb(cap, 0, Y0 + 21.6, 0.6, 1.4, 1, 1.4, 'cloth')                          # pom
    ar = m.bone('top_arm_r', [4, Y0 + 12.5, 0], body)                         # throwing arm, held forward
    cb(ar, 4, Y0 + 11.5, -3, 2, 2, 7, 'bone')
    cb(ar, 4, Y0 + 11.3, 0, 2.4, 2.4, 2.4, 'leather')
    bomb = m.bone('top_bomb', [4, Y0 + 12.5, -8], ar)
    cb(bomb, 4, Y0 + 10.3, -8.5, 4.4, 4.4, 4.4, 'bomb', decals={'north': [('R', 1, 1, 1, 1, '#8a8a96')]})
    cb(bomb, 4, Y0 + 9.8, -8.5, 3.4, 5.4, 3.4, 'bomb')
    cb(bomb, 4, Y0 + 14.7, -8.5, 0.8, 1.4, 0.8, 'fuse')
    cb(bomb, 4, Y0 + 16.1, -8.5, 1, 1, 1, 'spark')
    al = m.bone('top_arm_l', [-4, Y0 + 12.5, 0], body)
    cb(al, -4, Y0 + 6.5, 0, 2, 7, 2, 'bone')
    m.hitbox(2.0, 3.2)
    # ---- animations
    m.anim('idle', 2.0, 'loop', {'top_body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)},
                                 'top_head': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 2.0)},
                                 'top_arm_r': {'rotation': loop([[0, 0, 0], [-6, 0, 0]], 2.0)},
                                 'top_arm_l': {'rotation': loop([[0, 0, -4], [6, 0, -2]], 2.0)},
                                 'top_bomb': {'rotation': loop([[0, 0, 0], [0, 15, 0]], 2.0)}})
    T, REL = 0.8, 0.3
    m.anim('attack', T, 'once', {
        'top_arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-140, 0, 0]), (REL, [-30, 0, 0]), (0.4, [30, 0, 0]), (0.55, [20, 0, 0]), (T, [0, 0, 0])]},
        'top_bomb': {'scale': [(0, S(1)), (REL, S(1)), (REL + 0.02, S(0.01)), (0.55, S(0.01)), (0.7, S(1.15)), (T, S(1))]},
        'top_body': {'rotation': [(0, [0, 0, 0]), (0.15, [-10, -15, 0]), (REL, [12, 10, 0]), (0.45, [10, 5, 0]), (T, [0, 0, 0])]},
        'top_arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [-60, 0, -10]), (REL, [20, 0, -6]), (T, [0, 0, 0])]},
        'top_head': {'rotation': [(0, [0, 0, 0]), (0.15, [-8, 0, 0]), (REL, [8, 0, 0]), (T, [0, 0, 0])]},
        'top_leg_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-10, 0, 0]), (REL, [8, 0, 0]), (T, [0, 0, 0])]},
        'top_leg_l': {'rotation': [(0, [0, 0, 0]), (0.15, [10, 0, 0]), (REL, [-12, 0, 0]), (T, [0, 0, 0])]}})
    m.anim('spawn', 0.8, 'once', {
        'base': {'scale': [(0, [1, 0.05, 1]), (0.3, [1.02, 1.08, 1.02]), (0.4, S(1)), (0.8, S(1))]},
        'top': {'scale': [(0, S(0.01)), (0.35, S(0.01)), (0.36, S(1)), (0.8, S(1))],
                'position': [(0, [0, 8, 0]), (0.35, [0, 8, 0]), (0.55, [0, -1, 0]), (0.65, [0, 0.5, 0]), (0.8, [0, 0, 0])]},
        'top_arm_r': {'rotation': [(0, [0, 0, 0]), (0.35, [-20, 0, 0]), (0.6, [10, 0, 0]), (0.8, [0, 0, 0])]}})
    building_hit(m)
    fall = {0: [0, -22, -6], 1: [0, -22, 6], 2: [-6, -22, 0], 3: [6, -22, 0]}       # anim x mirrored
    rfall = {'n': [0, -30, -8], 's': [0, -30, 8], 'e': [-8, -30, 0], 'w': [8, -30, 0]}
    death = {'base_tower': {'scale': [(0, S(1)), (0.15, S(1.03)), (0.35, [1.06, 0.85, 1.06]), (0.65, [1.12, 0.4, 1.12]), (0.9, [1.15, 0.3, 1.15])]},
             'base_crown': {'position': [(0, [0, 0, 0]), (0.25, [0, 1, 0]), (0.65, [0, -18, 0]), (0.9, [0, -20, 0])],
                            'rotation': [(0, [0, 0, 0]), (0.65, [6, 0, -8]), (0.9, [8, 0, -10])]},
             'top': {'position': [(0, [0, 0, 0]), (0.12, [0, 3, 0]), (0.3, [0, 1, 0])],
                     'scale': [(0, S(1)), (0.12, S(1.1)), (0.3, S(0.01)), (1.0, S(0.01))]}}
    for k, v in fall.items():
        death['base_ram_%d' % k] = {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.6, v)],
                                    'rotation': [(0, [0, 0, 0]), (0.6, [30 if k < 2 else 0, 0, 30 if k >= 2 else 0])]}
    for k, v in rfall.items():
        death['base_rail_' + k] = {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.6, v)]}
    m.anim('death', 1.0, 'hold', death)
    return m


MODELS = (elixir_golem, elixir_golemite, elixir_blob, goblin_cage, x_bow, bomb_tower)
CARDS = {'clash_elixir_golem': 'elixir-golem.png', 'clash_elixir_golemite': 'elixir-golem.png', 'clash_elixir_blob': 'elixir-golem.png',
         'clash_goblin_cage': 'goblin-cage.png', 'clash_x_bow': 'x-bow.png', 'clash_bomb_tower': 'bomb-tower.png'}
BUILDINGS = ('clash_goblin_cage', 'clash_x_bow', 'clash_bomb_tower')


# ------------------------------------------------------------------ comparison sheets
def compose(docs_offsets):
    """merge several bbmodel docs into one, shifted along x (same camera + scale)."""
    import copy
    out = {'elements': [], 'outliner': [], 'textures': [], 'resolution': {'width': 16, 'height': 16}, 'animations': []}
    for ti, (d, dx) in enumerate(docs_offsets):
        d = copy.deepcopy(d)
        t = d['textures'][0]
        t['id'] = str(ti); t['uv_width'] = t.get('uv_width') or d['resolution']['width']; t['uv_height'] = t.get('uv_height') or d['resolution']['height']
        out['textures'].append(t)
        for e in d['elements']:
            e['from'][0] += dx; e['to'][0] += dx
            if 'origin' in e:
                e['origin'][0] += dx
            for f in e['faces'].values():
                if f.get('texture') is not None and f.get('texture') is not False:
                    f['texture'] = ti
            out['elements'].append(e)

        def sh(n):
            if isinstance(n, str):
                return
            n['origin'] = [n.get('origin', [0, 0, 0])[0] + dx] + list(n.get('origin', [0, 0, 0])[1:])
            for ch in n.get('children', []):
                sh(ch)
        for n in d['outliner']:
            if isinstance(n, dict):
                sh(n)
            out['outliner'].append(n)
        out['animations'] += d['animations']
    return out


def cmp_sheet(name, out):
    from PIL import Image, ImageDraw
    from bbrender import render, sample
    W = os.path.dirname(os.path.abspath(__file__))
    ref = os.path.join(W, 'pkg342/ClashMC_v3.4.2/models/base')
    REF = os.path.join(W, '../refimg')
    d = json.load(open(os.path.join(out, name + '.bbmodel')))
    hog = json.load(open(os.path.join(ref, 'clash_hog_rider.bbmodel')))
    parts = [(hog, 70)]
    if name in BUILDINGS:
        parts.append((json.load(open(os.path.join(ref, 'clash_tesla.bbmodel'))), 125))
    parts.append((d, 0))
    comp = compose(parts)
    tint = (90, 140, 255)
    big = render(comp, 620, cam=(0.6, 0.5, -1.0), tint=tint)
    card = Image.open(os.path.join(REF, CARDS[name])).convert('RGBA')
    card = card.resize((int(card.width * 300 / card.height), 300))
    frames = []
    anims = [a['name'] for a in d['animations']]
    picks = [('idle', 0)]
    if 'walk' in anims:
        picks.append(('walk', 0.25 * next(a['length'] for a in d['animations'] if a['name'] == 'walk')))
    al = next(a['length'] for a in d['animations'] if a['name'] == 'attack')
    picks += [('attack', al * 0.4), ('attack', al * 0.6), ('death', 0.95)]
    for an, t in picks:
        im = render(d, 200, cam=(0.6, 0.5, -1.0), tint=(255, 90, 90), pose=sample(d, an, t))
        ImageDraw.Draw(im).text((4, 4), '%s %.2f' % (an, t), fill=(0, 0, 0, 255))
        frames.append(im)
    back = render(d, 200, cam=(-0.6, 0.6, 1.0), tint=tint)
    frames.append(back)
    Wd = max(620 + card.width + 10, 200 * len(frames))
    sheet = Image.new('RGBA', (Wd, 620 + 200), (232, 236, 241, 255))
    sheet.paste(big, (0, 0))
    sheet.paste(card, (630, 20), card)
    for i, f in enumerate(frames):
        sheet.paste(f, (i * 200, 620))
    ImageDraw.Draw(sheet).text((630, 330), '%s  %d cubes' % (name, len(d['elements']) - 1), fill=(0, 0, 0, 255))
    sheet.convert('RGB').save(os.path.join(out, 'cmp_%s.png' % name))


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    only = [a for a in sys.argv[3:] if not a.startswith('--')]
    os.makedirs(out, exist_ok=True)
    for fn in MODELS:
        m = fn()
        if only and m.name not in only:
            continue
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total - 1, 'split', n, 'bad', bad, 'hitbox', m.hitbox_size)
        if '--cmp' in sys.argv:
            cmp_sheet(m.name, out)
