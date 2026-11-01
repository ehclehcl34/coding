"""m3 models: elixir golem / elixir golemite / elixir blob / goblin cage / x-bow / bomb tower (bbgen2, BetterModel).
Units: px (16 = 1 block). Front = north (-Z). Origin = feet centre.
Troops: idle / walk / attack / spawn(->deploy) / hit / death.  Buildings: idle / attack / spawn / hit / death.
Turrets (x_bow, bomb_tower): root -> base (base_*) + top (top_*), top pivot at x=0, z=0."""
import sys, os, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """centre (x, z) / bottom (y) box"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def S(v):
    return [v, v, v]


def common_tail(m, root='root', hit_bone='body', death=None, spawn=None):
    m.anim('spawn', 0.5, 'once', spawn or {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                                  'scale': [(0, S(0.3)), (0.35, S(1.08)), (0.5, S(1))]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death or {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                                  'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})


def building_hit(m, bone='root', amp=1.0):
    m.anim('hit', 0.3, 'once', {bone: {'position': [(0, [0, 0, 0]), (0.05, [amp, 0, 0.4 * amp]), (0.1, [-amp, 0, -0.3 * amp]),
                                                    (0.16, [0.6 * amp, 0, 0]), (0.22, [-0.3 * amp, 0, 0]), (0.3, [0, 0, 0])]}})


# --------------------------------------------------------------- shared elixir palette / decals
ELIXIR_MATS = {
    'elx': ('#cf38d2', 'gem'), 'elx_l': ('#ee74ee', 'gem'), 'elx_d': ('#7e1f8e', 'gem'), 'elx_dd': ('#4a0f58', 'gem'),
    'glow': ('#ff8cf4', 'glow'), 'core': ('#ff6ae6', 'glow'), 'eye': ('#ff4fd2', 'glow'),
    'gold': ('#e2b03a', 'metal', {'rivets': True}), 'gold_d': ('#a77a22', 'metal'),
    'band': ('#efefef', 'cloth'), 'white': ('#fbf6ff', 'plain'), 'pupil': ('#2a0838', 'plain'),
}
GLOSS = [('rect', 0.1, 0.08, 0.2, 0.5, '#ffc8ff'), ('rect', 0.2, 0.08, 0.34, 0.16, '#ffc8ff'), ('px', 0.14, 0.12, '#ffffff'),
         ('rect', 0.55, 0.62, 0.9, 0.68, '#93279e'), ('rect', 0.48, 0.7, 0.6, 0.76, '#93279e'),
         ('rect', 0.7, 0.3, 0.76, 0.36, '#ff9cf7'), ('px', 0.38, 0.8, '#ffb6fa'), ('px', 0.82, 0.18, '#ffb6fa')]
GLOSS2 = [('rect', 0.12, 0.12, 0.22, 0.4, '#ffc8ff'), ('px', 0.16, 0.16, '#ffffff'), ('rect', 0.5, 0.6, 0.85, 0.66, '#93279e'),
          ('px', 0.7, 0.3, '#ffb6fa')]


# =================================================================== elixir golem / golemite
def elixir_golem(name='clash_elixir_golem', s=1.0, dens=1.5, detail=True, hb=(2.0, 2.8)):
    """Pink/purple elixir crystal golem in a gold frame. Glowing chest core, team bands on waist and arms."""
    m = Model(name, density=dens)
    m.mats_(ELIXIR_MATS)

    def c(bone, x, y, z, w, h, d, mat, **kw):
        if 'rot_origin' in kw:
            kw['rot_origin'] = [v * s for v in kw['rot_origin']]
        return cb(bone, x * s, y * s, z * s, w * s, h * s, d * s, mat, **kw)

    def B(n, o, p):
        return m.bone(n, [v * s for v in o], p)

    root = B('root', [0, 0, 0], None)
    # ---- legs
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = B('leg_' + side, [sx * 5.5, 11, 0], root)
        c(lg, sx * 5.5, 3, 0.5, 8, 9.5, 9, 'elx', decals={'north': GLOSS2, 'east': GLOSS2, 'west': GLOSS2})
        c(lg, sx * 5.5, 0, -0.3, 9.6, 4, 10.6, 'elx_d', decals={'north': [('rect', 0.15, 0.2, 0.3, 0.45, '#c46ad0')]})
        c(lg, sx * 5.5, 0, -5.9, 9.8, 2.4, 1.0, 'gold')                       # gold toe cap
    body = B('body', [0, 12, 0], root)
    # ---- waist / chest
    c(body, 0, 10, 0.5, 18, 7, 13, 'elx_d', decals={'north': GLOSS2})
    tcb = B('tc_band', [0, 15, 0], body)
    c(tcb, 0, 13.5, 0.5, 19.2, 3.4, 14.2, 'band', decals={'north': [('rect', 0.44, 0.0, 0.56, 1.0, '#9a9a9a')]})
    c(body, 0, 13.2, -6.9, 3.4, 4, 1.2, 'gold')                                   # belt buckle
    c(body, 0, 16.5, 0, 22, 15, 15, 'elx', decals={'north': GLOSS, 'east': GLOSS, 'west': GLOSS, 'south': GLOSS})
    c(body, 0, 31, 0.5, 18, 3, 13, 'elx_l', decals={'north': GLOSS2})
    c(body, 0, 32.4, -0.5, 12.5, 2.2, 10, 'gold')                                 # gold collar
    # front gold frame + glowing core
    c(body, 0, 19.5, -8.1, 11, 11, 1.4, 'gold', decals={'north': [('rect', 0.14, 0.14, 0.86, 0.86, '#5a1466')]})
    core = B('core', [0, 25, -8.6], body)
    c(core, 0, 20.8, -8.75, 7.6, 8.4, 1.2, 'core', decals={'north': [('rect', 0.44, 0.06, 0.56, 0.2, '#ffc4f6'), ('rect', 0.36, 0.2, 0.64, 0.36, '#ffc4f6'),
                                                                     ('rect', 0.24, 0.36, 0.76, 0.8, '#ffc4f6'), ('rect', 0.32, 0.8, 0.68, 0.9, '#ffc4f6'),
                                                                     ('rect', 0.32, 0.42, 0.42, 0.62, '#ffffff'), ('rect', 0.5, 0.6, 0.68, 0.76, '#ff8cf0')]})
    for sx in (1, -1):                                                             # gold straps front / back
        c(body, sx * 7.6, 16.5, -7.9, 2, 15, 0.9, 'gold_d')
        c(body, sx * 7.6, 16.5, 7.9, 2, 15, 0.9, 'gold_d')
        c(body, sx * 7.6, 31.2, 0, 2, 0.9, 16.6, 'gold_d')
    # crystal shards on shoulders / back
    shards = [(-6, 30, 5, 3.6, 7), (-1, 31, 6, 4, 9), (4.5, 30, 5, 3.4, 6.5)]
    if detail:
        shards += [(8, 28, 6, 3, 5), (-9, 27, 6.5, 2.8, 4.5), (1.5, 22, 8, 3, 4)]
    for (x, y, z, w, h) in shards:
        c(body, x, y, z, w, h, w, 'elx_l', rot=('x', 22.5), decals={'north': GLOSS2})
    if detail:                                                                     # drips under the belly
        for (x, z, h) in ((-5, -5, 1.6), (3, -6, 2.4), (6, -2, 1.2), (-2, 5, 1.4)):
            c(body, x, 10 - h, z, 1.6, h, 1.6, 'glow')
    # ---- head (sunk into the shoulders)
    head = B('head', [0, 34, -2], body)
    c(head, 0, 33, -4.6, 12, 8.6, 10, 'elx', decals={'north': [('rect', 0.06, 0.3, 0.94, 0.66, '#3a0846'),
                                                             ('rect', 0.3, 0.8, 0.7, 0.88, '#5a1466'),
                                                             ('rect', 0.12, 0.06, 0.3, 0.16, '#ffc8ff')]})
    for sx in (1, -1):
        c(head, sx * 2.8, 36.0, -9.9, 3.6, 2.4, 0.8, 'eye', decals={'north': [('rect', 0.25, 0.25, 0.6, 0.75, '#ffffff'),
                                                                            ('rect', 0.0 if sx > 0 else 0.7, 0.0, 0.3 if sx > 0 else 1.0, 0.3, '#ff3cc8')]})
        c(head, sx * 2.8, 38.7, -9.8, 4, 0.9, 0.7, 'elx_dd', rot=('z', sx * 22.5))      # angry brow
    c(head, 0, 39.9, -4.6, 12.6, 1.6, 10.6, 'gold', decals={'north': [('px', 0.5, 0.5, '#fff0a0')]})  # gold head band
    c(head, 0, 41.4, -4, 3.2, 3.4, 3.2, 'elx_l', rot=('y', 45))                  # crown crystal
    if detail:
        for sx in (1, -1):
            c(head, sx * 3.8, 41.4, -3.5, 2, 2.2, 2, 'elx_l', rot=('z', -sx * 22.5))
    # ---- arms
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = B('arm_' + side, [sx * 12, 29, 0], body)
        c(arm, sx * 14, 24.5, 0, 8, 7, 9, 'elx', decals={'north': GLOSS2})
        c(arm, sx * 14.3, 30.4, 0, 9.4, 2.2, 10.4, 'gold')                        # pauldron rim
        c(arm, sx * 14.3, 31.4, 0, 7.6, 2.2, 8.6, 'elx_l')
        if detail:
            c(arm, sx * 15, 33, 1, 3, 4.5, 3, 'elx_l', rot=('z', -sx * 22.5))      # shoulder crystal
        c(arm, sx * 14, 16.5, 0, 6.5, 8.5, 7.5, 'elx_d')
        tca = B('tc_arm_' + side, [sx * 14, 20, 0], arm)
        c(tca, sx * 14, 19, 0, 7.3, 2.6, 8.3, 'band')
        c(arm, sx * 14.5, 5.5, -0.5, 9.4, 11, 10.5, 'elx_l', decals={'north': GLOSS, 'east': GLOSS2, 'west': GLOSS2})  # fist
        c(arm, sx * 14.5, 14.6, -0.5, 10.2, 2.6, 11.3, 'gold')                     # bracer
        c(arm, sx * 14.5, 7, -6.1, 7.6, 3, 1.0, 'gold_d')                          # knuckle plate
        c(arm, sx * 14.5, 4.3, -1.5, 1.6, 1.2, 1.6, 'glow')                        # drip
    m.hitbox(*hb)

    # ---- animations (positions scale with s)
    def P(v):
        return [v[0] * s, v[1] * s, v[2] * s]
    idle = {'body': {'position': loop([P([0, 0, 0]), P([0, -0.6, 0])], 3.0), 'rotation': loop([[0, 0, 1], [0, 0, -1]], 3.0)},
            'arm_r': {'rotation': loop([[0, 0, 2], [4, 0, -1]], 3.0)}, 'arm_l': {'rotation': loop([[0, 0, -2], [4, 0, 1]], 3.0)},
            'head': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 3.0)},
            'core': {'scale': loop([[1, 1, 1], [1.15, 1.12, 1], [1, 1, 1], [1.15, 1.12, 1]], 3.0)}}
    m.anim('idle', 3.0, 'loop', idle)
    L = 1.6
    walk = {'leg_r': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], L)},
            'arm_r': {'rotation': loop([[-15, 0, 3], [15, 0, 3]], L)}, 'arm_l': {'rotation': loop([[15, 0, -3], [-15, 0, -3]], L)},
            'body': {'rotation': loop([[5, 0, 4], [5, 0, -4]], L),
                     'position': loop([P([0, -0.8, 0]), P([0, 0.6, 0]), P([0, -0.8, 0]), P([0, 0.6, 0])], L)},
            'head': {'rotation': loop([[0, 0, -3], [0, 0, 3]], L)},
            'core': {'scale': loop([[1, 1, 1], [1.12, 1.1, 1]], L / 2)}}
    m.anim('walk', L, 'loop', walk)
    att = {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.42, [-155, 0, -8]), (0.58, [28, 0, 4]), (0.72, [22, 0, 4]), (1.0, [0, 0, 0])]},
           'arm_l': {'rotation': [(0, [0, 0, 0]), (0.42, [-155, 0, 8]), (0.58, [28, 0, -4]), (0.72, [22, 0, -4]), (1.0, [0, 0, 0])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.42, [-12, 0, 0]), (0.58, [16, 0, 0]), (0.72, [13, 0, 0]), (1.0, [0, 0, 0])],
                    'position': [(0, P([0, 0, 0])), (0.42, P([0, 1.2, 1])), (0.58, P([0, -2.2, -2])), (0.75, P([0, -1.6, -1.5])), (1.0, P([0, 0, 0]))]},
           'head': {'rotation': [(0, [0, 0, 0]), (0.42, [-12, 0, 0]), (0.58, [8, 0, 0]), (1.0, [0, 0, 0])]},
           'core': {'scale': [(0, S(1)), (0.42, [1.3, 1.25, 1]), (0.6, S(0.9)), (1.0, S(1))]},
           'leg_r': {'rotation': [(0, [0, 0, 0]), (0.58, [-8, 0, 0]), (1.0, [0, 0, 0])]},
           'leg_l': {'rotation': [(0, [0, 0, 0]), (0.58, [-8, 0, 0]), (1.0, [0, 0, 0])]}}
    m.anim('attack', 1.0, 'once', att)
    death = {'body': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 5]), (0.24, [0, 0, -5]), (0.36, [0, 0, 3]), (0.7, [14, 0, 0])],
                      'position': [(0, P([0, 0, 0])), (0.36, P([0, 1, 0])), (0.7, P([0, -6, 0]))]},
             'arm_r': {'rotation': [(0, [0, 0, 0]), (0.36, [0, 0, -10]), (0.7, [0, 0, -55])]},
             'arm_l': {'rotation': [(0, [0, 0, 0]), (0.36, [0, 0, 10]), (0.7, [0, 0, 55])]},
             'core': {'scale': [(0, S(1)), (0.36, S(1.6)), (0.5, S(0.4))]},
             'root': {'scale': [(0, S(1)), (0.36, [1.05, 1.05, 1.05]), (0.75, [1.25, 0.35, 1.25]), (1.0, [1.45, 0.08, 1.45])]}}
    common_tail(m, death=death)
    m.anims[-1]['length'] = 1.0
    return m


def elixir_golemite():
    return elixir_golem('clash_elixir_golemite', s=0.56, dens=2.2, detail=False, hb=(1.3, 1.6))


# =================================================================== elixir blob
def elixir_blob():
    m = Model('clash_elixir_blob', density=3.0)
    m.mats_(ELIXIR_MATS)
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 0, 0], root)
    face = [('rect', 0.36, 0.55, 0.64, 0.62, '#4a0f58'), ('rect', 0.42, 0.62, 0.58, 0.68, '#4a0f58'), ('rect', 0.44, 0.62, 0.56, 0.66, '#ff6ab0')]
    cb(body, 0, 0, 0, 10, 4.6, 10, 'elx', decals={'north': face, 'east': GLOSS2, 'west': GLOSS2, 'south': GLOSS2})
    cb(body, 0, 4.6, 0, 8.6, 2.8, 8.6, 'elx', decals={'east': GLOSS2, 'west': GLOSS2})
    cb(body, 0, 7.4, 0.2, 6.6, 1.6, 6.6, 'elx_l', decals={'north': [('rect', 0.15, 0.2, 0.3, 0.6, '#ffd0ff')]})
    cb(body, 0, 9.0, 0.4, 4.4, 1.4, 4.4, 'elx_l')
    cb(body, 0, 10.4, 0.7, 2.6, 1.2, 2.6, 'elx_l')
    cb(body, 0, 11.4, 1.4, 1.4, 1.4, 1.4, 'elx_l', rot=('x', -22.5))               # curled tip
    cb(body, 0, -0.01, 0, 9.2, 0.6, 9.2, 'elx_d')                                 # darker underside rim
    for sx in (1, -1):                                                             # big eyes
        cb(body, sx * 2.1, 3.0, -4.75, 2.8, 3.2, 0.6, 'white', decals={'north': [('rect', 0.1, 0.0, 0.9, 0.08, '#d9b8e6')]})
        cb(body, sx * 2.0, 3.25, -5.15, 1.6, 2.0, 0.4, 'pupil', decals={'north': [('rect', 0.0, 0.0, 0.4, 0.35, '#ffffff')]})
        cb(body, sx * 4.4, 1.2, -4.0, 1.2, 1.2, 0.4, 'glow')                      # blush
    tc = m.bone('tc_ribbon', [0, 6.6, 0], body)
    cb(tc, 0, 6.0, 0, 8.9, 1.3, 8.9, 'band')
    cb(tc, 2.6, 6.6, -4.5, 1.3, 1.3, 0.8, 'band')                                 # bow knot
    cb(tc, 1.4, 6.7, -4.6, 1.8, 1.8, 0.6, 'band', rot=('z', 22.5))
    cb(tc, 3.9, 6.7, -4.6, 1.8, 1.8, 0.6, 'band', rot=('z', -22.5))
    cb(tc, 2.3, 4.8, -4.55, 0.7, 1.6, 0.4, 'band')                                # tails
    cb(tc, 3.1, 4.9, -4.55, 0.7, 1.5, 0.4, 'band')
    m.hitbox(0.7, 0.7)
    m.anim('idle', 1.2, 'loop', {'body': {'scale': loop([[1, 1, 1], [1.07, 0.93, 1.07]], 1.2)},
                                 'tc_ribbon': {'rotation': loop([[0, 0, 0], [0, 0, 3]], 1.2)}})
    walk = {'body': {'position': [(0, [0, 0, 0]), (0.1, [0, 1.2, 0]), (0.25, [0, 4.2, 0]), (0.4, [0, 1.2, 0]), (0.5, [0, 0, 0])],
                     'scale': [(0, [1.22, 0.76, 1.22]), (0.1, [0.9, 1.16, 0.9]), (0.25, [1, 1.04, 1]), (0.4, [0.94, 1.1, 0.94]), (0.5, [1.22, 0.76, 1.22])],
                     'rotation': [(0, [0, 0, 0]), (0.1, [8, 0, 0]), (0.25, [4, 0, 0]), (0.4, [-4, 0, 0]), (0.5, [0, 0, 0])]},
            'tc_ribbon': {'rotation': [(0, [0, 0, 0]), (0.25, [0, 0, -6]), (0.5, [0, 0, 0])]}}
    m.anim('walk', 0.5, 'loop', walk)
    m.anim('attack', 0.5, 'once', {'body': {
        'position': [(0, [0, 0, 0]), (0.15, [0, 0, 2]), (0.25, [0, 1.5, -3.5]), (0.32, [0, 0, -2.5]), (0.5, [0, 0, 0])],
        'rotation': [(0, [0, 0, 0]), (0.15, [-14, 0, 0]), (0.25, [18, 0, 0]), (0.5, [0, 0, 0])],
        'scale': [(0, S(1)), (0.15, [1.14, 0.82, 1.14]), (0.25, [0.9, 1.12, 0.9]), (0.32, [1.15, 0.85, 1.15]), (0.5, S(1))]}})
    common_tail(m, death={'body': {'scale': [(0, S(1)), (0.12, [0.85, 1.25, 0.85]), (0.3, [1.7, 0.18, 1.7]), (0.6, [1.9, 0.06, 1.9])]}})
    m.anims[-1]['length'] = 0.6
    return m


# =================================================================== goblin cage
def goblin_cage():
    m = Model('clash_goblin_cage', density=1.5)
    m.mats_({
        'stone': ('#8f8a80', 'brick', {'bh': 4, 'bw': 8}), 'stone_d': ('#6c675e', 'stone'), 'stone_l': ('#a9a397', 'stone'),
        'wood': ('#8b5a2b', 'wood'), 'wood_d': ('#5d3a1a', 'wood', {'grain': 'v'}), 'plank': ('#9c6a36', 'wood', {'planks': True}),
        'iron': ('#4d5057', 'metal'), 'iron_l': ('#6d7179', 'metal', {'rivets': True}), 'gold': ('#e0ae38', 'metal'),
        'skin': ('#6cbf34', 'skin'), 'skin_d': ('#4f9628', 'skin'), 'leather': ('#6e4524', 'leather'), 'leather_d': ('#4a2c14', 'leather'),
        'band': ('#efefef', 'cloth'), 'tooth': ('#f4eedc', 'bone'), 'nail': ('#d8cfb4', 'bone'), 'hair': ('#2b2b2b', 'hair'),
    })
    root = m.bone('root', [0, 0, 0])
    frame = m.bone('frame', [0, 0, 0], root)
    cb(frame, 0, 0, 0, 40, 4.2, 32, 'stone')
    cb(frame, 0, 4.2, 0, 36.5, 0.8, 28.5, 'stone_l')
    cb(frame, 0, 4.6, 0, 34, 1.6, 26, 'plank')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(frame, sx * 15, 6, sz * 11, 4, 31, 4, 'wood_d')
            cb(frame, sx * 15, 5.6, sz * 11, 5, 1.6, 5, 'iron_l')
    for sz in (1, -1):
        cb(frame, 0, 34, sz * 11, 26, 3, 3, 'wood')
        cb(frame, 0, 6, sz * 11, 26, 2, 2.6, 'wood')
    for sx in (1, -1):
        cb(frame, sx * 15, 34, 0, 3, 3, 18, 'wood')
        cb(frame, sx * 15, 6, 0, 2.6, 2, 18, 'wood')
    # back bars (static)
    for x in (-11.5, -7.7, -4, 0, 4, 7.7, 11.5):
        cb(frame, x, 8, 11, 1.2, 26, 1.2, 'iron')
    cb(frame, 0, 20, 11, 26, 1.2, 1.4, 'iron')
    # front bars (burst open on death)
    bf = m.bone('bars_f', [0, 7, -11], root)
    for x in (-11.5, -7.7, -4, 4, 7.7, 11.5):
        cb(bf, x, 8, -11, 1.2, 26, 1.2, 'iron')
    cb(bf, 0, 20, -11, 26, 1.2, 1.4, 'iron')
    cb(bf, 0, 17.1, -12.1, 3.2, 3.6, 1.6, 'gold', decals={'north': [('rect', 0.4, 0.35, 0.6, 0.75, '#3a2a10')]})   # padlock
    cb(bf, 0, 20.7, -12.1, 2.2, 1.6, 0.8, 'iron_l')
    for sx, side in ((1, 'r'), (-1, 'l')):
        bs = m.bone('bars_' + side, [sx * 15, 7, 0], root)
        for z in (-6.5, -3.25, 0, 3.25, 6.5):
            cb(bs, sx * 15, 8, z, 1.2, 26, 1.2, 'iron')
        cb(bs, sx * 15, 20, 0, 1.4, 1.2, 18, 'iron')
    # team colour: banners on the front posts + valance under the roof
    tcb = m.bone('tc_banner', [0, 33, -13], frame)
    emblem = [('rect', 0.25, 0.25, 0.75, 0.55, '#4a4a4a'), ('rect', 0.35, 0.33, 0.45, 0.42, '#efefef'), ('rect', 0.55, 0.33, 0.65, 0.42, '#efefef'),
              ('rect', 0.0, 0.0, 1.0, 0.06, '#9a9a9a'), ('rect', 0.0, 0.9, 0.25, 1.0, '#9a9a9a'), ('rect', 0.75, 0.9, 1.0, 1.0, '#9a9a9a')]
    for sx in (1, -1):
        cb(tcb, sx * 15, 16, -13.4, 4.6, 17, 0.6, 'band', decals={'north': emblem})
        cb(tcb, sx * 15, 16, 13.4, 4.6, 17, 0.6, 'band', decals={'south': emblem})
    scallop = [('rect', 0.0, 0.0, 1.0, 0.25, '#bdbdbd')] + [('rect', i / 8 + 0.04, 0.75, i / 8 + 0.08, 1.0, '#9a9a9a') for i in range(8)]
    cb(tcb, 0, 31.6, 12.8, 26, 2.4, 0.6, 'band', decals={'south': scallop})
    # roof (pops off on death)
    roof = m.bone('roof', [0, 37, 0], root)
    cb(roof, 0, 37, 0, 37, 2.4, 27.5, 'plank')
    cb(roof, 0, 39.4, 0, 30, 1.4, 22, 'wood_d')
    for x in (-10, 0, 10):
        cb(roof, x, 37.2, 0, 2, 2.6, 28, 'iron_l')
    for sx, side in ((1, 'r'), (-1, 'l')):
        cb(roof, sx * 16, 39.4, -12, 1, 5, 1, 'wood_d')
        cb(roof, sx * 16, 44.4, -12, 1.6, 1.2, 1.6, 'gold')
        fl = m.bone('tc_flag_' + side, [sx * 16, 44, -12], roof)
        cb(fl, sx * 18.8, 40.6, -12, 5, 3.4, 0.6, 'band', decals={'north': [('rect', 0.7 if sx > 0 else 0.0, 0.3, 1.0 if sx > 0 else 0.3, 0.7, '#bdbdbd')]})
    # ---- muscular goblin inside, gripping the front bars
    gz = -2.5                                                                     # goblin stands close to the front bars
    gob = m.bone('gob', [0, 12, gz], root)

    def g(b, x, y, z, *a, **k):
        return cb(b, x, y, z + gz, *a, **k)
    for sx in (1, -1):
        g(gob, sx * 3.2, 6.2, 1, 4, 6, 4.4, 'skin_d')
        g(gob, sx * 3.2, 6.2, -0.4, 4.6, 1.8, 6, 'leather_d')
    g(gob, 0, 10.5, 1, 11, 4, 7.4, 'leather', decals={'north': [('rect', 0.3, 0.4, 0.7, 1.0, '#5a3418')]})
    g(gob, 0, 13.8, 1, 11.6, 1.6, 8, 'leather_d')
    g(gob, 0, 13.8, -3.1, 2, 1.6, 0.6, 'gold')
    g(gob, 0, 15.2, 1, 11.4, 4.5, 7.2, 'skin', decals={'north': [('rect', 0.48, 0.0, 0.52, 1.0, '#4f9628'), ('rect', 0.25, 0.45, 0.75, 0.5, '#4f9628')]})
    g(gob, 0, 19.2, 0.6, 14.6, 4.6, 8.6, 'skin', decals={'north': [('rect', 0.48, 0.1, 0.52, 0.9, '#4f9628'), ('rect', 0.12, 0.85, 0.46, 0.9, '#4f9628'),
                                                                     ('rect', 0.54, 0.85, 0.88, 0.9, '#4f9628')]})
    g(gob, 0, 21.8, 2.2, 9, 2.6, 6, 'skin')                                       # trapezius
    head = m.bone('gob_head', [0, 23, gz], gob)
    g(head, 0, 22.6, -0.6, 9.6, 7.6, 8, 'skin', decals={'north': [
        ('rect', 0.1, 0.26, 0.44, 0.35, '#1d3a0c'), ('rect', 0.56, 0.26, 0.9, 0.35, '#1d3a0c'),          # angry brows
        ('rect', 0.16, 0.37, 0.4, 0.52, '#fff7b0'), ('rect', 0.6, 0.37, 0.84, 0.52, '#fff7b0'),
        ('rect', 0.26, 0.4, 0.36, 0.52, '#c0180c'), ('rect', 0.64, 0.4, 0.74, 0.52, '#c0180c'),
        ('rect', 0.18, 0.7, 0.82, 0.92, '#3a0c08'), ('rect', 0.22, 0.7, 0.78, 0.77, '#f4eedc'), ('rect', 0.3, 0.86, 0.7, 0.92, '#f4eedc')]})
    g(head, 0, 25, -5.2, 2.2, 2.6, 1.6, 'skin_d')                                  # nose
    g(head, 0, 30, 0, 3.6, 1.2, 6, 'hair')                                         # mohawk
    for sx in (1, -1):
        g(head, sx * 6.9, 26, -0.4, 6, 2.4, 1.2, 'skin', rot=('z', -sx * 22.5))     # pointy ears
        g(head, sx * 6.4, 25.2, -1.2, 0.8, 1.2, 0.8, 'gold')
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('gob_arm_' + side, [sx * 8.5, 21, 0.5 + gz], gob)
        g(arm, sx * 9.2, 17.6, 0.4, 5.6, 6, 5.8, 'skin')                            # big shoulder / bicep
        cb(arm, sx * 7.6, 17.8, -6.6, 4.4, 4.4, 4.6, 'skin_d')                       # forearm forward
        cb(arm, sx * 7.4, 17.5, -8.2, 4.8, 1.4, 1.8, 'leather')                      # wrist wrap
        cb(arm, sx * 7, 17.2, -10.4, 3.8, 4.8, 3.2, 'skin', decals={'north': [('rect', 0.0, 0.3, 1.0, 0.36, '#4f9628'), ('rect', 0.0, 0.62, 1.0, 0.68, '#4f9628')]})
    m.head_scale = ('gob', 1.1, [0, 6, -11])
    m.hitbox(3.2, 2.6)
    # ---- animations
    L = 1.6
    idle = {'gob': {'position': loop([[0, 0, 0.0], [0, 0, 1.0], [0, 0, -0.3], [0, 0, 1.0], [0, 0, -0.3], [0, 0, 0.2], [0, 0, 0], [0, 0, 0]], L),
                    'rotation': loop([[0, 0, 0], [-4, 0, 2], [3, 0, -2], [-4, 0, 2], [3, 0, -2], [0, 0, 0], [0, 0, 0], [0, 0, 0]], L)},
            'bars_f': {'rotation': loop([[0, 0, 0], [-1.6, 0, 0.6], [1.2, 0, -0.6], [-1.6, 0, 0.6], [1.2, 0, -0.6], [0, 0, 0], [0, 0, 0], [0, 0, 0]], L),
                       'position': loop([[0, 0, 0], [0.3, 0, 0.4], [-0.3, 0, -0.3], [0.3, 0, 0.4], [-0.3, 0, -0.3], [0, 0, 0], [0, 0, 0], [0, 0, 0]], L)},
            'gob_head': {'rotation': loop([[0, 0, 0], [8, 0, 8], [-4, 0, -8], [8, 0, 8], [-4, 0, -8], [0, 10, 0], [0, -10, 0], [0, 0, 0]], L)},
            'tc_flag_r': {'rotation': loop([[0, 8, 0], [0, -8, 0]], L)}, 'tc_flag_l': {'rotation': loop([[0, -8, 0], [0, 8, 0]], L)}}
    m.anim('idle', L, 'loop', idle)
    att = {'gob': {'position': [(0, [0, 0, 0]), (0.1, [0, 0.4, 1.6]), (0.2, [0, 0, -0.6]), (0.3, [0, 0.4, 1.6]), (0.4, [0, 0, -0.6]), (0.6, [0, 0, 0])]},
           'bars_f': {'rotation': [(0, [0, 0, 0]), (0.1, [-3, 0, 1]), (0.2, [3, 0, -1]), (0.3, [-3, 0, 1]), (0.4, [3, 0, -1]), (0.6, [0, 0, 0])],
                      'position': [(0, [0, 0, 0]), (0.1, [0.5, 0, 0.6]), (0.2, [-0.5, 0, -0.6]), (0.3, [0.5, 0, 0.6]), (0.4, [-0.5, 0, -0.6]), (0.6, [0, 0, 0])]},
           'gob_head': {'rotation': [(0, [0, 0, 0]), (0.1, [-18, 0, 0]), (0.45, [-14, 0, 0]), (0.6, [0, 0, 0])]},
           'roof': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.6, 0]), (0.2, [0, 0, 0]), (0.35, [0, 0.6, 0]), (0.4, [0, 0, 0])]}}
    m.anim('attack', 0.6, 'once', att)
    m.anim('spawn', 0.6, 'once', {'root': {'position': [(0, [0, 26, 0]), (0.28, [0, 0, 0]), (0.4, [0, 1.2, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, S(0.6)), (0.28, [1.1, 0.86, 1.1]), (0.4, [0.97, 1.04, 0.97]), (0.6, S(1))]}})
    building_hit(m)
    death = {'bars_f': {'rotation': [(0, [0, 0, 0]), (0.1, [-6, 0, 0]), (0.3, [82, 0, 0]), (0.38, [74, 0, 0]), (0.45, [80, 0, 0])],
                        'position': [(0, [0, 0, 0]), (0.3, [0, -2, -1]), (0.45, [0, -2.4, -1])]},
             'bars_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 4]), (0.34, [0, 0, -78]), (0.45, [0, 0, -72])], 'position': [(0, [0, 0, 0]), (0.34, [0, -3, 0])]},
             'bars_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -4]), (0.34, [0, 0, 78]), (0.45, [0, 0, 72])], 'position': [(0, [0, 0, 0]), (0.34, [0, -3, 0])]},
             'roof': {'position': [(0, [0, 0, 0]), (0.2, [0, 7, 0]), (0.5, [0, -1, 2]), (0.7, [0, -2.5, 2])],
                      'rotation': [(0, [0, 0, 0]), (0.2, [-6, 0, 10]), (0.5, [-8, 0, 16]), (0.7, [-8, 0, 18])]},
             'gob': {'position': [(0, [0, 0, 0]), (0.12, [0, -2, 0]), (0.3, [0, 8, -14]), (0.45, [0, 6, -24])],
                     'scale': [(0, S(1)), (0.3, S(1.1)), (0.42, S(1)), (0.46, S(0.01)), (1.0, S(0.01))]},
             'gob_head': {'rotation': [(0, [0, 0, 0]), (0.12, [-20, 0, 0]), (0.3, [-10, 0, 0])]},
             'frame': {'rotation': [(0, [0, 0, 0]), (0.15, [0, 0, 2]), (0.3, [0, 0, -1]), (0.5, [0, 0, 0])]}}
    m.anim('death', 1.0, 'hold', death)
    return m


# =================================================================== x-bow (turret)
def x_bow():
    m = Model('clash_x_bow', density=1.5)
    m.mats_({
        'stone': ('#8d8a84', 'brick', {'bh': 4, 'bw': 8}), 'stone_l': ('#aaa69d', 'stone'), 'stone_d': ('#67635c', 'stone'),
        'wood': ('#8b5a2b', 'wood'), 'wood_d': ('#5a381a', 'wood'), 'wood_v': ('#6e4622', 'wood', {'grain': 'v'}),
        'plank': ('#9a6a38', 'wood', {'planks': True}), 'iron': ('#565a62', 'metal', {'rivets': True}), 'iron_d': ('#3d4046', 'metal'),
        'steel': ('#c4c9d2', 'metal'), 'shaft': ('#c09460', 'wood'), 'string': ('#efe6cc', 'rope'), 'band': ('#efefef', 'cloth'),
        'brass': ('#d2a446', 'metal'),
    })
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    # stone platform
    cb(base, 0, 0, 0, 36, 5, 36, 'stone')
    cb(base, 0, 5, 0, 31, 1.6, 31, 'stone_l')
    # four splayed wooden legs + cross braces
    for sx in (1, -1):
        for sz in (1, -1):
            cb(base, sx * 11, 6.6, sz * 11, 4, 10, 4, 'wood_v')
            cb(base, sx * 11, 6.4, sz * 11, 5.4, 1.6, 5.4, 'iron')
    for sx in (1, -1):
        cb(base, sx * 11, 10.6, 0, 1.4, 1.6, 26, 'wood_d', rot=('x', 22.5 * sx))
    cb(base, 0, 10.6, 11, 26, 1.6, 1.4, 'wood_d', rot=('z', 22.5))
    # deck
    cb(base, 0, 16.4, 0, 28, 2.6, 28, 'plank')
    cb(base, 0, 16.0, 0, 29, 1.0, 29, 'iron_d')
    # pedestal + swivel ring
    cb(base, 0, 19, 0, 13, 1.4, 13, 'iron')
    cb(base, 0, 20.2, 0, 10, 0.8, 10, 'brass')
    # team banners hanging from the deck (front, sides)
    tcb = m.bone('base_tc_banner', [0, 16, 0], base)
    emblem = [('rect', 0.2, 0.15, 0.8, 0.22, '#9a9a9a'), ('rect', 0.47, 0.15, 0.53, 0.75, '#5a5a5a'), ('rect', 0.2, 0.35, 0.8, 0.42, '#5a5a5a'),
              ('rect', 0.0, 0.88, 0.3, 1.0, '#8a8a8a'), ('rect', 0.7, 0.88, 1.0, 1.0, '#8a8a8a')]
    for x in (-5.5, 5.5):
        cb(tcb, x, 6.5, -14.4, 6, 10, 0.6, 'band', decals={'north': emblem})
    for sx in (1, -1):
        cb(tcb, sx * 14.4, 6.5, 0, 0.6, 10, 7, 'band', decals={'east' if sx > 0 else 'west': emblem})
    cb(tcb, 0, 17.2, -14.3, 28.4, 1.4, 0.6, 'band')
    # ---------------- top (turret): pivot on the rotation axis
    top = m.bone('top', [0, 21, 0], root)
    cb(top, 0, 21, 0, 12, 2, 12, 'wood_d')
    for sx in (1, -1):
        cb(top, sx * 4.4, 23, 1, 1.6, 6, 8, 'iron')                                # yoke cheeks
    HZ = -25.0                                                                    # bow head z
    bow = m.bone('top_bow', [0, 27, 1], top)
    cb(bow, 0, 25, -8.5, 6.4, 5, 37, 'wood', decals={'up': [('rect', 0.3, 0.0, 0.7, 1.0, '#3a2410')]})
    cb(bow, 0, 26.2, 1, 9.6, 1.6, 1.6, 'iron_d')                                  # axle pin
    cb(bow, 0, 24.6, HZ, 9.6, 5.6, 5, 'iron')                                      # bow head
    cb(bow, 0, 24.6, 10.6, 7.4, 5.6, 1.6, 'iron')                                   # butt plate
    for sx in (1, -1):                                                            # side rails
        cb(bow, sx * 1.7, 30, -6, 0.8, 0.8, 30, 'wood_d')
    tcs = m.bone('top_tc_band', [0, 27, 0], bow)
    for z in (-12, 6):
        cb(tcs, 0, 24.6, z, 6.8, 5.6, 2.4, 'band')
    # winch (crank) at the back
    cb(bow, 0, 22.8, 7, 11, 3, 3, 'wood_d')
    for sx in (1, -1):
        cr = m.bone('top_crank_' + ('r' if sx > 0 else 'l'), [sx * 6.2, 24.3, 7], bow)
        cb(cr, sx * 6.2, 21.3, 7, 0.8, 6, 6, 'iron', decals={'east': [('ering', 0.5, 0.5, 0.5, 0.5, 0.3, '#2a2c30')], 'west': [('ering', 0.5, 0.5, 0.5, 0.5, 0.3, '#2a2c30')]})
        cb(cr, sx * 7.2, 24, 7, 1.2, 1.2, 1.2, 'brass')
        cb(cr, sx * 7.2, 24.6, 10.1, 1.0, 1.0, 5, 'iron_d')
    # spare bolts strapped to the side
    for sx in (1, -1):
        cb(bow, sx * 3.7, 25.4, -2, 1, 1, 16, 'shaft')
        cb(bow, sx * 3.7, 25.2, -10.8, 1.4, 1.4, 1.6, 'steel')
    # limbs (swept back), wrapped grips in team colour, steel tips; string bones are children of the limbs
    L = 18.0
    a = math.radians(22.5)
    tipx, tipz = 3.5 + L * math.cos(a), HZ + L * math.sin(a)
    SL = tipx / math.cos(a)
    nock_z = tipz + SL * math.sin(a)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lb = m.bone('top_limb_' + side, [sx * 3.5, 30.5, HZ], bow)
        x0, x1 = (3.5, 3.5 + L) if sx > 0 else (-3.5 - L, -3.5)
        lb.box([x0, 29.0, HZ - 1.6], [x1, 32.0, HZ + 1.6], 'wood_d', rot=('y', -22.5 * sx), rot_origin=[sx * 3.5, 30.5, HZ])
        x0, x1 = (3.5, 3.5 + L) if sx > 0 else (-3.5 - L, -3.5)
        lb.box([x0 + (2 if sx > 0 else 0), 29.5, HZ - 2.3], [x1 - (0 if sx > 0 else 2), 31.5, HZ - 1.6], 'iron', rot=('y', -22.5 * sx), rot_origin=[sx * 3.5, 30.5, HZ])
        cb(lb, sx * tipx, 28.6, tipz, 2.4, 3.8, 2.4, 'steel')
        tw = m.bone('top_tc_wrap_' + side, [sx * 12, 30.5, HZ + 4], lb)
        for k in (0.45, 0.72):
            px_, pz_ = sx * (3.5 + L * k * math.cos(a)), HZ + L * k * math.sin(a)
            cb(tw, px_, 28.8, pz_, 2.6, 3.4, 3.6, 'band')
        st = m.bone('top_string_' + side, [sx * tipx, 30.55, tipz], lb)
        x0, x1 = (0, SL) if sx > 0 else (-SL, 0)
        st.box([x0, 30.1, nock_z - 0.45], [x1, 31.0, nock_z + 0.45], 'string', rot=('y', 22.5 * sx), rot_origin=[0, 30.55, nock_z])
    # bolt
    bolt = m.bone('top_bolt', [0, 31.2, -20], bow)
    blen = 22.0
    cb(bolt, 0, 30.4, nock_z - blen / 2, 1.6, 1.6, blen, 'shaft')
    cb(bolt, 0, 30.1, nock_z - blen - 1.4, 3.0, 2.2, 3.0, 'steel')
    cb(bolt, 0, 30.6, nock_z - blen - 3.6, 1.6, 1.2, 1.6, 'steel')
    fl = m.bone('top_tc_fletch', [0, 31.2, nock_z - 3], bolt)
    cb(fl, 0, 32.0, nock_z - 3.2, 0.5, 2.0, 4.2, 'band')
    cb(fl, 0, 31.0, nock_z - 3.2, 4.4, 0.5, 4.2, 'band')
    BK, BP = 1.2, [0, 27, -4]                                                      # enlarge the whole bow for a bolder silhouette
    m.scale_bone('top_bow', BK, BP)
    mz = [0, 31.2, nock_z - blen - 4.2]
    m.muzzle = tuple(round(BP[i] + (mz[i] - BP[i]) * BK, 2) for i in range(3))
    m.hitbox(2.6, 2.4)

    # ---------------- animations
    m.anim('idle', 2.4, 'loop', {'top_bow': {'rotation': loop([[0, 0, 0], [-1.5, 0, 0]], 2.4)},
                                 'base_tc_banner': {'rotation': loop([[2, 0, 0], [-2, 0, 0]], 2.4)},
                                 'top_crank_r': {'rotation': loop([[0, 0, 0], [8, 0, 0]], 2.4)},
                                 'top_crank_l': {'rotation': loop([[0, 0, 0], [8, 0, 0]], 2.4)}})
    T = 0.3
    att = {'top_string_r': {'rotation': [(0, [0, 0, 0]), (0.03, [0, 31.5, 0]), (0.06, [0, 26, 0]), (0.1, [0, 30, 0]), (0.16, [0, 18, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_string_l': {'rotation': [(0, [0, 0, 0]), (0.03, [0, -31.5, 0]), (0.06, [0, -26, 0]), (0.1, [0, -30, 0]), (0.16, [0, -18, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_limb_r': {'rotation': [(0, [0, 0, 0]), (0.03, [0, -9, 0]), (0.06, [0, -5, 0]), (0.1, [0, -8, 0]), (0.16, [0, -5, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_limb_l': {'rotation': [(0, [0, 0, 0]), (0.03, [0, 9, 0]), (0.06, [0, 5, 0]), (0.1, [0, 8, 0]), (0.16, [0, 5, 0]), (0.26, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_bolt': {'position': [(0, [0, 0, 0]), (0.03, [0, 0, -14]), (0.05, [0, 0, -18]), (0.06, [0, 0, 4]), (0.18, [0, 0, 4]), (0.26, [0, 0, 0]), (T, [0, 0, 0])],
                        'scale': [(0, S(1)), (0.03, S(1)), (0.05, S(0.01)), (0.17, S(0.01)), (0.2, S(1)), (T, S(1))]},
           'top_bow': {'position': [(0, [0, 0, 0]), (0.04, [0, 0.4, 2.6]), (0.12, [0, 0, 0.6]), (T, [0, 0, 0])],
                       'rotation': [(0, [0, 0, 0]), (0.04, [-4, 0, 0]), (0.12, [-1, 0, 0]), (T, [0, 0, 0])]},
           'top_crank_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.27, [-180, 0, 0]), (T, [-180, 0, 0])]},
           'top_crank_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.27, [-180, 0, 0]), (T, [-180, 0, 0])]},
           'top': {'position': [(0, [0, 0, 0]), (0.04, [0, 0, 0.8]), (0.12, [0, 0, 0]), (T, [0, 0, 0])]}}
    m.anim('attack', T, 'once', att)
    m.anim('spawn', 0.8, 'once', {
        'base': {'scale': [(0, [1, 0.05, 1]), (0.3, [1.02, 1.08, 1.02]), (0.4, S(1)), (0.8, S(1))]},
        'top': {'scale': [(0, S(0.01)), (0.3, S(0.01)), (0.31, S(1)), (0.8, S(1))],
                'position': [(0, [0, 24, 0]), (0.3, [0, 24, 0]), (0.58, [0, -1.5, 0]), (0.68, [0, 0.6, 0]), (0.8, [0, 0, 0])]},
        'top_bow': {'rotation': [(0, [0, 0, 0]), (0.3, [-10, 0, 0]), (0.58, [3, 0, 0]), (0.8, [0, 0, 0])]}})
    building_hit(m)
    m.anim('death', 1.0, 'hold', {
        'base': {'scale': [(0, S(1)), (0.15, [1.03, 1.03, 1.03]), (0.55, [1.05, 0.72, 1.05]), (0.9, [1.08, 0.58, 1.08])],
                 'rotation': [(0, [0, 0, 0]), (0.55, [0, 0, 3]), (0.9, [0, 0, 4])]},
        'top': {'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.6, [-5, -12, 2]), (0.8, [-7, -15, 2]), (1.0, [-7, -15, 2])],
                'rotation': [(0, [0, 0, 0]), (0.2, [-6, 0, 0]), (0.6, [18, 0, -45]), (0.8, [22, 0, -62]), (1.0, [22, 0, -60])]},
        'top_string_r': {'rotation': [(0, [0, 0, 0]), (0.1, [0, 31.5, 0])]},
        'top_string_l': {'rotation': [(0, [0, 0, 0]), (0.1, [0, -31.5, 0])]},
        'top_bolt': {'position': [(0, [0, 0, 0]), (0.3, [0, -6, 2])], 'rotation': [(0, [0, 0, 0]), (0.3, [0, 0, 40])]}})
    return m


# =================================================================== bomb tower (turret) v2: slim Tesla-like stone tower + bomber on top
def bomb_tower():
    m = Model('clash_bomb_tower', density=1.6)
    m.mats_({
        'stone': ('#9a9488', 'brick', {'bh': 4, 'bw': 6}), 'stone_d': ('#6e6a60', 'brick', {'bh': 3, 'bw': 6}), 'stone_l': ('#b6b0a3', 'stone'),
        'slab': ('#a8a296', 'stone'), 'wood': ('#8b5a2b', 'wood'), 'door': ('#4a2e14', 'wood', {'grain': 'v'}),
        'iron': ('#565a62', 'metal', {'rivets': True}), 'iron_d': ('#3a3d42', 'metal'), 'brass': ('#c9973a', 'metal'),
        'bone': ('#e8e2cf', 'bone'), 'bone_d': ('#c9c1a8', 'bone'), 'pants': ('#6a4a2e', 'leather', {'stitch': False}),
        'lens': ('#5fc8ff', 'gem'), 'bomb': ('#2b2b33', 'metal'), 'fuse': ('#6a5636', 'rope'), 'spark': ('#ffd04a', 'glow'),
        'band': ('#efefef', 'cloth'),
    })
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    tower = m.bone('base_tower', [0, 0, 0], base)
    slit = [('rect', 0.44, 0.3, 0.56, 0.7, '#1e1a16'), ('rect', 0.38, 0.45, 0.62, 0.53, '#1e1a16')]
    cb(tower, 0, 0, 0, 26, 2.5, 26, 'stone_d')                                    # plinth
    cb(tower, 0, 2.5, 0, 20, 4, 20, 'stone_d')                                    # base course
    cb(tower, 0, 6.5, 0, 16, 10, 16, 'stone', decals={'east': slit, 'west': slit, 'south': slit})
    cb(tower, 0, 16, 0, 17, 1.2, 17, 'stone_l')                                   # string course
    cb(tower, 0, 17.2, 0, 14, 8.3, 14, 'stone', decals={'east': slit, 'west': slit, 'south': slit})
    for sx in (1, -1):
        for sz in (1, -1):
            cb(tower, sx * 7.4, 6.5, sz * 7.4, 2.6, 9.5, 2.6, 'stone_l')           # corner quoins
            cb(tower, sx * 6.4, 17.2, sz * 6.4, 2.4, 8.3, 2.4, 'stone_l')
            cb(tower, sx * 9.6, 2.5, sz * 9.6, 2.2, 5, 2.2, 'stone_l')              # buttress feet
    crown = m.bone('base_crown', [0, 27, 0], base)                                # corbel + platform (breaks away on death)
    cb(crown, 0, 25.5, 0, 17.4, 2.4, 17.4, 'stone_l')
    cb(crown, 0, 27.9, 0, 20.6, 1.6, 20.6, 'stone_d')
    cb(crown, 0, 29.5, 0, 22, 1.5, 22, 'slab')
    cb(tower, 0, 6.5, -8.3, 5.2, 7, 0.8, 'door', decals={'north': [('rect', 0.0, 0.3, 1.0, 0.38, '#3a3d42'), ('rect', 0.0, 0.72, 1.0, 0.8, '#3a3d42'),
                                                                 ('px', 0.8, 0.55, '#d2a446')]})
    cb(tower, 0, 13.5, -8.4, 6.4, 1.2, 1.0, 'stone_l')                            # lintel
    # team colour: trim on the flare + banners on the shaft
    tct = m.bone('base_tc_trim', [0, 26, 0], crown)
    cb(tct, 0, 26.2, 0, 17.9, 1.1, 17.9, 'band')
    tcb = m.bone('base_tc_banner', [0, 25, -8.8], tower)
    bomb_emb = [('rect', 0.22, 0.32, 0.78, 0.68, '#3a3a3a'), ('rect', 0.3, 0.26, 0.7, 0.74, '#3a3a3a'), ('rect', 0.45, 0.16, 0.55, 0.26, '#7a6a4a'),
                ('px', 0.6, 0.1, '#ffd04a'), ('rect', 0.34, 0.36, 0.44, 0.44, '#8a8a8a'), ('rect', 0.0, 0.0, 1.0, 0.06, '#9a9a9a'),
                ('rect', 0.0, 0.93, 0.3, 1.0, '#9a9a9a'), ('rect', 0.7, 0.93, 1.0, 1.0, '#9a9a9a')]
    cb(tcb, 0, 14.4, -8.8, 7, 11, 0.6, 'band', decals={'north': bomb_emb})
    cb(tcb, 0, 14.4, 8.8, 7, 11, 0.6, 'band', decals={'south': bomb_emb})
    for sx in (1, -1):
        cb(tcb, sx * 8.8, 17.4, 0, 0.6, 8, 5.6, 'band', decals={'east' if sx > 0 else 'west': bomb_emb})
    # railing (falls off on death)
    for nm, sz in (('n', -1), ('s', 1)):
        rb = m.bone('base_rail_' + nm, [0, 31, sz * 10], base)
        for x in (-10, 0, 10):
            cb(rb, x, 31, sz * 10, 1.6, 3.4, 1.6, 'iron' if x else 'iron_d')
        cb(rb, 0, 33.2, sz * 10, 21, 0.9, 0.9, 'iron_d')
    for nm, sx in (('e', 1), ('w', -1)):
        rb = m.bone('base_rail_' + nm, [sx * 10, 31, 0], base)
        cb(rb, sx * 10, 31, 0, 1.6, 3.4, 1.6, 'iron_d')
        cb(rb, sx * 10, 33.2, 0, 0.9, 0.9, 19, 'iron_d')
    # big bomb hidden inside the shaft + rubble chunks (both show when the tower crumbles)
    rub = m.bone('base_rubble', [0, 4, 0], base)
    for (x, z, w, h, rr) in ((-4.5, -4, 4, 9, 22.5), (4.5, -4.5, 3.6, 10, -22.5), (4.5, 4.5, 4, 8.6, 22.5), (-4.5, 4.5, 3.6, 10.4, -22.5)):
        cb(rub, x, 4, z, w, h, w, 'stone_l' if w > 3.8 else 'stone_d', rot=('y', rr))
    bb = m.bone('base_bigbomb', [0, 13, 0], base)
    cb(bb, 0, 7.6, 0, 11, 11, 11, 'bomb', decals={'north': [('rect', 0.16, 0.14, 0.34, 0.3, '#6a6a76'), ('rect', 0.38, 0.45, 0.62, 0.68, '#e8e8e8'),
                                                            ('rect', 0.42, 0.5, 0.48, 0.56, '#2b2b33'), ('rect', 0.52, 0.5, 0.58, 0.56, '#2b2b33'),
                                                            ('rect', 0.42, 0.7, 0.58, 0.75, '#e8e8e8')]})
    cb(bb, 0, 18.6, 0, 3.6, 1.4, 3.6, 'iron')
    cb(bb, 0, 20, 0, 1.0, 2.0, 1.0, 'fuse')
    sp = m.bone('base_bigbomb_spark', [0, 22.6, 0], bb)
    cb(sp, 0, 22, 0, 1.4, 1.4, 1.4, 'spark')
    # ---------------- top: the bomber (turns to aim), pivot at the platform centre
    Y0 = 31
    top = m.bone('top', [0, Y0, 0], root)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('top_leg_' + side, [sx * 2.6, Y0 + 8.6, 0], top)
        cb(lg, sx * 2.6, Y0 + 1.2, 0, 1.8, 7.4, 1.8, 'bone')
        cb(lg, sx * 2.6, Y0 + 4.0, 0, 2.4, 1.4, 2.4, 'bone_d')
        cb(lg, sx * 2.6, Y0, -0.6, 2.8, 1.4, 4, 'bone_d')
    body = m.bone('top_body', [0, Y0 + 8.6, 0], top)
    cb(body, 0, Y0 + 7.2, 0.2, 8.4, 2.8, 4.8, 'pants')
    cb(body, 0, Y0 + 9.6, 0.8, 1.8, 3, 1.8, 'bone_d')                             # spine
    cb(body, 0, Y0 + 11.6, 0, 8.4, 5.2, 5, 'bone', decals={'north': [('rect', 0.47, 0.0, 0.53, 1.0, '#9a927c')] +
                                                            [('rect', 0.1, y, 0.9, y + 0.1, '#5a5446') for y in (0.2, 0.45, 0.7)],
                                                            'east': [('rect', 0.0, y, 1.0, y + 0.1, '#5a5446') for y in (0.2, 0.45, 0.7)],
                                                            'west': [('rect', 0.0, y, 1.0, y + 0.1, '#5a5446') for y in (0.2, 0.45, 0.7)]})
    cb(body, 0, Y0 + 9.4, -2.9, 2.6, 2.6, 1.6, 'bomb')                             # small belt bomb
    scarf = m.bone('top_tc_scarf', [0, Y0 + 16.6, 0], body)
    cb(scarf, 0, Y0 + 16.2, 0, 8.8, 2, 6, 'band')
    cb(scarf, -2.2, Y0 + 13.2, 3.2, 2.2, 3.6, 0.8, 'band')
    head = m.bone('top_head', [0, Y0 + 17.6, 0], body)
    cb(head, 0, Y0 + 17.4, -0.4, 9, 7.6, 8, 'bone', decals={'north': [
        ('rect', 0.12, 0.4, 0.42, 0.66, '#1c1a18'), ('rect', 0.58, 0.4, 0.88, 0.66, '#1c1a18'), ('px', 0.26, 0.52, '#ff9a2a'), ('px', 0.72, 0.52, '#ff9a2a'),
        ('rect', 0.45, 0.7, 0.55, 0.8, '#3a3530'), ('rect', 0.22, 0.86, 0.78, 0.92, '#3a3530'),
        ('rect', 0.34, 0.86, 0.37, 1.0, '#3a3530'), ('rect', 0.5, 0.86, 0.53, 1.0, '#3a3530'), ('rect', 0.65, 0.86, 0.68, 1.0, '#3a3530')]})
    cb(head, 0, Y0 + 16.6, -0.8, 6.6, 1.2, 6.2, 'bone_d')                          # jaw
    hb = m.bone('top_tc_band', [0, Y0 + 23, 0], head)
    cb(hb, 0, Y0 + 22.5, -0.4, 9.6, 1.6, 8.6, 'band')
    for sx in (1, -1):                                                            # goggles on the band
        cb(head, sx * 2.3, Y0 + 22.1, -4.95, 3.6, 2.6, 0.9, 'brass')
        cb(head, sx * 2.3, Y0 + 22.5, -5.45, 2.4, 1.8, 0.4, 'lens')
    # throwing arm: raised up-back, holding a bomb above the shoulder
    ar = m.bone('top_arm_r', [5.2, Y0 + 15.4, 0.4], body)
    cb(ar, 5.2, Y0 + 14.2, 0.4, 2.6, 2.4, 2.6, 'bone_d')                           # shoulder
    ar.box([4.3, Y0 + 15.4, -0.5], [6.1, Y0 + 22.4, 1.3], 'bone', rot=('x', 22.5), rot_origin=[5.2, Y0 + 15.4, 0.4])
    cb(ar, 5.2, Y0 + 20.8, 3.0, 2.6, 2.4, 2.6, 'bone_d')                           # hand
    bomb = m.bone('top_bomb', [5.2, Y0 + 24.7, 4.2], ar)
    cb(bomb, 5.2, Y0 + 22.0, 4.2, 5.4, 5.4, 5.4, 'bomb', decals={'north': [('rect', 0.15, 0.15, 0.4, 0.35, '#6a6a76')], 'east': [('rect', 0.15, 0.15, 0.4, 0.35, '#6a6a76')]})
    cb(bomb, 5.2, Y0 + 27.4, 4.2, 1.6, 0.8, 1.6, 'iron')
    cb(bomb, 5.2, Y0 + 28.2, 4.2, 0.6, 1.2, 0.6, 'fuse')
    cb(bomb, 5.2, Y0 + 29.3, 4.2, 1.0, 1.0, 1.0, 'spark')
    al = m.bone('top_arm_l', [-5.2, Y0 + 15.4, 0.4], body)
    cb(al, -5.2, Y0 + 14.2, 0.4, 2.6, 2.4, 2.6, 'bone_d')
    cb(al, -5.4, Y0 + 8.6, 0.4, 1.8, 6.4, 1.8, 'bone')
    cb(al, -5.4, Y0 + 7.4, 0.4, 2.4, 1.8, 2.4, 'bone_d')
    TK = 0.78                                                                     # bomber scale (about 1.1 blocks tall)
    m.scale_bone('top', TK, [0, Y0, 0])
    m.hitbox(2.0, 3.2)

    # ---------------- animations
    m.anim('idle', 2.0, 'loop', {'top_body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)},
                                 'top_head': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 2.0)},
                                 'top_arm_r': {'rotation': loop([[0, 0, 0], [-6, 0, 0]], 2.0)},
                                 'top_arm_l': {'rotation': loop([[0, 0, -4], [6, 0, -2]], 2.0)},
                                 'top_bomb': {'rotation': loop([[0, 0, 0], [0, 15, 0]], 2.0)},
                                 'base_bigbomb_spark': {'scale': loop([S(1), S(1)], 2.0)}})
    T = 0.8
    REL = 0.3
    att = {'top_arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-35, 0, 0]), (REL, [85, 0, 0]), (0.38, [125, 0, 0]), (0.5, [105, 0, 0]), (0.72, [0, 0, 0]), (T, [0, 0, 0])]},
           'top_bomb': {'scale': [(0, S(1)), (REL, S(1)), (REL + 0.02, S(0.01)), (0.55, S(0.01)), (0.7, S(1.15)), (T, S(1))]},
           'top_body': {'rotation': [(0, [0, 0, 0]), (0.15, [-10, -15, 0]), (REL, [14, 10, 0]), (0.45, [10, 5, 0]), (T, [0, 0, 0])],
                        'position': [(0, [0, 0, 0]), (0.15, [0, 0, 0.6]), (REL, [0, -0.4, -0.8]), (T, [0, 0, 0])]},
           'top_arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [-60, 0, -10]), (REL, [20, 0, -6]), (T, [0, 0, 0])]},
           'top_head': {'rotation': [(0, [0, 0, 0]), (0.15, [-8, 0, 0]), (REL, [8, 0, 0]), (T, [0, 0, 0])]},
           'top_leg_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-10, 0, 0]), (REL, [8, 0, 0]), (T, [0, 0, 0])]},
           'top_leg_l': {'rotation': [(0, [0, 0, 0]), (0.15, [10, 0, 0]), (REL, [-12, 0, 0]), (T, [0, 0, 0])]}}
    m.anim('attack', T, 'once', att)
    m.anim('spawn', 0.8, 'once', {
        'base': {'scale': [(0, [1, 0.05, 1]), (0.3, [1.02, 1.08, 1.02]), (0.4, S(1)), (0.8, S(1))]},
        'top': {'scale': [(0, S(0.01)), (0.35, S(0.01)), (0.36, S(1)), (0.8, S(1))],
                'position': [(0, [0, 12, 0]), (0.35, [0, 12, 0]), (0.58, [0, -0.8, 0]), (0.68, [0, 0.4, 0]), (0.8, [0, 0, 0])]},
        'top_arm_r': {'rotation': [(0, [0, 0, 0]), (0.35, [-20, 0, 0]), (0.6, [10, 0, 0]), (0.8, [0, 0, 0])]}})
    building_hit(m)
    rail_fall = {'n': [0, -31.5, -9], 's': [0, -31.5, 9], 'e': [-9, -31.5, 0], 'w': [9, -31.5, 0]}   # anim x is mirrored
    rail_rot = {'n': [60, 0, 0], 's': [-60, 0, 0], 'e': [0, 0, -60], 'w': [0, 0, 60]}
    death = {'base_tower': {'scale': [(0, S(1)), (0.15, S(1.03)), (0.3, [1.06, 0.92, 1.06]), (0.6, [1.1, 0.4, 1.1]), (0.85, [1.12, 0.34, 1.12])],
                            'rotation': [(0, [0, 0, 0]), (0.08, [0, 0, 2.5]), (0.16, [0, 0, -2.5]), (0.24, [0, 0, 1.5]), (0.32, [0, 0, 0])]},
             'base_bigbomb': {'position': [(0, [0, 0, 0]), (0.3, [0, 0, 0]), (0.5, [0, 7, 0]), (0.75, [0, 1.0, 0]), (0.85, [0, 2.0, 0]), (0.95, [0, 1.6, 0])],
                              'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, 0]), (0.75, [0, 0, 8]), (0.95, [0, 0, 6])]},
             'base_bigbomb_spark': {'scale': [(0, S(1)), (0.5, S(1)), (0.6, S(2.2)), (0.7, S(1.2)), (0.8, S(2.2)), (0.9, S(1.3)), (1.0, S(2))]},
             'base_crown': {'position': [(0, [0, 0, 0]), (0.25, [0, 0, 0]), (0.45, [0, -10, 0])],
                            'rotation': [(0, [0, 0, 0]), (0.25, [0, 0, 0]), (0.45, [8, 0, -10])],
                            'scale': [(0, S(1)), (0.3, S(1)), (0.46, S(0.01)), (1.0, S(0.01))]},
             'top': {'position': [(0, [0, 0, 0]), (0.15, [0, 4, 0]), (0.35, [-4, -6, 2]), (0.45, [-5, -10, 3])],
                     'rotation': [(0, [0, 0, 0]), (0.15, [-10, 0, 0]), (0.35, [20, 0, -40])],
                     'scale': [(0, S(1)), (0.3, S(1)), (0.45, S(0.01)), (1.0, S(0.01))]}}
    for k in rail_fall:
        death['base_rail_' + k] = {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.55, rail_fall[k])],
                                   'rotation': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.55, rail_rot[k])]}
    m.anim('death', 1.0, 'hold', death)
    return m


# =================================================================== batch 2 (CR-faithful designs)
BONE_MATS = {'bone': ('#ece6d2', 'bone'), 'bone_d': ('#c9c1a8', 'bone'), 'band': ('#efefef', 'cloth')}
RIBS = [('rect', 0.47, 0.0, 0.53, 1.0, '#9a927c')] + [('rect', 0.1, y, 0.9, y + 0.12, '#4a4438') for y in (0.18, 0.45, 0.72)]


def skull_face(eyes='#1c1a18', glow=None):
    d = [('rect', 0.12, 0.38, 0.42, 0.64, eyes), ('rect', 0.58, 0.38, 0.88, 0.64, eyes),
         ('rect', 0.45, 0.68, 0.55, 0.78, '#3a3530'), ('rect', 0.22, 0.85, 0.78, 0.91, '#3a3530'),
         ('rect', 0.34, 0.85, 0.37, 1.0, '#3a3530'), ('rect', 0.5, 0.85, 0.53, 1.0, '#3a3530'), ('rect', 0.65, 0.85, 0.68, 1.0, '#3a3530')]
    if glow:
        d += [('px', 0.27, 0.52, glow), ('px', 0.73, 0.52, glow)]
    return d


# ------------------------------------------------------------------- shared shape helpers (batch 3: CR-faithful)
def oct_(bone, x, y, z, w, h, mat, d=None, dec=None, axis='y'):
    """octagonal prism (3 boxes). axis 'y' = vertical, 'x' = lying along x (w = diameter, h = length)"""
    out = []
    for (a, b) in ((1.0, 0.6), (0.6, 1.0), (0.86, 0.86)):
        if axis == 'y':
            out.append(cb(bone, x, y, z, w * a, h, (d or w) * b, mat, decals=dec))
        else:
            out.append(cb(bone, x, y - w * a / 2, z, h, w * a, w * b, mat, decals=dec))
    return out


def sphere(bone, cx, cy, cz, r, mats, n=6, dec=None):
    """round ball from stacked octagonal slices, shrinking toward top and bottom"""
    hs = 2 * r / n
    for i in range(n):
        yc = cy - r + hs * (i + 0.5)
        hw = math.sqrt(max(r * r - (yc - cy) ** 2, 0.5)) * 1.04
        mat = mats[i % len(mats)]
        oct_(bone, cx, yc - hs / 2, cz, 2 * hw, hs, mat, dec={f: dec for f in ('north', 'south', 'east', 'west')} if dec else None)


CRACKS = [('rect', 0.15, 0.3, 0.45, 0.4, '#55534f'), ('rect', 0.4, 0.3, 0.47, 0.8, '#55534f'), ('rect', 0.62, 0.55, 0.88, 0.65, '#55534f'),
          ('rect', 0.66, 0.1, 0.8, 0.25, '#b8b6b0'), ('px', 0.25, 0.75, '#b8b6b0')]
BOULDER_MATS = {'rock': ('#8e8c88', 'stone'), 'rock_d': ('#77756f', 'stone'), 'rock_l': ('#a6a49e', 'stone')}


# ------------------------------------------------------------------- HQ helpers (batch 4)
HQ_BONE = {'bone': ('#efe8d4', 'bone'), 'bone_d': ('#cfc6aa', 'bone'), 'bone_dd': ('#a89e84', 'bone'), 'tooth': ('#fbf6e6', 'bone'),
           'socket': ('#141210', 'plain'), 'band': ('#efefef', 'cloth')}


def skull_hq(m, parent, name, cx, cy, cz, W, underbite=False, open_mouth=False):
    """detailed cartoon skull. cy = bottom of the cranium. returns the head bone"""
    H, D = 0.84 * W, 0.92 * W
    zf = cz - D / 2
    head = m.bone(name, [cx, cy, cz], parent)
    face = [('rect', 0.08, 0.34, 0.44, 0.74, '#3a342c'), ('rect', 0.56, 0.34, 0.92, 0.74, '#3a342c'),      # socket rims
            ('rect', 0.12, 0.38, 0.4, 0.72, '#141210'), ('rect', 0.6, 0.38, 0.88, 0.72, '#141210'),
            ('rect', 0.44, 0.76, 0.5, 0.92, '#141210'), ('rect', 0.5, 0.76, 0.56, 0.92, '#141210'), ('rect', 0.47, 0.72, 0.53, 0.78, '#2a2520'),
            ('rect', 0.2, 0.1, 0.34, 0.16, '#ffffff'), ('shade', 0.0, 0.0, 1.0, 0.08, 1.08)]
    cb(head, cx, cy, cz, W, H, D, 'bone', decals={'north': face, 'east': [('rect', 0.6, 0.6, 0.8, 0.75, '#bdb498')],
                                                    'west': [('rect', 0.2, 0.6, 0.4, 0.75, '#bdb498')]})
    cb(head, cx, cy + H, cz + 0.2, W * 0.82, W * 0.14, D * 0.82, 'bone')                            # dome
    cb(head, cx, cy + H + W * 0.14, cz + 0.3, W * 0.56, W * 0.08, D * 0.56, 'bone')
    cb(head, cx, cy + H * 0.15, cz + 0.4, W + 0.3, H * 0.62, D * 0.7, 'bone_d')                      # temples / back
    cb(head, cx, cy + H * 0.74, zf - 0.25, W * 0.92, H * 0.1, 0.5, 'bone')                          # brow ridge
    for sx in (1, -1):
        cb(head, cx + sx * W * 0.34, cy + H * 0.2, zf - 0.2, W * 0.24, H * 0.14, 0.5, 'bone')        # cheekbones
    teeth_dec = [('rect', x, 0.0, x + 0.035, 1.0, '#8a8066') for x in (0.2, 0.36, 0.5, 0.64, 0.8)]
    jw_z = zf - (0.9 if underbite else 0.0)
    if open_mouth:
        cb(head, cx, cy - H * 0.16, zf + 0.6, W * 0.62, H * 0.2, 1.2, 'socket')                        # dark mouth
    cb(head, cx, cy - H * 0.06, zf - 0.05, W * 0.6, H * 0.14, 0.7, 'tooth', decals={'north': teeth_dec})   # upper teeth
    jaw = m.bone(name + '_jaw', [cx, cy, cz + D * 0.2], head)
    jy = cy - H * (0.42 if open_mouth else 0.26)
    cb(jaw, cx, jy, cz - (0.5 if underbite else 0.2), W * 0.74, H * 0.2, D * 0.82 + (0.8 if underbite else 0), 'bone_d')
    cb(jaw, cx, jy + H * 0.2 - 0.05, jw_z + (0.35 if not underbite else -0.1), W * 0.58, H * 0.14, 0.6, 'tooth', decals={'north': teeth_dec})  # lower teeth
    return head


def ribcage(bone, cx, y0, cz, w, h, d):
    cb(bone, cx, y0, cz + d * 0.3, 1.0, h, 1.0, 'bone_d')                                   # spine
    cb(bone, cx, y0 + h * 0.2, cz - d / 2, 0.9, h * 0.8, 0.5, 'bone')                        # sternum
    for i in range(3):
        y = y0 + h * (0.12 + 0.3 * i)
        ww = w * (0.82 + 0.09 * i)
        cb(bone, cx, y, cz - d / 2 + 0.05, ww, 0.6, 0.55, 'bone')
        cb(bone, cx, y, cz + d / 2 - 0.25, ww * 0.6, 0.6, 0.5, 'bone_d')
        for sx in (1, -1):
            cb(bone, cx + sx * (ww / 2 - 0.3), y, cz, 0.6, 0.6, d, 'bone')
    cb(bone, cx, y0 + h, cz, w * 0.95, 0.7, d * 0.7, 'bone')                                  # collarbone


def bone_arm(bone, x, ytop, z, L, t=0.9, fingers=True, down=True):
    """humerus + elbow + twin forearm bones + hand (hanging down from ytop)"""
    u = L * 0.46
    cb(bone, x, ytop - 1.0, z, t + 0.6, 1.0, t + 0.6, 'bone_d')
    cb(bone, x, ytop - 1.0 - u, z, t, u, t, 'bone')
    cb(bone, x, ytop - 1.4 - u, z, t + 0.5, 0.8, t + 0.5, 'bone_d')
    for dz in (-0.3, 0.3):
        cb(bone, x, ytop - 1.2 - L * 0.9, z + dz, t * 0.55, L * 0.44, t * 0.55, 'bone')
    hy = ytop - 1.4 - L * 0.95
    cb(bone, x, hy, z, t + 0.5, 1.0, t + 0.8, 'bone_d')
    if fingers:
        for dz in (-0.5, 0.0, 0.5):
            cb(bone, x, hy - 0.9, z + dz - 0.2, 0.5, 0.9, 0.4, 'bone')
    return hy


def bone_leg(bone, x, ytop, z, L, t=1.0):
    u = L * 0.45
    cb(bone, x, ytop - 1.0, z, t + 1.0, 1.0, t + 0.6, 'bone_d')                               # hip joint
    cb(bone, x, ytop - 1.0 - u, z, t, u, t, 'bone')
    cb(bone, x, ytop - 1.4 - u, z, t + 0.6, 0.9, t + 0.6, 'bone_d')                           # knee
    cb(bone, x, 1.0, z, t * 0.85, ytop - 2.4 - u, t * 0.85, 'bone')
    cb(bone, x, 0, z - 0.5, t + 1.0, 1.0, t + 2.2, 'bone_d')                                  # foot
    for dx in (-0.45, 0.45):
        cb(bone, x + dx, 0, z - 2.0, 0.6, 0.7, 0.8, 'bone')                                   # toes


# ------------------------------------------------------------------- elixir collector HQ
def elixir_collector():
    m = Model('clash_elixir_collector', density=2.0)
    m.mats_({
        'plank': ('#9c6a36', 'wood', {'planks': True}), 'stave': ('#946030', 'wood', {'grain': 'v'}), 'stave_d': ('#6b4220', 'wood', {'grain': 'v'}),
        'wood': ('#7a4a22', 'wood'), 'wood_l': ('#b07a40', 'wood'), 'iron': ('#4a5260', 'metal', {'rivets': True}), 'iron_d': ('#30363f', 'metal'),
        'copper': ('#cf7a3c', 'metal'), 'copper_d': ('#9a5426', 'metal'),
        'elx': ('#ff50e6', 'gem'), 'elx_l': ('#ff9af5', 'gem'), 'glow': ('#ffb8fb', 'glow'), 'glass': ('#e8f4ff', 'gem'),
        'bubble': ('#ffe6ff', 'glow'), 'band': ('#efefef', 'metal'), 'stone': ('#8f8a80', 'brick', {'bh': 3, 'bw': 6}), 'stone_l': ('#aaa498', 'stone'),
    })
    staves = [('rect', x, 0.0, x + 0.03, 1.0, '#4a2c12') for x in (0.18, 0.36, 0.54, 0.72, 0.9)] + [('shade', 0.0, 0.8, 1.0, 1.0, 0.8)]
    drop = [('rect', 0.44, 0.15, 0.56, 0.3, '#7a7a7a'), ('rect', 0.36, 0.3, 0.64, 0.75, '#7a7a7a'), ('rect', 0.42, 0.75, 0.58, 0.85, '#7a7a7a'),
            ('rect', 0.4, 0.38, 0.47, 0.5, '#ffffff')]
    root = m.bone('root', [0, 0, 0])
    frame = m.bone('frame', [0, 0, 0], root)
    oct_(frame, 0, 0, 0, 40, 2.2, 'stone')
    for (x, z) in ((15, 15), (-15, 15), (15, -15), (-15, -15)):
        cb(frame, x, 0, z, 4, 3, 4, 'stone_l')
    oct_(frame, 0, 2.2, 0, 35, 2.2, 'plank')
    tcb = m.bone('tc_seal_base', [0, 5, 0], frame)
    oct_(tcb, 0, 4.4, 0, 29, 2.4, 'band', dec={'north': drop, 'east': drop, 'west': drop, 'south': drop})
    oct_(frame, 0, 6.8, 0, 25, 6.2, 'stave', dec={f: staves for f in ('north', 'south', 'east', 'west')})
    oct_(frame, 0, 7.6, 0, 25.6, 1.0, 'iron_d')
    oct_(frame, 0, 12.0, 0, 25.6, 1.0, 'iron')
    for (x, z) in ((9.4, 9.4), (-9.4, 9.4), (9.4, -9.4), (-9.4, -9.4)):        # carved posts
        cb(frame, x, 13, z, 2.6, 18, 2.6, 'wood', decals={f: [('rect', 0.0, 0.48, 1.0, 0.52, '#4a2c12')] for f in ('north', 'south', 'east', 'west')})
        cb(frame, x, 13, z, 3.4, 1.2, 3.4, 'iron_d')
        cb(frame, x, 29.8, z, 3.4, 1.2, 3.4, 'iron_d')
    # pipe + valve
    cb(frame, 15.2, 4.4, 0, 2.8, 28, 2.8, 'copper', decals={f: [('rect', 0.0, y, 1.0, y + 0.03, '#9a5426') for y in (0.25, 0.5, 0.75)] for f in ('east', 'north', 'south')})
    for y in (7.0, 31.0):
        cb(frame, 13.2, y, 0, 4.8, 2.6, 2.6, 'copper')
        cb(frame, 11.2, y - 0.3, 0, 1.0, 3.2, 3.2, 'copper_d')
    cb(frame, 15.2, 17.6, 0, 3.6, 2.4, 3.6, 'copper_d')
    lev = m.bone('lever', [17.6, 18.8, 0], frame)
    cb(lev, 17.2, 18.2, 0, 1.2, 1.2, 1.2, 'iron')
    cb(lev, 17.8, 18.5, 0, 0.7, 0.7, 7.4, 'wood_l')
    cb(lev, 17.8, 15.1, 0, 0.7, 7.4, 0.7, 'wood_l')
    for (dy, dz, h, d) in ((3.6, 0, 0.9, 6.6), (-3.6, 0, 0.9, 6.6), (0, 3.6, 6.6, 0.9), (0, -3.6, 6.6, 0.9)):
        cb(lev, 18.0, 18.85 + dy - h / 2, dz, 1.1, h, d, 'wood')
    cb(lev, 18.8, 21.6, 0, 1.2, 1.6, 1.2, 'wood_l')
    # glass vat
    tank = m.bone('tank', [0, 13, 0], root)
    gloss = [('rect', 0.1, 0.04, 0.18, 0.92, '#ffe8ff'), ('rect', 0.24, 0.04, 0.28, 0.55, '#ffe0ff'), ('rect', 0.7, 0.3, 0.76, 0.36, '#ffc8fb'),
             ('rect', 0.55, 0.8, 0.85, 0.86, '#c02ac8'), ('shade', 0.0, 0.85, 1.0, 1.0, 0.85)]
    oct_(tank, 0, 13.6, 0, 16, 16.8, 'elx', dec={f: gloss for f in ('north', 'south', 'east', 'west')})
    oct_(tank, 0, 13, 0, 17.6, 1.0, 'glass')
    oct_(tank, 0, 30.0, 0, 17.6, 1.0, 'glass')
    oct_(tank, 0, 27.6, 0, 16.3, 0.8, 'elx_l')                                   # liquid surface line
    core = m.bone('glow_core', [0, 22, 0], tank)
    oct_(core, 0, 14.6, 0, 15.2, 14.8, 'glow')
    for nm, pts in (('bubbles_a', ((-2.5, -8.1), (8.1, 2), (2, 8.1), (-8.1, -1))), ('bubbles_b', ((2.5, -8.1), (-8.1, 2.5), (-2.5, 8.1), (8.1, -2.5)))):
        bb = m.bone(nm, [0, 16, 0], tank)
        for (x, z) in pts:
            cb(bb, x, 15.5, z, 1.6, 1.6, 1.6, 'bubble')
            cb(bb, x * 0.7, 18.2, z * (1.0 if abs(z) > 7 else 0.7), 1.0, 1.0, 1.0, 'bubble')
            cb(bb, x * 1.0, 20.6, z, 0.7, 0.7, 0.7, 'bubble')
    # lid
    top = m.bone('lid', [0, 31, 0], root)
    oct_(top, 0, 31.0, 0, 25.6, 1.2, 'iron')
    oct_(top, 0, 32.2, 0, 23.4, 4.6, 'stave', dec={f: staves for f in ('north', 'south', 'east', 'west')})
    oct_(top, 0, 34.6, 0, 24, 0.8, 'iron_d')
    tct = m.bone('tc_seal_top', [0, 37, 0], top)
    oct_(tct, 0, 36.8, 0, 18, 2.2, 'band', dec={'north': drop, 'south': drop, 'east': drop, 'west': drop})
    oct_(top, 0, 39, 0, 10, 1.4, 'wood_l')
    oct_(top, 0, 40.4, 0, 6, 1.2, 'iron')
    cb(top, 0, 41.6, 0, 2.4, 1.8, 2.4, 'copper')
    cb(top, 0, 43.4, 0, 3.6, 0.8, 3.6, 'copper_d')
    shards = m.bone('shards', [0, 22, 0], root)
    for (x, z) in ((-3.5, -3.5), (3.5, -3.5), (3.5, 3.5), (-3.5, 3.5)):
        cb(shards, x, 18, z, 3.6, 4, 1.2, 'elx_l')
        cb(shards, x * 0.5, 23, z * 0.5, 3, 3, 0.8, 'glass')
    pud = m.bone('puddle', [0, 12, 0], root)
    oct_(pud, 0, 11.4, 0, 22, 1.2, 'elx')
    m.hitbox(2.6, 2.6)
    m.anim('idle', 1.2, 'loop', {'lever': {'rotation': [(0, [0, 0, 0]), (1.2, [90, 0, 0])]},
                                 'tank': {'scale': [(0, S(1)), (0.6, [1.015, 1.02, 1.015]), (1.2, S(1))]},
                                 'bubbles_a': {'position': [(0, [0, 0, 0]), (1.2, [0, 9, 0])], 'scale': [(0, S(1)), (1.2, S(0.2))]},
                                 'bubbles_b': {'position': [(0, [0, 4.5, 0]), (0.6, [0, 9, 0]), (0.61, [0, 0, 0]), (1.2, [0, 4.5, 0])],
                                               'scale': [(0, S(0.6)), (0.6, S(0.2)), (0.61, S(1)), (1.2, S(0.6))]}}, interp='linear')
    m.anim('attack', 0.6, 'once', {
        'glow_core': {'scale': [(0, S(1)), (0.18, [1.16, 1.08, 1.16]), (0.3, [1.12, 1.06, 1.12]), (0.6, S(1))]},
        'tank': {'scale': [(0, S(1)), (0.18, [1.06, 1.05, 1.06]), (0.32, [0.97, 0.97, 0.97]), (0.6, S(1))]},
        'lid': {'position': [(0, [0, 0, 0]), (0.18, [0, 1.4, 0]), (0.32, [0, -0.3, 0]), (0.6, [0, 0, 0])]},
        'lever': {'rotation': [(0, [0, 0, 0]), (0.3, [180, 0, 0]), (0.6, [360, 0, 0])]},
        'bubbles_a': {'position': [(0, [0, 0, 0]), (0.6, [0, 9, 0])], 'scale': [(0, S(1.4)), (0.6, S(0.2))]}})
    m.anim('spawn', 0.6, 'once', {'root': {'position': [(0, [0, 24, 0]), (0.28, [0, 0, 0]), (0.4, [0, 1.2, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, S(0.6)), (0.28, [1.1, 0.86, 1.1]), (0.4, [0.97, 1.04, 0.97]), (0.6, S(1))]}})
    building_hit(m)
    m.anim('death', 0.9, 'hold', {
        'tank': {'scale': [(0, S(1)), (0.08, S(1.05)), (0.14, [0.98, 1.03, 0.98]), (0.18, S(1.12)), (0.2, S(0.01)), (0.9, S(0.01))]},
        'shards': {'scale': [(0, S(1)), (0.18, S(1)), (0.3, S(2.0)), (0.75, S(0.9))],
                   'position': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.45, [0, 6, 0]), (0.75, [0, -8, 0])],
                   'rotation': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.75, [30, 90, 20])]},
        'lid': {'position': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.35, [0, 4, 0]), (0.7, [-3, -16, 2])],
                'rotation': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.7, [10, 0, 35])]},
        'puddle': {'position': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.3, [0, 1.4, 0])], 'scale': [(0, S(1)), (0.5, [1.05, 1, 1.05])]},
        'frame': {'rotation': [(0, [0, 0, 0]), (0.25, [0, 0, 2]), (0.4, [0, 0, -1]), (0.55, [0, 0, 0])]}})
    return m


# ------------------------------------------------------------------- guard HQ
def guard():
    m = Model('clash_guard', density=3.0)
    m.mats_(dict(HQ_BONE, **{'helm': ('#2e3440', 'metal', {'rivets': True}), 'helm_l': ('#4a5464', 'metal'), 'helm_d': ('#1e232c', 'metal'),
                             'wood': ('#7a4a22', 'wood'), 'wood_l': ('#a06a34', 'wood'), 'shield': ('#a4682f', 'wood', {'planks': True, 'grain': 'v'}),
                             'iron': ('#3c424c', 'metal'), 'steel': ('#d0d4dc', 'metal'), 'gold': ('#f2c23a', 'metal'), 'leather': ('#5a3a1e', 'leather'),
                             'feather': ('#efefef', 'cloth')}))
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.7, 5.8, 0], root)
        bone_leg(lg, sx * 1.7, 5.8, 0, 5.0, 1.0)
    body = m.bone('body', [0, 6, 0], root)
    cb(body, 0, 5.4, 0, 4.8, 1.4, 2.6, 'bone_d')                                   # pelvis
    cb(body, 0, 6.8, 0.6, 1.0, 1.4, 1.0, 'bone_d')
    ribcage(body, 0, 7.4, 0, 5.4, 3.4, 3.2)
    cb(body, -0.6, 8.2, 0, 7.0, 0.7, 4.0, 'leather', rot=('z', 45))               # spear-carrier strap
    head = skull_hq(m, body, 'head', 0, 12.6, -0.3, 7.2, underbite=True)
    # black helmet: rounded dome + brim + nasal guard + cheek guards + rivets
    cb(head, 0, 17.2, -0.2, 8.2, 2.4, 7.8, 'helm', decals={'north': [('px', 0.15, 0.6, '#8a94a4'), ('px', 0.85, 0.6, '#8a94a4')]})
    cb(head, 0, 19.6, 0.0, 7.0, 1.2, 6.6, 'helm')
    cb(head, 0, 20.8, 0.2, 5.0, 0.7, 4.8, 'helm_l')
    cb(head, 0, 16.6, -0.2, 8.8, 0.9, 8.4, 'helm_l')                               # brim band
    cb(head, 0, 14.6, -4.6, 1.6, 3.4, 0.7, 'helm', decals={'north': [('rect', 0.2, 0.0, 0.4, 1.0, '#5a6474')]})   # wide nasal guard
    for sx in (1, -1):
        cb(head, sx * 4.0, 11.4, 0.0, 0.8, 5.0, 6.6, 'helm', decals={'east' if sx > 0 else 'west': [('px', 0.2, 0.2, '#8a94a4'), ('px', 0.2, 0.8, '#8a94a4')]})
        cb(head, sx * 3.3, 11.4, -3.1, 1.6, 4.2, 0.8, 'helm')                       # cheek plates forward
    cb(head, 0, 21.4, 0.6, 1.6, 0.8, 1.6, 'helm_d')
    fe = m.bone('tc_feather', [0, 22, 0.6], head)                                # team plume: 3 tapered pieces
    cb(fe, 0, 22.0, 0.4, 1.3, 2.4, 2.6, 'feather')
    cb(fe, 0, 24.0, 1.6, 1.1, 1.8, 2.6, 'feather', rot=('x', -22.5))
    cb(fe, 0, 24.6, 3.6, 0.8, 1.2, 2.2, 'feather', rot=('x', -45))
    ar = m.bone('arm_r', [3.4, 10.6, 0], body)
    hy = bone_arm(ar, 3.6, 10.8, 0, 4.4, 0.8)
    sp = m.bone('spear', [3.6, hy + 0.4, -1], ar)
    cb(sp, 3.6, hy, -3.4, 0.8, 0.8, 17, 'wood', decals={'east': [('rect', 0.5, 0.0, 0.62, 1.0, '#5a3418')]})
    cb(sp, 3.6, hy - 0.15, 3.0, 1.1, 1.1, 2.4, 'leather')                           # grip wrap
    cb(sp, 3.6, hy - 0.2, -11.8, 1.2, 1.2, 1.0, 'iron')                             # collar
    cb(sp, 3.6, hy - 0.5, -13.8, 0.6, 1.8, 3.0, 'steel')                            # leaf blade
    cb(sp, 3.6, hy - 0.2, -15.6, 0.6, 1.2, 1.0, 'steel')
    cb(sp, 3.6, hy + 0.05, -16.5, 0.6, 0.6, 0.8, 'steel')
    al = m.bone('arm_l', [-3.4, 10.6, 0], body)
    bone_arm(al, -3.6, 10.8, -0.6, 4.0, 0.8, fingers=False)
    sh = m.bone('shield', [-1.2, 8.2, -3.8], al)
    S0, Y0, Z0 = 10.4, 1.6, -4.2
    cb(sh, -1.2, Y0 + S0 * 0.2, Z0, S0, S0 * 0.6, 1.0, 'shield')
    cb(sh, -1.2, Y0, Z0, S0 * 0.6, S0, 1.0, 'shield')
    cb(sh, -1.2, Y0 + S0 * 0.07, Z0 - 0.05, S0 * 0.86, S0 * 0.86, 1.1, 'shield', decals={'north': [('shade', 0.0, 0.0, 1.0, 0.15, 1.12), ('shade', 0.0, 0.85, 1.0, 1.0, 0.8)]})
    cx, cy, zr = -1.2, Y0 + S0 / 2, Z0 - 0.7                                        # iron rim (8 segments)
    R0 = S0 / 2 - 0.4
    for (dx, dy, w, h, rr) in ((0, R0, S0 * 0.42, 0.8, 0), (0, -R0, S0 * 0.42, 0.8, 0), (R0, 0, 0.8, S0 * 0.42, 0), (-R0, 0, 0.8, S0 * 0.42, 0),
                               (R0 * 0.71, R0 * 0.71, S0 * 0.42, 0.8, -45), (-R0 * 0.71, R0 * 0.71, S0 * 0.42, 0.8, 45),
                               (R0 * 0.71, -R0 * 0.71, S0 * 0.42, 0.8, 45), (-R0 * 0.71, -R0 * 0.71, S0 * 0.42, 0.8, -45)):
        cb(sh, cx + dx, cy + dy - h / 2, zr, w, h, 0.6, 'iron', rot=('z', rr) if rr else None)
    # 3D gold crown emblem
    cb(sh, cx, cy - 1.6, zr - 0.1, 4.4, 1.2, 0.5, 'gold')
    for (dx, hh) in ((-1.8, 1.6), (0, 2.2), (1.8, 1.6)):
        cb(sh, cx + dx, cy - 0.4, zr - 0.1, 0.8, hh, 0.5, 'gold')
    cb(sh, cx, cy - 1.4, zr - 0.35, 0.6, 0.6, 0.3, 'socket')
    m.hitbox(0.8, 1.6)
    m.anim('idle', 2.0, 'loop', {'body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.0)},
                                 'head': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 2.0)},
                                 'head_jaw': {'rotation': loop([[0, 0, 0], [4, 0, 0]], 1.0)},
                                 'tc_feather': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 1.0)},
                                 'arm_r': {'rotation': loop([[0, 0, 0], [-4, 0, 0]], 2.0)}})
    L = 0.6
    m.anim('walk', L, 'loop', {'leg_r': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], L)},
                               'arm_r': {'rotation': loop([[-8, 0, 0], [8, 0, 0]], L)},
                               'tc_feather': {'rotation': loop([[-10, 0, 0], [6, 0, 0]], L / 2)},
                               'body': {'position': loop([[0, 0, 0], [0, 0.6, 0], [0, 0, 0], [0, 0.6, 0]], L), 'rotation': [(0, [6, 0, 0]), (L, [6, 0, 0])]}})
    m.anim('attack', 0.5, 'once', {
        'spear': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.3, 3]), (0.25, [0, 0, -5]), (0.33, [0, 0, -4.5]), (0.5, [0, 0, 0])]},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [20, 0, 0]), (0.25, [-20, 0, 0]), (0.5, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.15, [-8, 12, 0]), (0.25, [12, -10, 0]), (0.5, [0, 0, 0])]},
        'head_jaw': {'rotation': [(0, [0, 0, 0]), (0.25, [14, 0, 0]), (0.5, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.25, [-20, 0, 0]), (0.5, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (0.25, [15, 0, 0]), (0.5, [0, 0, 0])]}})
    common_tail(m, death={'body': {'rotation': [(0, [0, 0, 0]), (0.5, [-70, 0, 10]), (0.9, [-85, 0, 10])], 'position': [(0, [0, 0, 0]), (0.9, [0, -5, 3])]},
                          'head': {'position': [(0, [0, 0, 0]), (0.5, [1, -2, 0]), (0.9, [3, -8, -2])], 'rotation': [(0, [0, 0, 0]), (0.9, [30, 0, 60])]},
                          'leg_r': {'rotation': [(0, [0, 0, 0]), (0.6, [-30, 0, 20])]}, 'leg_l': {'rotation': [(0, [0, 0, 0]), (0.6, [-30, 0, -20])]}})
    return m


# ------------------------------------------------------------------- wall breaker HQ
def wall_breaker():
    m = Model('clash_wall_breaker', density=3.0)
    m.mats_(dict(HQ_BONE, **{'keg': ('#b06a30', 'wood', {'grain': 'v'}), 'keg_l': ('#c8803c', 'wood', {'grain': 'v'}), 'keg_d': ('#7a4620', 'wood'),
                             'iron': ('#3a3e46', 'metal', {'rivets': True}), 'fuse': ('#7a6040', 'rope'), 'spark': ('#ffd04a', 'glow'),
                             'flame': ('#ff8a1e', 'glow'), 'rope': ('#c8a870', 'rope')}))
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.3, 3.8, 0], root)
        bone_leg(lg, sx * 1.3, 3.8, 0, 3.4, 0.8)
    body = m.bone('body', [0, 3.8, 0], root)
    cb(body, 0, 3.4, 0, 3.8, 1.0, 2.2, 'bone_d')
    ribcage(body, 0, 4.4, 0, 4.2, 2.6, 2.6)
    head = skull_hq(m, body, 'head', 0, 8.6, -0.2, 6.6, open_mouth=True)
    tcb = m.bone('tc_bandana', [0, 13, 0], head)
    cb(tcb, 0, 12.6, -0.1, 7.2, 1.8, 6.6, 'band', decals={'north': [('px', 0.3, 0.5, '#bdbdbd'), ('px', 0.7, 0.4, '#bdbdbd')]})
    cb(tcb, 0, 14.4, 0.4, 6.0, 0.9, 5.4, 'band')
    cb(tcb, 0, 12.6, 3.4, 1.6, 1.6, 0.8, 'band')                                    # knot
    cb(tcb, 0.9, 10.6, 3.6, 1.2, 2.4, 0.5, 'band', rot=('z', 22.5))                 # knot tails
    cb(tcb, -0.9, 10.8, 3.6, 1.2, 2.0, 0.5, 'band', rot=('z', -22.5))
    for sx, side in ((1, 'r'), (-1, 'l')):                                          # arms raised holding the barrel
        a = m.bone('arm_' + side, [sx * 2.4, 7.2, 0], body)
        cb(a, sx * 2.4, 6.6, 0, 1.3, 1.3, 1.3, 'bone_d')
        cb(a, sx * 3.4, 7.4, 0, 0.8, 3.4, 0.8, 'bone')
        cb(a, sx * 3.6, 10.6, 0, 1.3, 0.8, 1.3, 'bone_d')
        for dz in (-0.25, 0.25):
            cb(a, sx * 3.8, 11.2, dz, 0.45, 3.4, 0.45, 'bone')
        cb(a, sx * 3.8, 14.4, 0, 1.4, 1.0, 1.6, 'bone_d')
        for dz in (-0.5, 0.0, 0.5):
            cb(a, sx * 3.2, 15.2, dz, 0.9, 0.5, 0.4, 'bone')
    bomb = m.bone('bomb', [0, 19.4, 0], body)
    hoop_dec = [('shade', 0.0, 0.0, 1.0, 0.2, 1.1), ('shade', 0.0, 0.8, 1.0, 1.0, 0.8)]
    oct_(bomb, 0, 19.6, 0, 8.4, 9.6, 'keg', axis='x', dec={'north': hoop_dec, 'south': hoop_dec, 'up': hoop_dec})
    oct_(bomb, 0, 19.6, 0, 7.6, 11.0, 'keg_d', axis='x')                           # end caps
    for x in (-3.6, 3.6, 0):
        oct_(bomb, x, 19.6, 0, 8.9, 0.9 if x else 0.6, 'iron' if x else 'rope', axis='x')
    for sx in (1, -1):
        cb(bomb, sx * 5.55, 18.6, 0, 0.3, 2.0, 2.0, 'keg_l')                       # end plate
    cb(bomb, 0, 23.8, 0, 1.8, 0.7, 1.8, 'iron')
    cb(bomb, 0.3, 24.4, 0, 0.7, 1.8, 0.7, 'fuse', rot=('z', -22.5))
    spk = m.bone('spark', [1.0, 26.6, 0], bomb)
    cb(spk, 1.0, 26.0, 0, 1.4, 1.4, 1.4, 'spark')
    cb(spk, 1.0, 26.3, 0, 2.4, 0.6, 0.6, 'flame')
    cb(spk, 1.0, 26.3, 0, 0.6, 0.6, 2.4, 'flame')
    m.hitbox(0.6, 1.1)
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, -0.4, 0]], 0.8)},
                                 'bomb': {'rotation': loop([[0, 0, 3], [0, 0, -3]], 0.8)},
                                 'spark': {'scale': loop([S(1), S(1.6), S(0.8), S(1.4)], 0.8)},
                                 'head': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 0.8)},
                                 'head_jaw': {'rotation': loop([[0, 0, 0], [8, 0, 0]], 0.4)}})
    L = 0.3
    m.anim('walk', L, 'loop', {'leg_r': {'rotation': loop([[50, 0, 0], [-50, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-50, 0, 0], [50, 0, 0]], L)},
                               'body': {'rotation': [(0, [14, 0, 0]), (L, [14, 0, 0])],
                                        'position': loop([[0, 0, 0], [0, 1.0, 0], [0, 0, 0], [0, 1.0, 0]], L)},
                               'bomb': {'rotation': loop([[-6, 0, 4], [-6, 0, -4]], L)},
                               'head_jaw': {'rotation': loop([[0, 0, 0], [12, 0, 0]], L)},
                               'spark': {'scale': loop([S(1), S(1.7), S(0.8), S(1.5)], L)}})
    m.anim('attack', 0.3, 'once', {
        'root': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.2, [0, 3, -7]), (0.3, [0, 1, -9])],
                 'rotation': [(0, [0, 0, 0]), (0.08, [-12, 0, 0]), (0.2, [35, 0, 0]), (0.3, [50, 0, 0])]},
        'bomb': {'scale': [(0, S(1)), (0.2, S(1.15)), (0.3, S(1.35))]},
        'spark': {'scale': [(0, S(1)), (0.3, S(2.5))]}})
    common_tail(m, death={'root': {'rotation': [(0, [0, 0, 0]), (0.5, [0, 0, 80]), (0.9, [0, 0, 90])],
                                   'position': [(0, [0, 0, 0]), (0.9, [0, -3, 0])]},
                          'bomb': {'position': [(0, [0, 0, 0]), (0.5, [3, -6, 0]), (0.9, [4, -9, 0])], 'scale': [(0, S(1)), (0.7, S(1)), (0.9, S(0.01))]}})
    return m


# ------------------------------------------------------------------- boulder HQ
def boulder():
    m = Model('clash_boulder', density=2.5)
    m.mats_(BOULDER_MATS)
    root = m.bone('root', [0, 0, 0])
    bo = m.bone('boulder', [0, 9.6, 0], root)
    sphere(bo, 0, 9.6, 0, 9.6, ['rock_d', 'rock', 'rock_l', 'rock', 'rock_l', 'rock', 'rock_d', 'rock'], n=9, dec=CRACKS)
    for (x, y, z, w) in ((5.5, 14, -5, 3.4), (-6, 6, -4.5, 3.0), (2, 4, 7, 3.6), (-4, 15, 5, 3.0), (7.5, 7, 3, 2.6)):   # lumps
        cb(bo, x, y - w / 2, z, w, w, w, 'rock_l', decals={'north': CRACKS[:2]})
    m.hitbox(1.2, 1.2)
    roll = {'boulder': {'rotation': [(0, [0, 0, 0]), (0.15, [90, 0, 0]), (0.3, [180, 0, 0]), (0.45, [270, 0, 0]), (0.6, [360, 0, 0])]}}
    m.anim('roll', 0.6, 'loop', roll, interp='linear')
    m.anim('idle', 0.6, 'loop', roll, interp='linear')
    return m


# ------------------------------------------------------------------- bowler HQ
def bowler():
    m = Model('clash_bowler', density=2.0)
    m.mats_(dict(BOULDER_MATS, **{
        'skin': ('#7774e6', 'skin'), 'skin_d': ('#5d5ac8', 'skin'), 'skin_l': ('#8f8cf2', 'skin'), 'nose': ('#a48cf0', 'skin'),
        'loin': ('#c8a878', 'leather', {'stitch': False}), 'belt': ('#7a5530', 'leather'), 'band': ('#efefef', 'cloth'),
        'nail': ('#d8d8f0', 'bone'), 'white': ('#fff6dc', 'plain'), 'mouth': ('#2a1a40', 'plain'), 'tooth': ('#fbf6e6', 'bone'),
        'buckle': ('#d8a838', 'metal')}))
    mus = [('rect', 0.48, 0.1, 0.52, 0.85, '#5d5ac8'), ('rect', 0.12, 0.6, 0.45, 0.65, '#5d5ac8'), ('rect', 0.55, 0.6, 0.88, 0.65, '#5d5ac8'),
           ('rect', 0.15, 0.1, 0.35, 0.16, '#a8a6fa'), ('shade', 0.0, 0.85, 1.0, 1.0, 0.85)]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 5.5, 12, 0], root)
        cb(lg, sx * 5.5, 6.6, 0.5, 7.8, 6.2, 8.2, 'skin')                          # thigh
        cb(lg, sx * 5.5, 2.4, 0.5, 6.8, 4.6, 7.2, 'skin')                          # shin
        cb(lg, sx * 5.5, 0, -0.6, 8.6, 2.8, 9.8, 'skin_d')                         # foot
        for dx in (-2.6, 0, 2.6):
            cb(lg, sx * 5.5 + dx, 0, -5.8, 2.2, 1.8, 1.4, 'skin_d')                # toes
            cb(lg, sx * 5.5 + dx, 0.9, -6.6, 1.2, 0.7, 0.3, 'nail')
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 11.4, 0.5, 19, 5, 13.4, 'skin_d')                                  # hips
    cb(body, 0, 15.0, 0.5, 20.4, 2.6, 14.4, 'belt', decals={'north': [('rect', 0.0, 0.4, 1.0, 0.5, '#5a3a20')]})
    cb(body, 0, 15.0, -6.9, 3.4, 2.8, 0.8, 'buckle')
    cb(body, 0, 7.6, -7.4, 8.4, 7.6, 0.8, 'loin', decals={'north': [('rect', 0.0, 0.85, 0.2, 1.0, '#a08458'), ('rect', 0.8, 0.85, 1.0, 1.0, '#a08458'),
                                                                     ('rect', 0.1, 0.0, 0.9, 0.06, '#a08458')]})
    cb(body, 0, 7.6, 7.4, 9.4, 7.6, 0.8, 'loin')
    cb(body, 0, 17.4, 0.6, 20, 10, 14, 'skin', decals={'north': mus})             # chest + belly
    cb(body, 0, 15.8, -5.6, 14, 6, 3, 'skin_l', decals={'north': [('rect', 0.48, 0.3, 0.52, 0.5, '#5d5ac8')]})   # gut
    for sx in (1, -1):
        cb(body, sx * 4.8, 21.4, -6.6, 8.6, 4.4, 2.4, 'skin_l')                   # pecs
    cb(body, 0, 26.6, 2.4, 25, 6, 14, 'skin_l', decals={'north': mus[3:], 'up': mus[3:]})   # hunched shoulder mass
    cb(body, 0, 31.6, 4, 18, 3, 10, 'skin')                                        # trapezius hump
    for sx in (1, -1):
        cb(body, sx * 11.4, 27.0, 1.6, 6, 6.6, 12, 'skin')                         # deltoid rounding
    head = m.bone('head', [0, 31, -5], body)
    eye = [('rect', 0.0, 0.0, 1.0, 1.0, '#fff4d8'), ('rect', 0.3, 0.05, 0.85, 0.95, '#2f8fff'), ('rect', 0.42, 0.25, 0.72, 0.8, '#0a1430'),
           ('rect', 0.45, 0.15, 0.58, 0.4, '#ffffff'), ('rect', 0.0, 0.0, 1.0, 0.2, '#5d5ac8')]
    cb(head, 0, 29.4, -7.6, 10.4, 9.2, 9, 'skin', decals={'north': [('rect', 0.1, 0.62, 0.3, 0.72, '#9a8cf4'), ('rect', 0.7, 0.62, 0.9, 0.72, '#9a8cf4')],
                                                         'up': [('rect', 0.3, 0.3, 0.55, 0.5, '#a8a6fa')]})
    cb(head, 0, 38.6, -7.4, 8.6, 1.3, 7.4, 'skin', decals={'up': [('rect', 0.25, 0.25, 0.55, 0.5, '#b4b2ff')]})   # dome
    cb(head, 0, 31.0, -7.6, 11.2, 5.4, 7.6, 'skin')                                 # cheeks / wide face
    cb(head, 0, 35.2, -12.2, 10.6, 1.6, 1.8, 'skin_d')                              # heavy brow
    cb(head, 0, 36.6, -11.8, 8.6, 0.8, 1.0, 'skin', decals={'north': [('rect', 0.1, 0.4, 0.9, 0.6, '#6866d8')]})   # forehead wrinkle
    for sx in (1, -1):
        cb(head, sx * 2.8, 33.1, -12.15, 3.0, 2.0, 0.4, 'white', decals={'north': eye if sx > 0 else [(k[0], 1 - k[3], k[2], 1 - k[1], k[4], k[5]) if k[0] == 'rect' and False else k for k in eye]})
        cb(head, sx * 2.8, 34.8, -12.3, 3.4, 0.6, 0.6, 'skin_d')                    # upper eyelid
        cb(head, sx * 3.8, 30.6, -11.9, 3.0, 2.6, 1.2, 'skin_l')                    # smiling cheeks
    # big bulbous drooping nose
    cb(head, 0, 31.4, -12.8, 2.8, 3.4, 1.8, 'nose')
    cb(head, 0, 29.2, -14.4, 4.8, 3.8, 3.6, 'nose', decals={'north': [('rect', 0.2, 0.1, 0.45, 0.3, '#c4b4ff')], 'down': [('rect', 0.15, 0.3, 0.4, 0.7, '#5a4aa8'), ('rect', 0.6, 0.3, 0.85, 0.7, '#5a4aa8')]})
    cb(head, 0, 29.6, -16.3, 3.6, 2.8, 0.6, 'nose')
    for sx in (1, -1):
        cb(head, sx * 2.6, 29.2, -13.6, 1.2, 2.0, 2.0, 'nose')                       # nostril wings
    # confident smirk: dark mouth line rising to one side, two buck teeth
    cb(head, 0, 25.8, -8.8, 9.8, 3.6, 7.6, 'skin')                                  # lower face
    cb(head, -0.4, 27.2, -12.75, 6.4, 0.9, 0.3, 'mouth')
    cb(head, 3.2, 27.7, -12.75, 1.6, 0.9, 0.3, 'mouth')
    cb(head, 4.3, 28.3, -12.75, 1.2, 0.8, 0.3, 'mouth')
    cb(head, -3.7, 27.0, -12.7, 0.8, 0.8, 0.3, 'skin_d')                            # dimple on the low side
    for x in (0.0, 1.3):
        cb(head, x, 26.3, -12.9, 1.2, 1.3, 0.4, 'tooth')
    cb(head, 0, 24.0, -9.6, 9.2, 2.4, 6.6, 'skin')                                  # big jaw
    cb(head, 0, 24.0, -12.3, 6.0, 2.2, 1.4, 'skin_l')                               # chin
    for sx in (1, -1):                                                              # big pointy ears (up and back)
        cb(head, sx * 5.8, 30.0, -6.4, 1.6, 4.4, 3.2, 'skin')
        cb(head, sx * 7.6, 31.2, -6.0, 4.4, 4.2, 1.2, 'skin_l', rot=('z', sx * 22.5), decals={'north': [('rect', 0.2, 0.25, 0.8, 0.75, '#c49af0')]})
        cb(head, sx * 9.8, 34.0, -5.8, 2.4, 2.4, 1.0, 'skin_l', rot=('z', sx * 45))
        cb(head, sx * 10.9, 35.8, -5.6, 1.0, 1.4, 0.8, 'skin_l', rot=('z', sx * 45))
        cb(head, sx * 6.4, 29.0, -7.0, 0.6, 1.0, 0.6, 'nail')                         # ear stud
    for sx, side in ((1, 'r'), (-1, 'l')):                                          # arms in the carry pose
        a = m.bone('arm_' + side, [sx * 14, 30, 1], body)
        cb(a, sx * 16, 24.6, 1.5, 8.8, 8.6, 9.4, 'skin_l', decals={'north': mus[3:]})
        cb(a, sx * 16, 18.2, -0.5, 7.6, 7, 8, 'skin')
        tca = m.bone('tc_band_' + side, [sx * 16, 22, 0], a)
        cb(tca, sx * 16, 22.2, 0.5, 8.8, 2.6, 9.2, 'band')
        cb(a, sx * 13.4, 12.2, -6.6, 7.4, 8.0, 8.4, 'skin')                         # forearm forward
        cb(a, sx * 13.4, 14.0, -6.6, 8.0, 3.0, 6.0, 'skin_l')
        cb(a, sx * 9.8, 10.6, -12.4, 6.6, 7.8, 6.8, 'skin_d')                        # big hands
        for i, dy in enumerate((0.4, 2.6, 4.8)):
            cb(a, sx * 7.2, 10.6 + dy, -14.6, 1.8, 1.9, 2.0, 'skin_d')               # fingers wrapped on the boulder
            cb(a, sx * 6.4, 10.9 + dy, -15.2, 0.4, 1.2, 0.8, 'nail')
        cb(a, sx * 9.0, 16.4, -11.0, 2.4, 2.0, 3.0, 'skin_d')                         # thumb
    bo = m.bone('boulder', [0, 15, -13], m.by_name('arm_r'))
    sphere(bo, 0, 15, -14, 7.4, ['rock_d', 'rock', 'rock_l', 'rock', 'rock', 'rock_d'], n=6, dec=CRACKS)
    m.head_scale = ('head', 1.35, [0, 21, 5])
    m.hitbox(1.8, 2.9)
    m.anim('idle', 2.4, 'loop', {'body': {'position': loop([[0, 0, 0], [0, -0.8, 0]], 2.4), 'rotation': loop([[2, 0, 0], [4, 0, 0]], 2.4)},
                                 'head': {'rotation': loop([[0, 8, 0], [0, -8, 0]], 2.4)},
                                 'arm_r': {'rotation': loop([[0, 0, 0], [3, 0, 0]], 2.4)}, 'arm_l': {'rotation': loop([[0, 0, 0], [3, 0, 0]], 2.4)}})
    L = 1.4
    m.anim('walk', L, 'loop', {'leg_r': {'rotation': loop([[22, 0, 0], [-22, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-22, 0, 0], [22, 0, 0]], L)},
                               'arm_r': {'rotation': loop([[-4, 0, 0], [4, 0, 0]], L)}, 'arm_l': {'rotation': loop([[-4, 0, 0], [4, 0, 0]], L)},
                               'body': {'rotation': loop([[6, 0, 4], [6, 0, -4]], L), 'position': loop([[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0]], L)}})
    T, R = 0.9, 0.4
    swing = [(0, [0, 0, 0]), (0.25, [70, 0, 0]), (R, [20, 0, 0]), (0.55, [-35, 0, 0]), (T, [0, 0, 0])]
    m.anim('attack', T, 'once', {
        'arm_r': {'rotation': swing}, 'arm_l': {'rotation': swing},
        'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-4, 14, 0]), (R, [22, -4, 0]), (0.55, [16, -6, 0]), (T, [0, 0, 0])],
                 'position': [(0, [0, 0, 0]), (0.25, [0, 0.5, 2]), (R, [0, -2.5, -3]), (0.6, [0, -2, -2]), (T, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.25, [-10, 0, 0]), (R, [-30, 0, 0]), (0.6, [-25, 0, 0]), (T, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (R, [20, 0, 0]), (T, [0, 0, 0])]},
        'head': {'rotation': [(0, [0, 0, 0]), (0.25, [-6, -10, 0]), (R, [-10, 0, 0]), (T, [0, 0, 0])]},
        'boulder': {'scale': [(0, S(1)), (R, S(1)), (R + 0.02, S(0.01)), (0.78, S(0.01)), (0.88, S(1)), (T, S(1))]}})
    common_tail(m, death={'body': {'rotation': [(0, [0, 0, 0]), (0.6, [70, 0, 0]), (0.9, [85, 0, 0])],
                                   'position': [(0, [0, 0, 0]), (0.6, [0, -6, -4]), (0.9, [0, -8, -6])]},
                          'boulder': {'position': [(0, [0, 0, 0]), (0.6, [0, -10, -6])]}})
    return m


# ------------------------------------------------------------------- inferno dragon HQ
def inferno_dragon():
    m = Model('clash_inferno_dragon', density=2.5)
    m.mats_({'scale': ('#4cc07c', 'scale'), 'scale_d': ('#2f8a58', 'scale'), 'scale_l': ('#6ad898', 'scale'), 'belly': ('#c6e88c', 'scale'),
             'helm': ('#38505c', 'metal', {'rivets': True}), 'helm_l': ('#557282', 'metal'), 'helm_d': ('#243640', 'metal'),
             'wing': ('#3a9a64', 'leather', {'stitch': False}), 'wing_d': ('#2a7a4c', 'leather', {'stitch': False}),
             'claw': ('#efe2c4', 'bone'), 'tooth': ('#fbf4e0', 'bone'), 'lava': ('#ff5a14', 'glow'), 'lava_y': ('#ffb030', 'glow'), 'glow_w': ('#fff2a0', 'glow'),
             'hose': ('#f2c41a', 'metal'), 'brass': ('#d0a040', 'metal'), 'lens': ('#ff9a2a', 'glow'), 'band': ('#efefef', 'metal'),
             'rivet': ('#9ab4c0', 'metal'), 'nostril': ('#1d4a30', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 15, 0], root)
    cb(body, 0, 10, 1, 12, 10, 13, 'scale', decals={'east': [('shade', 0.0, 0.8, 1.0, 1.0, 0.85)], 'west': [('shade', 0.0, 0.8, 1.0, 1.0, 0.85)]})
    cb(body, 0, 11, 1, 13.4, 7, 11, 'scale')                                       # rounder flanks
    cb(body, 0, 19.6, 1.5, 9.6, 1.2, 10, 'scale_l')                               # back rounding
    cb(body, 0, 8.4, -0.6, 10.4, 7.6, 10.4, 'belly', decals={f: [('rect', 0.0, y, 1.0, y + 0.05, '#9ec068') for y in (0.25, 0.5, 0.75)] for f in ('north', 'east', 'west')})
    cb(body, 0, 7.8, -0.4, 8.4, 0.8, 8.4, 'belly')
    for sx in (1, -1):
        cb(body, sx * 3.6, 6.4, -3.2, 3.2, 3.4, 3.4, 'scale_d')
        for dx in (-0.9, 0, 0.9):
            cb(body, sx * 3.6 + dx, 5.8, -4.9, 0.7, 1.0, 1.2, 'claw')
        cb(body, sx * 3.8, 6.8, 5.2, 3.4, 3.6, 3.6, 'scale_d')
        cb(body, sx * 3.8, 6.2, 3.2, 2.8, 1.0, 1.2, 'claw')
    for i, z in enumerate((-1, 3, 7)):                                               # back spikes
        cb(body, 0, 20.4, z + 4, 1.2, 1.8 - 0.3 * i, 1.6, 'scale_d', rot=('x', 22.5))
    tk = m.bone('tc_tank', [0, 23, 3], body)                                          # team fuel tank (with caps and hoops)
    oct_(tk, 0, 20.2, 3.5, 7.4, 9.0, 'band', axis='z') if False else None
    for (w, h, d) in ((7.4, 4.4, 9.0), (4.4, 7.4, 9.0), (6.4, 6.4, 9.0)):
        cb(tk, 0, 23.9 - h / 2, 3.5, w, h, d, 'band')
    for z in (0.2, 6.8):
        cb(tk, 0, 20.0, z, 7.0, 7.8, 0.7, 'helm_l')
    cb(body, 0, 19.8, -0.6, 13.6, 1.0, 1.4, 'helm_d')                               # straps
    cb(body, 0, 19.8, 7.6, 13.6, 1.0, 1.4, 'helm_d')
    cb(body, 0, 27.6, 3.5, 1.8, 1.2, 1.8, 'brass')
    cb(body, 0, 28.8, 3.5, 2.6, 0.6, 0.6, 'brass')
    # yellow hose: tank -> helmet
    cb(body, -3.2, 25.6, -1.4, 1.3, 1.3, 4.2, 'hose', decals={'up': [('rect', 0.0, y, 1.0, y + 0.1, '#b08a10') for y in (0.3, 0.6)]})
    cb(body, -5.2, 22.0, -3.8, 1.3, 4.6, 1.3, 'hose')
    cb(body, -5.6, 21.2, -6.4, 1.3, 1.3, 4.0, 'hose')
    head = m.bone('head', [0, 19, -6], body)
    eye = [('rect', 0.15, 0.3, 0.85, 0.95, '#ffb030'), ('rect', 0.35, 0.45, 0.65, 0.9, '#1a1008'), ('rect', 0.3, 0.35, 0.45, 0.5, '#ffffff')]
    cb(head, 0, 14.8, -10.5, 10, 8.4, 9, 'scale', decals={'east': [('shade', 0.0, 0.0, 1.0, 1.0, 1.0)]})
    for sx in (1, -1):
        cb(head, sx * 4.4, 18.4, -13.4, 1.2, 3.2, 3.2, 'scale_l', decals={'east' if sx > 0 else 'west': [], 'north': eye})   # eye bulge + eye
        cb(head, sx * 4.4, 18.6, -15.05, 2.8, 2.8, 0.3, 'lens' if False else 'scale_l', decals={'north': eye})
    # helmet: layered dome + crenellated rim + rivets + goggles
    cb(head, 0, 21.4, -10.3, 11, 2.4, 10, 'helm', decals={'north': [('px', x, 0.6, '#9ab4c0') for x in (0.1, 0.3, 0.5, 0.7, 0.9)]})
    cb(head, 0, 23.8, -10.0, 9.4, 1.2, 8.6, 'helm')
    cb(head, 0, 25.0, -9.8, 7.2, 0.8, 6.4, 'helm_l')
    for x in (-4.2, -1.4, 1.4, 4.2):
        cb(head, x, 23.8, -14.9, 1.6, 1.8, 1.0, 'helm_l')                             # crenellations
    for sx in (1, -1):
        cb(head, sx * 5.4, 15.4, -10.0, 0.9, 7.4, 9.6, 'helm', decals={'east' if sx > 0 else 'west': [('px', 0.15, 0.2, '#9ab4c0'), ('px', 0.85, 0.2, '#9ab4c0'), ('px', 0.15, 0.8, '#9ab4c0'), ('px', 0.85, 0.8, '#9ab4c0')]})
        cb(head, sx * 6.0, 18.0, -9.6, 0.8, 3.6, 3.6, 'helm_l')                       # gear-like side boss
        for dy, dz in ((0, -2.2), (0, 2.2), (2.2, 0), (-2.2, 0)):
            cb(head, sx * 6.1, 19.4 + dy, -9.6 + dz, 0.6, 0.8, 0.8, 'helm_d')
    for sx in (1, -1):                                                                # goggles strapped on the helmet front
        cb(head, sx * 2.5, 21.6, -15.6, 3.8, 3.2, 0.9, 'brass')
        cb(head, sx * 2.5, 22.1, -16.15, 2.6, 2.2, 0.4, 'lens', decals={'north': [('rect', 0.15, 0.15, 0.4, 0.4, '#fff2a0')]})
    cb(head, 0, 22.6, -15.6, 1.4, 0.8, 0.8, 'brass')
    # collar: crenellated armour cup under the jaw
    cb(head, 0, 11.4, -9.6, 10.6, 2.6, 9.6, 'helm')
    for x in (-4.0, -1.3, 1.3, 4.0):
        cb(head, x, 14.0, -14.0, 1.8, 1.4, 0.9, 'helm_l')
    # snout with big nostrils + upper teeth
    cb(head, 0, 16.2, -17.4, 7.4, 4.6, 5.4, 'scale', decals={'north': [('rect', 0.12, 0.25, 0.32, 0.55, '#1d4a30'), ('rect', 0.68, 0.25, 0.88, 0.55, '#1d4a30')],
                                                            'up': [('rect', 0.2, 0.6, 0.8, 0.7, '#2f8a58')]})
    cb(head, 0, 19.4, -16.6, 5.6, 1.2, 4.0, 'scale_l')
    for x in (-2.7, -0.9, 0.9, 2.7):
        cb(head, x, 15.0, -19.6, 0.8, 1.3, 0.8, 'tooth')                              # upper teeth
    for sx in (1, -1):
        cb(head, sx * 3.3, 14.6, -18.2, 0.8, 1.7, 0.8, 'tooth')                       # fangs
    mouth = m.bone('mouth', [0, 15.4, -14], head)
    cb(mouth, 0, 13.2, -16.6, 6.8, 2.0, 6.0, 'lava', decals={'up': [('rect', 0.2, 0.2, 0.8, 0.8, '#ffb030'), ('rect', 0.35, 0.3, 0.65, 0.6, '#fff2a0')]})
    cb(mouth, 0, 12.2, -16.4, 7.4, 1.2, 6.6, 'scale_d')                              # lower jaw
    cb(mouth, 0, 12.0, -19.4, 6.4, 1.6, 1.2, 'scale')
    for x in (-2.6, -0.9, 0.9, 2.6):
        cb(mouth, x, 13.4, -19.4, 0.8, 1.1, 0.7, 'tooth')                             # lower teeth
    cb(mouth, 0, 13.6, -18.6, 3.4, 1.4, 1.6, 'glow_w')                               # inferno core
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 5.5, 21, 0], body)
        cb(w, sx * 10.5, 20.6, -1.8, 10, 1.6, 1.6, 'scale_d')
        cb(w, sx * 18.5, 20.8, -1.4, 7, 1.2, 1.2, 'scale_d')
        cb(w, sx * 22.4, 20.4, -1.4, 1.2, 2.2, 1.2, 'claw')
        for i, (x0, d) in enumerate(((10, 10), (16, 9), (20.5, 6.5))):               # membrane panels
            cb(w, sx * x0, 21.0, -0.8 + d / 2, 5.8 if i < 2 else 4.6, 0.6, d, 'wing' if i % 2 == 0 else 'wing_d',
               decals={'up': [('rect', 0.0, 0.92, 1.0, 1.0, '#1f5a38')]})
        for x0 in (13, 18.8):
            cb(w, sx * x0, 21.2, 3.6, 0.8, 0.8, 9, 'scale_d')                          # finger spars
    t1 = m.bone('tail', [0, 12.5, 7.5], body)
    cb(t1, 0, 11, 10, 4.6, 4.0, 5.6, 'scale')
    t2 = m.bone('tail2', [0, 12.5, 12.5], t1)
    cb(t2, 0, 11.4, 14.6, 3.0, 3.0, 4.4, 'scale_d')
    cb(t2, 0, 11.2, 17.8, 4.6, 2.6, 2.4, 'scale_d')
    cb(t2, 0, 13.6, 13.6, 0.8, 1.2, 1.4, 'claw')
    m.head_scale = ('head', 1.25, [0, 19, -6])
    m.hitbox(1.6, 1.4)

    def flap(L, amp, extra=None):
        tr = {}
        for side, s in (('r', 1), ('l', -1)):
            tr['wing_' + side] = {'rotation': loop([[0, 0, s * amp], [0, 0, -s * amp * 0.8]], L)}
        tr['body'] = {'position': loop([[0, 0, 0], [0, 1.2, 0]], L)}
        tr['tail'] = {'rotation': loop([[0, 12, 0], [0, -12, 0]], L * 2)}
        tr['tail2'] = {'rotation': loop([[0, -10, 0], [0, 10, 0]], L * 2)}
        if extra:
            tr.update(extra)
        return tr
    m.anim('idle', 1.6, 'loop', flap(0.8, 35, {'head': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 1.6)},
                                               'mouth': {'rotation': loop([[6, 0, 0], [12, 0, 0]], 0.8)}}))
    w = flap(0.5, 40)
    w['body']['rotation'] = [(0, [10, 0, 0]), (0.5, [10, 0, 0])]
    w['tail'] = {'rotation': loop([[-8, 12, 0], [-8, -12, 0]], 1.0)}
    w['tail2'] = {'rotation': loop([[0, -10, 0], [0, 10, 0]], 1.0)}
    w['mouth'] = {'rotation': [(0, [6, 0, 0]), (1.0, [6, 0, 0])]}
    m.anim('walk', 1.0, 'loop', w)
    att = flap(0.4, 30)
    att['head'] = {'rotation': [(0, [0, 0, 0]), (0.08, [-8, 0, 0]), (0.16, [8, 0, 0]), (0.28, [8, 3, 0]), (0.4, [8, -3, 0])],
                   'position': [(0, [0, 0, 0]), (0.16, [0, 0, -1.5]), (0.4, [0, 0, -1])]}
    att['mouth'] = {'scale': [(0, S(1)), (0.1, S(1.25)), (0.2, S(1.15)), (0.3, S(1.3)), (0.4, S(1.2))],
                    'rotation': [(0, [6, 0, 0]), (0.1, [28, 0, 0]), (0.4, [24, 0, 0])]}
    m.anim('attack', 0.4, 'once', att)
    common_tail(m, death={'root': {'position': [(0, [0, 0, 0]), (0.6, [0, -10, 0]), (0.9, [0, -14, 0])],
                                   'rotation': [(0, [0, 0, 0]), (0.6, [20, 0, 70]), (0.9, [25, 0, 90])],
                                   'scale': [(0, S(1)), (0.7, S(1)), (0.9, S(0.4))]}})
    return m


ALL = {'elixir_golem': elixir_golem, 'elixir_golemite': elixir_golemite, 'elixir_blob': elixir_blob,
       'goblin_cage': goblin_cage, 'x_bow': x_bow, 'bomb_tower': bomb_tower,
       'elixir_collector': elixir_collector, 'guard': guard, 'wall_breaker': wall_breaker, 'bowler': bowler,
       'boulder': boulder, 'inferno_dragon': inferno_dragon}

if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    only = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    for k, fn in ALL.items():
        if only and k not in only:
            continue
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad, 'muzzle', getattr(m, 'muzzle', None))
