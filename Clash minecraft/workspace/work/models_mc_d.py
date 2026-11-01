"""MC-style (vanilla Minecraft mob look) models, set D:
witch / night witch / wizard / dart goblin / goblin brawler / heal spirit.
Player/zombie rig proportions, few big boxes, 1 texel = 1 px pixel-art textures, faces painted flat on the head.
Units: px (16 = 1 block), front = north (-Z), origin = feet centre.
usage: python3 models_mc_d.py <model_tools dir> <out dir> [only...]"""
import sys, os, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
import numpy as np
import bbgen2
from bbgen2 import Model, hexrgb, clamp

# ------------------------------------------------------------------ MC pixel-art painter
_orig_paint = bbgen2.paint


def mcpaint(kind, base, w, h, rng, face, opts):
    if kind != 'mc':
        return _orig_paint(kind, base, w, h, rng, face, opts)
    c = hexrgb(base)
    g = np.random.default_rng(rng.randrange(1 << 30))
    img = np.ones((h, w, 3)) * c
    n = opts.get('n', 0.06)
    img *= 1 + g.uniform(-n, n, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    pat = opts.get('pat')
    vert = face not in ('up', 'down')
    if pat == 'wool':
        img[((yy + xx) % 2) == 0] *= 0.95
        m = g.random((h, w)) < 0.12
        img[m] *= 0.88
    elif pat in ('plank', 'vplank'):
        if pat == 'vplank' and vert:
            for x in range(w):
                img[:, x] *= 1 + 0.07 * math.sin(x * 2.3 + g.random())
            for x in range(3, w, 4):
                img[:, x] *= 0.72
        else:
            for y in range(h):
                img[y, :] *= 1 + 0.07 * math.sin(y * 2.3 + g.random())
            if h >= 4:
                for y in range(3, h, 4):
                    img[y, :] *= 0.72
        m = g.random((h, w)) < 0.1
        img[m] *= 0.85
    elif pat == 'gold':
        img[((xx + yy) % 6) == 0] *= 1.18
        img[((xx - yy) % 7) == 3] *= 0.9
        if h > 2:
            img[0, :] = clamp(img[0, :] * 1.2 + 10)
    elif pat == 'iron':
        if h > 2:
            img[0, :] = clamp(img[0, :] * 1.18 + 10)
        m = g.random((h, w)) < 0.1
        img[m] *= 1.1
    elif pat == 'glow':
        cy, cx = (h - 1) / 2, (w - 1) / 2
        d = np.sqrt(((yy - cy) / max(h, 1)) ** 2 + ((xx - cx) / max(w, 1)) ** 2)
        img = img * (1.15 - d.reshape(h, w, 1) * 0.5) + 15
    elif pat == 'leaf':
        m = g.random((h, w))
        img[m < 0.22] *= 0.72
        img[m > 0.85] *= 1.15
    elif pat == 'skin':
        m = g.random((h, w)) < 0.06
        img[m] *= 0.94
    sp = opts.get('sp', 0.0)
    if sp:
        m = g.random((h, w)) < sp
        img[m] *= 0.85
    e = opts.get('e', 0.8)
    if e < 1 and w >= 3 and h >= 3:
        img[0, :] *= e; img[-1, :] *= e; img[:, 0] *= e; img[:, -1] *= e
    if face == 'down':
        img *= 0.8
    return clamp(img)


bbgen2.paint = mcpaint


def MC(color, pat=None, **kw):
    o = dict(kw)
    if pat:
        o['pat'] = pat
    return (color, 'mc', o)


# ------------------------------------------------------------------ helpers
def bx(bone, x0, y0, z0, x1, y1, z1, mat, **kw):
    return bone.box([min(x0, x1), min(y0, y1), min(z0, z1)], [max(x0, x1), max(y0, y1), max(z0, z1)], mat, **kw)


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """centred on (x, z), bottom at y"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def G(rows, pal):
    """pixel grid decal: rows top->bottom as seen from outside the face; '.' = keep"""
    out = []
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and ch != ' ':
                out.append(('px', x, y, pal[ch]))
    return out


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def kf(*pts):
    return [(t, list(v)) for t, v in pts]


def common_tail(m, root='root', hit_bone='body', death=None, spawn_len=0.5):
    m.anim('spawn', spawn_len, 'once', {root: {'position': kf((0, [0, -6, 0]), (spawn_len * 0.7, [0, 1.5, 0]), (spawn_len, [0, 0, 0])),
                                               'scale': kf((0, [0.3, 0.3, 0.3]), (spawn_len * 0.7, [1.08, 1.08, 1.08]), (spawn_len, [1, 1, 1]))}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': kf((0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])),
                                           'rotation': kf((0, [0, 0, 0]), (0.08, [-8, 0, 0]), (0.3, [0, 0, 0]))}})
    m.anim('death', 0.9, 'hold', death or {root: {'rotation': kf((0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])),
                                                  'position': kf((0, [0, 0, 0]), (0.6, [0, -2, 0]), (0.9, [0, -3, 0]))}})


def walk_anim(m, L=0.8, leg=26, arm=22, extra=None, arms=('arm_r', 'arm_l'), arm_base=None):
    ab = arm_base or {}
    w = {'leg_r': {'rotation': loop([[leg, 0, 0], [-leg, 0, 0]], L)},
         'leg_l': {'rotation': loop([[-leg, 0, 0], [leg, 0, 0]], L)},
         'body': {'position': loop([[0, 0, 0], [0, 0.6, 0], [0, 0, 0], [0, 0.6, 0]], L)}}
    for a, s in zip(arms, (1, -1)):
        if a:
            b = ab.get(a, [0, 0, 0])
            w[a] = {'rotation': loop([[b[0] - s * arm, b[1], b[2]], [b[0] + s * arm, b[1], b[2]]], L)}
    if extra:
        w.update(extra)
    m.anim('walk', L, 'loop', w)


def new_model(name, density=1.0):
    m = Model(name, density=density)
    m.round = False
    return m


# shared pixel palettes
SKULL = {'k': '#2a1a10', 'd': '#7a5a10'}


# =================================================================== WITCH
def witch():
    m = new_model('clash_witch')
    m.mats_({
        'skin': MC('#e6c3c6', 'skin', e=1.0), 'hair': MC('#4a2a6a', 'wool', e=0.85),
        'hood': MC('#6b44a8', 'wool'), 'hood_d': MC('#4d2f80', 'wool'), 'top': MC('#3a3740', 'wool'),
        'cloth': MC('#efefef', 'wool', e=0.85), 'boot': MC('#2a2430', None, e=0.75),
        'gold': MC('#f2c03a', 'gold', e=0.72), 'gskull': MC('#f0bf3c', 'gold', e=0.75),
        'wood': MC('#5a3b22', 'vplank', e=0.75), 'bone': MC('#e8dcc0', None, n=0.05, e=0.8),
        'horn': MC('#8a7a62', None, e=0.75), 'orb': MC('#ff5ae0', 'glow', e=1.0), 'orb_w': MC('#ffd0f6', 'glow', e=1.0),
        'belt': MC('#2a1f33', None, e=0.8),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 12, 0], root)
    # legs (only shoes show under the dress)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        bx(lg, sx * 0.1, 0, -2, sx * 3.9, 11, 2, 'boot')
    # torso: dark grey top, belt, violet collar
    bx(body, -4, 12, -2, 4, 24, 2, 'top', decals={'north': G([
        '........', '........', '...gg...', '...gg...', '........', '........',
        '........', '........', '........', '........', '........', '........'], {'g': '#e3b23a'})})
    bx(body, -4.3, 12, -2.3, 4.3, 13.5, 2.3, 'belt')
    bx(body, -4.6, 22, -2.6, 4.6, 24.4, 2.6, 'hood')                                # hood mantle on the shoulders
    tcd = m.bone('tc_dress', [0, 12, 0], body)
    bx(tcd, -4.5, 4, -2.75, 4.5, 12.2, 2.75, 'cloth', decals={'north': G(['.........'] * 7 + ['ddddddddd'], {'d': '#cfcfcf'})})
    bx(tcd, -5, 2.4, -3.25, 5, 4.2, 3.25, 'cloth')                                 # hem flare
    cape = m.bone('cape', [0, 24, 2.6], body)
    bx(cape, -4.6, 3, 2.6, 4.6, 24, 3.6, 'hood_d', decals={'south': G(['.' * 9] * 20 + ['d.d.d.d.d'], {'d': '#3a2364'})})
    # arms (slim 3 px)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.5, 22.5, 0], body)
        bx(arm, sx * 4, 12, -1.5, sx * 7, 24, 1.5, 'hood')
        bx(arm, sx * 4, 12, -1.5, sx * 7, 16, 1.5, 'skin')
        tg = m.bone('tc_glove_' + side, [sx * 5.5, 14, 0], arm)
        bx(tg, sx * 3.8, 11.8, -1.7, sx * 7.2, 15.2, 1.7, 'cloth')
        # golden shoulder skull
        bx(arm, sx * 3.7, 23.5, -2, sx * 7.4, 25, 2, 'gold')
        bx(arm, sx * 4.2, 25, -1.6, sx * 7.4, 28, 1.6, 'gskull', decals={'north': G(['...', 'k.k', '.d.'], SKULL),
                                                                          ('east' if sx > 0 else 'west'): G(['...', '..k', '...'], SKULL)})
    # head
    head = m.bone('head', [0, 24, 0], body)
    face = G(['hhhhhhhh',
              'hhhhhhhh',
              'hsssssssh'[:8],
              'sbbssbbs',
              'sPWssWPs',
              'ssssssss',
              'sssllsss',
              'ssssssss'], {'h': '#4a2a6a', 's': '#e6c3c6', 'b': '#3a1f50', 'P': '#ff3fd2', 'W': '#ffc6f4', 'l': '#5a2a6e'})
    side_hair = G(['hhhhhhhh', 'hhhhhhhh', 'hhhhhhhs', 'hhhhhhss', 'hhhhhhss', 'hhhhhhhs', 'hhhhhhhs', 'hhhhhh.s'], {'h': '#4a2a6a', 's': '#e6c3c6'})
    side_hair_w = G([r[::-1] for r in ['hhhhhhhh', 'hhhhhhhh', 'hhhhhhhs', 'hhhhhhss', 'hhhhhhss', 'hhhhhhhs', 'hhhhhhhs', 'hhhhhh.s']],
                    {'h': '#4a2a6a', 's': '#e6c3c6'})
    bx(head, -4, 24, -4, 4, 32, 4, 'skin', decals={'north': face, 'east': side_hair, 'west': side_hair_w},
       faces={'up': 'hair', 'south': 'hair'})
    hood = m.bone('hood', [0, 24, 0], head)
    bx(hood, -4.7, 32, -4.9, 4.7, 33.2, 4.7, 'hood')                               # top
    for sx in (1, -1):
        bx(hood, sx * 4, 25.5, -4.9, sx * 4.9, 32, 4.7, 'hood', decals={'north': G(['d'] * 7, {'d': '#3e2668'})})
    bx(hood, -4.7, 24, 4, 4.7, 32, 4.9, 'hood_d')                                  # back
    bx(hood, -4.7, 31, -5.3, 4.7, 32.4, -4.6, 'hood_d')                            # front brim
    bx(hood, -3, 33.2, -3, 3, 35, 3.5, 'hood')                                     # pointed tip
    bx(hood, -1.5, 35, -0.5, 1.5, 37, 2.5, 'hood_d')
    # staff with ram skull (right hand)
    staff = m.bone('staff', [5.5, 13.5, -2.6], m.by_name('arm_r'))
    bx(staff, 4.6, 1, -3.5, 6.4, 34, -1.7, 'wood')
    bx(staff, 4.3, 30, -3.8, 6.7, 31, -1.4, 'gold')
    bx(staff, 3.5, 34, -4.8, 7.5, 38, -0.6, 'bone', decals={'north': G(['....', 'k..k', '.kk.', '....'], {'k': '#2a2018'})})
    bx(staff, 4.3, 34, -5.8, 6.7, 36, -4.8, 'bone', decals={'north': G(['k.k', '...'], {'k': '#2a2018'})})   # snout
    for sx in (1, -1):
        hx = 5.5 + sx * 2
        bx(staff, hx, 35, -3.6, hx + sx * 1.8, 38.6, -0.4, 'horn', decals={('east' if sx > 0 else 'west'): G(['....', '.dd.', '.d..', '....'], {'d': '#5a4c3a'})})
        bx(staff, hx, 33, -5, hx + sx * 1.6, 35, -3.4, 'horn')
    orb = m.bone('orb', [5.5, 39.2, -2.7], staff)
    bx(orb, 4.6, 38, -3.6, 6.4, 39.8, -1.8, 'orb')
    bx(orb, 5.1, 39.8, -3.1, 5.9, 40.6, -2.3, 'orb_w')
    m.hitbox(0.9, 2.1)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
            'head': {'rotation': loop([[0, 5, 0], [2, 0, 0], [0, -5, 0], [2, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([[-14, 0, 0], [-17, 0, 0]], 2.0)},
            'staff': {'rotation': loop([[14, 0, 0], [17, 0, 0]], 2.0)},
            'arm_l': {'rotation': loop([[0, 0, -3], [-4, 0, -5]], 2.0)},
            'cape': {'rotation': loop([[2, 0, 0], [5, 0, 0]], 2.0)},
            'orb': {'scale': loop([[1, 1, 1], [1.2, 1.2, 1.2]], 1.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk_anim(m, 0.8, leg=18, arm=20, arms=(None, 'arm_l'), extra={
        'arm_r': {'rotation': loop([[-18, 0, 0], [-10, 0, 0]], 0.8)}, 'staff': {'rotation': loop([[18, 0, 0], [10, 0, 0]], 0.8)},
        'cape': {'rotation': loop([[10, 0, 0], [16, 0, 0]], 0.8)}})
    # attack 0.7 s: draw the staff back, swing it forward and fire from the skull
    m.anim('attack', 0.7, 'once', {
        'arm_r': {'rotation': kf((0, [-14, 0, 0]), (0.22, [30, 0, 6]), (0.34, [-75, 0, 0]), (0.5, [-60, 0, 0]), (0.7, [-14, 0, 0]))},
        'staff': {'rotation': kf((0, [14, 0, 0]), (0.22, [-20, 0, 0]), (0.34, [20, 0, 0]), (0.7, [14, 0, 0]))},
        'orb': {'scale': kf((0, [1, 1, 1]), (0.22, [1.3, 1.3, 1.3]), (0.34, [2.0, 2.0, 2.0]), (0.42, [0.7, 0.7, 0.7]), (0.7, [1, 1, 1]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.22, [-6, 10, 0]), (0.34, [8, -8, 0]), (0.7, [0, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.22, [-25, 0, -15]), (0.34, [15, 0, -10]), (0.7, [0, 0, 0]))}})
    # summon 0.6 s: raise the staff high over the head, skull glows, thump down
    m.anim('summon', 0.6, 'once', {
        'arm_r': {'rotation': kf((0, [-14, 0, 0]), (0.2, [-165, 0, -8]), (0.42, [-165, 0, -8]), (0.52, [-40, 0, 0]), (0.6, [-14, 0, 0]))},
        'staff': {'rotation': kf((0, [14, 0, 0]), (0.2, [0, 0, 0]), (0.42, [0, 0, 0]), (0.6, [14, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [-30, 0, -45]), (0.45, [-30, 0, -45]), (0.6, [0, 0, 0]))},
        'orb': {'scale': kf((0, [1, 1, 1]), (0.2, [1.8, 1.8, 1.8]), (0.42, [2.4, 2.4, 2.4]), (0.52, [1, 1, 1]), (0.6, [1, 1, 1]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.52, [5, 0, 0]), (0.6, [0, 0, 0]))},
        'head': {'rotation': kf((0, [0, 0, 0]), (0.2, [-14, 0, 0]), (0.52, [4, 0, 0]), (0.6, [0, 0, 0]))}})
    common_tail(m)
    return m


# =================================================================== NIGHT WITCH
def night_witch():
    m = new_model('clash_night_witch')
    m.mats_({
        'skin': MC('#e2c4c4', 'skin', e=1.0), 'cloak': MC('#2b2a31', 'wool'), 'cloak_d': MC('#1d1c22', 'wool'),
        'dress': MC('#3c3a46', 'wool'), 'cloth': MC('#efefef', 'wool', e=0.85), 'iron': MC('#c7ccd4', 'iron', e=0.7),
        'boot': MC('#1c1b20', None, e=0.75), 'shaft': MC('#2e2a2c', 'vplank', e=0.75), 'blade': MC('#4a4c58', 'iron', e=0.7),
        'blade_e': MC('#8c93a3', 'iron', e=0.8), 'crys': MC('#52e8ff', 'glow', e=1.0), 'crys_w': MC('#d4fbff', 'glow', e=1.0),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 12, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        bx(lg, sx * 0.1, 0, -2, sx * 3.9, 11, 2, 'boot')
    bx(body, -4, 12, -2, 4, 24, 2, 'dress', decals={'north': G(['.' * 8] * 2 + ['..dddd..', '...dd...'] + ['.' * 8] * 8, {'d': '#2a2933'})})
    bx(body, -4.3, 12, -2.3, 4.3, 13.6, 2.3, 'iron', decals={'north': G(['...kk...', '...kk...'], {'k': '#6c7280'})})   # silver belt
    bx(body, -4.7, 22, -2.7, 4.7, 24.4, 2.7, 'cloak')                               # collar
    bx(body, -4.5, 4.6, -2.75, 4.5, 12.2, 2.75, 'dress')                            # skirt
    tct = m.bone('tc_trim', [0, 4, 0], body)
    bx(tct, -5, 3, -3.25, 5, 4.8, 3.25, 'cloth')
    bx(tct, -4.6, 11, -2.85, 4.6, 12, 2.85, 'cloth')                                # waist trim under the belt
    cape = m.bone('cape', [0, 24, 2.7], body)
    bx(cape, -5, 2, 2.7, 5, 24, 3.8, 'cloak_d')
    for x0, h in ((-5, 2), (-1.5, 1.2), (2.5, 2.4)):                                 # ragged hem
        bx(cape, x0, 2 - h, 2.8, x0 + 2.5, 2, 3.7, 'cloak_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.5, 22.5, 0], body)
        bx(arm, sx * 4, 12, -1.5, sx * 7, 24, 1.5, 'cloak')
        bx(arm, sx * 4, 12, -1.5, sx * 7, 18, 1.5, 'skin')
        bx(arm, sx * 3.75, 15, -1.75, sx * 7.25, 17, 1.75, 'iron')                   # silver armlet
        bx(arm, sx * 3.7, 22, -2, sx * 7.3, 24.6, 2, 'cloak_d')                      # shoulder of the cloak
    head = m.bone('head', [0, 24, 0], body)
    face = G(['kkkkkkkk',
              'kkkkkkkk',
              'kkkkkkkk',
              'sCWkkWCs',
              'ssskksss',
              'ssssssss',
              'sssmmsss',
              'ssssssss'], {'k': '#1d1c22', 's': '#e2c4c4', 'C': '#3fe6ff', 'W': '#d8fcff', 'm': '#6a3a4a'})
    hairs = G(['kkkkkkkk'] * 6 + ['kkkkkkks', 'kkkkkkss'], {'k': '#1a191e', 's': '#e2c4c4'})
    hairw = G(['kkkkkkkk'] * 6 + ['skkkkkkk', 'sskkkkkk'], {'k': '#1a191e', 's': '#e2c4c4'})
    bx(head, -4, 24, -4, 4, 32, 4, 'skin', decals={'north': face, 'east': hairs, 'west': hairw}, faces={'up': 'cloak_d', 'south': 'cloak_d'})
    hood = m.bone('hood', [0, 24, 0], head)
    bx(hood, -4.7, 32, -5, 4.7, 33.3, 4.8, 'cloak')
    for sx in (1, -1):
        bx(hood, sx * 4, 24.5, -5, sx * 4.9, 32, 4.8, 'cloak')
    bx(hood, -4.7, 23, 4, 4.7, 32, 4.9, 'cloak_d')
    bx(hood, -4.7, 30.6, -5.4, 4.7, 32.3, -4.6, 'cloak')                            # brim
    bx(hood, -1, 29, -5.4, 1, 30.6, -4.6, 'cloak')                                  # hood point between the eyes
    bx(hood, -3, 33.3, -3, 3, 35.5, 3.6, 'cloak')
    bx(hood, -1.5, 35.5, 0, 1.5, 37.5, 3.6, 'cloak_d')
    # long dark axe-staff with a glowing crystal
    staff = m.bone('staff', [5.5, 13.5, -2.6], m.by_name('arm_r'))
    bx(staff, 4.6, -1, -3.5, 6.4, 38, -1.7, 'shaft')
    for y in (28, 36):
        bx(staff, 4.3, y, -3.8, 6.7, y + 1, -1.4, 'iron')
    bx(staff, 5, 29, -9.5, 6, 36, -3.5, 'blade', decals={'east': G(['eeee..', 'e.....'] + ['e.....'] * 4 + ['eeeee.'], {'e': '#9aa2b2'}),
                                                       'west': G(['..eeee', '.....e'] + ['.....e'] * 4 + ['.eeeee'], {'e': '#9aa2b2'})})
    bx(staff, 5, 25.5, -10.5, 6, 30, -8.5, 'blade_e')                               # hooked lower tip of the blade
    bx(staff, 5, 36, -7, 6, 38, -3.5, 'blade')
    cr = m.bone('crystal', [5.5, 40, -2.6], staff)
    bx(cr, 4.4, 38, -3.7, 6.6, 41.5, -1.5, 'crys')
    bx(cr, 5, 41.5, -3.1, 6, 42.6, -2.1, 'crys_w')
    m.hitbox(1.0, 2.2)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
            'head': {'rotation': loop([[0, 5, 0], [2, 0, 0], [0, -5, 0], [2, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([[-14, 0, 0], [-17, 0, 0]], 2.0)},
            'staff': {'rotation': loop([[14, 0, 0], [17, 0, 0]], 2.0)},
            'arm_l': {'rotation': loop([[0, 0, -3], [-4, 0, -5]], 2.0)},
            'cape': {'rotation': loop([[3, 0, 0], [7, 0, 0]], 2.0)},
            'crystal': {'scale': loop([[1, 1, 1], [1.15, 1.15, 1.15]], 1.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk_anim(m, 0.8, leg=18, arm=20, arms=(None, 'arm_l'), extra={
        'arm_r': {'rotation': loop([[-18, 0, 0], [-10, 0, 0]], 0.8)}, 'staff': {'rotation': loop([[18, 0, 0], [10, 0, 0]], 0.8)},
        'cape': {'rotation': loop([[12, 0, 0], [20, 0, 0]], 0.8)}})
    # attack 0.8 s: wind the scythe back over the shoulder, then a wide sweep across
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': kf((0, [-14, 0, 0]), (0.28, [-120, -30, 20]), (0.42, [-70, 50, -10]), (0.55, [-40, 40, 0]), (0.8, [-14, 0, 0]))},
        'staff': {'rotation': kf((0, [14, 0, 0]), (0.28, [20, 0, 0]), (0.42, [40, 0, 0]), (0.8, [14, 0, 0]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.28, [-6, 25, 0]), (0.42, [8, -25, 0]), (0.55, [4, -15, 0]), (0.8, [0, 0, 0]))},
        'cape': {'rotation': kf((0, [3, 0, 0]), (0.42, [25, 0, 0]), (0.8, [3, 0, 0]))},
        'crystal': {'scale': kf((0, [1, 1, 1]), (0.42, [1.6, 1.6, 1.6]), (0.8, [1, 1, 1]))}})
    m.anim('summon', 0.6, 'once', {
        'arm_r': {'rotation': kf((0, [-14, 0, 0]), (0.2, [-165, 0, -8]), (0.42, [-165, 0, -8]), (0.52, [-40, 0, 0]), (0.6, [-14, 0, 0]))},
        'staff': {'rotation': kf((0, [14, 0, 0]), (0.2, [0, 0, 0]), (0.42, [0, 0, 0]), (0.6, [14, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [-30, 0, -45]), (0.45, [-30, 0, -45]), (0.6, [0, 0, 0]))},
        'crystal': {'scale': kf((0, [1, 1, 1]), (0.2, [1.8, 1.8, 1.8]), (0.42, [2.4, 2.4, 2.4]), (0.52, [1, 1, 1]), (0.6, [1, 1, 1]))},
        'cape': {'rotation': kf((0, [3, 0, 0]), (0.3, [30, 0, 0]), (0.6, [3, 0, 0]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.52, [5, 0, 0]), (0.6, [0, 0, 0]))}})
    common_tail(m)
    return m


# =================================================================== WIZARD
def wizard():
    m = new_model('clash_wizard')
    m.mats_({
        'skin': MC('#e0a77e', 'skin', e=1.0), 'hair': MC('#6a3f22', 'wool', e=0.85), 'shirt': MC('#4a2e1e', 'wool'),
        'cloth': MC('#efefef', 'wool', e=0.82), 'belt': MC('#5a3a20', None, e=0.75), 'boot': MC('#4a2e1c', None, e=0.72),
        'trim': MC('#d8d2c4', 'wool', e=0.85), 'gold': MC('#f2c03a', 'gold', e=0.72),
        'fire': MC('#ff7a1c', 'glow', e=1.0), 'fire_y': MC('#ffe25a', 'glow', e=1.0), 'fire_r': MC('#e8401a', 'glow', e=1.0),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 12, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        bx(lg, sx * 0, 0, -2, sx * 4, 4, 2, 'boot')
        tp = m.bone('tc_pants_' + side, [sx * 2, 12, 0], lg)
        bx(tp, sx * 0, 4, -2, sx * 4, 12, 2, 'cloth')
    bx(body, -4, 12, -2, 4, 24, 2, 'shirt', decals={'north': G(['........'] * 9 + ['...gg...'] + ['........'] * 2, {'g': '#e8b84a'})})
    bx(body, -4.25, 12, -2.25, 4.25, 13.5, 2.25, 'belt', decals={'north': G(['...gg....', '...gg....'], {'g': '#e8b84a'})})
    tcc = m.bone('tc_cloak', [0, 24, 0], body)
    for sx in (1, -1):
        bx(tcc, sx * 1.5, 13.5, -2.4, sx * 4.4, 24.3, 2.4, 'cloth')                  # open coat panels
    bx(tcc, -4.4, 6, 2.3, 4.4, 24.3, 3.3, 'cloth', decals={'south': G(['.' * 9] * 18, {})})   # back / long tail
    for sx in (1, -1):
        bx(tcc, sx * 1.5, 7, -2.4, sx * 4.4, 13.5, -1.4, 'cloth')                    # front coat tails
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 6, 22, 0], body)
        tca = m.bone('tc_sleeve_' + side, [sx * 6, 22, 0], arm)
        bx(tca, sx * 4, 15, -2, sx * 8, 24, 2, 'cloth')
        bx(arm, sx * 4.2, 14.4, -2.2, sx * 7.8, 15.4, 2.2, 'trim')                    # cuff
        bx(arm, sx * 4, 12, -2, sx * 8, 15, 2, 'skin')
        fl = m.bone('flame_' + side, [sx * 6, 10.5, 0], arm)
        bx(fl, sx * 5, 9, -1, sx * 7, 11, 1, 'fire')
        bx(fl, sx * 5.5, 8, -0.5, sx * 6.5, 9, 0.5, 'fire_y')
        bx(fl, sx * 4.5, 9.5, -0.5, sx * 5, 10.5, 0.5, 'fire_r')
    head = m.bone('head', [0, 24, 0], body)
    face = G(['hhhhhhhh',
              'hhhhhhhh',
              'hBBssBBh',
              'sWEssEWs',
              'sssnnsss',
              'shhhhhhs',
              'shmmmmhs',
              'sshhhhss'], {'h': '#6a3f22', 's': '#e0a77e', 'B': '#4a2a16', 'W': '#ffffff', 'E': '#3a5aa8',
                            'n': '#c88a64', 'm': '#5a1e18'})
    hs = G(['hhhhhhhh', 'hhhhhhhh', 'hhhhhhhs', 'hhhhhhss', 'hhhhhsss', 'hhhhhhss', 'hhhhhhhs', 'hhhhhhhs'], {'h': '#6a3f22', 's': '#e0a77e'})
    hw = G([r[::-1] for r in ['hhhhhhhh', 'hhhhhhhh', 'hhhhhhhs', 'hhhhhhss', 'hhhhhsss', 'hhhhhhss', 'hhhhhhhs', 'hhhhhhhs']],
           {'h': '#6a3f22', 's': '#e0a77e'})
    bx(head, -4, 24, -4, 4, 32, 4, 'skin', decals={'north': face, 'east': hs, 'west': hw}, faces={'up': 'hair', 'south': 'hair'})
    bx(head, -1, 22.5, -4.6, 1, 24.5, -3.6, 'hair')                                  # goatee tip
    bx(head, -0.5, 27.2, -4.6, 0.5, 28.4, -4, 'skin')                                # nose
    hood = m.bone('tc_hood', [0, 24, 0], head)
    bx(hood, -4.7, 32, -4.9, 4.7, 33.3, 4.7, 'cloth')
    for sx in (1, -1):
        bx(hood, sx * 4, 24.5, -4.9, sx * 4.9, 32, 4.7, 'cloth', decals={'north': G(['t'] * 8, {'t': '#ffffff'})})
    bx(hood, -4.7, 22.5, 4, 4.7, 32, 5, 'cloth')
    bx(hood, -4.7, 31, -5.3, 4.7, 32.3, -4.6, 'cloth', decals={'north': G(['t' * 9], {'t': '#ffffff'})})
    bx(hood, -3.5, 33.3, -2.5, 3.5, 34.6, 4, 'cloth')
    m.hitbox(0.9, 2.1)

    hold = lambda s, a=0: [-30 + a, 0, s * 6]
    flame_fix = lambda a=0: [30 - a, 0, 0]
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
            'head': {'rotation': loop([[0, 5, 0], [2, 0, 0], [0, -5, 0], [2, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([hold(1), hold(1, -5)], 2.0)}, 'arm_l': {'rotation': loop([hold(-1, -5), hold(-1)], 2.0)},
            'flame_r': {'scale': loop([[1, 1, 1], [1.15, 1.3, 1.15]], 0.4), 'rotation': loop([flame_fix(), flame_fix(-5)], 2.0)},
            'flame_l': {'scale': loop([[1.15, 1.3, 1.15], [1, 1, 1]], 0.4), 'rotation': loop([flame_fix(-5), flame_fix()], 2.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk_anim(m, 0.8, leg=26, arm=10, arm_base={'arm_r': hold(1), 'arm_l': hold(-1)}, extra={
        'flame_r': {'scale': loop([[1, 1, 1], [1.15, 1.3, 1.15]], 0.4), 'rotation': [(0, flame_fix()), (0.8, flame_fix())]},
        'flame_l': {'scale': loop([[1.15, 1.3, 1.15], [1, 1, 1]], 0.4), 'rotation': [(0, flame_fix()), (0.8, flame_fix())]},
        'tc_cloak': {'rotation': loop([[4, 0, 0], [8, 0, 0]], 0.4)}})
    att = {}
    for side, s in (('r', 1), ('l', -1)):
        att['arm_' + side] = {'rotation': kf((0, hold(s)), (0.2, [15, 0, s * 10]), (0.3, [-90, 0, -s * 10]), (0.42, [-85, 0, -s * 8]), (0.6, hold(s)))}
        att['flame_' + side] = {'scale': kf((0, [1, 1, 1]), (0.2, [1.4, 1.4, 1.4]), (0.3, [2.0, 2.0, 2.0]), (0.36, [0.4, 0.4, 0.4]), (0.6, [1, 1, 1])),
                                'rotation': kf((0, flame_fix()), (0.2, [-15, 0, 0]), (0.3, [90, 0, 0]), (0.42, [85, 0, 0]), (0.6, flame_fix()))}
    att['body'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.3, [10, 0, 0]), (0.42, [6, 0, 0]), (0.6, [0, 0, 0])),
                   'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 1]), (0.3, [0, 0, -1.5]), (0.6, [0, 0, 0]))}
    m.anim('attack', 0.6, 'once', att)
    common_tail(m)
    return m


# =================================================================== DART GOBLIN (small rig)
def dart_goblin():
    m = new_model('clash_dart_goblin')
    m.mats_({
        'skin': MC('#8cc43c', 'skin', e=1.0), 'skin_d': MC('#6fa02c', 'skin', e=0.85), 'leaf': MC('#3c8a2a', 'leaf', e=0.8),
        'leaf_l': MC('#5aae34', 'leaf', e=0.8), 'mask': MC('#b98a52', 'vplank', e=0.72), 'cloth': MC('#efefef', None, n=0.03, e=1.0),
        'eye': MC('#ff2a1a', 'glow', e=1.0), 'pipe': MC('#a89a58', 'plank', e=0.75), 'band': MC('#6a4a2a', None, e=0.8),
        'dark': MC('#1e1a14', None, e=1.0),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.5, 4, 0], root)
        bx(lg, sx * 0.25, 0, -1.25, sx * 2.75, 4, 1.25, 'skin', faces={'down': 'skin_d'})
    bx(body, -2.5, 4, -1.5, 2.5, 10, 1.5, 'skin', decals={'north': G(['.....', '.....', '..d..', '.....', '.....', '.....'], {'d': '#6fa02c'})})
    sk = m.bone('skirt', [0, 6, 0], body)
    bx(sk, -3, 3, -2, 3, 6.5, 2, 'leaf', decals={'north': G(['llllll', 'l.l.l.', 'l.l.l.', '.l...l'], {'l': '#5aae34'})})
    for sx in (1, -1):
        bx(sk, sx * 0.4, 2, -2.2, sx * 2.6, 3.4, -1.6, 'leaf_l')
    # arms reaching forward to hold the pipe (baked pose)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 3.5, 9.5, 0], body)
        reach = -5.5 if sx > 0 else -9.5
        bx(arm, sx * 2.5, 8, -1, sx * 4.5, 10, 1, 'skin')
        bx(arm, sx * 2.6, 8.3, reach, sx * 4.2, 9.9, -1, 'skin')
        bx(arm, sx * 0.6, 8.3, reach - 1.6, sx * 3.0, 10.3, reach + 0.2, 'skin_d')   # hand on the pipe
    head = m.bone('head', [0, 10, 0], body)
    bx(head, -3, 10, -3, 3, 16, 3, 'skin', decals={'east': G(['......', '......', '...d..', '......', '......', '......'], {'d': '#5a8a24'})})
    for sx, side in ((1, 'r'), (-1, 'l')):
        e = m.bone('ear_' + side, [sx * 3, 13, 0], head)
        bx(e, sx * 3, 12.5, -0.5, sx * 6.5, 14, 0.5, 'skin')
        bx(e, sx * 5.5, 14, -0.5, sx * 6.5, 15, 0.5, 'skin')
    # wooden voodoo mask
    mask = m.bone('mask', [0, 13, -3], head)
    bx(mask, -3.5, 8.5, -4, 3.5, 17.5, -3, 'mask', decals={'north': G([
        '.......', '.......', '.......', '.......', '.......', '.......', '.......', '...d...', '.......'], {'d': '#7a5430'})})
    tcp = m.bone('tc_paint', [0, 14, -4], mask)
    for sx in (1, -1):
        bx(tcp, sx * 0.4, 13, -4.3, sx * 3.2, 15.8, -4, 'cloth', decals={'north': G(['ccc', 'c.c', 'ccc'], {'c': '#efefef'})})
        bx(mask, sx * 1.3, 13.9, -4.5, sx * 2.3, 14.9, -4.2, 'eye')
    # leaf headdress
    hd = m.bone('headdress', [0, 16, 0], head)
    for x, z, h, r, mat in ((0, 0.5, 6, None, 'leaf_l'), (2.2, 1, 5, ('z', -22.5), 'leaf'), (-2.2, 1, 5, ('z', 22.5), 'leaf'),
                            (3.5, 1.5, 4, ('z', -45), 'leaf_l'), (-3.5, 1.5, 4, ('z', 45), 'leaf_l'), (0, 2.5, 5, ('x', 22.5), 'leaf')):
        cb(hd, x, 15.5, z, 2, h, 1, mat, rot=r, rot_origin=[x, 15.5, z])
    # blowgun
    pipe = m.bone('pipe', [0, 11.5, -4], body)
    bx(pipe, -0.75, 10.75, -18, 0.75, 12.25, -3.8, 'pipe')
    for z in (-7, -12):
        bx(pipe, -1, 10.5, z - 0.5, 1, 12.5, z + 0.5, 'band')
    bx(pipe, -1.1, 10.4, -18.6, 1.1, 12.6, -17, 'band', decals={'north': G(['..', '.k'], {'k': '#1e1a14'})})
    m.bone('muzzle', [0, 11.5, -18.8], pipe)
    m.hitbox(0.7, 1.2)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 1.0)},
            'head': {'rotation': loop([[0, 0, 0], [-3, 0, 0]], 1.0)},
            'ear_r': {'rotation': loop([[0, 0, 0], [0, 0, 10], [0, 0, 0], [0, 0, 0]], 1.0)},
            'ear_l': {'rotation': loop([[0, 0, 0], [0, 0, 0], [0, 0, -10], [0, 0, 0]], 1.0)},
            'headdress': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 1.0)},
            'pipe': {'rotation': loop([[0, 0, 0], [-2, 0, 0]], 1.0)}}
    m.anim('idle', 1.0, 'loop', idle)
    walk_anim(m, 0.4, leg=38, arm=0, arms=(None, None), extra={
        'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.4), 'rotation': loop([[6, 4, 0], [6, -4, 0]], 0.4)},
        'ear_r': {'rotation': loop([[0, 0, 12], [0, 0, -6]], 0.2)}, 'ear_l': {'rotation': loop([[0, 0, -12], [0, 0, 6]], 0.2)},
        'headdress': {'rotation': loop([[0, 0, 6], [0, 0, -6]], 0.2)}})
    m.anim('attack', 0.3, 'once', {
        'head': {'rotation': kf((0, [0, 0, 0]), (0.08, [-5, 0, 0]), (0.12, [4, 0, 0]), (0.3, [0, 0, 0]))},
        'body': {'position': kf((0, [0, 0, 0]), (0.08, [0, 0, 0.8]), (0.12, [0, 0, -0.8]), (0.3, [0, 0, 0])),
                 'rotation': kf((0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.12, [5, 0, 0]), (0.3, [0, 0, 0]))},
        'pipe': {'position': kf((0, [0, 0, 0]), (0.08, [0, 0, 0.6]), (0.12, [0, 0, -1.4]), (0.3, [0, 0, 0]))},
        'ear_r': {'rotation': kf((0, [0, 0, 0]), (0.12, [0, 0, 16]), (0.3, [0, 0, 0]))},
        'ear_l': {'rotation': kf((0, [0, 0, 0]), (0.12, [0, 0, -16]), (0.3, [0, 0, 0]))}})
    common_tail(m)
    return m


# =================================================================== GOBLIN BRAWLER (big rig, built at 1x then scaled)
BRAWL_K = 1.3


def goblin_brawler():
    K = BRAWL_K
    m = new_model('clash_goblin_brawler', density=1.0 / K)
    m.mats_({
        'skin': MC('#7cbf38', 'skin', e=1.0), 'skin_d': MC('#64a02a', 'skin', e=0.9), 'wrap': MC('#f2efe6', 'wool', e=0.8),
        'cloth': MC('#efefef', 'wool', e=0.82), 'belt': MC('#5a3a20', None, e=0.75), 'dark': MC('#2a2a2a', None, e=0.9),
        'gold': MC('#f2c03a', 'gold', e=0.72),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 10, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.5, 10, 0], root)
        bx(lg, sx * 0.25, 0, -2.25, sx * 4.75, 10, 2.25, 'skin', faces={'down': 'skin_d'},
           decals={'north': G(['.....'] * 8 + ['.....', 'd.d.d'], {'d': '#4a7a20'})})
        ts = m.bone('tc_shorts_' + side, [sx * 2.5, 10, 0], lg)
        bx(ts, sx * 0, 4.5, -2.5, sx * 5, 10, 2.5, 'cloth')
    chest = G(['..........',
               '..........',
               '..........',
               '.dddd.ddd.'[:10],
               '..........',
               '....dd....',
               '...d..d...',
               '....dd....',
               '...d..d...',
               '..........',
               '..........',
               '..........'], {'d': '#5a9a28'})
    bx(body, -5, 10, -2.5, 5, 22, 2.5, 'skin', decals={'north': chest})
    tcw = m.bone('tc_shorts', [0, 10, 0], body)
    bx(tcw, -5.25, 9.5, -2.75, 5.25, 12, 2.75, 'cloth')
    bx(body, -5.4, 11.6, -2.9, 5.4, 12.8, 2.9, 'belt', decals={'north': G(['....gg....'], {'g': '#e8b84a'})})
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 7.5, 20, 0], body)
        bx(arm, sx * 5, 11, -2.5, sx * 10, 22, 2.5, 'skin', decals={'north': G(['.....', '.....', '.....', '.ddd.'] + ['.....'] * 7, {'d': '#64a02a'})})
        fist = m.bone('fist_' + side, [sx * 7.5, 10, 0], arm)
        bx(fist, sx * 4.7, 7.5, -2.9, sx * 10.3, 12.5, 2.9, 'wrap', decals={'north': G(['......', 'd.d.d.', '......', '.d.d.d', '......'], {'d': '#c8c2b0'})})
    head = m.bone('head', [0, 22, 0], body)
    face = G(['ssssssss',
              'ssssssss',
              'skkkkkks',
              'sWEssEWs',
              'ssssssss',
              'ssssssss',
              'sdTTTTds',
              'ssddddss'], {'s': '#7cbf38', 'k': '#1e1a14', 'W': '#ffffff', 'E': '#3a2a10', 'd': '#3a1a12', 'T': '#f4f0e0'})
    bx(head, -4, 22, -4, 4, 30, 4, 'skin', decals={'north': face})
    bx(head, -1, 25, -5.5, 1, 27.5, -4, 'skin_d')                                    # big nose
    for sx, side in ((1, 'r'), (-1, 'l')):
        e = m.bone('ear_' + side, [sx * 4, 26, 0], head)
        bx(e, sx * 4, 25.5, -0.5, sx * 8, 27.5, 0.5, 'skin')
        bx(e, sx * 7, 27.5, -0.5, sx * 8, 29, 0.5, 'skin')
    bx(head, -1, 30, -1, 1, 31.5, 3, 'dark')                                         # small black top-knot
    m.hitbox(1.3, 2.4)
    m.head_scale = ('root', K, [0, 0, 0])                                            # whole rig x1.3 (texels stay 8 on the head)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.5, 0]], 2.0), 'rotation': [(0, [6, 0, 0]), (2.0, [6, 0, 0])]},
            'head': {'rotation': loop([[-6, 4, 0], [-4, -4, 0]], 2.0)},
            'arm_r': {'rotation': loop([[-24, 0, 6], [-28, 0, 8]], 1.0)}, 'arm_l': {'rotation': loop([[-28, 0, -8], [-24, 0, -6]], 1.0)},
            'ear_r': {'rotation': loop([[0, 0, 0], [0, 0, 8]], 1.0)}, 'ear_l': {'rotation': loop([[0, 0, -8], [0, 0, 0]], 1.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk_anim(m, 0.6, leg=30, arm=20, arm_base={'arm_r': [-20, 0, 6], 'arm_l': [-20, 0, -6]}, extra={
        'body': {'position': loop([[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0]], 0.6), 'rotation': loop([[10, 5, 0], [10, -5, 0]], 0.6)}})
    # attack 0.5 s: wind up the right fist, then a straight punch
    m.anim('attack', 0.5, 'once', {
        'arm_r': {'rotation': kf((0, [-24, 0, 6]), (0.15, [30, 0, 15]), (0.25, [-95, -10, 0]), (0.35, [-90, -10, 0]), (0.5, [-24, 0, 6]))},
        'arm_l': {'rotation': kf((0, [-28, 0, -8]), (0.15, [-60, 0, -10]), (0.25, [10, 0, -10]), (0.5, [-28, 0, -8]))},
        'body': {'rotation': kf((0, [6, 0, 0]), (0.15, [2, 25, 0]), (0.25, [14, -25, 0]), (0.35, [12, -20, 0]), (0.5, [6, 0, 0])),
                 'position': kf((0, [0, 0, 0]), (0.15, [0, 0, 1.5]), (0.25, [0, 0, -2.5]), (0.5, [0, 0, 0]))},
        'fist_r': {'scale': kf((0, [1, 1, 1]), (0.25, [1.15, 1.15, 1.15]), (0.35, [1, 1, 1]))}})
    common_tail(m)
    return m


# =================================================================== HEAL SPIRIT
def heal_spirit():
    m = new_model('clash_heal_spirit')
    m.mats_({
        'body': MC('#ffe04a', 'glow', n=0.05, e=0.88), 'body_d': MC('#f5c832', 'glow', n=0.05, e=0.88),
        'tongue': MC('#e8384a', None, n=0.05, e=0.8), 'cloth': MC('#efefef', None, n=0.03, e=0.85), 'tooth': MC('#ffffff', None, n=0.02, e=1.0),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 3, 0], root)
    face = G(['........',
              '........',
              '.kk..kk.',
              '.kk..kk.',
              '........',
              '.mmmmmm.',
              '.mwmmmm.',
              '.mmmmmm.',
              '..mmmm..',
              '........'], {'k': '#3a2408', 'm': '#7a2a12', 'w': '#ffffff'})
    bx(body, -4, 4, -3.5, 4, 14, 3.5, 'body', decals={'north': face})
    bx(body, -3, 2, -2.5, 3, 4, 2.5, 'body_d')                                    # tapering ghost tail
    bx(body, -1.5, 0.5, -0.5, 1.5, 2, 2.5, 'body_d')
    tg = m.bone('tongue', [1.5, 6.5, -3.5], body)
    bx(tg, 0.2, 5.4, -6, 2.8, 6.6, -3.4, 'tongue', decals={'up': G(['...', '.d.'] + ['.d.'] * 2, {'d': '#b82030'})})
    bx(tg, 0.2, 4.4, -6.2, 2.8, 5.6, -5, 'tongue')
    tcp = m.bone('tc_patch', [-2.5, 6, -3.5], body)
    bx(tcp, -3.8, 10.8, -3.8, -1.2, 13, -3.5, 'cloth')
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 4, 8, 0], body)
        bx(a, sx * 4, 6, -1, sx * 6, 9, 1, 'body_d')
    m.hitbox(0.7, 0.8)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 1, 0]], 1.0), 'rotation': loop([[0, 0, 2], [0, 0, -2]], 1.0)},
            'tongue': {'rotation': loop([[0, 0, 0], [10, 0, 0]], 0.5)},
            'arm_r': {'rotation': loop([[0, 0, 10], [0, 0, -10]], 0.5)}, 'arm_l': {'rotation': loop([[0, 0, -10], [0, 0, 10]], 0.5)}}
    m.anim('idle', 1.0, 'loop', idle)
    m.anim('walk', 0.4, 'loop', {
        'body': {'position': kf((0, [0, 0, 0]), (0.1, [0, 3, 0]), (0.2, [0, 4, 0]), (0.3, [0, 2, 0]), (0.4, [0, 0, 0])),
                 'scale': kf((0, [1.1, 0.9, 1.1]), (0.1, [0.95, 1.08, 0.95]), (0.3, [1, 1, 1]), (0.4, [1.1, 0.9, 1.1])),
                 'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.4, [0, 0, 0]))},
        'tongue': {'rotation': loop([[0, 0, 0], [20, 0, 0]], 0.2)},
        'arm_r': {'rotation': loop([[0, 0, 25], [0, 0, -10]], 0.2)}, 'arm_l': {'rotation': loop([[0, 0, -25], [0, 0, 10]], 0.2)}})
    m.anim('attack', 0.5, 'once', {
        'body': {'scale': kf((0, [1, 1, 1]), (0.12, [1.2, 0.8, 1.2]), (0.25, [0.9, 1.1, 0.9]), (0.35, [1.5, 1.5, 1.5]), (0.5, [1, 1, 1])),
                 'position': kf((0, [0, 0, 0]), (0.12, [0, -0.5, 1]), (0.25, [0, 6, -6]), (0.35, [0, 1, -9]), (0.5, [0, 0, 0])),
                 'rotation': kf((0, [0, 0, 0]), (0.12, [-10, 0, 0]), (0.25, [20, 0, 0]), (0.5, [0, 0, 0]))},
        'tongue': {'rotation': kf((0, [0, 0, 0]), (0.25, [30, 0, 0]), (0.5, [0, 0, 0]))}})
    m.anim('spawn', 0.5, 'once', {'root': {'scale': kf((0, [0.2, 0.2, 0.2]), (0.3, [1.15, 1.15, 1.15]), (0.5, [1, 1, 1])),
                                           'position': kf((0, [0, 10, 0]), (0.3, [0, 0, 0]), (0.5, [0, 0, 0]))}})
    m.anim('hit', 0.3, 'once', {'body': {'rotation': kf((0, [0, 0, 0]), (0.08, [12, 0, 0]), (0.3, [0, 0, 0])),
                                         'scale': kf((0, [1, 1, 1]), (0.08, [1.08, 0.92, 1.08]), (0.3, [1, 1, 1]))}})
    m.anim('death', 0.35, 'hold', {'root': {'scale': kf((0, [1, 1, 1]), (0.12, [1.5, 1.5, 1.5]), (0.35, [0.01, 0.01, 0.01]))}})
    return m


MODELS = [witch, night_witch, wizard, dart_goblin, goblin_brawler, heal_spirit]

if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    only = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    for fn in MODELS:
        if only and fn.__name__ not in only:
            continue
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        p = os.path.join(out, m.name + '.bbmodel')
        m.export(p)
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad, 'hitbox', getattr(m, 'hitbox_size', None),
              [(a['name'], a['length']) for a in m.anims])
