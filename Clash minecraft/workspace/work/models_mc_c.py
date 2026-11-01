"""MC-style (vanilla mob look, like the user's clash_hog_rider) models, letter C:
elixir_collector / guard / wall_breaker / bowler / boulder / inferno_dragon / bomb.
Units px (16 = 1 block), front = north (-Z), origin = feet centre. density 1.0 = 1 texel per px, no rounding."""
import sys, os, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def S(v):
    return [v, v, v]


def shrink(m, k):
    """scale the whole rig by k but keep the texture grid (vanilla baby / giant mobs keep their 64px skin)"""
    m.scale_bone('root', k, [0, 0, 0])
    for b in m.bones:
        for c in b.cubes:
            c['dens'] = 1.0 / k


def mk(name):
    m = Model(name, density=1.0)
    m.round = False
    return m


def troop_tail(m, hit_bone='body', death=None):
    m.anim('spawn', 0.5, 'once', {'root': {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                           'scale': [(0, S(0.3)), (0.35, S(1.08)), (0.5, S(1))]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'rotation': [(0, [0, 0, 0]), (0.08, [-8, 0, 0]), (0.3, [0, 0, 0])],
                                           'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.2]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death or {'root': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 85]), (0.9, [0, 0, 90])],
                                                    'position': [(0, [0, 0, 0]), (0.9, [0, -3, 0])]}})


def walk_cycle(L, amp=35, arms=('arm_r', 'arm_l'), arm_amp=None):
    a = amp if arm_amp is None else arm_amp
    t = {'leg_r': {'rotation': loop([[amp, 0, 0], [-amp, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-amp, 0, 0], [amp, 0, 0]], L)}}
    if arms:
        t[arms[0]] = {'rotation': loop([[-a, 0, 0], [a, 0, 0]], L)}
        t[arms[1]] = {'rotation': loop([[a, 0, 0], [-a, 0, 0]], L)}
    return t


# ---- paint helpers (flat vanilla faces)
def px(x, y, c, W=8, H=8):
    """pixel (x, y) on a W x H face grid -> rect decal"""
    return ('rect', x / W, y / H, (x + 1) / W, (y + 1) / H, c)


def prect(x0, y0, x1, y1, c, W=8, H=8):
    return ('rect', x0 / W, y0 / H, (x1 + 1) / W, (y1 + 1) / H, c)


SKEL = {'bone': ('#c8c8c8', 'bone'), 'bone_d': ('#9a9a9a', 'bone'), 'band': ('#efefef', 'cloth')}
SKULL_FACE = [prect(1, 3, 2, 4, '#3a3a3a'), prect(5, 3, 6, 4, '#3a3a3a'), px(1, 3, '#1c1c1c'), px(6, 3, '#1c1c1c'),
              px(3, 5, '#4a4a4a'), px(4, 5, '#4a4a4a'), prect(1, 6, 6, 6, '#5a5a5a'), px(2, 7, '#5a5a5a'), px(4, 7, '#5a5a5a'), px(6, 7, '#5a5a5a')]
RIB = [prect(0, 2, 7, 2, '#6e6e6e', 8, 12), prect(0, 4, 7, 4, '#6e6e6e', 8, 12), prect(0, 6, 7, 6, '#6e6e6e', 8, 12), prect(3, 0, 4, 11, '#b0b0b0', 8, 12),
       prect(0, 8, 2, 11, '#2a2a2a', 8, 12), prect(5, 8, 7, 11, '#2a2a2a', 8, 12)]


def skeleton(m, arms_up=False):
    """vanilla skeleton rig (32 px). returns dict of bones"""
    root = m.bone('root', [0, 0, 0])
    b = {'root': root}
    for sx, side in ((1, 'r'), (-1, 'l')):
        b['leg_' + side] = lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 2, 0, 0, 2, 12, 2, 'bone')
    body = b['body'] = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 12, 0, 8, 12, 4, 'bone', decals={'north': RIB, 'south': RIB})
    head = b['head'] = m.bone('head', [0, 24, 0], body)
    cb(head, 0, 24, 0, 8, 8, 8, 'bone', decals={'north': SKULL_FACE})
    for sx, side in ((1, 'r'), (-1, 'l')):
        b['arm_' + side] = a = m.bone('arm_' + side, [sx * 5, 22, 0], body)
        if arms_up:
            cb(a, sx * 5, 22, 0, 2, 12, 2, 'bone')
        else:
            cb(a, sx * 5, 12, 0, 2, 12, 2, 'bone')
    return b


# =================================================================== elixir collector
def elixir_collector():
    m = mk('clash_elixir_collector')
    m.mats_({'plank': ('#a07a46', 'wood', {'planks': True}), 'log': ('#6b4a28', 'wood', {'grain': 'v'}), 'stone': ('#8a8a8a', 'stone'),
             'iron': ('#b8b8b8', 'metal'), 'copper': ('#c06a3a', 'metal'), 'elx': ('#e04ad8', 'gem'), 'glow': ('#ff9af2', 'glow'),
             'glass': ('#dcecf4', 'gem'), 'band': ('#efefef', 'cloth'), 'bubble': ('#ffd8fa', 'glow')})
    root = m.bone('root', [0, 0, 0])
    fr = m.bone('frame', [0, 0, 0], root)
    cb(fr, 0, 0, 0, 40, 3, 40, 'stone')
    cb(fr, 0, 3, 0, 34, 3, 34, 'plank')
    tb = m.bone('tc_seal_base', [0, 6, 0], fr)
    cb(tb, 0, 6, 0, 28, 2, 28, 'band')
    cb(fr, 0, 8, 0, 24, 6, 24, 'log')
    for (x, z) in ((10, 10), (-10, 10), (10, -10), (-10, -10)):
        cb(fr, x, 14, z, 3, 18, 3, 'log')
    cb(fr, 16, 6, 0, 3, 26, 3, 'copper')
    cb(fr, 13.5, 29, 0, 6, 3, 3, 'copper')
    lev = m.bone('lever', [18.5, 19, 0], fr)
    cb(lev, 18.5, 18.5, 0, 1, 1, 9, 'log')
    cb(lev, 18.5, 14.5, 0, 1, 9, 1, 'log')
    for (dy, dz, h, d) in ((4, 0, 1, 9), (-5, 0, 1, 9), (0, 4.5, 9, 1), (0, -4.5, 9, 1)):
        cb(lev, 18.5, 18.5 + dy if h == 1 else 14.5, dz, 1, h, d, 'log')
    tank = m.bone('tank', [0, 14, 0], root)
    gl = [('rect', 0.1, 0.0, 0.2, 1.0, '#ffd0fa'), ('rect', 0.25, 0.0, 0.3, 0.6, '#ffd0fa'), ('rect', 0.0, 0.9, 1.0, 1.0, '#b030b0')]
    cb(tank, 0, 14, 0, 16, 18, 16, 'elx', decals={f: gl for f in ('north', 'south', 'east', 'west')})
    core = m.bone('glow_core', [0, 23, 0], tank)
    cb(core, 0, 15, 0, 15, 16, 15, 'glow')
    bub = m.bone('bubbles', [0, 16, 0], tank)
    for (x, z) in ((-3, -8.5), (4, -8.5), (8.5, 2), (-8.5, -3), (2, 8.5)):
        cb(bub, x, 16, z, 1, 1, 1, 'bubble')
    lid = m.bone('lid', [0, 32, 0], root)
    cb(lid, 0, 32, 0, 24, 5, 24, 'log')
    tt = m.bone('tc_seal_top', [0, 37, 0], lid)
    cb(tt, 0, 37, 0, 18, 2, 18, 'band')
    cb(lid, 0, 39, 0, 8, 2, 8, 'plank')
    cb(lid, 0, 41, 0, 2, 2, 2, 'copper')
    m.hitbox(2.6, 2.6)
    m.anim('idle', 1.2, 'loop', {'lever': {'rotation': [(0, [0, 0, 0]), (1.2, [90, 0, 0])]},
                                 'bubbles': {'position': [(0, [0, 0, 0]), (1.2, [0, 14, 0])], 'scale': [(0, S(1)), (1.2, S(0.3))]}}, interp='linear')
    m.anim('attack', 0.6, 'once', {'glow_core': {'scale': [(0, S(1)), (0.2, [1.15, 1.08, 1.15]), (0.6, S(1))]},
                                   'tank': {'scale': [(0, S(1)), (0.2, [1.05, 1.04, 1.05]), (0.6, S(1))]},
                                   'lid': {'position': [(0, [0, 0, 0]), (0.2, [0, 1.5, 0]), (0.6, [0, 0, 0])]},
                                   'lever': {'rotation': [(0, [0, 0, 0]), (0.6, [360, 0, 0])]}})
    m.anim('spawn', 0.6, 'once', {'root': {'position': [(0, [0, 24, 0]), (0.3, [0, 0, 0]), (0.45, [0, 1, 0]), (0.6, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'root': {'position': [(0, [0, 0, 0]), (0.05, [1, 0, 0]), (0.1, [-1, 0, 0]), (0.2, [0.5, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', {'tank': {'scale': [(0, S(1)), (0.15, S(1.1)), (0.18, S(0.01)), (0.9, S(0.01))]},
                                  'lid': {'position': [(0, [0, 0, 0]), (0.18, [0, 0, 0]), (0.35, [0, 5, 0]), (0.7, [-4, -18, 2])],
                                          'rotation': [(0, [0, 0, 0]), (0.7, [10, 0, 40])]}})
    return m


# =================================================================== guard (small skeleton, black helmet, team plume, round shield)
def guard():
    m = mk('clash_guard')
    m.mats_(dict(SKEL, **{'helm': ('#2a2a30', 'metal'), 'helm_l': ('#44444c', 'metal'), 'plank': ('#a07040', 'wood', {'planks': True, 'grain': 'v'}),
                          'stick': ('#6b4a28', 'wood'), 'iron': ('#d0d0d0', 'metal'), 'gold': ('#f0c030', 'metal')}))
    b = skeleton(m)
    face = SKULL_FACE + [prect(1, 7, 6, 7, '#e8e8e8'), px(2, 7, '#5a5a5a'), px(5, 7, '#5a5a5a')]           # underbite teeth
    b['head'].cubes[0]['decals'] = {'north': face}
    h = b['head']
    cb(h, 0, 28, 0, 9, 4.5, 9, 'helm', decals={'north': [prect(0, 0, 8, 0, '#44444c', 9, 5)]})            # helmet shell (outer layer)
    cb(h, 0, 25, -4.3, 2, 4, 0.6, 'helm')                                                               # nasal guard
    for sx in (1, -1):
        cb(h, sx * 4.3, 24.5, 0, 0.6, 4, 8, 'helm')
    pl = m.bone('tc_plume', [0, 32.5, 0], h)
    cb(pl, 0, 32.5, 0.5, 1, 3, 4, 'band')
    cb(pl, 0, 35.5, 2, 1, 1.5, 3, 'band')
    sp = m.bone('spear', [5, 13, 0], b['arm_r'])
    cb(sp, 5, 12.5, -3, 1, 1, 22, 'stick')
    cb(sp, 5, 12, -15, 2, 2, 2, 'iron')
    cb(sp, 5, 12.5, -16.5, 1, 1, 1, 'iron')
    sh = m.bone('shield', [-4, 15, -3], b['arm_l'])
    crown = [prect(3, 5, 8, 6, '#f0c030', 12, 12), px(3, 4, '#f0c030', 12, 12), px(5, 3, '#f0c030', 12, 12), px(6, 3, '#f0c030', 12, 12),
             px(8, 4, '#f0c030', 12, 12), ('ering', 0.5, 0.5, 0.5, 0.5, 0.17, '#5a5a5a')]
    cb(sh, -4, 11, -3.5, 12, 8, 1, 'plank', decals={'north': crown})
    cb(sh, -4, 9, -3.5, 8, 12, 1, 'plank', decals={'north': crown})
    cb(sh, -4, 14.5, -4.3, 2, 2, 0.6, 'iron')
    shrink(m, 0.7)
    m.hitbox(0.7, 1.5)
    m.anim('idle', 2.0, 'loop', {'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 2.0)}, 'arm_r': {'rotation': loop([[-30, 0, 0], [-34, 0, 0]], 2.0)},
                                 'arm_l': {'rotation': loop([[-40, 20, 0], [-38, 20, 0]], 2.0)}, 'tc_plume': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 1.0)}})
    w = walk_cycle(0.6, 30, arms=None)
    w['arm_r'] = {'rotation': [(0, [-30, 0, 0]), (0.6, [-30, 0, 0])]}
    w['arm_l'] = {'rotation': [(0, [-40, 20, 0]), (0.6, [-40, 20, 0])]}
    m.anim('walk', 0.6, 'loop', w)
    m.anim('attack', 0.5, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 0]), (0.15, [-10, 0, 0]), (0.25, [-60, 0, 0]), (0.5, [-30, 0, 0])]},
                                   'spear': {'position': [(0, [0, 0, 0]), (0.15, [0, 0, 2]), (0.25, [0, 0, -4]), (0.5, [0, 0, 0])]},
                                   'arm_l': {'rotation': [(0, [-40, 20, 0]), (0.5, [-40, 20, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.25, [8, -8, 0]), (0.5, [0, 0, 0])]}})
    troop_tail(m)
    return m


# =================================================================== wall breaker (tiny skeleton, team bandana, barrel bomb overhead)
def wall_breaker():
    m = mk('clash_wall_breaker')
    m.mats_(dict(SKEL, **{'barrel': ('#9a6232', 'wood', {'grain': 'v', 'planks': False}), 'barrel_t': ('#b07a40', 'wood'), 'iron': ('#4a4a50', 'metal'),
                          'fuse': ('#6a5636', 'rope'), 'spark': ('#ffd040', 'glow')}))
    b = skeleton(m, arms_up=True)
    b['head'].cubes[0]['decals'] = {'north': SKULL_FACE[:6] + [prect(2, 6, 5, 7, '#1c1c1c'), prect(2, 6, 5, 6, '#e0e0e0')]}   # open mouth
    bd = m.bone('tc_bandana', [0, 30, 0], b['head'])
    cb(bd, 0, 29.5, 0, 8.6, 2.6, 8.6, 'band')
    cb(bd, 0, 28.5, 4.6, 2, 2, 0.8, 'band')
    bomb = m.bone('bomb', [0, 40, 0], b['body'])
    hoops = [('rect', 0.15, 0.0, 0.25, 1.0, '#4a4a50'), ('rect', 0.75, 0.0, 0.85, 1.0, '#4a4a50')]
    cb(bomb, 0, 34, 0, 16, 12, 12, 'barrel', decals={f: hoops for f in ('north', 'south', 'up', 'down')})
    for sx in (1, -1):
        cb(bomb, sx * 8.2, 35, 0, 0.4, 10, 10, 'barrel_t')
    cb(bomb, 0, 46, 0, 1, 3, 1, 'fuse')
    sp = m.bone('spark', [0, 49.5, 0], bomb)
    cb(sp, 0, 49, 0, 2, 2, 2, 'spark')
    shrink(m, 0.55)
    m.hitbox(0.6, 1.2)
    m.anim('idle', 0.8, 'loop', {'spark': {'scale': loop([S(1), S(1.5), S(0.8), S(1.3)], 0.8)}, 'bomb': {'rotation': loop([[0, 0, 2], [0, 0, -2]], 0.8)}})
    w = walk_cycle(0.3, 50, arms=None)
    w['body'] = {'rotation': [(0, [12, 0, 0]), (0.3, [12, 0, 0])], 'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 0.3)}
    w['spark'] = {'scale': loop([S(1), S(1.6)], 0.15)}
    m.anim('walk', 0.3, 'loop', w)
    m.anim('attack', 0.3, 'once', {'root': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1]), (0.2, [0, 2, -5]), (0.3, [0, 1, -7])],
                                            'rotation': [(0, [0, 0, 0]), (0.08, [-10, 0, 0]), (0.3, [45, 0, 0])]},
                                   'bomb': {'scale': [(0, S(1)), (0.3, S(1.3))]}, 'spark': {'scale': [(0, S(1)), (0.3, S(2.5))]}})
    troop_tail(m, death={'root': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 85]), (0.9, [0, 0, 90])]},
                         'bomb': {'position': [(0, [0, 0, 0]), (0.6, [4, -10, 0])], 'scale': [(0, S(1)), (0.7, S(1)), (0.9, S(0.01))]}})
    return m


# =================================================================== bowler (big indigo player rig)
def bowler():
    """HQ vanilla-like CR Bowler: indigo gorilla-built giant, bald, heavy brow, big bulbous nose, pointy ears,
    big jaw + grin, huge forearms + fists, team arm bands, leather belt + pale loincloth, craggy boulder"""
    m = mk('clash_bowler')
    m.mats_({'skin': ('#6b69dc', 'skin'), 'skin_d': ('#5452bc', 'skin'), 'skin_l': ('#8583ea', 'skin'), 'nose': ('#9a86e6', 'skin'),
             'loin': ('#c9a97a', 'leather', {'stitch': False}), 'loin_d': ('#a88a5e', 'leather', {'stitch': False}),
             'belt': ('#5e4026', 'leather'), 'buckle': ('#b9a06a', 'metal'), 'wrap': ('#8a6a48', 'leather'),
             'band': ('#efefef', 'cloth'), 'rope': ('#c9a265', 'rope'), 'hole': ('#2a2a2e', 'plain'), 'stone': ('#8c8c8c', 'stone'), 'stone_d': ('#727272', 'stone'), 'stone_l': ('#a2a2a2', 'stone')})
    D = '#4a48a8'
    root = m.bone('root', [0, 0, 0])
    # legs: short + thick
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = m.bone('leg_' + side, [x, 10, 0], root)
        cb(lg, x, 5.2, 0, 5.0, 5.0, 5.0, 'skin')                                  # thigh
        cb(lg, x, 1.0, -0.1, 5.4, 4.4, 5.4, 'skin', decals={'north': [prect(0, 0, 7, 0, D)]})   # calf
        cb(lg, x, 0, -0.8, 5.8, 1.2, 6.8, 'skin_d',                               # wide foot with toes
           decals={'north': [px(1, 2, D, 8, 3), px(3, 2, D, 8, 3), px(5, 2, D, 8, 3)]})
        cb(lg, x, 4.6, -2.7, 2.6, 1.2, 0.4, 'skin_l')                              # kneecap highlight
    body = m.bone('body', [0, 10, 0], root)
    # loincloth + belt
    cb(body, 0, 10.4, 0, 12.2, 1.6, 7.4, 'rope')
    cb(body, -3.0, 9.0, -3.9, 1.0, 1.8, 0.8, 'rope')
    for i, (dx, ln) in enumerate(((-4.6, 5.2), (-2.6, 6.4), (-0.6, 5.6), (1.4, 6.8), (3.4, 5.0), (5.0, 6.0))):
        cb(body, dx, 11.0 - ln, -3.9, 2.0, ln, 0.6, 'loin' if i % 2 else 'loin_d')
        cb(body, dx, 11.0 - ln + 0.4, 3.9, 2.0, ln - 0.4, 0.6, 'loin_d' if i % 2 else 'loin')
    for sx in (1, -1):
        cb(body, sx * 5.8, 5.8, 0, 0.6, 5.2, 7.2, 'loin_d')
    # torso: gorilla build, chest much wider than waist
    cb(body, 0, 12.2, 0, 11.0, 5.0, 7.0, 'skin', decals={'north': [prect(3, 1, 4, 6, D), prect(1, 3, 2, 3, D), prect(5, 3, 6, 3, D)]})
    cb(body, 0, 16.8, 0.2, 14.4, 7.2, 8.4, 'skin')                                 # chest
    for sx in (1, -1):
        cb(body, sx * 3.4, 18.6, -4.3, 5.8, 3.6, 0.8, 'skin_l',                    # pecs
           decals={'north': [prect(0, 7, 7, 7, D)]})
        cb(body, sx * 4.6, 23.6, 0.8, 5.2, 1.8, 6.0, 'skin')                       # trapezius
    cb(body, 0, 13.4, -3.8, 5.4, 4.0, 0.6, 'skin_l', decals={'north': [prect(3, 0, 4, 7, D), prect(0, 3, 7, 3, D)]})   # abs
    cb(body, 0, 18.0, 4.4, 10.0, 5.4, 0.6, 'skin_d')                               # back muscle
    # head: low + forward, bald
    hd = m.bone('head', [0, 23.4, -1.8], body)
    W9 = dict(W=9, H=9)
    face = [px(1, 4, '#ffffff', **W9), px(2, 4, '#ffffff', **W9), px(6, 4, '#ffffff', **W9), px(7, 4, '#ffffff', **W9),
            px(1, 5, '#ffffff', **W9), px(2, 5, '#2a8aff', **W9), px(6, 5, '#2a8aff', **W9), px(7, 5, '#ffffff', **W9),
            px(1, 3, D, **W9), px(2, 3, D, **W9), px(6, 3, D, **W9), px(7, 3, D, **W9),
            px(1, 7, '#2a2858', **W9), px(2, 8, '#2a2858', **W9), px(3, 8, '#f2efe0', **W9), px(4, 8, '#2a2858', **W9),
            px(5, 8, '#f2efe0', **W9), px(6, 8, '#2a2858', **W9), px(7, 7, '#2a2858', **W9)]
    cb(hd, 0, 23.8, -3.0, 9.0, 9.0, 9.0, 'skin', decals={'north': face, 'up': [prect(2, 2, 5, 5, '#7a78e2')]})
    cb(hd, 0, 29.4, -7.6, 9.4, 1.4, 1.4, 'skin_d')                                 # heavy brow ridge
    cb(hd, 0, 22.6, -3.8, 9.6, 2.6, 8.4, 'skin', decals={'north': [prect(1, 0, 6, 0, '#2a2858')]})   # big jaw
    cb(hd, 0, 22.2, -8.1, 4.6, 1.8, 0.8, 'skin_l')                                 # chin
    cb(hd, 0, 26.2, -8.1, 2.2, 3.0, 1.6, 'nose')                                   # nose bridge
    cb(hd, 0, 25.0, -8.9, 3.4, 2.4, 2.2, 'nose', decals={'down': [px(2, 3, D), px(5, 3, D)]})   # bulbous tip
    for sx in (1, -1):
        ear = m.bone('ear_' + ('r' if sx > 0 else 'l'), [sx * 4.8, 27, -2.6], hd)    # big leaf-shaped elf ears
        inner = {'north': [prect(2, 2, 5, 7, '#9a86e6')]}
        ro = dict(rot=('z', -sx * 22.5), rot_origin=[sx * 4.6, 27, -1.6])
        cb(ear, sx * 5.9, 25.8, -1.6, 2.8, 3.2, 1.0, 'skin', decals=inner, **ro)     # broad ear facing forward
        cb(ear, sx * 6.3, 29.0, -1.6, 2.2, 2.4, 1.0, 'skin', decals=inner, **ro)
        cb(ear, sx * 6.7, 31.4, -1.6, 1.3, 1.8, 0.9, 'skin', **ro)
        cb(ear, sx * 7.0, 33.2, -1.6, 0.7, 1.0, 0.8, 'skin', **ro)                   # pointy tip
        cb(ear, sx * 4.9, 26.4, -1.6, 0.8, 2.6, 1.4, 'skin_d', **ro)                  # ear root
        cb(hd, sx * 3.2, 24.6, -7.6, 1.6, 1.4, 0.4, 'skin_l')                       # cheeks
    # arms: huge forearms + fists (gorilla)
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.6
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x, 19.6, 0, 6.2, 5.6, 6.2, 'skin')                                   # shoulder (deltoid)
        cb(a, x, 14.6, 0, 5.2, 5.2, 5.2, 'skin', decals={'north': [prect(3, 1, 4, 6, D)]})     # upper arm
        t = m.bone('tc_band_' + side, [x, 17, 0], a)
        cb(t, x, 16.0, 0, 5.8, 1.8, 5.8, 'band')                                   # team arm band
        cb(a, x, 7.6, 0, 6.6, 7.2, 6.6, 'skin', decals={'north': [prect(0, 2, 0, 6, D)]})     # big forearm
        cb(a, x, 12.8, 0, 7.0, 1.6, 7.0, 'wrap')                                   # leather elbow wrap
        hd_ = m.bone('hand_' + side, [x - sx * 1.0, 7.4, 0], a)                    # wrist bone: posed by angle
        hx = x - sx * 1.0
        groove = [prect(0, 0, 7, 0, D)] + [('rect', f, 0.15, f + 0.04, 1.0, D) for f in (0.25, 0.5, 0.75)]
        cb(hd_, hx, 3.2, 0, 3.2, 4.2, 6.8, 'skin_d', decals={'north': [prect(0, 0, 7, 0, D)]})        # palm
        cb(hd_, hx - sx * 0.3, -0.4, 0, 2.6, 3.6, 6.8, 'skin_d', decals={'east': groove, 'west': groove})   # fingers
        cb(hd_, hx - sx * 2.0, 2.0, -2.8, 1.6, 3.4, 1.6, 'skin_d')                                    # thumb
    # craggy boulder (held at chest by both hands via the arm pose)
    bo = m.bone('boulder', [0, 16, -14], body)                                   # cradled in both hands below the chest
    cxb, cyb, czb, R = 0.0, 14.2, -15.6, 7.2
    n = 7
    hgt = 2 * R / n
    for i in range(n):
        yc = -R + hgt * (i + 0.5)
        rr = max(2.0, (R * R - yc * yc) ** 0.5)
        mat = 'stone' if i % 2 else 'stone_d'
        cb(bo, cxb, cyb + yc - hgt / 2, czb, 2 * rr, hgt, 1.5 * rr, mat)
        cb(bo, cxb, cyb + yc - hgt / 2, czb, 1.5 * rr, hgt, 2 * rr, mat)
    for (dx, dy, dz, w) in ((4.6, 3.0, -4.0, 3.4), (-5.0, -1.4, -3.6, 3.0), (0.8, 6.0, -2.0, 3.6),
                            (-2.4, -5.0, -4.6, 3.0), (5.6, -3.0, 2.0, 2.8), (-5.4, 3.4, 2.6, 3.0)):
        cb(bo, cxb + dx, cyb + dy - w / 2, czb + dz, w, w * 0.8, w, 'stone_l')
    for (hx, hy) in ((-2.6, 2.0), (2.6, 2.0), (0.0, -2.4)):                        # bowling-ball finger holes, front face
        rr = (R * R - hy * hy - hx * hx) ** 0.5
        cb(bo, cxb + hx, cyb + hy - 1.7, czb - rr - 0.6, 3.4, 3.4, 0.6, 'stone_d',
           decals={'north': [('rect', 0.2, 0.2, 0.8, 0.8, '#1c1c20'), ('rect', 0.3, 0.3, 0.7, 0.7, '#0e0e10')]})
    import random
    rng = random.Random(7)
    for bn in m.bones:
        for c in bn.cubes:
            if not c['mat'].startswith('skin'):
                continue
            for f in ('north', 'south', 'east', 'west', 'up'):
                dec = c['decals'].setdefault(f, [])
                base = [('shade', 0, 0, 1, 0.18, 1.10), ('shade', 0, 0.78, 1, 1, 0.84)] if f != 'up' else [('shade', 0.2, 0.2, 0.8, 0.8, 1.06)]
                if f != 'up':
                    base += [('shade', 0, 0, 0.12, 1, 0.9), ('shade', 0.88, 0, 1, 1, 0.9)]
                for _ in range(6):                                                   # mottled skin
                    x0, y0 = rng.random() * 0.85, rng.random() * 0.85
                    base.append(('shade', x0, y0, x0 + 0.1, y0 + 0.1, rng.choice((0.93, 1.06))))
                c['decals'][f] = base + dec
    shrink(m, 1.55)
    m.hitbox(1.8, 3.2)
    hold_h = {'hand_r': {'rotation': [(0, [-40, 0, 35])]}, 'hand_l': {'rotation': [(0, [-40, 0, -35])]}}
    up = [-50, 0, 0]
    m.anim('idle', 2.4, 'loop', {'arm_r': {'rotation': loop([up, [-52, 0, 0]], 2.4)},
                                 'arm_l': {'rotation': loop([up, [-52, 0, 0]], 2.4)},
                                 'boulder': {'position': loop([[0, 0, 0], [0, 0.4, 0]], 2.4)}, **hold_h,
                                 'head': {'rotation': loop([[-10, 10, 0], [-10, 4, 0]], 2.4)},
                                 'body': {'rotation': loop([[4, 0, 0], [6, 0, 0]], 2.4)}})
    w = walk_cycle(1.2, 25, arms=None)
    w['arm_r'] = {'rotation': loop([up, [-48, 0, 0]], 0.6)}
    w['arm_l'] = {'rotation': loop([up, [-48, 0, 0]], 0.6)}
    w.update(hold_h)
    w['body'] = {'rotation': loop([[6, 0, -3], [6, 0, 3]], 1.2)}
    m.anim('walk', 1.2, 'loop', w)
    sw = [(0, up), (0.25, [10, 0, 0]), (0.45, [-60, 0, 0]), (0.6, [-30, 0, 0]), (0.9, up)]
    m.anim('attack', 0.9, 'once', {'arm_r': {'rotation': sw}, 'arm_l': {'rotation': sw}, **hold_h,
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-10, 10, 0]), (0.45, [20, -6, 0]), (0.9, [0, 0, 0])]},
                                   'boulder': {'scale': [(0, S(1)), (0.45, S(1)), (0.47, S(0.01)), (0.8, S(0.01)), (0.9, S(1))],
                                               'position': [(0, [0, 0, 0]), (0.25, [0, -14, 18]), (0.45, [0, -4, -4]), (0.47, [0, 0, 0])]}})
    troop_tail(m)
    return m



# =================================================================== boulder
def boulder():
    m = mk('clash_boulder')
    m.mats_({'cobble': ('#8a8a8a', 'stone'), 'cobble_d': ('#727272', 'stone'), 'cobble_l': ('#9c9c9c', 'stone')})
    root = m.bone('root', [0, 0, 0])
    bo = m.bone('boulder', [0, 9.5, 0], root)
    cb(bo, 0, 2.5, 0, 14, 14, 14, 'cobble')
    cb(bo, 0, 3.5, 0, 19, 12, 12, 'cobble_d')
    cb(bo, 0, 0, 0, 12, 19, 12, 'cobble_l')
    cb(bo, 0, 3.5, 0, 12, 12, 19, 'cobble')
    m.hitbox(1.2, 1.2)
    roll = {'boulder': {'rotation': [(0, [0, 0, 0]), (0.15, [90, 0, 0]), (0.3, [180, 0, 0]), (0.45, [270, 0, 0]), (0.6, [360, 0, 0])]}}
    m.anim('roll', 0.6, 'loop', roll, interp='linear')
    m.anim('idle', 0.6, 'loop', roll, interp='linear')
    return m


# =================================================================== inferno dragon (blocky green baby dragon)
def inferno_dragon():
    m = mk('clash_inferno_dragon')
    m.mats_({'scale': ('#4aa85a', 'scale'), 'scale_d': ('#357a42', 'scale'), 'belly': ('#c8d878', 'scale'), 'iron': ('#5a6a72', 'metal'),
             'iron_l': ('#7a8a92', 'metal'), 'brass': ('#c8a040', 'metal'), 'lens': ('#ff9a2a', 'glow'), 'lava': ('#ff5a10', 'glow'),
             'glow_w': ('#ffe080', 'glow'), 'hose': ('#e8c020', 'plain'), 'band': ('#efefef', 'metal'), 'wing': ('#3a8a4a', 'leather', {'stitch': False}),
             'tooth': ('#f0f0e0', 'bone')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 14, 0], root)
    cb(body, 0, 10, 1, 10, 8, 14, 'scale', decals={'down': [('rect', 0.1, 0.1, 0.9, 0.9, '#c8d878')]})
    cb(body, 0, 9.5, -1, 8, 2, 10, 'belly')
    for sx in (1, -1):
        cb(body, sx * 3, 6, -3, 3, 4, 3, 'scale_d')
        cb(body, sx * 3, 6, 5, 3, 4, 3, 'scale_d')
    tk = m.bone('tc_tank', [0, 18, 3], body)
    cb(tk, 0, 18, 3, 5, 5, 9, 'band')
    cb(body, 0, 23, 3, 1, 1, 1, 'brass')
    cb(body, -3, 20, -2, 1, 1, 5, 'hose')
    cb(body, -3, 17, -5, 1, 4, 1, 'hose')
    head = m.bone('head', [0, 18, -6], body)
    eye = [prect(0, 3, 1, 3, '#ffffff', 8, 8), px(1, 3, '#ff8a20'), prect(6, 3, 7, 3, '#ffffff'), px(6, 3, '#ff8a20')]
    cb(head, 0, 14, -10, 8, 8, 8, 'scale', decals={'north': eye})
    cb(head, 0, 14, -16, 6, 4, 4, 'scale', decals={'north': [px(1, 1, '#1a3a20', 6, 4), px(4, 1, '#1a3a20', 6, 4), prect(0, 3, 5, 3, '#f0f0e0', 6, 4)]})
    cb(head, 0, 20, -10, 8.8, 3, 8.8, 'iron', decals={'north': [px(1, 1, '#a0b0b8', 9, 3), px(7, 1, '#a0b0b8', 9, 3)]})   # helmet
    for sx in (1, -1):
        cb(head, sx * 4.3, 15, -10, 0.6, 5, 8.4, 'iron')
        cb(head, sx * 2, 20.5, -14.6, 3, 2, 0.6, 'brass')
        cb(head, sx * 2, 21, -15, 2, 1, 0.4, 'lens')
    for x in (-3, 0, 3):
        cb(head, x, 23, -14, 1.4, 1, 1, 'iron_l')
    mouth = m.bone('mouth', [0, 14, -12], head)
    cb(mouth, 0, 12, -15.5, 6, 2, 5, 'scale_d', decals={'up': [('rect', 0.15, 0.1, 0.85, 0.9, '#ff5a10')]})
    cb(mouth, 0, 13.6, -17.6, 4, 0.8, 0.6, 'lava')
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 5, 18, 0], body)
        cb(w, sx * 11, 17.5, 1, 12, 1, 9, 'wing', decals={'up': [('rect', 0.0, 0.0, 1.0, 0.12, '#2a6a38')]})
    t = m.bone('tail', [0, 12, 8], body)
    cb(t, 0, 11, 11, 4, 3, 7, 'scale')
    cb(t, 0, 11, 15, 2, 2, 3, 'scale_d')
    m.hitbox(1.4, 1.4)
    fl = lambda L, a: {'wing_r': {'rotation': loop([[0, 0, a], [0, 0, -a * 0.7]], L)}, 'wing_l': {'rotation': loop([[0, 0, -a], [0, 0, a * 0.7]], L)},
                       'body': {'position': loop([[0, 0, 0], [0, 1, 0]], L)}, 'tail': {'rotation': loop([[0, 10, 0], [0, -10, 0]], L * 2)}}
    m.anim('idle', 1.6, 'loop', fl(0.8, 30))
    m.anim('walk', 1.0, 'loop', fl(0.5, 40))
    a = fl(0.4, 25)
    a['mouth'] = {'rotation': [(0, [0, 0, 0]), (0.1, [25, 0, 0]), (0.4, [20, 0, 0])], 'scale': [(0, S(1)), (0.1, S(1.2)), (0.25, S(1.1)), (0.4, S(1.2))]}
    a['head'] = {'rotation': [(0, [0, 0, 0]), (0.1, [6, 0, 0]), (0.4, [6, 0, 0])]}
    m.anim('attack', 0.4, 'once', a)
    troop_tail(m, death={'root': {'position': [(0, [0, 0, 0]), (0.6, [0, -10, 0]), (0.9, [0, -14, 0])], 'rotation': [(0, [0, 0, 0]), (0.9, [20, 0, 90])]}})
    return m


# =================================================================== bomb
def bomb():
    m = mk('clash_bomb')
    m.mats_({'bomb': ('#2a2a30', 'metal'), 'bomb_l': ('#3a3a42', 'metal'), 'iron': ('#7a7a80', 'metal'), 'fuse': ('#6a5636', 'rope'), 'spark': ('#ffd040', 'glow'),
             'flame': ('#ff8a20', 'glow'), 'core': ('#fff8e0', 'glow')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 0, 0], root)
    hl = [prect(1, 1, 2, 2, '#6a6a74', 12, 12)]
    cb(body, 0, 1, 0, 10, 10, 10, 'bomb')
    cb(body, 0, 2, 0, 13, 8, 8, 'bomb_l', decals={'north': hl, 'east': hl})
    cb(body, 0, 2, 0, 8, 8, 13, 'bomb_l', decals={'north': hl, 'east': hl})
    cb(body, 0, 0, 0, 8, 12, 8, 'bomb')
    cb(body, 0, 12, 0, 4, 1.5, 4, 'iron')
    cb(body, 0, 13.5, 0, 1, 2.0, 1, 'fuse')
    cb(body, 0.5, 15.3, 0, 1, 1.6, 1, 'fuse')                                              # fuse bending over
    sp = m.bone('spark', [1.0, 17.4, 0], body)
    cb(sp, 1.0, 16.4, 0, 2.6, 2.6, 2.6, 'flame')                                           # orange glow
    cb(sp, 1.0, 16.9, 0, 1.6, 1.6, 1.6, 'spark')                                           # hot yellow core
    cb(sp, 1.0, 17.3, 0, 0.8, 0.8, 0.8, 'core')                                            # white-hot centre
    for (dx, dy, dz) in ((1.9, 1.9, 0.6), (-0.9, 2.3, -0.8), (0.4, 2.8, 1.4), (2.3, 0.6, -1.2)):
        cb(sp, 1.0 + dx, 16.9 + dy, dz, 0.5, 0.5, 0.5, 'spark')                             # flying embers
    m.hitbox(0.8, 0.8)
    m.anim('idle', 0.6, 'loop', {'spark': {'scale': loop([S(1), S(1.4), S(0.85), S(1.25)], 0.6), 'rotation': loop([[0, 0, 0], [0, 90, 0], [0, 180, 0], [0, 270, 0]], 0.6)}, 'body': {'scale': loop([S(1), [1.04, 0.97, 1.04]], 0.6)}})
    m.anim('spawn', 0.5, 'once', {'root': {'position': [(0, [0, 20, 0]), (0.25, [0, 0, 0]), (0.35, [0, 2, 0]), (0.5, [0, 0, 0])]},
                                  'body': {'scale': [(0, S(1)), (0.25, [1.15, 0.8, 1.15]), (0.4, S(1))]}})
    m.anim('death', 0.3, 'hold', {'body': {'scale': [(0, S(1)), (0.15, S(1.4)), (0.2, S(0.01))]}})
    return m


ALL = {'elixir_collector': elixir_collector, 'guard': guard, 'wall_breaker': wall_breaker, 'bowler': bowler, 'boulder': boulder,
       'inferno_dragon': inferno_dragon, 'bomb': bomb}

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
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad)
