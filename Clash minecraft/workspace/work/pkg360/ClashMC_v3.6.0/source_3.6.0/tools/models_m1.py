"""New models (m1): witch / night witch / wizard / dart goblin / goblin brawler / heal spirit (bbgen2, BetterModel).
Units: pixels (16 = 1 block), front = north (-Z), origin = centre of the feet.
Animations: idle / walk / attack / spawn(->deploy) / hit / death (+ summon for the witches).
Original designs: role-readable, not based on any existing game's characters."""
import sys, os, json, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """box centred on (x, z), bottom at y"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    """evenly spaced keyframes (last = first)"""
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def kf(*pts):
    """kf((t, [x,y,z]), ...) -> list"""
    return [(t, list(v)) for t, v in pts]


def common_tail(m, root='root', hit_bone='body', death=None):
    """spawn / hit / death"""
    m.anim('spawn', 0.5, 'once', {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                         'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death or {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                                  'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})


def face(eye, pupil=None, white=None, sock=None, brow=None, mouth=None, y=0.4, h=0.18, x0=0.14, w=0.26, extra=()):
    """simple front face decal (fractions of the face)"""
    out = []
    for xa in (x0, 1 - x0 - w):
        if sock:
            out.append(('rect', xa - 0.04, y - 0.04, xa + w + 0.04, y + h + 0.04, sock))
        out.append(('rect', xa, y, xa + w, y + h, eye))
        if pupil:
            out.append(('rect', xa + w * 0.3, y + h * 0.25, xa + w * 0.7, y + h * 0.85, pupil))
        if white:
            out.append(('rect', xa + w * 0.15, y + h * 0.1, xa + w * 0.35, y + h * 0.4, white))
        if brow:
            out.append(('rect', xa - 0.03, y - 0.1, xa + w + 0.03, y - 0.04, brow))
    if mouth:
        out.append(mouth)
    return out + list(extra)


# =================================================================== WITCH
def witch():
    """Plain village witch: simple dark hooded cloak with a pointed hood, team band on the hood and a team sash,
    ordinary face, plain wooden staff with a small skull and a small green glow."""
    m = Model('clash_witch', density=1.5)
    m.mats_({
        'robe': ('#3f3846', 'cloth'), 'robe_d': ('#2e2934', 'cloth'),
        'cloth': ('#efefef', 'cloth'), 'skin': ('#e8c2a4', 'skin'), 'hair': ('#5a4a44', 'hair'),
        'wood': ('#6e4a2c', 'wood', {'grain': 'v'}), 'wood_d': ('#4e3420', 'wood'), 'bone': ('#e4dcc6', 'bone'),
        'orb': ('#7ee86a', 'glow'), 'boot': ('#2a2220', 'leather'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 2, 2, 0, 2.6, 9, 2.6, 'robe_d')
        cb(lg, sx * 2, 0, -0.6, 3, 2.6, 4.2, 'boot')
    body = m.bone('body', [0, 12, 0], root)
    seam = [('rect', 0.47, 0.0, 0.53, 1.0, '#2e2934')]
    cb(body, 0, 1.6, 0, 12, 6, 9, 'robe', decals={'north': seam})
    cb(body, 0, 7.6, 0.2, 10.2, 5, 7.6, 'robe', decals={'north': seam})
    cb(body, 0, 12.6, 0.2, 8.8, 2, 6.4, 'robe')
    cb(body, 0, 14.4, 0.2, 8, 7, 5.4, 'robe', decals={'north': seam})
    cb(body, 0, 19.8, 0.2, 10.0, 2.0, 6.4, 'robe_d')                            # plain cloak shoulders
    cb(body, 0, 3.0, 3.6, 9, 17.6, 1, 'robe_d')                                 # cloak back
    tc = m.bone('tc_sash', [0, 13, 0], body)
    cb(tc, 0, 13.0, 0.2, 9.2, 1.4, 6.8, 'cloth')                                # simple sash
    cb(tc, -2.6, 9.6, -3.7, 1.4, 3.6, 0.5, 'cloth')                             # sash end
    head = m.bone('head', [0, 22.5, 0], body)
    fd = face('#2a2018', pupil='#5a8a3a', brow='#4a3a32', y=0.42, h=0.16, x0=0.16, w=0.24,
              mouth=('rect', 0.38, 0.78, 0.62, 0.83, '#8a4a3a'),
              extra=[('rect', 0.0, 0.0, 1.0, 0.2, '#5a4a44'), ('rect', 0.46, 0.58, 0.54, 0.7, '#d6aa8a')])
    cb(head, 0, 22.5, -0.3, 7.4, 7.4, 7.4, 'skin', decals={'north': fd})
    cb(head, 0, 29.8, 0.4, 9.4, 1.6, 9.0, 'robe')
    for sx in (1, -1):
        cb(head, sx * 4.2, 21.6, 0.4, 1.2, 8.4, 9.0, 'robe')
        cb(head, sx * 3.3, 20.6, -3.9, 1.4, 6.0, 1.0, 'hair')                   # hair locks
    cb(head, 0, 21.6, 4.4, 9.4, 8.4, 1.2, 'robe')
    tch = m.bone('tc_hood', [0, 30, 0], head)
    cb(tch, 0, 30.4, -4.5, 9.8, 1.2, 1.0, 'cloth')                              # team band at the hood edge
    cb(head, 0, 31.2, 1.0, 7.0, 2.4, 7.0, 'robe')                               # plain pointed hood
    cb(head, 0, 33.4, 2.4, 4.6, 2.6, 4.6, 'robe', rot=('x', 22.5))
    cb(head, 0, 35.2, 4.4, 2.4, 2.2, 2.4, 'robe_d', rot=('x', 45))
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.4, 21, 0], body)
        cb(arm, sx * 5.6, 12.2, 0.2, 3.2, 9, 3.6, 'robe')
        cb(arm, sx * 5.6, 18.6, 0.2, 3.4, 2.6, 3.8, 'robe_d')
        cb(arm, sx * 5.6, 10.0, -0.3, 2.4, 2.2, 2.4, 'skin')
    staff = m.bone('staff', [5.6, 11, -0.3], m.by_name('arm_r'))
    cb(staff, 5.6, 1.0, -0.3, 1.3, 29.0, 1.3, 'wood')
    cb(staff, 5.6, 22.0, -0.3, 1.7, 1.0, 1.7, 'wood_d')                          # simple binding
    cb(staff, 5.6, 29.6, -0.3, 2.0, 1.0, 2.0, 'wood_d')
    sk = [('rect', 0.12, 0.3, 0.42, 0.62, '#2a2420'), ('rect', 0.58, 0.3, 0.88, 0.62, '#2a2420'),
          ('rect', 0.44, 0.66, 0.56, 0.76, '#5a5048'), ('rect', 0.26, 0.86, 0.74, 0.92, '#5a5048')]
    cb(staff, 5.6, 30.4, -0.3, 2.8, 2.6, 2.8, 'bone', decals={'north': sk})       # small skull
    orb = m.bone('orb', [5.6, 34.0, -0.3], staff)
    cb(orb, 5.6, 33.2, -0.3, 1.6, 1.6, 1.6, 'orb')                                # small green glow
    m.hitbox(0.9, 2.1)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [3, 0, 0], [0, -6, 0], [3, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([[-6, 0, 4], [-9, 0, 4]], 2.0)},
            'arm_l': {'rotation': loop([[-4, 0, -4], [-8, 0, -6]], 2.0)},
            'staff': {'rotation': loop([[6, 0, 0], [9, 0, 0]], 2.0)},
            'orb': {'scale': loop([[1, 1, 1], [1.15, 1.15, 1.15]], 1.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], 0.8)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], 0.8)},
            'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.8), 'rotation': loop([[4, 3, 0], [4, -3, 0]], 0.8)},
            'arm_l': {'rotation': loop([[18, 0, -4], [-18, 0, -4]], 0.8)},
            'arm_r': {'rotation': loop([[-14, 0, 4], [-4, 0, 4]], 0.8)},
            'staff': {'rotation': loop([[10, 0, 0], [4, 0, 0]], 0.8)}}
    m.anim('walk', 0.8, 'loop', walk)
    # attack 0.7 s: draw the staff back, then swing it forward and fire (glow flares)
    att = {'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.22, [25, 0, 8]), (0.34, [-62, 0, 0]), (0.5, [-50, 0, 0]), (0.7, [0, 0, 0]))},
           'staff': {'rotation': kf((0, [0, 0, 0]), (0.22, [-40, 0, 0]), (0.34, [128, 0, 0]), (0.5, [110, 0, 0]), (0.7, [0, 0, 0]))},
           'orb': {'scale': kf((0, [1, 1, 1]), (0.22, [1.2, 1.2, 1.2]), (0.34, [1.8, 1.8, 1.8]), (0.42, [0.8, 0.8, 0.8]), (0.7, [1, 1, 1]))},
           'body': {'rotation': kf((0, [0, 0, 0]), (0.22, [-8, 12, 0]), (0.34, [10, -8, 0]), (0.5, [6, -4, 0]), (0.7, [0, 0, 0]))},
           'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.22, [-30, 0, -20]), (0.34, [20, 0, -12]), (0.7, [0, 0, 0]))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.22, [-6, 0, 0]), (0.34, [6, 0, 0]), (0.7, [0, 0, 0]))}}
    m.anim('attack', 0.7, 'once', att)
    # summon 0.6 s: raise the staff high, glow brightens, thump it down
    m.anim('summon', 0.6, 'once', {
        'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.25, [-150, 0, 6]), (0.38, [-150, 0, 6]), (0.48, [-40, 0, 0]), (0.6, [0, 0, 0]))},
        'staff': {'rotation': kf((0, [0, 0, 0]), (0.25, [180, 0, 0]), (0.38, [180, 0, 0]), (0.48, [40, 0, 0]), (0.6, [0, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.25, [-40, 0, -50]), (0.45, [-40, 0, -50]), (0.6, [0, 0, 0]))},
        'orb': {'scale': kf((0, [1, 1, 1]), (0.25, [1.6, 1.6, 1.6]), (0.38, [2.0, 2.0, 2.0]), (0.48, [1, 1, 1]), (0.6, [1, 1, 1]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.25, [-10, 0, 0]), (0.48, [6, 0, 0]), (0.6, [0, 0, 0]))},
        'head': {'rotation': kf((0, [0, 0, 0]), (0.25, [-14, 0, 0]), (0.48, [4, 0, 0]), (0.6, [0, 0, 0]))}})
    common_tail(m)
    return m


# =================================================================== NIGHT WITCH
def night_witch():
    """Gothic bat-summoner: black and violet dress with ragged hem, bat-wing collar, horned hood,
    scythe staff with a crescent blade and a violet gem."""
    m = Model('clash_night_witch', density=1.5)
    m.mats_({
        'dress': ('#1d1724', 'cloth'), 'dress_d': ('#120e17', 'cloth'), 'violet': ('#4b2470', 'cloth'), 'violet_l': ('#6a35a0', 'cloth'),
        'cloth': ('#efefef', 'cloth'), 'skin': ('#ddd2ea', 'skin'), 'hair': ('#2a2036', 'hair'),
        'horn': ('#6a5878', 'bone'), 'horn_t': ('#e2d4f0', 'bone'), 'boot': ('#141016', 'leather'),
        'shaft': ('#2c2230', 'wood', {'grain': 'v'}), 'steel': ('#9da4b4', 'metal'), 'edge': ('#e2b8ff', 'glow'),
        'gem': ('#c055ff', 'glow'), 'gem_w': ('#f2d8ff', 'glow'), 'silver': ('#b8bcc8', 'metal'), 'wing': ('#2e1f40', 'leather', {'stitch': False}), 'wing_in': ('#5b2d8a', 'leather', {'stitch': False}),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 13, 0], root)
        cb(lg, sx * 2, 2, 0, 2.6, 10, 2.6, 'dress_d')
        cb(lg, sx * 2, 0, -0.4, 3, 3.4, 4, 'boot')
        cb(lg, sx * 2, 0, -3.0, 2.2, 1.4, 1.6, 'boot')
    body = m.bone('body', [0, 13, 0], root)
    panel = [('rect', 0.36, 0.0, 0.64, 1.0, '#4b2470'), ('rect', 0.36, 0.0, 0.4, 1.0, '#6a35a0'), ('rect', 0.6, 0.0, 0.64, 1.0, '#6a35a0')]
    cb(body, 0, 3.0, 0, 12.4, 6, 9.4, 'dress', decals={'north': panel, 'south': panel})
    cb(body, 0, 9.0, 0.2, 10.2, 5, 7.6, 'dress', decals={'north': panel})
    for i, x in enumerate((-5.4, -2.7, 0, 2.7, 5.4)):                          # ragged hem points
        for z in (-4.4, 4.4):
            cb(body, x, 1.2 + (i % 2) * 0.8, z, 2.0, 2.0, 0.8, 'dress_d' if i % 2 else 'violet')
    for z in (-2.4, 0.4, 3.0):
        for sx in (1, -1):
            cb(body, sx * 5.9, 1.4 + (0.8 if z > 0 else 0), z, 0.8, 2.0, 2.0, 'violet')
    # torso, corset, sash
    cb(body, 0, 14, 0.2, 8, 8, 5.4, 'dress', decals={'north': [('rect', 0.3, 0.1, 0.7, 0.9, '#4b2470'),
                                                                ('rect', 0.48, 0.1, 0.52, 0.9, '#b8bcc8'),
                                                                ('rect', 0.38, 0.3, 0.62, 0.34, '#b8bcc8'), ('rect', 0.38, 0.55, 0.62, 0.59, '#b8bcc8')]})
    tc = m.bone('tc_sash', [0, 14, 0], body)
    cb(tc, 0, 13.4, 0.2, 10.6, 1.8, 8.0, 'cloth')
    cb(tc, 2.6, 8.0, -4.2, 1.6, 5.6, 0.6, 'cloth')                             # sash tails
    cb(tc, 3.8, 9.0, -4.1, 1.4, 4.6, 0.6, 'cloth')
    cb(body, 2.4, 13.2, -4.3, 2.0, 2.0, 0.8, 'silver')                          # clasp
    cb(body, 0, 21, 0.2, 9.8, 1.6, 6.4, 'violet')                               # shoulders
    # bat-wing collar (rises behind the head, two scallops each side)
    for sx, side in ((1, 'r'), (-1, 'l')):
        col = m.bone('collar_' + side, [sx * 3, 22, 2.4], body)
        cb(col, sx * 5.4, 21.4, 2.8, 5.4, 8.0, 0.8, 'wing', rot=('z', -sx * 22.5), faces={'north': 'wing_in'})
        cb(col, sx * 8.6, 27.4, 2.8, 1.6, 5.0, 0.8, 'wing', rot=('z', -sx * 45), faces={'north': 'wing_in'})   # outer spike
        cb(col, sx * 5.4, 28.8, 2.8, 1.6, 4.0, 0.8, 'wing', rot=('z', -sx * 22.5), faces={'north': 'wing_in'})  # inner spike
        cb(col, sx * 9.4, 22.6, 2.8, 1.4, 3.6, 0.8, 'wing', rot=('z', -sx * 45))                                # lower scallop
        cb(col, sx * 6.9, 24.2, 2.3, 4.2, 0.8, 0.6, 'horn', rot=('z', -sx * 45))                                # wing rib
        tcc = m.bone('tc_collar_' + side, [sx * 4, 24, 2.3], col)
        cb(tcc, sx * 5.0, 21.8, 2.3, 3.4, 4.2, 0.3, 'cloth', rot=('z', -sx * 22.5))     # team lining
    # head
    head = m.bone('head', [0, 23, 0], body)
    fd = face('#d070ff', pupil='#fbeaff', brow='#2a2036', y=0.4, h=0.2, x0=0.1, w=0.32,
              mouth=('rect', 0.36, 0.78, 0.64, 0.84, '#5a1a50'),
              extra=[('rect', 0.0, 0.0, 1.0, 0.2, '#2a2036'), ('rect', 0.0, 0.0, 0.12, 0.4, '#2a2036'), ('rect', 0.88, 0.0, 1.0, 0.4, '#2a2036'),
                     ('rect', 0.46, 0.6, 0.54, 0.7, '#c0b6d0'), ('rect', 0.06, 0.36, 0.1, 0.4, '#2a2036'), ('rect', 0.9, 0.36, 0.94, 0.4, '#2a2036')])
    cb(head, 0, 23, -0.3, 7.2, 7.4, 7.2, 'skin', decals={'north': fd})
    cb(head, 0, 30.2, 0.4, 9.2, 1.6, 8.8, 'dress')
    for sx in (1, -1):
        cb(head, sx * 4.1, 22.2, 0.4, 1.2, 8.4, 8.8, 'dress')
        cb(head, sx * 3.2, 21.2, -3.8, 1.2, 6.8, 0.9, 'hair')
    cb(head, 0, 22.2, 4.4, 9.2, 8.4, 1.2, 'dress')
    cb(head, 0, 30.6, -4.4, 9.8, 1.4, 1.0, 'violet')                            # hood brim
    for sx in (1, -1):
        cb(head, sx * 4.5, 22.0, -4.4, 1.0, 9.0, 1.0, 'violet')
    cb(head, 0, 31.6, 1.2, 6.4, 1.6, 6.0, 'dress_d')
    for sx, side in ((1, 'r'), (-1, 'l')):                                    # curved horns
        h1 = m.bone('horn_' + side, [sx * 3.4, 31.6, -1.0], head)
        cb(h1, sx * 4.0, 30.8, -1.0, 2.4, 3.6, 2.4, 'horn', rot=('z', -sx * 22.5))
        cb(h1, sx * 5.2, 33.6, -0.4, 2.0, 3.4, 2.0, 'horn', rot=('z', -sx * 22.5))
        cb(h1, sx * 6.0, 36.4, 0.6, 1.5, 2.8, 1.5, 'horn', rot=('x', 22.5))
        cb(h1, sx * 6.1, 38.6, 2.0, 1.0, 2.0, 1.0, 'horn_t', rot=('x', 45))
    # arms
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.4, 21.5, 0], body)
        cb(arm, sx * 5.6, 15, 0.2, 2.8, 7, 3.2, 'dress')
        cb(arm, sx * 5.6, 19.2, 0.2, 3.4, 2.8, 3.8, 'violet')
        cb(arm, sx * 5.9, 12.6, 0.2, 3.8, 2.6, 4.0, 'violet', rot=('z', -sx * 22.5))   # flared cuff
        cb(arm, sx * 5.6, 10.4, -0.3, 2.2, 2.2, 2.2, 'skin')
    # scythe staff in right hand
    staff = m.bone('staff', [5.6, 11.4, -0.3], m.by_name('arm_r'))
    sx0, z0 = 5.6, -0.3
    cb(staff, sx0, 0.4, z0, 1.4, 36.6, 1.4, 'shaft')
    for y in (8.5, 13.8, 30.5):
        cb(staff, sx0, y, z0, 1.9, 0.9, 1.9, 'silver')
    cb(staff, sx0, -0.6, z0, 1.0, 1.4, 1.0, 'silver')
    cb(staff, sx0, 36.6, z0, 2.6, 2.4, 2.6, 'silver')                           # blade socket
    # crescent blade: arc from the top of the shaft curving forward and down
    # crescent blade in the x-y plane (faces the viewer): from the top of the shaft it curves outward and down
    cx_, cy, R = sx0, 31.6, 7.0
    segs = [(12, 'x', -22.5, 3.2), (42, 'x', -45, 3.0), (72, 'y', 22.5, 2.6), (102, 'y', -22.5, 2.2), (130, 'y', -45, 1.6)]
    blade = m.bone('blade', [sx0, 37, z0], staff)
    for k, (th, ax, rr, wdt) in enumerate(segs):
        t = math.radians(th)
        x, y = cx_ + R * math.sin(t), cy + R * math.cos(t)
        L = 3.4 if k < 4 else 3.0
        if ax == 'x':
            blade.box([x - L / 2, y - wdt / 2, z0 - 0.45], [x + L / 2, y + wdt / 2, z0 + 0.45], 'steel', rot=('z', rr))
        else:
            blade.box([x - wdt / 2, y - L / 2, z0 - 0.45], [x + wdt / 2, y + L / 2, z0 + 0.45], 'steel', rot=('z', rr))
        r2 = R - wdt / 2 - 0.3                                                  # glowing inner (cutting) edge
        x2, y2 = cx_ + r2 * math.sin(t), cy + r2 * math.cos(t)
        if ax == 'x':
            blade.box([x2 - L / 2, y2 - 0.35, z0 - 0.55], [x2 + L / 2, y2 + 0.35, z0 + 0.55], 'edge', rot=('z', rr))
        else:
            blade.box([x2 - 0.35, y2 - L / 2, z0 - 0.55], [x2 + 0.35, y2 + L / 2, z0 + 0.55], 'edge', rot=('z', rr))
    gem = m.bone('gem', [sx0, 38, z0], staff)
    cb(gem, sx0, 36.8, z0 - 1.5, 1.8, 1.8, 1.0, 'gem')
    cb(gem, sx0, 39.0, z0, 1.6, 1.6, 1.6, 'gem')
    cb(gem, sx0, 39.4, z0, 0.8, 0.8, 0.8, 'gem_w')
    m.hitbox(1.0, 2.2)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
            'head': {'rotation': loop([[0, 7, 0], [2, 0, 0], [0, -7, 0], [2, 0, 0]], 2.0)},
            'collar_r': {'rotation': loop([[0, 0, 0], [0, -6, 4]], 1.0)}, 'collar_l': {'rotation': loop([[0, 0, 0], [0, 6, -4]], 1.0)},
            'arm_r': {'rotation': loop([[-8, 0, 4], [-11, 0, 4]], 2.0)}, 'staff': {'rotation': loop([[8, 0, 0], [11, 0, 0]], 2.0)},
            'arm_l': {'rotation': loop([[-6, 0, -8], [-10, 0, -12]], 2.0)},
            'gem': {'scale': loop([[1, 1, 1], [1.3, 1.3, 1.3]], 1.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], 0.8)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], 0.8)},
            'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.8), 'rotation': loop([[4, 3, 0], [4, -3, 0]], 0.8)},
            'arm_l': {'rotation': loop([[18, 0, -6], [-18, 0, -6]], 0.8)},
            'arm_r': {'rotation': loop([[-12, 0, 4], [-4, 0, 4]], 0.8)}, 'staff': {'rotation': loop([[12, 0, 0], [4, 0, 0]], 0.8)},
            'collar_r': {'rotation': loop([[0, 0, 0], [0, -8, 6]], 0.4)}, 'collar_l': {'rotation': loop([[0, 0, 0], [0, 8, -6]], 0.4)}}
    m.anim('walk', 0.8, 'loop', walk)
    # attack 0.8 s: raise the scythe up and back, then sweep the blade down across the front
    att = {'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.28, [-30, 0, 50]), (0.42, [-55, 0, -10]), (0.55, [-45, 0, -20]), (0.8, [0, 0, 0]))},
           'staff': {'rotation': kf((0, [0, 0, 0]), (0.28, [0, 0, -105]), (0.42, [0, 0, 105]), (0.55, [0, 0, 115]), (0.8, [0, 0, 0]))},
           'body': {'rotation': kf((0, [0, 0, 0]), (0.28, [-6, 15, 0]), (0.42, [8, -18, 0]), (0.55, [8, -24, 0]), (0.8, [0, 0, 0]))},
           'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.28, [-20, 0, -40]), (0.45, [20, 0, -20]), (0.8, [0, 0, 0]))},
           'gem': {'scale': kf((0, [1, 1, 1]), (0.28, [1.6, 1.6, 1.6]), (0.42, [2.0, 2.0, 2.0]), (0.8, [1, 1, 1]))},
           'collar_r': {'rotation': kf((0, [0, 0, 0]), (0.42, [0, -10, 8]), (0.8, [0, 0, 0]))},
           'collar_l': {'rotation': kf((0, [0, 0, 0]), (0.42, [0, 10, -8]), (0.8, [0, 0, 0]))}}
    m.anim('attack', 0.8, 'once', att)
    m.anim('summon', 0.6, 'once', {
        'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.25, [-150, 0, 8]), (0.4, [-150, 0, 8]), (0.5, [-40, 0, 0]), (0.6, [0, 0, 0]))},
        'staff': {'rotation': kf((0, [0, 0, 0]), (0.25, [180, 0, 0]), (0.4, [180, 0, 0]), (0.5, [40, 0, 0]), (0.6, [0, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.25, [-30, 0, -70]), (0.45, [-30, 0, -70]), (0.6, [0, 0, 0]))},
        'collar_r': {'rotation': kf((0, [0, 0, 0]), (0.25, [0, -20, 20]), (0.45, [0, -20, 20]), (0.6, [0, 0, 0]))},
        'collar_l': {'rotation': kf((0, [0, 0, 0]), (0.25, [0, 20, -20]), (0.45, [0, 20, -20]), (0.6, [0, 0, 0]))},
        'gem': {'scale': kf((0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.4, [2.8, 2.8, 2.8]), (0.5, [1, 1, 1]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.25, [-10, 0, 0]), (0.5, [6, 0, 0]), (0.6, [0, 0, 0]))},
        'head': {'rotation': kf((0, [0, 0, 0]), (0.25, [-14, 0, 0]), (0.5, [4, 0, 0]), (0.6, [0, 0, 0]))}})
    common_tail(m)
    return m


# =================================================================== WIZARD
def wizard():
    """Plain apprentice wizard: muted blue-grey robe with a simple cloth hood (team band on the hood edge),
    rope belt, short beard, a small flame in each hand."""
    m = Model('clash_wizard', density=1.5)
    m.mats_({
        'robe': ('#5a6678', 'cloth'), 'robe_d': ('#454f5e', 'cloth'),
        'cloth': ('#efefef', 'cloth'), 'skin': ('#e6b48c', 'skin'), 'beard': ('#6b4a32', 'hair'),
        'boot': ('#4a3424', 'leather'), 'rope': ('#b39a6a', 'rope'),
        'fire': ('#ff8a2a', 'glow'), 'fire_y': ('#ffd25a', 'glow'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 2, 2, 0, 2.8, 9, 2.8, 'robe_d')
        cb(lg, sx * 2, 0, -0.6, 3.2, 2.8, 4.4, 'boot')
    body = m.bone('body', [0, 12, 0], root)
    seam = [('rect', 0.47, 0.0, 0.53, 1.0, '#454f5e')]
    cb(body, 0, 2.0, 0, 11.4, 5.6, 8.4, 'robe', decals={'north': seam})
    cb(body, 0, 7.6, 0.2, 10, 5, 7.4, 'robe', decals={'north': seam})
    cb(body, 0, 12.6, 0.2, 8.6, 2, 6.2, 'robe')
    cb(body, 0, 14.4, 0.2, 8, 7, 5.4, 'robe', decals={'north': seam})
    cb(body, 0, 13.0, 0.2, 9.0, 1.0, 6.6, 'rope')                                # rope belt
    cb(body, -2.4, 12.6, -3.5, 1.4, 1.4, 0.8, 'rope')                            # knot
    for dx in (-2.0, -2.8):
        cb(body, dx, 8.4, -3.5, 0.6, 4.4, 0.6, 'rope')                            # hanging ends
    # hood + short shoulder cape (one piece of cloth)
    cb(body, 0, 19.4, 0.4, 10.4, 2.6, 7.0, 'robe_d')
    head = m.bone('head', [0, 22, 0], body)
    fd = face('#2a1e16', brow='#5a3a24', y=0.4, h=0.14, x0=0.18, w=0.2,
              mouth=('rect', 0.38, 0.82, 0.62, 0.87, '#3a2016'),
              extra=[('rect', 0.45, 0.5, 0.55, 0.66, '#d39a72'), ('rect', 0.12, 0.7, 0.88, 1.0, '#6b4a32'),
                     ('rect', 0.3, 0.64, 0.7, 0.72, '#6b4a32'), ('rect', 0.38, 0.8, 0.62, 0.88, '#3a2016')])
    cb(head, 0, 22, -0.2, 7.2, 7.2, 7.2, 'skin', decals={'north': fd})
    cb(head, 0, 20.6, -2.4, 4.6, 1.8, 3.0, 'beard')                               # short beard
    hood = m.bone('hood', [0, 26, 0], head)
    cb(hood, 0, 29.2, 0.3, 9.2, 1.6, 8.8, 'robe')
    for sx in (1, -1):
        cb(hood, sx * 4.1, 21.4, 0.3, 1.2, 8.0, 8.8, 'robe')
    cb(hood, 0, 21.4, 4.2, 9.2, 8.0, 1.2, 'robe')
    cb(hood, 0, 29.8, 2.6, 6.4, 1.4, 4.4, 'robe')                                 # soft rounded crown
    cb(hood, 0, 21.0, 5.0, 6.0, 4.0, 1.0, 'robe_d')                               # fold hanging at the back
    tch = m.bone('tc_hood', [0, 26, -4.2], hood)
    cb(tch, 0, 29.6, -4.3, 9.6, 1.2, 1.0, 'cloth')
    for sx in (1, -1):
        cb(tch, sx * 4.3, 21.2, -4.3, 1.0, 8.4, 1.0, 'cloth')
    # arms + small hand flames
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.4, 21, 0], body)
        cb(arm, sx * 5.6, 12.0, 0.2, 3.0, 9.4, 3.4, 'robe')
        cb(arm, sx * 5.6, 10.2, -0.2, 2.4, 2.2, 2.4, 'skin')
        fx, fy, fz = sx * 5.5, 8.6, -2.2
        fl = m.bone('flame_' + side, [fx, fy, fz], arm)
        cb(fl, fx, fy - 0.8, fz, 1.6, 1.6, 1.6, 'fire')
        cb(fl, fx, fy + 0.8, fz, 0.9, 1.1, 0.9, 'fire_y')
    m.hitbox(0.9, 2.1)

    hold = lambda s, a=0: [-38 + a, 0, s * 8]
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [2, 0, 0], [0, -6, 0], [2, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([hold(1), hold(1, -6)], 2.0)}, 'arm_l': {'rotation': loop([hold(-1, -6), hold(-1)], 2.0)},
            'flame_r': {'scale': loop([[1, 1, 1], [1.1, 1.2, 1.1]], 0.5), 'rotation': loop([[38, 0, 0], [44, 0, 0]], 2.0)},
            'flame_l': {'scale': loop([[1.1, 1.2, 1.1], [1, 1, 1]], 0.5), 'rotation': loop([[44, 0, 0], [38, 0, 0]], 2.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], 0.8)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], 0.8)},
            'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.8), 'rotation': loop([[4, 3, 0], [4, -3, 0]], 0.8)},
            'arm_r': {'rotation': loop([hold(1, 10), hold(1, -10)], 0.8)}, 'arm_l': {'rotation': loop([hold(-1, -10), hold(-1, 10)], 0.8)},
            'flame_r': {'rotation': loop([[28, 0, 0], [48, 0, 0]], 0.8)}, 'flame_l': {'rotation': loop([[48, 0, 0], [28, 0, 0]], 0.8)}}
    m.anim('walk', 0.8, 'loop', walk)
    # attack 0.6 s: pull both hands back, then thrust both forward and throw the fireball
    att = {}
    for side, s in (('r', 1), ('l', -1)):
        att['arm_' + side] = {'rotation': kf((0, hold(s)), (0.2, [-10, 0, s * 4]), (0.3, [-92, 0, -s * 8]), (0.42, [-82, 0, -s * 6]), (0.6, hold(s)))}
        att['flame_' + side] = {'scale': kf((0, [1, 1, 1]), (0.2, [1.3, 1.3, 1.3]), (0.3, [1.8, 1.8, 1.8]), (0.36, [0.5, 0.5, 0.5]), (0.6, [1, 1, 1])),
                                'rotation': kf((0, [38, 0, 0]), (0.2, [10, 0, 0]), (0.3, [92, 0, 0]), (0.42, [82, 0, 0]), (0.6, [38, 0, 0]))}
    att['body'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-9, 0, 0]), (0.3, [10, 0, 0]), (0.42, [6, 0, 0]), (0.6, [0, 0, 0])),
                   'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 1]), (0.3, [0, 0, -1.5]), (0.6, [0, 0, 0]))}
    att['head'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-6, 0, 0]), (0.3, [4, 0, 0]), (0.6, [0, 0, 0]))}
    m.anim('attack', 0.6, 'once', att)
    common_tail(m)
    return m


# =================================================================== DART GOBLIN
def dart_goblin():
    """Small fast goblin: bark mask with painted stripes, leaf crest, team scarf, long blowpipe held at the mouth,
    dart quiver on the back."""
    m = Model('clash_dart_goblin', density=2.0)
    m.mats_({
        'skin': ('#7cc63a', 'skin'), 'skin_d': ('#5ea42a', 'skin'), 'bark': ('#8a5a32', 'wood'), 'bark_d': ('#5e3a1e', 'wood'),
        'leaf': ('#3f8f2a', 'plain'), 'leaf_l': ('#5cb83a', 'plain'), 'cloth': ('#efefef', 'cloth'), 'hide': ('#7a5230', 'leather', {'stitch': False}),
        'pipe': ('#b08a50', 'wood', {'grain': 'v'}), 'band': ('#4a3020', 'leather', {'stitch': False}), 'dart': ('#e8e0c8', 'bone'),
        'feather': ('#ffd04a', 'plain'), 'nail': ('#e8e0c8', 'bone'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.6, 5, 0], root)
        cb(lg, sx * 1.6, 1, 0, 1.9, 4.4, 2.0, 'skin_d')
        cb(lg, sx * 1.6, 0, -0.7, 2.4, 1.2, 3.4, 'skin')                          # big bare feet
        cb(lg, sx * 1.6, 0.9, -0.1, 2.2, 0.8, 2.3, 'hide')                         # ankle wrap
    body = m.bone('body', [0, 5, 0], root)
    cb(body, 0, 4.2, 0, 5.6, 2.6, 3.8, 'hide', decals={'north': [('rect', 0.3, 0.5, 0.7, 1.0, '#5e3a1e')]})       # loincloth
    cb(body, 0, 2.6, -1.8, 2.6, 2.0, 0.5, 'leaf')                                # front flap leaf
    cb(body, 0, 6.6, 0, 5.2, 4.2, 3.4, 'skin', decals={'north': [('rect', 0.2, 0.2, 0.42, 0.24, '#5ea42a'), ('rect', 0.58, 0.2, 0.8, 0.24, '#5ea42a'),
                                                                   ('rect', 0.48, 0.3, 0.52, 0.9, '#5ea42a')]})
    cb(body, 0.0, 6.6, -1.8, 1.0, 4.2, 0.4, 'band', rot=('z', 45))                 # quiver strap
    q = m.bone('quiver', [0, 8, 2], body)
    cb(q, -1.0, 6.4, 2.4, 1.8, 5.0, 1.6, 'bark', rot=('z', -22.5))
    for dx in (-0.4, 0.4):
        cb(q, -2.2 + dx, 11.0, 2.4, 0.5, 1.2, 0.5, 'feather', rot=('z', -22.5))
    tc = m.bone('tc_scarf', [0, 10.6, 0], body)
    cb(tc, 0, 9.7, 0, 6.6, 2.0, 4.6, 'cloth')
    cb(tc, -1.6, 8.6, -2.5, 1.8, 1.6, 0.8, 'cloth')                               # knot
    cb(tc, -1.9, 6.6, -2.5, 1.3, 2.4, 0.5, 'cloth', rot=('z', -22.5))            # front end
    tail = m.bone('tc_scarf_tail', [1.4, 10.6, 2.0], tc)
    cb(tail, 1.6, 6.8, 2.5, 1.8, 3.8, 0.5, 'cloth')
    cb(tail, 3.0, 7.6, 2.5, 1.4, 3.0, 0.5, 'cloth')
    for sx in (1, -1):
        cb(body, sx * 3.2, 9.9, 0, 2.6, 0.8, 3.6, 'leaf_l', rot=('z', -sx * 22.5))   # leaf shoulder pads
    # head
    head = m.bone('head', [0, 11, 0], body)
    cb(head, 0, 11, 0.2, 6.6, 5.6, 5.6, 'skin', decals={'south': [('rect', 0.2, 0.0, 0.8, 0.2, '#3f8f2a')]})
    mask = [('rect', 0.1, 0.3, 0.38, 0.52, '#1a120a'), ('rect', 0.62, 0.3, 0.9, 0.52, '#1a120a'),
            ('rect', 0.18, 0.36, 0.32, 0.48, '#ffe04a'), ('rect', 0.68, 0.36, 0.82, 0.48, '#ffe04a'),
            ('rect', 0.05, 0.12, 0.95, 0.2, '#e8e0c8'), ('rect', 0.15, 0.6, 0.3, 0.66, '#e8e0c8'), ('rect', 0.7, 0.6, 0.85, 0.66, '#e8e0c8'),
            ('rect', 0.4, 0.62, 0.6, 0.95, '#3a2412')]
    cb(head, 0, 11.4, -2.9, 6.4, 5.4, 0.9, 'bark', decals={'north': mask})
    cb(head, 0, 13.2, -3.6, 1.2, 1.6, 0.6, 'bark_d')                              # mask nose ridge
    for sx, side in ((1, 'r'), (-1, 'l')):                                       # long ears
        e = m.bone('ear_' + side, [sx * 3.2, 14, 0.4], head)
        cb(e, sx * 4.6, 13.4, 0.4, 3.2, 1.6, 1.2, 'skin', rot=('z', sx * 22.5))
        cb(e, sx * 6.6, 14.6, 0.4, 2.2, 1.0, 0.9, 'skin_d', rot=('z', sx * 45))
    crest = m.bone('crest', [0, 16.6, 0], head)                                  # leaf crest
    for (x, z, h, ax, r, mat) in ((0, -1.2, 3.4, 'x', -22.5, 'leaf_l'), (-1.6, 0.2, 3.0, 'z', 22.5, 'leaf'), (1.6, 0.2, 3.0, 'z', -22.5, 'leaf'),
                                  (0, 1.6, 3.0, 'x', 22.5, 'leaf'), (-0.8, 2.6, 2.4, 'x', 45, 'leaf_l'), (0.9, 2.6, 2.4, 'x', 45, 'leaf_l')):
        cb(crest, x, 16.2, z, 1.6, h, 0.6, mat, rot=(ax, r))
    # blowpipe at the mouth, held with both hands
    pipe = m.bone('pipe', [0, 12.4, -3.4], body)
    cb(pipe, 0, 11.8, -9.4, 1.2, 1.2, 12, 'pipe')
    cb(pipe, 0, 11.6, -4.2, 1.7, 1.6, 1.6, 'band')                                # mouthpiece
    for z in (-8.0, -12.2):
        cb(pipe, 0, 11.65, z, 1.5, 1.5, 0.8, 'band')
    cb(pipe, 0, 11.6, -15.2, 1.7, 1.6, 1.0, 'bark_d')
    mz = m.bone('muzzle', [0, 12.4, -15.8], pipe)
    cb(mz, 0, 12.0, -16.0, 0.8, 0.8, 0.8, 'dart')
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 3.2, 10.2, -0.2], body)
        hz = -6.0 if sx > 0 else -9.6
        cb(arm, sx * 3.2, 8.8, -0.8, 1.7, 2.0, 2.4, 'skin')                       # shoulder
        cb(arm, sx * 2.5, 9.8, (hz - 1.6) / 2 - 0.4, 1.5, 1.5, abs(hz) - 1.0, 'skin_d')   # forearm reaching forward
        cb(arm, sx * 1.0, 11.0, hz, 1.9, 1.9, 1.9, 'skin')                       # hand on the pipe
    m.hitbox(0.7, 1.2)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 1.0)},
            'head': {'rotation': loop([[0, 0, 0], [-3, 0, 0]], 1.0)},
            'ear_r': {'rotation': loop([[0, 0, 0], [0, 0, 8], [0, 0, 0], [0, 0, 0]], 1.0)},
            'ear_l': {'rotation': loop([[0, 0, 0], [0, 0, 0], [0, 0, -8], [0, 0, 0]], 1.0)},
            'crest': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 1.0)},
            'tc_scarf_tail': {'rotation': loop([[10, 0, 0], [20, 0, 6]], 1.0)},
            'pipe': {'rotation': loop([[0, 0, 0], [-2, 0, 0]], 1.0)}}
    m.anim('idle', 1.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[38, 0, 0], [-38, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[-38, 0, 0], [38, 0, 0]], 0.4)},
            'body': {'position': loop([[0, 0, 0], [0, 1.0, 0], [0, 0, 0], [0, 1.0, 0]], 0.4), 'rotation': loop([[10, 4, 0], [10, -4, 0]], 0.4)},
            'ear_r': {'rotation': loop([[0, 0, 10], [0, 0, -6]], 0.2)}, 'ear_l': {'rotation': loop([[0, 0, -10], [0, 0, 6]], 0.2)},
            'tc_scarf_tail': {'rotation': loop([[45, 0, 10], [60, 0, -10]], 0.2)}}
    m.anim('walk', 0.4, 'loop', walk)
    # attack 0.3 s: quick inhale (cheeks puff), then a sharp blow — pipe kicks, dart tip flares
    att = {'head': {'scale': kf((0, [1, 1, 1]), (0.08, [1.12, 1.04, 1.06]), (0.12, [0.96, 1, 1]), (0.3, [1, 1, 1])),
                    'rotation': kf((0, [0, 0, 0]), (0.08, [-5, 0, 0]), (0.12, [4, 0, 0]), (0.3, [0, 0, 0]))},
           'body': {'position': kf((0, [0, 0, 0]), (0.08, [0, 0, 0.8]), (0.12, [0, 0, -0.8]), (0.3, [0, 0, 0])),
                    'rotation': kf((0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.12, [5, 0, 0]), (0.3, [0, 0, 0]))},
           'pipe': {'position': kf((0, [0, 0, 0]), (0.08, [0, 0, 0.6]), (0.12, [0, 0, -1.4]), (0.3, [0, 0, 0]))},
           'muzzle': {'scale': kf((0, [1, 1, 1]), (0.1, [1, 1, 1]), (0.14, [3.0, 3.0, 3.0]), (0.22, [0.5, 0.5, 0.5]), (0.3, [1, 1, 1]))},
           'ear_r': {'rotation': kf((0, [0, 0, 0]), (0.12, [0, 0, 14]), (0.3, [0, 0, 0]))},
           'ear_l': {'rotation': kf((0, [0, 0, 0]), (0.12, [0, 0, -14]), (0.3, [0, 0, 0]))}}
    m.anim('attack', 0.3, 'once', att)
    common_tail(m)
    return m


# =================================================================== GOBLIN BRAWLER
def goblin_brawler():
    """Hulking muscular goblin fighter (1.5x, bigger than a person): huge wrapped fists, team shorts, heavy belt with gold buckle,
    mohawk, tusks, scars."""
    m = Model('clash_goblin_brawler', density=1.5)
    m.mats_({
        'skin': ('#78c03a', 'skin'), 'skin_d': ('#5c9e2a', 'skin'), 'skin_l': ('#92d655', 'skin'),
        'cloth': ('#efefef', 'cloth'), 'wrap': ('#e9dcc0', 'cloth'), 'belt': ('#3a2618', 'leather'), 'gold': ('#e8b23a', 'metal'),
        'hair': ('#2a1e16', 'hair'), 'tooth': ('#f2ead2', 'bone'), 'nail': ('#cfc6aa', 'bone'),
    })
    wrapd = [('rect', 0.0, 0.2, 1.0, 0.28, '#b9a888'), ('rect', 0.0, 0.55, 1.0, 0.63, '#b9a888'), ('rect', 0.0, 0.85, 1.0, 0.92, '#b9a888')]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.8, 7, 0], root)
        cb(lg, sx * 2.8, 1.0, 0, 3.4, 6.0, 3.6, 'skin_d')
        cb(lg, sx * 2.8, 0, -0.9, 4.2, 1.6, 5.2, 'skin')
        cb(lg, sx * 2.8, 1.4, 0, 3.8, 1.4, 4.0, 'wrap')                           # ankle wrap
        tl = m.bone('tc_shorts_' + side, [sx * 2.8, 7, 0], lg)
        cb(tl, sx * 2.9, 4.4, 0, 4.2, 3.0, 4.4, 'cloth')
    body = m.bone('body', [0, 8, 0], root)
    tcs = m.bone('tc_shorts', [0, 8, 0], body)
    cb(tcs, 0, 6.0, 0, 9.6, 3.4, 6.0, 'cloth', decals={'north': [('rect', 0.46, 0.2, 0.54, 1.0, '#c8c8c8')]})
    cb(body, 0, 9.0, 0, 10.0, 2.0, 6.6, 'belt')
    cb(body, 0, 8.6, -3.4, 3.6, 2.8, 0.8, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#b07818')]})
    cb(body, 0, 10.8, 0, 9.6, 3.2, 6.2, 'skin', decals={'north': [('rect', 0.3, 0.2, 0.7, 0.26, '#5c9e2a'), ('rect', 0.3, 0.6, 0.7, 0.66, '#5c9e2a'),
                                                                    ('rect', 0.48, 0.0, 0.52, 1.0, '#5c9e2a')]})          # abs
    chest = [('rect', 0.1, 0.62, 0.48, 0.7, '#5c9e2a'), ('rect', 0.52, 0.62, 0.9, 0.7, '#5c9e2a'), ('rect', 0.48, 0.1, 0.52, 0.7, '#5c9e2a'),
             ('rect', 0.15, 0.2, 0.3, 0.26, '#92d655'), ('rect', 0.65, 0.2, 0.8, 0.26, '#92d655'),
             ('rect', 0.62, 0.3, 0.66, 0.55, '#c0e090'), ('rect', 0.7, 0.32, 0.74, 0.5, '#c0e090')]                 # pecs + scar
    cb(body, 0, 13.8, 0.2, 12.2, 5.2, 7.4, 'skin', decals={'north': chest})
    cb(body, 0, 18.6, 1.0, 9.0, 1.8, 5.2, 'skin_d')                               # traps
    # head (hunched forward)
    head = m.bone('head', [0, 19, -1.6], body)
    fd = face('#ffe04a', pupil='#1a1a10', sock='#3a6a1a', y=0.3, h=0.18, x0=0.12, w=0.3,
              extra=[('rect', 0.06, 0.18, 0.44, 0.26, '#2a4a12'), ('rect', 0.56, 0.18, 0.94, 0.26, '#2a4a12'),
                     ('rect', 0.4, 0.46, 0.6, 0.64, '#5c9e2a'), ('rect', 0.2, 0.74, 0.8, 0.84, '#2a1a10'),
                     ('rect', 0.22, 0.64, 0.3, 0.76, '#f2ead2'), ('rect', 0.7, 0.64, 0.78, 0.76, '#f2ead2'),
                     ('rect', 0.12, 0.05, 0.16, 0.24, '#c0e090')])
    cb(head, 0, 17.4, -2.6, 7.0, 6.2, 6.0, 'skin', decals={'north': fd})
    cb(head, 0, 16.6, -4.4, 5.6, 1.6, 2.6, 'skin_d')                               # jaw
    for sx in (1, -1):
        cb(head, sx * 1.8, 17.8, -5.6, 0.9, 1.6, 0.8, 'tooth')                     # tusks
    cb(head, 0, 19.6, -5.9, 1.8, 1.8, 1.0, 'skin_l')                               # nose
    cb(head, 0, 23.4, -2.2, 1.6, 2.0, 6.4, 'hair')                                  # mohawk
    cb(head, 0, 24.6, -1.6, 1.2, 1.4, 4.0, 'hair')
    for sx, side in ((1, 'r'), (-1, 'l')):
        e = m.bone('ear_' + side, [sx * 3.4, 21, -2.2], head)
        cb(e, sx * 5.4, 20.0, -2.2, 4.4, 2.4, 1.2, 'skin', rot=('z', sx * 22.5))
        cb(e, sx * 8.0, 21.6, -2.2, 2.6, 1.6, 1.0, 'skin_d', rot=('z', sx * 45))
    cb(head, -4.6, 19, -2.2, 0.8, 1.4, 0.8, 'gold')                              # earring
    # arms with big wrapped fists
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 7.2, 17.4, 0.4], body)
        cb(arm, sx * 7.6, 13.4, 0.4, 4.6, 5.2, 4.8, 'skin', decals={'north': [('rect', 0.2, 0.3, 0.8, 0.36, '#5c9e2a')]})
        cb(arm, sx * 8.0, 9.4, 0.2, 4.0, 4.4, 4.2, 'skin_d')
        fist = m.bone('fist_' + side, [sx * 8.2, 9.0, 0], arm)
        cb(fist, sx * 8.2, 4.4, -0.2, 5.4, 5.0, 5.4, 'wrap', decals={f: wrapd for f in ('north', 'south', 'east', 'west')})
        kn = [('rect', 0.24, 0.0, 0.28, 1.0, '#3a6a1a'), ('rect', 0.49, 0.0, 0.53, 1.0, '#3a6a1a'), ('rect', 0.74, 0.0, 0.78, 1.0, '#3a6a1a')]
        cb(fist, sx * 8.2, 3.6, -0.6, 4.8, 0.8, 4.0, 'skin', decals={'down': kn})                      # knuckles (face forward when punching)
        cb(fist, sx * 8.2, 4.4, -2.9, 4.0, 2.4, 0.6, 'skin_d')
        tcw = m.bone('tc_wrist_' + side, [sx * 8.2, 9.0, 0], fist)
        cb(tcw, sx * 8.2, 8.4, -0.2, 4.7, 1.4, 4.7, 'cloth')
    # hulking scale: whole body x1.5, then exaggerate (smaller head, bigger forearms and fists, stubbier legs)
    m.scale_bone('root', 1.5, [0, 0, 0])
    hb = m.by_name('head')
    m.scale_bone('head', 0.82, hb.origin)
    for sd in ('r', 'l'):
        m.scale_bone('fist_' + sd, 1.18, m.by_name('fist_' + sd).origin)
    m.hitbox(1.3, 2.4)

    g_r, g_l = [-48, 0, -12], [-58, 0, 12]                                         # guard pose
    idle = {'body': {'position': loop([[0, 0, 0], [0, -0.9, 0]], 0.6), 'rotation': loop([[4, 0, 0], [6, 0, 0]], 0.6)},
            'arm_r': {'rotation': loop([g_r, [-54, 0, -12]], 0.6)}, 'arm_l': {'rotation': loop([g_l, [-52, 0, 12]], 0.6)},
            'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 2.4)},
            'leg_r': {'rotation': loop([[0, 0, 0], [6, 0, 0]], 0.6)}, 'leg_l': {'rotation': loop([[0, 0, 0], [6, 0, 0]], 0.6)}}
    m.anim('idle', 2.4, 'loop', {k: (v if k != 'body' and k != 'arm_r' and k != 'arm_l' and not k.startswith('leg') else
                                     {c: loop([p[1] for p in pts[:-1]] * 4, 2.4) for c, pts in v.items()}) for k, v in idle.items()})
    walk = {'leg_r': {'rotation': loop([[40, 0, 0], [-40, 0, 0]], 0.5)}, 'leg_l': {'rotation': loop([[-40, 0, 0], [40, 0, 0]], 0.5)},
            'body': {'position': loop([[0, 0, 0], [0, 1.8, 0], [0, 0, 0], [0, 1.8, 0]], 0.5), 'rotation': loop([[12, 8, 3], [12, -8, -3]], 0.5)},
            'arm_r': {'rotation': loop([[-70, 0, -10], [-20, 0, -10]], 0.5)}, 'arm_l': {'rotation': loop([[-20, 0, 10], [-70, 0, 10]], 0.5)},
            'head': {'rotation': loop([[-8, -6, 0], [-8, 6, 0]], 0.5)}}
    m.anim('walk', 0.5, 'loop', walk)
    # attack 0.5 s: cock the right fist back, then a straight punch with the whole body behind it
    att = {'arm_r': {'rotation': kf((0, g_r), (0.14, [-20, 0, -18]), (0.22, [-96, 0, 6]), (0.3, [-92, 0, 6]), (0.5, g_r)),
                     'position': kf((0, [0, 0, 0]), (0.14, [0, 0, 2.2]), (0.22, [0, 0, -5.2]), (0.3, [0, 0, -4.5]), (0.5, [0, 0, 0]))},
           'fist_r': {'scale': kf((0, [1, 1, 1]), (0.2, [1.0, 1.0, 1.0]), (0.24, [1.25, 1.25, 1.25]), (0.34, [1, 1, 1]))},
           'arm_l': {'rotation': kf((0, g_l), (0.14, [-70, 0, 14]), (0.22, [-40, 0, 16]), (0.5, g_l))},
           'body': {'rotation': kf((0, [4, 0, 0]), (0.14, [-2, 22, 0]), (0.22, [14, -24, 0]), (0.3, [12, -20, 0]), (0.5, [4, 0, 0])),
                    'position': kf((0, [0, 0, 0]), (0.14, [0, 0, 1.5]), (0.22, [0, 0, -3]), (0.5, [0, 0, 0]))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.14, [-4, -14, 0]), (0.22, [6, 14, 0]), (0.5, [0, 0, 0]))},
           'leg_r': {'rotation': kf((0, [0, 0, 0]), (0.22, [16, 0, 0]), (0.5, [0, 0, 0]))},
           'leg_l': {'rotation': kf((0, [0, 0, 0]), (0.22, [-22, 0, 0]), (0.5, [0, 0, 0]))}}
    m.anim('attack', 0.5, 'once', att)
    common_tail(m)
    return m


# =================================================================== HEAL SPIRIT
def heal_spirit():
    """Small floaty golden spirit: glowing blob with a happy face, glowing plus-sign crest, floating halo,
    little light wings, team ribbon with a bow at the back."""
    m = Model('clash_heal_spirit', density=2.0)
    m.mats_({
        'gold': ('#ffcf3a', 'glow'), 'gold_s': ('#ffd84a', 'glow'), 'gold_d': ('#e6a826', 'soft'), 'cream': ('#fff6c8', 'glow'),
        'halo': ('#ffe680', 'glow'), 'wing': ('#fff4d0', 'glow'), 'cloth': ('#efefef', 'cloth'),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 3, 0], root)
    fd = face('#2a1a08', white='#ffffff', y=0.24, h=0.36, x0=0.16, w=0.24,
              mouth=('rect', 0.4, 0.74, 0.6, 0.8, '#7a3a10'),
              extra=[('rect', 0.36, 0.7, 0.4, 0.76, '#7a3a10'), ('rect', 0.6, 0.7, 0.64, 0.76, '#7a3a10'),
                     ('rect', 0.06, 0.62, 0.18, 0.7, '#ff9a6a'), ('rect', 0.82, 0.62, 0.94, 0.7, '#ff9a6a')])
    for sx in (1, -1):
        cb(body, sx * 2.2, -3, -0.2, 2.6, 1.8, 3.0, 'gold_d')                       # stubby feet
    cb(body, 0, -1.6, 0, 9.4, 5.6, 9.0, 'gold_s', decals={'north': fd})
    cb(body, 0, 4.0, 0, 7.6, 2.6, 7.4, 'gold', decals={'north': [('rect', 0.2, 0.3, 0.3, 0.5, '#fff6c8')]})
    cb(body, 0, 6.6, 0, 5.0, 1.4, 5.0, 'gold')
    tc = m.bone('tc_ribbon', [0, 3, 0], body)
    cb(tc, 0, 3.2, 0, 9.8, 1.3, 9.4, 'cloth')
    cb(tc, 0, 3.0, 5.0, 3.0, 1.8, 1.0, 'cloth')                                     # bow
    for sx in (1, -1):
        cb(tc, sx * 2.0, 3.2, 5.2, 2.0, 1.6, 0.6, 'cloth', rot=('z', sx * 22.5))
        cb(tc, sx * 1.0, 0.6, 5.0, 1.0, 2.6, 0.5, 'cloth', rot=('z', sx * 22.5))   # ribbon tails
    crest = m.bone('crest', [0, 8, 0], body)                                         # glowing plus sign
    cb(crest, 0, 9.1, 0, 4.2, 1.4, 1.4, 'cream')
    cb(crest, 0, 7.7, 0, 1.4, 4.2, 1.4, 'cream')
    halo = m.bone('halo', [0, 13.6, 0.6], body)
    for z in (-2.7, 2.7):                                                          # octagonal halo ring
        cb(halo, 0, 13.2, 0.6 + z, 2.8, 0.7, 0.8, 'halo')
    for x in (-2.7, 2.7):
        cb(halo, x, 13.2, 0.6, 0.8, 0.7, 2.8, 'halo')
    for dx in (-1.95, 1.95):
        for dz in (-1.95, 1.95):
            cb(halo, dx, 13.2, 0.6 + dz, 2.2, 0.7, 0.8, 'halo', rot=('y', 45 if dx * dz > 0 else -45))
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 4.2, 4.4, 1.2], body)
        cb(w, sx * 5.8, 3.6, 1.6, 3.0, 2.6, 0.6, 'wing', rot=('z', -sx * 22.5))
        cb(w, sx * 6.6, 5.6, 1.6, 2.0, 1.6, 0.6, 'wing', rot=('z', -sx * 45))
    m.hitbox(0.7, 0.8)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.8, 0]], 1.0), 'scale': loop([[1, 1, 1], [0.97, 1.04, 0.97]], 1.0)},
            'halo': {'rotation': loop([[0, 0, 0], [0, 45, 0]], 1.0), 'position': loop([[0, 0, 0], [0, 0.6, 0]], 1.0)},
            'crest': {'scale': loop([[1, 1, 1], [1.15, 1.15, 1.15]], 0.5)},
            'wing_r': {'rotation': loop([[0, -20, 0], [0, 20, 0]], 0.3)}, 'wing_l': {'rotation': loop([[0, 20, 0], [0, -20, 0]], 0.3)}}
    m.anim('idle', 1.0, 'loop', idle)
    walk = {'body': {'position': loop([[0, 0, 0], [0, 2.2, 0]], 0.3), 'scale': loop([[1.08, 0.92, 1.08], [0.95, 1.06, 0.95]], 0.3)},
            'halo': {'position': loop([[0, -0.6, 0], [0, 0.8, 0]], 0.3)},
            'wing_r': {'rotation': loop([[0, -30, 0], [0, 30, 0]], 0.15)}, 'wing_l': {'rotation': loop([[0, 30, 0], [0, -30, 0]], 0.15)}}
    m.anim('walk', 0.3, 'loop', walk)
    # attack 0.4 s: crouch, pounce forward, burst into light
    att = {'body': {'scale': kf((0, [1, 1, 1]), (0.08, [1.25, 0.75, 1.25]), (0.2, [0.9, 1.15, 0.9]), (0.3, [1.7, 1.7, 1.7]), (0.4, [1, 1, 1])),
                    'position': kf((0, [0, 0, 0]), (0.08, [0, -0.5, 0.5]), (0.2, [0, 5, -6]), (0.3, [0, 2, -8]), (0.4, [0, 0, 0]))},
           'halo': {'scale': kf((0, [1, 1, 1]), (0.2, [1, 1, 1]), (0.3, [2.0, 1, 2.0]), (0.4, [1, 1, 1]))},
           'crest': {'scale': kf((0, [1, 1, 1]), (0.2, [1.2, 1.2, 1.2]), (0.3, [2.2, 2.2, 2.2]), (0.4, [1, 1, 1]))},
           'wing_r': {'rotation': kf((0, [0, 0, 0]), (0.08, [0, 0, 30]), (0.2, [0, 0, -30]), (0.4, [0, 0, 0]))},
           'wing_l': {'rotation': kf((0, [0, 0, 0]), (0.08, [0, 0, -30]), (0.2, [0, 0, 30]), (0.4, [0, 0, 0]))}}
    m.anim('attack', 0.4, 'once', att)
    m.anim('spawn', 0.5, 'once', {'root': {'scale': kf((0, [0.2, 0.2, 0.2]), (0.3, [1.15, 1.15, 1.15]), (0.5, [1, 1, 1])),
                                           'position': kf((0, [0, 10, 0]), (0.3, [0, 0, 0]), (0.5, [0, 0, 0]))}})
    m.anim('hit', 0.3, 'once', {'body': {'rotation': kf((0, [0, 0, 0]), (0.08, [12, 0, 0]), (0.3, [0, 0, 0]))},
                                'root': {'scale': kf((0, [1, 1, 1]), (0.08, [1.06, 0.94, 1.06]), (0.3, [1, 1, 1]))}})
    m.anim('death', 0.35, 'hold', {'root': {'scale': kf((0, [1, 1, 1]), (0.12, [1.5, 1.5, 1.5]), (0.35, [0.01, 0.01, 0.01]))},
                                   'crest': {'scale': kf((0, [1, 1, 1]), (0.12, [2, 2, 2]))}})
    return m


# =================================================================== shared: longbow + archer animations
def make_bow(m, parent, hx, hy, hz, wood, tip, string, grip=None, k=1.0, tc_limbs=False):
    """vertical recurve bow in the y-z plane held at (hx, hy, hz), scaled by k; limbs curve forward (-z).
    Adds bones bow / arrow_tip (and tc_bow_limbs when the limbs are team-coloured)."""
    bow = m.bone('bow', [hx, hy, hz], parent)
    lb = m.bone('tc_bow_limbs', [hx, hy, hz], bow) if tc_limbs else bow
    cb(bow, hx, hy - 1.6 * k, hz, 1.4, 3.2 * k, 1.6, grip or wood)
    for sy in (1, -1):
        cb(lb, hx, hy + sy * 3.6 * k - 2.0 * k, hz - 0.6, 1.1, 4.0 * k, 1.1, wood, rot=('x', -sy * 22.5))
        cb(lb, hx, hy + sy * 6.9 * k - 1.5 * k, hz - 1.0, 1.0, 3.0 * k, 1.0, wood, rot=('x', sy * 22.5))
        cb(bow, hx, hy + sy * 8.5 * k - 0.55, hz - 0.5, 1.2, 1.1, 1.2, tip)
    cb(lb, hx, hy - 8.4 * k, hz + 0.4, 0.3, 16.8 * k, 0.3, string)
    at = m.bone('arrow_tip', [hx, hy, hz - 1.6], bow)
    cb(at, hx, hy - 0.4, hz - 1.6, 0.9, 0.9, 1.0, tip)
    return bow


def archer_anims(m, idle_extra=None, walk_extra=None, L=0.6):
    """bow in the left hand; the right hand draws the string. attack: raise, draw, release."""
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [2, 0, 0], [0, -6, 0], [2, 0, 0]], 2.0)},
            'arm_l': {'rotation': loop([[-12, 0, -4], [-16, 0, -6]], 2.0)}, 'bow': {'rotation': loop([[12, 0, 0], [16, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([[0, 0, 4], [-4, 0, 6]], 2.0)}}
    idle.update(idle_extra or {})
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[26, 0, 0], [-26, 0, 0]], 0.7)}, 'leg_l': {'rotation': loop([[-26, 0, 0], [26, 0, 0]], 0.7)},
            'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.7), 'rotation': loop([[4, 3, 0], [4, -3, 0]], 0.7)},
            'arm_r': {'rotation': loop([[-22, 0, 4], [22, 0, 4]], 0.7)},
            'arm_l': {'rotation': loop([[-6, 0, -4], [-20, 0, -4]], 0.7)}, 'bow': {'rotation': loop([[6, 0, 0], [20, 0, 0]], 0.7)}}
    walk.update(walk_extra or {})
    m.anim('walk', 0.7, 'loop', walk)
    f = L / 0.6
    att = {'body': {'rotation': kf((0, [0, 0, 0]), (0.15 * f, [0, -30, 0]), (0.36 * f, [-4, -34, 0]), (0.42 * f, [2, -28, 0]), (L, [0, 0, 0]))},
           'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.15 * f, [-86, 18, 0]), (0.36 * f, [-88, 22, 0]), (0.42 * f, [-80, 18, 0]), (L, [0, 0, 0]))},
           'bow': {'rotation': kf((0, [0, 0, 0]), (0.15 * f, [86, 0, 0]), (0.36 * f, [88, 0, 0]), (0.42 * f, [70, 0, 0]), (0.5 * f, [86, 0, 0]), (L, [0, 0, 0]))},
           'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.15 * f, [-86, 40, 0]), (0.36 * f, [-84, 62, 0]), (0.42 * f, [-70, 10, 30]), (L, [0, 0, 0])),
                     'position': kf((0, [0, 0, 0]), (0.15 * f, [0, 0, -1]), (0.36 * f, [0, 0, 2.5]), (0.42 * f, [0, 0, 2.5]), (L, [0, 0, 0]))},
           'arrow_tip': {'scale': kf((0, [1, 1, 1]), (0.36 * f, [1.6, 1.6, 1.6]), (0.42 * f, [2.6, 2.6, 2.6]), (0.5 * f, [0.6, 0.6, 0.6]), (L, [1, 1, 1]))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.15 * f, [0, 26, 0]), (0.42 * f, [0, 26, 0]), (L, [0, 0, 0]))}}
    m.anim('attack', L, 'once', att)
    common_tail(m)

# =================================================================== HQ helpers (rounded boxes, 3D face parts)
def rbox(bone, x, y, z, w, h, d, mat, r=1.0, decals=None, rot=None):
    """rounded box = three crossing boxes (edges bevelled by r). decals: north/south go on the z box, east/west on x, up/down on y."""
    dec = decals or {}
    pick = lambda fs: {f: v for f, v in dec.items() if f in fs}
    r = min(r, w / 2 - 0.05, h / 2 - 0.05, d / 2 - 0.05)
    cb(bone, x, y + r, z, w, h - 2 * r, d - 2 * r, mat, decals=pick(('east', 'west')), noround=True, rot=rot)
    cb(bone, x, y, z, w - 2 * r, h, d - 2 * r, mat, decals=pick(('up', 'down')), noround=True, rot=rot)
    cb(bone, x, y + r, z, w - 2 * r, h - 2 * r, d, mat, decals=pick(('north', 'south')), noround=True, rot=rot)


def eye_dec(iris, sx, pupil='#141018', lid='#3a2422', white='#ffffff', glow=False):
    """eye decal (front face): sclera, iris looking slightly inward, pupil, 1px highlight, upper lid"""
    o = 0.06 * sx                      # +x eye -> look toward u=1 (centre)
    out = [('rect', 0, 0, 1, 1, white), ('rect', 0.18 + o, 0.2, 0.86 + o, 1.0, iris)]
    if pupil:
        out.append(('rect', 0.36 + o, 0.42, 0.68 + o, 0.9, pupil))
    out += [('rect', 0.3 + o, 0.3, 0.46 + o, 0.48, '#ffffff'), ('rect', 0, 0, 1, 0.16, lid)]
    if glow:
        out = [('rect', 0, 0, 1, 1, white), ('rect', 0.2, 0.2, 0.8, 0.85, iris), ('rect', 0.35, 0.35, 0.6, 0.6, '#ffffff'), ('rect', 0, 0, 1, 0.14, lid)]
    return out


def eyes(head, xs, y, z, w, h, iris, mat='eye', **kw):
    for sx in (1, -1):
        cb(head, sx * xs, y, z, w, h, 0.3, mat, decals={'north': eye_dec(iris, sx, **kw)}, dens=4, noround=True)


def fist(bone, x, y, z, mat, w=2.8, h=2.6, d=3.0, sx=1):
    """chunky hand: palm block + knuckle row + thumb"""
    rbox(bone, x, y, z, w, h, d, mat, r=0.5)
    cb(bone, x, y - 0.4, z - 0.4, w - 0.4, 0.8, d - 1.0, mat, noround=True)
    cb(bone, x - sx * (w / 2 - 0.2), y + 0.6, z - 0.9, 0.9, 1.4, 1.2, mat, noround=True)


def boot(bone, x, z, mat, w=2.8, h=2.6, d=3.6, sole='#2a1a12', cuff=None, toe=None):
    rbox(bone, x, 0.3, z, w, h, d, mat, r=0.5)
    cb(bone, x, 0.0, z - 0.4, w + 0.1, 0.5, d + 0.6, 'sole', noround=True)
    cb(bone, x, 0.3, z - d / 2 - 0.2, w - 0.6, 1.4, 1.0, toe or mat, noround=True)      # toe cap
    if cuff:
        cb(bone, x, h - 0.3, z, w + 0.4, 0.9, d - 0.6 + 0.4, cuff, noround=True)


# =================================================================== PRINCESS (HQ)
def princess():
    """CR Princess (0.85x knight): dark bob, gold crown with gems, steel chestplate over chain mail,
    team-coloured robe/sleeves/leggings, brown boots and gloves, quiver on her back, longbow in the left hand."""
    m = Model('clash_princess', density=2.0)
    m.mats_({
        'skin': ('#f7d8c2', 'skin'), 'blush': ('#f2a8a0', 'skin'), 'eye': ('#ffffff', 'plain'), 'mouth': ('#b8404a', 'plain'),
        'hair': ('#2a1c1a', 'hair'), 'hair_l': ('#4a3430', 'hair'), 'cloth': ('#efefef', 'cloth'),
        'armor': ('#cfd4dc', 'metal'), 'armor_d': ('#a0a6b2', 'metal'), 'chain': ('#8c919c', 'metal'), 'gold': ('#f4c23a', 'metal'),
        'gem': ('#e83850', 'gem'), 'gem_b': ('#3a8ae8', 'gem'), 'wood': ('#8e5a2e', 'wood', {'grain': 'v'}), 'grip': ('#5a3a22', 'leather'),
        'string': ('#f2ead6', 'plain'), 'boot': ('#6a4228', 'leather'), 'sole': ('#2a1a12', 'plain'), 'glove': ('#7a4e30', 'leather'),
        'quiver': ('#7a4e30', 'leather'), 'feather': ('#f4f0e8', 'plain'), 'feather_r': ('#d83a3a', 'plain'), 'white': ('#f6f2ec', 'cloth'),
    })
    chain_dec = [('rect', i / 8, j / 3, i / 8 + 0.06, j / 3 + 0.12, '#5a5e68') for i in range(8) for j in range(3)]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.6, 6, 0], root)
        tl = m.bone('tc_legging_' + side, [sx * 1.6, 6, 0], lg)
        rbox(tl, sx * 1.6, 2.4, 0, 2.4, 4.2, 2.4, 'cloth', r=0.4)
        boot(lg, sx * 1.6, -0.2, 'boot', w=2.9, h=2.8, d=3.6, cuff='boot')
        cb(lg, sx * 1.6, 1.4, -2.0, 1.0, 0.8, 0.3, 'gold', noround=True)                     # boot buckle
    body = m.bone('body', [0, 6, 0], root)
    tr = m.bone('tc_robe', [0, 6, 0], body)
    rbox(tr, 0, 3.8, 0.1, 8.8, 4.6, 6.8, 'cloth', r=1.0, decals={'north': [('rect', 0.47, 0.0, 0.53, 1.0, '#c8c8c8'), ('rect', 0.2, 0.2, 0.24, 1.0, '#d8d8d8')]})
    cb(tr, 0, 3.6, 0.1, 8.0, 0.6, 6.2, 'cloth', noround=True)
    cb(body, 0, 3.7, 0.1, 9.0, 0.5, 7.0, 'gold', noround=True)                           # gold hem
    rbox(body, 0, 7.8, 0, 7.6, 1.8, 5.4, 'chain', r=0.4, decals={'north': chain_dec, 'south': chain_dec})
    rbox(body, 0, 9.2, -0.1, 7.4, 4.0, 5.4, 'armor', r=0.9, decals={'north': [('rect', 0.15, 0.1, 0.35, 0.8, '#eef0f6'), ('rect', 0.47, 0.0, 0.53, 1.0, '#9aa0aa'),
                                                                              ('px', 0.12, 0.15, '#7a808a'), ('px', 0.88, 0.15, '#7a808a')]})
    cb(body, 0, 12.8, -2.9, 6.0, 0.6, 0.5, 'gold', noround=True)                          # plate trim
    cb(body, 0, 11.2, -2.95, 1.2, 1.2, 0.4, 'gem_b', noround=True)                         # chest gem
    cb(body, 0, 8.6, 0, 8.0, 0.9, 5.8, 'grip', noround=True)                               # belt
    cb(body, 0, 8.4, -2.95, 1.4, 1.3, 0.4, 'gold', noround=True)
    rbox(body, 3.0, 7.0, -2.2, 1.8, 1.8, 1.4, 'grip', r=0.3)                                  # belt pouch
    for sx in (1, -1):
        rbox(body, sx * 3.2, 11.6, -0.1, 2.0, 1.8, 5.0, 'armor_d', r=0.4)                    # plate side curve
        cb(body, sx * 2.4, 12.4, -2.95, 0.5, 0.5, 0.3, 'armor_d', noround=True)                # rivets
        cb(body, sx * 2.4, 10.0, -2.95, 0.5, 0.5, 0.3, 'armor_d', noround=True)
    rbox(tr, 0, 12.6, 0.2, 8.8, 1.6, 5.8, 'cloth', r=0.5)                                  # collar / shoulders
    cb(body, 0, 13.6, -2.7, 4.0, 0.7, 1.0, 'white', noround=True)
    q = m.bone('quiver', [-1, 10, 3.4], body)                                            # quiver with fletched arrows
    rbox(q, -1.2, 7.0, 3.8, 2.8, 7.0, 2.6, 'quiver', r=0.5, rot=('z', 22.5))
    cb(q, -1.2, 12.4, 3.8, 3.0, 0.6, 2.8, 'gold', rot=('z', 22.5), noround=True)
    for i, dx in enumerate((-0.7, 0.2, 1.0)):
        cb(q, -3.6 + dx, 13.6, 3.6 + (i - 1) * 0.6, 0.5, 2.2, 0.8, 'feather_r' if i == 1 else 'feather', rot=('z', 22.5), noround=True)
    # head
    head = m.bone('head', [0, 14.2, 0], body)
    rbox(head, 0, 14.0, -0.1, 9.0, 8.8, 8.4, 'skin', r=1.5, decals={'north': [('rect', 0.08, 0.6, 0.24, 0.68, '#f4b0a8'), ('rect', 0.76, 0.6, 0.92, 0.68, '#f4b0a8')]})
    eyes(head, 1.9, 16.8, -4.4, 2.2, 2.6, '#6a3a22')
    for sx in (1, -1):
        cb(head, sx * 2.0, 19.8, -4.4, 2.8, 0.8, 0.6, 'hair', rot=('z', sx * 22.5), noround=True)   # thick angled brows
        cb(head, sx * 4.6, 16.4, 0.4, 0.8, 1.8, 1.4, 'skin', noround=True)                         # ears
    cb(head, 0, 15.9, -4.6, 1.0, 1.0, 0.6, 'skin', noround=True)                                   # nose
    cb(head, 0.2, 15.2, -4.4, 2.2, 0.4, 0.3, 'mouth', noround=True)                                       # closed confident smile
    cb(head, 1.4, 15.4, -4.4, 0.6, 0.4, 0.3, 'mouth', noround=True)
    # layered dark bob
    rbox(head, 0, 21.0, 0.3, 9.8, 3.4, 9.4, 'hair', r=1.2, decals={'up': [('rect', 0.3, 0.2, 0.36, 0.8, '#4a3430')]})
    for sx in (1, -1):
        rbox(head, sx * 4.7, 16.0, 0.6, 1.4, 6.0, 8.6, 'hair', r=0.4)
        cb(head, sx * 5.1, 15.6, 0.6, 1.0, 1.0, 8.4, 'hair_l', noround=True)                     # flicked-out ends
    rbox(head, 0, 15.6, 4.5, 9.8, 6.4, 1.6, 'hair', r=0.5)
    cb(head, 0, 15.2, 4.9, 8.8, 0.9, 1.4, 'hair_l', noround=True)
    for i, (x, w, h, rr) in enumerate(((-3.0, 3.0, 1.2, 0), (-0.6, 3.0, 1.4, -22.5), (1.8, 3.0, 1.6, -22.5), (3.9, 1.6, 2.4, 0))):
        cb(head, x, 21.7 - h, -4.5, w, h, 0.9, 'hair' if i % 2 else 'hair_l', rot=('z', rr) if rr else None, noround=True)   # side-swept fringe
    for sx in (1, -1):
        rbox(head, sx * 4.9, 18.6, -1.2, 1.6, 4.0, 5.4, 'hair', r=0.5)                                # puffy volume at the sides
        cb(head, sx * 5.4, 20.2, 2.4, 1.0, 3.0, 3.0, 'hair_l', noround=True)
    cb(head, 0, 24.2, 2.8, 7.0, 0.8, 4.0, 'hair_l', noround=True)                                       # top sheen
    crown = m.bone('crown', [0, 24, 0], head)
    cb(crown, 0, 23.9, 0, 5.6, 1.2, 5.4, 'gold', decals={f: [('rect', 0.4, 0.2, 0.6, 0.8, '#e83850')] for f in ('north', 'south', 'east', 'west')})
    for x, z in ((0, -2.5), (-2.5, 0), (2.5, 0), (0, 2.5), (-1.8, -1.8), (1.8, -1.8)):
        cb(crown, x, 25.1, z, 0.9, 1.2, 0.9, 'gold', noround=True)
        cb(crown, x, 26.3, z, 0.6, 0.6, 0.6, 'gold', noround=True)
    cb(crown, 0, 24.1, -2.85, 1.0, 0.8, 0.4, 'gem', noround=True)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.0, 13.4, 0], body)
        ts = m.bone('tc_sleeve_' + side, [sx * 5.0, 13.4, 0], arm)
        rbox(ts, sx * 5.2, 11.0, 0, 3.0, 3.0, 3.2, 'cloth', r=0.7)                              # puff sleeve
        for yy in (11.4, 12.6):
            cb(arm, sx * 5.2, yy, 0, 3.1, 0.4, 3.3, 'white', noround=True)                    # white stripes
        rbox(ts, sx * 5.1, 9.0, 0, 2.3, 2.4, 2.5, 'cloth', r=0.3)
        cb(arm, sx * 5.1, 8.6, 0, 2.7, 0.8, 2.9, 'white', noround=True)
        fist(arm, sx * 5.1, 6.4, -0.1, 'glove', w=2.6, h=2.4, d=2.8, sx=sx)
    make_bow(m, m.by_name('arm_l'), -5.1, 7.6, -0.7, 'wood', 'gold', 'string', grip='grip', k=0.85)
    m.hitbox(0.8, 1.7)
    archer_anims(m)
    return m


# =================================================================== ICE WIZARD (HQ)
def ice_wizard():
    """CR Ice Wizard (0.9x): round chubby body, cyan spiky hair, bushy frosty brows, glowing eyes, big nose,
    cyan horseshoe moustache, brown leather coat with fur collar over a team-coloured suit + belt, bare hands casting ice."""
    m = Model('clash_ice_wizard', density=2.0)
    m.mats_({
        'skin': ('#f0d4c8', 'skin'), 'eye': ('#b8faff', 'glow'), 'hair': ('#2fb6ec', 'hair'), 'hair_l': ('#5cd4fa', 'hair'), 'hair_d': ('#1a86c0', 'hair'),
        'brow': ('#e4f8ff', 'fur'), 'cloth': ('#efefef', 'cloth'), 'mouth': ('#5a2a2a', 'plain'),
        'coat': ('#7a4e30', 'leather'), 'coat_d': ('#5a3820', 'leather'), 'fur': ('#e0d8cc', 'fur'), 'fur_d': ('#b8ad9c', 'fur'),
        'boot': ('#4e3220', 'leather'), 'sole': ('#241810', 'plain'), 'gold': ('#e0b040', 'metal'), 'ice': ('#8fe8ff', 'glow'), 'ice_w': ('#e8fcff', 'glow'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.1, 5.4, 0], root)
        tl = m.bone('tc_pants_' + side, [sx * 2.1, 5.4, 0], lg)
        rbox(tl, sx * 2.1, 2.2, 0, 3.0, 3.6, 3.0, 'cloth', r=0.5)
        boot(lg, sx * 2.1, -0.3, 'boot', w=3.4, h=2.6, d=4.0, cuff='fur')
    body = m.bone('body', [0, 5.4, 0], root)
    ts = m.bone('tc_suit', [0, 5.4, 0], body)
    rbox(ts, 0, 4.4, -0.2, 9.6, 8.4, 8.0, 'cloth', r=2.2, decals={'north': [('rect', 0.47, 0.0, 0.53, 1.0, '#c8c8c8'), ('px', 0.5, 0.25, '#a0a0a0'), ('px', 0.5, 0.55, '#a0a0a0')]})
    rbox(ts, 0, 6.6, -0.2, 10.2, 1.6, 8.6, 'cloth', r=0.6)                                # belt
    cb(body, 0, 6.5, -4.6, 2.2, 1.8, 0.5, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#8a6a20')]}, noround=True)
    for sx in (1, -1):
        rbox(body, sx * 4.4, 3.6, 0.9, 1.8, 9.4, 7.4, 'coat', r=0.5)                          # open leather coat
        cb(body, sx * 3.6, 8.6, -3.4, 1.2, 4.0, 0.6, 'coat_d', rot=('z', sx * 22.5), noround=True)   # lapels
    rbox(body, 0, 3.4, 4.3, 10.0, 9.6, 1.2, 'coat', r=0.4, decals={'south': [('rect', 0.48, 0.0, 0.52, 0.5, '#5a3820')]})
    for sx in (1, -1):
        cb(body, sx * 2.4, 2.4, 4.6, 4.2, 2.0, 0.9, 'coat_d', rot=('z', sx * 22.5), noround=True)   # coat tails
        rbox(body, sx * 4.6, 2.8, -2.6, 1.6, 1.2, 2.6, 'fur', r=0.3)                               # fur hem
    rbox(body, 0, 11.8, 0.4, 11.4, 2.6, 9.0, 'fur', r=1.0)                                 # fur collar (fluffy, 2 layers)
    for sx in (1, -1):
        for yy in (5.0, 8.0):
            cb(body, sx * 3.6, yy, -3.0, 0.8, 0.8, 0.5, 'gold', noround=True)                 # coat buttons
    rbox(body, -3.0, 4.6, -3.4, 2.2, 2.0, 1.4, 'coat_d', r=0.3)                           # belt pouch
    for sx in (1, -1):
        cb(body, sx * 1.8, 6.5, -4.6, 0.6, 1.8, 0.4, 'gold', noround=True)                    # belt studs
    cb(body, 0, 11.6, 0.6, 10.6, 0.8, 8.4, 'fur_d', noround=True)
    # head
    head = m.bone('head', [0, 14, 0], body)
    rbox(head, 0, 13.6, -0.2, 9.6, 9.2, 9.0, 'skin', r=1.8, decals={'north': [('rect', 0.06, 0.55, 0.22, 0.64, '#e8b0b0'), ('rect', 0.78, 0.55, 0.94, 0.64, '#e8b0b0')]})
    eyes(head, 2.1, 17.6, -4.75, 2.2, 1.6, '#4fe0ff', glow=True, white='#d8fcff', lid='#4a7a90')
    for sx in (1, -1):
        cb(head, sx * 2.2, 19.4, -4.9, 3.6, 1.2, 1.4, 'brow', rot=('z', sx * 22.5), noround=True)     # bushy frosty brows
        cb(head, sx * 3.9, 20.0, -4.7, 1.6, 1.2, 1.2, 'brow', rot=('z', sx * 45), noround=True)
        cb(head, sx * 4.9, 17.0, 0.4, 0.9, 2.2, 1.6, 'skin', noround=True)                           # ears
    rbox(head, 0, 15.8, -5.2, 2.2, 2.4, 1.6, 'skin', r=0.5)                                         # big nose
    cb(head, 0, 14.4, -4.75, 2.4, 0.8, 0.3, 'mouth', noround=True)
    bd = m.bone('beard', [0, 16, -4.8], head)                                                       # cyan horseshoe moustache
    rbox(bd, 0, 15.2, -5.2, 6.4, 1.4, 1.4, 'hair', r=0.4)
    for sx in (1, -1):
        cb(bd, sx * 2.9, 12.4, -5.0, 1.4, 3.2, 1.2, 'hair', noround=True)
        cb(bd, sx * 3.0, 11.8, -4.9, 1.0, 0.8, 1.0, 'hair_l', noround=True)
        cb(bd, sx * 1.6, 15.4, -5.9, 1.8, 0.8, 0.3, 'hair_l', noround=True)
    cb(bd, 0, 12.6, -4.8, 1.4, 1.4, 0.8, 'hair', noround=True)                                     # small chin tuft
    hair = m.bone('hair', [0, 23, 0], head)                                                         # cyan spiky hair, layered
    rbox(hair, 0, 21.6, 0.4, 10.0, 2.4, 9.6, 'hair', r=1.0)
    spikes = ((0, -2.2, 5.6, 'x', 22.5), (-2.4, -1.6, 4.8, 'z', 22.5), (2.4, -1.6, 4.8, 'z', -22.5), (-4.0, 0.6, 3.8, 'z', 45), (4.0, 0.6, 3.8, 'z', -45),
              (-1.2, 1.0, 5.6, 'x', 22.5), (1.4, 1.2, 5.6, 'x', 22.5), (0, 3.4, 4.6, 'x', 45), (-2.8, 3.0, 4.0, 'x', 45), (2.8, 3.0, 4.0, 'x', 45),
              (-3.6, -2.4, 3.2, 'z', 22.5), (3.6, -2.4, 3.2, 'z', -22.5), (-1.4, 4.4, 3.4, 'x', 45), (1.4, 4.4, 3.4, 'x', 45))
    for (x, z, h, ax, r) in spikes:
        cb(hair, x, 23.2, z, 2.6, h * 0.6, 2.6, 'hair_d' if abs(x) > 3 else 'hair', rot=(ax, r), noround=True)
        cb(hair, x + (0 if ax == 'x' else (-0.8 if r > 0 else 0.8) * (1 if abs(r) < 40 else 1.6)), 23.2 + h * 0.5,
           z + (h * 0.25 if ax == 'x' else 0), 1.6, h * 0.5, 1.6, 'hair_l', rot=(ax, r), noround=True)
    for sx in (1, -1):
        cb(hair, sx * 4.9, 17.6, 0.8, 0.9, 4.0, 4.0, 'hair_d', noround=True)                     # sideburns
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.8, 12.6, 0], body)
        rbox(arm, sx * 6.0, 8.4, 0.2, 3.2, 4.8, 3.6, 'coat', r=0.7)
        rbox(arm, sx * 6.0, 8.0, 0.1, 3.8, 1.4, 4.0, 'fur', r=0.5)                               # fur cuff
        fist(arm, sx * 6.0, 5.4, -0.1, 'skin', w=3.0, h=2.7, d=3.0, sx=sx)                     # bare chunky hands
        for yy in (9.6, 11.4):
            cb(arm, sx * 6.0, yy, -1.6, 3.3, 0.4, 0.6, 'coat_d', noround=True)                # sleeve seams
        fr = m.bone('frost_' + side, [sx * 6.0, 4.6, -2.0], arm)
        cb(fr, sx * 6.0, 3.4, -2.2, 2.2, 2.2, 2.2, 'ice', noround=True)
        for (dx, dy, dz, h, ax, r) in ((0, 1.6, 0, 2.0, 'z', 22.5), (1.2, 0.6, -0.6, 1.6, 'x', 22.5), (-1.0, 0.8, -0.4, 1.4, 'z', -45), (0.3, 0.2, -1.4, 1.4, 'x', -22.5)):
            cb(fr, sx * (6.0 + dx), 4.0 + dy, -2.2 + dz, 0.8, h, 0.8, 'ice_w', rot=(ax, sx * r if ax == 'z' else r), noround=True)
    m.hitbox(0.9, 1.75)

    hold = lambda s, a=0: [-36 + a, 0, s * 8]
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [2, 0, 0], [0, -6, 0], [2, 0, 0]], 2.0)},
            'beard': {'rotation': loop([[0, 0, 2], [0, 0, -2]], 2.0)},
            'arm_r': {'rotation': loop([hold(1), hold(1, -6)], 2.0)}, 'arm_l': {'rotation': loop([hold(-1, -6), hold(-1)], 2.0)},
            'frost_r': {'scale': loop([[1, 1, 1], [1.2, 1.2, 1.2]], 0.6), 'rotation': loop([[36, 0, 0], [36, 30, 0]], 1.2)},
            'frost_l': {'scale': loop([[1.2, 1.2, 1.2], [1, 1, 1]], 0.6), 'rotation': loop([[36, 0, 0], [36, -30, 0]], 1.2)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], 0.8)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], 0.8)},
            'body': {'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.8), 'rotation': loop([[4, 3, 0], [4, -3, 0]], 0.8)},
            'arm_r': {'rotation': loop([hold(1, 10), hold(1, -10)], 0.8)}, 'arm_l': {'rotation': loop([hold(-1, -10), hold(-1, 10)], 0.8)},
            'beard': {'rotation': loop([[-4, 0, 3], [-4, 0, -3]], 0.8)}}
    m.anim('walk', 0.8, 'loop', walk)
    att = {}
    for side, s in (('r', 1), ('l', -1)):
        att['arm_' + side] = {'rotation': kf((0, hold(s)), (0.2, [-10, 0, s * 4]), (0.3, [-92, 0, -s * 8]), (0.42, [-82, 0, -s * 6]), (0.6, hold(s)))}
        att['frost_' + side] = {'scale': kf((0, [1, 1, 1]), (0.2, [1.4, 1.4, 1.4]), (0.3, [2.4, 2.4, 2.4]), (0.38, [0.6, 0.6, 0.6]), (0.6, [1, 1, 1])),
                                'rotation': kf((0, [36, 0, 0]), (0.3, [92, 0, 0]), (0.6, [36, 0, 0]))}
    att['body'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-9, 0, 0]), (0.3, [10, 0, 0]), (0.42, [6, 0, 0]), (0.6, [0, 0, 0])),
                   'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 1]), (0.3, [0, 0, -1.5]), (0.6, [0, 0, 0]))}
    att['head'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-6, 0, 0]), (0.3, [4, 0, 0]), (0.6, [0, 0, 0]))}
    att['beard'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.32, [12, 0, 0]), (0.6, [0, 0, 0]))}
    m.anim('attack', 0.6, 'once', att)
    common_tail(m)
    return m


# =================================================================== MAGIC ARCHER (HQ)
def magic_archer():
    """CR Magic Archer (1.0x): grey swept-back hair with white streaks, glowing turquoise eyes, strong black brows, square jaw,
    dark green tunic, team-coloured cape, glowing team-coloured recurve bow, quiver of glowing arrows."""
    m = Model('clash_magic_archer', density=2.0)
    m.mats_({
        'skin': ('#f2b08e', 'skin'), 'eye': ('#c8fff8', 'glow'), 'mouth': ('#8a3a32', 'plain'),
        'hair': ('#8c8e96', 'hair'), 'hair_w': ('#f0f0f2', 'hair'), 'hair_d': ('#5e6068', 'hair'), 'brow': ('#1a1a1e', 'hair'),
        'cloth': ('#efefef', 'cloth'), 'tunic': ('#1f4a2c', 'cloth'), 'tunic_d': ('#14321e', 'cloth'),
        'pants': ('#2e2a28', 'cloth'), 'boot': ('#4a3220', 'leather'), 'sole': ('#1e140c', 'plain'), 'leather': ('#6a4628', 'leather'),
        'brass': ('#c8a040', 'metal'), 'bowtc': ('#efefef', 'glow'), 'magic': ('#4ef0e8', 'glow'), 'grip': ('#3a2a20', 'leather'),
    })
    streak = [('rect', 0.12, 0.0, 0.22, 1.0, '#f0f0f2'), ('rect', 0.58, 0.0, 0.68, 1.0, '#f0f0f2')]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.8, 8, 0], root)
        rbox(lg, sx * 1.8, 2.6, 0, 2.6, 5.6, 2.8, 'pants', r=0.4)
        boot(lg, sx * 1.8, -0.3, 'boot', w=3.1, h=3.4, d=3.8, cuff='leather')
        cb(lg, sx * 1.8, 1.6, -0.3, 3.3, 0.5, 4.0, 'brass', noround=True)                      # boot strap
        rbox(lg, sx * 1.8, 5.0, -0.6, 2.8, 1.8, 2.2, 'leather', r=0.3)                        # knee pad
    body = m.bone('body', [0, 8, 0], root)
    rbox(body, 0, 5.6, 0, 7.8, 9.0, 4.8, 'tunic', r=1.0, decals={'north': [('rect', 0.45, 0.0, 0.55, 1.0, '#14321e'), ('px', 0.5, 0.3, '#c8a040'), ('px', 0.5, 0.6, '#c8a040')]})
    for sx in (1, -1):
        cb(body, sx * 2.2, 4.4, -0.2, 3.6, 2.6, 5.2, 'tunic_d', noround=True)                    # tunic skirt flaps
    rbox(body, 0, 7.4, 0, 8.4, 1.2, 5.4, 'leather', r=0.3)                                     # belt
    cb(body, 0, 7.3, -2.8, 1.6, 1.4, 0.4, 'brass', noround=True)
    rbox(body, 2.8, 5.8, -2.4, 2.0, 2.2, 1.4, 'leather', r=0.3)                                # pouch
    for yy in (9.4, 11.0, 12.6):
        cb(body, 0, yy, -2.5, 0.7, 0.7, 0.4, 'brass', noround=True)                           # tunic buttons
    cb(body, -3.0, 4.4, -2.6, 0.9, 3.4, 0.8, 'leather', rot=('z', -22.5), noround=True)        # belt dagger sheath
    cb(body, -3.6, 7.6, -2.6, 0.7, 1.4, 0.7, 'brass', rot=('z', -22.5), noround=True)
    for sx in (1, -1):
        cb(body, sx * 2.6, 13.2, -2.0, 2.4, 1.2, 1.4, 'tunic_d', rot=('z', sx * 22.5), noround=True)   # collar
    cb(body, 0, 10.0, -2.5, 1.0, 6.4, 0.4, 'leather', rot=('z', 45), noround=True)             # quiver strap
    q = m.bone('quiver', [1.2, 12, 2.6], body)
    rbox(q, 1.4, 7.6, 3.4, 2.6, 7.2, 2.4, 'leather', r=0.5, rot=('z', -22.5))
    cb(q, 1.4, 13.0, 3.4, 2.8, 0.6, 2.6, 'brass', rot=('z', -22.5), noround=True)
    for i, dx in enumerate((-0.6, 0.2, 1.0)):
        cb(q, 3.3 + dx, 14.0, 3.0 + i * 0.4, 0.6, 2.0, 0.6, 'magic', rot=('z', -22.5), noround=True)
        cb(q, 3.7 + dx, 15.6, 3.0 + i * 0.4, 1.0, 1.0, 0.3, 'cloth' if i == 1 else 'hair_w', rot=('z', -22.5), noround=True)
    tc = m.bone('tc_cape', [0, 14.4, 2.8], body)                                              # team cape, layered
    rbox(tc, 0, 3.4, 3.1, 8.8, 11.2, 0.9, 'cloth', r=0.3, decals={'south': [('rect', 0.32, 0.0, 0.36, 1.0, '#d0d0d0'), ('rect', 0.64, 0.0, 0.68, 1.0, '#d0d0d0')]})
    for sx in (1, -1):
        cb(tc, sx * 2.6, 1.6, 3.2, 3.4, 2.2, 0.8, 'cloth', rot=('z', sx * 22.5), noround=True)  # tattered points
        cb(tc, sx * 4.4, 6.8, 1.6, 0.9, 7.2, 3.2, 'cloth', noround=True)
    rbox(tc, 0, 13.4, 0.3, 9.6, 2.0, 6.0, 'cloth', r=0.7)
    cb(tc, 0, 13.0, -2.9, 2.4, 1.6, 0.6, 'brass', noround=True)                                # cape clasp
    for sx in (1, -1):
        rbox(tc, sx * 4.0, 12.6, 0.3, 2.6, 2.4, 5.4, 'cloth', r=0.6)                            # cape shoulder folds
        cb(tc, sx * 1.4, 0.8, 3.3, 1.6, 2.0, 0.6, 'cloth', rot=('z', -sx * 22.5), noround=True)
    head = m.bone('head', [0, 15.4, 0], body)
    rbox(head, 0, 15.2, -0.1, 9.2, 9.2, 8.6, 'skin', r=1.5)
    rbox(head, 0, 14.8, -1.4, 6.6, 2.0, 5.8, 'skin', r=0.8)                                   # square jaw
    eyes(head, 2.0, 18.6, -4.5, 2.4, 1.4, '#2ff0e0', glow=True, white='#a8fff4', lid='#2a3a3a')
    for sx in (1, -1):
        cb(head, sx * 2.2, 20.1, -4.6, 3.8, 1.2, 1.0, 'brow', rot=('z', sx * 22.5), noround=True)    # strong angled brows (V)
        cb(head, sx * 4.7, 18.0, 0.4, 0.9, 2.2, 1.6, 'skin', noround=True)                             # ears
    cb(head, 0, 17.2, -4.9, 1.2, 2.2, 0.8, 'skin', noround=True)                                      # nose bridge
    cb(head, 0, 16.6, -5.2, 1.6, 1.0, 0.8, 'skin', noround=True)
    cb(head, -0.2, 15.6, -4.45, 2.6, 0.5, 0.3, 'mouth', noround=True)                                  # smirk
    cb(head, 1.4, 15.9, -4.45, 0.8, 0.5, 0.3, 'mouth', noround=True)
    cb(head, 0, 14.8, -4.45, 1.6, 0.4, 0.3, 'skin', noround=True)
    hair = m.bone('hair', [0, 24, 0], head)                                                           # swept-back grey hair, white streaks
    rbox(hair, 0, 23.0, 0.8, 9.8, 2.8, 9.2, 'hair', r=1.1, decals={'up': streak})
    for i, (z, h, rr, mat) in enumerate(((-3.4, 2.4, -22.5, 'hair_w'), (-1.0, 2.6, -22.5, 'hair'), (1.6, 2.2, 0, 'hair_w'), (3.6, 2.0, 22.5, 'hair'))):
        cb(hair, 0, 24.6, z, 8.6 - i * 0.6, h, 2.6, mat, rot=('x', rr) if rr else None, noround=True)   # quiff layers
    rbox(hair, 0, 16.4, 4.6, 9.6, 8.0, 1.6, 'hair', r=0.5, decals={'south': streak})
    cb(hair, 0, 19.6, 5.6, 7.0, 4.0, 1.2, 'hair_d', rot=('x', 22.5), noround=True)
    for sx in (1, -1):
        cb(hair, sx * 2.4, 16.0, 5.4, 2.4, 2.6, 0.8, 'hair_w', noround=True)                      # streaked nape locks
    for sx in (1, -1):
        rbox(hair, sx * 4.7, 19.4, 1.4, 1.2, 4.8, 6.4, 'hair', r=0.3)
        cb(hair, sx * 4.8, 22.0, 0.4, 1.0, 1.4, 6.0, 'hair_w', noround=True)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 5.0, 14.6, 0], body)
        rbox(arm, sx * 5.1, 11.4, 0, 2.8, 3.4, 3.0, 'tunic', r=0.6)
        rbox(arm, sx * 5.1, 8.6, 0, 2.5, 2.8, 2.7, 'tunic_d', r=0.3)
        rbox(arm, sx * 5.1, 8.0, 0, 2.8, 1.6, 3.0, 'leather', r=0.3)                              # bracer
        fist(arm, sx * 5.1, 5.8, -0.1, 'leather', w=2.7, h=2.4, d=2.9, sx=sx)
    make_bow(m, m.by_name('arm_l'), -5.1, 7.0, -0.7, 'bowtc', 'magic', 'magic', grip='grip', k=0.95, tc_limbs=True)
    m.hitbox(0.9, 1.95)
    archer_anims(m, idle_extra={'arrow_tip': {'scale': loop([[1, 1, 1], [1.3, 1.3, 1.3]], 0.5)}})
    return m


# =================================================================== HUNTER (HQ)
def hunter():
    """CR Hunter (1.1x, stocky): team-coloured coonskin cap with a striped tail, big round red nose, thick black brows,
    black handlebar moustache + short grey beard, barrel chest in a team shirt, leather vest, double-barrel shotgun at the hip."""
    m = Model('clash_hunter', density=2.0)
    m.mats_({
        'skin': ('#f4b08e', 'skin'), 'nose': ('#ff8676', 'skin'), 'eye': ('#ffffff', 'plain'), 'mouth': ('#6a2a2a', 'plain'),
        'beard': ('#c8c6c0', 'fur'), 'beard_d': ('#98968e', 'fur'), 'stache': ('#242222', 'hair'), 'stache_l': ('#46423e', 'hair'),
        'brow': ('#1e1c1c', 'fur'), 'cloth': ('#efefef', 'cloth'), 'fur': ('#efefef', 'fur'), 'tail_d': ('#3a3430', 'fur'),
        'leather': ('#7a5232', 'leather'), 'leather_d': ('#5a3a22', 'leather'), 'pants': ('#6a4a30', 'cloth'),
        'boot': ('#3e2a1c', 'leather'), 'sole': ('#1e140c', 'plain'), 'belt': ('#3a2618', 'leather'),
        'iron': ('#5a5c64', 'metal'), 'iron_d': ('#3a3c42', 'metal'), 'wood': ('#7a4a24', 'wood'), 'brass': ('#d0a040', 'metal'), 'flash': ('#ffb030', 'glow'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.6, 7, 0], root)
        rbox(lg, sx * 2.6, 2.6, 0, 3.6, 4.6, 3.6, 'pants', r=0.6)
        boot(lg, sx * 2.6, -0.4, 'boot', w=4.2, h=3.0, d=4.8, cuff='leather_d')
    body = m.bone('body', [0, 7, 0], root)
    tsh = m.bone('tc_shirt', [0, 7, 0], body)
    rbox(tsh, 0, 6.4, -0.2, 11.0, 5.4, 8.2, 'cloth', r=2.0)                                  # round belly
    rbox(tsh, 0, 10.8, 0.0, 12.6, 6.2, 8.6, 'cloth', r=2.2, decals={'north': [('rect', 0.48, 0.0, 0.52, 1.0, '#c8c8c8'),
                                                                              ('px', 0.5, 0.3, '#8a8a8a'), ('px', 0.5, 0.6, '#8a8a8a')]})  # barrel chest
    for sx in (1, -1):
        rbox(body, sx * 5.8, 6.6, 1.8, 1.2, 10.4, 6.4, 'leather', r=0.3)                       # open leather vest
        cb(body, sx * 4.6, 13.8, -2.9, 2.4, 3.0, 0.8, 'leather_d', rot=('z', sx * 22.5), noround=True)
    rbox(body, 0, 6.6, 4.4, 12.0, 10.4, 1.0, 'leather', r=0.3)
    rbox(body, 0, 6.4, -0.2, 11.8, 1.7, 8.8, 'belt', r=0.4)
    cb(body, 0, 6.3, -4.6, 2.6, 2.0, 0.5, 'brass', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#7a5a20')]}, noround=True)
    cb(body, -3.6, 4.4, -3.6, 2.4, 2.4, 1.6, 'leather_d', noround=True)                        # cartridge pouch
    for i in range(5):
        cb(body, 2.0 + i * 0.9, 6.5, -4.5, 0.6, 1.4, 0.4, 'brass', noround=True)                 # shells on the belt
    for sx in (1, -1):
        for yy in (8.5, 11.5):
            cb(body, sx * 5.2, yy, -2.0, 0.6, 0.6, 0.5, 'brass', noround=True)                    # vest buttons
    head = m.bone('head', [0, 17, 0], body)
    rbox(head, 0, 16.6, -0.2, 10.0, 9.4, 9.0, 'skin', r=1.8, decals={'north': [('rect', 0.06, 0.5, 0.22, 0.6, '#f49a8a'), ('rect', 0.78, 0.5, 0.94, 0.6, '#f49a8a')]})
    eyes(head, 2.3, 20.0, -4.75, 1.6, 1.6, '#3a2a1a')
    for sx in (1, -1):
        cb(head, sx * 2.4, 21.4, -5.0, 4.4, 1.9, 1.6, 'brow', rot=('z', sx * 22.5), noround=True)    # thick black brows (stern V)
        cb(head, sx * 4.4, 22.4, -4.8, 1.6, 1.2, 1.2, 'brow', noround=True)
        cb(head, sx * 5.1, 19.6, 0.4, 1.0, 2.4, 1.8, 'skin', noround=True)
    rbox(head, 0, 17.6, -5.6, 3.6, 3.4, 2.6, 'nose', r=0.9)                                          # big round nose
    bd = m.bone('beard', [0, 18, -4.6], head)
    rbox(bd, 0, 13.4, -4.4, 10.0, 4.4, 3.2, 'beard', r=1.2)                                       # short grey beard
    rbox(bd, 0, 12.2, -4.6, 6.6, 1.8, 2.4, 'beard_d', r=0.6)
    for sx in (1, -1):
        rbox(bd, sx * 4.6, 14.4, -1.6, 1.4, 4.4, 5.0, 'beard', r=0.4)
    rbox(bd, 0, 15.6, -6.0, 9.0, 2.8, 2.2, 'stache', r=0.8)                                       # big black handlebar moustache
    for sx in (1, -1):
        rbox(bd, sx * 5.2, 14.8, -5.8, 2.6, 2.4, 2.0, 'stache', r=0.6, rot=('z', sx * 22.5))
        cb(bd, sx * 6.6, 16.0, -5.6, 1.6, 2.0, 1.6, 'stache', rot=('z', -sx * 22.5), noround=True)     # curled-up tips
        cb(bd, sx * 6.9, 17.6, -5.5, 1.0, 1.2, 1.0, 'stache_l', noround=True)
        cb(bd, sx * 2.0, 17.6, -6.4, 2.6, 0.6, 1.2, 'stache_l', noround=True)
    cb(head, 0, 15.2, -4.75, 2.6, 0.8, 0.3, 'mouth', noround=True)
    cap = m.bone('tc_cap', [0, 26, 0], head)                                                       # team coonskin cap
    rbox(cap, 0, 25.0, 0.3, 11.0, 4.6, 10.0, 'fur', r=1.2)
    rbox(cap, 0, 29.2, 0.4, 9.2, 2.0, 8.6, 'fur', r=1.0)
    rbox(cap, 0, 24.6, 0.3, 11.6, 1.6, 10.6, 'fur', r=0.6)                                        # fluffy rim
    tail = m.bone('cap_tail', [0, 27, 5], head)                                                    # striped tail at the back
    for i in range(6):
        rbox(tail, 0.15 * i, 26.2 - i * 2.0, 5.8 + i * 0.25, 2.9 - i * 0.18, 2.0, 2.9 - i * 0.18, 'tail_d' if i % 2 else 'beard_d', r=0.6)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 6.8, 16.2, 0.2], body)
        tsl = m.bone('tc_sleeve_' + side, [sx * 6.8, 16.2, 0.2], arm)
        rbox(tsl, sx * 7.1, 12.6, 0.2, 3.8, 4.2, 4.0, 'cloth', r=1.0)
        rbox(tsl, sx * 7.0, 10.4, 0.2, 3.4, 2.4, 3.6, 'cloth', r=0.5)
        rbox(arm, sx * 7.0, 9.8, 0.1, 3.8, 1.2, 4.0, 'leather_d', r=0.3)                        # glove cuff
        fist(arm, sx * 7.0, 7.4, 0.0, 'leather', w=3.6, h=3.0, d=3.8, sx=sx)
    gx = 1.4
    gun = m.bone('gun', [gx, 11.0, -0.5], body)                                                    # detailed double-barrel shotgun
    cb(gun, gx, 8.2, 3.0, 2.8, 3.4, 5.6, 'wood', rot=('x', -22.5))                                 # stock
    cb(gun, gx, 9.4, 0.4, 2.2, 2.2, 3.0, 'wood', noround=True)                                     # wrist
    rbox(gun, gx, 9.8, -2.5, 3.4, 3.2, 4.4, 'iron', r=0.4, decals={'east': [('rect', 0.2, 0.3, 0.8, 0.7, '#d0a040')], 'west': [('rect', 0.2, 0.3, 0.8, 0.7, '#d0a040')]})
    for dx in (-0.6, 0.6):
        cb(gun, gx + dx, 12.8, -0.6, 0.6, 1.2, 1.2, 'iron_d', rot=('x', 22.5), noround=True)        # hammers
    cb(gun, gx, 8.8, -1.4, 0.6, 1.0, 1.6, 'iron_d', noround=True)                                  # trigger guard
    for dx in (-0.9, 0.9):
        cb(gun, gx + dx, 11.0, -10.7, 1.8, 1.8, 12.4, 'iron', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#101010')]}, noround=True)
    cb(gun, gx, 11.6, -10.7, 0.6, 0.6, 12.0, 'iron_d', noround=True)                               # rib
    for z in (-6.0, -12.0, -16.4):
        cb(gun, gx, 10.8, z, 4.0, 2.2, 0.8, 'brass', noround=True)                                 # barrel bands
    rbox(gun, gx, 9.2, -7.9, 3.2, 1.9, 6.0, 'wood', r=0.4)                                         # fore-end
    mz = m.bone('muzzle', [gx, 11.9, -17.1], gun)
    cb(mz, gx, 11.5, -17.1, 0.6, 0.8, 0.4, 'flash', noround=True)
    m.hitbox(1.0, 2.15)

    ar, al = [-30, 0, -12], [-52, 42, 0]
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.5, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [2, 0, 0], [0, -6, 0], [2, 0, 0]], 2.0)},
            'beard': {'rotation': loop([[0, 0, 2], [0, 0, -2]], 2.0)},
            'arm_r': {'rotation': loop([ar, [-32, 0, -12]], 2.0)}, 'arm_l': {'rotation': loop([al, [-54, 42, 0]], 2.0)},
            'gun': {'rotation': loop([[0, 0, 0], [-2, 0, 0]], 2.0)}}
    m.anim('idle', 2.0, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[24, 0, 0], [-24, 0, 0]], 0.8)}, 'leg_l': {'rotation': loop([[-24, 0, 0], [24, 0, 0]], 0.8)},
            'body': {'position': loop([[0, 0, 0], [0, 0.9, 0], [0, 0, 0], [0, 0.9, 0]], 0.8), 'rotation': loop([[4, 0, 4], [4, 0, -4]], 0.8)},
            'arm_r': {'rotation': loop([ar, [-34, 0, -12]], 0.8)}, 'arm_l': {'rotation': loop([al, [-56, 42, 0]], 0.8)},
            'gun': {'rotation': loop([[0, 0, 0], [-3, 0, 0]], 0.8)},
            'beard': {'rotation': loop([[-3, 0, 3], [-3, 0, -3]], 0.8)}}
    m.anim('walk', 0.8, 'loop', walk)
    # attack 0.7 s: level the gun, BOOM (flash + recoil kick), settle
    att = {'gun': {'rotation': kf((0, [0, 0, 0]), (0.14, [4, 0, 0]), (0.2, [-28, 0, 0]), (0.34, [-12, 0, 0]), (0.7, [0, 0, 0])),
                   'position': kf((0, [0, 0, 0]), (0.14, [0, 0, -0.6]), (0.2, [0, 0, 3]), (0.34, [0, 0, 1.2]), (0.7, [0, 0, 0]))},
           'muzzle': {'scale': kf((0, [1, 1, 1]), (0.18, [1, 1, 1]), (0.21, [7, 7, 7]), (0.28, [4, 4, 4]), (0.34, [1, 1, 1]))},
           'body': {'rotation': kf((0, [0, 0, 0]), (0.14, [4, 0, 0]), (0.2, [-12, 0, 0]), (0.34, [-5, 0, 0]), (0.7, [0, 0, 0])),
                    'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 1.8]), (0.4, [0, 0, 0.6]), (0.7, [0, 0, 0]))},
           'arm_r': {'rotation': kf((0, ar), (0.2, [-48, 0, -12]), (0.34, [-40, 0, -12]), (0.7, ar))},
           'arm_l': {'rotation': kf((0, al), (0.2, [-70, 42, 0]), (0.34, [-62, 42, 0]), (0.7, al))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.2, [-10, 0, 0]), (0.4, [0, 0, 0]))},
           'beard': {'rotation': kf((0, [0, 0, 0]), (0.2, [-14, 0, 0]), (0.36, [6, 0, 0]), (0.7, [0, 0, 0]))}}
    m.anim('attack', 0.7, 'once', att)
    common_tail(m)
    return m


# =================================================================== BANDIT (HQ)
def bandit():
    """CR Bandit (0.85x): white hair with chunky bangs and a ponytail, black eye mask with teal eyes, wide grin,
    forest-green hooded cloak with a team patch, team-coloured tunic, brown belt and gloves, short leather blackjack. Extra: dash."""
    m = Model('clash_bandit', density=2.0)
    m.mats_({
        'skin': ('#f8c8a8', 'skin'), 'eye': ('#ffffff', 'plain'), 'mouth': ('#8a2a32', 'plain'),
        'hair': ('#f2f0ec', 'hair'), 'hair_d': ('#c8c4c0', 'hair'), 'cloak': ('#2f5a34', 'cloth'), 'cloak_d': ('#1f4024', 'cloth'),
        'cloth': ('#efefef', 'cloth'), 'belt': ('#6a4426', 'leather'), 'glove': ('#7a4e2e', 'leather'), 'pants': ('#3a3438', 'cloth'),
        'boot': ('#3a2a22', 'leather'), 'sole': ('#1a120e', 'plain'), 'jack': ('#3a2e2a', 'leather'), 'jack_l': ('#6a5a4a', 'leather'),
        'mask': ('#141418', 'leather', {'stitch': False}), 'brass': ('#c8a040', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.5, 6.4, 0], root)
        rbox(lg, sx * 1.5, 2.4, 0, 2.2, 4.4, 2.4, 'pants', r=0.3)
        boot(lg, sx * 1.5, -0.2, 'boot', w=2.7, h=3.2, d=3.4, cuff='boot')
        cb(lg, sx * 1.5, 1.6, -1.9, 1.0, 0.8, 0.3, 'brass', noround=True)
        cb(lg, sx * 1.5, 1.8, -0.2, 2.9, 0.4, 3.6, 'belt', noround=True)
        cb(lg, sx * 1.5, 4.4, -0.2, 2.4, 0.4, 2.6, 'belt', noround=True)
    body = m.bone('body', [0, 6.4, 0], root)
    tt = m.bone('tc_tunic', [0, 6.4, 0], body)
    rbox(tt, 0, 5.8, 0, 7.0, 7.6, 4.4, 'cloth', r=1.0, decals={'north': [('rect', 0.46, 0.0, 0.54, 0.5, '#c8c8c8')]})
    rbox(tt, 0, 4.4, 0, 7.8, 2.4, 5.0, 'cloth', r=0.6)                                       # tunic hem
    rbox(body, 0, 6.8, 0, 7.6, 1.2, 5.0, 'belt', r=0.3)
    cb(body, 0, 6.7, -2.6, 1.4, 1.4, 0.4, 'brass', noround=True)
    rbox(body, -2.6, 5.0, -2.3, 2.0, 2.2, 1.4, 'belt', r=0.4)                                 # coin pouch
    cb(body, -2.6, 7.0, -2.3, 1.2, 0.5, 1.0, 'brass', noround=True)
    rbox(body, 0, 4.0, 2.9, 8.2, 9.8, 0.8, 'cloak', r=0.3, decals={'south': [('rect', 0.3, 0.0, 0.34, 1.0, '#1f4024'), ('rect', 0.66, 0.0, 0.7, 1.0, '#1f4024')]})
    for sx in (1, -1):
        cb(body, sx * 2.6, 2.6, 3.0, 3.2, 2.0, 0.7, 'cloak', rot=('z', sx * 22.5), noround=True)
        cb(body, sx * 4.2, 6.6, 1.8, 0.8, 7.0, 2.6, 'cloak', noround=True)
    rbox(body, 0, 12.4, 0.3, 8.8, 2.0, 5.6, 'cloak', r=0.7)
    for sx in (1, -1):
        rbox(body, sx * 3.0, 12.0, -0.4, 2.4, 2.0, 4.6, 'cloak', r=0.5)                       # cloak shoulder folds
        cb(body, sx * 1.6, 12.8, -2.4, 1.6, 1.6, 0.6, 'cloak_d', rot=('z', sx * 22.5), noround=True)
    cb(body, 0, 12.6, -2.8, 1.4, 1.4, 0.5, 'brass', noround=True)                             # cloak clasp
    tp = m.bone('tc_patch', [0, 9, 3.4], body)
    cb(tp, 0, 8.0, 3.4, 3.0, 3.0, 0.4, 'cloth', noround=True)
    head = m.bone('head', [0, 14, 0], body)
    rbox(head, 0, 13.8, -0.1, 9.0, 8.8, 8.4, 'skin', r=1.5, decals={'north': [('rect', 0.06, 0.62, 0.2, 0.7, '#f4a8a0'), ('rect', 0.8, 0.62, 0.94, 0.7, '#f4a8a0')]})
    # 3D black eye mask with teal eyes
    rbox(head, 0, 17.4, -4.4, 9.4, 2.8, 0.8, 'mask', r=0.3)
    for sx in (1, -1):
        cb(head, sx * 5.0, 17.8, -2.8, 0.7, 2.0, 3.2, 'mask', noround=True)
        cb(head, sx * 5.2, 17.0, 1.2, 0.5, 1.4, 2.4, 'mask', rot=('x', 22.5), noround=True)      # knot tails
    eyes(head, 2.1, 17.6, -4.85, 2.4, 2.2, '#2ac0a8', lid='#141418')
    cb(head, 0, 16.6, -4.7, 1.0, 1.0, 0.6, 'skin', noround=True)                                   # nose
    cb(head, 0, 14.6, -4.45, 4.2, 1.6, 0.3, 'mouth', decals={'north': [('rect', 0.0, 0.0, 1.0, 0.35, '#ffffff'), ('rect', 0.25, 0.65, 0.75, 1.0, '#e05a6a'),
                                                                     ('rect', 0.0, 0.7, 0.12, 1.0, '#f8c8a8'), ('rect', 0.88, 0.7, 1.0, 1.0, '#f8c8a8')]}, dens=4, noround=True)  # wide open grin
    for sx in (1, -1):
        cb(head, sx * 2.3, 16.0, -4.45, 0.6, 0.6, 0.3, 'mouth', noround=True)                          # upturned corners
    # white hair: crown, chunky bangs, side locks, ponytail
    rbox(head, 0, 21.0, 0.3, 9.6, 2.6, 9.2, 'hair', r=1.0)
    for i, (x, h) in enumerate(((-3.8, 2.6), (-2.0, 3.0), (-0.4, 2.8), (1.2, 3.0), (2.8, 2.6), (4.0, 2.2))):
        cb(head, x, 21.4 - h, -4.5, 1.8, h, 0.9, 'hair' if i % 2 else 'hair_d', noround=True)
    for sx in (1, -1):
        rbox(head, sx * 4.6, 14.4, -0.8, 1.0, 7.4, 6.2, 'hair', r=0.3)
        cb(head, sx * 4.5, 13.6, -2.8, 1.0, 2.0, 1.4, 'hair_d', noround=True)
    rbox(head, 0, 15.0, 4.4, 9.4, 6.8, 1.0, 'hair', r=0.3)
    pt = m.bone('ponytail', [0, 20, 5], head)
    rbox(pt, 0, 17.6, 5.6, 2.6, 2.6, 2.6, 'hair', r=0.5)
    rbox(pt, 0, 13.4, 6.2, 2.4, 4.6, 2.2, 'hair', r=0.5)
    rbox(pt, 0, 10.4, 6.4, 1.8, 3.2, 1.8, 'hair_d', r=0.4)
    cb(pt, 0, 17.0, 5.4, 2.8, 0.8, 2.8, 'cloak_d', noround=True)                                 # tie
    # forest-green hood
    rbox(head, 0, 22.6, 0.8, 10.6, 1.8, 9.6, 'cloak', r=0.7)
    for sx in (1, -1):
        rbox(head, sx * 5.3, 15.0, 0.9, 0.9, 8.6, 8.6, 'cloak', r=0.3)
    rbox(head, 0, 19.0, 5.1, 10.6, 5.2, 0.9, 'cloak', r=0.3)
    cb(head, 0, 23.0, -4.0, 10.8, 1.0, 1.0, 'cloak_d', noround=True)
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 4.5, 12.8, 0], body)
        ts = m.bone('tc_sleeve_' + side, [sx * 4.5, 12.8, 0], arm)
        rbox(ts, sx * 4.6, 10.0, 0, 2.6, 3.0, 2.8, 'cloth', r=0.6)
        rbox(arm, sx * 4.6, 7.6, 0, 2.4, 2.6, 2.6, 'glove', r=0.3)
        fist(arm, sx * 4.6, 5.8, -0.1, 'glove', w=2.6, h=2.2, d=2.8, sx=sx)
    club = m.bone('club', [4.6, 6.9, -0.4], m.by_name('arm_r'))                          # short leather blackjack (points forward)
    cb(club, 4.6, 6.4, -2.8, 1.1, 1.1, 5.0, 'jack_l', noround=True)
    for z in (-1.4, -2.6, -3.8):
        cb(club, 4.6, 6.3, z, 1.4, 1.4, 0.5, 'jack', noround=True)                              # grip wraps
    rbox(club, 4.6, 5.7, -6.0, 2.4, 2.4, 2.6, 'jack', r=0.5)
    rbox(club, 4.6, 5.5, -8.2, 2.8, 2.8, 2.4, 'jack', r=0.7, decals={'north': [('rect', 0.2, 0.25, 0.4, 0.4, '#6a5a4a')]})
    cb(club, 4.6, 5.4, 0.6, 0.4, 1.6, 1.6, 'jack_l', noround=True)                              # wrist strap
    m.hitbox(0.8, 1.7)

    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 1.6)},
            'head': {'rotation': loop([[0, 8, 0], [2, 0, 0], [0, -8, 0], [2, 0, 0]], 1.6)},
            'arm_r': {'rotation': loop([[-20, 0, 6], [-24, 0, 6]], 1.6)}, 'club': {'rotation': loop([[-10, 0, 0], [-14, 0, 0]], 1.6)},
            'arm_l': {'rotation': loop([[0, 0, -6], [-4, 0, -8]], 1.6)},
            'ponytail': {'rotation': loop([[4, 0, 4], [8, 0, -4]], 1.6)}}
    m.anim('idle', 1.6, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[32, 0, 0], [-32, 0, 0]], 0.6)}, 'leg_l': {'rotation': loop([[-32, 0, 0], [32, 0, 0]], 0.6)},
            'body': {'position': loop([[0, 0, 0], [0, 0.9, 0], [0, 0, 0], [0, 0.9, 0]], 0.6), 'rotation': loop([[8, 4, 0], [8, -4, 0]], 0.6)},
            'arm_r': {'rotation': loop([[-30, 0, 6], [-14, 0, 6]], 0.6)}, 'club': {'rotation': loop([[-10, 0, 0], [-10, 0, 0]], 0.6)},
            'arm_l': {'rotation': loop([[28, 0, -4], [-28, 0, -4]], 0.6)},
            'ponytail': {'rotation': loop([[20, 0, 6], [32, 0, -6]], 0.3)}}
    m.anim('walk', 0.6, 'loop', walk)
    # attack 0.5 s: club raised high, then a hard downward swing
    att = {'arm_r': {'rotation': kf((0, [-20, 0, 6]), (0.18, [-165, 0, 10]), (0.28, [-50, 0, -4]), (0.36, [-35, 0, -6]), (0.5, [-20, 0, 6]))},
           'club': {'rotation': kf((0, [-10, 0, 0]), (0.18, [15, 0, 0]), (0.28, [140, 0, 0]), (0.36, [130, 0, 0]), (0.5, [-10, 0, 0]))},
           'body': {'rotation': kf((0, [0, 0, 0]), (0.18, [-10, 14, 0]), (0.28, [16, -10, 0]), (0.36, [14, -8, 0]), (0.5, [0, 0, 0]))},
           'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.18, [-40, 0, -24]), (0.28, [20, 0, -10]), (0.5, [0, 0, 0]))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.18, [-8, 0, 0]), (0.28, [6, 0, 0]), (0.5, [0, 0, 0]))}}
    m.anim('attack', 0.5, 'once', att)
    # dash 0.4 s: crouch, then a long forward lunge with the body leaning far forward
    m.anim('dash', 0.4, 'once', {
        'body': {'rotation': kf((0, [0, 0, 0]), (0.08, [12, 0, 0]), (0.2, [42, 0, 0]), (0.32, [40, 0, 0]), (0.4, [0, 0, 0]))},
        'root': {'position': kf((0, [0, 0, 0]), (0.08, [0, -1, 1]), (0.2, [0, -1.5, -6]), (0.32, [0, -1, -8]), (0.4, [0, 0, 0]))},
        'leg_r': {'rotation': kf((0, [0, 0, 0]), (0.2, [-50, 0, 0]), (0.32, [-40, 0, 0]), (0.4, [0, 0, 0]))},
        'leg_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [45, 0, 0]), (0.32, [40, 0, 0]), (0.4, [0, 0, 0]))},
        'arm_r': {'rotation': kf((0, [-20, 0, 6]), (0.2, [50, 0, 10]), (0.32, [45, 0, 10]), (0.4, [-20, 0, 6]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [55, 0, -10]), (0.32, [50, 0, -10]), (0.4, [0, 0, 0]))},
        'head': {'rotation': kf((0, [0, 0, 0]), (0.2, [-30, 0, 0]), (0.32, [-28, 0, 0]), (0.4, [0, 0, 0]))},
        'ponytail': {'rotation': kf((0, [4, 0, 0]), (0.2, [70, 0, 0]), (0.4, [4, 0, 0]))}})
    common_tail(m)
    return m


MODELS = [witch, night_witch, wizard, dart_goblin, goblin_brawler, heal_spirit,
          princess, ice_wizard, magic_archer, hunter, bandit]



# =================================================================== preview
def preview(path, out_png, extra=()):
    from bbrender import render, sample
    from PIL import Image, ImageDraw
    doc = json.load(open(path))
    names = {a['name']: a['length'] for a in doc['animations']}
    tint = (60, 110, 255)
    shots = [('idle front', None, (0.6, 0.5, -1.0)), ('idle back', None, (-0.7, 0.45, 1.0)), ('idle side', None, (1.0, 0.2, -0.05))]
    L = names['attack']
    for f in (0.3, 0.5, 0.75):
        shots.append(('attack %.2f' % (L * f), ('attack', L * f), (0.9, 0.35, -0.6)))
    shots.append(('walk', ('walk', names['walk'] * 0.25), (0.6, 0.5, -1.0)))
    for extra_an in ('summon', 'dash'):
        if extra_an in names:
            shots.append((extra_an, (extra_an, names[extra_an] * 0.5), (0.9, 0.35, -0.6)))
    S = 260
    sheet = Image.new('RGBA', (S * 4, S * 3 + 30), (255, 255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (lab, an, cam) in enumerate(shots):
        pose = sample(doc, an[0], an[1]) if an else sample(doc, 'idle', 0)
        im = render(doc, S, cam=cam, tint=tint, pose=pose)
        x, y = (i % 4) * S, (i // 4) * (S + 10)
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + 2), lab, fill=(0, 0, 0, 255))
    # tiny 'from 15 blocks' render (red team), upscaled
    small = render(doc, 36, cam=(0.6, 0.5, -1.0), tint=(255, 70, 60), pose=sample(doc, 'idle', 0)).resize((144, 144), Image.NEAREST)
    small2 = render(doc, 36, cam=(0.6, 0.5, -1.0), tint=tint, pose=sample(doc, 'idle', 0)).resize((144, 144), Image.NEAREST)
    i = len(shots)
    x, y = (i % 4) * S, (i // 4) * (S + 10)
    sheet.paste(small, (x, y + 10)); sheet.paste(small2, (x + 116, y + 110))
    dr.text((x + 4, y + 2), 'far (36px)', fill=(0, 0, 0, 255))
    sheet.save(out_png)


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
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad, [(a['name'], a['length']) for a in m.anims])
        preview(p, os.path.join(out, 'preview_' + m.name + '.png'))
