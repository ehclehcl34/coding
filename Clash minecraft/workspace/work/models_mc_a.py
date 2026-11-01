"""MC-style models (letter A): princess / ice wizard / magic archer / hunter / bandit.
Vanilla-Minecraft mob rig (head 8x8x8, body 8x12x4, arms 4x12x4 or slim 3x12x4, legs 4x12x4), density 1.0
(1 texel = 1 px), flat painted faces, hair/hats as thin outer-layer slabs, few cubes. Front = north (-Z), origin = feet centre.
Usage: python3 models_mc_a.py <model_tools dir> <out dir> [fn ...]"""
import sys, os, json
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def kf(*pts):
    return [(t, list(v)) for t, v in pts]


def pixmap(rows, pal):
    """rows of chars (top->bottom, left->right as seen from the front) -> pixel decals; '.' = leave"""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                out.append(('px', x, y, pal[ch]))
    return out


def common_tail(m, root='root', hit_bone='body'):
    m.anim('spawn', 0.5, 'once', {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                         'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                         'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})


def new_model(name):
    m = Model(name, density=1.0)
    m.round = False                      # no bevel stacks: plain vanilla boxes
    return m


def rig(m, leg_h=12, body_h=12, body_w=8, body_d=4, arm_w=4, head=8, leg_w=4,
        leg='pants', body='shirt', arm='shirt', hand='skin', head_mat='skin', face=None, body_dec=None, tc_body=False, tc_legs=False, tc_arms=False):
    """player/zombie rig. Returns bones dict. Arms hang from the shoulder; the last 3 px of an arm is the hand."""
    root = m.bone('root', [0, 0, 0])
    B = {'root': root}
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * leg_w / 2, leg_h, 0], root)
        tgt = m.bone('tc_leg_' + side, [sx * leg_w / 2, leg_h, 0], lg) if tc_legs else lg
        cb(tgt, sx * leg_w / 2, 0, 0, leg_w, leg_h, 4, 'cloth' if tc_legs else leg)
        B['leg_' + side] = lg
    bd = m.bone('body', [0, leg_h, 0], root)
    tb = m.bone('tc_body', [0, leg_h, 0], bd) if tc_body else bd
    cb(tb, 0, leg_h, 0, body_w, body_h, body_d, 'cloth' if tc_body else body, decals={'north': body_dec} if body_dec else None)
    B['body'] = bd
    top = leg_h + body_h
    hd = m.bone('head', [0, top, 0], bd)
    cb(hd, 0, top, 0, head, head, head, head_mat, decals={'north': face} if face else None)
    B['head'] = hd
    for sx, side in ((1, 'r'), (-1, 'l')):
        ax = sx * (body_w / 2 + arm_w / 2)
        a = m.bone('arm_' + side, [ax, top - 2, 0], bd)
        ta = m.bone('tc_arm_' + side, [ax, top - 2, 0], a) if tc_arms else a
        cb(ta, ax, top - body_h + 3, 0, arm_w, body_h - 3, 4, 'cloth' if tc_arms else arm)
        cb(a, ax, top - body_h, 0, arm_w, 3, 4, hand)
        B['arm_' + side] = a
    m.top = top
    return B


def hair_layer(bone, top, s, mat, back=8, side=8, fringe=1, i=0.5, front_sides=0):
    """outer-layer hair/hat made of thin slabs around an s-cube head whose top is at `top`"""
    w = s + 2 * i
    cb(bone, 0, top, 0, w, i * 2, w, mat)                                            # top
    if back:
        cb(bone, 0, top - back, s / 2 + i / 2, w, back, i, mat)                      # back
    for sx in (1, -1):
        if side:
            cb(bone, sx * (s / 2 + i / 2), top - side, 0, i, side, w, mat)           # sides
    if fringe:
        cb(bone, 0, top - fringe, -s / 2 - i / 2, w, fringe, i, mat)                 # fringe on the forehead
    for sx in (1, -1):
        if front_sides:
            cb(bone, sx * (s / 2 - 0.5), top - front_sides, -s / 2 - i / 2, 1.0 + i, front_sides, i, mat)


def walk_anim(m, L=0.8, amp=30, arm_amp=30, extra=None, arms=True):
    w = {'leg_r': {'rotation': loop([[amp, 0, 0], [-amp, 0, 0]], L)}, 'leg_l': {'rotation': loop([[-amp, 0, 0], [amp, 0, 0]], L)},
         'body': {'position': loop([[0, 0, 0], [0, 0.6, 0], [0, 0, 0], [0, 0.6, 0]], L)}}
    if arms:
        w['arm_r'] = {'rotation': loop([[-arm_amp, 0, 0], [arm_amp, 0, 0]], L)}
        w['arm_l'] = {'rotation': loop([[arm_amp, 0, 0], [-arm_amp, 0, 0]], L)}
    w.update(extra or {})
    m.anim('walk', L, 'loop', w)


def make_bow(m, parent, hx, hy, hz, wood, tip, string, tc_limbs=False):
    """vertical pixel bow in the y-z plane held at (hx, hy, hz); limbs curve forward (-z)"""
    bow = m.bone('bow', [hx, hy, hz], parent)
    lb = m.bone('tc_bow_limbs', [hx, hy, hz], bow) if tc_limbs else bow
    cb(bow, hx, hy - 1.5, hz, 1, 3, 1, 'grip')
    for sy in (1, -1):
        cb(lb, hx, hy + sy * 3.5 - 2, hz - 1, 1, 4, 1, wood)
        cb(lb, hx, hy + (5.5 if sy > 0 else -8.5), hz, 1, 3, 1, wood)
        cb(bow, hx, hy + (8.5 if sy > 0 else -9.5), hz + 0.5, 1, 1, 1, tip)
    cb(lb, hx, hy - 9, hz + 1, 0.2, 18, 0.2, string)
    at = m.bone('arrow_tip', [hx, hy, hz - 2], bow)
    cb(at, hx, hy - 0.5, hz - 2.5, 1, 1, 1, tip)
    return bow


def archer_anims(m, idle_extra=None):
    idle = {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
            'head': {'rotation': loop([[0, 6, 0], [0, 0, 0], [0, -6, 0], [0, 0, 0]], 2.0)},
            'arm_l': {'rotation': loop([[-10, 0, -3], [-14, 0, -4]], 2.0)}, 'bow': {'rotation': loop([[10, 0, 0], [14, 0, 0]], 2.0)},
            'arm_r': {'rotation': loop([[0, 0, 3], [-4, 0, 4]], 2.0)}}
    idle.update(idle_extra or {})
    m.anim('idle', 2.0, 'loop', idle)
    walk_anim(m, 0.8, extra={'arm_l': {'rotation': loop([[-6, 0, -3], [-20, 0, -3]], 0.8)}, 'bow': {'rotation': loop([[6, 0, 0], [20, 0, 0]], 0.8)}})
    att = {'body': {'rotation': kf((0, [0, 0, 0]), (0.15, [0, -30, 0]), (0.36, [-4, -34, 0]), (0.42, [2, -28, 0]), (0.6, [0, 0, 0]))},
           'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.15, [-86, 18, 0]), (0.36, [-88, 22, 0]), (0.42, [-80, 18, 0]), (0.6, [0, 0, 0]))},
           'bow': {'rotation': kf((0, [0, 0, 0]), (0.15, [86, 0, 0]), (0.36, [88, 0, 0]), (0.42, [70, 0, 0]), (0.5, [86, 0, 0]), (0.6, [0, 0, 0]))},
           'arm_r': {'rotation': kf((0, [0, 0, 0]), (0.15, [-86, 40, 0]), (0.36, [-84, 62, 0]), (0.42, [-70, 10, 30]), (0.6, [0, 0, 0])),
                     'position': kf((0, [0, 0, 0]), (0.15, [0, 0, -1]), (0.36, [0, 0, 2.5]), (0.42, [0, 0, 2.5]), (0.6, [0, 0, 0]))},
           'arrow_tip': {'scale': kf((0, [1, 1, 1]), (0.36, [1.6, 1.6, 1.6]), (0.42, [2.6, 2.6, 2.6]), (0.5, [0.6, 0.6, 0.6]), (0.6, [1, 1, 1]))},
           'head': {'rotation': kf((0, [0, 0, 0]), (0.15, [0, 26, 0]), (0.42, [0, 26, 0]), (0.6, [0, 0, 0]))}}
    m.anim('attack', 0.6, 'once', att)
    common_tail(m)


# =================================================================== PRINCESS
def princess():
    m = new_model('clash_princess')
    m.mats_({'skin': ('#f2c8a8', 'skin'), 'hair': ('#2a1c1a', 'hair'), 'cloth': ('#efefef', 'cloth'), 'boot': ('#6a4228', 'leather'),
             'glove': ('#7a4e30', 'leather'), 'armor': ('#c6ccd4', 'metal'), 'chain': ('#8c919c', 'metal'), 'gold': ('#f4c23a', 'metal'),
             'gem': ('#e83850', 'gem'), 'wood': ('#8e5a2e', 'wood'), 'grip': ('#4a2e1a', 'leather'), 'string': ('#f2ead6', 'plain'),
             'quiver': ('#7a4e30', 'leather'), 'feather': ('#f4f0e8', 'plain')})
    face = pixmap(['HHHHHHHH', 'HHHHHHHS', 'HBBSSBBH', 'SWESSEWS', 'SSSSSSSS', 'SSSNSSSS', 'SSPMMPSS', 'SSSSSSSS'],
                  {'H': '#2a1c1a', 'B': '#1a1210', 'W': '#ffffff', 'E': '#6a3a22', 'N': '#d8a888', 'M': '#c84a5a', 'P': '#f0a8a0'})
    B = rig(m, leg_h=9, body_h=10, body_w=8, arm_w=3, face=face, tc_body=True, tc_legs=True, tc_arms=True, hand='glove')
    t = m.top
    for sx in (1, -1):                                                         # boots
        cb(B['leg_r' if sx > 0 else 'leg_l'], sx * 2, 0, -0.25, 4.4, 3, 4.5, 'boot')
    cb(B['body'], 0, 12, 0, 8.6, 4.5, 4.6, 'armor', decals={'north': [('rect', 0.45, 0, 0.55, 1, '#9aa0aa')]})   # chestplate
    cb(B['body'], 0, 10, 0, 8.4, 2, 4.4, 'chain')                                # chain mail
    cb(B['body'], 0, 9.5, 0, 8.6, 1, 4.6, 'grip')                                # belt
    q = m.bone('quiver', [0, 14, 2.5], B['body'])                               # quiver on the back
    cb(q, -1, 11, 3, 3, 7, 2, 'quiver', rot=('z', 22.5))
    cb(q, -2.6, 17.5, 3, 1, 2, 1, 'feather', rot=('z', 22.5))
    hd = B['head']
    hair_layer(hd, t + 8, 8, 'hair', back=6, side=5, fringe=1)                  # dark bob
    cr = m.bone('crown', [0, t + 9, 0], hd)
    cb(cr, 0, t + 9, 0, 5, 1, 5, 'gold', decals={'north': [('px', 2, 0, '#e83850')]})
    for x, z in ((-2, -2), (0, -2), (2, -2), (-2, 2), (2, 2)):
        cb(cr, x, t + 10, z, 1, 1, 1, 'gold')
    make_bow(m, B['arm_l'], -5.5, 8.5, -1, 'wood', 'gold', 'string')
    m.hitbox(0.7, 1.75)
    archer_anims(m)
    return m


# =================================================================== ICE WIZARD
def ice_wizard():
    m = new_model('clash_ice_wizard')
    m.mats_({'skin': ('#e6d0cc', 'skin'), 'hair': ('#2fb6ec', 'hair'), 'hair_l': ('#7ad8f8', 'hair'), 'cloth': ('#efefef', 'cloth'),
             'coat': ('#7a4e30', 'leather'), 'coat_d': ('#5a3820', 'leather'), 'boot': ('#4e3220', 'leather'), 'gold': ('#e0b040', 'metal'),
             'fur': ('#ddd5c8', 'fur'), 'ice': ('#8fe8ff', 'glow'), 'ice_w': ('#e8fcff', 'glow')})
    face = pixmap(['HHHHHHHH', 'SSSSSSSS', 'BBBSSBBB', 'SGGSSGGS', 'SSSNNSSS', 'SHHHHHHS', 'SHSMMSHS', 'SHSSSSHS'],
                  {'H': '#2fb6ec', 'B': '#c8f0ff', 'G': '#7ff4ff', 'N': '#d0b0aa', 'M': '#5a2a2a'})
    B = rig(m, leg_h=9, body_h=11, body_w=9, body_d=5, arm_w=4, face=face, tc_body=True, tc_legs=True, arm='coat', hand='skin')
    t = m.top
    for sx, side in ((1, 'r'), (-1, 'l')):
        cb(B['leg_' + side], sx * 2, 0, -0.25, 4.4, 3, 4.6, 'boot')
        cb(B['body'], sx * 3.9, 9, 0.2, 1.4, 11, 5.6, 'coat')                  # open leather coat
        tf = m.bone('frost_' + side, [sx * 6.5, 7.5, -1], B['arm_' + side])     # icy glow in the hands
        cb(tf, sx * 6.5, 6.5, -1.5, 2, 2, 2, 'ice')
        cb(tf, sx * 6.5, 8.5, -1.5, 1, 2, 1, 'ice_w')
    cb(B['body'], 0, 9, 2.75, 9.6, 11, 0.6, 'coat')
    cb(B['body'], 0, 19, 0, 9.8, 1.5, 5.8, 'fur')                              # fur collar
    cb(B['body'], 0, 13, 0, 9.4, 1.5, 5.4, 'cloth')                             # team belt (part of the suit)
    cb(B['body'], 0, 13, -2.75, 2, 1.5, 0.4, 'gold')
    hd = B['head']
    hair_layer(hd, t + 8, 8, 'hair', back=4, side=3, fringe=0)
    for x, z, h in ((-3, -3, 3), (-1, -2, 4), (1, -3, 3), (3, -2, 4), (-2, 1, 3), (2, 1, 3), (0, 2, 4), (-3, 3, 2), (3, 3, 2)):   # spiky tufts
        cb(hd, x, t + 9, z, 2, h, 2, 'hair' if h > 3 else 'hair_l')
    m.hitbox(0.8, 1.85)
    hold = lambda s, a=0: [-35 + a, 0, s * 6]
    m.anim('idle', 2.0, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
                                 'head': {'rotation': loop([[0, 6, 0], [0, 0, 0], [0, -6, 0], [0, 0, 0]], 2.0)},
                                 'arm_r': {'rotation': loop([hold(1), hold(1, -5)], 2.0)}, 'arm_l': {'rotation': loop([hold(-1, -5), hold(-1)], 2.0)},
                                 'frost_r': {'scale': loop([[1, 1, 1], [1.25, 1.25, 1.25]], 0.6)}, 'frost_l': {'scale': loop([[1.25, 1.25, 1.25], [1, 1, 1]], 0.6)}})
    walk_anim(m, 0.8, arms=False, extra={'arm_r': {'rotation': loop([hold(1, 10), hold(1, -10)], 0.8)}, 'arm_l': {'rotation': loop([hold(-1, -10), hold(-1, 10)], 0.8)}})
    att = {}
    for side, s in (('r', 1), ('l', -1)):
        att['arm_' + side] = {'rotation': kf((0, hold(s)), (0.2, [-10, 0, s * 4]), (0.3, [-92, 0, -s * 8]), (0.42, [-82, 0, -s * 6]), (0.6, hold(s)))}
        att['frost_' + side] = {'scale': kf((0, [1, 1, 1]), (0.2, [1.4, 1.4, 1.4]), (0.3, [2.4, 2.4, 2.4]), (0.38, [0.6, 0.6, 0.6]), (0.6, [1, 1, 1]))}
    att['body'] = {'rotation': kf((0, [0, 0, 0]), (0.2, [-8, 0, 0]), (0.3, [8, 0, 0]), (0.6, [0, 0, 0]))}
    m.anim('attack', 0.6, 'once', att)
    common_tail(m)
    return m


# =================================================================== MAGIC ARCHER
def magic_archer():
    m = new_model('clash_magic_archer')
    m.mats_({'skin': ('#eeb08c', 'skin'), 'hair': ('#8c8e96', 'hair'), 'hair_w': ('#f0f0f2', 'hair'), 'cloth': ('#efefef', 'cloth'),
             'tunic': ('#1f4a2c', 'cloth'), 'pants': ('#2e2a28', 'cloth'), 'boot': ('#4a3220', 'leather'), 'leather': ('#6a4628', 'leather'),
             'bowtc': ('#efefef', 'glow'), 'magic': ('#4ef0e8', 'glow'), 'grip': ('#3a2a20', 'leather'), 'brass': ('#c8a040', 'metal')})
    face = pixmap(['HWHHWHHW', 'HHHHHHHH', 'BBBSSBBB', 'SWGSSGWS', 'SSSNNSSS', 'SSSSSSSS', 'SSMMMMSS', 'SSSSSSSS'],
                  {'H': '#8c8e96', 'W': '#f0f0f2', 'B': '#1a1a1e', 'G': '#2ff0e0', 'N': '#d8906e', 'M': '#8a3a32'})
    B = rig(m, face=face, body='tunic', arm='tunic', leg='pants', hand='leather',
            body_dec=[('rect', 0.44, 0, 0.56, 1, '#14321e'), ('rect', 0, 0.72, 1, 0.8, '#6a4628'), ('px', 4, 9, '#c8a040')])
    t = m.top
    for sx, side in ((1, 'r'), (-1, 'l')):
        cb(B['leg_' + side], sx * 2, 0, -0.25, 4.4, 4, 4.5, 'boot')
    tc = m.bone('tc_cape', [0, t, 2], B['body'])                               # team cape
    cb(tc, 0, 4, 2.4, 8.4, 20, 0.8, 'cloth')
    cb(tc, 0, t - 1, 0, 8.6, 1.4, 4.8, 'cloth')
    q = m.bone('quiver', [0, 20, 3], B['body'])
    cb(q, 1.5, 16, 3.4, 2.5, 8, 2, 'leather', rot=('z', -22.5))
    cb(q, 3.4, 24, 3.4, 1, 2, 1, 'magic', rot=('z', -22.5))
    hd = B['head']
    hair_layer(hd, t + 8, 8, 'hair', back=6, side=4, fringe=0)
    cb(hd, 0, t + 8.5, -2.5, 6, 1.5, 3, 'hair_w')                              # swept-back white streak quiff
    cb(hd, -2.5, t + 8.5, 1.5, 1, 1, 5, 'hair_w')
    make_bow(m, B['arm_l'], -6, 10, -1, 'bowtc', 'magic', 'magic', tc_limbs=True)
    m.hitbox(0.7, 2.0)
    archer_anims(m, idle_extra={'arrow_tip': {'scale': loop([[1, 1, 1], [1.3, 1.3, 1.3]], 0.5)}})
    return m


# =================================================================== HUNTER
def hunter():
    m = new_model('clash_hunter')
    m.mats_({'skin': ('#eea888', 'skin'), 'cloth': ('#efefef', 'cloth'), 'fur': ('#efefef', 'fur'), 'tail_d': ('#3a3430', 'fur'), 'tail_l': ('#8a7a6a', 'fur'),
             'leather': ('#7a5232', 'leather'), 'pants': ('#6a4a30', 'cloth'), 'boot': ('#3e2a1c', 'leather'), 'belt': ('#3a2618', 'leather'),
             'iron': ('#5a5c64', 'metal'), 'wood': ('#7a4a24', 'wood'), 'brass': ('#d0a040', 'metal'), 'flash': ('#ffb030', 'glow'),
             'nose': ('#ff8676', 'skin')})
    face = pixmap(['SSSSSSSSS', 'BBBBSBBBB', 'SWESSSEWS', 'SSSRRRSSS', 'SKKKKKKKS', 'KKKKKKKKK', 'KGGMMMGGK', 'SGGGGGGGS', 'SSGGGGGSS'],
                  {'B': '#1e1c1c', 'W': '#ffffff', 'E': '#3a2a1a', 'R': '#ff8676', 'K': '#242222', 'G': '#b8b6b0', 'M': '#6a2a2a'})
    B = rig(m, leg_h=12, body_h=14, body_w=10, body_d=6, arm_w=4, head=9, face=face, tc_body=True, tc_arms=True, leg='pants', hand='leather')
    t = m.top
    for sx, side in ((1, 'r'), (-1, 'l')):
        cb(B['leg_' + side], sx * 2, 0, -0.25, 4.4, 4, 4.6, 'boot')
        cb(B['body'], sx * 4.4, 12, 0.3, 1.4, 14, 6.6, 'leather')               # leather vest
    cb(B['body'], 0, 12, 3.1, 10.4, 14, 0.6, 'leather')
    cb(B['body'], 0, 13, 0, 10.6, 1.5, 6.6, 'belt')
    cb(B['body'], 0, 13, -3.3, 2, 1.5, 0.3, 'brass')
    hd = B['head']
    cb(hd, 0, t + 4.5, -4.9, 2, 2, 1, 'nose')                                  # big nose
    cb(hd, 0, t - 1.5, -4.0, 7, 2, 1.2, 'fur', faces={'north': 'beardm', 'south': 'beardm', 'east': 'beardm', 'west': 'beardm', 'up': 'beardm', 'down': 'beardm'})
    m.mat('beardm', '#b8b6b0', 'fur')
    cap = m.bone('tc_cap', [0, t + 9, 0], hd)                                   # team coonskin cap
    cb(cap, 0, t + 7.5, 0, 10, 3.5, 10, 'fur')
    tail = m.bone('cap_tail', [0, t + 8, 5], hd)
    for i in range(4):
        cb(tail, 0, t + 6 - i * 2, 5.6, 2, 2, 2, 'tail_d' if i % 2 else 'tail_l')
    gun = m.bone('gun', [1, 13, -1], B['body'])
    cb(gun, 1, 10.5, 2, 2, 3, 6, 'wood')
    cb(gun, 1, 12, -3, 3, 3, 4, 'iron')
    for dx in (-0.75, 0.75):
        cb(gun, 1 + dx, 13.5, -11, 1.5, 1.5, 12, 'iron', decals={'north': [('px', 0, 0, '#101010')]})
    cb(gun, 1, 12, -8, 3, 1.5, 5, 'wood')
    mz = m.bone('muzzle', [1, 14.25, -17.5], gun)
    cb(mz, 1, 14, -17.2, 0.5, 0.5, 0.4, 'flash')
    m.hitbox(0.9, 2.2)
    ar, al = [-40, 0, -14], [-55, 40, 0]
    m.anim('idle', 2.0, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 2.0)},
                                 'head': {'rotation': loop([[0, 6, 0], [0, 0, 0], [0, -6, 0], [0, 0, 0]], 2.0)},
                                 'arm_r': {'rotation': loop([ar, [-42, 0, -14]], 2.0)}, 'arm_l': {'rotation': loop([al, [-57, 40, 0]], 2.0)},
                                 'cap_tail': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 2.0)}})
    walk_anim(m, 0.9, arms=False, extra={'arm_r': {'rotation': loop([ar, [-44, 0, -14]], 0.9)}, 'arm_l': {'rotation': loop([al, [-59, 40, 0]], 0.9)},
                                         'cap_tail': {'rotation': loop([[10, 0, 6], [10, 0, -6]], 0.45)}})
    m.anim('attack', 0.7, 'once', {
        'gun': {'rotation': kf((0, [0, 0, 0]), (0.14, [4, 0, 0]), (0.2, [-28, 0, 0]), (0.34, [-12, 0, 0]), (0.7, [0, 0, 0])),
                'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 3]), (0.34, [0, 0, 1.2]), (0.7, [0, 0, 0]))},
        'muzzle': {'scale': kf((0, [1, 1, 1]), (0.18, [1, 1, 1]), (0.21, [9, 9, 9]), (0.28, [5, 5, 5]), (0.34, [1, 1, 1]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.2, [-10, 0, 0]), (0.34, [-4, 0, 0]), (0.7, [0, 0, 0])),
                 'position': kf((0, [0, 0, 0]), (0.2, [0, 0, 1.6]), (0.7, [0, 0, 0]))},
        'arm_r': {'rotation': kf((0, ar), (0.2, [-58, 0, -14]), (0.34, [-50, 0, -14]), (0.7, ar))},
        'arm_l': {'rotation': kf((0, al), (0.2, [-72, 40, 0]), (0.34, [-64, 40, 0]), (0.7, al))}})
    common_tail(m)
    return m


# =================================================================== BANDIT
def bandit():
    m = new_model('clash_bandit')
    m.mats_({'skin': ('#f6c4a2', 'skin'), 'hair': ('#f0eeea', 'hair'), 'cloak': ('#2f5a34', 'cloth'), 'cloth': ('#efefef', 'cloth'),
             'belt': ('#6a4426', 'leather'), 'glove': ('#7a4e2e', 'leather'), 'pants': ('#3a3438', 'cloth'), 'boot': ('#3a2a22', 'leather'),
             'jack': ('#3a2e2a', 'leather'), 'jack_l': ('#6a5a4a', 'leather'), 'brass': ('#c8a040', 'metal')})
    face = pixmap(['HHHHHHHH', 'HHHHHHHH', 'KKKKKKKK', 'KWTKKTWK', 'SSSNNSSS', 'SSSSSSSS', 'SMWWWWMS', 'SSMMMMSS'],
                  {'H': '#f0eeea', 'K': '#141418', 'W': '#ffffff', 'T': '#2ac0a8', 'N': '#e0a888', 'M': '#8a2a32'})
    B = rig(m, leg_h=9, body_h=10, body_w=8, arm_w=3, face=face, tc_body=True, tc_arms=True, leg='pants', hand='glove',
            body_dec=None)
    t = m.top
    for sx, side in ((1, 'r'), (-1, 'l')):
        cb(B['leg_' + side], sx * 2, 0, -0.25, 4.4, 3.5, 4.5, 'boot')
    cb(B['body'], 0, 12, 0, 8.6, 1.4, 4.6, 'belt')
    cb(B['body'], 0, 12, -2.4, 1.4, 1.4, 0.3, 'brass')
    cb(B['body'], 0, 6, 2.4, 8.6, 13, 0.8, 'cloak')                            # green cloak
    cb(B['body'], 0, t - 1.5, 0, 8.8, 1.5, 4.8, 'cloak')
    tp = m.bone('tc_patch', [0, 13, 2.9], B['body'])
    cb(tp, 0, 12, 2.9, 3, 3, 0.2, 'cloth')
    hd = B['head']
    hair_layer(hd, t + 8, 8, 'hair', back=7, side=6, fringe=0)
    hair_layer(hd, t + 9, 9, 'cloak', back=6, side=5, fringe=0, i=0.5)      # hood over the hair
    pt = m.bone('ponytail', [0, t + 5, 4.8], hd)
    cb(pt, 0, t - 2, 5.2, 2, 7, 1.6, 'hair')
    club = m.bone('club', [5.5, 1 + 9 + 2, -1], B['arm_r'])                   # blackjack pointing forward from the fist
    cb(club, 5.5, 10.5, -4, 1, 1, 5, 'jack_l')
    cb(club, 5.5, 10, -8, 2, 2, 3, 'jack')
    m.hitbox(0.7, 1.75)
    m.anim('idle', 1.6, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 1.6)},
                                 'head': {'rotation': loop([[0, 8, 0], [0, 0, 0], [0, -8, 0], [0, 0, 0]], 1.6)},
                                 'arm_r': {'rotation': loop([[-20, 0, 4], [-24, 0, 4]], 1.6)}, 'club': {'rotation': loop([[-10, 0, 0], [-14, 0, 0]], 1.6)},
                                 'ponytail': {'rotation': loop([[4, 0, 4], [8, 0, -4]], 1.6)}})
    walk_anim(m, 0.6, amp=35, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-14, 0, 4]], 0.6)}, 'ponytail': {'rotation': loop([[20, 0, 6], [32, 0, -6]], 0.3)}})
    m.anim('attack', 0.5, 'once', {
        'arm_r': {'rotation': kf((0, [-20, 0, 4]), (0.18, [-165, 0, 10]), (0.28, [-50, 0, -4]), (0.36, [-35, 0, -6]), (0.5, [-20, 0, 4]))},
        'club': {'rotation': kf((0, [-10, 0, 0]), (0.18, [15, 0, 0]), (0.28, [140, 0, 0]), (0.36, [130, 0, 0]), (0.5, [-10, 0, 0]))},
        'body': {'rotation': kf((0, [0, 0, 0]), (0.18, [-10, 14, 0]), (0.28, [16, -10, 0]), (0.5, [0, 0, 0]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.18, [-40, 0, -24]), (0.28, [20, 0, -10]), (0.5, [0, 0, 0]))}})
    m.anim('dash', 0.4, 'once', {
        'body': {'rotation': kf((0, [0, 0, 0]), (0.08, [12, 0, 0]), (0.2, [42, 0, 0]), (0.32, [40, 0, 0]), (0.4, [0, 0, 0]))},
        'root': {'position': kf((0, [0, 0, 0]), (0.08, [0, -1, 1]), (0.2, [0, -1.5, -6]), (0.32, [0, -1, -8]), (0.4, [0, 0, 0]))},
        'leg_r': {'rotation': kf((0, [0, 0, 0]), (0.2, [-50, 0, 0]), (0.32, [-40, 0, 0]), (0.4, [0, 0, 0]))},
        'leg_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [45, 0, 0]), (0.32, [40, 0, 0]), (0.4, [0, 0, 0]))},
        'arm_r': {'rotation': kf((0, [-20, 0, 4]), (0.2, [50, 0, 10]), (0.4, [-20, 0, 4]))},
        'arm_l': {'rotation': kf((0, [0, 0, 0]), (0.2, [55, 0, -10]), (0.4, [0, 0, 0]))},
        'head': {'rotation': kf((0, [0, 0, 0]), (0.2, [-30, 0, 0]), (0.4, [0, 0, 0]))},
        'ponytail': {'rotation': kf((0, [4, 0, 0]), (0.2, [70, 0, 0]), (0.4, [4, 0, 0]))}})
    common_tail(m)
    return m


MODELS = [princess, ice_wizard, magic_archer, hunter, bandit]
CARD = {'clash_princess': 'princess', 'clash_ice_wizard': 'ice-wizard', 'clash_magic_archer': 'magic-archer', 'clash_hunter': 'hunter', 'clash_bandit': 'bandit'}


def compare(path, out_png):
    """3/4 render next to clash_hog_rider (same camera, same scale) and the card art"""
    from bbrender import render, sample
    from PIL import Image
    W = os.path.dirname(os.path.abspath(__file__))
    hog = json.load(open(os.path.join(W, 'pkg342/ClashMC_v3.4.2/models/base/clash_hog_rider.bbmodel')))
    doc = json.load(open(path))
    sheet = Image.new('RGBA', (1000, 360), (255, 255, 255, 255))
    sheet.paste(render(hog, 340, cam=(0.6, 0.5, -1.0), tint=(60, 110, 255)), (0, 10))
    sheet.paste(render(doc, 340, cam=(0.6, 0.5, -1.0), tint=(60, 110, 255), pose=sample(doc, 'idle', 0)), (340, 10))
    art = Image.open(os.path.join(os.path.dirname(W), 'refimg', CARD[doc['name']] + '.png')).convert('RGBA'); art.thumbnail((300, 340))
    sheet.paste(art, (690, 10), art)
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
        print(m.name, 'cubes', m.cubes_total - 1, 'split', n, 'bad', bad, [(a['name'], a['length']) for a in m.anims])
        compare(p, os.path.join(out, 'cmp_' + m.name.replace('clash_', '') + '.png'))
