"""New models (batch m2): P.E.K.K.A, dark prince, sparky, battle ram, cannon cart, broken cannon cart (bbgen2, BetterModel).
Units: pixels (16 = 1 block), front = north (-Z), origin = centre of the feet.
Animations: idle / walk / attack / spawn(->deploy) / hit / death (+ sparky 'charge').
Role-readable original designs, not based on any existing game's characters.
Usage: python3 models_m2.py <model_tools dir> <out dir> [--no-preview] [names...]"""
import sys, os, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """box centred on (x, z), bottom at y"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    """evenly spaced keyframes (last = first)"""
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def spin(length, axis=0, turns=1, steps=4):
    """continuous rotation (wheel roll): 0 -> 360*turns"""
    out = []
    for i in range(steps + 1):
        v = [0, 0, 0]
        v[axis] = 360.0 * turns * i / steps
        out.append((round(length * i / steps, 4), v))
    return out


def common_tail(m, root='root', hit_bone='body', death=None, spawn=None, extra=None):
    ex = extra or {}
    m.anim('spawn', 0.5, 'once', dict(ex, **(spawn or {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                                  'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})))
    m.anim('hit', 0.3, 'once', dict(ex, **{hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}}))
    m.anim('death', 0.9, 'hold', dict(ex, **(death or {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                                  'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})))


def wheel(bone, x, y, z, r, t, mat, hub, spoke, side):
    """wheel disc in the y-z plane (axle along x), centre (x, y, z). side = +1/-1 for the hub cap"""
    sp = [('rect', 0.43, 0.0, 0.57, 1.0, spoke), ('rect', 0.0, 0.43, 1.0, 0.57, spoke)]
    rim = [('shade', 0, 0, 1, 0.1, 0.7), ('shade', 0, 0.9, 1, 1, 0.7)]
    cb(bone, x, y - r, z, t, 2 * r, 1.0 * r, mat, decals={'east': sp + rim, 'west': sp + rim})
    cb(bone, x, y - 0.5 * r, z, t, 1.0 * r, 2 * r, mat, decals={'east': sp, 'west': sp})
    s = 1.7 * r                                                           # corner fill -> stepped round outline
    cb(bone, x, y - s / 2, z, t * 0.96, s, s, mat, decals={'east': sp, 'west': sp})
    cb(bone, x + side * (t / 2 + 0.5), y - 1.4, z, 1.0, 2.8, 2.8, hub)
    cb(bone, x - side * (t / 2 + 0.3), y - 1.0, z, 0.6, 2.0, 2.0, hub)


# =================================================================== P.E.K.K.A
def pekka():
    """Huge armoured knight robot: bulky dark blue-purple plate, horned helm with purple eye slits,
    great sword held one-handed in the right fist (grip through the fist, forearm forward), blade raised upright at rest.
    Attack: sword up and back over the right shoulder, then a big diagonal chop to the front-left."""
    m = Model('clash_pekka', density=1.0)
    m.mats_({
        'plate': ('#3b3f68', 'metal', {'rivets': True}), 'plate_d': ('#252743', 'metal'), 'plate_l': ('#5c6194', 'metal', {'rivets': True}),
        'joint': ('#16172a', 'metal'), 'horn': ('#d9cdb3', 'bone'), 'eye': ('#c45bff', 'glow'), 'core': ('#a13cf0', 'glow'),
        'blade': ('#b3bdca', 'metal'), 'edge': ('#e6edf5', 'metal'), 'grip': ('#3a2a20', 'leather'),
        'tcm': ('#e8e8e8', 'metal'), 'cloth': ('#efefef', 'cloth'),
    })
    rune = [('rect', 0.4, 0.04, 0.6, 0.94, '#5a2c86'), ('rect', 0.44, 0.08, 0.56, 0.9, '#c45bff'),
            ('rect', 0.3, 0.25, 0.7, 0.28, '#c45bff'), ('rect', 0.3, 0.55, 0.7, 0.58, '#c45bff')]
    root = m.bone('root', [0, 0, 0])
    # ---- legs
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 5, 16, 0.5], root)
        cb(lg, sx * 5, 9.5, 0.5, 6.5, 7, 6.5, 'joint')
        cb(lg, sx * 5, 2.5, 0, 7.5, 7.5, 8, 'plate', decals={'north': [('rect', 0.42, 0.1, 0.58, 0.9, '#262842')]})
        cb(lg, sx * 5, 8.5, -4.2, 5.5, 4.5, 2, 'plate_l')
        cb(lg, sx * 5, 0, -1.2, 8.5, 3, 10.5, 'plate_d')
        cb(lg, sx * 5, 0, -6.8, 6.5, 2.2, 1.6, 'plate_l')
    # ---- body
    body = m.bone('body', [0, 16, 0.5], root)
    cb(body, 0, 13.5, 0.5, 17, 4.5, 12, 'plate_d')                          # hips / faulds
    cb(body, 0, 18, 0.5, 18, 13, 13, 'plate', decals={'east': [('rect', 0.1, 0.45, 0.9, 0.52, '#262842')],
                                                       'west': [('rect', 0.1, 0.45, 0.9, 0.52, '#262842')]})
    cb(body, 0, 20.5, -6.4, 14, 9.5, 1.8, 'plate_l', decals={'north': [('rect', 0.47, 0.0, 0.53, 1.0, '#7a80b4'),
                                                                        ('rect', 0.05, 0.92, 0.95, 1.0, '#262842')]})
    cb(body, 0, 18.2, -6.3, 12, 2, 1.6, 'plate_d')
    cb(body, 0, 30, -0.5, 12, 3, 10, 'plate_d')                             # gorget
    cb(body, 0, 19.5, 7.5, 14, 10, 2, 'plate_d', decals={'south': [('rect', 0.1, 0.2, 0.9, 0.26, '#3d4758'), ('rect', 0.1, 0.74, 0.9, 0.8, '#3d4758')]})
    cb(body, 0, 22, 8.9, 5, 5, 1, 'core')                                    # back power core
    cb(body, 0, 21.3, 9.5, 3, 6.4, 0.8, 'plate_d')
    for sx in (1, -1):                                                       # pauldrons
        cb(body, sx * 12, 27.5, 0.5, 8.5, 6.5, 12, 'plate')
        cb(body, sx * 12.3, 33, 0.5, 7, 2.5, 10, 'plate_l')
        cb(body, sx * 13.8, 34.5, 0.5, 2.6, 3.6, 2.6, 'plate_l', rot=('z', -sx * 22.5))
    tc = m.bone('tc_trim', [0, 16, 0.5], body)
    cb(tc, 0, 16.5, 0.5, 18.6, 2.2, 13.6, 'tcm', decals={'north': [('rect', 0.42, 0.0, 0.58, 1.0, '#9a9a9a')]})
    cb(tc, 0, 23, -7.9, 5, 4.5, 1, 'tcm', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#b8b8b8')]})
    cb(tc, 0, 8, -6.6, 6, 8.5, 0.8, 'cloth')
    cb(tc, 0, 9, 6.9, 7, 7.5, 0.8, 'cloth')
    for sx in (1, -1):
        cb(tc, sx * 12, 27.2, 0.5, 9.1, 1.4, 12.6, 'tcm')
    # ---- head (low between the shoulders)
    head = m.bone('head', [0, 31.5, -1], body)
    visor = [('rect', 0.06, 0.36, 0.94, 0.6, '#0b0d12'), ('rect', 0.12, 0.43, 0.42, 0.53, '#c45bff'),
             ('rect', 0.58, 0.43, 0.88, 0.53, '#c45bff'), ('rect', 0.2, 0.45, 0.34, 0.51, '#f6dcff'),
             ('rect', 0.66, 0.45, 0.8, 0.51, '#f6dcff'), ('rect', 0.46, 0.6, 0.54, 0.94, '#1a1e26'),
             ('rect', 0.28, 0.74, 0.4, 0.8, '#1a1e26'), ('rect', 0.6, 0.74, 0.72, 0.8, '#1a1e26')]
    cb(head, 0, 31, -1.5, 10, 10, 10, 'plate', decals={'north': visor})
    for sx in (1, -1):
        cb(head, sx * 2.6, 35.15, -6.75, 3.0, 0.9, 0.5, 'eye')               # slit glow
    cb(head, 0, 40.6, -1.5, 2.2, 1.8, 10.6, 'plate_l')                      # crest
    cb(head, 0, 30.5, -6.6, 7, 3, 1.5, 'plate_d')                           # chin guard
    for sx in (1, -1):                                                       # horns: out, up, curl
        cb(head, sx * 6.2, 35.5, -1.5, 3.2, 3, 3.2, 'horn')
        cb(head, sx * 8.4, 37.4, -1.5, 2.6, 5, 2.6, 'horn', rot=('z', -sx * 22.5))
        cb(head, sx * 9.2, 41.6, -1.5, 1.8, 3.4, 1.8, 'horn', rot=('z', sx * 22.5))
    # ---- right arm -> hand_r (closed fist) -> sword. The grip runs straight THROUGH the fist; the sword pivot is
    #      the grip centre inside the fist, so the sword can never separate from the hand.
    ar = m.bone('arm_r', [12, 29, 0.5], body)
    cb(ar, 12.5, 22, 0.5, 6, 7, 6.5, 'joint')                               # upper arm hangs down
    cb(ar, 12.7, 20.5, 0.5, 7, 3.5, 7.5, 'plate_l')                         # elbow cop (elbow bent 90 deg)
    cb(ar, 14.9, 20.3, -3.5, 6.2, 4.4, 8.5, 'plate', decals={'up': [('rect', 0.4, 0.0, 0.6, 1.0, '#262842')]})   # forearm, horizontal forward
    cb(ar, 16.3, 20.0, -7.4, 5.8, 5.0, 1.2, 'plate_l')                      # gauntlet cuff
    H = (16.5, 22.5, -10.3)                                                  # fist centre = grip centre (belly height, in front)
    hand = m.bone('hand_r', list(H), ar)
    hx, hy, hz = H
    fing = [('rect', 0.0, y, 1.0, y + 0.1, '#262842') for y in (0.25, 0.5, 0.75)]
    R = dict(rot=('x', -22.5), rot_origin=list(H))                          # grip vertical through the fist (perpendicular to the
    cb(hand, hx, hy - 2.5, hz, 5.0, 5.0, 5.0, 'plate_l', decals={'east': fing, 'west': fing, 'north': fing}, **R)   # forearm), blade UP
    sw = m.bone('sword', list(H), hand)
    # bottom -> top along the grip axis: pommel | grip through the fist | crossguard | blade pointing up
    cb(sw, hx, hy - 6.8, hz, 3.2, 2.8, 3.2, 'plate_l', **R)                 # pommel just below the fist (rel -6.8..-4)
    cb(sw, hx, hy - 4.0, hz, 1.8, 7.5, 1.8, 'grip', **R)                    # grip rel -4..+3.5 (fist -2.5..+2.5): out both ends
    cb(sw, hx, hy + 3.5, hz, 3.4, 1.8, 3.4, 'plate_d', **R)                 # crossguard just above the fist
    cb(sw, hx, hy + 3.5, hz, 12.0, 1.8, 2.4, 'plate_d', **R)
    cb(sw, hx, hy + 3.8, hz - 1.5, 2.4, 1.2, 0.6, 'core', **R)
    for sx in (1, -1):
        cb(sw, hx + sx * 6.6, hy + 2.9, hz, 1.8, 3.0, 2.6, 'plate_l', **R)
    rune_v = [('rect', 0.42, 0.06, 0.58, 0.96, '#5a2c86'), ('rect', 0.46, 0.1, 0.54, 0.92, '#c45bff'),
              ('rect', 0.3, 0.35, 0.7, 0.38, '#c45bff'), ('rect', 0.3, 0.67, 0.7, 0.7, '#c45bff')]
    cb(sw, hx, hy + 5.3, hz, 1.8, 12.2, 6.0, 'blade', decals={'east': rune_v, 'west': rune_v}, **R)   # blade rel +5.3..+17.5
    for sz in (1, -1):
        cb(sw, hx, hy + 5.4, hz + sz * 3.3, 1.1, 12.0, 1.0, 'edge', **R)
    cb(sw, hx, hy + 17.5, hz, 1.8, 2.0, 4.4, 'blade', **R)
    cb(sw, hx, hy + 19.5, hz, 1.8, 1.6, 2.2, 'edge', **R)
    # ---- left arm: free clenched fist at the left side
    al = m.bone('arm_l', [-12, 29, 0.5], body)
    cb(al, -12.5, 21, 0.5, 6, 8, 6.5, 'joint')
    cb(al, -12.7, 19.5, 0.5, 7, 3.5, 7.5, 'plate_l')
    cb(al, -13.0, 16.0, -0.4, 5.4, 4.6, 5.8, 'plate')
    cb(al, -13.0, 16.6, -0.4, 6.4, 1.6, 6.8, 'plate_l')
    cb(al, -13.0, 11.6, -0.6, 5.0, 4.6, 5.0, 'plate_l', decals={'north': fing, 'west': fing})
    m.scale_bone('root', 1.2, [0, 0, 0])                                     # 1.2x bigger
    m.hitbox(1.7, 3.3)

    # ---------------- animations (hand_r +5 at rest -> blade down, about 17 deg forward of vertical)
    HR = {'hand_r': {'rotation': [(0, [-10, 0, 0])]}}
    m.anim('idle', 2.4, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.5, 0]], 2.4), 'rotation': loop([[0, 0, 0], [1.5, 0, 0]], 2.4)},
        'arm_r': {'rotation': loop([[0, 0, 0], [-3, 0, 0]], 2.4)},
        'hand_r': {'rotation': loop([[-10, 0, 0], [-8, 0, 0]], 2.4)},
        'arm_l': {'rotation': loop([[0, 0, -2], [3, 0, -3]], 2.4)},
        'head': {'rotation': loop([[0, 10, 0], [0, 0, 0], [0, -10, 0], [0, 0, 0]], 4.8)}})
    L = 1.2
    m.anim('walk', L, 'loop', {
        'leg_r': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], L)},
        'leg_l': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], L)},
        'arm_l': {'rotation': loop([[-14, 0, -2], [14, 0, -2]], L)},
        'arm_r': {'rotation': loop([[3, 0, 0], [-5, 0, 0]], L)},
        'hand_r': {'rotation': [(0, [-10, 0, 0]), (L, [-10, 0, 0])]},
        'body': {'position': loop([[0, 0, 0], [0, -1.4, 0], [0, 0, 0], [0, -1.4, 0]], L),
                 'rotation': loop([[3, 3, 3], [3, 0, 0], [3, -3, -3], [3, 0, 0]], L)},
        'head': {'rotation': loop([[0, -3, -2], [0, 0, 0], [0, 3, 2], [0, 0, 0]], L)}})
    # attack: sword up and back over the right shoulder (0.3-0.45), big diagonal chop down to the front-left (0.6), follow-through
    m.anim('attack', 1.0, 'once', {
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.3, [-145, 0, 20]), (0.45, [-152, 0, 24]), (0.6, [-40, 0, -24]),
                               (0.8, [-25, 0, -18]), (1.0, [0, 0, 0])]},
        'hand_r': {'rotation': [(0, [-10, 0, 0]), (0.3, [28, 0, 0]), (0.45, [32, 0, 0]), (0.6, [137, 0, 0]),
                                (0.8, [120, 0, 0]), (1.0, [-10, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.45, [-35, 0, -8]), (0.6, [20, 0, -12]), (1.0, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.45, [-8, 18, 0]), (0.6, [14, -22, 0]), (0.8, [12, -18, 0]), (1.0, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.45, [0, 0.8, 1]), (0.6, [0, -2, -1.5]), (0.8, [0, -1.6, -1.2]), (1.0, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (0.45, [-6, 0, 0]), (0.6, [-18, 0, 0]), (0.8, [-16, 0, 0]), (1.0, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.45, [4, 0, 0]), (0.6, [12, 0, 0]), (0.8, [10, 0, 0]), (1.0, [0, 0, 0])]},
        'head': {'rotation': [(0, [0, 0, 0]), (0.45, [6, -10, 0]), (0.6, [-10, 12, 0]), (1.0, [0, 0, 0])]}})
    common_tail(m, extra=HR, death={
        'root': {'rotation': [(0, [0, 0, 0]), (0.3, [-8, 0, 0]), (0.7, [80, 0, 0]), (0.9, [88, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.3, [0, -2, 0]), (0.9, [0, -1, 0])]},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.6, [-80, 0, 0]), (0.9, [-88, 0, 0])]},
        'hand_r': {'rotation': [(0, [-10, 0, 0]), (0.6, [55, 0, 0]), (0.9, [67, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.9, [-60, 0, -20])]},
        'head': {'rotation': [(0, [0, 0, 0]), (0.6, [-20, 0, 15])]}})
    for an in m.anims:                                                       # animation distances follow the 1.2x scale
        for ch in an['tracks'].values():
            if 'position' in ch:
                ch['position'] = [(t, [v * 1.2 for v in val]) for t, val in ch['position']]
    return m


# =================================================================== Dark prince
def dark_prince():
    """Dark armoured rider on a black barded horse: spiked helm, spiked mace, round shield (bone 'shield'),
    team-coloured cape. Walk = gallop, attack = overhead mace swing."""
    m = Model('clash_dark_prince', density=1.25)
    m.mats_({
        'horse': ('#3a3442', 'fur'), 'horse_d': ('#241f2a', 'fur'), 'mane': ('#5e2a82', 'hair'), 'hoof': ('#111114', 'plain'),
        'arm': ('#2b2d35', 'metal', {'rivets': True}), 'arm_d': ('#17181d', 'metal'), 'arm_l': ('#4c505c', 'metal', {'rivets': True}),
        'spike': ('#b4bac6', 'metal'), 'leather': ('#3d2418', 'leather'), 'iron': ('#5a5e68', 'metal', {'rivets': True}),
        'wood': ('#4a3020', 'wood'), 'glow': ('#ff5a2a', 'glow'), 'capd': ('#1e1c24', 'cloth'), 'cloth': ('#efefef', 'cloth'),
        'emb': ('#7a1f2a', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 12.5, 0], root)
    # ---- horse legs (gallop pairs)
    for name, x, z in (('fl_leg', -3.0, -7), ('fr_leg', 3.0, -7), ('bl_leg', -3.0, 8.5), ('br_leg', 3.0, 8.5)):
        lg = m.bone(name, [x, 12.5, z], body)
        cb(lg, x, 6, z, 3.2, 7, 3.4, 'horse')
        cb(lg, x, 1.6, z, 2.8, 4.8, 3.0, 'horse_d')
        cb(lg, x, 0, z - 0.2, 3.4, 1.8, 3.6, 'hoof')
        if z < 0:                                                          # front greaves with a spike
            cb(lg, x, 6.5, z - 1.9, 3.4, 4, 0.8, 'arm')
            cb(lg, x, 7.8, z - 2.8, 0.9, 0.9, 1.4, 'spike')
    # ---- horse body + barding
    cb(body, 0, 9, 0.8, 11, 10, 22, 'horse', decals={'east': [('rect', 0.1, 0.2, 0.9, 0.24, '#3a3542')],
                                                     'west': [('rect', 0.1, 0.2, 0.9, 0.24, '#3a3542')]})
    cb(body, 0, 9.5, -10.6, 11.6, 8.5, 1.8, 'arm', decals={'north': [('rect', 0.46, 0.0, 0.54, 1.0, '#4c505c')]})
    for x in (-3.4, 0, 3.4):
        cb(body, x, 13.6, -12.6, 1.2, 1.2, 2.6, 'spike')
    cb(body, 0, 8.8, 2, 11.8, 7.8, 14.5, 'capd')                              # dark caparison
    cb(body, 0, 18.6, 9, 10.4, 1.4, 6, 'arm')                                # crupper plate
    for x in (-2.5, 2.5):
        cb(body, x, 19.6, 10, 1, 1.6, 1, 'spike')
    cb(body, 0, 18.8, 0.8, 8.2, 1.6, 7.5, 'leather')                         # saddle
    tcb = m.bone('tc_trim', [0, 12.5, 0], body)
    cb(tcb, 0, 8.4, 2, 12.2, 1.6, 14.9, 'cloth')
    cb(tcb, 0, 15.9, 2, 12.0, 0.8, 14.7, 'cloth')
    tail = m.bone('tail', [0, 17.5, 11.5], body)
    cb(tail, 0, 16.0, 12.4, 3.0, 3.0, 2.4, 'mane')
    cb(tail, 0, 9.0, 13.6, 3.4, 9.0, 3.0, 'mane', rot=('x', -22.5))
    cb(tail, 0, 6.0, 15.2, 2.6, 4, 2.4, 'mane', rot=('x', -22.5), rot_origin=[0, 13.5, 13.6])
    # ---- horse neck / head
    head = m.bone('head', [0, 17, -9], body)
    NR = dict(rot=('x', -22.5), rot_origin=[0, 20.25, -12])
    cb(head, 0, 15.5, -12.0, 6.4, 9.5, 7.2, 'horse', **NR)
    cb(head, 0, 17.0, -12.8, 7.0, 4.5, 6.4, 'arm', **NR)                    # neck armour (crinet)
    cb(head, 0, 15.0, -8.0, 2.0, 11, 2.2, 'mane', **NR)
    cb(head, 0, 19.8, -6.6, 0.9, 0.9, 1.8, 'spike', **NR)
    eye = [('rect', 0.15, 0.3, 0.4, 0.5, '#ff5a2a'), ('rect', 0.2, 0.35, 0.3, 0.45, '#ffd0a0')]
    cb(head, 0, 23.5, -16.5, 5.4, 5.4, 8, 'horse', decals={'east': eye, 'west': [(k, 1 - x1, y0, 1 - x0, y1, c) for (k, x0, y0, x1, y1, c) in eye]})
    cb(head, 0, 22.8, -21.2, 4.4, 4.2, 3, 'horse_d', decals={'north': [('rect', 0.15, 0.3, 0.35, 0.5, '#050506'), ('rect', 0.65, 0.3, 0.85, 0.5, '#050506')]})
    cb(head, 0, 26.6, -18.2, 6.0, 3, 7.4, 'arm')                             # chamfron
    cb(head, 0, 28.5, -20.5, 1.4, 4, 1.4, 'spike', rot=('x', -22.5))        # forehead spike
    for sx in (1, -1):
        cb(head, sx * 1.9, 28.6, -14.2, 1.2, 2.8, 1.2, 'horse_d')
    cb(head, 0, 28.6, -14.5, 1.4, 2.4, 3.5, 'mane')
    # ---- rider
    rider = m.bone('rider', [0, 20, 1], body)
    for sx in (1, -1):
        cb(rider, sx * 5.3, 14.6, 0.6, 2.8, 6, 3.6, 'arm_d')
        cb(rider, sx * 5.5, 12.4, -0.2, 3, 2.6, 4.8, 'arm')
        cb(rider, sx * 6.9, 12.9, 0.6, 0.8, 0.8, 1.4, 'spike')
    cb(rider, 0, 19.8, 1, 8, 3, 5.5, 'arm_d')
    cb(rider, 0, 22.5, 1, 9, 7.5, 5.6, 'arm', decals={'north': [('rect', 0.46, 0.05, 0.54, 0.95, '#4c505c'),
                                                                ('rect', 0.15, 0.08, 0.85, 0.16, '#4c505c')]})
    cb(rider, 0, 22, -1.9, 9.4, 1.2, 0.6, 'emb')
    for sx in (1, -1):                                                       # spiked pauldrons
        cb(rider, sx * 5.8, 27.8, 1, 4.4, 3.6, 5.8, 'arm_l')
        cb(rider, sx * 6.6, 31.2, 1, 1.4, 3, 1.4, 'spike', rot=('z', -sx * 22.5))
        cb(rider, sx * 6.2, 31.0, 3.0, 1.1, 2.2, 1.1, 'spike', rot=('z', -sx * 22.5))
    cape = m.bone('tc_cape', [0, 29.5, 4], rider)
    cb(cape, 0, 18, 4.4, 8.6, 11.5, 0.9, 'cloth', decals={'south': [('rect', 0.0, 0.0, 1.0, 0.08, '#c8c8c8')]})
    cb(cape, 0, 15.5, 4.9, 9.8, 3, 0.9, 'cloth', decals={'south': [('rect', 0.2, 0.7, 0.3, 1.0, '#cfcfcf'), ('rect', 0.6, 0.7, 0.7, 1.0, '#cfcfcf')]})
    cb(cape, 0, 28.4, 3.9, 9.2, 1.6, 1.4, 'cloth')
    rh = m.bone('rider_head', [0, 30, 1], rider)
    visor = [('rect', 0.08, 0.36, 0.92, 0.5, '#08080a'), ('rect', 0.4, 0.5, 0.6, 0.86, '#08080a'),
             ('rect', 0.16, 0.39, 0.38, 0.47, '#ff5a2a'), ('rect', 0.62, 0.39, 0.84, 0.47, '#ff5a2a'),
             ('rect', 0.47, 0.0, 0.53, 0.34, '#4c505c')]
    cb(rh, 0, 30, 0.8, 6.6, 6.8, 6.6, 'arm', decals={'north': visor})
    cb(rh, 0, 29.6, 0.8, 7.4, 1.4, 7.4, 'arm_d')
    cb(rh, 0, 36.6, 0.8, 1.8, 3.6, 1.8, 'spike')
    cb(rh, 0, 39.9, 0.8, 0.9, 1.3, 0.9, 'spike')
    for sx in (1, -1):
        cb(rh, sx * 3.8, 34.5, 0.8, 1.2, 3.2, 1.2, 'spike', rot=('z', -sx * 45))
        cb(rh, sx * 2.6, 35.8, 3.4, 1.0, 2.4, 1.0, 'spike', rot=('x', 22.5))
    cb(rh, 0, 35.6, 4.2, 1.2, 2.6, 1.2, 'spike', rot=('x', 45))
    # right arm + mace
    ar = m.bone('arm_r', [5.6, 28.5, 1], rider)
    cb(ar, 5.9, 21.5, 1, 3, 7, 3.4, 'arm_d')
    cb(ar, 6.0, 20.2, 0.6, 3.6, 3.6, 4.2, 'arm')
    mace = m.bone('mace', [6.0, 22, 0.4], ar)
    gx, gy, gz = 6.0, 22, 0.4
    cb(mace, gx, gy - 3.5, gz, 1.3, 15, 1.3, 'wood')
    cb(mace, gx, gy - 4.3, gz, 1.8, 1, 1.8, 'iron')
    cb(mace, gx, gy + 10.8, gz, 2.0, 1.0, 2.0, 'iron')
    cb(mace, gx, gy + 11.4, gz, 5.4, 5.4, 5.4, 'iron')
    cb(mace, gx, gy + 11.7, gz, 4.8, 4.8, 4.8, 'iron', rot=('y', 45))
    cb(mace, gx, gy + 11.7, gz, 4.8, 4.8, 4.8, 'iron', rot=('x', 45))
    cb(mace, gx, gy + 16.6, gz, 1.4, 2.4, 1.4, 'spike')
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cb(mace, gx + dx * 3.6, gy + 13.5, gz + dz * 3.6, 2.0 if dx else 1.4, 1.4, 2.0 if dz else 1.4, 'spike')
    # left arm + round shield
    al = m.bone('arm_l', [-5.6, 28.5, 1], rider)
    cb(al, -5.9, 21.5, 1, 3, 7, 3.4, 'arm_d')
    cb(al, -5.6, 20.4, -1.6, 3.4, 3.4, 4.6, 'arm')
    sh = m.bone('shield', [-10.4, 23.5, 1.0], al)
    C = [-10.4, 23.5, 1.0]
    S = dict(rot=('y', 22.5), rot_origin=C)
    cx, cy, cz = C
    emblem = [('rect', 0.42, 0.06, 0.58, 0.94, '#b0283a'), ('rect', 0.06, 0.42, 0.94, 0.58, '#b0283a')]
    cb(sh, cx, cy - 6.2, cz, 6.6, 12.4, 1.2, 'spike', **S)
    cb(sh, cx, cy - 3.3, cz, 12.4, 6.6, 1.2, 'spike', **S)
    cb(sh, cx, cy - 4.8, cz, 9.6, 9.6, 1.2, 'spike', **S)
    cb(sh, cx, cy - 5.1, cz - 0.9, 5.2, 10.2, 0.6, 'arm', decals={'north': emblem}, **S)
    cb(sh, cx, cy - 2.6, cz - 0.9, 10.2, 5.2, 0.6, 'arm', decals={'north': emblem}, **S)
    cb(sh, cx, cy - 3.9, cz - 0.9, 7.8, 7.8, 0.6, 'arm', decals={'north': emblem}, **S)
    cb(sh, cx, cy - 1.4, cz - 1.6, 2.8, 2.8, 1.0, 'arm_l', **S)
    cb(sh, cx, cy - 0.5, cz - 2.9, 1.0, 1.0, 1.8, 'spike', **S)
    for dx, dy in ((3.3, 0), (-3.3, 0), (0, 3.3), (0, -3.3)):
        cb(sh, cx + dx, cy + dy - 0.5, cz - 1.3, 0.9, 1.0, 0.5, 'spike', **S)
    m.hitbox(1.4, 2.4)

    # ---------------- animations
    m.anim('idle', 2.0, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.0)},
        'head': {'rotation': loop([[0, 0, 0], [6, 4, 0], [0, 0, 0], [3, -4, 0]], 2.0)},
        'tail': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 2.0)},
        'tc_cape': {'rotation': loop([[6, 0, 0], [10, 0, 2]], 2.0)},
        'arm_r': {'rotation': loop([[-12, 0, 0], [-16, 0, 0]], 2.0)},
        'rider_head': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 4.0)}})
    L = 0.5
    def leg(a, b, ph):                 # gallop leg swing with phase shift
        keys = [a, (a + b) / 2, b, (a + b) / 2]
        n = len(keys)
        sh_ = int(round(ph * n)) % n
        keys = keys[sh_:] + keys[:sh_]
        return {'rotation': loop([[k, 0, 0] for k in keys], L)}
    m.anim('walk', L, 'loop', {
        'fl_leg': leg(-42, 26, 0), 'fr_leg': leg(-42, 26, 0.25),
        'bl_leg': leg(30, -28, 0.5), 'br_leg': leg(30, -28, 0.75),
        'body': {'rotation': loop([[-6, 0, 0], [0, 0, 0], [6, 0, 0], [0, 0, 0]], L),
                 'position': loop([[0, 2.2, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0]], L)},
        'head': {'rotation': loop([[10, 0, 0], [0, 0, 0], [-8, 0, 0], [0, 0, 0]], L)},
        'tail': {'rotation': loop([[-30, 0, 0], [-20, 0, 0]], L)},
        'rider': {'rotation': loop([[8, 0, 0], [2, 0, 0], [-4, 0, 0], [2, 0, 0]], L),
                  'position': loop([[0, -0.6, 0], [0, 0, 0], [0, 0.6, 0], [0, 0, 0]], L)},
        'arm_r': {'rotation': loop([[-24, 0, 0], [-18, 0, 0]], L)},
        'tc_cape': {'rotation': loop([[38, 0, 0], [48, 0, 3]], L)}})
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': [(0, [-14, 0, 0]), (0.28, [-152, 0, -12]), (0.36, [-156, 0, -14]), (0.46, [-62, 0, 8]),
                               (0.56, [-50, 0, 6]), (0.8, [-14, 0, 0])]},
        'mace': {'rotation': [(0, [0, 0, 0]), (0.28, [30, 0, 0]), (0.36, [36, 0, 0]), (0.46, [176, 0, 0]),
                              (0.56, [170, 0, 0]), (0.8, [0, 0, 0])]},
        'rider': {'rotation': [(0, [0, 0, 0]), (0.3, [-10, -18, 0]), (0.46, [14, 16, 0]), (0.6, [10, 10, 0]), (0.8, [0, 0, 0])]},
        'rider_head': {'rotation': [(0, [0, 0, 0]), (0.3, [-6, 10, 0]), (0.46, [8, -10, 0]), (0.8, [0, 0, 0])]},
        'head': {'rotation': [(0, [0, 0, 0]), (0.3, [-10, 0, 0]), (0.46, [6, 0, 0]), (0.8, [0, 0, 0])]},
        'tc_cape': {'rotation': [(0, [8, 0, 0]), (0.46, [30, 0, 0]), (0.8, [8, 0, 0])]}})
    common_tail(m, death={
        'root': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                 'position': [(0, [0, 0, 0]), (0.6, [0, -3, 0]), (0.9, [0, -6, 0])]},
        'rider': {'rotation': [(0, [0, 0, 0]), (0.5, [-25, 0, 0])]}})
    return m


# =================================================================== Sparky
def sparky():
    """Wheeled tesla-coil cannon cart: iron chassis, copper-wound barrel with glowing coil rings (bone 'coil'),
    coil tower with a glowing orb and a lightning sparkle, team flags. Anims incl. 'charge'."""
    m = Model('clash_sparky', density=1.25)
    m.mats_({
        'iron': ('#4b505a', 'metal', {'rivets': True}), 'iron_d': ('#2b2e35', 'metal'), 'copper': ('#c8733a', 'metal'),
        'copper_d': ('#8f4a22', 'metal'), 'wood': ('#7a5232', 'wood', {'planks': True}), 'wheel': ('#5a3b22', 'wood'),
        'hub': ('#c8733a', 'metal'), 'glow': ('#6fe3ff', 'glow'), 'glow_w': ('#e8fbff', 'glow'), 'cloth': ('#efefef', 'cloth'),
        'pole': ('#3a2a1c', 'wood'), 'gold': ('#e8b84a', 'metal'),
    })
    stripes = [('rect', 0.0, y, 1.0, y + 0.1, '#7a3c18') for y in (0.12, 0.37, 0.62, 0.87)]
    root = m.bone('root', [0, 0, 0])
    for name, x, z, side in (('wheel_fr', 10.5, -6.5, 1), ('wheel_fl', -10.5, -6.5, -1), ('wheel_br', 10.5, 7, 1), ('wheel_bl', -10.5, 7, -1)):
        w = m.bone(name, [x, 5.5, z], root)
        wheel(w, x, 5.5, z, 5.5, 2.4, 'wheel', 'hub', '#3a2414', side)
    cart = m.bone('cart', [0, 6, 0], root)
    cb(cart, 0, 5.5, 0.3, 17, 5, 22, 'iron', decals={'north': [('rect', 0.1, 0.3, 0.9, 0.42, '#2b2e35')]})
    cb(cart, 0, 10.5, 0.3, 18, 1.5, 23, 'wood')
    for z in (-6.5, 7):
        cb(cart, 0, 4.7, z, 19.6, 1.6, 1.6, 'iron_d')
    for sx in (1, -1):
        for z in (-6.5, 7):
            cb(cart, sx * 10.5, 11.6, z, 3.4, 1.0, 9, 'iron_d')
        cb(cart, sx * 7.0, 12, 6.5, 2.4, 6.5, 5.5, 'copper', decals={'east': stripes, 'west': stripes})   # capacitors
        cb(cart, sx * 7.0, 18.5, 6.5, 1.6, 1.0, 1.6, 'iron_d')
    cb(cart, 0, 6.5, -11.4, 14, 2.4, 1.2, 'iron_d')                         # front bumper
    # barrel (pivot at the rear mount)
    br = m.bone('barrel', [0, 16, 6], cart)
    cb(br, 0, 12, 6.5, 11, 9, 9, 'iron', decals={'south': [('rect', 0.2, 0.25, 0.8, 0.75, '#2b2e35'),
                                                             ('rect', 0.3, 0.35, 0.7, 0.65, '#6fe3ff')]})
    cb(br, 0, 12.75, -5, 8.5, 8.5, 18, 'iron_d')                             # tube z -14..4
    for z in (-12, -7.5, -3, 1.5):
        cb(br, 0, 11.75, z, 10.5, 10.5, 1.8, 'copper', decals={f: [('rect', 0.0, 0.45, 1.0, 0.55, '#8f4a22')] for f in ('east', 'west', 'up')})
    cb(br, 0, 11.5, -14.9, 11, 11, 1.6, 'copper_d', decals={'north': [('ering', 0.5, 0.5, 0.45, 0.45, 0.25, '#e09050')]})
    cb(br, 0, 21, 1.5, 1.2, 1.0, 9, 'copper')                               # cable
    tower = m.bone('tower', [0, 21, 6.5], br)
    cb(tower, 0, 21, 6.5, 5.4, 5.6, 5.4, 'copper', decals={f: stripes for f in ('north', 'south', 'east', 'west')})
    cb(tower, 0, 20.6, 6.5, 6.6, 1.2, 6.6, 'iron_d')
    cb(tower, 0, 26.4, 6.5, 3.2, 1.0, 3.2, 'iron_d')
    coil = m.bone('coil', [0, 17, -5], br)
    for z in (-9.75, -5.25, -0.75):
        cb(coil, 0, 12.3, z, 9.4, 9.4, 2.7, 'glow')
    orb = m.bone('orb', [0, 29.5, 6.5], tower)
    cb(orb, 0, 27.3, 6.5, 4.6, 4.6, 4.6, 'glow')
    cb(orb, 0, 27.8, 6.5, 3.6, 3.6, 3.6, 'glow_w', rot=('y', 45))
    spark = m.bone('spark', [0, 32, 6.5], orb)
    for (x, y, r) in ((0.6, 31.6, -22.5), (-0.5, 33.4, 22.5), (0.5, 35.2, -22.5)):
        cb(spark, x, y, 6.5, 0.8, 2.2, 0.8, 'glow_w', rot=('z', r))
    cb(spark, 2.6, 31.2, 6.5, 0.7, 1.6, 0.7, 'glow', rot=('z', 45))
    cb(spark, -2.4, 31.4, 6.5, 0.7, 1.6, 0.7, 'glow', rot=('z', -45))
    cb(br, 0, 13.6, -16.1, 6.8, 6.8, 0.8, 'iron_d')
    cb(br, 0, 16.3, -17.9, 1.4, 1.4, 3.0, 'copper')                         # electrode prong
    mz = m.bone('muzzle', [0, 17, -19.6], br)
    cb(mz, 0, 14.4, -16.7, 5.2, 5.2, 0.6, 'glow', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#c8f6ff')]})
    cb(mz, 0, 16.0, -19.6, 2.0, 2.0, 2.0, 'glow_w')
    for sx, side in ((1, 'r'), (-1, 'l')):                                  # team flags
        cb(cart, sx * 8.2, 11.5, 10.6, 0.8, 15, 0.8, 'pole')
        cb(cart, sx * 8.2, 26.4, 10.6, 1.2, 1.2, 1.2, 'gold')
        fl = m.bone('tc_flag_' + side, [sx * 8.2, 26, 10.6], cart)
        cb(fl, sx * 8.2, 21.5, 13.2, 0.4, 4.4, 4.6, 'cloth', decals={'east': [('rect', 0.0, 0.0, 1.0, 0.12, '#bdbdbd')],
                                                                      'west': [('rect', 0.0, 0.0, 1.0, 0.12, '#bdbdbd')]})
        cb(fl, sx * 8.2, 22.3, 16.3, 0.4, 2.8, 1.8, 'cloth')
    m.hitbox(1.6, 1.8)

    wheels = ('wheel_fr', 'wheel_fl', 'wheel_br', 'wheel_bl')
    flags = lambda L, a: {('tc_flag_' + s): {'rotation': loop([[0, a, 0], [0, -a * 0.6, 0]], L)} for s in 'rl'}
    idle = {'coil': {'scale': loop([[1, 1, 1], [1.05, 1.05, 1.0]], 0.5)},
            'orb': {'scale': loop([[1, 1, 1], [1.12, 1.12, 1.12]], 0.5)},
            'spark': {'scale': [(0, [1, 1, 1]), (0.12, [0.3, 0.6, 0.3]), (0.25, [1.1, 1.1, 1.1]), (0.5, [0.2, 0.2, 0.2]),
                                (0.62, [1, 1.2, 1]), (0.9, [0.4, 0.5, 0.4]), (1.0, [1, 1, 1])],
                      'rotation': [(0, [0, 0, 0]), (0.5, [0, 180, 0]), (1.0, [0, 360, 0])]},
            'cart': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 1.0)}}
    idle.update(flags(2.0, 18))
    m.anim('idle', 2.0, 'loop', idle)
    L = 0.8
    walk = dict(idle)
    walk.update({w: {'rotation': spin(L)} for w in wheels})
    walk['cart'] = {'position': loop([[0, 0, 0], [0, 0.6, 0]], L / 2), 'rotation': loop([[1, 0, 1], [1, 0, -1]], L)}
    walk['barrel'] = {'rotation': loop([[0, 0, 0], [-2, 0, 0]], L / 2)}
    walk.update(flags(0.4, 28))
    m.anim('walk', L, 'loop', walk)
    m.anim('charge', 1.0, 'once', {
        'coil': {'scale': [(0, [1, 1, 1]), (0.25, [1.12, 1.12, 1.05]), (0.4, [1.06, 1.06, 1]), (0.6, [1.18, 1.18, 1.08]),
                           (0.75, [1.12, 1.12, 1.04]), (0.92, [1.25, 1.25, 1.1]), (1.0, [1.2, 1.2, 1.08])]},
        'orb': {'scale': [(0, [1, 1, 1]), (0.3, [1.2, 1.2, 1.2]), (0.6, [1.35, 1.35, 1.35]), (1.0, [1.5, 1.5, 1.5])]},
        'spark': {'scale': [(0, [1, 1, 1]), (0.1, [1.6, 1.6, 1.6]), (0.2, [0.5, 0.8, 0.5]), (0.35, [1.8, 1.8, 1.8]),
                            (0.5, [0.6, 1, 0.6]), (0.65, [2, 2, 2]), (0.8, [0.8, 1.2, 0.8]), (1.0, [2.2, 2.2, 2.2])],
                  'rotation': [(0, [0, 0, 0]), (1.0, [0, 540, 0])]},
        'barrel': {'rotation': [(0, [0, 0, 0]), (0.2, [-1.5, 1.5, 0]), (0.3, [-1.5, -1.5, 0]), (0.4, [-2.5, 1.5, 0]), (0.5, [-2.5, -1.5, 0]),
                                (0.6, [-3, 2, 0]), (0.7, [-3, -2, 0]), (0.8, [-4, 2, 0]), (0.9, [-4, -2, 0]), (1.0, [-4, 0, 0])]},
        'cart': {'position': [(0, [0, 0, 0]), (1.0, [0, -0.6, 0])]}})
    m.anim('attack', 0.6, 'once', {
        'barrel': {'rotation': [(0, [-4, 0, 0]), (0.06, [-2, 0, 0]), (0.1, [-14, 0, 0]), (0.25, [-8, 0, 0]), (0.6, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.06, [0, 0, -1]), (0.1, [0, 0.5, 5]), (0.25, [0, 0, 3]), (0.6, [0, 0, 0])]},
        'coil': {'scale': [(0, [1.2, 1.2, 1.08]), (0.06, [1.35, 1.35, 1.12]), (0.1, [0.75, 0.75, 1]), (0.3, [0.85, 0.85, 1]), (0.6, [1, 1, 1])]},
        'orb': {'scale': [(0, [1.5, 1.5, 1.5]), (0.1, [0.5, 0.5, 0.5]), (0.6, [1, 1, 1])]},
        'spark': {'scale': [(0, [2, 2, 2]), (0.1, [0.1, 0.1, 0.1]), (0.45, [0.1, 0.1, 0.1]), (0.6, [1, 1, 1])]},
        'muzzle': {'scale': [(0, [1, 1, 1]), (0.06, [1.25, 1.25, 1.25]), (0.1, [1.8, 1.8, 1.8]), (0.2, [0.6, 0.6, 0.6]), (0.6, [1, 1, 1])]},
        'cart': {'rotation': [(0, [0, 0, 0]), (0.1, [-5, 0, 0]), (0.3, [1.5, 0, 0]), (0.6, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.1, [0, 0.5, 2.5]), (0.3, [0, 0, 1]), (0.6, [0, 0, 0])]},
        **{w: {'rotation': [(0, [0, 0, 0]), (0.25, [-35, 0, 0]), (0.6, [-30, 0, 0])]} for w in wheels}})
    common_tail(m, hit_bone='cart', death={
        'cart': {'rotation': [(0, [0, 0, 0]), (0.2, [-6, 0, 0]), (0.6, [10, 0, 25]), (0.9, [12, 0, 30])],
                 'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.9, [0, -4, 0])]},
        'coil': {'scale': [(0, [1, 1, 1]), (0.15, [1.5, 1.5, 1.2]), (0.4, [0.01, 0.01, 0.01])]},
        'orb': {'scale': [(0, [1, 1, 1]), (0.15, [1.8, 1.8, 1.8]), (0.4, [0.01, 0.01, 0.01])]},
        'muzzle': {'scale': [(0, [1, 1, 1]), (0.3, [0.01, 0.01, 0.01])]},
        'wheel_fr': {'position': [(0, [0, 0, 0]), (0.6, [-4, -1, -2])], 'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, -50])]},
        'root': {'scale': [(0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.9, [0.8, 0.5, 0.8])]}})
    return m


# =================================================================== Battle ram
def barbarian(m, root, p, X, Z, inner, S=0.8):
    """small barbarian (team-coloured shirt) at (X, Z); inner = +1 if the log is toward +x"""
    def B(bone, x, y, z, w, h, d, mat, **kw):
        return cb(bone, X + x * S, y * S, Z + z * S, w * S, h * S, d * S, mat, **kw)
    def O(x, y, z):
        return [X + x * S, y * S, Z + z * S]
    face = [('rect', 0.1, 0.28, 0.44, 0.36, '#6a2e10'), ('rect', 0.56, 0.28, 0.9, 0.36, '#6a2e10'),
            ('rect', 0.16, 0.4, 0.4, 0.54, '#ffffff'), ('rect', 0.6, 0.4, 0.84, 0.54, '#ffffff'),
            ('rect', 0.26, 0.42, 0.38, 0.54, '#2a55b0'), ('rect', 0.62, 0.42, 0.74, 0.54, '#2a55b0'),
            ('rect', 0.44, 0.5, 0.56, 0.68, '#c27a52')]
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('%s_leg_%s' % (p, side), O(sx * 2.4, 10.5, 0), root)
        B(lg, sx * 2.4, 3, 0, 4.6, 7.8, 5, 'pants')
        B(lg, sx * 2.4, 0, -0.6, 5.1, 3.4, 6.3, 'boot')
        B(lg, sx * 2.4, 3.1, -0.4, 5.5, 1.4, 6.1, 'fur')
    body = m.bone(p + '_body', O(0, 10.5, 0), root)
    B(body, 0, 13.0, -2.75, 4.0, 7.0, 0.4, 'skin', decals={'north': [('rect', 0.2, 0.3, 0.8, 0.4, '#c98a64')]})   # open collar
    for sx in (1, -1):
        B(body, sx * 4.2, 18.6, 0, 3.4, 2.4, 6.4, 'fur')
    tc = m.bone('tc_%s_shirt' % p, O(0, 15, 0), body)
    B(tc, 0, 10.5, 0, 9.4, 9.8, 5.6, 'cloth')
    B(tc, inner * -3, 6.8, -3.1, 2.6, 4.0, 0.7, 'cloth')
    B(body, 0, 10.4, 0, 10.0, 2.2, 6.2, 'leather')
    B(body, 0, 10.9, -3.15, 2.0, 1.8, 0.5, 'gold')
    head = m.bone(p + '_head', O(0, 20.5, 0), body)
    B(head, 0, 20.3, 0, 7.2, 7.6, 7.2, 'skin', decals={'north': face})
    B(head, 0, 27.0, 0.3, 8.0, 2.0, 8.0, 'hair')
    B(head, 0, 18.6, 3.0, 8.2, 9.0, 2.8, 'hair')
    for sx in (1, -1):
        B(head, sx * 3.85, 21.2, 0.6, 1.0, 6.2, 6.4, 'hair')
        B(head, sx * 1.6, 15.2, -4.0, 1.6, 2.6, 1.2, 'hair')               # beard braids
    B(head, 0, 16.6, -3.9, 6.2, 5.2, 1.4, 'hair')                          # beard
    B(head, 0, 21.4, -4.3, 6.0, 1.3, 0.9, 'hair')                          # moustache
    B(head, 0, 25.3, -3.7, 7.6, 1.0, 0.4, 'band')
    for sx, nm in ((inner, 'in'), (-inner, 'out')):
        a = m.bone('%s_arm_%s' % (p, nm), O(sx * 6.4, 19.3, 0), body)
        B(a, sx * 6.4, 13.6, 0, 3.8, 6.6, 3.8, 'skin')
        B(a, sx * 6.4, 10.6, 0, 4.2, 3.2, 4.2, 'leather')
        B(a, sx * 6.4, 9.6, -0.1, 3.8, 1.2, 3.8, 'skin')
    return body


def battle_ram():
    """Two barbarians (team-coloured shirts) running with a big log tipped with an iron ram head."""
    m = Model('clash_battle_ram', density=1.25)
    m.mats_({
        'skin': ('#e3a47c', 'skin'), 'hair': ('#c75a1c', 'hair'), 'pants': ('#5a3b26', 'leather', {'stitch': False}),
        'boot': ('#3b2618', 'leather'), 'fur': ('#8a6a48', 'fur'), 'leather': ('#4a2c18', 'leather'),
        'cloth': ('#efefef', 'cloth'), 'gold': ('#e8b84a', 'metal'), 'band': ('#3a2414', 'leather'),
        'log': ('#7b5230', 'wood', {'grain': 'v'}), 'bark': ('#5a3a20', 'wood', {'grain': 'v'}), 'end': ('#c9a06a', 'wood'),
        'iron': ('#565b64', 'metal', {'rivets': True}), 'iron_d': ('#33363d', 'metal'), 'iron_l': ('#8a909b', 'metal'),
        'rope': ('#b39466', 'rope'),
    })
    root = m.bone('root', [0, 0, 0])
    S = 0.85
    barbarian(m, root, 'a', 14.6, -7.0, -1, S)
    barbarian(m, root, 'b', -14.6, 7.0, 1, S)
    ram = m.bone('ram', [0, 10, -2], root)
    R2 = 8.25                                     # log half thickness (16.5 px, ~2.5x the old log)
    bark = [('rect', 0.15, 0.0, 0.2, 1.0, '#5a3a20'), ('rect', 0.45, 0.0, 0.5, 1.0, '#5a3a20'), ('rect', 0.78, 0.0, 0.83, 1.0, '#5a3a20'),
            ('rect', 0.3, 0.3, 0.38, 0.34, '#4a2e18'), ('rect', 0.6, 0.66, 0.7, 0.7, '#4a2e18')]

    def cross(bone, z, d, mat, grow=0.0, dec=None, **kw):
        """rounded-square log section along z: two crossed boxes"""
        a, b = 2 * (R2 + grow), 2 * (R2 + grow) * 0.73
        cb(bone, 0, 10 - a / 2, z, b, a, d, mat, decals=dec or {}, **kw)
        cb(bone, 0, 10 - b / 2, z, a, b, d, mat, decals=dec or {}, **kw)
    cross(ram, -2, 44, 'log', dec={'east': bark, 'west': bark, 'up': bark, 'down': bark})        # log z -24..20
    ring = [('ering', 0.5, 0.5, 0.25, 0.25, 0.25, '#8a6a40'), ('ering', 0.5, 0.5, 0.47, 0.47, 0.08, '#5a3a20')]
    cb(ram, 0, 10 - R2 + 0.6, 20.2, 2 * R2 * 0.73 - 1, 2 * R2 - 1.2, 0.5, 'end', decals={'south': ring})
    cb(ram, 0, 10 - R2 * 0.73 + 0.6, 20.2, 2 * R2 - 1.2, 2 * R2 * 0.73 - 1.2, 0.5, 'end', decals={'south': ring})
    for z in (-17, 13):
        cross(ram, z, 2.2, 'iron', grow=0.5)
    for (x, y, z) in ((4, 18.6, 5), (-5, 18.6, -10)):                          # knot stubs
        cb(ram, x, y - 0.6, z, 2.2, 1.6, 2.2, 'bark')
    for (sx, z) in ((1, -7.0), (-1, 7.0)):                                      # rope grips where the hands hold
        cross(ram, z, 1.4, 'rope', grow=0.35)
        cb(ram, sx * (R2 + 0.9), 7.4, z, 1.4, 4.0, 2.4, 'rope')
    tcb = m.bone('tc_band', [0, 10, -2], ram)
    cross(tcb, 0, 3.4, 'cloth', grow=0.4)
    cb(tcb, 0, 0.6, 1.2, 2.4, 3.6, 0.8, 'cloth')
    # big iron ram head
    cb(ram, 0, 0.2, -27.0, 19.6, 19.6, 6.4, 'iron', decals={'east': [('rect', 0.05, 0.1, 0.95, 0.18, '#33363d')], 'west': [('rect', 0.05, 0.1, 0.95, 0.18, '#33363d')]})
    cb(ram, 0, 2.2, -31.4, 15.6, 15.6, 2.6, 'iron_l', decals={'north': [('rect', 0.15, 0.28, 0.36, 0.42, '#22252a'), ('rect', 0.64, 0.28, 0.85, 0.42, '#22252a'),
                                                                    ('rect', 0.28, 0.7, 0.72, 0.8, '#22252a')]})
    cb(ram, 0, 4.6, -33.4, 10.8, 10.8, 1.6, 'iron_l')
    cb(ram, 0, 0.0, -23.3, 20.4, 20.4, 1.2, 'iron_d')
    for sx in (1, -1):                                                         # curled ram horns
        cb(ram, sx * 11.0, 15.0, -26.0, 4.0, 5.0, 6.0, 'iron_d')
        cb(ram, sx * 12.2, 9.0, -28.0, 3.6, 6.4, 3.6, 'iron_d', rot=('x', 22.5))
        cb(ram, sx * 11.4, 5.6, -31.4, 3.2, 3.2, 3.6, 'iron_d')
        cb(ram, sx * 6.0, 19.8, -27.0, 2.0, 2.4, 2.0, 'iron_l')
    m.hitbox(2.0, 1.8)

    def run(p, ph, L):
        k = [[34, 0, 0], [-34, 0, 0]]
        if ph:
            k = k[::-1]
        return {p + '_leg_r': {'rotation': loop(k, L)}, p + '_leg_l': {'rotation': loop(k[::-1], L)},
                p + '_arm_out': {'rotation': loop([[-v[0] * 1.2, 0, 0] for v in k[::-1]], L)},
                p + '_arm_in': {'rotation': loop([[-6, 0, 0], [-10, 0, 0]], L / 2)},
                p + '_body': {'rotation': [(0, [12, 0, 0]), (L, [12, 0, 0])],
                              'position': loop([[0, 0, 0], [0, 1.0, 0]], L / 2)},
                p + '_head': {'rotation': [(0, [-10, 0, 0]), (L, [-10, 0, 0])]}}
    idle = {}
    for p, ph in (('a', 0), ('b', 1)):
        idle[p + '_body'] = {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)}
        idle[p + '_head'] = {'rotation': loop([[0, 10 * (1 if ph else -1), 0], [0, 0, 0], [0, -10 * (1 if ph else -1), 0], [0, 0, 0]], 4.0)}
        idle[p + '_arm_out'] = {'rotation': loop([[0, 0, 0], [-4, 0, 0]], 2.0)}
    idle['ram'] = {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)}
    m.anim('idle', 2.0, 'loop', idle)
    L = 0.4
    walk = {}
    walk.update(run('a', 0, L))
    walk.update(run('b', 1, L))
    walk['ram'] = {'position': loop([[0, 0, 0], [0, 0.9, 0]], L / 2), 'rotation': loop([[1.2, 0, 0.8], [-1.2, 0, -0.8]], L / 2)}
    m.anim('walk', L, 'loop', walk)
    att = {'ram': {'position': [(0, [0, 0, 0]), (0.12, [0, 0.5, 3]), (0.2, [0, -0.5, -7]), (0.27, [0, -0.3, -6]), (0.4, [0, 0, 0])],
                   'rotation': [(0, [0, 0, 0]), (0.12, [-4, 0, 0]), (0.2, [3, 0, 0]), (0.4, [0, 0, 0])]}}
    for p in ('a', 'b'):
        att[p + '_body'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-8, 0, 0]), (0.2, [18, 0, 0]), (0.27, [16, 0, 0]), (0.4, [0, 0, 0])],
                            'position': [(0, [0, 0, 0]), (0.12, [0, 0, 2]), (0.2, [0, -0.5, -4]), (0.27, [0, -0.5, -3.5]), (0.4, [0, 0, 0])]}
        att[p + '_leg_r'] = {'rotation': [(0, [0, 0, 0]), (0.2, [-22, 0, 0]), (0.4, [0, 0, 0])]}
        att[p + '_leg_l'] = {'rotation': [(0, [0, 0, 0]), (0.2, [24, 0, 0]), (0.4, [0, 0, 0])]}
        att[p + '_arm_out'] = {'rotation': [(0, [0, 0, 0]), (0.12, [20, 0, 0]), (0.2, [-50, 0, 0]), (0.4, [0, 0, 0])]}
        att[p + '_head'] = {'rotation': [(0, [0, 0, 0]), (0.2, [-14, 0, 0]), (0.4, [0, 0, 0])]}
    m.anim('attack', 0.4, 'once', att)
    hit = {}
    for b in ('a_body', 'b_body', 'ram'):
        hit[b] = {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                  'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}
    m.anim('spawn', 0.5, 'once', {'root': {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', hit)
    m.anim('death', 0.9, 'hold', {
        'ram': {'position': [(0, [0, 0, 0]), (0.4, [0, -1.8, 0]), (0.9, [0, -1.8, 0])], 'rotation': [(0, [0, 0, 0]), (0.4, [-3, 0, 0]), (0.9, [-2, 6, 0])]},
        'a_body': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, -70]), (0.9, [0, 0, -85])], 'position': [(0, [0, 0, 0]), (0.9, [-2, -6, 0])]},
        'b_body': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 70]), (0.9, [0, 0, 85])], 'position': [(0, [0, 0, 0]), (0.9, [2, -6, 0])]},
        'root': {'scale': [(0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.9, [0.9, 0.7, 0.9])]}})
    return m


# =================================================================== Cannon cart
CART_MATS = {
    'wood': ('#8a5a32', 'wood', {'grain': 'v'}), 'plank': ('#8a5a32', 'wood', {'planks': True}), 'wood_d': ('#5e3b1f', 'wood'),
    'wheel': ('#6b4426', 'wood'), 'iron': ('#4a4e56', 'metal', {'rivets': True}), 'iron_d': ('#2c2f35', 'metal'),
    'brass': ('#c9973a', 'metal'), 'tcm': ('#e6e6e6', 'metal'), 'cloth': ('#efefef', 'cloth'), 'ball': ('#26272b', 'metal'),
    'bore': ('#0c0c0e', 'plain'), 'rope': ('#a58a5a', 'rope'),
}
BORE = [('rect', 0.2, 0.2, 0.8, 0.8, '#0c0c0e'), ('rect', 0.12, 0.12, 0.88, 0.2, '#6a6e78'), ('rect', 0.12, 0.8, 0.88, 0.88, '#24262b')]


def cannon_barrel(m, parent, p, ay, az, tcname):
    """the cart cannon barrel, axis at height ay, trunnion at z = az. returns (barrel bone, muzzle bone)"""
    bar = m.bone(p + 'barrel', [0, ay, az], parent)
    cb(bar, 0, ay - 3.5, az + 3.5, 7.5, 7, 6, 'iron')                     # breech
    cb(bar, 0, ay - 1.25, az + 7.4, 2.5, 2.5, 2.2, 'iron_d')              # cascabel
    cb(bar, 0, ay - 0.6, az + 8.8, 1.2, 1.2, 1.2, 'iron_d')
    cb(bar, 0, ay - 2.75, az - 6, 5.5, 5.5, 13, 'iron')                    # tube
    cb(bar, 0, ay - 3.25, az - 13.5, 6.5, 6.5, 2.4, 'iron_d', decals={'north': BORE})
    cb(bar, 0, ay + 2.6, az + 0.5, 1.2, 1.0, 1.6, 'brass')                 # vent
    for sx in (1, -1):
        cb(bar, sx * 3.6, ay - 0.9, az, 1.8, 1.8, 1.8, 'iron_d')           # trunnions
    tc = m.bone(tcname, [0, ay, az], bar)
    for z in (az - 2.5, az - 10):
        cb(tc, 0, ay - 3.1, z, 6.2, 6.2, 1.6, 'tcm')
    mz = m.bone(p + 'muzzle', [0, ay, az - 14.8], bar)
    return bar, mz


def cannon_cart():
    """Small cannon on a two-wheeled wooden cart with a front shield plate (bone 'shield') and a team pennant."""
    m = Model('clash_cannon_cart', density=1.25)
    m.mats_(CART_MATS)
    root = m.bone('root', [0, 0, 0])
    for side, sx in (('r', 1), ('l', -1)):
        w = m.bone('wheel_' + side, [sx * 10.4, 6, 1], root)
        wheel(w, sx * 10.4, 6, 1, 6, 2.4, 'wheel', 'iron', '#3d2614', sx)
    cart = m.bone('cart', [0, 6, 1], root)
    cb(cart, 0, 6.5, 2, 15, 3.5, 18, 'plank', decals={'up': [('rect', 0.0, y, 1.0, y + 0.04, '#4a2e18') for y in (0.25, 0.5, 0.75)]})
    for sx in (1, -1):
        cb(cart, sx * 7.8, 8.5, 2, 1.6, 3, 18, 'wood_d')
        cb(cart, sx * 3.6, 10, 1.5, 1.8, 4.6, 7, 'wood_d')                  # cheeks
    cb(cart, 0, 5.2, 1, 19, 1.6, 1.6, 'iron_d')                             # axle
    cb(cart, 0, 1.0, 15.6, 4, 2.4, 12, 'wood_d', rot=('x', 22.5))            # trail to the ground
    cb(cart, 0, 0, 20.8, 4.8, 1.4, 2.6, 'iron')
    for (x, z) in ((3.3, 8.6), (5.6, 8.6), (4.4, 6.4)):                     # cannon balls
        cb(cart, x, 10, z, 2.3, 2.3, 2.3, 'ball')
    cb(cart, -4.6, 10, 8.4, 3.4, 4, 3.4, 'wood_d', decals={f: [('rect', 0.0, 0.3, 1.0, 0.4, '#2c2f35'), ('rect', 0.0, 0.7, 1.0, 0.8, '#2c2f35')]
                                                         for f in ('north', 'south', 'east', 'west')})   # powder keg
    bar, mz = cannon_barrel(m, cart, '', 14.6, 1.5, 'tc_band')
    # front shield plate (low, the barrel rides over it)
    sh = m.bone('shield', [0, 6, -8.8], cart)
    vert = [('rect', x, 0, x + 0.04, 1, '#5a3a1e') for x in (0.2, 0.4, 0.6, 0.8)]
    cb(sh, 0, 3.2, -8.8, 20.4, 8.6, 2, 'wood', decals={'north': vert + [('rect', 0.12, 0.6, 0.18, 0.66, '#3a2412'), ('rect', 0.8, 0.3, 0.86, 0.36, '#3a2412')]})
    cb(sh, 0, 11.4, -8.8, 7.0, 0.8, 2.2, 'iron')                            # barrel rest
    for sx in (1, -1):
        cb(sh, sx * 7.0, 11.8, -8.8, 6.4, 2.2, 2, 'wood')                    # raised wings
        cb(sh, sx * 9.9, 3.0, -9.9, 1.2, 11.4, 0.6, 'iron')
        cb(sh, sx * 4.0, 3.0, -9.95, 1.0, 9.0, 0.5, 'iron')
        cb(sh, sx * 7.0, 12.6, -10.1, 1.2, 1.2, 0.4, 'brass')
        cb(sh, sx * 7.0, 5.0, -10.1, 1.2, 1.2, 0.4, 'brass')
        cb(sh, sx * 9.6, 14.0, -8.8, 1.6, 2.0, 1.6, 'iron', rot=('z', -sx * 22.5))   # spiked corners
    cb(sh, 0, 6.6, -9.95, 20.6, 0.8, 0.5, 'iron')
    # team pennant
    cb(cart, -6.2, 10, 10, 0.9, 16, 0.9, 'wood_d')
    cb(cart, -6.2, 26, 10, 1.3, 1.3, 1.3, 'brass')
    pn = m.bone('tc_pennant', [-6.2, 25.5, 10], cart)
    cb(pn, -6.2, 22.3, 12.6, 0.4, 3.4, 4.6, 'cloth')
    cb(pn, -6.2, 23.1, 16.1, 0.4, 1.8, 2.6, 'cloth')
    m.scale_bone('root', 1.35, [0, 0, 0])                                   # 1.35x bigger
    m.hitbox(2.0, 2.1)

    pen = lambda L, a: {'tc_pennant': {'rotation': loop([[0, a, 0], [0, -a * 0.5, 0]], L)}}
    idle = {'barrel': {'rotation': loop([[0, 0, 0], [-1.5, 0, 0]], 2.0)}}
    idle.update(pen(2.0, 16))
    m.anim('idle', 2.0, 'loop', idle)
    L = 0.6
    walk = {'wheel_r': {'rotation': spin(L)}, 'wheel_l': {'rotation': spin(L)},
            'cart': {'position': loop([[0, 0, 0], [0, 0.5, 0]], L / 2), 'rotation': loop([[1, 0, 1], [1, 0, -1]], L)},
            'barrel': {'rotation': loop([[0, 0, 0], [-2, 0, 0]], L / 2)}}
    walk.update(pen(0.3, 26))
    m.anim('walk', L, 'loop', walk)
    m.anim('attack', 0.5, 'once', {
        'barrel': {'rotation': [(0, [0, 0, 0]), (0.08, [-2, 0, 0]), (0.12, [-12, 0, 0]), (0.28, [-6, 0, 0]), (0.5, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.08, [0, 0, -0.8]), (0.12, [0, 0.4, 3.5]), (0.28, [0, 0, 1.5]), (0.5, [0, 0, 0])]},
        'muzzle': {'scale': [(0, [1, 1, 1]), (0.12, [1.4, 1.4, 1]), (0.25, [1, 1, 1])]},
        'cart': {'rotation': [(0, [0, 0, 0]), (0.12, [-4, 0, 0]), (0.3, [1, 0, 0]), (0.5, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.12, [0, 0.3, 1.8]), (0.3, [0, 0, 0.8]), (0.5, [0, 0, 0])]},
        'wheel_r': {'rotation': [(0, [0, 0, 0]), (0.3, [-20, 0, 0]), (0.5, [-18, 0, 0])]},
        'wheel_l': {'rotation': [(0, [0, 0, 0]), (0.3, [-20, 0, 0]), (0.5, [-18, 0, 0])]}})
    common_tail(m, hit_bone='cart', death={
        'wheel_r': {'position': [(0, [0, 0, 0]), (0.5, [-3, -1, 0])], 'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, -60]), (0.9, [0, 0, -80])]},
        'wheel_l': {'position': [(0, [0, 0, 0]), (0.5, [3, -1, 0])], 'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, 60]), (0.9, [0, 0, 80])]},
        'cart': {'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.6, [0, -5, 0]), (0.9, [0, -5.5, 0])],
                 'rotation': [(0, [0, 0, 0]), (0.6, [-6, 10, 0])]},
        'shield': {'rotation': [(0, [0, 0, 0]), (0.5, [70, 0, 0]), (0.9, [85, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.6, [0, -4, -3])]}})
    return m


# =================================================================== Cannon cart (broken) = building with turret
def cannon_cart_broken():
    """What the cannon cart leaves behind: the cannon on its wrecked cart bed, wheel debris and smoke.
    root -> base (base_*, static) + top (top_*, turns to aim)."""
    m = Model('clash_cannon_cart_broken', density=1.25)
    m.mats_(dict(CART_MATS, smoke=('#55565c', 'plain'), smoke_l=('#86878e', 'plain'), ember=('#ff7a1e', 'glow'), char=('#2a1d14', 'wood')))
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    bed = m.bone('base_bed', [0, 0, 0], base)
    cb(bed, 0, 0, 1, 16, 3.6, 17, 'plank', decals={'up': [('rect', 0.0, y, 1.0, y + 0.04, '#4a2e18') for y in (0.25, 0.5, 0.75)] +
                                                   [('rect', 0.7, 0.05, 0.95, 0.35, '#2a1d14'), ('rect', 0.05, 0.7, 0.25, 0.95, '#2a1d14')],
                                                   'north': [('rect', 0.6, 0.0, 0.8, 1.0, '#2a1d14')]})
    for sx in (1, -1):
        cb(bed, sx * 8.6, 0, 1, 1.6, 3.2, 17, 'wood_d')
    cb(bed, 8.6, 3.0, -4.5, 1.4, 2.2, 6, 'char', rot=('x', -22.5))          # snapped rail end
    cb(bed, 0, 0, 13.0, 4, 2.0, 8, 'wood_d', rot=('y', 22.5))                # broken trail
    cb(bed, 0, 3.6, 0, 10, 1.6, 10, 'iron')                                  # turntable
    cb(bed, 0, 3.2, 0, 11.4, 0.6, 11.4, 'iron_d')
    deb = m.bone('base_debris', [0, 0, 0], base)
    # wheel lying flat on the ground (left back) + half wheel leaning on the right
    cb(deb, -11.5, 0, 9, 10, 1.6, 5, 'wheel', decals={'up': [('rect', 0.44, 0, 0.56, 1, '#3d2614')]})
    cb(deb, -11.5, 0, 9, 5, 1.6, 10, 'wheel', decals={'up': [('rect', 0, 0.44, 1, 0.56, '#3d2614')]})
    cb(deb, -11.5, 0, 9, 7.1, 1.5, 7.1, 'wheel', rot=('y', 45))
    cb(deb, -11.5, 1.6, 9, 2.6, 0.8, 2.6, 'iron')
    cb(deb, 10.5, 0, -1.5, 2.2, 10, 5, 'wheel', rot=('z', 22.5), decals={'east': [('rect', 0.44, 0, 0.56, 1, '#3d2614')]})
    cb(deb, 10.5, 1.2, -1.5, 2.2, 5, 9.0, 'wheel', rot=('z', 22.5))
    for (x, z, r, l) in ((-9, -8, 22.5, 6), (6.5, 11.5, -45, 7), (12.5, 8, 0, 5)):   # spokes / plank shards
        cb(deb, x, 0, z, 1.2, 1.0, l, 'wood_d', rot=('y', r))
    cb(deb, -6.5, 0, -9.5, 6.5, 1.0, 3.2, 'wood', rot=('y', -22.5))          # shield plank shards
    cb(deb, -9.5, 0.8, -6.5, 4.2, 6.0, 1.4, 'wood', rot=('x', 45))
    cb(deb, 4.5, 0, -10.5, 2.0, 2.0, 2.0, 'ball')
    cb(deb, 7.0, 0, 7.0, 2.0, 2.0, 2.0, 'ball')
    cb(deb, 8.0, 0, -8.5, 1.4, 1.2, 1.4, 'ember')
    pn = m.bone('base_tc_pennant', [-6.5, 3.5, 7], base)
    cb(bed, -6.5, 3.5, 7, 0.9, 10, 0.9, 'wood_d', rot=('z', 22.5))          # broken leaning pole
    cb(pn, -8.2, 10.5, 9.4, 0.4, 3.2, 4.2, 'cloth', rot=('z', 22.5), decals={'east': [('rect', 0.7, 0.6, 1.0, 1.0, '#bdbdbd')]})
    cb(pn, -8.6, 11.5, 12.6, 0.4, 1.6, 2.2, 'cloth', rot=('z', 22.5))
    smoke = m.bone('base_smoke', [5, 3.5, 6], base)
    cb(smoke, 5, 3.6, 6, 3, 3, 3, 'smoke')
    cb(smoke, 5.8, 6.4, 6.6, 2.4, 2.4, 2.4, 'smoke_l')
    cb(smoke, 5.0, 8.6, 6.0, 1.6, 1.6, 1.6, 'smoke_l')
    cb(smoke, 4.0, 2.8, 5.2, 1.2, 1.0, 1.2, 'ember')
    # turret
    top = m.bone('top', [0, 5.2, 0], root)
    cb(top, 0, 5.2, 0.5, 9, 1.4, 9, 'iron_d')
    for sx in (1, -1):
        cb(top, sx * 3.6, 6.4, 1.0, 1.8, 4.4, 7, 'wood_d')
        cb(top, sx * 3.6, 10.4, 1.0, 2.2, 0.8, 2.6, 'iron')
    bar, mz = cannon_barrel(m, top, 'top_', 11.0, 1.0, 'top_tc_band')
    m.scale_bone('root', 1.35, [0, 0, 0])                                   # 1.35x bigger (turret pivot stays at x=0, z=0)
    m.hitbox(2.1, 1.8)

    m.anim('idle', 2.4, 'loop', {
        'base_smoke': {'position': loop([[0, 0, 0], [0, 1.4, 0]], 1.2), 'scale': loop([[1, 1, 1], [1.15, 1.25, 1.15]], 1.2),
                       'rotation': [(0, [0, 0, 0]), (1.2, [0, 90, 0]), (2.4, [0, 180, 0])]},
        'base_tc_pennant': {'rotation': loop([[0, 12, 0], [0, -6, 0]], 2.4)},
        'top_barrel': {'rotation': loop([[0, 0, 0], [-1.5, 0, 0]], 2.4)}})
    m.anim('attack', 0.5, 'once', {
        'top_barrel': {'rotation': [(0, [0, 0, 0]), (0.08, [-2, 0, 0]), (0.12, [-12, 0, 0]), (0.28, [-6, 0, 0]), (0.5, [0, 0, 0])],
                       'position': [(0, [0, 0, 0]), (0.08, [0, 0, -0.8]), (0.12, [0, 0.4, 3.5]), (0.28, [0, 0, 1.5]), (0.5, [0, 0, 0])]},
        'top_muzzle': {'scale': [(0, [1, 1, 1]), (0.12, [1.4, 1.4, 1]), (0.25, [1, 1, 1])]},
        'top': {'position': [(0, [0, 0, 0]), (0.12, [0, -0.4, 0.6]), (0.3, [0, 0, 0])]},
        'base_smoke': {'scale': [(0, [1, 1, 1]), (0.12, [1.5, 1.5, 1.5]), (0.5, [1, 1, 1])]}})
    m.anim('spawn', 0.6, 'once', {
        'root': {'position': [(0, [0, 14, 0]), (0.28, [0, 0, 0]), (0.4, [0, 1.6, 0]), (0.5, [0, 0, 0]), (0.6, [0, 0, 0])],
                 'scale': [(0, [0.9, 1.1, 0.9]), (0.28, [1.0, 1.0, 1.0]), (0.32, [1.15, 0.8, 1.15]), (0.45, [0.96, 1.05, 0.96]), (0.6, [1, 1, 1])]},
        'base_smoke': {'scale': [(0, [0.01, 0.01, 0.01]), (0.3, [0.01, 0.01, 0.01]), (0.38, [2, 1.6, 2]), (0.6, [1, 1, 1])]},
        'top_barrel': {'rotation': [(0, [0, 0, 0]), (0.32, [8, 0, 0]), (0.45, [-4, 0, 0]), (0.6, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {
        'root': {'scale': [(0, [1, 1, 1]), (0.08, [1.06, 0.92, 1.06]), (0.18, [0.98, 1.03, 0.98]), (0.3, [1, 1, 1])]},
        'top_barrel': {'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', {
        'top_barrel': {'rotation': [(0, [0, 0, 0]), (0.2, [-10, 0, 0]), (0.6, [18, 0, 12]), (0.9, [20, 0, 14])],
                       'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.6, [0, -3, 0]), (0.9, [0, -3.5, 0])]},
        'top': {'position': [(0, [0, 0, 0]), (0.6, [0, -1.2, 0])]},
        'base_smoke': {'scale': [(0, [1, 1, 1]), (0.3, [1.6, 1.6, 1.6]), (0.9, [1.9, 2.1, 1.9])],
                       'position': [(0, [0, 0, 0]), (0.9, [0, 4, 0])]},
        'root': {'scale': [(0, [1, 1, 1]), (0.5, [1, 1, 1]), (0.9, [1.05, 0.6, 1.05])]}})
    return m


# =================================================================== Zappies
def zappies():
    """Zappies: a small squat electrical machine (no rider). Grey steel casing rolling on two side wheels (+ rear caster),
    orange riveted brackets, team-coloured side panels, a white tesla coil drum on top (bone 'coil') with a
    crackling cyan spark (bone 'spark'), and a short front emitter nozzle (tip = bone 'muzzle')."""
    m = Model('clash_zappies', density=1.5)
    m.mats_({
        'steel': ('#8a929c', 'metal', {'rivets': True}), 'steel_d': ('#555c66', 'metal'), 'steel_l': ('#bcc4cd', 'metal'),
        'orange': ('#e8822a', 'metal', {'rivets': True}), 'coil_w': ('#f4fcff', 'metal'), 'glow': ('#6fe3ff', 'glow'),
        'glow_w': ('#effcff', 'glow'), 'tcm': ('#e8e8e8', 'metal'), 'joint': ('#33383f', 'metal'),
    })
    rivets = [('px', 0.5, 0.12, '#5a5a5a'), ('px', 0.5, 0.88, '#5a5a5a')]
    edge = [('rect', 0.0, 0.0, 1.0, 0.07, '#5a616b'), ('rect', 0.0, 0.93, 1.0, 1.0, '#5a616b'),
            ('rect', 0.0, 0.0, 0.05, 1.0, '#5a616b'), ('rect', 0.95, 0.0, 1.0, 1.0, '#5a616b')]
    winding = [('rect', 0.0, y, 1.0, y + 0.09, '#5cc6dc') for y in (0.18, 0.38, 0.58, 0.78)]
    root = m.bone('root', [0, 0, 0])
    for side, sx in (('r', 1), ('l', -1)):                                    # two big side wheels
        w = m.bone('wheel_' + side, [sx * 6.3, 4.0, 0.2], root)
        wheel(w, sx * 6.3, 4.0, 0.2, 4.0, 1.6, 'steel_d', 'orange', '#2b2f35', sx)
    cs = m.bone('wheel_b', [0, 1.1, 3.8], root)                              # small rear caster
    cb(cs, 0, 0, 3.8, 1.2, 2.2, 2.2, 'joint')
    cb(root, 0, 2.2, 3.8, 1.8, 1.4, 1.2, 'steel_d')
    body = m.bone('body', [0, 4.2, 0], root)
    cb(body, 0, 4.0, 0, 10, 7, 9, 'steel', decals={'north': edge + [('ering', 0.72, 0.3, 0.16, 0.18, 0.35, '#33383f'), ('px', 0.72, 0.25, '#e8822a')],
                                                     'south': edge, 'up': edge})
    cb(body, 0, 3.4, 0, 9.0, 1.0, 8.0, 'steel_d')                            # underside skirt
    cb(body, 0, 10.6, 0, 10.6, 1.0, 9.6, 'steel_d')                          # top rim
    for sx in (1, -1):
        for z in (-3.3, 3.3):                                                  # orange riveted brackets
            cb(body, sx * 5.15, 5.0, z, 0.8, 5.0, 1.2, 'orange', decals={'east': rivets, 'west': rivets})
        cb(body, sx * 3.7, 5.0, -4.85, 1.2, 5.0, 0.8, 'orange', decals={'north': rivets})
        cb(body, sx * 4.6, 10.4, -4.2, 1.6, 1.6, 1.6, 'orange')              # top hinges
        cb(body, sx * 4.6, 10.4, 4.2, 1.6, 1.6, 1.6, 'orange')
    tc = m.bone('tc_panel', [0, 7.5, 0], body)
    for sx in (1, -1):
        cb(tc, sx * 5.1, 6.6, 0, 0.6, 3.8, 4.6, 'tcm', decals={'east': [('rect', 0.1, 0.45, 0.9, 0.55, '#bdbdbd')],
                                                               'west': [('rect', 0.1, 0.45, 0.9, 0.55, '#bdbdbd')]})
    cb(tc, 0, 5.2, 4.75, 6.0, 4.6, 0.6, 'tcm')
    # front emitter nozzle
    cb(body, 0, 4.9, -5.4, 3.6, 3.6, 1.8, 'steel_d')
    cb(body, 0, 4.7, -6.6, 4.0, 4.0, 0.8, 'orange')
    cb(body, 0, 5.6, -7.4, 2.2, 2.2, 1.2, 'steel_l')
    cb(body, 0, 6.2, -8.5, 1.0, 1.0, 1.4, 'steel_l')
    mz = m.bone('muzzle', [0, 6.7, -9.6], body)
    cb(mz, 0, 5.9, -9.6, 1.6, 1.6, 1.6, 'glow')
    # tesla coil drum on top
    coil = m.bone('coil', [0, 11.6, 0], body)
    cb(coil, 0, 11.6, 0, 6.0, 0.8, 6.0, 'steel_d')
    cb(coil, 0, 12.4, 0, 7.4, 3.8, 7.4, 'coil_w', decals={f: winding for f in ('north', 'south', 'east', 'west')})
    cb(coil, 0, 12.4, 0, 6.4, 3.8, 6.4, 'coil_w', rot=('y', 45), decals={f: winding for f in ('north', 'south', 'east', 'west')})
    cb(coil, 0, 16.2, 0, 5.0, 0.7, 5.0, 'steel_l')
    cb(coil, 0, 16.9, 0, 1.8, 1.4, 1.8, 'glow')
    spark = m.bone('spark', [0, 18.3, 0], coil)
    for (x, y, r) in ((0.5, 18.0, -22.5), (-0.5, 19.9, 22.5), (0.5, 21.8, -22.5)):
        cb(spark, x, y, 0, 0.9, 2.3, 0.9, 'glow_w', rot=('z', r))
    cb(spark, 0.1, 23.8, 0, 1.2, 1.2, 1.2, 'glow')
    cb(spark, 2.2, 18.6, 0, 0.7, 1.8, 0.7, 'glow', rot=('z', -45))
    cb(spark, -2.1, 19.2, 0.4, 0.7, 1.6, 0.7, 'glow', rot=('z', 45))
    m.hitbox(0.8, 1.1)

    flick = [(0, [1, 1, 1]), (0.08, [0.4, 0.7, 0.4]), (0.16, [1.15, 1.1, 1.15]), (0.3, [0.5, 0.6, 0.5]),
             (0.4, [1, 1.2, 1]), (0.52, [0.3, 0.5, 0.3]), (0.6, [1, 1, 1])]
    m.anim('idle', 1.2, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 0.6)},
        'coil': {'scale': loop([[1, 1, 1], [1.04, 1.06, 1.04]], 0.3), 'rotation': spin(1.2, axis=1)},
        'spark': {'scale': flick + [(t + 0.6, v) for t, v in flick[1:]], 'rotation': [(0, [0, 0, 0]), (0.6, [0, 180, 0]), (1.2, [0, 360, 0])]},
        'muzzle': {'scale': loop([[1, 1, 1], [0.75, 0.75, 0.75]], 0.3)}})
    L = 0.5
    m.anim('walk', L, 'loop', {
        'wheel_r': {'rotation': spin(L)}, 'wheel_l': {'rotation': spin(L)}, 'wheel_b': {'rotation': spin(L / 2)},
        'body': {'position': loop([[0, 0, 0], [0, 0.5, 0]], L / 2), 'rotation': loop([[3, 0, 1.5], [3, 0, -1.5]], L)},
        'coil': {'rotation': spin(L * 2, axis=1)},
        'spark': {'scale': loop([[1, 1, 1], [0.5, 0.8, 0.5]], L / 2)}})
    m.anim('attack', 0.6, 'once', {
        'coil': {'rotation': [(0, [0, 0, 0]), (0.1, [0, 150, 0]), (0.2, [0, 380, 0]), (0.3, [0, 720, 0]), (0.45, [0, 900, 0]), (0.6, [0, 1080, 0])],
                 'scale': [(0, [1, 1, 1]), (0.15, [1.1, 1.08, 1.1]), (0.27, [1.2, 1.15, 1.2]), (0.31, [0.9, 0.9, 0.9]), (0.45, [1.04, 1.04, 1.04]), (0.6, [1, 1, 1])]},
        'spark': {'scale': [(0, [1, 1, 1]), (0.12, [1.4, 1.4, 1.4]), (0.2, [1.1, 1.3, 1.1]), (0.28, [1.8, 1.8, 1.8]), (0.31, [0.15, 0.15, 0.15]),
                            (0.45, [0.3, 0.3, 0.3]), (0.6, [1, 1, 1])]},
        'muzzle': {'scale': [(0, [1, 1, 1]), (0.2, [1.3, 1.3, 1.3]), (0.28, [1.4, 1.4, 1.4]), (0.31, [1.7, 1.7, 1.7]), (0.38, [0.5, 0.5, 0.5]), (0.6, [1, 1, 1])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.2, [3, 0, 0]), (0.28, [4, 0, 0]), (0.31, [-9, 0, 0]), (0.45, [-2, 0, 0]), (0.6, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.2, [0, -0.5, 0]), (0.28, [0, -0.6, -0.4]), (0.31, [0, 0.6, 1.6]), (0.45, [0, 0, 0.5]), (0.6, [0, 0, 0])]},
        'wheel_r': {'rotation': [(0, [0, 0, 0]), (0.31, [0, 0, 0]), (0.45, [-40, 0, 0]), (0.6, [-40, 0, 0])]},
        'wheel_l': {'rotation': [(0, [0, 0, 0]), (0.31, [0, 0, 0]), (0.45, [-40, 0, 0]), (0.6, [-40, 0, 0])]}})
    common_tail(m, death={
        'root': {'rotation': [(0, [0, 0, 0]), (0.15, [0, 0, -8]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                 'position': [(0, [0, 0, 0]), (0.6, [0, -1, 0]), (0.9, [0, -2, 0])]},
        'spark': {'scale': [(0, [1, 1, 1]), (0.12, [2, 2, 2]), (0.3, [0.01, 0.01, 0.01])]},
        'muzzle': {'scale': [(0, [1, 1, 1]), (0.3, [0.01, 0.01, 0.01])]},
        'coil': {'rotation': [(0, [0, 0, 0]), (0.5, [0, 200, 0]), (0.9, [0, 240, 0])]},
        'wheel_r': {'rotation': [(0, [0, 0, 0]), (0.6, [120, 0, 0])]}})
    return m

# =================================================================== HQ helpers (rounded volumes, painted eyes)
def blob(bone, x, y, z, w, h, d, mat, r=None, decals=None, full=True, rot=None, rot_origin=None):
    """rounded box from 3 crossed boxes (+ an inner corner filler): x/z centre, y bottom. decals: north/south on the
    z-full box, east/west on the x-full box, up/down on the y-full box."""
    r = r if r is not None else max(0.35, min(w, h, d) * 0.17)
    dec = decals or {}
    pick = lambda fs: {f: v for f, v in dec.items() if f in fs}
    kw = {}
    if rot:
        kw = dict(rot=rot, rot_origin=rot_origin or [x, y + h / 2, z])
    cb(bone, x, y + r, z, w, h - 2 * r, d - 2 * r, mat, decals=pick(('east', 'west')), noround=True, **kw)
    cb(bone, x, y, z, w - 2 * r, h, d - 2 * r, mat, decals=pick(('up', 'down')), noround=True, **kw)
    cb(bone, x, y + r, z, w - 2 * r, h - 2 * r, d, mat, decals=pick(('north', 'south')), noround=True, **kw)
    if full:
        q = r * 0.45
        cb(bone, x, y + q, z, w - 2 * q, h - 2 * q, d - 2 * q, mat, noround=True, **kw)


def eye(x0, y0, x1, y1, iris, look=0.0, lid='#3a2418', pupil='#0c0c10'):
    """painted eye decal (fractions of the face): sclera, iris, pupil, 1px highlight, upper lid line"""
    w, h = x1 - x0, y1 - y0
    ix0 = x0 + w * (0.18 + 0.14 * look)
    ix1 = ix0 + w * 0.62
    return [('rect', x0, y0, x1, y1, '#ffffff'), ('rect', ix0, y0 + h * 0.18, ix1, y1, iris),
            ('rect', ix0 + w * 0.17, y0 + h * 0.38, ix1 - w * 0.17, y1 - h * 0.08, pupil),
            ('rect', ix0 + w * 0.05, y0 + h * 0.24, ix0 + w * 0.2, y0 + h * 0.4, '#ffffff'),
            ('rect', x0 - w * 0.04, y0 - h * 0.06, x1 + w * 0.04, y0 + h * 0.1, lid)]


def spike(bone, x, y, z, s, mat, axis='y', sign=1, tip=None):
    """tapered spike: base cube + smaller tip cube along axis"""
    tip = tip or mat
    if axis == 'y':
        cb(bone, x, y, z, s, s * 1.1, s, mat)
        cb(bone, x, y + s * 1.1, z, s * 0.55, s * 0.9, s * 0.55, tip)
    elif axis == 'x':
        cb(bone, x + sign * s * 0.55, y - s / 2, z, s * 1.1, s, s, mat)
        cb(bone, x + sign * (s * 1.1 + s * 0.45), y - s * 0.275, z, s * 0.9, s * 0.55, s * 0.55, tip)
    else:
        cb(bone, x, y - s / 2, z + sign * s * 0.55, s, s, s * 1.1, mat)
        cb(bone, x, y - s * 0.275, z + sign * (s * 1.1 + s * 0.45), s * 0.55, s * 0.55, s * 0.9, tip)


def fist(bone, x, y, z, s, mat, side=1, knuckle=None):
    """chunky fist: palm block + finger row + thumb (y = bottom)"""
    blob(bone, x, y, z, s, s * 0.9, s, mat, full=False)
    for i in range(4):
        cb(bone, x - s * 0.36 + i * s * 0.24, y + s * 0.05, z - s * 0.48, s * 0.22, s * 0.42, s * 0.3, knuckle or mat, noround=True)
    cb(bone, x - side * s * 0.52, y + s * 0.35, z - s * 0.15, s * 0.24, s * 0.42, s * 0.4, mat, noround=True)


# =================================================================== helpers for the CR-style humanoids
def biped_walk(L, leg=24, arm=22, bob=0.8, lean=4, arms=('arm_r', 'arm_l')):
    tr = {'leg_r': {'rotation': loop([[-leg, 0, 0], [leg, 0, 0]], L)},
          'leg_l': {'rotation': loop([[leg, 0, 0], [-leg, 0, 0]], L)},
          'body': {'position': loop([[0, 0, 0], [0, bob, 0]], L / 2), 'rotation': loop([[lean, 0, 2], [lean, 0, -2]], L)}}
    if arms[0]:
        tr[arms[0]] = {'rotation': loop([[arm, 0, 0], [-arm, 0, 0]], L)}
    if arms[1]:
        tr[arms[1]] = {'rotation': loop([[-arm, 0, 0], [arm, 0, 0]], L)}
    return tr


# =================================================================== Mega Knight
def mega_knight():
    """CR-style Mega Knight: huge black-iron knight, spiked bucket helm with a narrow slit, massive spiked pauldrons,
    giant spiked gauntlets, no weapon. attack = double-fist smash, jump = crouch, launch, slam."""
    m = Model('clash_mega_knight', density=2.0)
    m.mats_({
        'iron': ('#3d414a', 'metal', {'rivets': True}), 'iron_d': ('#272a31', 'metal'), 'iron_l': ('#5c616c', 'metal', {'rivets': True}),
        'silver': ('#b9c1cc', 'metal', {'rivets': True}), 'silver_d': ('#8e96a2', 'metal'), 'spike': ('#dfe5ec', 'metal'),
        'skin': ('#f2c4a2', 'skin'), 'mous': ('#1a1a1a', 'hair'), 'gold': ('#d9a63a', 'metal'), 'tcm': ('#e6e6e6', 'metal'), 'cloth': ('#efefef', 'cloth'),
        'rivet': ('#cfd5dd', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 6, 13, 0], root)
        blob(lg, sx * 6, 7.8, 0, 8, 6.2, 8, 'iron_d', full=False)
        blob(lg, sx * 6, 2.4, 0, 9, 6.0, 9.4, 'iron', decals={'north': [('rect', 0.44, 0.1, 0.56, 0.9, '#272a31')]})
        blob(lg, sx * 6, 6.2, -4.6, 6.2, 4.2, 2.2, 'silver', full=False)    # knee cop
        blob(lg, sx * 6, 0, -1.4, 10.4, 3.4, 12.6, 'iron_d')
        cb(lg, sx * 6, 0, -7.6, 8.4, 2.4, 1.0, 'silver')                    # toe cap
    body = m.bone('body', [0, 13, 0], root)
    blob(body, 0, 10.6, 0, 20, 5.4, 13, 'iron_d', full=False)
    blob(body, 0, 15, 0.5, 24, 14, 16, 'iron', decals={'east': [('rect', 0.1, 0.5, 0.9, 0.56, '#272a31')], 'west': [('rect', 0.1, 0.5, 0.9, 0.56, '#272a31')]})
    blob(body, 0, 17, -7.6, 18, 10, 2.2, 'iron_l', full=False, decals={'north': [('rect', 0.1, 0.45, 0.9, 0.52, '#3d414a')]})
    cb(body, 0, 17.4, -8.8, 1.6, 9.0, 0.8, 'silver')
    for x in (-7.4, 7.4):
        for y in (18.4, 21.6, 24.8):
            cb(body, x, y, -8.9, 0.9, 0.9, 0.6, 'rivet')
    blob(body, 0, 17, 8.4, 16, 10, 2.0, 'iron_d', full=False)
    cb(body, 0, 27.6, -0.5, 14, 2.6, 12, 'iron_d')                           # gorget
    tc = m.bone('tc_belt', [0, 13, 0], body)
    blob(tc, 0, 13.4, 0.5, 24.8, 2.8, 16.8, 'tcm', full=False)
    trim = [('rect', 0.0, 0.85, 1.0, 1.0, '#bdbdbd'), ('rect', 0.0, 0.0, 0.06, 1.0, '#bdbdbd'), ('rect', 0.94, 0.0, 1.0, 1.0, '#bdbdbd')]
    cb(tc, 0, 5.0, -7.0, 9, 8.6, 0.8, 'cloth', decals={'north': trim})
    cb(tc, 0, 5.0, 7.4, 10, 8.6, 0.8, 'cloth', decals={'south': trim})
    cb(body, 0, 13.2, -8.8, 3.6, 3.2, 0.8, 'gold')
    for sx in (1, -1):
        blob(body, sx * 10.6, 6.4, 0.5, 2.4, 6.6, 11, 'iron', full=False)  # tassets
    for sx in (1, -1):                                                       # huge silver spiked pauldrons
        blob(body, sx * 15.5, 25.0, 0.5, 11.5, 9.6, 15.6, 'silver', decals={'north': [('rect', 0, 0.35, 1, 0.4, '#8e96a2'), ('rect', 0, 0.7, 1, 0.75, '#8e96a2')]})
        blob(body, sx * 15.8, 33.6, 0.5, 9.6, 3.4, 12.6, 'silver', full=False)
        cb(body, sx * 15.5, 24.6, 0.5, 12.2, 1.4, 16.2, 'silver_d')
        for z in (-4, 1, 6):
            spike(body, sx * 16.6, 36.6, z, 3.0, 'silver_d', tip='spike')
        spike(body, sx * 21.2, 29.6, 0.5, 3.2, 'silver_d', axis='x', sign=sx, tip='spike')
        for z in (-6, -2, 2, 6):
            cb(body, sx * 21.3, 25.0, z + 0.5, 0.6, 0.9, 0.9, 'rivet')
    head = m.bone('head', [0, 28, -1], body)
    eyes = eye(0.12, 0.15, 0.4, 0.85, '#4aa8e8', look=0.2, lid='#1a1a1a') + eye(0.6, 0.15, 0.88, 0.85, '#4aa8e8', look=0.2, lid='#1a1a1a')
    blob(head, 0, 27.6, -1, 15, 14, 14, 'iron', decals={'up': [('rect', 0.45, 0.0, 0.55, 1.0, '#272a31')]})   # big round helmet
    blob(head, 0, 40.6, -1, 11, 2.6, 10.4, 'iron_l', full=False)
    cb(head, 0, 32.4, -8.4, 9.6, 3.4, 1.0, 'skin', decals={'north': eyes})   # eyes behind the visor
    cb(head, 0, 31.8, -8.9, 1.4, 1.6, 0.8, 'skin')                          # nose bridge
    for sx in (1, -1):
        cb(head, sx * 1.8, 31.1, -9.0, 3.2, 1.0, 0.8, 'mous', rot=('z', -sx * 22.5))   # black mustache
    cb(head, 0, 35.8, -8.7, 13.4, 1.8, 1.4, 'iron_l')                       # visor brow bar
    cb(head, 0, 27.4, -8.7, 13.0, 4.2, 1.4, 'iron_l', decals={'north': [('rect', x, 0.2, x + 0.06, 0.8, '#15171a') for x in (0.2, 0.33, 0.61, 0.74)]})
    for sx in (1, -1):
        cb(head, sx * 5.6, 31.6, -8.7, 1.6, 4.2, 1.4, 'iron_l')
    blob(head, 0, 37.6, -1, 15.6, 2.2, 14.6, 'iron_l', full=False)
    for x in (-6, -3, 0, 3, 6):
        cb(head, x, 38.3, -8.4, 1.0, 1.0, 0.6, 'rivet')
    cb(head, 0, 43.0, -1, 3.6, 1.6, 3.6, 'iron_l')
    fe = m.bone('tc_feather', [0, 44, -1], head)                             # team-coloured feather plume
    cb(fe, 0, 44.2, -1.4, 2.8, 3.6, 2.8, 'cloth')
    cb(fe, 0, 46.4, 1.6, 2.4, 2.4, 4.6, 'cloth', rot=('x', 22.5))
    cb(fe, 0, 45.4, 5.2, 2.0, 2.0, 3.6, 'cloth', rot=('x', 45))
    cb(fe, 0, 43.2, 7.4, 1.4, 1.6, 2.6, 'cloth', rot=('x', 45))
    for sx, side in ((1, 'r'), (-1, 'l')):                                   # arms with maces built onto the forearms
        a = m.bone('arm_' + side, [sx * 14, 27, 0.5], body)
        blob(a, sx * 15, 18, 0.5, 7, 9, 7.5, 'iron_d', full=False)
        blob(a, sx * 15.3, 16.4, 0.5, 8.6, 3.4, 8.8, 'silver', full=False)
        blob(a, sx * 15.5, 11.4, 0, 9, 6.6, 9.6, 'iron')
        mx, my = sx * 15.5, 7.0
        blob(a, mx, my - 5.2, 0, 10.4, 10.4, 10.4, 'silver', r=2.4)
        spike(a, mx + sx * 5.2, my, 0, 2.6, 'silver_d', axis='x', sign=sx, tip='spike')
        spike(a, mx, my, -5.2, 2.6, 'silver_d', axis='z', sign=-1, tip='spike')
        spike(a, mx, my, 5.2, 2.6, 'silver_d', axis='z', sign=1, tip='spike')
        for (dx, dy, dz) in ((sx * 4.0, 3.6, -4.0), (sx * 4.0, -3.6, -4.0), (sx * 4.0, 3.6, 4.0), (sx * 4.0, -3.6, 4.0), (-sx * 4.0, -3.6, -4.0)):
            cb(a, mx + dx, my + dy - 1.1, dz, 2.2, 2.2, 2.2, 'spike')
    m.hitbox(2.0, 3.0)

    m.anim('idle', 2.4, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.6, 0]], 2.4), 'rotation': loop([[0, 0, 0], [2, 0, 0]], 2.4)},
        'arm_r': {'rotation': loop([[0, 0, 3], [-4, 0, 5]], 2.4)}, 'arm_l': {'rotation': loop([[0, 0, -3], [-4, 0, -5]], 2.4)},
        'head': {'rotation': loop([[0, 8, 0], [0, 0, 0], [0, -8, 0], [0, 0, 0]], 4.8)}})
    w = biped_walk(1.0, leg=22, arm=16, bob=-1.4, lean=4)
    w['body']['position'] = loop([[0, 0, 0], [0, -1.4, 0]], 0.5)
    m.anim('walk', 1.0, 'loop', w)
    smash = {s: {'rotation': [(0, [0, 0, 0]), (0.32, [-165, 0, -sg * 12]), (0.4, [-170, 0, -sg * 12]), (0.5, [-30, 0, -sg * 8]),
                              (0.62, [-28, 0, -sg * 6]), (0.8, [0, 0, 0])]} for s, sg in (('arm_r', 1), ('arm_l', -1))}
    smash['body'] = {'rotation': [(0, [0, 0, 0]), (0.36, [-10, 0, 0]), (0.5, [22, 0, 0]), (0.62, [18, 0, 0]), (0.8, [0, 0, 0])],
                     'position': [(0, [0, 0, 0]), (0.36, [0, 1, 1]), (0.5, [0, -4, -2]), (0.62, [0, -3.5, -1.5]), (0.8, [0, 0, 0])]}
    smash['leg_r'] = {'rotation': [(0, [0, 0, 0]), (0.5, [-20, 0, 0]), (0.8, [0, 0, 0])]}
    smash['leg_l'] = {'rotation': [(0, [0, 0, 0]), (0.5, [14, 0, 0]), (0.8, [0, 0, 0])]}
    smash['head'] = {'rotation': [(0, [0, 0, 0]), (0.36, [8, 0, 0]), (0.5, [-14, 0, 0]), (0.8, [0, 0, 0])]}
    m.anim('attack', 0.8, 'once', smash)
    m.anim('jump', 0.9, 'once', {
        'root': {'position': [(0, [0, 0, 0]), (0.15, [0, -3, 0]), (0.3, [0, 14, -4]), (0.45, [0, 24, -8]), (0.6, [0, 0, -12]),
                              (0.7, [0, -2, -12]), (0.9, [0, 0, -12])],
                 'scale': [(0, [1, 1, 1]), (0.15, [1.12, 0.84, 1.12]), (0.3, [0.94, 1.1, 0.94]), (0.58, [1, 1, 1]), (0.64, [1.18, 0.8, 1.18]),
                           (0.78, [0.97, 1.04, 0.97]), (0.9, [1, 1, 1])]},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [20, 0, 10]), (0.4, [-165, 0, 10]), (0.6, [-30, 0, -10]), (0.9, [0, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [20, 0, -10]), (0.4, [-165, 0, -10]), (0.6, [-30, 0, 10]), (0.9, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-25, 0, 0]), (0.4, [-40, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.15, [-25, 0, 0]), (0.4, [-40, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.15, [14, 0, 0]), (0.4, [-8, 0, 0]), (0.62, [20, 0, 0]), (0.9, [0, 0, 0])]}})
    common_tail(m, spawn={'root': {'position': [(0, [0, 30, 0]), (0.25, [0, 0, 0]), (0.5, [0, 0, 0])],
                                   'scale': [(0, [1, 1, 1]), (0.25, [1, 1, 1]), (0.3, [1.18, 0.8, 1.18]), (0.42, [0.97, 1.04, 0.97]), (0.5, [1, 1, 1])]}},
                death={'root': {'rotation': [(0, [0, 0, 0]), (0.3, [6, 0, 0]), (0.7, [-80, 0, 0]), (0.9, [-88, 0, 0])],
                                'position': [(0, [0, 0, 0]), (0.9, [0, -1, 4])]},
                       'arm_r': {'rotation': [(0, [0, 0, 0]), (0.7, [0, 0, 60])]}, 'arm_l': {'rotation': [(0, [0, 0, 0]), (0.7, [0, 0, -60])]}})
    return m


# =================================================================== Giant Skeleton
def giant_skeleton():
    """CR-style Giant Skeleton: tall bony giant, big dark-grey skull with a heavy jaw, huge black bomb with a lit fuse
    strapped on his back (bone 'bomb'), team-coloured straps and loincloth. attack = heavy two-handed punch."""
    m = Model('clash_giant_skeleton', density=2.0)
    m.mats_({
        'bone': ('#ece6d2', 'bone'), 'bone_d': ('#c7bfa6', 'bone'), 'skull': ('#f2eee2', 'bone'), 'skull_d': ('#d6cfba', 'bone'),
        'tooth': ('#fbf8ee', 'bone'), 'bomb': ('#1d1e22', 'metal'), 'iron': ('#4a4d55', 'metal', {'rivets': True}),
        'rope': ('#8a6a40', 'rope'), 'spark': ('#ffd04a', 'glow'), 'flame': ('#ff8a1e', 'glow'), 'cloth': ('#efefef', 'cloth'),
        'fur': ('#efefef', 'fur'), 'fur_d': ('#d2d2d2', 'fur'), 'leather': ('#8a5a2e', 'leather'), 'wood': ('#8a5a32', 'wood', {'grain': 'v'}),
        'wood_l': ('#b07a44', 'wood'), 'hoop': ('#3a3c42', 'metal', {'rivets': True}), 'socket': ('#141416', 'plain'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 4.5, 19, 0], root)
        blob(lg, sx * 4.5, 16.6, 0, 4.6, 2.8, 4.6, 'bone_d', full=False)
        cb(lg, sx * 4.5, 10.6, 0, 3.0, 6.4, 3.0, 'bone')
        blob(lg, sx * 4.5, 8.2, 0, 4.6, 3.0, 4.8, 'bone_d', full=False)
        cb(lg, sx * 4.5, 2.4, 0, 2.6, 6.0, 2.6, 'bone')
        cb(lg, sx * 5.7, 2.8, 0.6, 1.2, 5.4, 1.2, 'bone_d')
        blob(lg, sx * 4.5, 0, -1.6, 5.8, 2.6, 8.2, 'bone_d', full=False)
        for dx in (-1.8, 0, 1.8):
            cb(lg, sx * 4.5 + dx, 0, -6.4, 1.4, 1.4, 1.8, 'bone')
    body = m.bone('body', [0, 19, 0], root)
    blob(body, 0, 17.4, 0, 12.4, 4.2, 6.6, 'bone', full=False)
    for y in (21.4, 23.6, 25.8, 28.0, 30.2):
        cb(body, 0, y, 2.4, 3.0, 1.6, 3.0, 'bone_d')                          # spine
    for y, hw in ((23.4, 6.2), (25.8, 7.2), (28.2, 7.8)):                    # curved ribs
        for sx in (1, -1):
            cb(body, sx * (hw / 2 + 0.6), y, -4.2, hw - 1.0, 1.4, 1.4, 'bone')
            cb(body, sx * (hw + 0.4), y, -0.6, 1.4, 1.4, 7.6, 'bone')
            cb(body, sx * (hw / 2 + 0.8), y, 3.4, hw - 0.6, 1.4, 1.2, 'bone_d')
    blob(body, 0, 22.6, -4.9, 2.6, 9.0, 1.4, 'bone', full=False)
    blob(body, 0, 31.2, 0.5, 22, 2.8, 8.4, 'bone', full=False)
    blob(body, -11.6, 32.0, 0.5, 7.0, 3.4, 7.4, 'leather', full=False)      # leather shoulder guard
    tc = m.bone('tc_straps', [0, 25, 0], body)
    cb(tc, 0, 12.2, -3.4, 7.6, 6.8, 0.8, 'cloth')
    cb(tc, 0, 12.2, 3.4, 8.6, 6.8, 0.8, 'cloth')
    cb(tc, 0, 18.0, 0, 12.8, 1.6, 7.2, 'cloth')
    for sx in (1, -1):
        cb(tc, sx * 4.2, 22.0, -5.6, 2.2, 10.0, 0.8, 'cloth')
        cb(tc, sx * 4.2, 33.2, 0.5, 2.4, 0.8, 9.4, 'cloth')
    head = m.bone('head', [0, 33, -0.5], body)
    cb(head, 0, 31.4, 0.8, 3.2, 2.6, 3.2, 'bone_d')
    sockets = [('rect', 0.06, 0.3, 0.46, 0.76, '#141416'), ('rect', 0.54, 0.3, 0.94, 0.76, '#141416'),
               ('rect', 0.1, 0.26, 0.42, 0.3, '#3a3a3e'), ('rect', 0.58, 0.26, 0.9, 0.3, '#3a3a3e'),
               ('rect', 0.06, 0.3, 0.1, 0.4, '#f2eee2'), ('rect', 0.9, 0.3, 0.94, 0.4, '#f2eee2'),
               ('rect', 0.43, 0.78, 0.57, 0.96, '#2a2a2e'), ('rect', 0.47, 0.82, 0.53, 0.96, '#141416')]
    blob(head, 0, 35.4, -1.0, 13.2, 10.6, 12.2, 'skull', r=2.2, decals={'north': sockets})   # big white skull
    for sx in (1, -1):
        blob(head, sx * 5.2, 35.2, -6.2, 2.8, 2.4, 1.8, 'skull', full=False)  # cheekbones
    blob(head, 0, 43.0, -6.6, 12.8, 1.4, 1.8, 'skull_d', full=False)        # brow ridge
    cb(head, 0, 33.6, -5.6, 9.6, 2.2, 2.4, 'skull')
    for x in (-3.6, -1.8, 0, 1.8, 3.6):
        cb(head, x, 32.8, -6.9, 1.6, 1.8, 1.0, 'tooth')
    jaw = m.bone('jaw', [0, 35, 2], head)
    blob(jaw, 0, 29.8, -3.6, 13.8, 4.8, 12.4, 'skull_d', full=False)        # big underbite jaw
    cb(jaw, 0, 30.0, -10.2, 9.0, 3.8, 1.8, 'skull_d')
    for x in (-4.0, -2.4, -0.8, 0.8, 2.4, 4.0):
        cb(jaw, x, 33.6, -10.2, 1.4, 2.4, 1.0, 'tooth')                      # lower teeth in front
    hat = m.bone('tc_hat', [0, 45, -1.5], head)                              # team-coloured fur ushanka
    blob(hat, 0, 45.2, -1.2, 13.4, 5.4, 12.8, 'fur')
    blob(hat, 0, 50.2, -1.2, 9.6, 1.8, 9.0, 'fur', full=False)
    blob(hat, 0, 44.2, -7.8, 14.8, 3.8, 2.8, 'fur_d')
    blob(hat, 0, 42.8, 5.2, 14.0, 3.6, 2.2, 'fur_d', full=False)
    for sx in (1, -1):
        blob(hat, sx * 8.0, 36.0, 0.4, 2.2, 9.4, 8.4, 'fur_d')              # ear flaps
        cb(hat, sx * 8.0, 34.6, 0.4, 0.8, 1.6, 0.8, 'fur')
    bar = m.bone('barrel', [0, 26, 11], body)                               # gunpowder barrel on the back
    staves = [('rect', x, 0, x + 0.02, 1, '#5a3a20') for x in (0.25, 0.5, 0.75)]
    blob(bar, 0, 18.2, 11.6, 12.4, 15.4, 12.4, 'wood', r=2.4, decals={'south': staves + [('rect', 0.3, 0.38, 0.7, 0.62, '#1a1a1a'), ('rect', 0.38, 0.44, 0.62, 0.56, '#e8d8a8')],
                                                                        'east': staves, 'west': staves})
    for y in (19.6, 25.0, 30.6):
        blob(bar, 0, y, 11.6, 12.9, 1.2, 12.9, 'hoop', r=2.4, full=False)
    cb(bar, 0, 33.5, 11.6, 9.0, 0.6, 9.0, 'wood_l')
    cb(bar, 0, 25.4, 5.0, 14.0, 1.6, 1.2, 'leather')
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 11, 32.5, 0.5], body)
        blob(a, sx * 11.5, 30.0, 0.5, 5.6, 3.8, 5.6, 'bone_d', full=False)
        cb(a, sx * 11.5, 22.4, 0.5, 3.0, 7.8, 3.0, 'bone')
        blob(a, sx * 11.5, 19.8, 0.5, 4.6, 3.0, 4.6, 'bone_d', full=False)
        cb(a, sx * 10.9, 12.6, 0.5, 1.6, 7.4, 1.8, 'bone')
        cb(a, sx * 12.1, 12.6, 0.5, 1.6, 7.4, 1.8, 'bone')
        cb(a, sx * 11.5, 11.6, 0.4, 3.8, 1.4, 3.8, 'bone_d')
        blob(a, sx * 11.5, 7.2, 0, 6.8, 4.6, 5.6, 'bone', full=False)       # big bony hand
        for i in range(4):
            cb(a, sx * 11.5 - 2.5 + i * 1.66, 4.4, -2.2, 1.3, 3.2, 1.4, 'bone')
        cb(a, sx * 11.5 - sx * 3.6, 6.4, -1.2, 1.4, 2.8, 1.4, 'bone')
    bomb = m.bone('bomb', [11.5, 4.6, -4.2], m.by_name('arm_r'))           # black bomb held in the right hand
    blob(bomb, 11.5, 0.2, -4.6, 9.6, 9.6, 9.6, 'bomb', r=2.6, decals={'north': [('rect', 0.15, 0.15, 0.35, 0.3, '#6a6c74')]})
    cb(bomb, 11.5, 9.6, -4.6, 3.2, 1.4, 3.2, 'iron')
    cb(bomb, 11.5, 11.0, -4.6, 0.9, 1.8, 0.9, 'rope')
    fz = m.bone('fuse', [11.5, 12.8, -4.2], bomb)
    cb(fz, 11.5, 12.0, -4.2, 1.8, 1.8, 1.8, 'flame')
    cb(fz, 11.5, 12.4, -4.2, 1.0, 1.0, 1.0, 'spark')
    m.scale_bone('root', 1.12, [0, 0, 0])                                    # tall: ~57 px
    m.scale_bone('head', 1.45, m.by_name('head').origin)                     # huge CR-style skull + hat
    m.hitbox(1.6, 3.6)

    m.anim('idle', 2.4, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.6, 0]], 2.4)},
        'jaw': {'rotation': loop([[0, 0, 0], [10, 0, 0]], 1.2)},
        'head': {'rotation': loop([[0, 10, 0], [0, 0, 0], [0, -10, 0], [0, 0, 0]], 4.8)},
        'fuse': {'scale': loop([[1, 1, 1], [1.4, 1.6, 1.4]], 0.3)},
        'arm_r': {'rotation': loop([[0, 0, 2], [-5, 0, 4]], 2.4)}, 'arm_l': {'rotation': loop([[0, 0, -2], [-5, 0, -4]], 2.4)}})
    w = biped_walk(1.1, leg=22, arm=20, bob=1.0, lean=5)
    w['jaw'] = {'rotation': loop([[0, 0, 0], [8, 0, 0]], 0.55)}
    w['bomb'] = {'rotation': loop([[3, 0, 0], [-3, 0, 0]], 0.55)}
    w['fuse'] = {'scale': loop([[1, 1, 1], [1.4, 1.6, 1.4]], 0.3)}
    m.anim('walk', 1.1, 'loop', w)
    punch = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [35, 0, sg * 25]), (0.42, [38, 0, sg * 25]), (0.55, [-92, -sg * 24, 0]),
                              (0.7, [-88, -sg * 22, 0]), (1.0, [0, 0, 0])]} for s, sg in (('arm_r', 1), ('arm_l', -1))}
    punch['body'] = {'rotation': [(0, [0, 0, 0]), (0.4, [-10, 0, 0]), (0.55, [18, 0, 0]), (0.7, [15, 0, 0]), (1.0, [0, 0, 0])],
                     'position': [(0, [0, 0, 0]), (0.4, [0, 0, 1.5]), (0.55, [0, -1.5, -2.5]), (1.0, [0, 0, 0])]}
    punch['jaw'] = {'rotation': [(0, [0, 0, 0]), (0.4, [5, 0, 0]), (0.55, [22, 0, 0]), (1.0, [0, 0, 0])]}
    punch['leg_r'] = {'rotation': [(0, [0, 0, 0]), (0.55, [-16, 0, 0]), (1.0, [0, 0, 0])]}
    punch['leg_l'] = {'rotation': [(0, [0, 0, 0]), (0.55, [12, 0, 0]), (1.0, [0, 0, 0])]}
    m.anim('attack', 1.0, 'once', punch)
    common_tail(m, death={
        'root': {'scale': [(0, [1, 1, 1]), (0.5, [1, 0.9, 1]), (0.9, [1.05, 0.25, 1.05])], 'position': [(0, [0, 0, 0]), (0.9, [0, -1, 0])]},
        'bomb': {'position': [(0, [0, 0, 0]), (0.35, [0, -8, 6]), (0.9, [0, -14, 8])], 'rotation': [(0, [0, 0, 0]), (0.9, [-30, 20, 0])]},
        'fuse': {'scale': [(0, [1, 1, 1]), (0.45, [1.8, 2.2, 1.8]), (0.9, [2.2, 2.6, 2.2])]},
        'jaw': {'rotation': [(0, [0, 0, 0]), (0.4, [30, 0, 0])]}})
    return m


# =================================================================== Valkyrie
def valkyrie():
    """CR-style Valkyrie: orange braided pigtails, horned steel helmet, fur-trimmed brown leather outfit,
    big double-bladed battle axe (bone 'axe', grip through the right fist). attack = full 360 spin with the axe out."""
    m = Model('clash_valkyrie', density=2.0)
    m.mats_({
        'skin': ('#f6c2a0', 'skin'), 'skin_d': ('#e8a688', 'skin'), 'hair': ('#f2621e', 'hair'), 'hair_d': ('#c8461a', 'hair'),
        'hair_l': ('#ff8a3a', 'hair'), 'leather': ('#7a4a26', 'leather'), 'fur': ('#efe0c0', 'fur'), 'steel': ('#bcc3cd', 'metal'),
        'steel_d': ('#7d838d', 'metal', {'rivets': True}), 'wood': ('#7a4e2a', 'wood'), 'edge': ('#f2f6fa', 'metal'), 'gold': ('#f0c040', 'metal'),
        'boot': ('#6a4026', 'leather'), 'cloth': ('#efefef', 'cloth'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.5, 7, 0], root)
        cb(lg, sx * 2.5, 3.4, 0, 3.6, 3.8, 3.8, 'skin')
        blob(lg, sx * 2.5, 0, -0.5, 4.8, 3.4, 6.2, 'boot')
        cb(lg, sx * 2.5, 0, -3.5, 4.0, 1.8, 0.8, 'leather')                 # toe cap
        blob(lg, sx * 2.5, 2.9, -0.4, 5.6, 1.9, 6.6, 'fur', full=False)      # fur cuff
    body = m.bone('body', [0, 7, 0], root)
    tc = m.bone('tc_belt', [0, 9, 0], body)                                 # team-coloured suit
    pleat = [('rect', x, 0.1, x + 0.03, 1.0, '#c8c8c8') for x in (0.2, 0.4, 0.6, 0.8)]
    blob(tc, 0, 4.4, 0, 10.6, 4.2, 7.2, 'cloth', decals={'north': pleat, 'south': pleat, 'east': pleat, 'west': pleat})
    blob(tc, 0, 8.6, 0, 9.2, 6.4, 6.0, 'cloth', decals={'north': [('rect', 0.32, 0.0, 0.68, 0.22, '#f6c2a0'), ('rect', 0.42, 0.22, 0.58, 0.32, '#f6c2a0')]})
    for sx in (1, -1):
        cb(tc, sx * 2.6, 14.2, 0, 1.6, 1.0, 5.6, 'cloth')                    # shoulder straps
    cb(body, 0, 8.0, 0, 9.8, 1.6, 6.6, 'leather', decals={'north': [('px', x, 0.5, '#d9a63a') for x in (0.1, 0.3, 0.7, 0.9)]})
    cb(body, 0, 7.8, -3.5, 2.4, 2.0, 0.6, 'gold')
    cb(body, 0, 14.6, 0, 4.4, 1.4, 3.6, 'skin')
    head = m.bone('head', [0, 15.5, 0], body)
    face = eye(0.08, 0.3, 0.44, 0.64, '#3a8ee0', look=0.3) + eye(0.56, 0.3, 0.92, 0.64, '#3a8ee0', look=0.3) + \
        [('rect', 0.28, 0.72, 0.72, 0.96, '#6a1414'), ('rect', 0.3, 0.72, 0.7, 0.8, '#ffffff'), ('rect', 0.36, 0.86, 0.64, 0.96, '#e05a6a'),
         ('rect', 0.06, 0.64, 0.22, 0.72, '#f29a8a'), ('rect', 0.78, 0.64, 0.94, 0.72, '#f29a8a')]
    blob(head, 0, 15.0, -0.4, 9.2, 8.6, 8.2, 'skin', decals={'north': face})   # big round head
    cb(head, 0, 17.0, -5.0, 1.6, 1.9, 1.3, 'skin_d')                        # nose
    for sx in (1, -1):
        cb(head, sx * 2.3, 20.2, -4.7, 3.4, 0.9, 0.9, 'hair_d', rot=('z', sx * 22.5))   # angry orange brows
        cb(head, sx * 4.7, 15.8, -0.2, 0.8, 2.0, 1.6, 'skin_d')             # ears
    blob(head, 0, 22.2, 0.8, 11.4, 4.8, 10.6, 'hair')                       # voluminous hair
    blob(head, 0.6, 26.0, 1.2, 8.4, 1.8, 7.6, 'hair_l', full=False)
    cb(head, 1.8, 21.6, -4.8, 7.4, 2.6, 1.6, 'hair_l')                      # swept fringe
    cb(head, -3.4, 21.4, -4.7, 3.6, 2.4, 1.4, 'hair')
    for (x, y, z) in ((-5.6, 24.6, -2.0), (5.4, 25.0, -1.0), (-4.2, 26.4, 3.0), (3.6, 26.6, 3.6), (0.0, 23.0, 6.2), (-6.4, 19.0, 3.6), (6.4, 19.4, 3.0)):
        blob(head, x, y, z, 3.0, 2.6, 3.0, 'hair_l', full=False)           # curls
    blob(head, 0, 10.4, 4.4, 11.8, 13.2, 3.4, 'hair')                       # back mass
    for sx in (1, -1):
        blob(head, sx * 6.1, 11.4, 1.8, 2.4, 11.6, 7.2, 'hair', full=False)  # side hair
        for k, y in enumerate((8.4, 5.8, 3.2)):                               # thick braids over the shoulders
            blob(head, sx * 5.4, y, -2.2, 3.1 - k * 0.2, 2.7, 3.1 - k * 0.2, 'hair' if k % 2 == 0 else 'hair_l', full=False)
        cb(head, sx * 5.4, 2.6, -2.2, 3.0, 0.8, 3.0, 'leather')
        cb(head, sx * 5.4, 1.2, -2.2, 2.0, 1.4, 2.0, 'hair_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5.6, 13, 0], body)
        blob(a, sx * 6.0, 10.0, 0, 3.9, 3.6, 3.9, 'skin', full=False)        # shoulder / bicep
        cb(a, sx * 6.1, 7.4, 0, 3.4, 3.0, 3.5, 'skin')
        wb = m.bone('tc_wrist_' + side, [sx * 6.1, 7, 0], a)
        blob(wb, sx * 6.1, 5.4, 0, 4.0, 2.1, 4.1, 'cloth', full=False)
        fist(a, sx * 6.1, 2.2, -0.2, 3.8, 'skin', side=sx, knuckle='skin_d')
    H = (6.1, 4.0, -0.2)
    axe = m.bone('axe', list(H), m.by_name('arm_r'))
    hx, hy, hz = H
    cb(axe, hx, hy - 4, hz, 1.5, 21, 1.5, 'wood')                            # haft through the fist
    for y in (hy + 3.2, hy - 3.0):
        cb(axe, hx, y, hz, 1.9, 1.0, 1.9, 'leather')
    cb(axe, hx, hy - 5.2, hz, 2.2, 1.4, 2.2, 'gold')
    blob(axe, hx, hy + 9.6, hz, 2.8, 4.6, 2.8, 'steel_d', full=False)
    cb(axe, hx, hy + 14.2, hz, 1.2, 2.4, 1.2, 'steel')
    for sz in (1, -1):                                                       # big double crescent blades
        cb(axe, hx, hy + 9.0, hz + sz * 3.6, 1.4, 6.6, 3.0, 'steel')
        cb(axe, hx, hy + 7.8, hz + sz * 6.0, 1.4, 9.0, 2.2, 'steel')
        cb(axe, hx, hy + 7.0, hz + sz * 7.8, 1.3, 10.6, 1.6, 'steel')
        cb(axe, hx, hy + 7.2, hz + sz * 8.95, 1.1, 10.2, 0.7, 'edge')
        cb(axe, hx, hy + 17.4, hz + sz * 8.0, 1.1, 1.2, 1.2, 'edge')
        cb(axe, hx, hy + 6.0, hz + sz * 8.0, 1.1, 1.2, 1.2, 'edge')
    m.hitbox(1.0, 1.8)

    m.anim('idle', 2.0, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)},
        'head': {'rotation': loop([[0, 8, 0], [0, 0, 0], [0, -8, 0], [0, 0, 0]], 4.0)},
        'arm_r': {'rotation': loop([[-10, 0, 4], [-14, 0, 5]], 2.0)}, 'arm_l': {'rotation': loop([[0, 0, -3], [4, 0, -4]], 2.0)}})
    w = biped_walk(0.7, leg=26, arm=24, bob=0.8, lean=5)
    w['arm_r'] = {'rotation': loop([[-14, 0, 4], [-6, 0, 4]], 0.7)}
    m.anim('walk', 0.7, 'loop', w)
    spin_t = [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.245, [0, -90, 0]), (0.37, [0, -180, 0]), (0.495, [0, -270, 0]), (0.62, [0, -360, 0]), (0.8, [0, -360, 0])]
    m.anim('attack', 0.8, 'once', {
        'root': {'rotation': spin_t},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 82]), (0.62, [0, 0, 82]), (0.8, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -172]), (0.62, [0, 0, -172]), (0.8, [0, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -70]), (0.62, [0, 0, -70]), (0.8, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.12, [6, 0, -6]), (0.62, [6, 0, -6]), (0.8, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.12, [0, -1, 0]), (0.62, [0, -1, 0]), (0.8, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (0.12, [-10, 0, 8]), (0.62, [-10, 0, 8]), (0.8, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.12, [10, 0, -8]), (0.62, [10, 0, -8]), (0.8, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Executioner
def executioner():
    """CR-style Executioner: big bare-chested man in a black executioner's hood with eye holes, chest strap,
    huge double-crescent axe (bone 'axe'). attack = throws the axe forward, it spins out and flies back."""
    m = Model('clash_executioner', density=2.0)
    m.mats_({
        'skin': ('#f0a890', 'skin'), 'skin_d': ('#d08870', 'skin'), 'hood': ('#26242a', 'leather', {'stitch': False}), 'hood_l': ('#55515c', 'leather'),
        'boot': ('#1e1a18', 'leather'), 'leather': ('#3a2a20', 'leather'), 'glove': ('#2a2a2e', 'leather', {'stitch': False}),
        'steel': ('#c9d0d9', 'metal'), 'edge': ('#f4f8fc', 'metal'), 'iron': ('#555a62', 'metal', {'rivets': True}), 'wood': ('#4e3220', 'wood'),
        'nose': ('#e8505a', 'skin'), 'gold': ('#d9a63a', 'metal'), 'cloth': ('#efefef', 'cloth'), 'blush': ('#f08a80', 'skin'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 3.4, 9, 0], root)
        tp = m.bone('tc_pants_' + side, [sx * 3.4, 9, 0], lg)                # team-coloured pants
        blob(tp, sx * 3.4, 3.2, 0, 5.8, 6.2, 6.0, 'cloth', full=False)
        blob(lg, sx * 3.4, 0, -0.8, 6.4, 3.8, 7.6, 'boot')
        cb(lg, sx * 3.4, 0, -4.4, 5.2, 2.2, 0.8, 'leather')
        cb(lg, sx * 3.4, 3.4, -0.6, 6.8, 1.0, 7.2, 'leather')
    body = m.bone('body', [0, 9, 0], root)
    chest = [('rect', 0.14, 0.2, 0.46, 0.24, '#d08870'), ('rect', 0.54, 0.2, 0.86, 0.24, '#d08870'), ('rect', 0.48, 0.24, 0.52, 0.5, '#d08870')]
    blob(body, 0, 9.4, 0.2, 14, 11.6, 8.6, 'skin', decals={'north': chest})
    blob(body, 0, 8.6, -3.6, 11.6, 8.8, 4.8, 'skin', decals={'north': [('rect', 0.47, 0.58, 0.53, 0.66, '#b06a58')]})   # big round belly
    for sx in (1, -1):
        blob(body, sx * 3.4, 15.6, -4.0, 5.4, 3.2, 1.4, 'skin', full=False)   # pecs
    blob(body, 0, 7.8, 0, 14.8, 2.6, 9.6, 'leather', full=False, decals={'north': [('px', x, 0.5, '#d9a63a') for x in (0.08, 0.25, 0.75, 0.92)]})
    cb(body, 0, 7.6, -5.0, 3.2, 3.0, 0.6, 'gold')
    cb(body, 0, 13.6, 4.45, 2.4, 13.0, 0.6, 'leather', rot=('z', 45))
    for (x, y) in ((-1.2, 17.2), (1.0, 16.6), (0.0, 15.6), (-0.6, 13.6), (0.6, 12.6)):
        cb(body, x, y, -5.0, 0.6, 1.0, 0.4, 'leather')                      # chest hair tufts
    for sx in (1, -1):
        cb(body, sx * 5.6, 7.2, -4.9, 1.8, 3.4, 0.8, 'leather')               # belt pouches/loops
        cb(body, sx * 5.6, 7.0, -5.2, 1.0, 1.0, 0.4, 'gold')
    tc = m.bone('tc_kilt', [0, 8, 0], body)                                   # team-coloured kilt
    pleat = [('rect', x, 0, x + 0.03, 1, '#c4c4c4') for x in (0.2, 0.4, 0.6, 0.8)]
    cb(tc, 0, 3.2, -4.4, 12.4, 5.0, 1.0, 'cloth', decals={'north': pleat})
    cb(tc, 0, 3.2, 4.6, 13.0, 5.0, 1.0, 'cloth', decals={'south': pleat})
    for x in (-4.8, -1.6, 1.6, 4.8):
        cb(body, x, 7.2, -5.0, 0.8, 0.8, 0.5, 'gold')                       # belt studs
    for sx, side in ((1, 'r'), (-1, 'l')):
        lgb = m.by_name('leg_' + side)
        for y in (1.2, 2.6):
            cb(lgb, sx * 3.4, y, -4.5, 5.6, 0.6, 0.6, 'leather')             # boot straps
        cb(lgb, sx * 3.4 + sx * 2.9, 1.6, -0.8, 0.6, 1.4, 1.4, 'gold')
    for sx in (1, -1):
        cb(tc, sx * 6.8, 3.2, 0, 1.0, 5.0, 8.8, 'cloth', decals={'east': pleat, 'west': pleat})
    head = m.bone('head', [0, 21, 0], body)
    grin = [('rect', 0.0, 0.55, 1.0, 1.0, '#d8a090'), ('rect', 0.1, 0.44, 0.9, 0.86, '#6a1414'), ('rect', 0.12, 0.44, 0.88, 0.62, '#ffffff'),
            ('rect', 0.3, 0.44, 0.31, 0.62, '#d0d0d0'), ('rect', 0.5, 0.44, 0.51, 0.62, '#d0d0d0'), ('rect', 0.69, 0.44, 0.7, 0.62, '#d0d0d0'),
            ('rect', 0.3, 0.7, 0.7, 0.86, '#e05a6a'), ('rect', 0.06, 0.4, 0.12, 0.5, '#6a1414'), ('rect', 0.88, 0.4, 0.94, 0.5, '#6a1414')]
    blob(head, 0, 19.0, -0.4, 11.0, 8.0, 10.0, 'skin', decals={'north': grin})   # lower face: big grin + stubble
    for sx in (1, -1):
        blob(head, sx * 3.8, 22.4, -5.0, 2.8, 2.2, 1.2, 'blush', full=False)  # cheeks
    blob(head, 0, 23.6, -6.6, 3.8, 3.2, 2.8, 'nose')                          # big round red nose
    eyes = [('rect', 0.1, 0.28, 0.46, 0.74, '#f0a890'), ('rect', 0.54, 0.28, 0.9, 0.74, '#f0a890')] + \
        eye(0.14, 0.36, 0.42, 0.68, '#3a8ee0', look=0.2) + eye(0.58, 0.36, 0.86, 0.68, '#3a8ee0', look=0.2)
    blob(head, 0, 25.6, -0.4, 11.8, 8.0, 10.8, 'hood', decals={'north': eyes})
    cb(head, 0, 25.4, -0.4, 12.2, 0.8, 11.2, 'hood_l')                       # hood rim
    cb(head, 0, 33.4, -0.4, 1.0, 0.5, 10.0, 'hood_l')                        # stitched seam
    for z in (-3.6, -1.2, 1.2, 3.6):
        cb(head, 0, 33.4, z - 0.4, 2.2, 0.5, 0.5, 'hood_l')
    blob(head, 0, 19.4, 4.4, 11.8, 7.2, 2.2, 'hood', full=False)            # hood back drape
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 8.6, 19, 0], body)
        blob(a, sx * 9.2, 14.8, 0, 5.4, 4.6, 5.6, 'skin', full=False)
        cb(a, sx * 9.3, 11.4, 0, 4.8, 4.0, 5.0, 'skin')
        blob(a, sx * 9.3, 8.2, 0, 5.8, 3.4, 6.0, 'glove', full=False)
        fist(a, sx * 9.3, 4.2, -0.2, 5.0, 'glove', side=sx)
    al = m.by_name('arm_l')
    blob(al, -9.4, 17.6, 0, 6.6, 2.8, 7.0, 'iron', full=False)               # shoulder guard
    for z in (-2.4, 0, 2.4):
        cb(al, -12.8, 18.6, z, 0.6, 0.8, 0.8, 'gold')
    H = (9.3, 6.4, -0.2)
    axe = m.bone('axe', list(H), m.by_name('arm_r'))
    hx, hy, hz = H
    cb(axe, hx, hy - 5, hz, 1.8, 23, 1.8, 'wood')
    for y in (hy + 4.0, hy - 3.6):
        cb(axe, hx, y, hz, 2.2, 1.0, 2.2, 'leather')
    cb(axe, hx, hy - 6, hz, 2.4, 1.4, 2.4, 'iron')
    blob(axe, hx, hy + 9.8, hz, 3.4, 6.0, 3.4, 'iron', full=False)
    cb(axe, hx, hy + 18.0, hz, 1.6, 2.0, 1.6, 'iron')
    for sz in (1, -1):
        cb(axe, hx + 0.9, hy + 12.4, hz + sz * 0.9, 0.5, 0.8, 0.8, 'gold')     # hub rivets
    for sz in (1, -1):                                                       # two huge round crescent blades
        cb(axe, hx, hy + 8.6, hz + sz * 4.2, 1.6, 8.4, 3.6, 'steel')
        cb(axe, hx, hy + 6.8, hz + sz * 7.2, 1.6, 12.0, 2.8, 'steel')
        cb(axe, hx, hy + 5.6, hz + sz * 9.4, 1.5, 14.4, 1.8, 'steel')
        if sz > 0:
            cb(axe, hx, hy + 5.8, hz + sz * 10.6, 1.3, 14.0, 0.8, 'edge')
        else:                                                                # chipped blade
            cb(axe, hx, hy + 5.8, hz + sz * 10.6, 1.3, 6.2, 0.8, 'edge')
            cb(axe, hx, hy + 14.6, hz + sz * 10.6, 1.3, 5.2, 0.8, 'edge')
        cb(axe, hx, hy + 19.6, hz + sz * 9.4, 1.3, 1.6, 1.6, 'edge')
        cb(axe, hx, hy + 4.2, hz + sz * 9.4, 1.3, 1.6, 1.6, 'edge')
    m.hitbox(1.2, 2.35)

    m.anim('idle', 2.2, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.4, 0]], 2.2), 'rotation': loop([[0, 0, 0], [2, 0, 0]], 2.2)},
        'head': {'rotation': loop([[0, 8, 0], [0, 0, 0], [0, -8, 0], [0, 0, 0]], 4.4)},
        'arm_r': {'rotation': loop([[-8, 0, 4], [-12, 0, 5]], 2.2)}, 'arm_l': {'rotation': loop([[0, 0, -3], [3, 0, -4]], 2.2)}})
    w = biped_walk(0.8, leg=24, arm=22, bob=0.9, lean=4)
    w['arm_r'] = {'rotation': loop([[-12, 0, 4], [-4, 0, 4]], 0.8)}
    m.anim('walk', 0.8, 'loop', w)
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.18, [-150, 0, 10]), (0.26, [-80, 0, 0]), (0.66, [-80, 0, 0]), (0.8, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.26, [0, 0, 0]), (0.36, [-200, 0, 0]), (0.46, [-400, 0, 0]), (0.56, [-600, 0, 0]),
                             (0.66, [-720, 0, 0]), (0.8, [-720, 0, 0])],
                'position': [(0, [0, 0, 0]), (0.26, [0, 0, 0]), (0.46, [0, -38, 0]), (0.66, [0, 0, 0]), (0.8, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.18, [-8, 10, 0]), (0.28, [12, -10, 0]), (0.6, [6, 0, 0]), (0.8, [0, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.18, [-30, 0, 0]), (0.3, [20, 0, 0]), (0.8, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Lumberjack
def lumberjack():
    """CR-style Lumberjack: wild hair, bushy beard, crazed grin, team-coloured plaid shirt (red/black plaid in
    the team colour), jeans, big woodcutter's axe (bone 'axe'). attack = fast double chop, walk = fast run."""
    m = Model('clash_lumberjack', density=2.0)
    m.mats_({
        'skin': ('#f6c2a0', 'skin'), 'skin_d': ('#d89a7a', 'skin'), 'beard': ('#ee8a2a', 'hair'), 'beard_d': ('#c86a1a', 'hair'),
        'beard_l': ('#ffa64a', 'hair'), 'pants': ('#5a3a24', 'cloth'), 'boot': ('#6a4026', 'leather'), 'leather': ('#4a2c18', 'leather'),
        'wood': ('#a0703c', 'wood'), 'iron': ('#555a62', 'metal', {'rivets': True}), 'steel': ('#c4cad3', 'metal'), 'edge': ('#f2f6fa', 'metal'),
        'cloth': ('#efefef', 'cloth'), 'nose': ('#e8484a', 'skin'), 'glass': ('#a24ae8', 'glow'), 'glass_l': ('#d6a0ff', 'glow'),
        'cork': ('#a0703c', 'wood'), 'fur': ('#efefef', 'fur'), 'fur_d': ('#d6d6d6', 'fur'), 'mouth': ('#5a1010', 'plain'),
        'tooth': ('#fbf8ee', 'bone'), 'tongue': ('#f07a8a', 'skin'), 'gold': ('#c9a03a', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.4, 7, 0], root)
        blob(lg, sx * 2.4, 3.4, 0, 4.2, 4.0, 4.4, 'pants', full=False)
        cb(lg, sx * 2.4, 1.0, 0, 3.2, 2.6, 3.4, 'skin')
        blob(lg, sx * 2.4, 0, -0.6, 4.4, 1.0, 6.2, 'boot', full=False)       # sandals
        cb(lg, sx * 2.4, 1.0, -2.0, 3.8, 0.6, 0.8, 'boot')
        cb(lg, sx * 2.4, 2.2, 0, 3.6, 0.6, 3.8, 'boot')
        cb(lg, sx * 2.4, 1.0, -3.0, 3.0, 0.9, 1.0, 'skin_d')                 # toes
    body = m.bone('body', [0, 7, 0], root)
    musc = [('rect', 0.12, 0.18, 0.46, 0.22, '#d89a7a'), ('rect', 0.54, 0.18, 0.88, 0.22, '#d89a7a'), ('rect', 0.48, 0.22, 0.52, 0.95, '#d89a7a'),
            ('rect', 0.3, 0.55, 0.7, 0.57, '#d89a7a'), ('rect', 0.3, 0.72, 0.7, 0.74, '#d89a7a'), ('rect', 0.3, 0.88, 0.7, 0.9, '#d89a7a')]
    blob(body, 0, 6.6, 0, 8.8, 8.6, 5.6, 'skin', decals={'north': musc})    # shirtless, lean muscular
    for sx in (1, -1):
        cb(body, sx * 2.1, 11.4, -2.9, 3.6, 2.4, 0.6, 'skin')               # pecs
    blob(body, 0, 5.2, 0, 9.2, 2.2, 6.0, 'pants', full=False)
    cb(body, 0, 6.4, 0, 9.6, 1.6, 6.2, 'leather', decals={'north': [('px', x, 0.5, '#c9a03a') for x in (0.1, 0.3, 0.7, 0.9)]})
    cb(body, 0, 6.2, -3.3, 2.2, 2.0, 0.6, 'gold')
    blob(body, -3.6, 4.4, -2.6, 2.4, 2.8, 1.6, 'leather', full=False)       # belt pouch
    cb(body, -3.6, 6.0, -3.5, 1.0, 0.6, 0.4, 'gold')
    for (x, y) in ((-1.0, 12.4), (0.8, 11.8), (-0.4, 10.6)):
        cb(body, x, y, -3.1, 0.6, 0.8, 0.4, 'beard_d')                       # chest hair
    cb(body, 0, 9.6, 3.0, 1.2, 12.6, 0.6, 'leather', rot=('z', 45))         # flask strap across the back
    fl = m.bone('flask', [-4.4, 15.6, 2.4], body)                            # purple Rage flask on the shoulder
    blob(fl, -4.4, 14.6, 2.6, 3.4, 3.6, 3.4, 'glass', decals={'south': [('rect', 0.2, 0.3, 0.8, 0.7, '#f0e0b0'), ('rect', 0.35, 0.4, 0.65, 0.6, '#8a3ad0')]})
    cb(fl, -4.4, 15.4, 0.8, 1.0, 1.4, 0.4, 'glass_l')
    cb(fl, -4.4, 18.2, 2.6, 1.4, 1.4, 1.4, 'glass')
    cb(fl, -4.4, 19.6, 2.6, 1.6, 1.0, 1.6, 'cork')
    head = m.bone('head', [0, 15, 0], body)
    face = eye(0.08, 0.28, 0.44, 0.74, '#8a3ad0', look=0.4) + eye(0.6, 0.4, 0.86, 0.66, '#8a3ad0', look=-0.6)
    blob(head, 0, 15.4, -0.3, 9.2, 7.8, 8.2, 'skin', decals={'north': face})
    blob(head, 0, 16.0, -5.6, 2.8, 2.6, 2.2, 'nose', full=False)              # scarlet nose
    cb(head, -2.6, 20.4, -4.7, 3.6, 1.2, 1.0, 'beard', rot=('z', -22.5))     # crazy brows
    cb(head, 2.6, 19.4, -4.7, 3.2, 1.0, 1.0, 'beard', rot=('z', 22.5))
    for sx in (1, -1):
        cb(head, sx * 4.8, 15.6, 0.0, 0.8, 2.0, 1.6, 'skin_d')
    blob(head, 0, 10.8, -3.0, 10.2, 5.8, 4.8, 'beard')                       # big ginger beard (layered)
    blob(head, 0, 8.4, -3.3, 8.6, 3.0, 3.8, 'beard_d', full=False)
    cb(head, 0, 6.8, -3.4, 5.4, 2.0, 2.6, 'beard')
    for sx in (1, -1):
        cb(head, sx * 4.6, 12.2, -0.6, 1.4, 6.2, 6.0, 'beard_d')            # sideburns
        cb(head, sx * 2.0, 14.6, -5.5, 3.8, 1.6, 1.6, 'beard_l', rot=('z', -sx * 22.5))   # moustache
    cb(head, 0, 11.2, -5.6, 5.6, 3.6, 0.6, 'mouth')                         # wide open mouth
    cb(head, 0, 14.0, -5.8, 4.8, 0.8, 0.6, 'tooth')
    blob(head, 0, 10.0, -6.2, 2.8, 2.6, 1.4, 'tongue', full=False)          # tongue out
    cb(head, 1.9, 8.6, -5.9, 0.9, 2.6, 0.9, 'glass')                        # purple drool
    cb(head, 1.9, 7.6, -5.9, 1.2, 1.1, 1.2, 'glass')
    cb(head, 0, 14.6, 4.1, 9.0, 4.4, 1.4, 'beard')                          # ginger hair at the back
    for (x, y, z) in ((-3.4, 8.0, -3.0), (3.2, 7.8, -3.2), (-1.2, 6.0, -3.2), (1.6, 6.2, -3.0), (-4.6, 10.0, -1.8), (4.6, 9.8, -1.8)):
        blob(head, x, y, z, 2.2, 2.4, 2.2, 'beard_l' if x > 0 else 'beard_d', full=False)   # beard curls
    for (x, z) in ((-3.0, -3.6), (3.4, -3.0), (-4.6, 2.0)):
        cb(head, x, 19.6, z, 1.6, 1.6, 1.4, 'beard', rot=('z', 22.5))        # hair tufts under the hat
    hat = m.bone('tc_hat', [0, 22, 0], head)                                 # team-coloured fur ushanka
    blob(hat, 0, 21.4, 0.0, 10.6, 5.0, 10.0, 'fur')
    blob(hat, 0, 25.8, 0.2, 7.6, 1.6, 7.2, 'fur', full=False)
    blob(hat, 0, 20.4, -4.6, 11.4, 3.2, 2.4, 'fur_d', full=False)
    blob(hat, 0, 19.8, 4.4, 10.8, 3.2, 2.0, 'fur_d', full=False)
    for sx in (1, -1):
        blob(hat, sx * 5.5, 13.4, 0.6, 1.9, 8.2, 6.8, 'fur_d', full=False)  # ear flaps
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5.6, 13, 0], body)
        blob(a, sx * 6.0, 9.6, 0, 3.6, 3.6, 3.7, 'skin', full=False)
        cb(a, sx * 6.0, 6.6, 0, 3.2, 3.2, 3.4, 'skin')
        cb(a, sx * 6.0, 5.4, 0, 3.7, 1.6, 3.9, 'leather')                    # wristband
        fist(a, sx * 6.0, 2.2, -0.2, 3.6, 'skin', side=sx, knuckle='skin_d')
    H = (6.0, 3.8, -0.2)
    axe = m.bone('axe', list(H), m.by_name('arm_r'))
    hx, hy, hz = H
    R = dict(rot=('z', -22.5), rot_origin=list(H))                          # felling axe tilted outward
    cb(axe, hx, hy - 4, hz, 1.5, 18, 1.5, 'wood', **R)
    cb(axe, hx, hy + 2.8, hz, 1.9, 1.2, 1.9, 'leather', **R)
    cb(axe, hx, hy - 4.6, hz, 1.9, 1.2, 1.9, 'iron', **R)
    cb(axe, hx, hy + 10.8, hz + 0.4, 2.2, 3.8, 4.0, 'iron', **R)
    cb(axe, hx, hy + 10.4, hz - 3.4, 1.3, 5.6, 3.4, 'steel', **R)
    cb(axe, hx, hy + 9.8, hz - 5.4, 1.2, 6.8, 1.4, 'steel', **R)
    cb(axe, hx, hy + 9.6, hz - 6.4, 1.0, 7.2, 0.7, 'edge', **R)
    cb(axe, hx, hy + 11.2, hz + 2.8, 1.8, 2.6, 1.4, 'iron', **R)
    m.hitbox(0.9, 1.8)

    m.anim('idle', 1.6, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 0.8)},
        'head': {'rotation': loop([[0, 14, 4], [0, 0, 0], [0, -14, -4], [0, 0, 0]], 1.6)},
        'arm_r': {'rotation': loop([[-10, 0, 3], [-16, 0, 4]], 0.8)}, 'arm_l': {'rotation': loop([[0, 0, -3], [6, 0, -5]], 0.8)}})
    w = biped_walk(0.45, leg=42, arm=40, bob=1.1, lean=14)
    w['arm_r'] = {'rotation': loop([[-30, 0, 4], [-10, 0, 4]], 0.45)}
    w['head'] = {'rotation': [(0, [-10, 0, 0]), (0.45, [-10, 0, 0])]}
    m.anim('walk', 0.45, 'loop', w)
    m.anim('attack', 0.5, 'once', {
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.08, [-150, 0, 6]), (0.17, [-40, 0, -6]), (0.25, [-150, 0, 6]), (0.34, [-40, 0, -6]), (0.5, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.08, [135, 0, 0]), (0.34, [135, 0, 0]), (0.5, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.08, [-8, 0, 0]), (0.17, [14, 0, 0]), (0.25, [-6, 0, 0]), (0.34, [14, 0, 0]), (0.5, [0, 0, 0])]},
        'head': {'rotation': [(0, [0, 0, 0]), (0.17, [-8, 0, 0]), (0.34, [-8, 0, 0]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Royal Hog
def royal_hog():
    """CR-style Royal Hog: small pink pig with a golden crown helmet, gold chest plate, team-coloured royal saddle
    blanket with gold trim, no rider. walk = fast gallop, attack = headbutt."""
    m = Model('clash_royal_hog', density=2.0)
    m.mats_({
        'pink': ('#c98e5a', 'fur'), 'pink_d': ('#a8703e', 'fur'), 'belly': ('#e0b080', 'fur'), 'mane': ('#4a3020', 'hair'),
        'snout': ('#e8a08a', 'skin'), 'snout_d': ('#d0807a', 'skin'), 'hoof': ('#3a2820', 'plain'),
        'steel': ('#a6aeb8', 'metal', {'rivets': True}), 'steel_l': ('#c6ccd4', 'metal'), 'steel_d': ('#6c737d', 'metal'),
        'cloth': ('#efefef', 'cloth'), 'tusk': ('#f8f2de', 'bone'), 'rivet': ('#dfe4ea', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    for name, x, z in (('fl_leg', -2.8, -3.6), ('fr_leg', 2.8, -3.6), ('bl_leg', -2.8, 4.4), ('br_leg', 2.8, 4.4)):
        lg = m.bone(name, [x, 4.4, z], root)
        blob(lg, x, 1.2, z, 3.2, 3.8, 3.4, 'pink', full=False)
        cb(lg, x, 0, z - 0.2, 3.4, 1.4, 3.6, 'hoof', decals={'north': [('rect', 0.45, 0, 0.55, 1, '#120c08')]})
        for dx in (-0.9, 0.9):
            cb(lg, x + dx, 0, z - 2.2, 1.4, 1.0, 0.8, 'hoof')                  # split toes
        cb(lg, x, 4.4, z, 3.6, 1.2, 3.8, 'pink_d')
    body = m.bone('body', [0, 7, 0], root)
    blob(body, 0, 3.4, 0.6, 10.4, 8.8, 12.6, 'pink', r=2.0)
    blob(body, 0, 3.0, 0.2, 8.4, 2.6, 10.0, 'belly', full=False)
    for sx in (1, -1):
        blob(body, sx * 3.8, 4.6, 4.0, 3.4, 6.4, 5.0, 'pink_d', full=False)  # haunches
    for k, z in enumerate((-5.6, -3.0, -0.4, 2.2, 4.8)):                    # dark mane ridge
        cb(body, 0, 11.4, z, 2.4 - k * 0.2, 2.4 - k * 0.3, 2.2, 'mane', rot=('x', 22.5))
    for sx in (1, -1):
        for (y, z) in ((8.6, -4.0), (9.4, -0.6), (8.8, 2.8), (6.6, 5.4)):
            cb(body, sx * 5.0, y, z, 1.0, 1.8, 1.6, 'pink_d', rot=('x', 22.5))   # fur tufts on the flanks
        cb(body, sx * 4.0, 1.4, -5.6, 2.4, 2.0, 2.4, 'belly')
    tail = m.bone('tail', [0, 10, 6.6], body)
    cb(tail, 0, 9.2, 7.4, 1.4, 1.4, 1.8, 'pink_d')
    cb(tail, 0, 10.4, 8.2, 1.2, 1.6, 1.2, 'pink_d')
    cb(tail, 0, 11.6, 7.6, 1.0, 1.0, 1.4, 'pink_d')
    head = m.bone('head', [0, 8.5, -5.5], body)
    blob(head, 0, 3.4, -8.6, 9.8, 8.8, 8.0, 'pink', r=1.8)
    for sx in (1, -1):
        blob(head, sx * 3.8, 3.2, -10.2, 2.6, 4.2, 4.0, 'pink', full=False)  # cheeks
    blob(head, 0, 3.6, -13.6, 6.2, 4.8, 3.0, 'snout', full=False)
    cb(head, 0, 4.2, -15.3, 5.0, 3.6, 0.6, 'snout_d', decals={'north': [('rect', 0.18, 0.3, 0.38, 0.7, '#6a2a32'), ('rect', 0.62, 0.3, 0.82, 0.7, '#6a2a32')]})
    cb(head, 0, 3.2, -14.4, 4.4, 0.5, 1.4, 'snout_d')                        # mouth line
    for sx in (1, -1):                                                       # big curved tusks
        cb(head, sx * 3.4, 3.0, -13.8, 1.5, 2.2, 1.5, 'tusk')
        cb(head, sx * 3.7, 4.8, -14.6, 1.3, 2.0, 1.3, 'tusk', rot=('x', -22.5))
        cb(head, sx * 3.5, 6.4, -15.2, 1.0, 1.6, 1.0, 'tusk', rot=('x', -45))
        cb(head, sx * 5.4, 8.6, -7.0, 1.0, 3.0, 2.8, 'pink_d', rot=('z', -sx * 22.5))   # ears
    slits = [('rect', x, 0.3, x + 0.07, 0.85, '#15171a') for x in (0.14, 0.28, 0.65, 0.79)] + [('rect', 0.44, 0.0, 0.56, 1.0, '#8a929c')]
    blob(head, 0, 8.4, -8.8, 10.8, 6.8, 9.0, 'steel', r=1.8)                  # knight helmet dome
    blob(head, 0, 7.8, -13.0, 9.6, 4.4, 1.4, 'steel_l', full=False, decals={'north': slits})   # visor with slits
    cb(head, 0, 8.2, -8.8, 11.2, 1.2, 9.4, 'steel_d')
    for x in (-4.4, -2.2, 2.2, 4.4):
        cb(head, x, 8.4, -13.6, 0.8, 0.8, 0.5, 'rivet')
    cb(head, 0, 15.0, -8.8, 1.4, 1.2, 9.4, 'steel_d')                        # crest ridge
    for sx in (1, -1):
        for z in (-11.0, -8.0, -5.0):
            cb(head, sx * 5.5, 9.6, z, 0.5, 0.8, 0.8, 'rivet')
        blob(head, sx * 5.4, 9.2, -12.0, 1.4, 3.2, 2.4, 'steel_d', full=False)   # cheek guards
    pl = m.bone('tc_plume', [0, 16, -8], head)                               # team-coloured feather plume
    cb(pl, 0, 15.8, -7.8, 2.6, 2.6, 3.6, 'cloth')
    cb(pl, 0, 16.6, -4.8, 2.2, 2.2, 3.4, 'cloth', rot=('x', 22.5))
    cb(pl, 0, 15.8, -2.0, 1.8, 2.0, 2.8, 'cloth', rot=('x', 45))
    cb(pl, 0, 14.6, 0.0, 1.2, 1.6, 2.0, 'cloth', rot=('x', 45))
    m.hitbox(1.0, 1.15)

    m.anim('idle', 1.6, 'loop', {
        'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 0.8)},
        'head': {'rotation': loop([[0, 0, 0], [6, 6, 0], [0, 0, 0], [6, -6, 0]], 1.6)},
        'tail': {'rotation': loop([[0, 25, 0], [0, -25, 0]], 0.4)}})
    L = 0.4
    def leg(a, b, ph):
        k = [a, (a + b) / 2, b, (a + b) / 2]
        n = len(k); sft = int(round(ph * n)) % n
        k = k[sft:] + k[:sft]
        return {'rotation': loop([[v, 0, 0] for v in k], L)}
    m.anim('walk', L, 'loop', {
        'fl_leg': leg(-40, 30, 0), 'fr_leg': leg(-40, 30, 0.25), 'bl_leg': leg(35, -32, 0.5), 'br_leg': leg(35, -32, 0.75),
        'body': {'rotation': loop([[-6, 0, 0], [0, 0, 0], [6, 0, 0], [0, 0, 0]], L), 'position': loop([[0, 1.6, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], L)},
        'head': {'rotation': loop([[8, 0, 0], [0, 0, 0], [-6, 0, 0], [0, 0, 0]], L)},
        'tail': {'rotation': loop([[0, 30, 0], [0, -30, 0]], L / 2)}})
    m.anim('attack', 0.5, 'once', {
        'head': {'rotation': [(0, [0, 0, 0]), (0.15, [-28, 0, 0]), (0.25, [24, 0, 0]), (0.35, [18, 0, 0]), (0.5, [0, 0, 0])]},
        'body': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.5, 2.5]), (0.25, [0, -0.5, -4]), (0.35, [0, 0, -3]), (0.5, [0, 0, 0])],
                 'rotation': [(0, [0, 0, 0]), (0.15, [-8, 0, 0]), (0.25, [8, 0, 0]), (0.5, [0, 0, 0])]},
        'bl_leg': {'rotation': [(0, [0, 0, 0]), (0.25, [30, 0, 0]), (0.5, [0, 0, 0])]},
        'br_leg': {'rotation': [(0, [0, 0, 0]), (0.25, [30, 0, 0]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== previews
def preview(doc, out_png, tools, frames):
    from bbrender import render, sample
    from PIL import Image
    S = 300
    tiles = []
    tiles.append(('idle front', render(doc, S, cam=(0.6, 0.5, -1.0), tint=(225, 55, 55))))
    tiles.append(('back', render(doc, S, cam=(-0.8, 0.45, 1.0), tint=(55, 90, 245))))
    tiles.append(('side', render(doc, S, cam=(1.0, 0.2, -0.05), tint=(225, 55, 55))))
    far = render(doc, 400, cam=(0.6, 0.9, -1.0), tint=(55, 90, 245), margin=0.3)
    far = far.resize((40, 40), Image.LANCZOS).resize((S, S), Image.NEAREST)
    tiles.append(('~15 blocks', far))
    keep = CLOSEUP.get(doc['name'])
    if keep:                                  # zoomed close-up of the hand + weapon only (grip check)
        import copy
        from bbrender import element_parents
        par = element_parents(doc)
        dd = copy.deepcopy(doc)
        dd['elements'] = [e for e in doc['elements'] if any(b[2] in keep for b in par.get(e['uuid'], []))]
        tiles.append(('close-up grip idle (side)', render(dd, S, cam=(1.0, 0.1, 0.0), pose=sample(doc, 'idle', 0.0))))
        tiles.append(('close-up grip idle (front)', render(dd, S, cam=(0.3, 0.15, -1.0), pose=sample(doc, 'idle', 0.0))))
    for (an, t) in frames:
        try:
            pose = sample(doc, an, t)
        except StopIteration:
            continue
        tiles.append(('%s %.2f' % (an, t), render(doc, S, cam=(0.75, 0.4, -1.0), tint=(225, 55, 55), pose=pose)))
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * S, rows * (S + 16)), (255, 255, 255, 255))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for i, (lab, im) in enumerate(tiles):
        x, y = (i % cols) * S, (i // cols) * (S + 16)
        sheet.paste(im, (x, y + 16))
        dr.text((x + 4, y + 2), lab, fill=(0, 0, 0, 255))
    sheet.save(out_png)


CLOSEUP = {'clash_pekka': ('arm_r',)}
FRAMES = {
    'clash_mega_knight': [('attack', 0.36), ('attack', 0.5), ('jump', 0.15), ('jump', 0.45), ('jump', 0.64), ('walk', 0.25), ('walk', 0.75), ('death', 0.9)],
    'clash_giant_skeleton': [('attack', 0.4), ('attack', 0.55), ('walk', 0.27), ('walk', 0.82), ('death', 0.9), ('idle', 0.6), ('hit', 0.08), ('deploy', 0.35)],
    'clash_valkyrie': [('attack', 0.12), ('attack', 0.3), ('attack', 0.45), ('walk', 0.17), ('walk', 0.52), ('death', 0.9), ('idle', 1.0), ('hit', 0.08)],
    'clash_executioner': [('attack', 0.18), ('attack', 0.3), ('attack', 0.46), ('walk', 0.2), ('walk', 0.6), ('death', 0.9), ('idle', 1.1), ('hit', 0.08)],
    'clash_lumberjack': [('attack', 0.08), ('attack', 0.17), ('walk', 0.11), ('walk', 0.34), ('death', 0.9), ('idle', 0.4), ('hit', 0.08), ('deploy', 0.35)],
    'clash_royal_hog': [('attack', 0.15), ('attack', 0.25), ('walk', 0.0), ('walk', 0.2), ('death', 0.9), ('idle', 0.4), ('hit', 0.08), ('deploy', 0.35)],
    'clash_pekka': [('attack', 0.3), ('attack', 0.45), ('attack', 0.6), ('attack', 0.8), ('walk', 0.3), ('walk', 0.9), ('death', 0.9), ('deploy', 0.35), ('hit', 0.08), ('idle', 1.2)],
    'clash_dark_prince': [('attack', 0.3), ('attack', 0.46), ('attack', 0.6), ('walk', 0.0), ('walk', 0.25), ('walk', 0.375), ('death', 0.9), ('idle', 1.0)],
    'clash_sparky': [('charge', 0.5), ('charge', 1.0), ('attack', 0.1), ('attack', 0.3), ('walk', 0.1), ('walk', 0.3), ('death', 0.9), ('idle', 0.5)],
    'clash_battle_ram': [('attack', 0.12), ('attack', 0.2), ('walk', 0.1), ('walk', 0.3), ('death', 0.9), ('idle', 1.0), ('deploy', 0.35), ('hit', 0.08)],
    'clash_cannon_cart': [('attack', 0.12), ('attack', 0.28), ('walk', 0.1), ('walk', 0.25), ('death', 0.9), ('idle', 1.0), ('hit', 0.08), ('deploy', 0.35)],
    'clash_zappies': [('attack', 0.15), ('attack', 0.28), ('attack', 0.31), ('walk', 0.1), ('walk', 0.3), ('death', 0.9), ('idle', 0.16), ('hit', 0.08)],
    'clash_cannon_cart_broken': [('attack', 0.12), ('attack', 0.28), ('deploy', 0.1), ('deploy', 0.32), ('death', 0.9), ('idle', 1.2), ('hit', 0.08), ('idle', 0.6)],
}

if __name__ == '__main__':
    tools = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    rest = sys.argv[3:]
    do_prev = '--no-preview' not in rest
    only = [a for a in rest if not a.startswith('--')]
    os.makedirs(out, exist_ok=True)
    for fn in (pekka, dark_prince, sparky, battle_ram, cannon_cart, cannon_cart_broken, zappies,
               mega_knight, giant_skeleton, valkyrie, executioner, lumberjack, royal_hog):
        if only and fn.__name__ not in only:
            continue
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        doc = m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad,
              'anims', [(a['name'], a['length'], a['loop']) for a in m.anims])
        for b in m.bones:
            if 'muzzle' in b.name:
                print('   muzzle bone', b.name, 'origin', b.origin)
        if do_prev:
            preview(doc, os.path.join(out, 'preview_' + m.name + '.png'), tools, FRAMES.get(m.name, []))
