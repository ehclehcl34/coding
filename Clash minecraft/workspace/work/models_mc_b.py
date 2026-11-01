"""ClashMC models in the user's vanilla-Minecraft mob style (like clash_hog_rider), batch B:
mega knight, giant skeleton, valkyrie, executioner, lumberjack, royal hog.
Player/zombie rig proportions (head 8, body 8x12x4, arms/legs 4x12x4 = 32 px), scaled for big units,
few big boxes, 1 texel = 1 px, faces painted flat on the head cube.
Usage: python3 models_mc_b.py <model_tools dir> <out dir> [--no-preview] [names...]"""
import sys, os
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def pix(rows, cmap):
    """8x8 (or any WxH) pixel painting -> decal rects. rows = list of strings, '.' = keep base texture"""
    H, W = len(rows), len(rows[0])
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.':
                out.append(('rect', x / W, y / H, (x + 1) / W, (y + 1) / H, cmap[ch]))
    return out


def new_model(name):
    m = Model(name, density=1.0)
    m.round = False                       # vanilla boxes: no bevels
    return m


class Rig:
    """player rig scaled by S. coordinates in rig units (32 tall), converted to px"""
    def __init__(self, m, S):
        self.m, self.S = m, S

    def bone(self, name, o, parent=None):
        return self.m.bone(name, [v * self.S for v in o], parent)

    def box(self, bone, x, y, z, w, h, d, mat, **kw):
        S = self.S
        if 'rot_origin' in kw:
            kw['rot_origin'] = [v * S for v in kw['rot_origin']]
        return cb(bone, x * S, y * S, z * S, w * S, h * S, d * S, mat, **kw)

    def humanoid(self, head_mat, body_mat, arm_mat, leg_mat, face=None, body_dec=None, arm_dec=None, leg_dec=None,
                 head_faces=None, arm_w=4, head=8):
        m = self.m
        root = m.bone('root', [0, 0, 0])
        legs = {}
        for sx, side in ((1, 'r'), (-1, 'l')):
            lg = self.bone('leg_' + side, [sx * 2, 12, 0], root)
            self.box(lg, sx * 2, 0, 0, 4, 12, 4, leg_mat, decals=leg_dec or {})
            legs[side] = lg
        body = self.bone('body', [0, 12, 0], root)
        self.box(body, 0, 12, 0, 8, 12, 4, body_mat, decals=body_dec or {})
        hd = self.bone('head', [0, 24, 0], body)
        self.box(hd, 0, 24, 0, head, head, head, head_mat, decals={'north': face or []}, faces=head_faces or {})
        arms = {}
        for sx, side in ((1, 'r'), (-1, 'l')):
            a = self.bone('arm_' + side, [sx * (4 + arm_w / 2 - 1), 22, 0], body)
            self.box(a, sx * (4 + arm_w / 2), 12, 0, arm_w, 12, 4, arm_mat, decals=arm_dec or {})
            arms[side] = a
        return root, body, hd, arms, legs


def common_tail(m, root='root', hit_bone='body', death=None, spawn=None):
    m.anim('spawn', 0.5, 'once', spawn or {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                                  'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death or {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                                  'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})


def mc_idle(m, L=2.4, extra=None):
    tr = {'arm_r': {'rotation': loop([[0, 0, 2], [-3, 0, 4]], L)}, 'arm_l': {'rotation': loop([[0, 0, -2], [3, 0, -4]], L)},
          'head': {'rotation': loop([[0, 10, 0], [0, 0, 0], [0, -10, 0], [0, 0, 0]], L * 2)},
          'body': {'position': loop([[0, 0, 0], [0, -0.3, 0]], L)}}
    tr.update(extra or {})
    m.anim('idle', L, 'loop', tr)


def mc_walk(m, L=0.8, amp=32, extra=None, arm_r=True):
    tr = {'leg_r': {'rotation': loop([[-amp, 0, 0], [amp, 0, 0]], L)}, 'leg_l': {'rotation': loop([[amp, 0, 0], [-amp, 0, 0]], L)},
          'arm_l': {'rotation': loop([[-amp * 0.8, 0, 0], [amp * 0.8, 0, 0]], L)}}
    if arm_r:
        tr['arm_r'] = {'rotation': loop([[amp * 0.8, 0, 0], [-amp * 0.8, 0, 0]], L)}
    tr.update(extra or {})
    m.anim('walk', L, 'loop', tr)


# palette helpers ------------------------------------------------------------
SKIN = '#e8b08c'; SKIN_D = '#c98e6c'


# =================================================================== Mega Knight
def mega_knight_old():
    m = new_model('clash_mega_knight')
    m.mats_({'iron': ('#3e424b', 'metal', {'rivets': True}), 'iron_d': ('#2a2d33', 'metal'), 'silver': ('#b4bcc6', 'metal', {'rivets': True}),
             'spike': ('#e2e7ee', 'metal'), 'cloth': ('#efefef', 'cloth'), 'gold': ('#e2b33c', 'metal')})
    r = Rig(m, 1.6)
    face = pix(["iiiiiiii",
                "irirrir.",
                "dddddddd",
                "dwbddbwd",
                "dssnnssd",
                "dkkddkkd",
                "igigigig",
                "iiiiiiii"], {'i': '#4c515b', 'r': '#9aa2ac', 'd': '#1c1e22', 'w': '#ffffff', 'b': '#3a9ae8', 's': '#e8b08c',
                              'n': '#c98e6c', 'k': '#141414', 'g': '#202226'})
    chest = pix(["........", ".ssssss.", ".s....s.", ".s.ss.s.", ".s....s.", ".ssssss.", "........", "........",
                 "gggggggg", "gggyyggg", "........", "........"], {'s': '#b4bcc6', 'g': '#5a5f69', 'y': '#e2b33c'})
    root, body, hd, arms, legs = r.humanoid('iron', 'iron', 'iron', 'iron_d', face=face, body_dec={'north': chest})
    tc = r.bone('tc_belt', [0, 12, 0], body)
    r.box(tc, 0, 11.6, 0, 8.6, 1.4, 4.6, 'cloth')
    r.box(tc, 0, 7.5, -2.3, 4, 4.2, 0.4, 'cloth')
    pl = r.bone('tc_plume', [0, 32, 0], hd)
    r.box(pl, 0, 32, 0, 1.2, 2.0, 1.2, 'cloth')
    r.box(pl, 0, 33.2, 1.6, 1.0, 1.2, 3.0, 'cloth')
    r.box(hd, 0, 32, 0, 2.0, 0.8, 2.0, 'silver')
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = arms[side]
        r.box(a, sx * 6.4, 21, 0, 6.2, 4, 6.2, 'silver')                    # big pauldron
        for z in (-1.8, 0, 1.8):
            r.box(a, sx * 6.8, 25, z, 1.2, 1.6, 1.2, 'spike')
        r.box(a, sx * 9.8, 22.4, 0, 1.4, 1.2, 1.2, 'spike')
        r.box(a, sx * 6, 7.0, 0, 6, 6, 6, 'silver')                         # spiked mace fist
        for (dx, dy, dz) in ((sx * 3.6, 9.4, 0), (0, 9.4, -3.6), (0, 9.4, 3.6), (0, 5.8, 0)):
            r.box(a, sx * 6 + dx, dy, dz, 1.4 if dx else 1.2, 1.2, 1.4 if dz else 1.2, 'spike')
    r.box(body, 0, 5.4, 0, 1.2, 1.2, 1.2, 'iron')                           # (crotch plate)
    m.hitbox(1.8, 3.3)
    mc_idle(m)
    mc_walk(m, 1.0, 22)
    smash = {s: {'rotation': [(0, [0, 0, 0]), (0.32, [-165, 0, -sg * 10]), (0.4, [-170, 0, -sg * 10]), (0.5, [-30, 0, -sg * 6]),
                              (0.62, [-28, 0, -sg * 4]), (0.8, [0, 0, 0])]} for s, sg in (('arm_r', 1), ('arm_l', -1))}
    smash['body'] = {'rotation': [(0, [0, 0, 0]), (0.36, [-10, 0, 0]), (0.5, [22, 0, 0]), (0.62, [18, 0, 0]), (0.8, [0, 0, 0])]}
    m.anim('attack', 0.8, 'once', smash)
    m.anim('jump', 0.9, 'once', {
        'root': {'position': [(0, [0, 0, 0]), (0.15, [0, -3, 0]), (0.3, [0, 14, -4]), (0.45, [0, 24, -8]), (0.6, [0, 0, -12]),
                              (0.7, [0, -2, -12]), (0.9, [0, 0, -12])],
                 'scale': [(0, [1, 1, 1]), (0.15, [1.12, 0.84, 1.12]), (0.3, [0.94, 1.1, 0.94]), (0.58, [1, 1, 1]), (0.64, [1.18, 0.8, 1.18]),
                           (0.78, [0.97, 1.04, 0.97]), (0.9, [1, 1, 1])]},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [20, 0, 10]), (0.4, [-165, 0, 10]), (0.6, [-30, 0, -10]), (0.9, [0, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [20, 0, -10]), (0.4, [-165, 0, -10]), (0.6, [-30, 0, 10]), (0.9, [0, 0, 0])]},
        'leg_r': {'rotation': [(0, [0, 0, 0]), (0.15, [-25, 0, 0]), (0.4, [-40, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [0, 0, 0])]},
        'leg_l': {'rotation': [(0, [0, 0, 0]), (0.15, [-25, 0, 0]), (0.4, [-40, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [0, 0, 0])]}})
    common_tail(m, spawn={'root': {'position': [(0, [0, 30, 0]), (0.25, [0, 0, 0]), (0.5, [0, 0, 0])],
                                   'scale': [(0, [1, 1, 1]), (0.25, [1, 1, 1]), (0.3, [1.18, 0.8, 1.18]), (0.42, [0.97, 1.04, 0.97]), (0.5, [1, 1, 1])]}},
                death={'root': {'rotation': [(0, [0, 0, 0]), (0.7, [-80, 0, 0]), (0.9, [-88, 0, 0])], 'position': [(0, [0, 0, 0]), (0.9, [0, -1, 4])]}})
    return m


# =================================================================== Giant Skeleton
PALM_ROT = -45
BOW_AIM = [90, 0, -30]


def giant_skeleton():
    """HQ vanilla-like CR giant skeleton: sculpted skull (real eye/nose cavities, cheekbones, single teeth),
    hollow ribcage of separate ribs, segmented spine, condyle joints, segmented curled fingers, toes,
    hollow open barrel with stave rim + rope straps, team ushanka with fur lining"""
    m = new_model('clash_giant_skeleton')
    m.mats_({'bone': ('#f2ecdd', 'bone'), 'bone_d': ('#d9d0bc', 'bone'), 'bone_k': ('#b2a891', 'bone'),
             'tooth': ('#f6f3ea', 'bone'), 'void': ('#141210', 'plain'),
             'fur': ('#efefef', 'cloth'), 'lining': ('#e2ebf0', 'fur'),
             'wood': ('#8a5a32', 'wood', {'planks': True}), 'wood_d': ('#5a3820', 'wood'),
             'hoop': ('#80848c', 'metal'), 'rope': ('#c9a265', 'rope'),
             'bomb': ('#2a2b31', 'soft'), 'cap': ('#44464e', 'metal'), 'spark': ('#ffe04a', 'glow'), 'flame': ('#ff8a1e', 'glow')})
    r = Rig(m, 2.0)
    B = r.box
    root = m.bone('root', [0, 0, 0])
    # ---------------------------------------------------------------- legs
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = r.bone('leg_' + side, [x, 11, 0], root)
        B(lg, x, 9.4, 0.3, 3.2, 1.8, 3.2, 'bone_d')                               # femoral head
        B(lg, x, 6.6, 0.3, 2.2, 3.0, 2.2, 'bone')                                 # femur shaft
        for dx in (-0.9, 0.9):
            B(lg, x + dx, 4.8, 0.3, 1.6, 1.9, 3.4, 'bone_d')                      # knee condyles
        B(lg, x, 5.2, -1.7, 1.6, 1.6, 0.8, 'bone')                                # kneecap
        B(lg, x, 1.4, 0.3, 2.2, 3.4, 2.2, 'bone')                                 # tibia
        B(lg, x + sx * 1.4, 1.6, 0.6, 0.8, 3.0, 0.8, 'bone_k')                    # fibula
        B(lg, x, 0.6, 0.3, 3.0, 0.9, 3.0, 'bone_d')                               # ankle
        B(lg, x, 0, 1.1, 2.4, 1.2, 2.0, 'bone_d')                                 # heel
        B(lg, x, 0, -1.0, 3.6, 0.9, 2.6, 'bone')                                  # metatarsals
        for i in range(4):
            B(lg, x - 1.35 + i * 0.9, 0, -2.9, 0.7, 0.7, 1.4, 'bone')              # toes
    # ---------------------------------------------------------------- pelvis + spine
    body = r.bone('body', [0, 11, 0], root)
    for sx in (1, -1):
        B(body, sx * 2.8, 9.6, 0.6, 3.4, 3.0, 1.2, 'bone_d', rot=('y', -sx * 22.5))  # iliac wings
    B(body, 0, 9.4, 1.4, 2.8, 3.2, 2.0, 'bone_k')                                 # sacrum
    B(body, 0, 9.0, -1.0, 4.4, 1.2, 1.2, 'bone')                                  # pubis
    for i in range(5):
        y = 12.4 + i * 1.0
        B(body, 0, y, 0.8, 2.6, 0.75, 2.6, 'bone')                                # lumbar vertebrae
        B(body, 0, y + 0.1, 2.4, 0.8, 0.6, 1.2, 'bone_d')                         # spinous process
    B(body, 0, 17.4, 2.0, 2.2, 7.6, 2.2, 'bone_k')                                # thoracic column
    # hollow ribcage: each rib = 2 sides + 2 front arcs + back
    for i in range(5):
        y = 17.2 + i * 1.65
        W, D = 10.0 + i * 1.1, 7.4
        h = 1.1
        for sx in (1, -1):
            B(body, sx * (W / 2 - 0.5), y, 0.0, 1.0, h, D - 0.4, 'bone')           # side
            fw = W / 2 - 1.6
            B(body, sx * (1.0 + fw / 2), y - (0.25 if i < 2 else 0), -D / 2 + 0.5, fw, h, 1.0, 'bone')   # front arc
        B(body, 0, y, D / 2 - 0.5, W - 1.4, h, 1.0, 'bone_d')                     # back
    B(body, 0, 18.0, -3.6, 1.8, 7.4, 1.0, 'bone_d')                               # sternum
    B(body, 0, 25.0, -3.6, 1.4, 0.8, 1.0, 'bone')                                 # manubrium
    for sx in (1, -1):
        B(body, sx * 4.4, 25.4, -2.6, 6.6, 1.2, 1.2, 'bone')     # clavicles
        B(body, sx * 3.6, 21.4, 4.1, 3.6, 4.4, 0.8, 'bone_d')   # shoulder blades
    # ---------------------------------------------------------------- skull
    hd = r.bone('head', [0, 26.4, -0.6], body)
    B(hd, 0, 27.4, -0.1, 10, 9, 8.6, 'bone', faces={'north': 'void'})            # cranium (front = dark cavity)
    fz = -5.1                                                                     # face plate centre z (1.4 thick)
    B(hd, 0, 33.4, fz, 10, 3.0, 1.4, 'bone')                                      # forehead
    B(hd, 0, 33.0, -5.95, 10.2, 0.9, 0.5, 'bone_d')                               # brow ridge
    for sx in (1, -1):
        B(hd, sx * 4.65, 29.4, fz, 0.7, 4.0, 1.4, 'bone')                         # outer socket rim
        B(hd, sx * 2.6, 29.4, fz, 3.4, 1.0, 1.4, 'bone')                          # under-socket cheekbone
        B(hd, sx * 4.0, 32.8, fz, 0.7, 0.6, 1.4, 'bone')                          # rounded socket corners
        B(hd, sx * 4.0, 30.4, fz, 0.7, 0.6, 1.4, 'bone')
        B(hd, sx * 1.2, 32.8, fz, 0.7, 0.6, 1.4, 'bone')
        B(hd, sx * 3.3, 29.2, -5.95, 2.6, 1.3, 0.4, 'bone')                       # cheekbone bump under the eye
        B(hd, sx * 4.6, 29.2, -5.4, 0.8, 1.6, 1.6, 'bone')                        # cheek corner (rounds the face edge)
        B(hd, sx * 5.1, 29.4, -2.6, 0.3, 1.2, 4.0, 'bone_d')                      # flush zygomatic arch
        B(hd, sx * 2.9, 27.4, fz, 4.2, 2.0, 1.4, 'bone')                          # maxilla
        B(hd, sx * 0.6, 28.6, fz, 0.4, 0.8, 1.4, 'bone')                          # nose cavity edges
    B(hd, 0, 30.4, fz, 1.6, 3.0, 1.4, 'bone')                                     # nasal bridge (splits eyes)
    B(hd, 0, 27.4, fz, 0.8, 1.2, 1.4, 'bone')                                     # under-nose
    for i in range(8):
        B(hd, -3.5 + i * 1.0, 26.0, -5.3, 0.9, 1.4, 0.8, 'tooth')                 # upper teeth
    jaw = r.bone('jaw', [0, 27.6, 2.2], hd)
    B(jaw, 0, 24.2, -5.0, 8.6, 1.8, 1.6, 'bone')                                  # chin
    for sx in (1, -1):
        B(jaw, sx * 4.3, 24.2, -1.6, 1.2, 1.8, 5.6, 'bone_d')                     # mandible sides
        B(jaw, sx * 4.3, 25.4, 1.6, 1.2, 2.8, 1.4, 'bone_d')                      # ramus
    for i in range(7):
        B(jaw, -3.0 + i * 1.0, 26.0, -5.1, 0.9, 1.0, 0.8, 'tooth')                # lower teeth
    # ---------------------------------------------------------------- ushanka (team) + fur lining
    hat = r.bone('tc_hat', [0, 35, -0.8], hd)
    B(hat, 0, 35.2, -0.4, 11.2, 3.8, 11.2, 'fur',
      decals={'north': pix(["...k.k...", ".........", "........."], {'k': '#cfcfcf'}),
              'up': pix(["....k....", "....k....", "kkkkkkkkk", "....k....", "....k...."], {'k': '#d8d8d8'})})
    B(hat, 0, 39.0, -0.4, 9.4, 0.9, 9.4, 'fur')
    B(hat, 0, 28.2, 5.0, 11.2, 7.0, 1.0, 'fur')                                   # back flap
    for sx in (1, -1):
        B(hat, sx * 6.3, 28.4, 0.0, 1.0, 6.8, 7.8, 'fur')                          # ear flaps
    fl = r.bone('lining', [0, 35, -0.8], hd)
    B(fl, 0, 33.8, -6.6, 12.4, 3.4, 2.4, 'lining')                                # thick front fold-up
    for i, (dx, dy, w) in enumerate(((-5.2, 0.0, 2.2), (-3.0, -0.4, 2.0), (-0.9, 0.1, 2.2), (1.2, -0.3, 2.0),
                                     (3.2, 0.2, 2.0), (5.3, -0.2, 2.0))):
        B(fl, dx, 33.4 + dy, -7.1, w, 1.0, 1.6, 'lining')                         # fluffy lower edge
        B(fl, dx + 0.3, 36.9 + (0.3 if i % 2 else 0), -6.9, w - 0.4, 0.7, 1.6, 'lining')   # fluffy top edge
    for sx in (1, -1):
        B(fl, sx * 6.1, 33.8, -3.0, 1.6, 3.4, 4.0, 'lining')                       # fold wraps round the sides
        B(fl, sx * 5.55, 28.4, 0.2, 0.5, 6.0, 7.4, 'lining')                       # inner flap fur
        B(fl, sx * 6.4, 27.2, 0.0, 1.8, 1.4, 8.4, 'lining')                        # thick flap bottom edge
        for dz in (-3.0, 0.2, 3.2):
            B(fl, sx * 6.4, 26.7, dz, 1.4, 0.6, 1.8, 'lining')                     # tufts hanging off the flap
        B(fl, sx * 6.4, 27.8, -4.1, 1.8, 7.0, 0.8, 'lining')                       # flap front edge
    B(fl, 0, 27.2, 5.0, 12.0, 1.4, 1.8, 'lining')                                 # back flap edge
    # ---------------------------------------------------------------- open barrel on the back
    bar = r.bone('barrel', [0, 22, 3.6], body)
    zc, y0, H = 10.0, 16.0, 13.0
    B(bar, 0, y0, zc - 4.6, 11.4, H, 1.0, 'wood')                                 # front wall
    B(bar, 0, y0, zc + 4.6, 11.4, H, 1.0, 'wood')                                 # back wall
    for sx in (1, -1):
        B(bar, sx * 5.2, y0, zc, 1.0, H, 8.2, 'wood')                             # side walls
    B(bar, 0, y0, zc, 9.4, 0.8, 8.2, 'wood_d')                                    # bottom
    for i, (dx, dz) in enumerate(((-3.2, -4.6), (1.8, -4.6), (5.2, 1.6), (-5.2, -1.4), (0.4, 4.6))):
        B(bar, dx, y0 + H, zc + dz, 1.0, 0.5 + (i % 2) * 0.3, 1.0, 'wood')        # uneven stave tops
    for y in (17.8, 26.4):                                                        # steel bands (4 strips each)
        B(bar, 0, y, zc - 5.2, 12.0, 1.2, 0.4, 'hoop')
        B(bar, 0, y, zc + 5.2, 12.0, 1.2, 0.4, 'hoop')
        for sx in (1, -1):
            B(bar, sx * 5.8, y, zc, 0.4, 1.2, 10.0, 'hoop')
    for sx in (1, -1):                                                            # rope straps
        x = sx * 5.2
        B(bar, x, 26.4, 0.4, 1.3, 1.3, 9.6, 'rope')                               # over the shoulder
        B(bar, x, 17.4, -4.6, 1.3, 9.6, 1.3, 'rope')                              # down the chest
        B(bar, x, 16.6, 0.4, 1.3, 1.3, 9.6, 'rope')                               # back under the arm
        B(bar, x, 15.0, -4.6, 1.2, 1.6, 1.2, 'rope')                              # knot
    # ---------------------------------------------------------------- arms
    # left: long hanging arm, clenched fist.  right: bent arm cradling a huge bomb in front of the belly
    x = -9.0
    a = r.bone('arm_l', [x, 24.8, 0], body)
    B(a, x, 22.4, 0, 3.6, 3.6, 3.6, 'bone_d')                                     # humeral head
    B(a, x, 17.4, 0, 2.2, 5.2, 2.2, 'bone')                                       # humerus
    for dz in (-0.8, 0.8):
        B(a, x, 15.4, dz, 3.2, 2.0, 1.4, 'bone_d')                                # elbow condyles
    B(a, x, 15.2, 1.6, 1.4, 1.4, 1.0, 'bone')                                     # olecranon
    for dz in (-0.6, 0.6):
        B(a, x, 10.6, dz, 1.0, 4.8, 1.0, 'bone')                                  # radius + ulna
    B(a, x, 9.8, 0, 3.0, 1.0, 3.2, 'bone_d')                                      # wrist
    B(a, x, 6.2, 0, 3.8, 3.6, 4.8, 'bone')                                        # big fist back
    for i, dz in enumerate((-1.8, -0.6, 0.6, 1.8)):
        B(a, x + 1.3, 5.2, dz, 1.8, 3.4, 1.1, 'bone_d')                           # curled fingers (knuckle row)
        B(a, x + 2.0, 4.2, dz, 1.0, 1.4, 1.1, 'bone')                             # fingertips tucked in
    B(a, x + 1.4, 7.4, -2.8, 1.4, 1.4, 1.8, 'bone_d')                             # thumb over the fist
    # right arm: wraps round the bomb's outer side, big splayed hand over its front-outer corner
    x = 9.4
    cx, cy, cz, R = 3.4, 18.4, -7.6, 5.6
    a = r.bone('arm_r', [x, 24.8, 0], body)
    B(a, x, 22.4, 0, 3.6, 3.6, 3.6, 'bone_d')                                     # humeral head
    B(a, x + 0.4, 16.8, -0.4, 2.2, 5.8, 2.2, 'bone')                              # humerus
    B(a, x + 0.4, 14.4, -0.6, 3.2, 2.6, 3.2, 'bone_d')                            # elbow knob
    B(a, x + 0.4, 14.8, 1.2, 1.4, 1.4, 1.0, 'bone')                               # olecranon
    for dy in (-0.6, 0.6):
        B(a, 9.3, 14.8 + dy, -5.6, 1.1, 1.1, 8.0, 'bone')                         # radius + ulna along the bomb's side
    B(a, 9.3, 14.0, -10.0, 2.6, 2.8, 1.8, 'bone_d')                               # wrist
    # palm: flat plate laid tangent on the bomb's front-outer diagonal (outside the surface)
    import math
    dgx, dgz = math.sqrt(0.5), -math.sqrt(0.5)
    dist = R + 0.75
    px_, pz_ = cx + dgx * dist, cz + dgz * dist
    B(a, px_, 14.2, pz_, 4.4, 5.0, 1.3, 'bone', rot=('y', PALM_ROT))
    def surf_z(fx, fy, pad):                                                      # front surface of the bomb at (x, y)
        q = R * R - (fy - cy) ** 2 - (fx - cx) ** 2
        return cz - math.sqrt(max(q, 0.0)) - pad
    ix = px_ - 2.2 * math.sqrt(0.5)                                               # inner edge of the palm
    for i, y in enumerate((14.8, 16.1, 17.4, 18.7)):
        ln = 2.8 if i in (1, 2) else 2.4
        yc = y + 0.55
        x1 = ix - ln / 2
        B(a, x1, y, surf_z(x1, yc, 0.55), ln, 1.1, 1.1, 'bone_d')                 # finger across the front
        x2 = ix - ln - 0.9
        B(a, x2, y + 0.05, surf_z(x2, yc, 0.5), 1.8, 1.0, 1.0, 'bone')            # fingertip hugging the curve
    ox, oz = px_ + 2.0 * math.sqrt(0.5), pz_ + 2.0 * math.sqrt(0.5)               # outer edge of the palm
    B(a, ox, 19.0, oz, 1.2, 2.6, 1.2, 'bone_d')                                   # thumb up the outer side
    B(a, ox - 0.4, 21.6, oz + 0.4, 1.0, 1.6, 1.0, 'bone')
    # huge round bomb: octagonal slices stacked into a sphere
    bomb = r.bone('bomb', [cx, cy, cz], a)
    hi = pix(["......", ".ww...", ".w....", "......", "......", "......"], {'w': '#666a74'})
    n = 9
    hgt = 2 * R / n
    for i in range(n):
        yc = -R + hgt * (i + 0.5)
        rr = max(1.0, (R * R - yc * yc) ** 0.5)
        dec = {'north': hi} if i == n // 2 + 1 else {}
        for rot in (None, ('y', 45)):
            B(bomb, cx, cy + yc - hgt / 2, cz, 2 * rr, hgt, 0.8 * rr, 'bomb', decals=dec if rot is None else {}, rot=rot)
            B(bomb, cx, cy + yc - hgt / 2, cz, 0.8 * rr, hgt, 2 * rr, 'bomb', rot=rot)
        B(bomb, cx, cy + yc - hgt / 2, cz, 1.5 * rr, hgt, 1.5 * rr, 'bomb', decals=dec)
    fx, fy, fzz = cx + 2.4, cy + R - 1.2, cz - 2.2                                # fuse on the top-front-outer side
    B(bomb, fx, fy, fzz, 2.6, 1.2, 2.6, 'cap')
    B(bomb, fx + 0.4, fy + 1.2, fzz - 0.4, 0.8, 1.4, 0.8, 'rope')
    B(bomb, fx + 0.9, fy + 2.4, fzz - 0.8, 0.8, 1.2, 0.8, 'rope', rot=('z', -22.5))
    fz_b = r.bone('fuse', [fx + 1.3, fy + 4.0, fzz - 0.8], bomb)
    B(fz_b, fx + 1.3, fy + 3.4, fzz - 0.8, 1.4, 1.4, 1.4, 'flame')
    B(fz_b, fx + 1.3, fy + 3.8, fzz - 0.8, 0.6, 2.0, 0.6, 'spark')
    m.hitbox(2.2, 4.2)
    stoop = {'body': {'rotation': loop([[10, 0, 0], [12, 0, 0]], 2.4), 'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.4)},
             'head': {'rotation': loop([[-8, 8, 0], [-8, 0, 0], [-8, -8, 0], [-8, 0, 0]], 4.8)},
             'jaw': {'rotation': loop([[0, 0, 0], [6, 0, 0], [0, 0, 0], [0, 0, 0]], 2.4)},
             'arm_r': {'rotation': loop([[0, 0, 0], [-3, 0, 0]], 2.4)}, 'arm_l': {'rotation': loop([[-10, 0, -3], [-14, 0, -5]], 2.4)}}
    fl_loop = {'scale': loop([[1, 1, 1], [1.5, 1.5, 1.5]], 0.3)}
    stoop['fuse'] = fl_loop
    m.anim('idle', 2.4, 'loop', stoop)
    mc_walk(m, 1.2, 22, arm_r=False, extra={'arm_r': {'rotation': loop([[0, 0, 0], [-4, 0, 0]], 0.6)}, 'fuse': fl_loop, 'body': {'rotation': loop([[12, 0, 0], [12, 0, 0]], 1.2)},
                               'head': {'rotation': loop([[-10, 0, 0], [-10, 0, 0]], 1.2)}})
    punch = {'arm_l': {'rotation': [(0, [0, 0, 0]), (0.35, [35, 0, -15]), (0.42, [38, 0, -15]), (0.55, [-95, 15, 0]),
                                    (0.7, [-90, 12, 0]), (1.0, [0, 0, 0])]},
             'arm_r': {'rotation': [(0, [0, 0, 0]), (0.4, [8, 0, 0]), (0.55, [-6, 0, 0]), (1.0, [0, 0, 0])]}}
    punch['body'] = {'rotation': [(0, [10, 0, 0]), (0.4, [0, -12, 0]), (0.55, [20, 14, 0]), (1.0, [10, 0, 0])]}
    punch['jaw'] = {'rotation': [(0, [0, 0, 0]), (0.5, [18, 0, 0]), (0.7, [0, 0, 0])]}
    m.anim('attack', 1.0, 'once', punch)
    common_tail(m, death={'root': {'scale': [(0, [1, 1, 1]), (0.5, [1, 0.9, 1]), (0.9, [1.05, 0.25, 1.05])]},
                          'jaw': {'rotation': [(0, [0, 0, 0]), (0.4, [25, 0, 0])]},
                          'bomb': {'scale': [(0, [1, 1, 1]), (0.05, [0, 0, 0])]}})      # game drops a separate clash_bomb
    return m



# =================================================================== Valkyrie
def valkyrie_old():
    m = new_model('clash_valkyrie')
    m.mats_({'skin': (SKIN, 'skin'), 'hair': ('#e8601c', 'hair'), 'cloth': ('#efefef', 'cloth'), 'leather': ('#6a4026', 'leather'),
             'wood': ('#7a4e2a', 'wood'), 'steel': ('#c0c7d0', 'metal'), 'steel_d': ('#7d838d', 'metal')})
    r = Rig(m, 1.0)
    face = pix(["hhhhhhhh",
                "hhhhhhhh",
                "hbbssbbh",
                "swbsswbs",
                "ssssssss",
                "sssnnsss",
                "ssmttmss",
                "ssssssss"], {'h': '#e8601c', 'b': '#b8400e', 's': SKIN, 'w': '#ffffff', 'n': SKIN_D, 'm': '#6a1414', 't': '#ffffff'})
    face = [(k, x0, y0, x1, y1, '#3a8ee0' if (c == '#ffffff' and 0.3 < y0 < 0.45 and int(round(x0 * 8)) in (2, 6)) else c) for (k, x0, y0, x1, y1, c) in face]
    boots = pix(["....", "....", "....", "....", "....", "....", "....", "....", "....", "bbbb", "bbbb", "bbbb"], {'b': '#6a4026'})
    root, body, hd, arms, legs = r.humanoid('skin', 'skin', 'skin', 'skin', face=face, leg_dec={f: boots for f in ('north', 'south', 'east', 'west')})
    suit = r.bone('tc_suit', [0, 12, 0], body)                                 # team-coloured suit
    r.box(suit, 0, 13.6, 0, 8.4, 9.0, 4.4, 'cloth')
    r.box(suit, 0, 9.4, 0, 8.6, 4.4, 4.6, 'cloth')
    r.box(body, 0, 13.4, 0, 8.6, 1.2, 4.6, 'leather', decals={'north': pix(["...yy..."], {'y': '#f0c040'})})
    r.box(hd, 0, 31.4, 0.4, 8.6, 1.4, 8.6, 'hair')                             # hair layer
    r.box(hd, 0, 24.4, 4.3, 8.6, 7.6, 0.8, 'hair')
    for sx in (1, -1):
        r.box(hd, sx * 4.3, 26.4, 1.2, 0.8, 5.0, 6.4, 'hair')
        r.box(hd, sx * 3.4, 16.4, -2.4, 1.8, 8.0, 1.8, 'hair', decals={'north': pix(["h", ".", "h", ".", "h", ".", "h", "."], {'h': '#b8400e'})})  # braids
    for sx, side in ((1, 'r'), (-1, 'l')):
        wb = r.bone('tc_wrist_' + side, [sx * 6, 14, 0], arms[side])
        r.box(wb, sx * 6, 13.4, 0, 4.4, 1.6, 4.4, 'cloth')
    axe = r.bone('axe', [6, 13, -0.2], arms['r'])
    r.box(axe, 6, 9, -0.2, 1, 18, 1, 'wood')                                   # haft through the hand
    r.box(axe, 6, 22, -0.2, 1.6, 3, 1.6, 'steel_d')
    for sz in (1, -1):
        r.box(axe, 6, 20, -0.2 + sz * 3.0, 0.8, 7, 4, 'steel')                 # double blades
        r.box(axe, 6, 19.2, -0.2 + sz * 5.2, 0.8, 8.6, 0.6, 'steel_d')
    m.hitbox(0.8, 2.0)
    mc_idle(m, extra={'arm_r': {'rotation': loop([[-10, 0, 4], [-14, 0, 5]], 2.4)}})
    mc_walk(m, 0.7, 30, arm_r=False, extra={'arm_r': {'rotation': loop([[-14, 0, 4], [-6, 0, 4]], 0.7)}})
    spin_t = [(0, [0, 0, 0]), (0.12, [0, 0, 0]), (0.245, [0, -90, 0]), (0.37, [0, -180, 0]), (0.495, [0, -270, 0]), (0.62, [0, -360, 0]), (0.8, [0, -360, 0])]
    m.anim('attack', 0.8, 'once', {
        'root': {'rotation': spin_t},
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, 82]), (0.62, [0, 0, 82]), (0.8, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -172]), (0.62, [0, 0, -172]), (0.8, [0, 0, 0])]},
        'arm_l': {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, -70]), (0.62, [0, 0, -70]), (0.8, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Executioner
def executioner_old():
    m = new_model('clash_executioner')
    m.mats_({'skin': ('#eeac94', 'skin'), 'hood': ('#232227', 'leather', {'stitch': False}), 'cloth': ('#efefef', 'cloth'),
             'leather': ('#2a2420', 'leather'), 'nose': ('#e0505a', 'skin'), 'wood': ('#4e3220', 'wood'),
             'steel': ('#c9d0d9', 'metal'), 'iron': ('#555a62', 'metal')})
    r = Rig(m, 1.2)
    face = pix(["kkkkkkkk",
                "kkkkkkkk",
                "kswkkswk",
                "kbwkkbwk",
                "kkkkkkkk",
                "ss....ss",
                "sttttttS",
                "ssmmmmss"], {'k': '#232227', 's': '#eeac94', 'w': '#ffffff', 'b': '#3a8ee0', 't': '#ffffff', 'm': '#6a1414', 'S': '#c89a8c'})
    gloves = pix(["....", "....", "....", "....", "....", "....", "....", "....", "gggg", "gggg", "gggg", "gggg"], {'g': '#2a2a2e'})
    boots = pix(["....", "....", "....", "....", "....", "....", "....", "....", "....", "kkkk", "kkkk", "kkkk"], {'k': '#1e1a18'})
    belly = pix(["........", "........", ".s....s.", "........", "........", "........", "....n...", "........",
                 "........", "........", "bbbbbbbb", "bbbyybbb"], {'s': '#c88a74', 'n': '#b06a58', 'b': '#2a2420', 'y': '#d9a63a'})
    root, body, hd, arms, legs = r.humanoid('skin', 'skin', 'skin', 'skin', face=face, body_dec={'north': belly},
                                            arm_dec={f: gloves for f in ('north', 'south', 'east', 'west')},
                                            head_faces={'up': 'hood', 'south': 'hood', 'east': 'hood', 'west': 'hood'})
    r.box(body, 0, 13.2, -2.4, 6, 5, 1.2, 'skin')                               # bare round belly
    r.box(hd, 0, 27.6, -4.6, 2, 1.6, 1.2, 'nose')                              # big red nose
    r.box(hd, 0, 26.8, 0.4, 8.6, 5.6, 8.0, 'hood', decals={})                  # hood layer (back/top), front open
    for sx, side in ((1, 'r'), (-1, 'l')):
        tp = r.bone('tc_pants_' + side, [sx * 2, 12, 0], legs[side])           # team-coloured pants
        r.box(tp, sx * 2, 3.2, 0, 4.4, 8.6, 4.4, 'cloth')
        r.box(legs[side], sx * 2, 0, -0.3, 4.4, 3.0, 4.8, 'leather')
    kilt = r.bone('tc_kilt', [0, 12, 0], body)                                 # team-coloured kilt
    r.box(kilt, 0, 9.0, 0, 8.8, 4.2, 4.8, 'cloth', decals={f: pix(["c.c.c.c."], {'c': '#c8c8c8'}) for f in ('north', 'south')})
    axe = r.bone('axe', [6, 13, -0.2], arms['r'])
    r.box(axe, 6, 9, -0.2, 1.2, 19, 1.2, 'wood')
    r.box(axe, 6, 21, -0.2, 2, 3.4, 2, 'iron')
    for sz in (1, -1):                                                         # big crescent double blades (one chipped)
        r.box(axe, 6, 19.0, -0.2 + sz * 3.6, 1, 8, 5, 'steel', decals={'east': pix(["s...", "....", "....", "...."] if sz < 0 else ["...."] * 4, {'s': '#8a929c'})})
        r.box(axe, 6, 18.0, -0.2 + sz * 6.4, 1, 10, 1, 'steel')
    m.hitbox(1.0, 2.4)
    mc_idle(m, extra={'arm_r': {'rotation': loop([[-8, 0, 4], [-12, 0, 5]], 2.4)}})
    mc_walk(m, 0.8, 28, arm_r=False, extra={'arm_r': {'rotation': loop([[-12, 0, 4], [-4, 0, 4]], 0.8)}})
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.18, [-150, 0, 10]), (0.26, [-80, 0, 0]), (0.66, [-80, 0, 0]), (0.8, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.26, [0, 0, 0]), (0.36, [-200, 0, 0]), (0.46, [-400, 0, 0]), (0.56, [-600, 0, 0]),
                             (0.66, [-720, 0, 0]), (0.8, [-720, 0, 0])],
                'position': [(0, [0, 0, 0]), (0.26, [0, 0, 0]), (0.46, [0, -38, 0]), (0.66, [0, 0, 0]), (0.8, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.18, [-8, 10, 0]), (0.28, [12, -10, 0]), (0.6, [6, 0, 0]), (0.8, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Lumberjack
def lumberjack_old():
    m = new_model('clash_lumberjack')
    m.mats_({'skin': (SKIN, 'skin'), 'fur': ('#efefef', 'fur'), 'pants': ('#5a3a24', 'cloth'), 'leather': ('#4a2c18', 'leather'),
             'wood': ('#a0703c', 'wood'), 'iron': ('#555a62', 'metal'), 'steel': ('#c4cad3', 'metal'), 'glass': ('#a24ae8', 'glow'),
             'cork': ('#a0703c', 'wood'), 'nose': ('#e0484a', 'skin')})
    r = Rig(m, 1.0)
    face = pix(["gggggggg",
                "ssssssss",
                "gwpssgss",
                "swpsswps",
                "sssnnsss",
                "goommoog",
                "gomttmog",
                "ggogggog"], {'g': '#ee8a2a', 'o': '#c86a1a', 's': SKIN, 'w': '#ffffff', 'p': '#8a3ad0', 'n': '#e0484a',
                              'm': '#5a1010', 't': '#f07a8a'})
    musc = pix(["........", "........", ".hh..hh.", "...gg...", "........", "...hh...", "........", "...hh...", "........",
                "bbbbbbbb", "bbbyybbb", "........"], {'h': '#d0987a', 'g': '#ee8a2a', 'b': '#4a2c18', 'y': '#c9a03a'})
    pants = pix(["pppp"] * 7 + ["ssss", "ssss", "ssss", "llll", "llll"], {'p': '#5a3a24', 's': SKIN, 'l': '#6a4026'})
    wrist = pix(["...."] * 8 + ["bbbb", "....", "....", "...."], {'b': '#4a2c18'})
    root, body, hd, arms, legs = r.humanoid('skin', 'skin', 'skin', 'skin', face=face, body_dec={'north': musc},
                                            leg_dec={f: pants for f in ('north', 'south', 'east', 'west')},
                                            arm_dec={f: wrist for f in ('north', 'south', 'east', 'west')})
    r.box(hd, 0, 24.2, -3.8, 6.6, 3.0, 1.0, 'leather', decals={'north': pix(["goommoog", "gomttmog", "ggogggog"],
                                                                                {'g': '#ee8a2a', 'o': '#c86a1a', 'm': '#5a1010', 't': '#f07a8a'})})  # beard volume
    r.box(hd, 0, 27.6, -4.6, 1.4, 1.2, 1.0, 'nose')
    hat = r.bone('tc_hat', [0, 30, 0], hd)                                     # team-coloured ushanka
    r.box(hat, 0, 30.2, 0, 8.8, 2.8, 8.8, 'fur')
    r.box(hat, 0, 30.0, -4.5, 8.8, 1.6, 0.8, 'fur')
    for sx in (1, -1):
        r.box(hat, sx * 4.5, 25.6, 0.4, 0.8, 5.0, 6.0, 'fur')
    fl = r.bone('flask', [-5, 24, 1], body)                                     # purple Rage flask on the shoulder
    r.box(fl, -5.4, 24, 1.0, 2.6, 3.0, 2.6, 'glass')
    r.box(fl, -5.4, 27, 1.0, 1.0, 1.0, 1.0, 'glass')
    r.box(fl, -5.4, 28, 1.0, 1.2, 0.8, 1.2, 'cork')
    axe = r.bone('axe', [6, 13, -0.2], arms['r'])
    R = dict(rot=('z', -22.5), rot_origin=[6, 13, -0.2])
    r.box(axe, 6, 9, -0.2, 1, 16, 1, 'wood', **R)
    r.box(axe, 6, 22, 0.4, 1.4, 2.4, 3, 'iron', **R)
    r.box(axe, 6, 21.2, -2.4, 0.8, 4.2, 2.6, 'steel', **R)
    m.hitbox(0.8, 2.0)
    mc_idle(m, L=1.6, extra={'arm_r': {'rotation': loop([[-10, 0, 3], [-16, 0, 4]], 1.6)}})
    mc_walk(m, 0.45, 42, arm_r=False, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-10, 0, 4]], 0.45)},
                                             'body': {'rotation': [(0, [10, 0, 0]), (0.45, [10, 0, 0])]}})
    m.anim('attack', 0.5, 'once', {
        'arm_r': {'rotation': [(0, [0, 0, 0]), (0.08, [-150, 0, 6]), (0.17, [-40, 0, -6]), (0.25, [-150, 0, 6]), (0.34, [-40, 0, -6]), (0.5, [0, 0, 0])]},
        'axe': {'rotation': [(0, [0, 0, 0]), (0.08, [135, 0, 0]), (0.34, [135, 0, 0]), (0.5, [0, 0, 0])]},
        'body': {'rotation': [(0, [0, 0, 0]), (0.08, [-8, 0, 0]), (0.17, [14, 0, 0]), (0.25, [-6, 0, 0]), (0.34, [14, 0, 0]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== Royal Hog
def royal_hog_old():
    m = new_model('clash_royal_hog')
    m.mats_({'pink': ('#f0a0a8', 'skin'), 'pink_d': ('#d88088', 'skin'), 'hoof': ('#5a3a2e', 'plain'), 'tusk': ('#f6f0dc', 'bone'),
             'steel': ('#a6aeb8', 'metal', {'rivets': True}), 'cloth': ('#efefef', 'cloth')})
    root = m.bone('root', [0, 0, 0])
    hoof = pix(["....", "....", "....", "....", "hhhh", "hhhh"], {'h': '#5a3a2e'})
    for name, x, z in (('fl_leg', -3, -5), ('fr_leg', 3, -5), ('bl_leg', -3, 5), ('br_leg', 3, 5)):
        lg = m.bone(name, [x, 6, z], root)
        cb(lg, x, 0, z, 4, 6, 4, 'pink', decals={f: hoof for f in ('north', 'south', 'east', 'west')})
    body = m.bone('body', [0, 10, 0], root)
    cb(body, 0, 6, 0, 10, 8, 16, 'pink')
    tail = m.bone('tail', [0, 12, 8], body)
    cb(tail, 0, 11, 8.6, 1.2, 1.2, 1.2, 'pink_d')
    head = m.bone('head', [0, 10, -8], body)
    face = pix(["........", "........", "........", ".wk..kw.", "........", "........", "........", "........"],
               {'w': '#ffffff', 'k': '#141414'})
    cb(head, 0, 6, -12, 8, 8, 8, 'pink', decals={'north': face})
    cb(head, 0, 6.6, -16.5, 4, 3, 1, 'pink_d', decals={'north': pix(["....", ".k.k", "...."], {'k': '#7a3a42'})})
    for sx in (1, -1):
        cb(head, sx * 3.0, 6.6, -16.6, 1, 2.6, 1, 'tusk')
    helm = pix(["ssssssss", "ssssssss", "sssssss.", "s.k.k.k.", "sk.k.k.s", "........", "........", "........"],
               {'s': '#a6aeb8', 'k': '#15171a'})
    cb(head, 0, 9.6, -12, 8.8, 4.8, 8.8, 'steel', decals={'north': pix(["ssssssss", "ssssssss", "skkskkss", "skkskkss", "ssssssss"],
                                                                         {'s': '#a6aeb8', 'k': '#15171a'})})   # knight helmet
    cb(head, 0, 14.4, -12, 1.6, 0.8, 8.8, 'steel')
    pl = m.bone('tc_plume', [0, 15, -12], head)                                # team-coloured plume
    cb(pl, 0, 15.2, -11, 1.4, 2.2, 1.4, 'cloth')
    cb(pl, 0, 16.4, -8.8, 1.2, 1.2, 4.0, 'cloth')
    m.hitbox(0.9, 1.2)
    m.anim('idle', 1.6, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.3, 0]], 0.8)},
                                 'head': {'rotation': loop([[0, 0, 0], [6, 6, 0], [0, 0, 0], [6, -6, 0]], 1.6)},
                                 'tail': {'rotation': loop([[0, 25, 0], [0, -25, 0]], 0.4)}})
    L = 0.4
    m.anim('walk', L, 'loop', {
        'fl_leg': {'rotation': loop([[-40, 0, 0], [30, 0, 0]], L)}, 'fr_leg': {'rotation': loop([[30, 0, 0], [-40, 0, 0]], L)},
        'bl_leg': {'rotation': loop([[30, 0, 0], [-35, 0, 0]], L)}, 'br_leg': {'rotation': loop([[-35, 0, 0], [30, 0, 0]], L)},
        'body': {'position': loop([[0, 1.2, 0], [0, 0, 0]], L / 2), 'rotation': loop([[-4, 0, 0], [4, 0, 0]], L)},
        'head': {'rotation': loop([[6, 0, 0], [-4, 0, 0]], L)}})
    m.anim('attack', 0.5, 'once', {
        'head': {'rotation': [(0, [0, 0, 0]), (0.15, [-28, 0, 0]), (0.25, [24, 0, 0]), (0.35, [18, 0, 0]), (0.5, [0, 0, 0])]},
        'body': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.5, 2.5]), (0.25, [0, -0.5, -4]), (0.35, [0, 0, -3]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


# =================================================================== preview + compare
def shade_pass(m, prefixes=('skin',), seed=7):
    """per-face shading for flat materials: lit top, darker bottom/edges, light mottling"""
    import random
    rng = random.Random(seed)
    for bn in m.bones:
        if bn.name == 'head':
            continue
        for c in bn.cubes:
            if not c['mat'].startswith(prefixes):
                continue
            for f in ('north', 'south', 'east', 'west'):
                base = [('shade', 0, 0, 1, 0.15, 1.08), ('shade', 0, 0.8, 1, 1, 0.86),
                        ('shade', 0, 0, 0.1, 1, 0.92), ('shade', 0.9, 0, 1, 1, 0.92)]
                for _ in range(4):
                    x0, y0 = rng.random() * 0.85, rng.random() * 0.85
                    base.append(('shade', x0, y0, x0 + 0.12, y0 + 0.12, rng.choice((0.95, 1.05))))
                c['decals'][f] = base + c['decals'].get(f, [])


def archer():
    """HQ vanilla-like CR/CoC Archer: pink bob + bangs, sleeveless green dress, team cape + hood,
    gold arm ring, brown belt + quiver, bare feet, recurve bow"""
    m = new_model('clash_archer')
    m.mats_({'skin': ('#f0b896', 'skin'), 'skin_d': ('#d89878', 'skin'), 'hair': ('#e8509e', 'hair'), 'hair_d': ('#c03a82', 'hair'),
             'dress': ('#7cc23a', 'cloth'), 'dress_d': ('#5e9a2a', 'cloth'), 'cape': ('#efefef', 'cloth'), 'cape_d': ('#d2d2d2', 'cloth'),
             'belt': ('#6a4426', 'leather'), 'gold': ('#e2b23a', 'metal'), 'wood': ('#8a5530', 'wood'), 'string': ('#e8e8e0', 'plain'),
             'feather': ('#f06aa8', 'cloth'), 'steel': ('#b8bcc4', 'metal')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    toes = pix(["........", "k.k.k.k."], {'k': '#c88a6a'})
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.9
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 1.0, 0, 2.8, 11.0, 2.9, S)                                      # bare leg
        cb(lg, x, 0, -0.5, 3.0, 1.0, 4.0, 'skin_d', decals={'north': toes})       # bare foot
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 18, 0, 6.6, 6.0, 3.4, 'dress', decals={'north': pix(["..k..k..", "...kk...", "........"], {'k': '#5e9a2a'})})
    skirt = m.bone('skirt', [0, 17, 0], body)                                   # (kept name; dress is green, not team)
    hem = pix(["........", "........", "........", "........", "k.k..k.k", "kkk.kkkk"], {'k': '#5e9a2a'})
    cb(skirt, 0, 12.4, 0, 7.8, 4.6, 4.6, 'dress', decals={'north': hem, 'south': hem, 'east': hem, 'west': hem})   # short dress hem, slight flare
    for i, dx in enumerate((-2.6, 0.0, 2.6)):
        cb(skirt, dx, 11.4, -2.1, 2.2, 1.6 - (i % 2) * 0.6, 0.5, 'dress_d')          # front flaps (flutter)
    cb(body, 0, 16.6, 0, 7.2, 1.3, 4.0, 'belt')                                    # belt
    cb(body, -1.6, 16.5, -2.1, 1.6, 1.5, 0.3, 'gold')                              # buckle
    cb(body, 2.4, 13.4, -2.3, 1.8, 2.4, 0.6, 'belt')                               # pouch
    vest = m.bone('tc_vest', [0, 22, 0], body)                                     # cape + hood (team colour)
    cb(vest, 0, 9.0, 2.2, 7.4, 14.4, 0.6, 'cape', decals={'south': pix(["....", "....", "....", "....", "....", "....", "k..k", "kkkk"], {'k': '#d2d2d2'})})
    cb(vest, 0, 6.6, 2.6, 8.4, 3.0, 0.6, 'cape_d')                                 # flared hem
    hood = m.bone('hood', [0, 24, 3], body)                                       # green hood hanging down the back
    cb(hood, 0, 20.6, 3.8, 7.0, 5.8, 3.0, 'dress', decals={'north': pix(["......", ".kkkk.", ".kkkk.", "......"], {'k': '#3e6a1c'})})
    cb(hood, 0, 25.4, 3.2, 6.6, 1.6, 2.8, 'dress_d')
    cb(hood, 0, 19.2, 4.8, 3.0, 1.6, 1.2, 'dress_d')
    for sx in (1, -1):
        cb(vest, sx * 3.4, 23.0, 0.4, 1.6, 1.4, 4.0, 'cape')                       # over the shoulders
    q = m.bone('quiver', [1.8, 18, 3.4], body)                                   # leather quiver, tilted, gold rims
    qr = dict(rot=('z', -22.5), rot_origin=[1.8, 18, 3.4])
    cb(q, 1.8, 13.4, 3.4, 2.8, 9.0, 2.8, 'belt', **qr)
    cb(q, 1.8, 21.6, 3.4, 3.2, 0.8, 3.2, 'gold', **qr)                             # top rim
    cb(q, 1.8, 13.2, 3.4, 3.2, 0.8, 3.2, 'gold', **qr)                             # bottom rim
    for i, (dx, dz, h) in enumerate(((-0.7, -0.6, 3.0), (0.6, -0.5, 3.6), (-0.5, 0.7, 3.4), (0.7, 0.6, 2.8))):
        cb(q, 1.8 + dx, 22.4, 3.4 + dz, 0.4, h, 0.4, 'wood', **qr)                 # arrow shafts
        cb(q, 1.8 + dx, 22.4 + h - 1.6, 3.4 + dz, 1.1, 1.6, 0.25, 'feather', **qr) # pink fletching
    cb(q, 0, 17.4, -1.85, 1.0, 6.8, 0.3, 'belt', rot=('z', 45), rot_origin=[0, 20.8, -1.85])   # chest strap
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", "........", ".p.rr.p.", "........"],
               {'k': '#7a2a5a', 'w': '#ffffff', 'b': '#3a6aa8', 'p': '#f29a9a', 'r': '#c2384a'})
    cb(hd, 0, 24, 0, 8, 8, 8, S, decals={'north': face})
    hair = m.bone('hair', [0, 28, 0], hd)
    cb(hair, 0, 29.6, 0.2, 9.0, 3.2, 8.8, 'hair')                                  # crown
    cb(hair, 0, 30.4, -4.5, 8.8, 1.6, 0.8, 'hair_d')                               # straight-cut bangs
    cb(hair, 0, 29.4, -4.6, 8.8, 1.2, 0.6, 'hair', decals={'north': pix(["k.k.k.k.k"], {'k': '#c03a82'})})
    for sx in (1, -1):
        cb(hair, sx * 4.4, 23.4, 0.4, 0.9, 6.6, 8.2, 'hair')                       # bob sides to the jaw
        cb(hair, sx * 4.3, 23.0, -3.6, 1.0, 1.2, 1.2, 'hair_d')                    # flicked ends
    cb(hair, 0, 23.4, 4.4, 9.0, 6.6, 0.9, 'hair')                                  # back
    rib = m.bone('tc_ribbon', [3.4, 30, 0.8], hair)
    cb(rib, 3.6, 30.4, 1.6, 0.6, 1.2, 1.6, 'cape')                                 # small team hair clip
    braid = m.bone('braid', [0, 24, 4.2], hair)                                    # (kept bone) short tuft at the nape
    cb(braid, 0, 22.6, 4.6, 3.0, 1.6, 0.8, 'hair_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.8
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x, 12.0, 0, 3.0, 12.0, 3.0, S)                                       # slim bare arm
        cb(a, x, 19.0, 0, 3.4, 0.9, 3.4, 'gold')                                   # gold arm ring
        if side == 'l':
            cb(a, x, 13.0, 0, 3.4, 3.0, 3.4, 'belt')                               # leather bracer
    bow = m.bone('bow', [-4.8, 12.6, -2.2], m.by_name('arm_l'))                    # ornate recurve bow, left hand
    bx, bz = -4.8, -2.2
    cb(bow, bx, 10.4, bz, 1.3, 4.4, 1.5, 'wood_d', decals={'east': pix(["g", ".", "g", "."], {'g': '#e2b23a'}), 'west': pix(["g", ".", "g", "."], {'g': '#e2b23a'})})   # carved riser
    cb(bow, bx, 11.6, bz, 1.5, 2.0, 1.7, 'belt', decals={'north': pix(["k", ".", "k"], {'k': '#4a2e18'})})   # leather grip
    cb(bow, bx - 0.75, 13.6, bz, 0.4, 0.5, 0.8, 'gold')                           # arrow rest
    segs = [(2.2, -0.4, 1.2), (3.9, -0.9, 1.1), (5.5, -1.2, 1.0), (7.0, -1.2, 0.9), (8.3, -0.8, 0.8), (9.3, 0.0, 0.7)]
    for sy in (1, -1):
        for j, (dy, dz, th) in enumerate(segs):
            h = 1.9 if j < 5 else 1.2
            yb = 12.6 + dy if sy > 0 else 12.6 - dy - h
            mat = 'wood' if j < 5 else 'gold'
            dec = {'north': pix(["g", "."], {'g': '#e2b23a'})} if j in (1, 3) else {}
            cb(bow, bx, yb, bz + dz, 0.9, h, th, mat, decals=dec)                   # curved limb
        cb(bow, bx, 12.6 + 2.0 if sy > 0 else 12.6 - 2.6, bz - 0.2, 1.3, 0.6, 1.5, 'gold')   # gold band
        cb(bow, bx, 12.6 + 10.3 if sy > 0 else 12.6 - 10.9, bz + 0.6, 0.8, 0.6, 0.9, 'gold')  # recurved tip
    cb(bow, bx, 12.6 - 10.6, bz + 0.9, 0.2, 21.2, 0.2, 'string')                    # string (archer side)
    m.mats_({'wood_d': ('#5e3a20', 'wood')})
    arw = m.bone('arrow', [bx, 12.6, bz], bow)                                     # nocked arrow
    cb(arw, bx - 0.75, 14.0, bz - 3.0, 0.4, 0.4, 8.0, 'wood')
    cb(arw, bx - 0.75, 13.8, bz - 7.4, 0.8, 0.8, 1.0, 'steel')
    cb(arw, bx - 0.75, 13.6, bz + 0.2, 0.25, 1.2, 1.6, 'feather')
    for bn in m.bones:                                                             # shorter legs (10 px)
        if bn.name == 'root':
            continue
        if bn.name.startswith('leg_'):
            bn.origin[1] -= 4
            for c in bn.cubes:
                if c['to'][1] > 2:
                    c['to'][1] -= 4
            continue
        bn.origin[1] -= 4
        for c in bn.cubes:
            c['frm'][1] -= 4; c['to'][1] -= 4; c['rot_origin'][1] -= 4
    m.hitbox(0.7, 1.9)
    shade_pass(m, ('skin', 'dress', 'cape'))
    ready = {'arm_l': [-40, 15, 0], 'arm_r': [-72, -40, 10], 'bow': [90, 60, -30]}   # right hand on the nock     # bow held level across the waist
    m.anim('idle', 2.0, 'loop', {'arm_l': {'rotation': loop([ready['arm_l'], [-42, 15, 0]], 2.0)},
                                 'arm_r': {'rotation': loop([ready['arm_r'], [-74, -40, 10]], 2.0)},
                                 'bow': {'rotation': loop([ready['bow'], ready['bow']], 2.0)},
                                 'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 4.0)},
                                 'body': {'position': loop([[0, 0, 0], [0, -0.2, 0]], 2.0)},
                                 'skirt': {'rotation': loop([[0, 0, 0], [3, 0, 2], [0, 0, 0], [-2, 0, -2]], 2.0)},
                                 'tc_vest': {'rotation': loop([[0, 0, 0], [4, 0, 0]], 2.0)}})
    mc_walk(m, 0.7, 30, extra={'arm_l': {'rotation': loop([ready['arm_l'], [-38, 15, 0]], 0.7)},
                               'arm_r': {'rotation': loop([ready['arm_r'], [-70, -40, 10]], 0.7)},
                               'bow': {'rotation': loop([ready['bow'], ready['bow']], 0.7)},
                               'skirt': {'rotation': loop([[8, 0, 4], [-6, 0, -4]], 0.7)},
                               'tc_vest': {'rotation': loop([[10, 0, 0], [16, 0, 0]], 0.35)}})
    # vanilla Minecraft bow-aim pose: both arms raised level, draw arm angled in, bow vertical, arrow drawn back
    al, ar_ = [-90, 25, 0], [-90, -12, 0]
    aim = {'arm_l': {'rotation': [(0, ready['arm_l']), (0.2, al), (0.65, al), (0.9, ready['arm_l'])]},
           'arm_r': {'rotation': [(0, ready['arm_r']), (0.2, ar_), (0.6, [-90, -18, 0]), (0.65, [-86, -6, 0]), (0.9, ready['arm_r'])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.2, [0, 12, 0]), (0.65, [0, 12, 0]), (0.9, [0, 0, 0])]},
           'bow': {'rotation': [(0, ready['bow']), (0.2, BOW_AIM), (0.65, BOW_AIM), (0.9, ready['bow'])]},
           'arrow': {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.6, [0, 0, 2.5]), (0.62, [0, 0, 0])],
                     'scale': [(0, [1, 1, 1]), (0.6, [1, 1, 1]), (0.62, [0, 0, 0]), (0.85, [0, 0, 0]), (0.9, [1, 1, 1])]}}
    m.anim('attack', 0.9, 'once', aim)
    common_tail(m)
    return m



def baby_dragon():
    """HQ vanilla-like CR Baby Dragon: pudgy upright green body + pale belly bands, big head with wide open mouth
    (teeth, tongue out), bulging side eyes, top horn, orange bat wings, tan paws/feet, spiked tail, team neck band"""
    m = new_model('clash_baby_dragon')
    m.mats_({'grn': ('#5ec83a', 'skin'), 'grn_d': ('#45a42a', 'skin'), 'belly': ('#a6e27a', 'skin'), 'tan': ('#f0f0f0', 'skin'), 'gum': ('#c8306e', 'skin'), 'throat': ('#7a1e2e', 'plain'),
             'wing': ('#c4c4c4', 'leather', {'stitch': False}), 'wing_m': ('#f2f2f2', 'leather', {'stitch': False}),
             'mouth': ('#6e2424', 'plain'), 'tongue': ('#e07482', 'skin'), 'tooth': ('#f4f2ea', 'bone'), 'eye': ('#fbf6e6', 'plain'),
             'band': ('#efefef', 'cloth')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 10, 0], root)
    stripes = [('rect', 0.1, f, 0.9, f + 0.07, '#86c85e') for f in (0.2, 0.45, 0.7)]
    cb(body, 0, 3.0, 0, 10.4, 8.0, 9.0, 'grn')                                     # round lower belly
    cb(body, 0, 2.4, 0, 8.4, 0.6, 7.0, 'grn')
    cb(body, 0, 4.0, -4.7, 7.0, 8.4, 0.6, 'belly', decals={'north': stripes})       # pale belly
    cb(body, 0, 11.0, 0.4, 9.0, 5.4, 8.0, 'grn')                                    # chest
    cb(body, 0, 11.4, -3.7, 6.0, 4.0, 0.5, 'belly', decals={'north': stripes[:2]})
    tc = m.bone('tc_scarf', [0, 15, -1], body)
    cb(tc, 0, 15.2, 0.0, 9.4, 1.2, 8.4, 'band')                                     # team neck band
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('b%s_leg' % side, [sx * 3.4, 4.5, 1.0], body)
        cb(lg, sx * 3.6, 1.2, 1.0, 3.6, 3.4, 4.2, 'grn')                              # stubby thigh
        cb(lg, sx * 3.6, 0, 0.2, 4.0, 1.4, 5.2, 'tan',
           decals={'north': pix(["k.k.k", "....."], {'k': '#b8b8b8'})})              # tan foot + claws
        ar = m.bone('f%s_leg' % side, [sx * 5.0, 14.0, -1.6], body)                   # little arm
        cb(ar, sx * 5.4, 10.4, -1.8, 2.6, 4.4, 2.8, 'grn')
        cb(ar, sx * 5.4, 8.6, -2.2, 3.0, 2.0, 3.2, 'tan', decals={'north': pix(["k.k", "..."], {'k': '#b8b8b8'})})   # paw
    # head
    hd = m.bone('head', [0, 16, -1], body)
    cb(hd, 0, 16.2, -1.6, 9.4, 7.2, 8.4, 'grn')                                     # skull
    cb(hd, 0, 19.0, -8.8, 8.2, 4.0, 6.0, 'grn',                                     # big snout
       decals={'north': pix(["........", ".kk..kk.", "........", "........"], {'k': '#2a5a1a'})})   # nostrils
    for i in range(7):                                                              # upper teeth
        cb(hd, -3.0 + i * 1.0, 18.2, -11.4 + (0 if i in (0, 6) else 0), 0.7, 0.9, 0.7, 'tooth')
    for sx in (1, -1):
        cb(hd, sx * 3.7, 18.2, -8.0, 0.7, 0.9, 4.6, 'tooth', decals={'east': pix(["k.k.k."], {'k': '#d0ccc0'}), 'west': pix(["k.k.k."], {'k': '#d0ccc0'})})
        cb(hd, sx * 4.9, 20.0, -4.6, 1.4, 2.6, 2.6, 'eye',                            # bulging side eyes
           decals={'north': pix([".", "k", "k"], {'k': '#2a1a10'}),                        # one pupil wrapping the front corner
                   'east': pix(["...", "..k", "..k"], {'k': '#2a1a10'}), 'west': pix(["...", "k..", "k.."], {'k': '#2a1a10'})})
        cb(hd, sx * 4.9, 22.4, -4.6, 1.5, 0.6, 2.8, 'grn_d')                          # eyelid
        ear = m.bone('ear_' + ('r' if sx > 0 else 'l'), [sx * 4.6, 21, 1.0], hd)
        cb(ear, sx * 5.0, 21.0, 1.4, 0.8, 2.6, 2.4, 'tan')                           # little ear frills
    cb(hd, 0, 18.6, -6.6, 7.4, 0.4, 6.0, 'gum')                                      # thin upper gum
    cb(hd, 0, 15.4, -2.8, 6.6, 3.4, 0.4, 'throat')                                  # dark throat
    jaw = m.bone('jaw', [0, 17.4, -2.0], hd)                                         # lower jaw, open
    cb(jaw, 0, 14.6, -6.2, 8.4, 2.6, 7.6, 'grn')
    cb(jaw, 0, 17.0, -6.0, 7.2, 0.4, 6.8, 'gum')
    for sx in (1, -1):
        cb(jaw, sx * 3.6, 17.2, -6.8, 0.7, 0.9, 5.0, 'tooth', decals={'east': pix(["k.k.k."], {'k': '#d0ccc0'}), 'west': pix(["k.k.k."], {'k': '#d0ccc0'})})
    for dx in (-3.0, -2.0, 2.0, 3.0):
        cb(jaw, dx, 17.2, -9.4, 0.8, 0.9, 0.7, 'tooth')                               # front lower teeth
    tg = m.bone('tongue', [0, 17.4, -6.0], jaw)
    cb(tg, 0, 17.2, -8.8, 2.6, 0.8, 5.8, 'tongue', decals={'up': pix(["..", "k.", "..", ".k"], {'k': '#c45a68'})})
    cb(tg, 0, 14.6, -12.0, 2.6, 3.4, 0.8, 'tongue')                                 # tongue hanging over the chin
    def plate(bone, y, z, h, w, d):                                               # 3D plate: wide base, narrower tip
        cb(bone, 0, y, z, w, h * 0.6, d, 'tan')
        cb(bone, 0, y + h * 0.6, z + d * 0.1, w * 0.7, h * 0.4, d * 0.6, 'tan')
    for (y, z, h, w, d) in ((23.0, -1.2, 1.8, 0.8, 1.6), (22.8, 0.6, 2.6, 1.0, 2.0), (21.4, 2.2, 2.8, 1.2, 2.0)):
        plate(hd, y, z, h, w, d)                                                    # mane from the back of the head
    def back_plate(yc, zb, h, out, w):                                            # chunky 3-tier plate sticking out of the back
        z = zb
        for k, (fw, fh, fo) in enumerate(((1.0, 1.0, 0.45), (0.7, 0.72, 0.33), (0.4, 0.42, 0.22))):
            cb(body, 0, yc - h * fh / 2, z + out * fo / 2, w * fw, h * fh, out * fo, 'tan')
            z += out * fo
    for (yc, zb, h, out, w) in ((16.4, 4.0, 3.0, 3.2, 2.2), (12.8, 4.2, 2.6, 2.8, 2.0), (9.0, 4.2, 2.2, 2.4, 1.8), (5.4, 4.2, 1.8, 2.0, 1.6)):
        back_plate(yc, zb, h, out, w)                                               # ... getting smaller down the back
    # wings: flat bat wings on the back
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 3.0, 15.0, 3.8], body)
        scal = pix(["........", "........", "........", "........", "........", "k..kk..k", "kk.kkk.k"], {'k': '#000000'})
        cb(w, sx * 8.0, 15.0, 4.2, 10.0, 7.0, 0.6, 'wing_m', decals={'north': [('shade', 0, 0.75, 1, 1, 0.8)], 'south': [('shade', 0, 0.75, 1, 1, 0.8)]})   # membrane
        cb(w, sx * 8.0, 21.6, 4.2, 10.4, 1.4, 1.2, 'wing')                            # leading edge bone
        cb(w, sx * 13.4, 18.4, 4.2, 1.2, 4.6, 1.0, 'wing')                            # wing tip claw-finger
        for k, fx in enumerate((5.4, 9.0)):
            cb(w, sx * fx, 15.6, 4.2, 0.8, 6.0, 0.9, 'wing')                          # membrane ribs
    # spiked tail
    t = m.bone('tail', [0, 5.0, 4.4], body)
    cb(t, 0, 3.0, 6.0, 4.6, 3.6, 3.6, 'grn')
    cb(t, 0, 2.4, 9.0, 3.0, 2.6, 3.4, 'grn')
    cb(t, 0, 2.0, 11.6, 1.8, 1.8, 2.6, 'grn')
    for z, h in ((6.0, 1.6), (9.0, 1.2), (11.4, 1.0)):
        cb(t, 0, 2.4 + (3.6 if z == 6.0 else 2.6 if z == 9.0 else 1.8), z, 0.8, h + 0.6, 1.4, 'tan')   # back spikes
    for bn in list(m.bones):                                                       # team parts -> ts_ child bones
        if bn.name.startswith('ts_'):
            continue
        moving = [c for c in bn.cubes if c['mat'] in ('tan', 'wing', 'wing_m') or
                  (c['mat'] == 'grn' and bn.name in ('fr_leg', 'fl_leg', 'br_leg', 'bl_leg'))]
        if not moving:
            continue
        tb = m.bone('ts_' + bn.name, list(bn.origin), bn)
        for c in moving:
            bn.cubes.remove(c); tb.cubes.append(c)
            if c['mat'] == 'grn':                                                      # limbs: green -> team, smooth
                for f in ('north', 'south', 'east', 'west'):
                    c['decals'][f] = [('lerp', '#f0f0f0', 0.0, 1.0, 'y')] + c['decals'].get(f, [])
                c['decals']['down'] = [('lerp', '#f0f0f0', 1, 1, 'y')]
            if c['mat'] == 'wing_m':                                                   # membrane: green at the root
                sx = 1 if c['frm'][0] > 0 else -1
                g = (1.0, -0.6, 'x') if sx < 0 else (-0.6, 1.0, 'x')
                for f in ('north', 'south'):
                    c['decals'][f] = [('lerp', '#5ec83a', *g)] + c['decals'].get(f, [])
    m.hitbox(1.2, 1.6)
    shade_pass(m, ('grn', 'tan', 'wing'))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -10, -a], [0, 10, a * 0.4]], L)},
                         'wing_l': {'rotation': loop([[0, 10, a], [0, -10, -a * 0.4]], L)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 1.0)},
            'tail': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 1.0)},
            'jaw': {'rotation': loop([[20, 0, 0], [26, 0, 0]], 1.0)},
            'fr_leg': {'rotation': loop([[-20, 0, 0], [-10, 0, 0]], 1.0)}, 'fl_leg': {'rotation': loop([[-20, 0, 0], [-10, 0, 0]], 1.0)}}
    idle.update(flap(0.5, 35))
    m.anim('idle', 1.0, 'loop', idle)
    walk = dict(idle); walk.update(flap(0.3, 45)); walk['body'] = {'rotation': loop([[12, 0, 0], [12, 0, 0]], 0.4)}
    walk['root'] = {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.4)}
    m.anim('walk', 0.4, 'loop', walk)
    m.anim('attack', 0.7, 'once', {'head': {'rotation': [(0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.35, [10, 0, 0]), (0.7, [0, 0, 0])]},
                                   'jaw': {'rotation': [(0, [20, 0, 0]), (0.2, [10, 0, 0]), (0.35, [40, 0, 0]), (0.55, [40, 0, 0]), (0.7, [20, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.35, [10, 0, 0]), (0.7, [0, 0, 0])]}})
    common_tail(m)
    return m




def balloon():
    """HQ vanilla-like Balloon: round team-coloured patched envelope with rope net, burner flame,
    rope-hung wooden basket with sandbags, skeleton pilot in leather flight cap holding a big bomb"""
    import random
    rng = random.Random(3)
    m = new_model('clash_balloon')
    m.mats_({'fab': ('#cfcfcf', 'cloth'), 'patch': ('#f4f4f4', 'cloth'), 'patch2': ('#a8a8a8', 'cloth'), 'strap': ('#5a3a22', 'leather'), 'glass': ('#8ad0e8', 'gem'), 'rope': ('#c9a265', 'rope'), 'wood': ('#8a5a32', 'wood', {'planks': True}),
             'wood_d': ('#5e3a20', 'wood'), 'metal': ('#9aa0a8', 'metal'), 'flame': ('#ffb030', 'glow'), 'flame2': ('#ff6a1a', 'glow'),
             'bone': ('#ece6d6', 'bone'), 'cap': ('#7a4a2a', 'leather'), 'bomb': ('#26272c', 'soft'), 'sand': ('#b08a5a', 'leather'),
             'spark': ('#ffe04a', 'glow'), 'void': ('#141210', 'plain'), 'ring': ('#3a2a20', 'plain')})
    root = m.bone('root', [0, 0, 0])
    env = m.bone('envelope', [0, 36, 0], root)
    fab = m.bone('tc_band', [0, 36, 0], env)                                       # whole envelope is team coloured
    # boxy Minecraft-style envelope: big bevelled block, stepped down to the mouth
    W, H, y0 = 20.0, 23.0, 30.0
    gore = [('rect', f, 0, f + 0.02, 1, '#b4b4b4') for f in (0.25, 0.5, 0.75)]     # sewn panel seams
    cb(fab, 0, y0 + 1, 0, W, H - 2, W, 'fab', decals={f: gore for f in ('north', 'south', 'east', 'west')})
    cb(fab, 0, y0, 0, W - 2, H, W - 2, 'fab')                                       # bevelled edges
    cb(fab, 0, y0 - 2.0, 0, W - 5, 2.0, W - 5, 'fab')                               # stepping down to the mouth
    cb(fab, 0, y0 - 3.6, 0, W - 10, 1.6, W - 10, 'fab')
    cb(env, 0, y0 - 3.8, 0, 5.6, 0.4, 5.6, 'ring')                                   # dark mouth
    st = lambda W_, H_: [('px', i / W_, 0.0, '#7e7e7e') for i in range(1, W_, 3)] + [('px', i / W_, 0.99, '#7e7e7e') for i in range(1, W_, 3)] + \
                        [('px', 0.0, j / H_, '#7e7e7e') for j in range(1, H_, 3)] + [('px', 0.99, j / H_, '#7e7e7e') for j in range(1, H_, 3)]
    hw = W / 2
    for (side, u, v, w, h, mat) in (('n', -4.0, 45.0, 6.0, 4.6, 'patch'), ('n', 5.0, 34.0, 4.4, 3.6, 'patch2'), ('e', 3.0, 44.0, 5.0, 4.0, 'patch'),
                                   ('w', -2.0, 35.0, 4.6, 5.0, 'patch2'), ('s', 2.0, 46.0, 5.6, 4.4, 'patch'), ('e', -5.0, 33.0, 3.4, 3.0, 'patch2')):
        if side in 'ns':
            z = -hw - 0.25 if side == 'n' else hw + 0.25
            cb(fab, u, v - h / 2, z, w, h, 0.5, mat, decals={'north': st(int(w * 2), int(h * 2)), 'south': st(int(w * 2), int(h * 2))})   # raised stitched patch
        else:
            x = hw + 0.25 if side == 'e' else -hw - 0.25
            cb(fab, x, v - h / 2, u, 0.5, h, w, mat, decals={'east': st(int(w * 2), int(h * 2)), 'west': st(int(w * 2), int(h * 2))})
    for (x, y, z) in ((-6.0, 36.0, -hw - 0.2), (hw + 0.2, 48.0, -6.0)):              # stitched-up tears
        dz = abs(z) > abs(x)
        cb(fab, x, y, z, 3.0 if dz else 0.4, 0.5, 0.4 if dz else 3.0, 'patch2',
           decals={k: [('px', i / 6, 0.0, '#1a1a1a') for i in range(0, 6)] + [('px', i / 6, 0.99, '#1a1a1a') for i in range(1, 6, 2)] for k in ('north', 'south', 'east', 'west')})
    # rope net: crossing ropes over the top and down every side, plus a belt round the middle
    for sg in (1, -1):
        cb(env, 0, y0 + H, sg * 0, 0.8, 0.5, W + 0.4, 'rope') if sg > 0 else cb(env, 0, y0 + H, 0, W + 0.4, 0.5, 0.8, 'rope')
        cb(env, 0, y0 - 1, sg * (hw + 0.3), 0.8, H + 1.4, 0.5, 'rope')
        cb(env, sg * (hw + 0.3), y0 - 1, 0, 0.5, H + 1.4, 0.8, 'rope')
        cb(env, 0, y0 + 10.0, sg * (hw + 0.35), W + 1.2, 0.8, 0.5, 'rope')
        cb(env, sg * (hw + 0.35), y0 + 10.0, 0, 0.5, 0.8, W + 1.2, 'rope')
        cb(env, 0, y0 + 0.4, sg * (hw - 0.6), W - 0.8, 0.7, 0.5, 'rope')
        cb(env, sg * (hw - 0.6), y0 + 0.4, 0, 0.5, 0.7, W - 0.8, 'rope')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(env, sx * (hw - 0.6), y0 + 9.8, sz * (hw + 0.35), 1.2, 1.2, 0.6, 'rope')   # knots
    # burner + flame
    bu = m.bone('burner', [0, 24, 0], root)
    cb(bu, 0, 23.6, 0, 4.6, 0.8, 4.6, 'metal')
    for sx in (1, -1):
        cb(bu, sx * 2.4, 22.4, 0, 0.5, 2.0, 0.5, 'metal')
    fl = m.bone('flame', [0, 24.4, 0], bu)
    cb(fl, 0, 24.4, 0, 2.4, 1.6, 2.4, 'flame2')
    cb(fl, 0, 25.4, 0, 1.4, 1.4, 1.4, 'flame')
    # hanging ropes to the basket corners
    for sx in (1, -1):
        for sz in (1, -1):
            cb(root, sx * 4.4, 12.6, sz * 4.4, 0.5, 12.4, 0.5, 'rope')
            cb(root, sx * 4.4, 25.0, sz * 4.4, 0.5, 5.4, 0.5, 'rope')
    # woven basket with corner posts, rope rims and knots
    bk = m.bone('basket', [0, 6, 0], root)
    weave = [('rect', f, 0, f + 0.04, 1, '#5e3a20') for f in (0.2, 0.4, 0.6, 0.8)] + [('rect', 0, f, 1, f + 0.05, '#6e4626') for f in (0.33, 0.66)]
    cb(bk, 0, 5.6, 0, 9.4, 7.0, 9.4, 'wood', decals={f: weave for f in ('north', 'south', 'east', 'west')})
    cb(bk, 0, 5.2, 0, 8.6, 0.6, 8.6, 'wood_d')                                       # floor lip
    cb(bk, 0, 12.0, 0, 8.0, 0.6, 8.0, 'wood_d')                                      # dark inside
    for sx in (1, -1):
        for sz in (1, -1):
            cb(bk, sx * 4.7, 5.0, sz * 4.7, 1.2, 8.2, 1.2, 'wood_d')                   # corner posts
            cb(bk, sx * 4.9, 12.0, sz * 4.9, 1.2, 1.2, 1.2, 'rope')                   # knots
    for y in (5.4, 12.4):
        for sg in (1, -1):
            cb(bk, 0, y, sg * 4.85, 10.0, 0.9, 0.6, 'rope')                           # rope rims
            cb(bk, sg * 4.85, y, 0, 0.6, 0.9, 10.0, 'rope')
    for (x, z, y) in ((5.6, -1.6, 6.4), (5.6, 2.2, 5.6), (-5.6, 0.8, 6.0), (-1.8, -5.6, 5.4)):   # hanging sandbags
        side_x = abs(x) > abs(z)
        bx, bz = (x + (0.4 if x > 0 else -0.4), z) if side_x else (x, z - 0.4)
        cb(bk, bx, y, bz, 2.2, 2.4, 2.2, 'sand', decals={'north': [('rect', 0.2, 0.15, 0.8, 0.25, '#8a6a40')]})
        cb(bk, bx, y + 2.4, bz, 1.4, 0.8, 1.4, 'sand')                                  # tied neck
        cb(bk, bx, y + 3.2, bz, 0.4, 0.8 + (12.0 - y - 3.2), 0.4, 'rope')               # rope up to the rim
    # pilot = the real bomber (upper body), scaled down, standing in the basket
    clone_into(m, bomber(), bk, {'body': 'pilot', 'head': 'skull', 'tc_band': 'tc_cap', 'goggles': 'goggles', 'arm_r': 'arm', 'arm_l': 'arm_l'},
               s=0.55, off=(0, 3.5, 1.2))
    # big bomb on the front rim
    bo = m.bone('bomb', [1.0, 13, -5], root)
    for (w, h, d, dy) in ((4.4, 3.0, 4.4, 0.7), (3.0, 4.4, 3.0, 0.0), (3.8, 3.8, 3.8, 0.3)):
        cb(bo, 1.0, 11.6 + dy, -5.8, w, h, d, 'bomb', decals={'north': pix(["....", ".w..", "....", "...."], {'w': '#6a6c74'})})
    cb(bo, 1.0, 16.0, -5.8, 1.4, 0.6, 1.4, 'metal')
    cb(bo, 1.4, 16.6, -5.8, 0.5, 1.2, 0.5, 'rope')
    sp = m.bone('fuse', [1.6, 18.2, -5.8], bo)
    cb(sp, 1.6, 17.8, -5.8, 0.8, 0.8, 0.8, 'spark')
    m.hitbox(2.2, 3.0)
    shade_pass(m, ('wood', 'bone'))
    sway = {'root': {'rotation': loop([[0, 0, 3], [0, 0, -3]], 2.4), 'position': loop([[0, 0, 0], [0, 1.0, 0]], 2.4)},
            'flame': {'scale': loop([[1, 1, 1], [1.2, 1.4, 1.2]], 0.3)},
            'skull': {'rotation': loop([[0, 15, 0], [0, -15, 0]], 2.4)},
            'arm': {'rotation': loop([[-50, 0, -10], [-52, 0, -10]], 2.4)}, 'arm_l': {'rotation': loop([[-50, 0, 10], [-52, 0, 10]], 2.4)},
            'fuse': {'scale': loop([[1, 1, 1], [1.6, 1.6, 1.6]], 0.3)}}
    m.anim('idle', 2.4, 'loop', sway)
    walk = dict(sway); walk['root'] = {'rotation': loop([[6, 0, 2], [6, 0, -2]], 1.6), 'position': loop([[0, 0, 0], [0, 0.6, 0]], 1.6)}
    m.anim('walk', 1.6, 'loop', walk)
    m.anim('attack', 1.0, 'once', {'arm': {'rotation': [(0, [0, 0, 0]), (0.3, [30, 0, 0]), (0.5, [0, 0, 0])]},
                                   'bomb': {'position': [(0, [0, 0, 0]), (0.3, [0, 0, -1]), (0.7, [0, -14, -1]), (0.72, [0, 0, 0])],
                                            'scale': [(0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.72, [0, 0, 0]), (0.95, [0, 0, 0]), (1.0, [1, 1, 1])]}})
    common_tail(m)
    return m



def barbarian():
    """HQ vanilla-like Barbarian: gold helmet + cheek guards, blond horseshoe moustache, big nose, muscular bare torso,
    spiked wristbands, team belt with shield buckle, brown kilt, sandals, sword"""
    m = new_model('clash_barbarian')
    m.mats_({'skin': ('#e8a878', 'skin'), 'skin_d': ('#c88a5e', 'skin'), 'gold': ('#e8b830', 'metal'), 'gold_d': ('#b88a20', 'metal'),
             'hair': ('#f0c848', 'hair'), 'hair_d': ('#d0a030', 'hair'), 'kilt': ('#6a4a34', 'leather', {'stitch': False}), 'belt': ('#efefef', 'leather'),
             'steel': ('#a8b0b8', 'metal'), 'band': ('#5a3a24', 'leather'), 'sandal': ('#4a3020', 'leather'), 'grip': ('#6a4426', 'leather')})
    D = '#b07650'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = m.bone('leg_' + side, [x, 10.5, 0], root)
        cb(lg, x, 1.0, 0, 3.6, 9.6, 3.6, 'skin')
        cb(lg, x, 0, -0.4, 4.0, 1.0, 5.0, 'sandal', decals={'up': pix(["....", "kkkk", "....", "...."], {'k': '#e8a878'})})
        cb(lg, x, 1.0, -1.2, 4.2, 0.8, 1.4, 'sandal')                                   # sandal strap
    body = m.bone('body', [0, 10.5, 0], root)
    slit = [('rect', 0.3, 0.4, 0.33, 1, '#4a3424'), ('rect', 0.7, 0.5, 0.73, 1, '#4a3424')]
    cb(body, 0, 5.6, 0, 9.8, 5.2, 6.0, 'kilt', decals={'north': slit, 'south': slit})
    tc = m.bone('tc_sash', [0, 12, 0], body)
    cb(tc, 0, 10.2, 0, 10.4, 2.4, 6.6, 'belt')                                           # team belt
    cb(body, 0, 10.0, -3.5, 2.6, 2.8, 0.4, 'steel', decals={'north': pix(["k..k", "....", ".kk.", "...."], {'k': '#6a7078'})})   # shield buckle
    cb(body, 0, 12.6, 0, 8.6, 4.0, 5.2, 'skin', decals={'north': [('rect', 0.48, 0.0, 0.52, 1, D), ('rect', 0.15, 0.5, 0.85, 0.54, D)]})   # abs
    cb(body, 0, 16.4, 0.2, 11.4, 4.8, 6.2, 'skin', decals={'north': [('rect', 0.48, 0.1, 0.52, 0.9, D), ('rect', 0.1, 0.85, 0.45, 0.9, D), ('rect', 0.55, 0.85, 0.9, 0.9, D)]})   # chest + pecs
    for sx in (1, -1):
        cb(body, sx * 3.0, 20.8, 0.6, 4.0, 1.4, 4.4, 'skin')                              # traps
    hd = m.bone('head', [0, 20.5, 0], body)
    face = pix(["........", "........", "........", ".wb..bw.", "........", "........", ".k....k.", "..kkkk.."],
               {'w': '#ffffff', 'b': '#3a7ad8', 'k': '#6a3a2a'})
    cb(hd, 0, 20.8, -0.4, 7.4, 7.0, 7.2, 'skin', decals={'north': face})
    cb(hd, 0, 23.0, -4.4, 1.8, 2.2, 1.2, 'skin_d')                                       # big nose
    hair = m.bone('hair', [0, 26, 0], hd)                                                 # blond helmet-like hair
    cb(hair, 0, 25.6, -0.4, 8.2, 3.0, 8.0, 'hair')
    cb(hair, 0, 28.6, -0.4, 6.8, 0.8, 6.6, 'hair')
    cb(hair, 0, 25.2, -4.3, 8.2, 1.4, 0.6, 'hair_d')                                     # fringe
    cb(hair, 0, 26.0, -0.4, 1.0, 3.6, 8.4, 'hair_d')                                     # centre parting
    cb(hair, 0, 21.2, 3.4, 8.2, 4.6, 1.0, 'hair')                                        # back hair
    for sx in (1, -1):
        cb(hair, sx * 4.0, 20.2, -1.6, 0.9, 5.4, 4.0, 'hair')                              # side locks
    br = m.bone('beard', [0, 20.8, -3.6], hd)                                             # horseshoe moustache
    cb(br, 0, 21.6, -4.3, 5.8, 1.4, 1.2, 'hair')
    for sx in (1, -1):
        cb(br, sx * 2.6, 19.6, -4.2, 1.3, 2.8, 1.2, 'hair')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.4
        a = m.bone('arm_' + side, [x, 19.3, 0], body)
        cb(a, x, 16.6, 0, 4.6, 4.2, 4.6, 'skin')                                          # deltoid
        cb(a, x, 10.6, 0, 3.8, 6.4, 3.8, 'skin', decals={'north': [('rect', 0.45, 0.1, 0.55, 0.6, D)]})
        cb(a, x, 11.0, 0, 4.4, 1.6, 4.4, 'band')                                          # spiked wristband
        for (dx, dz) in ((sx * 2.4, 0), (0, -2.4), (0, 2.4)):
            cb(a, x + dx, 11.4, dz, 0.8, 0.8, 0.8, 'steel')
        cb(a, x, 7.8, 0, 3.6, 2.8, 3.6, 'skin', decals={'north': pix(["k.k.", "...."], {'k': D})})   # fist
    sw = m.bone('sword', [6.4, 9.2, 0], m.by_name('arm_r'))
    fine_sword(m, sw, 6.4, 9.3, 0.0, L=11.0, k=1.4)
    m.hitbox(0.9, 1.9)
    shade_pass(m, ('skin', 'kilt'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-20, 0, 4], [-24, 0, 6]], 2.0)}})
    mc_walk(m, 0.7, 30, arm_r=False, extra={'arm_r': {'rotation': loop([[-20, 0, 4], [-30, 0, 4]], 0.7)}})
    m.anim('attack', 0.55, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 4]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, 0]), (0.55, [-20, 0, 4])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-6, 10, 0]), (0.35, [10, -10, 0]), (0.55, [0, 0, 0])]}})
    common_tail(m)
    return m



def elite_barbarian():
    """Barbarian + iron horned viking helmet (eye mask + nose guard, team stripe), yelling mouth"""
    m = barbarian()
    m.name = 'clash_elite_barbarian'
    m.mats_({'iron': ('#5e666c', 'metal'), 'iron_d': ('#40464c', 'metal'), 'horn': ('#e6dcc4', 'bone'), 'horn_d': ('#b8a888', 'bone'),
             'tcm': ('#efefef', 'metal'), 'mouth': ('#8a2a2a', 'plain'), 'tooth': ('#f6f4ea', 'bone')})
    hd = m.by_name('head')
    cb(hd, 0, 19.6, -4.1, 4.0, 1.8, 0.2, 'mouth', decals={'north': pix(["tttt", "....", ".pp.", "tttt"], {'t': '#f6f4ea', 'p': '#d86070'})})   # yelling mouth
    hm = m.bone('helmet', [0, 26, 0], hd)
    cb(hm, 0, 25.4, -0.4, 8.8, 3.6, 8.6, 'iron')                                        # dome
    cb(hm, 0, 29.0, -0.4, 7.4, 1.0, 7.2, 'iron')
    cb(hm, 0, 25.0, -4.9, 8.8, 1.4, 0.6, 'iron_d')                                      # brow band
    cb(hm, 0, 23.2, -4.9, 1.6, 3.4, 0.6, 'iron_d')                                      # nose guard
    for sx in (1, -1):
        cb(hm, sx * 2.9, 23.6, -4.9, 3.0, 0.6, 0.6, 'iron_d')                             # eye-mask rim under the eyes
        cb(hm, sx * 4.2, 23.6, -4.9, 0.6, 1.8, 0.6, 'iron_d')
        cb(hm, sx * 4.5, 22.4, -0.4, 0.5, 3.6, 8.0, 'iron')                               # side plates
        hr = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 4.6, 27, -0.4], hm)
        for (hx, hz, w, mat) in ((5.4, -0.4, 3.2, 'horn_d'), (7.2, -0.5, 2.8, 'horn_d'), (8.6, -1.0, 2.4, 'horn'),
                                 (9.4, -2.5, 1.9, 'horn'), (9.6, -4.0, 1.3, 'horn')):
            cb(hr, sx * hx, 26.6 - w / 2, hz, w, w, w + 0.3, mat)                       # level horn: straight out, tip turns forward
        cb(hr, sx * 6.0, 26.4, -2.2, 0.4, 1.2, 0.6, 'horn_d')                              # horn ridges
    cb(hm, 0, 28.8, -0.4, 1.2, 1.4, 8.8, 'iron_d')                                       # crest ridge
    return m



def barbarian_barrel():
    """HQ vanilla-like Barbarian Barrel: octagonal wooden barrel (axis X) with team hoops + steel spikes,
    barbarian head poking out of one end, sandaled feet out of the other, rolls forward"""
    m = new_model('clash_barbarian_barrel')
    m.mats_({'wood': ('#a8743e', 'wood', {'planks': True}), 'wood_d': ('#6a4424', 'wood'), 'hoop': ('#7a8088', 'metal'),
             'steel': ('#a8b0b8', 'metal'), 'skin': ('#e8a878', 'skin'), 'hair': ('#f0c848', 'hair'), 'sandal': ('#4a3020', 'leather'),
             'grip': ('#6a4426', 'leather'), 'gold': ('#e8b830', 'metal'), 'hole': ('#141210', 'plain')})
    cy, R, L = 12.0, 8.6, 22.0
    roll = m.bone('roll', [0, cy, 0], None)
    staves = [('rect', 0, f, 1, f + 0.03, '#6a4424') for f in (0.2, 0.4, 0.6, 0.8)]
    def octa(bone, x, ln, r, mat, dec=None, grow=0.0):                              # octagonal slab section along X
        for rot in (None, ('x', 45)):
            cb(bone, x, cy - r - grow, 0, ln, 2 * (r + grow), 0.83 * r + grow, mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
            cb(bone, x, cy - 0.415 * r - grow / 2, 0, ln, 0.83 * r + grow, 2 * (r + grow), mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
        cb(bone, x, cy - 0.76 * r - grow, 0, ln, 1.52 * r + 2 * grow, 1.52 * r + 2 * grow, mat, decals=dec or {})   # fills the diagonal notches
    D = {f: staves for f in ('north', 'south', 'up', 'down')}
    octa(roll, 0, 9.0, R, 'wood', D)                                                  # bulging belly
    for sx in (1, -1):
        octa(roll, sx * 6.5, 4.0, R - 0.6, 'wood', D)                                   # tapering
        r, th = R - 1.1, 1.6                                                           # open end: octagonal wooden ring
        for rot in (None, ('x', 45)):
            ro = dict(rot=rot, rot_origin=[0, cy, 0])
            for sg in (1, -1):
                cb(roll, sx * 9.8, cy + sg * (r - th / 2) - th / 2, 0, 3.0, th, 0.86 * r, 'wood', decals=D, **ro)
                cb(roll, sx * 9.8, cy - 0.43 * r, sg * (r - th / 2), 3.0, 0.86 * r, th, 'wood', decals=D, **ro)
        octa(roll, sx * 8.62, 0.2, r - th - 0.3, 'hole')                                  # dark inside: octagonal, stays inside the ring       # dark inside, recessed
    hp = m.bone('hoops', [0, cy, 0], roll)
    sp = m.bone('spikes', [0, cy, 0], roll)
    for hx in (-6.4, 6.4):
        octa(hp, hx, 2.2, R - 0.6, 'hoop', grow=0.05)                                    # iron hoops hugging the taper
        rh = R - 0.6 + 0.05                                                           # hoop surface radius
        for (dy, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):                               # spikes sitting on each hoop
            for (w, o, h) in ((1.6, 0.0, 1.0), (0.9, 1.0, 1.0)):
                if dz:
                    cb(sp, hx, cy - w / 2, dz * (rh + o + h / 2), w, w, h, 'steel')
                else:
                    cb(sp, hx, cy + (rh + o if dy > 0 else -rh - o - h), 0, w, h, w, 'steel')
    m.bone('sword', [0, 24, 0], roll)                                                     # (kept, empty)
    for sz in (1, -1):                                                                    # feet out of the back end
        cb(roll, -L / 2 - 2.0, cy - 2.0, sz * 2.4, 4.0, 3.2, 3.0, 'skin')
        cb(roll, -L / 2 - 4.2, cy - 2.4, sz * 2.4, 1.0, 4.0, 3.6, 'sandal',
           decals={'west': pix(["....", "kkkk", "....", "...."], {'k': '#e8a878'})})
    pk = m.bone('peek', [L / 2, cy, 0], None)                                            # (kept, empty)
    # reuse the real barbarian head (face, hair, moustache), turned to look out of the +X end, rolling with the barrel
    import copy
    bb = barbarian()
    for k, v in bb.mats.items():
        m.mats.setdefault(k, v)
    fmap = {'north': 'east', 'south': 'west', 'east': 'south', 'west': 'north', 'up': 'up', 'down': 'down'}
    hx0, hy0 = L / 2 - 1.6, cy - 4.4                                                   # head half inside the opening                                                   # where the head's (0, 20.5, 0) pivot goes
    for bn in bb.bones:
        if bn.name not in ('head', 'hair', 'beard'):
            continue
        for c in bn.cubes:
            f, t = c['frm'], c['to']
            P = lambda v: [-v[2], v[1], v[0]]                                           # rotate 90 deg: -Z (face) -> +X
            p1, p2 = P(f), P(t)
            lo = [min(p1[i], p2[i]) for i in range(3)]; hi = [max(p1[i], p2[i]) for i in range(3)]
            nc = cb(roll, (lo[0] + hi[0]) / 2 + hx0, lo[1] - 20.5 + hy0, (lo[2] + hi[2]) / 2, hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], c['mat'])
            nc['decals'] = {fmap[k]: v for k, v in c['decals'].items()}
            nc['faces'] = {fmap[k]: v for k, v in c['faces'].items()}
    m.hitbox(1.8, 1.4)
    m.anim('idle', 0.589, 'loop', {'roll': {'rotation': [(0, [0, 0, 0]), (0.196, [-120, 0, 0]), (0.393, [-240, 0, 0]), (0.589, [-360, 0, 0])]},
                                   }, interp='linear')
    return m



def battle_ram():
    """Two real barbarians (cloned from barbarian()) carrying an octagonal log overhead with an iron ram head + rings"""
    import copy
    m = new_model('clash_battle_ram')
    bb = barbarian()
    for k, v in bb.mats.items():
        m.mats.setdefault(k, v)
    m.mats_({'log': ('#a86a3a', 'wood', {'planks': True}), 'log_d': ('#7a4a26', 'wood'), 'iron': ('#646a70', 'metal'),
             'iron_l': ('#8a9098', 'metal')})
    root = m.bone('root', [0, 0, 0])
    for pre, dz in (('a', -6.5), ('b', 6.5)):                                       # one in front, one behind
        dx = 0.0
        made = {}
        for bn in bb.bones:
            if bn.name in ('root', 'sword', 'hitbox'):
                continue
            nm = bn.name
            if nm == 'tc_sash':
                nm = 'tc_%s_shirt' % pre
            elif nm in ('arm_r', 'arm_l'):
                inner = nm == 'arm_r'
                nm = '%s_arm_%s' % (pre, 'in' if inner else 'out')
            else:
                nm = '%s_%s' % (pre, nm)
            par = made.get(bn.parent.name) if bn.parent is not None and bn.parent.name != 'root' else root
            nb = m.bone(nm, [bn.origin[0] + dx, bn.origin[1], bn.origin[2] + dz], par)
            made[bn.name] = nb
            for c in bn.cubes:
                f, t = c['frm'], c['to']
                nc = cb(nb, (f[0] + t[0]) / 2 + dx, f[1], (f[2] + t[2]) / 2 + dz, t[0] - f[0], t[1] - f[1], t[2] - f[2], c['mat'], rot=c['rot'])
                nc['decals'] = copy.deepcopy(c['decals']); nc['faces'] = dict(c['faces'])
    # the ram: octagonal log overhead, iron ram head in front, iron band + ring at the back
    ram = m.bone('ram', [0, 35.6, 0], root)
    cy = 35.6
    def octa(bone, z, ln, r, mat, dec=None):
        for rot in (None, ('z', 45)):
            cb(bone, 0, cy - r, z, 0.83 * r, 2 * r, ln, mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
            cb(bone, 0, cy - 0.415 * r, z, 2 * r, 0.83 * r, ln, mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
    grain = {f: [('rect', 0, k, 1, k + 0.04, '#7a4a26') for k in (0.3, 0.65)] for f in ('east', 'west', 'up', 'down')}
    octa(ram, -0.35, 30.3, 5.5, 'log', grain)                                            # big log
    octa(ram, -18.6, 7.0, 7.0, 'iron')                                                  # ram head
    octa(ram, -23.1, 2.0, 5.2, 'iron')                                                  # faceted nose
    octa(ram, -24.6, 1.0, 3.0, 'iron')
    tb = m.bone('tc_band', [0, cy, 7], ram)
    octa(ram, 9.6, 2.8, 6.3, 'iron')                                                   # back band
    for z in (-18.6, 9.6):                                                              # rivets
        for (rx, ry) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            r = 7.2 if z < 0 else 6.5
            cb(ram, rx * r, cy + ry * r - 0.5, z, 1.0, 1.0, 1.0, 'iron_l')
    for sx in (1, -1):                                                                  # rings on the sides
        for z in (-18.6, 9.6):
            x0 = sx * (7.4 if z < 0 else 6.6)
            cb(ram, x0 + sx * 0.6, cy - 2.0, z, 0.5, 0.5, 2.2, 'iron_l')
            cb(ram, x0 + sx * 0.6, cy - 2.0, z - 1.0, 0.5, 1.6, 0.5, 'iron_l')
            cb(ram, x0 + sx * 0.6, cy - 2.0, z + 1.0, 0.5, 1.6, 0.5, 'iron_l')
    import random
    rng = random.Random(5)
    for c in ram.cubes:                                                                 # natural worn iron / wood shading
        if c['mat'] in ('iron', 'iron_l'):
            for f in ('north', 'south', 'east', 'west', 'up', 'down'):
                d = [('lerp', '#9aa2aa', 0.45, 0.0, 'y'), ('shade', 0, 0.8, 1, 1, 0.8)]
                for _ in range(5):
                    x0, y0 = rng.random() * 0.85, rng.random() * 0.85
                    d.append(('shade', x0, y0, x0 + 0.12, y0 + 0.12, rng.choice((0.82, 1.12))))
                c['decals'][f] = d + c['decals'].get(f, [])
    shade_pass(m, ('log',))
    m.hitbox(1.4, 2.6)
    up_in_a, up_out_a = [-172, 0, -8], [-172, 0, 12]
    pose = {'a_arm_in': up_in_a, 'a_arm_out': up_out_a, 'b_arm_in': [-172, 0, 8], 'b_arm_out': [-172, 0, -12]}
    hold = {k: {'rotation': loop([v, [v[0] + 3, v[1], v[2]]], 2.0)} for k, v in pose.items()}
    hold['ram'] = {'position': loop([[0, 0, 0], [0, -0.4, 0]], 2.0)}
    m.anim('idle', 2.0, 'loop', hold)
    walk = {k: {'rotation': loop([v, v], 0.4)} for k, v in pose.items()}
    for pre, ph in (('a', 1), ('b', -1)):
        walk[pre + '_leg_r'] = {'rotation': loop([[-35 * ph, 0, 0], [35 * ph, 0, 0]], 0.4)}
        walk[pre + '_leg_l'] = {'rotation': loop([[35 * ph, 0, 0], [-35 * ph, 0, 0]], 0.4)}
    walk['ram'] = {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.2)}
    m.anim('walk', 0.4, 'loop', walk)
    atk = {k: {'rotation': [(0, v), (0.15, [v[0] + 20, v[1], v[2]]), (0.25, [v[0] - 15, v[1], v[2]]), (0.4, v)]} for k, v in pose.items()}
    atk['ram'] = {'position': [(0, [0, 0, 0]), (0.15, [0, 0, 3]), (0.25, [0, 0, -5]), (0.4, [0, 0, 0])]}
    m.anim('attack', 0.4, 'once', atk)
    common_tail(m, hit_bone='ram')
    return m



def barbarian_hut():
    """HQ vanilla-like Barbarian Hut: stone base + steps, plaster walls, thick wooden posts with steel studs,
    dark doorway, team-coloured plank gable roof, big sword on the roof, round target on an A-stand, elixir puddle"""
    m = new_model('clash_barbarian_hut')
    m.mats_({'stone': ('#a8a8a4', 'stone'), 'plaster': ('#c4c6c8', 'stone'), 'wood': ('#c08a4a', 'wood', {'planks': True}),
             'wood_d': ('#8a5a30', 'wood'), 'roof': ('#efefef', 'wood', {'planks': True}), 'steel': ('#b8c0c8', 'metal'),
             'void': ('#1a1612', 'plain'), 'gold': ('#e8b830', 'metal'), 'grip': ('#6a4426', 'leather'), 'elixir': ('#e040c8', 'glow'), 'dart': ('#d8343a', 'cloth')})
    root = m.bone('root', [0, 0, 0])
    top = m.bone('top', [0, 0, 0], root)
    cb(top, 0, 0, 0, 25, 2.0, 23, 'stone')                                              # stone base
    cb(top, 0, 0, -13.2, 9, 1.4, 3.4, 'stone')                                          # steps
    cb(top, 0, 1.4, -15.0, 9, 1.2, 1.8, 'stone')
    cb(top, 0, 2.0, 0.2, 17.6, 14, 15.8, 'plaster')                                      # walls (inside the posts)
    cb(top, 0, 2.0, -8.0, 7.0, 10.0, 0.4, 'void')                                        # dark doorway
    stud = {'north': pix(["....", ".kk.", ".kk.", "....", "....", "....", "....", ".kk.", ".kk.", "...."], {'k': '#b8c0c8'})}
    for sx in (1, -1):
        for sz in (1, -1):
            cb(top, sx * 10.0, 0, sz * 8.6, 3.2, 18.0, 3.2, 'wood')   # thick corner posts
            for y in (6.0, 12.0):
                if sz < 0:
                    cb(top, sx * 10.0, y, -10.4, 1.4, 1.4, 0.5, 'steel')                 # studs centred on the post
                    cb(top, sx * 10.0, y + 0.35, -10.8, 0.7, 0.7, 0.4, 'steel')
        cb(top, sx * 4.4, 2.0, -9.0, 1.8, 11.0, 1.6, 'wood_d')                          # door jambs
    for sz in (1, -1):
        cb(top, 0, 15.4, sz * 9.0, 24, 2.6, 2.6, 'wood')                                 # lintel beams
    for sx in (1, -1):
        cb(top, sx * 10.6, 15.4, 0, 2.4, 2.6, 18, 'wood')
    # back is taller: plaster steps up the side walls, back posts run higher
    for sx in (1, -1):
        for (z0, z1, y0, y1) in ((-4.0, 8.6, 18.0, 20.4), (0.0, 8.6, 20.4, 22.8), (4.0, 8.6, 22.8, 25.0)):
            cb(top, sx * 8.4, y0, (z0 + z1) / 2 - 0.6, 0.8, y1 - y0, z1 - z0 - 1.2, 'plaster')
        cb(top, sx * 10.0, 18.0, 8.6, 3.2, 8.0, 3.2, 'wood')                              # back posts continue up
    cb(top, 0, 18.0, 7.6, 16.6, 7.0, 0.8, 'plaster')
    cb(top, 0, 24.6, 9.2, 24.0, 2.0, 2.6, 'wood')                                        # back top beam
    # single-slope plank roof, high at the back, low over the front (team coloured), boards staggered
    import random
    rng = random.Random(11)
    roof = m.bone('tc_shields', [0, 0, 0], top)
    for i in range(9):
        x = -11.0 + i * 2.75
        ln = 27.0 + rng.uniform(-1.6, 1.4)
        dz = rng.uniform(-0.8, 0.8)
        dy = rng.choice((0.0, 0.35, 0.7))
        cb(roof, x, 19.2 + dy, -1.2 + dz, 2.6, 1.2, ln, 'roof', rot=('x', -22.5), rot_origin=[0, 19.8, -12.0],
           decals={'up': [('rect', 0.4, 0, 0.45, 1, '#b8b8b8'), ('rect', 0.1, 0.3, 0.9, 0.33, '#c8c8c8')]})
    for (x, z) in ((-5.5, -4.0), (4.6, 3.0), (8.4, -7.0)):
        cb(roof, x, 20.6, z, 3.6, 0.5, 3.2, 'roof', rot=('x', -22.5), rot_origin=[0, 19.8, -12.0])   # patch boards
    # big sword lying across the front beam: hilt top-left, blade down to the right
    ro = dict(rot=('z', 22.5), rot_origin=[-1.0, 17.6, -15.0])
    cb(top, -5.0, 17.0, -15.0, 12.0, 2.2, 0.8, 'steel', decals={'north': [('rect', 0, 0.4, 1, 0.6, '#e0e6ec')]}, **ro)   # blade
    cb(top, -11.6, 17.3, -15.0, 1.4, 1.6, 0.7, 'steel', **ro)                              # tip
    cb(top, 1.6, 16.0, -15.0, 1.2, 4.8, 1.4, 'gold', **ro)                              # cross-guard
    cb(top, 3.8, 17.5, -15.0, 3.4, 1.2, 1.2, 'grip', **ro)                              # grip
    cb(top, 6.0, 17.4, -15.0, 1.4, 1.4, 1.4, 'gold', **ro)                              # pommel
    m.bone('tc_shield', [0, 15, -12.6], top)
    # round practice target on an A-frame stand
    # dart target hung on the left side wall, with red darts
    tg = m.bone('target', [9.6, 9, 0], top)
    for rot in (None, ('x', 45)):
        ro = dict(rot=rot, rot_origin=[9.6, 9, 0])
        cb(tg, 9.4, 9 - 3.6, 0, 0.8, 7.2, 3.0, 'wood', **ro)
        cb(tg, 9.4, 9 - 1.5, 0, 0.8, 3.0, 7.2, 'wood', **ro)
        cb(tg, 9.3, 9 - 3.9, 0, 0.6, 7.8, 3.2, 'steel', **ro)                            # steel rim
        cb(tg, 9.3, 9 - 1.6, 0, 0.6, 3.2, 7.8, 'steel', **ro)
    cb(tg, 9.9, 8.3, 0, 0.3, 1.4, 1.4, 'void')                                           # bullseye
    for (dy, dz) in ((0.6, -0.8), (-1.0, 1.2), (1.8, 1.0)):                              # darts
        cb(tg, 10.6, 9 + dy, dz, 1.6, 0.4, 0.4, 'grip')
        cb(tg, 11.6, 9 + dy - 0.3, dz, 0.6, 1.0, 1.0, 'dart')
    # elixir barrel on an A-frame stand beside the hut, with a tap pipe dripping elixir
    eb = m.bone('elixir_barrel', [-16.5, 7, 2], top)
    for rot in (None, ('x', 45)):
        ro = dict(rot=rot, rot_origin=[-16.5, 7, 2])
        cb(eb, -16.5, 7 - 4.4, 2, 6.0, 8.8, 3.6, 'wood', **ro)
        cb(eb, -16.5, 7 - 1.8, 2, 6.0, 3.6, 8.8, 'wood', **ro)
        for hx in (-18.8, -14.2):
            cb(eb, hx, 7 - 4.7, 2, 1.0, 9.4, 3.9, 'steel', **ro)                           # hoops
            cb(eb, hx, 7 - 1.95, 2, 1.0, 3.9, 9.4, 'steel', **ro)
    cb(eb, -16.5, 6.0, -2.8, 1.2, 1.2, 2.0, 'steel')                                     # tap pipe out the front
    cb(eb, -16.5, 5.0, -3.6, 1.0, 1.4, 0.8, 'steel')
    cb(eb, -16.5, 3.6, -3.6, 0.5, 1.2, 0.5, 'elixir')                                    # drip
    for sz in (1, -1):
        cb(eb, -16.5 + 2.4, 0, 2 + sz * 2.6, 1.4, 5.0, 1.4, 'wood_d', rot=('x', sz * 22.5), rot_origin=[-14.1, 2.5, 2 + sz * 2.6])   # A-frame legs
        cb(eb, -16.5 - 2.4, 0, 2 + sz * 2.6, 1.4, 5.0, 1.4, 'wood_d', rot=('x', sz * 22.5), rot_origin=[-18.9, 2.5, 2 + sz * 2.6])
    cb(top, -16.0, 0.05, -4.6, 5.0, 0.2, 3.4, 'elixir')                                  # elixir puddle
    m.hitbox(3.0, 2.0)
    m.anim('idle', 3.0, 'loop', {'target': {'rotation': loop([[0, 0, 0], [0, 0, 2], [0, 0, 0], [0, 0, -2]], 3.0)}})
    m.anim('attack', 0.5, 'once', {'top': {'scale': [(0, [1, 1, 1]), (0.15, [1.04, 0.96, 1.04]), (0.5, [1, 1, 1])]}})
    m.anim('deploy', 0.8, 'once', {'root': {'position': [(0, [0, -20, 0]), (0.6, [0, 1, 0]), (0.8, [0, 0, 0])]}})
    m.anim('death', 1.0, 'hold', {'root': {'scale': [(0, [1, 1, 1]), (0.6, [1.05, 0.5, 1.05]), (1.0, [1.1, 0.05, 1.1])]}})
    m.anim('hit', 0.3, 'once', {'top': {'position': [(0, [0, 0, 0]), (0.1, [0.6, 0, 0]), (0.2, [-0.6, 0, 0]), (0.3, [0, 0, 0])]}})
    shade_pass(m, ('wood', 'plaster', 'stone'))
    return m



def bats():
    """HQ vanilla-like CR Bat: chubby dark-purple body, huge pointed ears, team-coloured glowing eyes,
    little fangs, segmented membrane wings with finger bones, tiny clawed feet"""
    m = new_model('clash_bat')
    m.mats_({'fur': ('#4a3a5e', 'fur'), 'fur_d': ('#33284a', 'fur'), 'skin': ('#6a4a7a', 'skin'), 'mem': ('#5a3a6a', 'leather', {'stitch': False}),
             'ear_in': ('#a07090', 'skin'), 'eye': ('#ffffff', 'glow'), 'fang': ('#f4f0e6', 'bone'), 'mouth': ('#2a1020', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    cb(body, 0, 3.0, 0, 5.4, 5.2, 4.8, 'fur')                                          # chubby body
    cb(body, 0, 2.4, 0, 4.2, 0.6, 3.8, 'fur_d')
    cb(body, 0, 3.4, -2.5, 3.4, 3.6, 0.3, 'skin')                                      # belly
    for sx in (1, -1):
        cb(body, sx * 1.2, 1.6, 0.2, 0.8, 1.0, 0.8, 'skin')                              # tiny feet
    hd = m.bone('head', [0, 8, -0.4], body)
    cb(hd, 0, 7.8, -0.4, 5.6, 4.2, 4.6, 'fur')
    cb(hd, 0, 8.6, -2.9, 2.4, 1.6, 0.6, 'fur_d')                                        # snout
    cb(hd, 0, 7.9, -2.75, 2.6, 0.6, 0.3, 'mouth')
    for sx in (1, -1):
        cb(hd, sx * 0.8, 7.3, -2.8, 0.5, 0.8, 0.4, 'fang')                                # fangs
        e = m.bone('ts_eye_' + ('r' if sx > 0 else 'l'), [sx * 1.5, 10, -2.7], hd)
        cb(e, sx * 1.5, 9.6, -2.75, 1.4, 1.2, 0.3, 'eye')                                  # glowing eyes (team)
        ear = m.bone('ear_' + ('r' if sx > 0 else 'l'), [sx * 2.0, 12, -0.4], hd)
        cb(ear, sx * 2.0, 12.0, -0.4, 1.8, 3.0, 0.8, 'fur', decals={'north': [('rect', 0.25, 0.2, 0.75, 1, '#a07090')]})
        cb(ear, sx * 2.3, 15.0, -0.4, 1.0, 1.4, 0.6, 'fur')                               # pointed tip
        w = m.bone('wing_' + ('r' if sx > 0 else 'l'), [sx * 2.6, 7.4, 0.4], body)
        for k, (x0, ln, top, h) in enumerate(((2.6, 3.2, 8.4, 4.4), (5.8, 2.8, 9.2, 5.2), (8.6, 2.4, 9.6, 4.6))):
            cb(w, sx * (x0 + ln / 2), top - h, 0.4, ln, h, 0.4, 'mem',
               decals={'north': [('rect', 0, 0.85, 1, 1, '#3a2448')], 'south': [('rect', 0, 0.85, 1, 1, '#3a2448')]})   # membrane panels
            cb(w, sx * (x0 + ln), top - h, 0.4, 0.5, h + 0.4, 0.6, 'fur_d')               # finger bones
        cb(w, sx * 6.4, 8.6, 0.4, 7.8, 0.8, 0.8, 'fur_d')                                 # wing arm
        cb(w, sx * 2.9, 7.6, 0.4, 1.0, 1.2, 0.9, 'fur_d')
    m.hitbox(0.6, 0.8)
    shade_pass(m, ('fur', 'mem'))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, 0, -a], [0, 0, a * 0.6]], L)}, 'wing_l': {'rotation': loop([[0, 0, a], [0, 0, -a * 0.6]], L)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.5)}, 'ear_r': {'rotation': loop([[0, 0, -4], [0, 0, 4]], 0.5)}}
    idle.update(flap(0.25, 40))
    m.anim('idle', 0.5, 'loop', idle)
    walk = dict(idle); walk['body'] = {'rotation': loop([[15, 0, 0], [15, 0, 0]], 0.5)}
    m.anim('walk', 0.5, 'loop', walk)
    atk = flap(0.4, 50); atk = {k: {'rotation': [(0, v['rotation'][0][1]), (0.4, v['rotation'][0][1])]} for k, v in atk.items()}
    atk['body'] = {'rotation': [(0, [0, 0, 0]), (0.15, [-20, 0, 0]), (0.25, [30, 0, 0]), (0.4, [0, 0, 0])]}
    atk['root'] = {'position': [(0, [0, 0, 0]), (0.25, [0, -1, -3]), (0.4, [0, 0, 0])]}
    m.anim('attack', 0.4, 'once', atk)
    common_tail(m)
    return m



def bomb_tower():
    """HQ vanilla-like Bomb Tower: stone footing with pyramid studs + corner spikes, two thick pine posts with rope
    coils, riveted diagonal brace, plank crate top with a team stripe, goggled skeleton bomber hugging a bomb"""
    m = new_model('clash_bomb_tower')
    m.mats_({'stone': ('#9aa0a6', 'stone'), 'stone_d': ('#7e848a', 'stone'), 'pine': ('#d8a850', 'wood', {'planks': True}),
             'pine_d': ('#b0843a', 'wood'), 'rope': ('#b8945a', 'rope'), 'rope_d': ('#957444', 'rope'), 'steel': ('#9aa2aa', 'metal'),
             'tc': ('#efefef', 'cloth'), 'bone': ('#ece6d6', 'bone'), 'cap': ('#efefef', 'leather'), 'brass': ('#c8a040', 'metal'),
             'glass': ('#bfe6f2', 'gem'), 'void': ('#141210', 'plain'), 'spark': ('#ffd040', 'glow'), 'flame': ('#ff8a20', 'glow'),
             'core': ('#fff8e0', 'glow')})
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    tw = m.bone('base_tower', [0, 0, 0], base)
    import math
    for k in range(8):                                                                  # thick octagonal ring of stone blocks
        ang = k * 45
        x, z = math.sin(math.radians(ang)) * 14.0, -math.cos(math.radians(ang)) * 14.0
        if k % 2 == 0:
            ax = k % 4 == 0
            cb(tw, x, 0, z, 12.0 if ax else 6.0, 11.0, 6.0 if ax else 12.0, 'stone')
            cb(tw, x, 11.0, z, 10.8 if ax else 4.8, 1.2, 4.8 if ax else 10.8, 'stone_d')     # chamfered top
            for d in (-1, 1):                                                          # pyramid studs
                if ax:
                    sg = 1 if z > 0 else -1
                    cb(tw, x + d * 3.0, 3.4, z + sg * 3.5, 4.0, 4.0, 1.0, 'stone_d'); cb(tw, x + d * 3.0, 4.4, z + sg * 4.3, 2.0, 2.0, 0.8, 'stone_d')
                else:
                    sg = 1 if x > 0 else -1
                    cb(tw, x + sg * 3.5, 3.4, z + d * 3.0, 1.0, 4.0, 4.0, 'stone_d'); cb(tw, x + sg * 4.3, 4.4, z + d * 3.0, 0.8, 2.0, 2.0, 'stone_d')
        else:
            ro = dict(rot=('y', 45 if k in (1, 5) else -45), rot_origin=[x, 5.5, z])
            cb(tw, x, 0, z, 12.0, 11.0, 6.0, 'stone', **ro)
            ox, oz = math.sin(math.radians(ang)) * 17.6, -math.cos(math.radians(ang)) * 17.6
            cb(tw, ox, 3.0, oz, 3.0, 4.0, 3.0, 'stone_d', **ro); cb(tw, ox * 1.08, 3.8, oz * 1.08, 1.6, 2.4, 1.6, 'stone_d', **ro)   # side spikes
    cb(tw, 0, 0, 0, 24, 1.0, 24, 'stone_d')                                             # floor inside the ring
    for sx in (1, -1):                                                                  # four thick splayed legs
        for sz in (1, -1):
            cb(tw, sx * 5.4, 6.0, sz * 6.0, 6.0, 23.0, 6.0, 'pine', rot=('z', sx * 22.5), rot_origin=[sx * 5.4, 29.0, sz * 6.0])
            for k2, (yy, ww) in enumerate(((22.6, 8.2), (24.4, 9.0), (26.2, 8.6))):
                cb(tw, sx * 5.4, yy, sz * 6.0, ww, 1.9, ww, 'rope' if k2 % 2 == 0 else 'rope_d')   # thick rope coils
    for sz in (1, -1):
        cb(tw, 0, 15.0, sz * 6.0, 18.0, 2.8, 2.4, 'pine_d')                              # thick cross braces
    for sx in (1, -1):
        cb(tw, sx * 7.4, 15.0, 0, 2.4, 2.8, 14.0, 'pine_d')
    cb(tw, 0, 14.0, -9.0, 22.0, 3.4, 1.6, 'pine', rot=('z', 22.5), rot_origin=[0, 15.7, -9.0])   # riveted diagonal brace (front)
    for x in (-8.0, 8.0):
        cb(tw, x, 15.7 + x * 0.414 - 0.7, -10.0, 1.4, 1.4, 0.6, 'steel')
    planks = {f: [('rect', 0, k, 1, k + 0.04, '#9a7030') for k in (0.33, 0.66)] for f in ('north', 'south', 'east', 'west')}
    cb(tw, 0, 33.0, 0, 18.4, 1.6, 18.4, 'pine_d', decals={'up': [('rect', k, 0, k + 0.03, 1, '#7a5420') for k in (0.25, 0.5, 0.75)]})   # closed lid
    for sz in (1, -1):                                                                  # crate on top
        cb(tw, 0, 29.0, sz * 9.6, 21.0, 11.0, 2.0, 'pine', decals=planks)
    for sx in (1, -1):
        cb(tw, sx * 9.6, 29.0, 0, 2.0, 11.0, 17.2, 'pine', decals=planks)
    cb(tw, 0, 29.0, 0, 18.0, 1.4, 18.0, 'pine_d')
    for sx in (1, -1):
        for sz in (1, -1):
            cb(tw, sx * 10.0, 28.6, sz * 10.0, 2.4, 12.0, 2.4, 'pine_d')                  # corner battens
    st = m.bone('base_tc_stripe', [0, 15, 0], tw)
    for sz in (1, -1):
        cb(st, 0, 28.9, sz * 10.7, 5.0, 11.2, 0.3, 'tc')                                  # centred team stripe, front + back
    TS = 1.5                                                                           # whole tower 1.5x bigger
    for bn in m.bones:
        if bn.name.startswith('base'):
            bn.origin = [v * TS for v in bn.origin]
            for c in bn.cubes:
                c['frm'] = [v * TS for v in c['frm']]; c['to'] = [v * TS for v in c['to']]; c['rot_origin'] = [v * TS for v in c['rot_origin']]
    # bomber on top = the real bomber model
    top = m.bone('top', [0, 52.0, 0], root)
    BS, BO = 1.5, (0, 52.0, 0)
    clone_into(m, bomber(), top, {'leg_r': 'top_leg_r', 'leg_l': 'top_leg_l', 'body': 'top_body', 'head': 'top_head', 'tc_band': 'top_tc_cap',
                                  'goggles': 'top_goggles', 'arm_r': 'top_arm_r', 'arm_l': 'top_arm_l', 'bomb_hand': 'top_bomb', 'fuse': 'top_fuse'}, s=BS, off=BO)
    m.hitbox(3.0, 5.0)
    shade_pass(m, ('pine', 'stone', 'rope'))
    m.anim('idle', 2.0, 'loop', {'top_head': {'rotation': loop([[0, 12, 0], [0, -12, 0]], 2.0)},
                                 'top_arm_r': {'rotation': loop([[-38, 0, -16], [-40, 0, -16]], 2.0)}, 'top_arm_l': {'rotation': loop([[-38, 0, 16], [-40, 0, 16]], 2.0)},
                                 'top_fuse': {'scale': loop([[1, 1, 1], [1.4, 1.4, 1.4]], 0.3)}})
    m.anim('attack', 0.8, 'once', {'top_arm_r': {'rotation': [(0, [-38, 0, -16]), (0.15, [40, 0, 8]), (0.3, [-150, 0, 0]), (0.8, [-38, 0, -16])]},
                                   'top_arm_l': {'rotation': [(0, [-38, 0, 16]), (0.8, [-38, 0, 16])]},
                                   'top_bomb': {'scale': [(0, [1, 1, 1]), (0.3, [1, 1, 1]), (0.32, [0, 0, 0]), (0.7, [0, 0, 0]), (0.8, [1, 1, 1])]},
                                   'top_body': {'rotation': [(0, [0, 0, 0]), (0.15, [-15, 0, 0]), (0.3, [20, 0, 0]), (0.8, [0, 0, 0])]}})
    m.anim('deploy', 0.8, 'once', {'root': {'position': [(0, [0, -30, 0]), (0.6, [0, 1, 0]), (0.8, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'base': {'position': [(0, [0, 0, 0]), (0.1, [0.6, 0, 0]), (0.2, [-0.6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 1.0, 'hold', {'base': {'scale': [(0, [1, 1, 1]), (0.6, [1.05, 0.5, 1.05]), (1.0, [1.1, 0.05, 1.1])]},
                                  'top': {'scale': [(0, [1, 1, 1]), (0.2, [0, 0, 0])]}})
    return m



def bomber():
    """HQ vanilla-like Bomber: big grinning skull, team leather flight cap with flaps, big brass goggles,
    separate ribs/spine/pelvis, knobby thin limbs, brown leather gloves, carries the user's bomb"""
    m = new_model('clash_bomber')
    m.mats_({'bone': ('#ece6d6', 'bone'), 'bone_d': ('#cdc6b2', 'bone'), 'tooth': ('#f8f6ee', 'bone'), 'void': ('#1c1814', 'plain'),
             'cap': ('#efefef', 'leather'), 'brass': ('#d8a040', 'metal'), 'lens': ('#1e3040', 'gem'), 'strap': ('#6a3e22', 'leather'),
             'glove': ('#7a4424', 'leather'), 'spark': ('#ffd040', 'glow'), 'flame': ('#ff8a20', 'glow'), 'core': ('#fff8e0', 'glow')})
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.6
        lg = m.bone('leg_' + side, [x, 8.6, 0], root)
        cb(lg, x, 5.0, 0, 1.2, 3.4, 1.2, 'bone')                                          # femur
        cb(lg, x, 4.4, -0.1, 1.7, 1.2, 1.7, 'bone_d')                                     # knee
        cb(lg, x, 1.0, 0, 1.0, 3.4, 1.0, 'bone')                                          # shin
        cb(lg, x, 0, -0.6, 2.4, 1.0, 3.4, 'bone_d', decals={'north': pix(["k.k.k", "....."], {'k': '#a8a294'})})   # bony foot
    body = m.bone('body', [0, 8.6, 0], root)
    cb(body, 0, 8.2, 0.2, 4.6, 1.6, 2.4, 'bone_d')                                       # pelvis
    for k, y in enumerate((9.8, 10.6, 11.4)):
        cb(body, 0, y, 0.6, 1.0, 0.6, 1.0, 'bone')                                       # vertebrae
    for k, (y, w) in enumerate(((12.3, 5.0), (13.5, 5.6), (14.7, 5.2))):
        cb(body, 0, y, 0.2, w, 0.8, 3.2, 'bone')                                         # ribs
    cb(body, 0, 12.3, -1.4, 1.0, 3.2, 0.4, 'bone_d')                                     # sternum
    cb(body, 0, 15.9, 0.2, 7.0, 0.8, 1.2, 'bone')                                        # collar bones
    hd = m.bone('head', [0, 17.2, 0], body)
    cb(hd, 0, 17.4, 0.2, 7.2, 6.4, 6.6, 'bone')                                          # big skull
    cb(hd, 0, 21.0, -3.2, 7.2, 2.8, 0.4, 'bone')                                         # face plate above the mouth
    cb(hd, 0, 19.0, -3.3, 6.0, 0.9, 0.4, 'tooth', decals={'north': pix(["tktktkt"], {'t': '#f8f6ee', 'k': '#4a4238'})})   # upper teeth
    cb(hd, 0, 16.8, -0.8, 6.6, 1.4, 5.6, 'bone')                                         # lower jaw, closed
    cb(hd, 0, 18.2, -3.3, 6.0, 0.8, 0.4, 'tooth', decals={'north': pix(["tktktk"], {'t': '#f8f6ee', 'k': '#4a4238'})})   # lower teeth
    cap = m.bone('tc_band', [0, 2.4, 0], hd)                                             # team leather flight cap
    cb(cap, 0, 23.4, 0.4, 7.8, 1.6, 7.2, 'cap')
    cb(cap, 0, 22.0, 0.4, 8.0, 1.6, 7.4, 'cap')
    cb(cap, 0, 17.6, 3.7, 7.8, 5.4, 0.6, 'cap')                                          # back
    for sx in (1, -1):
        cb(cap, sx * 3.85, 17.0, 0.8, 0.6, 5.4, 5.6, 'cap')                                # ear flaps
    gg = m.bone('goggles', [0, 2.4, 0], hd)
    for sx in (1, -1):
        cb(gg, sx * 1.75, 20.6, -3.75, 3.0, 3.0, 0.8, 'brass')                             # brass rims
        cb(gg, sx * 1.75, 21.1, -4.2, 2.0, 2.0, 0.2, 'lens', decals={'north': pix(["...", ".w.", "..."], {'w': '#8ac8e0'})})
    cb(gg, 0, 21.0, 0.4, 8.6, 1.4, 8.0, 'strap', decals={f: [('rect', 0, 0.0, 1, 0.2, '#4a2a16'), ('rect', 0, 0.8, 1, 1, '#4a2a16')] for f in ('east', 'west', 'south')})   # thick leather strap, clearly outside the cap
    for sx in (1, -1):
        cb(gg, sx * 4.35, 20.8, 1.2, 0.4, 1.8, 1.8, 'brass')                              # side buckles
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.6
        a = m.bone('arm_' + side, [x, 16.0, 0], body)
        cb(a, x, 12.4, 0, 0.9, 3.6, 0.9, 'bone')
        cb(a, x, 11.8, 0, 1.3, 1.0, 1.3, 'bone_d')                                         # elbow
        cb(a, x, 9.0, 0, 0.8, 3.0, 0.8, 'bone')
        cb(a, x, 8.8, 0, 2.2, 0.8, 2.2, 'glove')                                          # glove cuff
        cb(a, x, 6.8, -0.2, 2.0, 2.2, 2.0, 'glove', decals={'north': pix(["k.k.", "...."], {'k': '#5a3018'})})   # leather glove
    bh = m.bone('bomb_hand', [0, 11, -4], body)                                         # bomb hugged at the belly (body injected later)
    k = 0.42
    fz = m.bone('fuse', [0, 8.6 + 15.4 * k, -4.4], bh)
    def bs(x, y, z, w, mat):
        cb(fz, x * k, 8.6 + y * k, -4.4 + z * k, w * k, w * k, w * k, mat)
    bs(0, 14.6, 0, 2.2, 'flame'); bs(0, 15.0, 0, 1.4, 'spark'); bs(0, 15.3, 0, 0.7, 'core')
    for (dx, dy, dz) in ((1.5, 1.6, 0.5), (-0.8, 2.0, -0.7), (0.3, 2.5, 1.2), (1.9, 0.6, -1.0)):
        bs(dx, 15.0 + dy, dz, 0.45, 'spark')
    m.bone('tc_scarf', [0, 17.2, 0], body)
    m.hitbox(0.7, 1.6)
    hold = {'arm_r': {'rotation': loop([[-38, 0, -16], [-40, 0, -16]], 2.0)}, 'arm_l': {'rotation': loop([[-38, 0, 16], [-40, 0, 16]], 2.0)}, 'fuse': {'scale': loop([[1, 1, 1], [1.4, 1.4, 1.4]], 0.3)}}
    mc_idle(m, 2.0, extra=hold)
    mc_walk(m, 0.6, 30, arm_r=False, extra=hold)
    m.anim('attack', 0.7, 'once', {'arm_r': {'rotation': [(0, [-38, 0, -16]), (0.2, [40, 0, 8]), (0.35, [-150, 0, 0]), (0.7, [-38, 0, -16])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-10, 15, 0]), (0.35, [15, -10, 0]), (0.7, [0, 0, 0])]},
                                   'bomb_hand': {'scale': [(0, [1, 1, 1]), (0.35, [1, 1, 1]), (0.37, [0, 0, 0]), (0.62, [0, 0, 0]), (0.7, [1, 1, 1])]}})
    common_tail(m)
    shade_pass(m, ('bone', 'cap', 'glove'))
    return m




def firecracker():
    """Firecracker: slim girl with a pink bob + team headband, team dress with a ragged hem, dark hooded shoulder cape tied
    with rope, brown belt + gold buckle, black gloves + boots; a wooden plank firework launcher bound with rope rides on her
    right shoulder (team/gold striped rocket nose peeking out), left hand on her hip."""
    m = new_model('clash_firecracker')
    m.mats_({'skin': ('#f2c4a2', 'skin'), 'hair': ('#e85aa8', 'hair'), 'hair_d': ('#c03c88', 'hair'), 'tc': ('#efefef', 'cloth'),
             'cape': ('#3e4048', 'cloth'), 'cape_d': ('#2a2c32', 'cloth'), 'rope': ('#a87a4a', 'rope'), 'belt': ('#8a5430', 'leather'),
             'gold': ('#e8b030', 'metal'), 'glove': ('#2c2e34', 'leather'), 'boot': ('#34363c', 'leather'), 'wood': ('#8a5a34', 'soft'),
             'wood_d': ('#6a4224', 'soft'), 'rocket': ('#e8b030', 'soft'), 'void': ('#1a1210', 'plain'), 'lip': ('#d0507a', 'plain'),
             'flash': ('#ffd860', 'glow')})
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.9, 11, 0], root)
        cb(lg, sx * 1.9, 3.0, 0, 2.6, 8.0, 2.6, 'skin')                                                     # legs
        cb(lg, sx * 1.9, 0, -0.3, 3.2, 3.6, 3.6, 'boot', decals={'north': [('rect', 0.3, 0.1, 0.7, 0.5, '#5a3a28')]})   # chunky boots (laces)
        cb(lg, sx * 1.9, 3.2, 0, 3.4, 0.6, 3.4, 'boot')                                                     # boot cuff
    body = m.bone('body', [0, 11, 0], root)
    td = m.bone('tc_dress', [0, 11, 0], body)
    cb(td, 0, 9.4, 0, 6.6, 9.6, 3.8, 'tc')                                                                  # team dress
    cb(td, 0, 8.0, 0, 7.6, 3.0, 4.6, 'tc')                                                                  # flared skirt
    for k, x in enumerate((-3.2, -1.6, 0.0, 1.6, 3.2)):
        cb(td, x, 7.0 - (0.6 if k % 2 else 0), -2.1, 1.4, 1.2, 0.4, 'tc')                                   # ragged hem points
        cb(td, x, 7.0 - (0.6 if k % 2 == 0 else 0), 2.1, 1.4, 1.2, 0.4, 'tc')
    cb(body, 0, 12.4, 0, 7.0, 1.4, 4.2, 'belt')                                                             # belt
    cb(body, -1.2, 12.2, -2.2, 1.8, 1.8, 0.3, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#8a5430')]})   # gold buckle
    cp = m.bone('cape', [0, 19, 0], body)
    cb(cp, 0, 17.6, 0.2, 7.8, 2.4, 5.0, 'cape')                                                              # hooded shoulder cape
    cb(cp, 0, 16.2, 2.4, 7.4, 3.6, 0.8, 'cape_d')                                                            # short back drape
    cb(cp, 0, 19.6, 2.0, 5.6, 2.2, 1.6, 'cape_d')                                                            # hood folded at the neck
    for sx in (1, -1):
        cb(cp, sx * 1.0, 16.8, -2.6, 0.6, 1.8, 0.6, 'rope')                                                  # rope ties
    cb(cp, 0, 18.4, -2.6, 2.6, 0.7, 0.6, 'rope')
    hd = m.bone('head', [0, 19.6, 0], body)
    face = [('rect', 0.14, 0.50, 0.40, 0.64, '#ffffff'), ('rect', 0.60, 0.50, 0.86, 0.64, '#ffffff'),
            ('rect', 0.24, 0.50, 0.38, 0.64, '#3a7ac0'), ('rect', 0.62, 0.50, 0.76, 0.64, '#3a7ac0'),
            ('rect', 0.28, 0.53, 0.34, 0.60, '#141018'), ('rect', 0.66, 0.53, 0.72, 0.60, '#141018'),
            ('rect', 0.12, 0.46, 0.42, 0.50, '#2a1a20'), ('rect', 0.58, 0.46, 0.88, 0.50, '#2a1a20'),           # lashes
            ('rect', 0.15, 0.40, 0.40, 0.43, '#a03070'), ('rect', 0.60, 0.38, 0.85, 0.41, '#a03070'),           # one brow raised (smug)
            ('rect', 0.46, 0.66, 0.54, 0.74, '#e0a888'), ('rect', 0.40, 0.80, 0.60, 0.84, '#d0507a')]           # nose + lips
    cb(hd, 0, 19.6, 0, 6.0, 6.2, 5.8, 'skin', decals={'north': face}, dens=3)
    cb(hd, 0, 24.0, 0.2, 6.5, 2.4, 6.7, 'hair')                                                          # hair covering the whole crown                                                              # pink bob top
    for sx in (1, -1):
        cb(hd, sx * 3.15, 19.4, 0.6, 0.6, 5.4, 5.2, 'hair', decals={sx > 0 and 'east' or 'west': [('rect', 0, k, 1, k + 0.04, '#c03c88') for k in (0.3, 0.6)]})   # bob sides
    cb(hd, 0, 19.4, 3.2, 6.6, 5.4, 0.6, 'hair')                                                              # bob back
    cb(hd, 0, 24.0, -3.1, 6.4, 0.8, 0.6, 'hair_d')                                                           # blunt fringe
    hb = m.bone('tc_headband', [0, 24, 0], hd)
    cb(hb, 0, 23.2, 0.3, 7.3, 1.6, 7.0, 'tc', decals={g: [('rect', 0, 0.45, 1, 0.55, '#d0d0d0')] for g in ('north', 'south', 'east', 'west')})   # team knit headband
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.3
        a = m.bone('arm_' + side, [x, 18.4, 0], body)
        cb(a, x, 13.6, 0, 2.2, 5.2, 2.2, 'skin')                                                            # slim arm
        cb(a, x, 11.2, 0, 2.6, 2.8, 2.6, 'glove')                                                            # black glove
        cb(a, x, 13.4, 0, 2.8, 0.8, 2.8, 'glove')                                                            # glove cuff
    ln = m.bone('launcher', [6.6, 20.0, 1.0], body)                                                          # launcher resting on the right shoulder
    cb(ln, 6.6, 19.6, -4.0, 4.4, 4.4, 14.0, 'wood', decals={g: [('rect', 0.32, 0, 0.35, 1, '#6a4224'), ('rect', 0.65, 0, 0.68, 1, '#6a4224')] for g in ('north', 'south', 'east', 'west', 'up', 'down')})   # plank tube
    cb(ln, 6.6, 19.2, -10.4, 5.2, 5.2, 1.2, 'wood_d'); cb(ln, 6.6, 19.2, 2.4, 5.2, 5.2, 1.2, 'wood_d')     # end hoops
    cb(ln, 6.6, 19.9, -11.05, 3.8, 3.8, 0.2, 'void')                                                         # muzzle
    for z in (-6.4, -5.2, -4.0):
        cb(ln, 6.6, 19.3, z, 5.0, 5.0, 0.8, 'rope')                                                          # rope lashing
    rk = m.bone('tc_rocket', [6.6, 21.8, -11], ln)
    cb(rk, 6.6, 20.4, -11.6, 3.0, 3.0, 1.4, 'tc'); cb(rk, 6.6, 20.9, -12.6, 2.0, 2.0, 1.0, 'rocket'); cb(rk, 6.6, 21.4, -13.2, 1.0, 1.0, 0.6, 'tc')   # striped rocket nose
    fl = m.bone('muzzle', [6.6, 21.8, -12], ln)
    cb(fl, 6.6, 19.6, -14.6, 4.4, 4.4, 1.6, 'flash')
    m.hitbox(0.8, 1.9)
    Z = [0.01, 0.01, 0.01]
    AR = [-120, 0, 25]                                                               # right hand up gripping the launcher
    AL = [0, 0, -35]                                                                  # left hand out on the hip
    m.anim('idle', 1.6, 'loop', {'arm_r': {'rotation': [(0, AR), (0.8, [-118, 0, 26]), (1.6, AR)]},
                                 'arm_l': {'rotation': [(0, AL), (0.8, [0, 0, -38]), (1.6, AL)]},
                                 'body': {'position': [(0, [0, 0, 0]), (0.8, [0, -0.3, 0]), (1.6, [0, 0, 0])]},
                                 'head': {'rotation': [(0, [0, 6, 0]), (0.8, [0, -4, 0]), (1.6, [0, 6, 0])]},
                                 'muzzle': {'scale': [(0, Z), (1.6, Z)]}})
    m.anim('walk', 0.6, 'loop', {'leg_r': {'rotation': [(0, [28, 0, 0]), (0.3, [-28, 0, 0]), (0.6, [28, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-28, 0, 0]), (0.3, [28, 0, 0]), (0.6, [-28, 0, 0])]},
                                 'arm_r': {'rotation': [(0, AR), (0.6, AR)]},
                                 'arm_l': {'rotation': [(0, [20, 0, -8]), (0.3, [-20, 0, -8]), (0.6, [20, 0, -8])]},
                                 'body': {'position': [(0, [0, 0, 0]), (0.15, [0, 0.6, 0]), (0.3, [0, 0, 0]), (0.45, [0, 0.6, 0]), (0.6, [0, 0, 0])]},
                                 'muzzle': {'scale': [(0, Z), (0.6, Z)]}})
    m.anim('attack', 0.8, 'once', {'launcher': {'rotation': [(0, [0, 0, 0]), (0.15, [-8, 0, 0]), (0.2, [10, 0, 0]), (0.45, [0, 0, 0]), (0.8, [0, 0, 0])],
                                                'position': [(0, [0, 0, 0]), (0.2, [0, 0, 2.0]), (0.45, [0, 0, 0]), (0.8, [0, 0, 0])]},
                                   'tc_rocket': {'scale': [(0, [1, 1, 1]), (0.19, [1, 1, 1]), (0.2, Z), (0.6, Z), (0.8, [1, 1, 1])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-10, 0, 0]), (0.45, [0, 0, 0]), (0.8, [0, 0, 0])],
                                            'position': [(0, [0, 0, 0]), (0.2, [0, 0, 1.6]), (0.45, [0, 0, 0.4]), (0.8, [0, 0, 0])]},
                                   'arm_r': {'rotation': [(0, AR), (0.8, AR)]}, 'arm_l': {'rotation': [(0, AL), (0.8, AL)]},
                                   'muzzle': {'scale': [(0, Z), (0.19, Z), (0.2, [1.5, 1.5, 1.5]), (0.3, [1, 1, 1]), (0.36, Z), (0.8, Z)]}})
    common_tail(m)
    return m


def cursed_hog():
    """Cursed Hog (Mother Witch's curse): chubby pink pig, big snout, tan tusks with team rings, floppy ears, a glowing pink
    potion splat on the head and a purple skull mark on the hip, curly tail, dark hooves."""
    m = new_model('clash_cursed_hog')
    m.mats_({'pig': ('#f0a0a0', 'soft'), 'pig_d': ('#d88484', 'soft'), 'snout': ('#f4b4b0', 'soft'), 'hoof': ('#3a2a2a', 'plain'),
             'tusk': ('#e8d4a8', 'soft'), 'tc': ('#efefef', 'cloth'), 'goo': ('#e04ad0', 'glow'), 'eye': ('#ffffff', 'plain'),
             'mark': ('#6a3a96', 'plain'), 'mouth': ('#a04a5a', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    SK = pix(["..kkkk..", ".kkkkkk.", ".k..k..k", ".k..k..k", ".kkkkkk.", "..k.k.k."], {'k': '#6a3a96'})
    cb(body, 0, 4.0, 1.0, 8.4, 7.4, 11.0, 'pig', decals={'down': [('rect', 0.2, 0.1, 0.8, 0.9, '#f4b4b0')]})   # chubby body, skull mark on the hips
    cb(body, 0, 4.6, 1.0, 9.0, 6.0, 10.0, 'pig', dens=3)
    for sx in (1, -1):                                                                                     # purple skull mark on the hips
        X = sx * 4.55
        cb(body, X, 6.4, 3.6, 0.1, 2.4, 3.0, 'mark'); cb(body, X, 5.8, 3.6, 0.1, 0.6, 2.2, 'mark')
        for dz in (-0.7, 0.7):
            cb(body, X + sx * 0.02, 7.0, 3.6 + dz, 0.1, 0.9, 0.8, 'pig')                                    # eye holes
        for dz in (-0.7, 0.0, 0.7):
            cb(body, X, 5.0, 3.6 + dz, 0.1, 0.8, 0.4, 'mark')                                                 # teeth
    for sx in (1, -1):
        cb(body, sx * 2.0, 10.8, -1.0, 2.6, 0.5, 2.2, 'goo')                                                # potion drops on the back
    for i, (lx, lz) in enumerate(((2.4, -3.0), (-2.4, -3.0), (2.4, 5.0), (-2.4, 5.0))):
        lg = m.bone('leg_%d' % i, [lx, 4.5, lz], body)
        cb(lg, lx, 1.0, lz, 2.6, 3.6, 2.6, 'pig')
        cb(lg, lx, 0.0, lz, 2.8, 1.0, 2.8, 'hoof')                                                           # hooves
    tl = m.bone('tail', [0, 9, 6.5], body)
    cb(tl, 0, 8.6, 6.8, 0.8, 0.8, 1.6, 'pig_d'); cb(tl, 0.6, 9.2, 7.4, 0.8, 1.4, 0.8, 'pig_d'); cb(tl, 0, 10.2, 7.2, 1.2, 0.6, 0.8, 'pig_d')   # curly tail
    hd = m.bone('head', [0, 9, -4.5], body)
    cb(hd, 0, 6.0, -8.4, 7.4, 6.6, 6.0, 'pig')                                                               # big head
    cb(hd, 0, 6.6, -12.0, 4.4, 3.4, 1.6, 'snout', decals={'north': pix(["......", ".k..k.", ".k..k.", "......"], {'k': '#8a4a5a'})})   # snout + nostrils
    cb(hd, 0, 5.6, -11.4, 4.0, 0.6, 0.6, 'mouth')
    for sx in (1, -1):
        cb(hd, sx * 2.0, 10.0, -11.45, 1.4, 1.2, 0.1, 'eye', decals={'north': [('rect', 0.3, 0.2, 0.75, 0.8, '#3a2418')]})   # eyes
        cb(hd, sx * 3.6, 11.2, -7.6, 1.8, 2.4, 0.6, 'pig_d', rot=('z', sx * 22.5), rot_origin=[sx * 3.4, 12.0, -7.6])   # floppy ears
        cb(hd, sx * 2.8, 6.8, -12.0, 0.9, 2.4, 0.9, 'tusk', rot=('z', -sx * 22.5), rot_origin=[sx * 2.6, 6.8, -12.0])   # tusks curving up
        tr = m.bone('tc_ring_' + ('r' if sx > 0 else 'l'), [sx * 2.6, 7, -12], hd)
        cb(tr, sx * 2.6, 6.6, -12.0, 1.2, 0.6, 1.2, 'tc')                                                     # team rings on the tusks
    cb(hd, 0, 12.6, -8.6, 3.6, 0.8, 3.2, 'goo'); cb(hd, -1.2, 11.0, -11.45, 1.0, 1.8, 0.2, 'goo')             # glowing potion splat on the head
    m.hitbox(1.0, 1.2)
    m.anim('idle', 1.2, 'loop', {'head': {'rotation': [(0, [0, 0, 0]), (0.6, [4, 0, 0]), (1.2, [0, 0, 0])]},
                                 'tail': {'rotation': [(0, [0, 0, -15]), (0.6, [0, 0, 15]), (1.2, [0, 0, -15])]}})
    trot = {('leg_%d' % i): {'rotation': [(0, [-30 if i in (0, 3) else 30, 0, 0]), (0.2, [30 if i in (0, 3) else -30, 0, 0]), (0.4, [-30 if i in (0, 3) else 30, 0, 0])]} for i in range(4)}
    trot['body'] = {'position': [(0, [0, 0, 0]), (0.1, [0, 0.6, 0]), (0.2, [0, 0, 0]), (0.3, [0, 0.6, 0]), (0.4, [0, 0, 0])]}
    trot['tail'] = {'rotation': [(0, [0, 0, -20]), (0.2, [0, 0, 20]), (0.4, [0, 0, -20])]}
    m.anim('walk', 0.4, 'loop', trot)
    m.anim('attack', 0.6, 'once', {'head': {'rotation': [(0, [0, 0, 0]), (0.2, [-20, 0, 0]), (0.32, [25, 0, 0]), (0.6, [0, 0, 0])]},
                                   'body': {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 1.5]), (0.32, [0, 0, -2.0]), (0.6, [0, 0, 0])]}})
    common_tail(m)
    return m


def mother_witch():
    """Mother Witch: tall boxy purple hood with a pink V-chevron trim over the brow running down both sides of the face,
    wrinkly old face with glowing cyan eyes and a cackling open mouth (one tooth), purple robe with a darker apron (patch,
    team trim), brown belt with a gold skull buckle + wooden spoon, ragged pink-purple hem, tattered cape, pale arms with
    purple fingerless gloves, and a gnarled wooden staff carrying an iron cauldron dripping pink potion."""
    import random as _r
    m = new_model('clash_mother_witch')
    m.mats_({'skin': ('#f0c8a8', 'soft'), 'skin_d': ('#d8a888', 'soft'), 'hood': ('#7a4ab0', 'soft'), 'hood_l': ('#9464c4', 'soft'),
             'hood_d': ('#5a3488', 'soft'), 'lining': ('#2a1a40', 'plain'), 'pink': ('#e64aa8', 'soft'), 'pink_d': ('#c03888', 'soft'),
             'robe': ('#8a56bc', 'soft'), 'robe_d': ('#6a3a96', 'soft'), 'apron': ('#64368e', 'soft'), 'hem': ('#c050b0', 'soft'),
             'belt': ('#6a4630', 'soft'), 'gold': ('#d8ac4c', 'soft'), 'glove': ('#7a48a8', 'soft'), 'tc': ('#eeeeee', 'cloth'),
             'wood': ('#8a5a34', 'soft'), 'wood_l': ('#a87444', 'soft'), 'rope': ('#d8c08a', 'rope'), 'iron': ('#3e3a48', 'soft'),
             'iron_l': ('#5a5466', 'soft'), 'goo': ('#e04ad0', 'glow'), 'eye': ('#6af0ff', 'glow'), 'mouth': ('#4a1a22', 'plain'),
             'tooth': ('#f4eedc', 'plain'), 'boot': ('#3a2a40', 'soft')})
    R = _r.Random(11)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 1.8, 0.0, -0.4, 2.4, 4.0, 2.8, 'boot')                                                # little dark shoes
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 8.0, 0.2, 7.8, 4.2, 5.0, 'robe')                                                            # robe
    cb(body, 0, 3.0, 0.2, 9.2, 5.0, 6.0, 'robe')                                                            # flared robe
    for x in (-3.8, -2.2, -0.6, 1.0, 2.6, 3.9):                                                              # ragged pink-purple hem strips
        for z in (-2.85, 3.25):
            h = R.choice((1.6, 2.4, 3.2))
            cb(body, x, 3.0 - h, z, 1.4, h, 0.5, R.choice(('hem', 'robe_d')))
    for sx in (1, -1):
        for z in (-1.6, 0.4, 2.2):
            h = R.choice((1.6, 2.6, 3.4))
            cb(body, sx * 4.35, 3.0 - h, z, 0.5, h, 1.6, R.choice(('hem', 'robe_d')))
    cb(body, 0, 12.0, 0, 7.0, 10.4, 3.8, 'robe')                                                            # bodice
    ap = m.bone('tc_apron', [0, 12, -2], body)
    cb(ap, 0, 3.6, -2.95, 5.4, 9.0, 0.3, 'tc')                                                               # apron border (team)
    cb(body, 0, 3.8, -3.15, 4.6, 8.6, 0.3, 'apron', decals={'north': [('rect', 0.25, 0.45, 0.55, 0.65, '#8a56bc'), ('rect', 0.3, 0.5, 0.33, 0.6, '#3a1a50')]})   # dark apron + stitched patch
    cb(body, 0, 2.2, -3.15, 2.2, 1.6, 0.3, 'apron')                                                          # pointed apron tip
    cb(body, 0, 11.6, 0, 7.6, 1.6, 4.4, 'belt')                                                              # belt
    sk = pix(["......", ".kk.kk", ".kk.kk", "...k..", "......", ".k.k.k"], {'k': '#5a4020'})
    cb(body, 0, 10.9, -2.4, 2.6, 2.8, 0.6, 'gold', decals={'north': sk})                                     # gold skull buckle
    cb(body, 3.0, 7.0, -2.0, 0.8, 4.4, 0.4, 'wood_l'); cb(body, 3.0, 6.0, -2.0, 1.8, 1.6, 0.6, 'wood_l')      # wooden spoon on the belt
    cp = m.bone('cape', [0, 24, 2.4], body)
    cb(cp, 0, 2.6, 2.8, 9.4, 20.4, 0.8, 'hood', decals={'south': [('fn', _folds(0.8, 1.1, 2))]})              # tattered cape
    for x in (-3.8, -1.4, 1.0, 3.4):
        h = R.choice((2.6, 3.8, 5.0))
        cb(cp, x, 2.6 - h, 2.8, 2.0, h, 0.8, R.choice(('hood_d', 'pink_d')))
    hd = m.bone('head', [0, 24, 0], body)
    face = [('rect', 0.15, 0.36, 0.42, 0.44, '#8a5a50'), ('rect', 0.58, 0.36, 0.85, 0.44, '#8a5a50'),             # heavy brows
            ('rect', 0.1, 0.62, 0.22, 0.66, '#d8a888'), ('rect', 0.78, 0.62, 0.9, 0.66, '#d8a888')]               # wrinkles
    cb(hd, 0, 24.0, 0.2, 6.6, 7.0, 6.6, 'skin', decals={'north': face}, dens=3)                              # old face
    for sx in (1, -1):
        cb(hd, sx * 1.6, 27.3, -3.2, 2.0, 1.2, 0.1, 'eye')                                                     # glowing cyan eyes
    cb(hd, 0, 26.0, -3.6, 1.4, 1.4, 1.0, 'skin_d')                                                           # bulbous nose
    cb(hd, 0, 24.4, -3.15, 3.6, 1.4, 0.1, 'mouth')                                                           # cackling open mouth
    cb(hd, 0.6, 25.0, -3.25, 0.6, 0.7, 0.1, 'tooth')                                                         # the one tooth
    cb(hd, 0, 23.4, -1.6, 4.6, 1.0, 3.6, 'skin')                                                             # chin
    ho = m.bone('hood', [0, 24, 0], hd)
    for sx in (1, -1):
        cb(ho, sx * 4.2, 21.4, 0.6, 1.4, 12.0, 8.0, 'hood')                                                    # hood sides
        cb(ho, sx * 3.6, 21.6, -3.3, 0.3, 10.0, 0.5, 'lining')
        cb(ho, sx * 3.9, 21.0, -3.75, 1.4, 12.0, 0.8, 'pink')                                                  # pink trim down the face
    cb(ho, 0, 21.4, 4.4, 9.8, 12.0, 1.0, 'hood_d')                                                           # back
    cb(ho, 0, 31.6, 0.6, 9.8, 4.4, 9.6, 'hood', decals={'up': [('shade', 0, 0, 1, 1, 1.08)]})                   # tall boxy crown
    cb(ho, 0, 35.8, 0.6, 1.0, 0.6, 9.6, 'hood_l')                                                            # ridge seam on top
    for sx in (1, -1):
        cb(ho, sx * 2.0, 29.4, -4.0, 4.6, 1.4, 1.0, 'pink', rot=('z', sx * 22.5), rot_origin=[0, 28.6, -4.0])   # pink V-chevron over the brow
        cb(ho, sx * 2.2, 30.6, -4.0, 4.6, 1.8, 0.9, 'hood', rot=('z', sx * 22.5), rot_origin=[0, 29.8, -4.0])  # hood brim above the chevron
    cb(ho, 0, 31.8, -4.0, 9.4, 2.2, 0.9, 'hood')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.0
        a = m.bone('arm_' + side, [x, 22.5, 0], body)
        cb(a, x, 20.0, 0.2, 3.2, 3.4, 3.6, 'hood', decals={g: [('fn', _folds(0.85, 1.1, 1))] for g in ('north', 'south', 'east', 'west')})   # drooping sleeve
        cb(a, x, 12.6, 0, 2.2, 7.6, 2.2, 'skin')                                                               # thin pale arm
        cb(a, x, 10.6, 0, 2.8, 2.6, 2.8, 'glove')                                                              # fingerless glove
        cb(a, x, 9.4, -0.4, 2.4, 1.4, 2.0, 'skin', decals={'north': [('rect', 0, 0.6, 1, 1, '#4a2a5a')]})       # bony fingers (dark nails)
    st = m.bone('staff', [5.0, 10.6, -0.4], m.by_name('arm_r'))
    for i, y in enumerate(range(-2, 36, 2)):
        cb(st, 5.0 + (0.25 if i % 2 else -0.25), y, -0.4 + (0.2 if i % 3 == 0 else -0.2), 1.5, 2.0, 1.5, 'wood' if i % 2 else 'wood_l')   # gnarled staff
    for y in (9.6, 10.6, 11.6, 2.0):
        cb(st, 5.0, y, -0.4, 1.9, 0.8, 1.9, 'rope')                                                            # wrapped grip
    for sx in (1, -1):
        cb(st, 5.0 + sx * 1.6, 35.0, -0.4, 2.4, 1.0, 1.0, 'wood', rot=('z', -sx * 45), rot_origin=[5.0 + sx * 1.0, 35.0, -0.4])   # forked claw holding the pot
    cn = m.bone('cauldron', [5.0, 38, -0.4], st)
    cb(cn, 5.0, 36.4, -0.4, 6.4, 5.6, 6.4, 'iron', decals={g: [('rect', 0.15, 0.15, 0.35, 0.3, '#5a5466')] for g in ('north', 'south', 'east', 'west')})   # iron pot
    cb(cn, 5.0, 37.2, -1.0, 7.4, 3.6, 5.2, 'iron'); cb(cn, 5.0, 37.2, -1.0, 5.2, 3.6, 7.4, 'iron')            # round belly
    cb(cn, 5.0, 42.0, -1.0, 6.8, 0.8, 6.8, 'iron_l')                                                         # rim
    cb(cn, 5.0, 42.1, -1.0, 5.4, 0.8, 5.4, 'goo')                                                            # pink potion surface
    for sx in (1, -1):
        cb(cn, 5.0 + sx * 3.9, 40.4, -1.0, 0.8, 1.4, 1.6, 'iron_l')                                            # handles
    for (dx, dz, y, h) in ((-2.6, -3.0, 35.0, 3.6), (1.4, -3.3, 36.2, 2.4), (3.0, 1.6, 34.6, 4.0)):
        cb(cn, 5.0 + dx, y, -1.0 + dz, 1.2, h, 0.6 if abs(dz) > 2 else 1.2, 'goo')                             # dripping potion
    cb(cn, 5.0 - 2.6, 37.6, -4.2, 1.4, 1.2, 0.6, 'goo')
    m.hitbox(0.8, 2.4)
    Z = [0.01, 0.01, 0.01]
    SA = [-25, 0, 6]
    UP = lambda v: [-v[0], 0, -v[2]]                                                  # staff counter-rotation: stays upright in the fist
    m.anim('idle', 2.0, 'loop', {'arm_r': {'rotation': [(0, SA), (1.0, [-28, 0, 7]), (2.0, SA)]},
                                 'staff': {'rotation': [(0, UP(SA)), (1.0, UP([-28, 0, 7])), (2.0, UP(SA))]},
                                 'arm_l': {'rotation': [(0, [-40, 0, -20]), (1.0, [-46, 0, -24]), (2.0, [-40, 0, -20])]},
                                 'body': {'position': [(0, [0, 0, 0]), (1.0, [0, 0.4, 0]), (2.0, [0, 0, 0])]},
                                 'head': {'rotation': [(0, [0, 6, 0]), (1.0, [3, -6, 0]), (2.0, [0, 6, 0])]},
                                 'cape': {'rotation': [(0, [4, 0, 0]), (1.0, [7, 0, 0]), (2.0, [4, 0, 0])]}})
    m.anim('walk', 0.8, 'loop', {'leg_r': {'rotation': [(0, [22, 0, 0]), (0.4, [-22, 0, 0]), (0.8, [22, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-22, 0, 0]), (0.4, [22, 0, 0]), (0.8, [-22, 0, 0])]},
                                 'arm_r': {'rotation': [(0, SA), (0.4, [-30, 0, 6]), (0.8, SA)]},
                                 'staff': {'rotation': [(0, UP(SA)), (0.4, UP([-30, 0, 6])), (0.8, UP(SA))]},
                                 'arm_l': {'rotation': [(0, [-30, 0, -14]), (0.4, [-10, 0, -14]), (0.8, [-30, 0, -14])]},
                                 'body': {'position': [(0, [0, 0, 0]), (0.2, [0, 0.5, 0]), (0.4, [0, 0, 0]), (0.6, [0, 0.5, 0]), (0.8, [0, 0, 0])]},
                                 'cape': {'rotation': [(0, [10, 0, 0]), (0.4, [16, 0, 0]), (0.8, [10, 0, 0])]}})
    m.anim('attack', 0.8, 'once', {'arm_l': {'rotation': [(0, [-40, 0, -20]), (0.25, [-150, 0, -10]), (0.4, [-80, 0, 0]), (0.6, [-75, 0, -4]), (0.8, [-40, 0, -20])]},
                                   'arm_r': {'rotation': [(0, SA), (0.25, [-60, 0, 6]), (0.45, [-30, 0, 6]), (0.8, SA)]},
                                   'staff': {'rotation': [(0, UP(SA)), (0.25, [40, 0, -6]), (0.45, UP([-30, 0, 6])), (0.8, UP(SA))]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-6, 0, 0]), (0.4, [8, 0, 0]), (0.8, [0, 0, 0])]},
                                   'head': {'rotation': [(0, [0, 0, 0]), (0.4, [-8, 0, 0]), (0.8, [0, 0, 0])]}})
    common_tail(m)
    return m


def electro_giant():
    """Electro Giant: giant build, bald head with a spiky ginger star-moustache, gold-rimmed goggles with glowing cyan
    lenses, a big riveted team collar plate over bare shoulders, crossed leather straps, brown belt with a gold hex-nut
    buckle, ragged indigo shorts, bare feet, chunky brown gloves with steel cuffs; on the back a dark battery box with gold
    coils and two rods topped with blue electrode balls, lightning crackling between them."""
    m = new_model('clash_electro_giant')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'hair': ('#e0702c', 'hair'), 'hair_d': ('#c05418', 'hair'),
             'tc': ('#efefef', 'cloth'), 'rivet': ('#5a5a72', 'soft'), 'strap': ('#7a5034', 'leather'), 'belt': ('#7a5034', 'leather'),
             'gold': ('#e8b030', 'metal'), 'gold_d': ('#b88418', 'metal'), 'lens': ('#5ae8ff', 'glow'), 'shorts': ('#3e3a6a', 'cloth'),
             'glove': ('#7a4a2e', 'leather'), 'glove_d': ('#5a341e', 'leather'), 'steel': ('#8a929c', 'soft'), 'box': ('#2e2e44', 'soft'),
             'box_l': ('#44445e', 'soft'), 'ball': ('#3a52b8', 'soft'), 'zap': ('#e4f8ff', 'glow'), 'zap_b': ('#7ae8ff', 'glow'),
             'eyew': ('#ffffff', 'plain'), 'silver': ('#b8c0c8', 'metal')})
    D = '#c88a64'
    r = Rig(m, 1.75); B = r.box
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = r.bone('leg_' + side, [x, 11, 0], root)
        B(lg, x, 1.2, 0, 3.8, 9.8, 3.8, 'skin')                                                     # bare legs
        B(lg, x, 7.4, 0, 4.4, 3.8, 4.4, 'shorts')   # shorts legs
        B(lg, x, 7.0, 0, 4.6, 0.6, 4.6, 'shorts', decals={f: pix(["k.k.k.k", "......."], {'k': '#2a2650'}) for f in ('north', 'south', 'east', 'west')})   # ragged hem
        B(lg, x, 0, -0.6, 4.4, 1.4, 5.4, 'skin_d', decals={'north': pix(["k.k.k.k", "......."], {'k': D})})   # bare feet + toes
    body = r.bone('body', [0, 11, 0], root)
    B(body, 0, 11.0, 0, 9.0, 3.0, 5.0, 'shorts')
    B(body, 0, 13.6, 0, 9.4, 10.6, 5.4, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.6, D)]})   # bare barrel chest
    for sx in (1, -1):
        B(body, sx * 2.6, 14.0, -2.75, 1.0, 9.0, 0.3, 'strap', rot=('z', sx * 22.5), rot_origin=[sx * 2.6, 18.5, -2.75])   # crossed leather straps
        B(body, sx * 2.6, 14.0, 2.75, 1.0, 9.0, 0.3, 'strap', rot=('z', -sx * 22.5), rot_origin=[sx * 2.6, 18.5, 2.75])
    B(body, 0, 13.2, 0, 10.0, 1.8, 6.0, 'belt')                                                   # brown belt
    B(body, 0, 12.7, -3.05, 2.8, 2.8, 0.3, 'gold', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#7a5034')]})   # gold hex-nut buckle
    B(body, 0, 13.0, -3.05, 2.0, 3.2, 0.25, 'gold')
    B(body, 0, 12.9, -3.05, 3.2, 2.4, 0.25, 'gold')
    tc = r.bone('tc_collar', [0, 23, 0], body)                                                    # big riveted team collar plate
    B(tc, 0, 21.0, 0, 11.4, 2.8, 6.6, 'tc')
    B(tc, 0, 19.6, -3.2, 7.2, 1.6, 0.4, 'tc')                                                     # front bib
    B(tc, 0, 18.2, -3.2, 3.6, 1.4, 0.4, 'tc')
    for sx in (1, -1):
        B(tc, sx * 5.8, 20.4, 0, 2.6, 2.6, 6.2, 'tc')                                              # shoulder caps
    for (x, y, z) in ((-4.2, 22.2, -3.35), (4.2, 22.2, -3.35), (-2.2, 20.0, -3.45), (2.2, 20.0, -3.45), (0, 18.6, -3.45), (-6.2, 22.4, 0), (6.2, 22.4, 0)):
        B(body, x, y, z, 0.7, 0.7, 0.3, 'rivet')                                                     # hex rivets
    hd = r.bone('head', [0, 24.0, -0.4], body)
    B(hd, 0, 23.8, -0.4, 7.2, 7.0, 6.6, 'skin', decals={'up': [('rect', 0.3, 0.3, 0.7, 0.7, '#f8c8a0')]})   # bald head
    for sx in (1, -1):
        B(hd, sx * 3.75, 25.6, 0.6, 0.4, 1.6, 1.4, 'skin')                                           # ears
        B(hd, sx * 3.65, 26.6, 1.8, 0.4, 2.0, 2.2, 'hair')                                           # ginger side tufts
        B(hd, sx * 1.7, 26.6, -3.95, 2.8, 2.8, 0.5, 'gold')                                          # goggle rims
        B(hd, sx * 1.7, 27.0, -4.25, 2.0, 2.0, 0.2, 'lens')                                          # glowing lenses
        B(hd, sx * 3.7, 27.1, -1.6, 0.3, 0.8, 4.6, 'strap')                                          # goggle strap
        # spiky star moustache: three pointed tufts each side
        B(hd, sx * 1.8, 24.2, -4.1, 3.2, 1.6, 0.8, 'hair', decals={'north': [('rect', 0.0, 0.7, 1.0, 1.0, '#c05418')]})
        B(hd, sx * 4.0, 24.6, -3.8, 2.2, 1.0, 0.8, 'hair', rot=('z', sx * 22.5), rot_origin=[sx * 3.0, 25.0, -3.6])   # tufts sweeping out
        B(hd, sx * 3.4, 22.4, -3.8, 1.2, 2.0, 0.8, 'hair_d', rot=('z', -sx * 22.5), rot_origin=[sx * 2.8, 24.0, -3.6])   # tufts sweeping down
    for sx in (1, -1):
        B(hd, sx * 1.8, 29.5, -3.85, 3.0, 0.9, 0.7, 'hair', decals={'north': [('rect', 0, 0.6, 1, 1, '#c05418')]})   # bushy ginger brows over the goggles
        B(hd, sx * 3.5, 29.9, -3.7, 1.4, 0.8, 0.7, 'hair_d', rot=('z', sx * 22.5), rot_origin=[sx * 3.0, 30.0, -3.7])   # flicked-up brow tips
    B(hd, 0, 26.8, -3.95, 1.0, 0.6, 0.4, 'gold')                                                  # goggle bridge
    B(hd, 0, 24.8, -4.4, 1.4, 1.8, 1.0, 'skin_d')                                                 # nose
    B(hd, 0, 23.2, -4.1, 4.4, 1.0, 0.8, 'hair_d')                                                 # chin tuft
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.6
        a = r.bone('arm_' + side, [x, 23.0, 0], body)
        B(a, x, 17.0, 0, 4.4, 5.2, 4.4, 'skin')                                                     # huge shoulders
        B(a, x, 12.6, 0, 3.8, 4.6, 3.8, 'skin')
        B(a, x, 11.6, 0, 4.6, 1.6, 4.6, 'steel')                                                    # steel glove cuff
        B(a, x, 8.6, -0.2, 4.8, 3.6, 4.8, 'glove', decals={'north': pix(["k.k.k", ".....", "....."], {'k': '#5a341e'})})   # chunky glove
        B(a, x + sx * 2.6, 11.0, 0, 1.0, 1.4, 1.4, 'steel')                                         # cuff bolt
    bp = r.bone('pack', [0, 20, 3.4], body)                                                        # battery pack on the back
    B(bp, 0, 13.8, 4.4, 7.4, 9.4, 2.4, 'box', decals={'south': [('rect', 0, 0, 1, 0.1, '#44445e'), ('rect', 0, 0.9, 1, 1, '#44445e')]})
    for k, y in enumerate((15.0, 17.2, 19.4)):
        B(bp, 0, y, 5.9, 6.8, 1.9, 1.2, 'gold', decals={'south': [('rect', 0, 0, 1, 0.25, '#f8d060'), ('rect', 0, 0.8, 1, 1, '#b88418')]})   # gold coils
    B(bp, 0, 23.0, 4.4, 2.0, 0.8, 2.0, 'box_l')
    B(bp, 4.0, 16.4, 5.0, 1.2, 1.6, 1.0, 'steel')                                                  # gauge
    for sx in (1, -1):
        B(bp, sx * 2.6, 23.2, 4.4, 0.8, 5.4, 0.8, 'steel')                                          # electrode rods
        B(bp, sx * 2.6, 28.4, 4.4, 3.2, 3.2, 3.2, 'ball', decals={f: [('rect', 0.15, 0.15, 0.45, 0.45, '#6a86e8')] for f in ('north', 'south', 'east', 'west')})   # blue electrode balls
        B(bp, sx * 2.6, 28.0, 4.4, 2.4, 4.0, 2.4, 'ball')
        B(bp, sx * 2.6, 28.8, 4.4, 4.0, 2.4, 2.4, 'ball')
    zp = r.bone('zap', [0, 30, 4.4], bp)                                                           # lightning between the balls
    for (x, y, w, h) in ((-1.4, 30.6, 1.4, 0.5), (-0.6, 30.0, 0.5, 1.2), (0.2, 29.6, 1.2, 0.5), (0.8, 29.6, 0.5, 1.4), (1.4, 30.6, 1.0, 0.5),
                         (-0.2, 31.8, 0.5, 1.6), (0.4, 32.8, 0.5, 1.4)):
        B(zp, x, y, 4.4, w, h, 0.5, 'zap')
    WX, LS = 1.25, 1.6
    for bn in m.bones:
        if bn.name == 'root': continue
        leg = bn.name.startswith('leg_')
        for c in bn.cubes:
            if not leg and bn.name not in ('head',):
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][0] *= WX
            if leg:
                if c['to'][1] > 3: c['to'][1] -= LS
                if c['frm'][1] > 3: c['frm'][1] -= LS
            else:
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][1] -= LS * 1.0
        if not leg and bn.name != 'head': bn.origin[0] *= WX
        bn.origin[1] -= LS if bn.name != 'root' else 0
    m.hitbox(2.2, 3.6)
    shade_pass(m, ('skin',))
    flick = lambda L: {'scale': [(round(L * k / 6, 3), [1, 1, 1] if k % 2 == 0 else [1.2, 0.7, 1]) for k in range(7)]}
    AO = [0, 0, 18]
    m.anim('idle', 2.4, 'loop', {'arm_r': {'rotation': [(0, [0, 0, 18]), (1.2, [-3, 0, 20]), (2.4, [0, 0, 18])]},
                                 'arm_l': {'rotation': [(0, [0, 0, -18]), (1.2, [-3, 0, -20]), (2.4, [0, 0, -18])]},
                                 'body': {'position': [(0, [0, 0, 0]), (1.2, [0, -0.5, 0]), (2.4, [0, 0, 0])]},
                                 'zap': flick(2.4)})
    m.anim('walk', 1.4, 'loop', {'leg_r': {'rotation': [(0, [22, 0, 0]), (0.7, [-22, 0, 0]), (1.4, [22, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-22, 0, 0]), (0.7, [22, 0, 0]), (1.4, [-22, 0, 0])]},
                                 'arm_r': {'rotation': [(0, [-20, 0, 16]), (0.7, [20, 0, 16]), (1.4, [-20, 0, 16])]},
                                 'arm_l': {'rotation': [(0, [20, 0, -16]), (0.7, [-20, 0, -16]), (1.4, [20, 0, -16])]},
                                 'body': {'position': [(0, [0, 0, 0]), (0.35, [0, 0.8, 0]), (0.7, [0, 0, 0]), (1.05, [0, 0.8, 0]), (1.4, [0, 0, 0])]},
                                 'zap': flick(1.4)})
    m.anim('attack', 1.0, 'once', {'arm_r': {'rotation': [(0, [0, 0, 18]), (0.35, [-150, 0, 10]), (0.5, [-20, 0, 0]), (1.0, [0, 0, 18])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.35, [-8, 10, 0]), (0.5, [12, -8, 0]), (1.0, [0, 0, 0])]},
                                   'zap': {'scale': [(0, [1, 1, 1]), (0.45, [1.8, 1.8, 1.8]), (0.6, [1, 1, 1]), (1.0, [1, 1, 1])]}})
    common_tail(m)
    return m


def electro_dragon():
    """Electro Dragon: the baby dragon body recoloured electric blue with a cyan belly, cyan wing membranes, white back
    spikes and a purple tongue; a huge blocky cyan lower jaw with a zig-zag rim, a cyan horn on the snout, cyan-ringed eyes
    and crackling sparks around the mouth (shown when attacking)."""
    m = new_model('clash_electro_dragon')
    root = m.bone('root', [0, 0, 0])
    src = baby_dragon()
    names = {b.name: b.name.replace('ts_', 'x_') for b in src.bones if b.name not in ('root', 'hitbox')}   # no soft team tint on limbs
    made = clone_into(m, src, root, names)
    pre = 'cl_baby_dragon_'
    FLAT = {'grn': '#2f6fc4', 'grn_d': '#2a64b4', 'belly': '#4ed0e6', 'tan': '#4ed0e6', 'wing': '#2a64b4', 'wing_m': '#4ed0e6',
            'tongue': '#7a44c8', 'gum': '#5a3aa0', 'mouth': '#3a2a6a', 'throat': '#2a1e50', 'tooth': '#2a64b4', 'eye': '#ffffff', 'band': '#efefef'}
    for k, c in FLAT.items():
        m.mats[pre + k] = (c, 'plain', {})                                               # flat colours, no gradients
    REMAP = {'#2a5a1a': '#1c2c5a', '#86c85e': '#3ab8d0', '#c45a68': '#5a2ea8', '#b8b8b8': '#1e508a', '#d0ccc0': '#3ab8d0'}
    for bn in m.bones:
        if bn.name.endswith('_leg'):
            for c in bn.cubes:
                if c['mat'] == pre + 'tan': c['mat'] = pre + 'grn_d'                       # blue feet + paws (spikes stay white)
    for bn in m.bones:                                                                  # drop the baby dragon's shading decals
        for c in bn.cubes:
            c['decals'] = {g: [d for d in v if d[0] not in ('shade', 'lerp', 'fn')] for g, v in c['decals'].items()} if isinstance(c['decals'], dict) else c['decals']
            c['decals'] = {g: [tuple(REMAP.get(x, x) if isinstance(x, str) else x for x in d) if isinstance(d, tuple) else d for d in v] for g, v in c['decals'].items()}
    m.mats_({'cyan': ('#4ed0e6', 'plain'), 'cyan_d': ('#3ab8d0', 'plain'), 'zap': ('#e4f8ff', 'glow'), 'zap_b': ('#7ae8ff', 'glow'),
             'iris': ('#34b8c8', 'plain'), 'mouth_in': ('#3a2470', 'plain')})
    hd, jaw, body = made['head'], made['jaw'], made['body']
    # big blocky cyan lower jaw with a zig-zag rim
    zig = [('rect', k / 8, 0, k / 8 + 0.0625, 0.22, '#00000000') for k in range(0, 8, 2)]
    cb(jaw, 0, 13.2, -6.6, 10.4, 4.2, 9.0, 'cyan')
    for k in range(5):
        cb(jaw, -4.0 + k * 2.0, 17.4, -10.75, 1.2, 1.0, 0.5, 'cyan')                                         # zig-zag front rim
    for sx in (1, -1):
        for k in range(4):
            cb(jaw, sx * 4.95, 17.4, -9.0 + k * 2.2, 0.5, 1.0, 1.2, 'cyan')                                  # zig-zag side rims
    tg = made['tongue']                                                              # tongue lies in the mouth (no longer hangs over the jaw)
    tg.cubes[:] = [c for c in tg.cubes if (c['to'][1] - c['frm'][1]) < 2.0]
    for c in tg.cubes:
        c['frm'][1] += 0.5; c['to'][1] += 0.5; c['frm'][2] -= 0.6; c['to'][2] -= 0.6
    cb(jaw, 0, 17.4, -6.6, 8.6, 0.25, 7.6, 'mouth_in')                                # dark purple mouth floor
    cb(hd, 0, 23.0, -9.6, 1.6, 2.0, 2.0, 'cyan'); cb(hd, 0, 25.0, -9.2, 1.0, 1.2, 1.2, 'cyan_d')            # horn on the snout
    for bn in m.bones:                                                                  # eyes: white, big cyan iris, dark slit pupil (toward the front)
        for c in bn.cubes:
            if c['mat'] == pre + 'eye':
                c['decals'] = {'east': [('rect', 0.36, 0.26, 0.88, 0.86, '#34c0d8'), ('rect', 0.28, 0.36, 0.96, 0.76, '#34c0d8'), ('rect', 0.46, 0.38, 0.8, 0.76, '#14203a'), ('rect', 0.4, 0.46, 0.86, 0.68, '#14203a'), ('rect', 0.62, 0.4, 0.76, 0.52, '#ffffff'), ('rect', 0.48, 0.62, 0.54, 0.68, '#ffffff')],
                               'west': [('rect', 0.12, 0.26, 0.64, 0.86, '#34c0d8'), ('rect', 0.04, 0.36, 0.72, 0.76, '#34c0d8'), ('rect', 0.2, 0.38, 0.54, 0.76, '#14203a'), ('rect', 0.14, 0.46, 0.6, 0.68, '#14203a'), ('rect', 0.24, 0.4, 0.38, 0.52, '#ffffff'), ('rect', 0.46, 0.62, 0.52, 0.68, '#ffffff')]}
                c['dens'] = 4
    # sparks crackling round the mouth (attack only)
    zp = m.bone('zap', [0, 18, -10], hd)
    for (x, y, z, w, h, d) in ((-3.0, 19.0, -12.6, 0.6, 2.4, 0.6), (-2.4, 21.0, -13.0, 1.8, 0.6, 0.6), (2.6, 18.6, -12.8, 0.6, 2.6, 0.6),
                               (3.2, 20.6, -13.2, 1.8, 0.6, 0.6), (0.0, 16.0, -13.6, 0.6, 2.0, 0.6), (0.8, 15.6, -13.6, 1.8, 0.6, 0.6)):
        cb(zp, x, y, z, w, h, d, 'zap')
    cb(zp, 0, 17.0, -12.8, 3.4, 3.4, 0.6, 'zap_b')
    m.hitbox(1.4, 1.8)
    return m


def flying_machine():
    """Flying Machine: upright bulging wooden barrel with riveted octagonal steel bands top + bottom, a rope looped around
    it, a stubby iron cannon poking out of a hole in the front, a 4-blade wooden propeller on a steel hub on top, and the
    pilot inside - only his team-coloured trousers and brown boots dangle below, pedalling a little crank."""
    m = new_model('clash_flying_machine')
    m.mats_({'wood': ('#b06a34', 'soft'), 'wood_d': ('#8a4e24', 'soft'), 'steel': ('#9aa2aa', 'soft'), 'steel_d': ('#6e767e', 'soft'),
             'rivet': ('#d8dde2', 'soft'), 'rope': ('#d4a066', 'rope'), 'iron': ('#4e545a', 'soft'), 'iron_d': ('#2c3034', 'soft'),
             'void': ('#141414', 'plain'), 'tc': ('#efefef', 'cloth'), 'boot': ('#6a4026', 'leather'), 'blade': ('#b8743c', 'soft'),
             'flash': ('#ffd860', 'glow')})
    ST = lambda: {g: [('fn', _staves(True, base=(176, 106, 52), seam=(112, 62, 28), upright=True))] for g in ('north', 'south', 'east', 'west')}
    MET = {g: [('fn', _soft_metal(1.2, 0.8))] for g in ('north', 'south', 'east', 'west', 'up', 'down')}
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 16, 0], root)
    # round bulging barrel: each slice is a 12-sided disc (two crossing slabs + a square), radius bulges at the middle
    import math as _m
    def disc(bn, y, h, r, mat, dec=None):
        cb(bn, 0, y, 0, 2 * r, h, 2 * r * 0.6, mat, decals=dec)
        cb(bn, 0, y, 0, 2 * r * 0.6, h, 2 * r, mat, decals=dec)
        cb(bn, 0, y, 0, 2 * r * 0.72, h, 2 * r * 0.72, mat, decals=dec)
    for (y, h, r) in ((8.0, 2.0, 5.2), (10.0, 2.5, 6.2), (12.5, 3.0, 6.9), (15.5, 3.0, 7.1), (18.5, 2.5, 6.6), (21.0, 2.0, 5.6)):
        disc(body, y, h, r, 'wood', ST())
    cb(body, 0, 7.7, 0, 7.0, 0.4, 7.0, 'wood_d'); cb(body, 0, 22.9, 0, 7.8, 0.4, 7.8, 'wood_d')               # lids
    # riveted steel bands hugging the top + bottom of the barrel
    for (y, r) in ((7.8, 5.7), (20.9, 6.1)):
        disc(body, y, 2.4, r, 'steel', MET)
        for k in range(8):
            ang = k * _m.pi / 4
            rr = r + 0.05 if k % 2 == 0 else r * 0.9
            cb(body, round(_m.sin(ang) * rr, 2), y + 0.75, round(-_m.cos(ang) * rr, 2), 0.9, 0.9, 0.9, 'rivet')   # rivets
    # rope looped round the belly
    for k in range(4):
        dx, dz = ((0, -7.25), (7.25, 0), (0, 7.25), (-7.25, 0))[k]
        cb(body, dx, 15.9 + (0.8 if k % 2 else -0.4), dz, 9.2 if dz else 1.2, 1.3, 1.2 if dz else 9.2, 'rope',
           decals={g: [('rect', q, 0, q + 0.05, 1, '#a87840') for q in (0.1, 0.3, 0.5, 0.7, 0.9)] for g in ('north', 'south', 'east', 'west', 'up')})
    for sx in (1, -1):
        for sz in (1, -1):
            cb(body, sx * 5.1, 16.0 + (0.3 if sx > 0 else 0.0), sz * 5.1, 1.2, 1.3, 5.0, 'rope', rot=('y', 45 * sx * sz), rot_origin=[sx * 5.1, 16.0, sz * 5.1])
    # cannon poking out of the front hole
    cb(body, 0, 12.4, -7.15, 6.2, 6.4, 0.2, 'void')                                                         # hole
    cn = m.bone('cannon', [0, 15.6, -6], body)
    cb(cn, 0, 13.2, -9.4, 5.0, 5.0, 7.0, 'iron', decals=MET)                                                # barrel
    cb(cn, 0, 12.7, -12.9, 6.0, 6.0, 1.8, 'iron')                                                          # muzzle lip
    cb(cn, 0, 13.9, -13.85, 3.6, 3.6, 0.2, 'void')                                                         # bore
    fl = m.bone('muzzle', [0, 15.7, -13], cn)
    cb(fl, 0, 13.9, -15.2, 3.8, 3.8, 1.6, 'flash')
    # propeller on top
    cb(body, 0, 23.6, 0, 3.0, 2.4, 3.0, 'steel_d')                                                          # mast
    pr = m.bone('prop', [0, 26, 0], body)
    cb(pr, 0, 26.0, 0, 5.2, 2.2, 5.2, 'steel', decals=MET)                                                  # hub
    cb(pr, 0, 28.2, 0, 2.8, 1.4, 2.8, 'steel_d')                                                            # cap
    for k in range(3):
        bl = m.bone('blade_%d' % k, [0, 26, 0], pr)
        bl.rot = [0, 120 * k, 0]
        cb(bl, 0, 26.4, -10.4, 4.6, 0.9, 15.0, 'blade', decals={'up': [('fn', _soft_wood)], 'down': [('fn', _soft_wood)]})   # wooden blade
        cb(bl, 0, 25.9, -3.8, 3.6, 2.0, 3.0, 'steel_d')                                                    # blade clamp
        cb(bl, 0, 27.7, -3.6, 1.0, 0.4, 1.0, 'rivet')
    # pilot's legs dangling under the barrel + pedal crank
    pl = m.bone('tc_pants', [0, 9, 0], body)
    for sx in (1, -1):
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 2.0, 9.0, 0], pl)
        cb(lg, sx * 2.0, 3.0, 0, 2.6, 6.2, 2.6, 'tc')                                                       # team trousers
        cb(lg, sx * 2.0, 0.6, -0.4, 3.0, 2.6, 3.6, 'boot', decals={'north': [('rect', 0, 0.75, 1, 1, '#3a2414')]})   # boots
    ck = m.bone('crank', [0, 3.0, -2.6], body)
    cb(ck, 0, 1.8, -2.6, 0.6, 2.4, 2.4, 'steel_d')                                                         # crank wheel
    cb(ck, 0, 2.6, -2.6, 6.0, 0.6, 0.6, 'steel')                                                          # axle + pedals
    for sx in (1, -1):
        cb(ck, sx * 3.3, 2.2, -2.6, 1.0, 1.4, 1.6, 'steel_d')
    cb(body, 2.6, 2.0, 2.4, 0.7, 7.0, 0.7, 'rope')                                                         # dangling rope
    K, C = 1.2, [0, 15.5, 0]                                                       # bigger barrel; parts riding on it shift with it
    for c in body.cubes:
        for k in ('frm', 'to', 'rot_origin'):
            c[k] = [C[i] + (c[k][i] - C[i]) * K for i in range(3)]
    def shift(bn, d):
        bn.origin = [bn.origin[i] + d[i] for i in range(3)]
        for c in bn.cubes:
            for k in ('frm', 'to', 'rot_origin'):
                c[k] = [c[k][i] + d[i] for i in range(3)]
        for ch in bn.children: shift(ch, d)
    shift(pr, [0, (23.3 - C[1]) * (K - 1), 0])
    shift(cn, [0, 0, -7.2 * (K - 1)])
    shift(pl, [0, (7.7 - C[1]) * (K - 1), 0]); shift(ck, [0, (7.7 - C[1]) * (K - 1), 0])
    m.hitbox(1.6, 2.0)
    Z = [0.01, 0.01, 0.01]
    spin = lambda L, n: {'rotation': [(round(L * k / 4, 3), [0, -90 * k * n, 0]) for k in range(5)]}
    pedal = lambda L: {'rotation': [(round(L * k / 4, 3), [-90 * k, 0, 0]) for k in range(5)]}
    m.anim('idle', 0.8, 'loop', {'prop': spin(0.8, 4), 'crank': pedal(0.8),
                                 'body': {'position': [(0, [0, 0, 0]), (0.4, [0, 0.8, 0]), (0.8, [0, 0, 0])], 'rotation': [(0, [0, 0, 2]), (0.4, [0, 0, -2]), (0.8, [0, 0, 2])]},
                                 'leg_r': {'rotation': [(0, [20, 0, 0]), (0.4, [-20, 0, 0]), (0.8, [20, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-20, 0, 0]), (0.4, [20, 0, 0]), (0.8, [-20, 0, 0])]},
                                 'muzzle': {'scale': [(0, Z), (0.8, Z)]}})
    m.anim('walk', 0.6, 'loop', {'prop': spin(0.6, 4), 'crank': pedal(0.6),
                                 'body': {'rotation': [(0, [8, 0, 0]), (0.3, [10, 0, 0]), (0.6, [8, 0, 0])], 'position': [(0, [0, 0, 0]), (0.3, [0, 0.6, 0]), (0.6, [0, 0, 0])]},
                                 'leg_r': {'rotation': [(0, [30, 0, 0]), (0.3, [-30, 0, 0]), (0.6, [30, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-30, 0, 0]), (0.3, [30, 0, 0]), (0.6, [-30, 0, 0])]},
                                 'muzzle': {'scale': [(0, Z), (0.6, Z)]}})
    m.anim('attack', 0.6, 'once', {'prop': spin(0.6, 3),
                                   'cannon': {'position': [(0, [0, 0, 0]), (0.1, [0, 0, 0]), (0.14, [0, 0, 1.6]), (0.4, [0, 0, 0]), (0.6, [0, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.14, [-6, 0, 0]), (0.4, [0, 0, 0]), (0.6, [0, 0, 0])]},
                                   'muzzle': {'scale': [(0, Z), (0.12, Z), (0.14, [1.4, 1.4, 1.4]), (0.22, [1.0, 1.0, 1.0]), (0.28, Z), (0.6, Z)]}})
    common_tail(m)
    return m


def ram_rider():
    """Ram Rider: stocky brown-grey ram (vanilla goat-like) with big curled tan horns, angry brows, tongue lolling out and a
    team bandana tied over the forehead; rider girl with a tall black flat-top, gold neck rings + armbands, terracotta dress,
    team sash and sandals, whirling a rope bola with two stones overhead in her right hand."""
    m = new_model('clash_ram_rider')
    m.mats_({'ram': ('#8a7466', 'soft'), 'ram_d': ('#6a5648', 'soft'), 'ram_l': ('#b8a494', 'soft'), 'muzzle': ('#b8a89a', 'skin'),
             'horn': ('#d8c4a0', 'bone'), 'horn_d': ('#b49c78', 'bone'), 'hoof': ('#2e2626', 'plain'), 'tongue': ('#e07a8a', 'skin'),
             'eye': ('#ffffff', 'plain'), 'tc': ('#efefef', 'cloth'), 'skin': ('#9a6440', 'skin'), 'skin_d': ('#7e4e30', 'skin'),
             'hair': ('#1e1a1a', 'hair'), 'dress': ('#d4743c', 'cloth'), 'dress_d': ('#b45a2a', 'cloth'), 'gold': ('#e8b030', 'metal'),
             'sandal': ('#8a5a30', 'leather'), 'rope': ('#b08a5a', 'rope'), 'stone': ('#c8ccd0', 'soft')})
    root = m.bone('root', [0, 0, 0])
    # ---- ram: short, barrel-bodied, woolly
    ram = m.bone('pony', [0, 9, 0], root)
    cb(ram, 0, 8.0, 1.0, 11.0, 10.0, 17.0, 'ram', decals={'down': [('rect', 0.2, 0.1, 0.8, 0.9, '#a8988a')]})   # woolly body
    cb(ram, 0, 17.6, 1.0, 9.0, 0.8, 14.0, 'ram_d')                                                         # back ridge
    for i, (lx, lz) in enumerate(((3.2, -5.0), (-3.2, -5.0), (3.2, 7.0), (-3.2, 7.0))):
        lg = m.bone('leg_%d' % i, [lx, 9, lz], ram)
        cb(lg, lx, 2.0, lz, 3.4, 7.0, 3.4, 'ram_d')                                                        # stubby leg
        cb(lg, lx, 0.0, lz, 3.8, 2.2, 3.8, 'hoof')                                                         # hoof
    tl = m.bone('tail', [0, 15, 9.6], ram)
    cb(tl, 0, 13.4, 10.0, 3.0, 3.0, 2.0, 'ram_l')                                                          # stubby tail
    hd = m.bone('pony_head', [0, 15, -7], ram)
    cb(hd, 0, 12.0, -9.5, 8.0, 8.4, 7.0, 'ram', decals={'north': [('rect', 0, 0, 1, 0.25, '#5a4c46')]})    # big blocky head
    cb(hd, 0, 11.0, -14.0, 6.0, 5.4, 3.0, 'muzzle', decals={'north': pix(["......", "k....k", "......", ".kkkk."], {'k': '#3a2a26'})})   # snout, nostrils + mouth
    cb(hd, 1.3, 10.4, -15.9, 1.8, 1.8, 0.8, 'tongue', decals={'north': [('rect', 0.45, 0, 0.55, 0.7, '#c05a6a')]}, rot=('x', -22.5), rot_origin=[1.3, 12.0, -15.5])   # tongue lolling out of the mouth corner
    for sx in (1, -1):
        cb(hd, sx * 2.2, 16.6, -13.05, 2.0, 1.4, 0.2, 'eye', decals={'north': [('rect', 0.0 if sx > 0 else 0.5, 0, 0.5 if sx > 0 else 1.0, 1, '#2a1a10')]})   # eyes
        cb(hd, sx * 2.3, 18.0, -13.3, 3.0, 0.8, 0.6, 'ram_d', rot=('z', -sx * 22.5), rot_origin=[sx * 2.3, 18.4, -13.0])   # angry brows
        cb(hd, sx * 4.4, 15.0, -9.0, 1.2, 2.4, 3.0, 'ram_d')                                              # floppy ears
        # big curled horn: up-back from the brow, round the side, tip forward under the ear
        for (x, y, z, w, h, d) in ((3.6, 18.6, -10.6, 3.0, 2.6, 3.4), (5.0, 19.8, -8.2, 3.2, 3.0, 3.6), (6.4, 18.8, -5.6, 3.2, 3.2, 3.4),
                                   (7.0, 15.8, -5.0, 3.0, 3.4, 3.2), (6.8, 13.4, -7.0, 2.8, 3.0, 3.0), (6.4, 12.4, -9.6, 2.4, 2.4, 2.6), (6.0, 12.6, -11.6, 1.8, 1.8, 1.8)):
            cb(hd, sx * x, y, z, w, h, d, 'horn', decals={f: [('rect', 0, k, 1, k + 0.12, '#b49c78') for k in (0.25, 0.65)] for f in ('north', 'south', 'up', 'east', 'west')})
    bd = m.bone('tc_bandana', [0, 19, -9], hd)
    cb(bd, 0, 19.6, -9.5, 8.4, 1.6, 7.4, 'tc')                                                             # team bandana over the brow
    cb(bd, 0, 18.4, -5.4, 2.4, 2.4, 1.6, 'tc')                                                             # knot
    cb(bd, 1.0, 15.6, -4.6, 1.6, 3.0, 0.6, 'tc', rot=('z', 22.5), rot_origin=[1.0, 18.4, -4.6])            # tails
    HS = 1.25                                                                        # chunkier head + horns
    for c in hd.cubes:
        for k in ('frm', 'to', 'rot_origin'):
            c[k] = [hd.origin[i] + (c[k][i] - hd.origin[i]) * HS for i in range(3)]
    for c in bd.cubes:
        for k in ('frm', 'to', 'rot_origin'):
            c[k] = [hd.origin[i] + (c[k][i] - hd.origin[i]) * HS for i in range(3)]
    bd.origin = [hd.origin[i] + (bd.origin[i] - hd.origin[i]) * HS for i in range(3)]
    # ---- rider
    body = m.bone('body', [0, 18, 1], ram)
    for sx in (1, -1):
        cb(body, sx * 4.0, 15.6, -0.2, 2.6, 2.4, 5.4, 'skin')                                              # thighs astride
        cb(body, sx * 6.0, 10.0, -2.0, 2.4, 6.0, 2.4, 'skin')                                              # shins
        cb(body, sx * 6.0, 9.2, -2.4, 2.8, 1.2, 3.4, 'sandal', decals={'north': [('rect', 0.3, 0, 0.7, 1, '#5a3a20')]})   # sandals
        cb(body, sx * 6.0, 12.6, -2.0, 2.6, 0.7, 2.6, 'sandal')                                            # sandal straps
    cb(body, 0, 16.0, 1.0, 7.4, 3.2, 5.0, 'dress_d')                                                       # skirt over the saddle
    cb(body, 0, 18.6, 1.0, 6.6, 5.4, 4.0, 'dress', decals={'north': [('rect', 0.15, 0.85, 0.85, 1.0, '#b45a2a')]})   # dress top
    ts = m.bone('tc_sash', [0, 18, 1], body)
    cb(ts, 0, 18.0, 1.0, 7.0, 1.4, 4.4, 'tc')                                                              # team sash
    cb(ts, -3.0, 15.4, 3.2, 2.0, 3.6, 1.2, 'tc')                                                           # rolled sash end at the back
    for k, y in enumerate((24.0, 24.9, 25.8)):
        cb(body, 0, y, 1.0, 5.4 - k * 0.6, 0.9, 4.6 - k * 0.6, 'gold')                                      # stacked gold neck rings
    hh = m.bone('head', [0, 26.4, 1], body)
    face = [('rect', 0.14, 0.50, 0.40, 0.64, '#ffffff'), ('rect', 0.60, 0.50, 0.86, 0.64, '#ffffff'),           # eye whites
            ('rect', 0.26, 0.50, 0.40, 0.64, '#3a2416'), ('rect', 0.60, 0.50, 0.74, 0.64, '#3a2416'),           # dark irises (looking ahead)
            ('rect', 0.30, 0.53, 0.36, 0.59, '#ffffff'), ('rect', 0.64, 0.53, 0.70, 0.59, '#ffffff'),           # catchlights
            ('rect', 0.12, 0.40, 0.42, 0.47, '#1e1a1a'), ('rect', 0.58, 0.40, 0.88, 0.47, '#1e1a1a'),           # thick determined brows
            ('rect', 0.12, 0.44, 0.20, 0.50, '#1e1a1a'), ('rect', 0.80, 0.44, 0.88, 0.50, '#1e1a1a'),
            ('rect', 0.44, 0.62, 0.56, 0.74, '#86532f'),                                                         # nose
            ('rect', 0.36, 0.82, 0.64, 0.86, '#5a2a1a'), ('rect', 0.60, 0.79, 0.66, 0.83, '#5a2a1a'),           # confident smirk
            ('rect', 0.12, 0.70, 0.18, 0.75, '#f4e2b8'), ('rect', 0.22, 0.72, 0.28, 0.77, '#f4e2b8'),           # cream face-paint dots
            ('rect', 0.72, 0.72, 0.78, 0.77, '#f4e2b8'), ('rect', 0.82, 0.70, 0.88, 0.75, '#f4e2b8')]
    cb(hh, 0, 26.4, 1.0, 6.4, 6.0, 6.2, 'skin', decals={'north': face, 'up': [('rect', 0, 0, 1, 1, '#1e1a1a')]}, dens=3)   # head (fine face texture)
    cb(hh, 0, 26.2, 0.8, 5.6, 0.6, 5.4, 'skin_d')                                                            # jaw shadow / chin
    cb(hh, 0, 31.3, 1.0, 6.8, 4.0, 6.9, 'hair', decals={f: [('rect', 0, 0.0, 1, 0.1, '#3a3232'), ('rect', 0, 0.9, 1, 1, '#141010')] for f in ('north', 'east', 'west', 'south')} | {'up': [('rect', 0.05, 0.05, 0.95, 0.95, '#2a2424')]})   # tall flat-top
    for sx in (1, -1):
        cb(hh, sx * 3.25, 29.4, 1.8, 0.3, 2.4, 4.6, 'hair', decals={sx > 0 and 'east' or 'west': [('rect', 0, 0, 1, 0.5, '#2a2424')]})   # short faded sides
        cb(hh, sx * 3.35, 28.2, 0.6, 0.5, 1.4, 1.0, 'skin_d')                                                # ears
        cb(hh, sx * 3.5, 26.8, 0.6, 0.4, 1.2, 1.2, 'gold')                                                   # hoop earrings
    cb(hh, 0, 28.6, 4.15, 6.4, 3.0, 0.3, 'hair')                                                            # back hairline
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.2
        a = m.bone('arm_' + side, [x, 24.0, 1.0], body)
        cb(a, x, 17.6, 1.0, 2.2, 6.4, 2.2, 'skin')                                                          # slim arm
        cb(a, x, 21.6, 1.0, 2.5, 1.0, 2.5, 'gold')                                                          # gold armband
        cb(a, x, 18.6, 1.0, 2.5, 0.9, 2.5, 'gold')                                                          # bracelet
    bo = m.bone('bola', [4.2, 17.8, 1.0], m.by_name('arm_r'))                                               # rope bola in the right hand
    cb(bo, 4.2, 16.6, 1.0, 1.2, 1.2, 1.2, 'rope', decals={f: [('rect', 0, 0.45, 1, 0.55, '#7a5a34')] for f in ('north', 'south', 'east', 'west')})   # knot in the fist
    for sx in (1, -1):
        cb(bo, 4.2 + sx * 2.9, 13.7 - 4.1, 1.0, 0.6, 8.2, 0.6, 'rope', decals={f: [('rect', 0, k, 1, k + 0.06, '#7a5a34') for k in (0.2, 0.45, 0.7)] for f in ('north', 'south', 'east', 'west')},
           rot=('z', sx * 45), rot_origin=[4.2 + sx * 2.9, 13.7, 1.0])                                     # rope strand
        X, Y = 4.2 + sx * 5.8, 7.4                                                                           # rounded white stone
        cb(bo, X, Y, 1.0, 2.6, 3.4, 2.6, 'stone', decals={f: [('rect', 0.15, 0.55, 0.45, 0.85, '#9aa0a6')] for f in ('north', 'south', 'east', 'west')})
        cb(bo, X, Y + 0.4, 1.0, 3.4, 2.6, 2.6, 'stone')
        cb(bo, X, Y + 0.4, 1.0, 2.6, 2.6, 3.4, 'stone')
        cb(bo, X - sx * 0.4, Y + 2.6, 1.0, 1.4, 0.8, 1.4, 'rope')                                            # rope wrapped on the stone
    DY = 3.0                                                                         # rider sits on the ram's back (~18)
    rider = set()
    def sub(bn):
        rider.add(bn.name); [sub(c) for c in bn.children]
    sub(m.by_name('body'))
    for bn in m.bones:
        if bn.name in rider:
            bn.origin[1] += DY
            for c in bn.cubes:
                c['frm'][1] += DY; c['to'][1] += DY; c['rot_origin'][1] += DY
    m.hitbox(1.5, 2.6)
    shade_pass(m, ('ram', 'horn', 'dress', 'skin'))
    UP = [180, 0, -10]                                                                # bola arm raised overhead
    hold = {'arm_r': {'rotation': loop([UP, [175, 0, -14]], 1.2)}, 'arm_l': {'rotation': loop([[-20, 0, -8], [-24, 0, -8]], 1.2)},
            'bola': {'rotation': [(0, [0, 0, 0]), (0.3, [0, -90, 0]), (0.6, [0, -180, 0]), (0.9, [0, -270, 0]), (1.2, [0, -360, 0])]},
            'pony_head': {'rotation': loop([[0, 0, 0], [5, 0, 0]], 1.2)}}
    m.anim('idle', 1.2, 'loop', hold)
    gal = {('leg_%d' % i): {'rotation': loop([[-30 if i in (0, 3) else 30, 0, 0], [30 if i in (0, 3) else -30, 0, 0]], 0.4)} for i in range(4)}
    gal['pony'] = {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.2)}
    gal['arm_r'] = {'rotation': [(0, UP), (0.4, UP)]}
    gal['arm_l'] = {'rotation': [(0, [-20, 0, -8]), (0.4, [-20, 0, -8])]}
    gal['bola'] = {'rotation': [(0, [0, 0, 0]), (0.1, [0, -90, 0]), (0.2, [0, -180, 0]), (0.3, [0, -270, 0]), (0.4, [0, -360, 0])]}
    m.anim('walk', 0.4, 'loop', gal)
    Z = [0.01, 0.01, 0.01]
    m.anim('attack', 0.8, 'once', {'pony_head': {'rotation': [(0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.32, [25, 0, 0]), (0.5, [10, 0, 0]), (0.8, [0, 0, 0])]},
                                   'pony': {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 1.5]), (0.32, [0, 0, -2.5]), (0.8, [0, 0, 0])]},
                                   'arm_r': {'rotation': [(0, UP), (0.8, UP)]},
                                   'bola': {'rotation': [(0, [0, 0, 0]), (0.2, [0, -180, 0]), (0.4, [0, -360, 0]), (0.6, [0, -540, 0]), (0.8, [0, -720, 0])]}})
    m.anim('throw', 0.6, 'once', {'arm_r': {'rotation': [(0, UP), (0.15, [190, 0, -10]), (0.28, [-70, 0, 0]), (0.45, [-50, 0, 0]), (0.6, UP)]},
                                  'bola': {'scale': [(0, [1, 1, 1]), (0.27, [1, 1, 1]), (0.28, Z), (0.55, Z), (0.6, [1, 1, 1])]},
                                  'body': {'rotation': [(0, [0, 0, 0]), (0.15, [-6, 10, 0]), (0.3, [8, -10, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m, hit_bone='pony')
    return m


def royal_giant():
    """Royal Giant: giant build, golden hair + huge golden beard/moustache/bushy brows, tiny gold crown, team tunic with red
    trim over a chainmail shirt (scale sleeves + skirt), red belt with a big gold buckle, bare legs/feet; hand cannon with
    gold bands held at the hip in the right hand, cannonball in the left fist."""
    m = new_model('clash_royal_giant')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'hair': ('#f0c030', 'hair'), 'hair_d': ('#d09a1c', 'hair'),
             'tunic': ('#efefef', 'cloth'), 'trim': ('#c83a30', 'cloth'), 'mail': ('#8a929c', 'soft'), 'mail_d': ('#646c76', 'soft'),
             'belt': ('#c83a30', 'leather'), 'gold': ('#e8b030', 'metal'), 'gold_d': ('#b88418', 'metal'), 'lace': ('#6a4a30', 'rope'),
             'iron': ('#4a5058', 'soft'), 'iron_d': ('#2c3036', 'soft'), 'void': ('#121418', 'plain'), 'eyew': ('#ffffff', 'plain'),
             'flash': ('#ffd860', 'glow')})
    D = '#c88a64'
    MAIL = {f: [('fn', _scales)] for f in ('north', 'south', 'east', 'west')}
    r = Rig(m, 1.75); B = r.box
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = r.bone('leg_' + side, [x, 11, 0], root)
        B(lg, x, 1.2, 0, 3.8, 9.8, 3.8, 'skin')                                                     # bare legs
        B(lg, x, 0, -0.6, 4.4, 1.4, 5.4, 'skin_d', decals={'north': pix(["k.k.k.k", "......."], {'k': D})})   # bare feet + toes
    body = r.bone('body', [0, 11, 0], root)
    B(body, 0, 8.6, 0, 10.0, 5.0, 5.8, 'mail', decals=MAIL)                                       # chainmail skirt
    B(body, 0, 8.4, 0, 10.2, 0.6, 6.0, 'mail_d')                                                  # skirt hem
    B(body, 0, 13.6, 0, 9.4, 11.0, 5.2, 'mail', decals=MAIL)                                      # mail shirt (shows at neck)
    tc = r.bone('tc_tunic', [0, 14, 0], body)
    B(tc, 0, 13.4, 0, 9.8, 10.0, 5.6, 'tunic', decals={'south': [('shade', 0, 0.8, 1, 1, 0.85)]})  # team tunic (sleeveless)
    for sx in (1, -1):
        B(body, sx * 4.75, 18.0, 0, 0.4, 5.6, 5.0, 'trim')                                         # red armhole trim
        B(body, sx * 1.9, 23.0, -2.85, 2.0, 0.6, 0.2, 'trim')                                      # collar trim
    B(body, 0, 21.6, -2.85, 1.8, 2.2, 0.2, 'mail', decals={'north': pix(["k...k", ".k.k.", "..k..", ".k.k."], {'k': '#6a4a30'})})   # laced neck slit
    B(body, 0, 13.2, 0, 10.2, 1.8, 6.0, 'belt')                                                   # red belt
    B(body, 0, 12.8, -3.05, 3.0, 2.6, 0.3, 'gold', decals={'north': [('rect', 0.22, 0.22, 0.78, 0.78, '#9a6a10'), ('rect', 0.3, 0.3, 0.7, 0.7, '#c83a30')]})   # big gold buckle
    hd = r.bone('head', [0, 24.6, -0.4], body)
    B(hd, 0, 24.6, -0.4, 7.4, 7.4, 7.0, 'skin', decals={'up': [('rect', 0.25, 0.25, 0.75, 0.75, '#f8c8a0')]})   # head
    B(hd, 0, 31.2, 0.4, 6.6, 1.0, 4.6, 'hair', decals={'up': [('rect', 0.0, 0.0, 1.0, 0.3, '#d09a1c')]})   # golden hair on top
    B(hd, 0, 25.0, 3.1, 7.6, 3.4, 0.6, 'hair')                                                    # back hair (lower ring)
    for sx in (1, -1):
        B(hd, sx * 3.85, 26.6, 0.8, 0.5, 4.6, 4.4, 'hair')                                          # side hair
        B(hd, sx * 3.95, 26.8, -0.6, 0.4, 1.6, 1.2, 'skin')                                         # ears
        B(hd, sx * 1.75, 27.4, -4.0, 1.8, 1.1, 0.2, 'eyew', decals={'north': [('rect', 0.5 if sx > 0 else 0.0, 0, 1.0 if sx > 0 else 0.5, 1, '#3a6aa8')]})   # eyes
        B(hd, sx * 1.9, 28.5, -4.2, 3.0, 1.0, 0.7, 'hair_d')                                        # bushy golden brows
        B(hd, sx * 1.5, 25.0, -4.35, 2.8, 0.9, 0.6, 'hair_d')                                       # handlebar moustache
        B(hd, sx * 3.0, 25.4, -4.3, 0.9, 0.7, 0.5, 'hair_d')                                        # moustache tips
    B(hd, 0, 25.8, -4.4, 1.8, 1.8, 1.0, 'skin_d')                                                 # big nose
    B(hd, 0, 21.4, -2.4, 8.0, 3.8, 3.6, 'hair', decals={'north': [('rect', 0.3, 0.75, 0.7, 1.0, '#c86a5a')]})   # huge golden beard (mouth)
    B(hd, 0, 20.4, -2.8, 6.0, 1.4, 2.8, 'hair_d')                                                 # beard tip
    for sx in (1, -1):
        B(hd, sx * 3.7, 23.0, -1.4, 0.6, 3.6, 3.6, 'hair')                                          # sideburns into the beard
    cr = r.bone('crown', [0, 32.2, 0.6], hd)
    B(cr, 0, 32.2, 0.6, 3.0, 0.9, 3.0, 'gold')                                                    # tiny crown band
    for (dx, dz) in ((-1.2, -1.2), (1.2, -1.2), (-1.2, 2.4), (1.2, 2.4), (0, -1.2)):
        B(cr, dx, 33.1, dz * 0.5 + 0.6, 0.6, 0.8, 0.6, 'gold_d')                                    # crown points
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.6
        a = r.bone('arm_' + side, [x, 23.0, 0], body)
        B(a, x, 18.4, 0, 4.6, 5.8, 4.6, 'mail', decals=MAIL)                                       # chainmail short sleeve
        B(a, x, 18.2, 0, 4.8, 0.6, 4.8, 'mail_d')
        B(a, x, 12.6, 0, 3.8, 6.0, 3.8, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.7, D)]})
        B(a, x, 9.6, -0.2, 4.6, 3.4, 4.6, 'skin_d', decals={'north': pix(["k.k.k", ".....", "....."], {'k': D})})   # big fist
    cn = r.bone('cannon', [9.0, 26.8, 0.0], body)                                                 # cannon resting on the right shoulder (on the body, so it never drifts)
    B(cn, 9.0, 24.4, -1.8, 5.4, 5.4, 12.0, 'iron', decals={f: [('fn', _soft_metal(1.2, 0.75))] for f in ('north', 'south', 'east', 'west', 'up')})   # big barrel
    B(cn, 9.0, 23.9, -7.4, 6.4, 6.4, 2.4, 'iron')                                                 # muzzle lip
    B(cn, 9.0, 24.9, -8.65, 4.4, 4.4, 0.2, 'void')                                                # bore
    B(cn, 9.0, 24.7, 5.4, 4.8, 4.8, 2.4, 'iron_d')                                                 # breech
    B(cn, 9.0, 26, 7.2, 2.2, 2.2, 1.6, 'iron_d')                                                # cascabel knob
    for z in (-9.2, -7.0):
        B(cn, 9.0, 24.1, z + 5.0, 6.0, 6.0, 1.4, 'gold', decals={f: [('rect', 0, 0.0, 1, 0.25, '#f8d060')] for f in ('north', 'south', 'east', 'west')})   # gold bands
    fl = r.bone('muzzle', [9.0, 27.1, -8.8], cn)
    B(fl, 9.0, 25.5, -10.2, 3.2, 3.2, 1.6, 'flash')                                               # muzzle flash (hidden; shows on attack)
    bl = r.bone('ball', [-6.6, 10.6, -1.6], m.by_name('arm_l'))
    B(bl, -6.6, 10.4, -3.0, 3.0, 3.0, 3.0, 'iron_d', decals={'north': [('rect', 0.15, 0.6, 0.45, 0.85, '#6a7078')]})   # cannonball in the fist
    WX, LS = 1.25, 1.6
    for bn in m.bones:
        if bn.name == 'root': continue
        leg = bn.name.startswith('leg_')
        for c in bn.cubes:
            if not leg and bn.name not in ('head', 'crown'):
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][0] *= WX
            if leg:
                if c['to'][1] > 3: c['to'][1] -= LS
                if c['frm'][1] > 3: c['frm'][1] -= LS
            else:
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][1] -= LS * 1.0
        if not leg and bn.name not in ('head', 'crown'): bn.origin[0] *= WX
        bn.origin[1] -= LS if bn.name != 'root' else 0
    m.hitbox(2.2, 3.6)
    shade_pass(m, ('skin', 'tunic'))
    Z = [0.01, 0.01, 0.01]
    ARMP = [0, 0, 110]                                                                # right arm stretched out sideways under the shouldered cannon (holds still)
    SA, RC = ARMP, -10                                # cannon shouldered beside the head (user's pick)
    m.anim('idle', 2.4, 'loop', {'arm_r': {'rotation': [(0, SA), (1.2, ARMP), (2.4, SA)]},
                                 'arm_l': {'rotation': [(0, [-10, 0, -4]), (1.2, [-13, 0, -6]), (2.4, [-10, 0, -4])]},
                                 'body': {'position': [(0, [0, 0, 0]), (1.2, [0, -0.5, 0]), (2.4, [0, 0, 0])]},
                                 'head': {'rotation': [(0, [0, 4, 0]), (1.2, [2, 0, 0]), (2.4, [0, 4, 0])]},
                                 'muzzle': {'scale': [(0, Z), (2.4, Z)]}})
    m.anim('walk', 1.4, 'loop', {'leg_r': {'rotation': [(0, [22, 0, 0]), (0.7, [-22, 0, 0]), (1.4, [22, 0, 0])]},
                                 'leg_l': {'rotation': [(0, [-22, 0, 0]), (0.7, [22, 0, 0]), (1.4, [-22, 0, 0])]},
                                 'arm_r': {'rotation': [(0, SA), (0.7, ARMP), (1.4, SA)]},
                                 'arm_l': {'rotation': [(0, [-22, 0, -4]), (0.7, [8, 0, -4]), (1.4, [-22, 0, -4])]},
                                 'body': {'position': [(0, [0, 0, 0]), (0.35, [0, 0.8, 0]), (0.7, [0, 0, 0]), (1.05, [0, 0.8, 0]), (1.4, [0, 0, 0])]},
                                 'muzzle': {'scale': [(0, Z), (1.4, Z)]}})
    m.anim('attack', 1.0, 'once', {'arm_r': {'rotation': [(0, SA), (0.3, SA), (0.36, ARMP), (0.6, ARMP), (1.0, SA)]},
                                   'cannon': {'rotation': [(0, [0, 0, 0]), (0.3, [0, 0, 0]), (0.36, [RC, 0, 0]), (0.6, [RC * 0.4, 0, 0]), (1.0, [0, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.3, [-3, 0, 0]), (0.36, [7, 0, 0]), (0.6, [2, 0, 0]), (1.0, [0, 0, 0])]},
                                   'arm_l': {'rotation': [(0, [-10, 0, -4]), (1.0, [-10, 0, -4])]},
                                   'muzzle': {'scale': [(0, Z), (0.33, Z), (0.35, [1.6, 1.6, 1.6]), (0.44, [1.1, 1.1, 1.1]), (0.5, Z), (1.0, Z)]}})
    common_tail(m)
    return m


def guard_parts():
    """Guard parts grafted onto the original HQ skeleton (mk_guard.py): snug dark-steel sallet helm hugging the skull with a big
    open face (skull fully visible), thick face rim, small team crest on top; steel-framed wooden kite shield; spear with gold collar."""
    m = new_model('clash_guard_parts')
    m.mats_({'steel': ('#5c646c', 'soft'), 'steel_l': ('#7e8890', 'soft'), 'steel_d': ('#3e454c', 'soft'), 'rivet': ('#aab2ba', 'soft'),
             'tc': ('#efefef', 'cloth'), 'wood': ('#a8703a', 'wood'), 'wood_d': ('#7e5028', 'wood'), 'iron': ('#4a5158', 'metal'),
             'blade': ('#c8ced6', 'metal'), 'grip': ('#6a3e22', 'wood'), 'gold': ('#e0a830', 'metal')})
    MET = lambda: {f: [('fn', _soft_metal(1.15, 0.85))] for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    root = m.bone('root', [0, 0, 0])
    hd = m.bone('head', [0, 17.16, 0], root)
    hm = m.bone('helmet', [0, 17.16, 0], hd)
    Z0, Z1 = -3.95, 3.6                                                          # skull: x +-3.35, y 15.97..23.8, z -3.61..3.19
    cb(hm, 0, 23.6, (Z0 + Z1) / 2, 7.8, 1.6, Z1 - Z0, 'steel', decals=MET())                               # rounded crown
    cb(hm, 0, 25.2, (Z0 + Z1) / 2 + 0.3, 6.2, 0.6, Z1 - Z0 - 1.6, 'steel_l')                              # crown dome
    for sx in (1, -1):
        cb(hm, sx * 3.65, 17.6, (Z0 + Z1) / 2 + 0.4, 0.6, 6.4, Z1 - Z0 - 0.8, 'steel', decals=MET())      # cheek plates
        cb(hm, sx * 3.35, 17.4, Z0 + 0.35, 1.2, 6.6, 0.7, 'steel_d')                                       # thick face rim (sides)
        cb(hm, sx * 3.9, 17.0, Z1 - 1.6, 0.6, 1.0, 3.2, 'steel_d')                                         # flared lower edge
    cb(hm, 0, 16.6, Z1 - 0.2, 7.8, 7.4, 0.6, 'steel', decals=MET())                                        # back plate (neck guard)
    cb(hm, 0, 16.2, Z1 + 0.2, 8.0, 0.8, 0.8, 'steel_d')                                                    # neck flare
    cb(hm, 0, 23.2, Z0 + 0.35, 7.8, 1.2, 0.7, 'steel_d')                                                   # brow rim
    for x in (-2.4, 0.0, 2.4):
        cb(hm, x, 23.5, Z0 - 0.05, 0.5, 0.5, 0.1, 'rivet')                                                 # rim rivets
    pl = m.bone('tc_plume', [0, 25.8, 0.2], hm)
    for (z, h) in ((-1.6, 1.6), (-0.4, 2.2), (0.8, 2.0), (2.0, 1.4)):
        cb(pl, 0, 25.8, z, 1.0, h, 1.2, 'tc')                                                               # small team crest
    sh = m.bone('shield', [4.5, 9.8, 0], root)
    SZ = -3.0                                                                    # shield board in front of the left arm
    rows = [(17.6, 7.6), (16.0, 7.6), (14.0, 7.6), (12.0, 7.6), (10.0, 7.6), (8.0, 7.2), (6.6, 6.0), (5.4, 4.6), (4.4, 3.0), (3.6, 1.6)]
    for i in range(len(rows) - 1):
        y1, w = rows[i]; y0 = rows[i + 1][0]
        cb(sh, 5.6, y0, SZ, w, y1 - y0 + 0.01, 0.8, 'wood', decals={'north': [('rect', 0.32, 0, 0.35, 1, '#7e5028'), ('rect', 0.65, 0, 0.68, 1, '#7e5028')]})   # vertical planks
        cb(sh, 5.6, y0, SZ + 0.1, w + 0.6, y1 - y0 + 0.01, 0.6, 'iron')                                   # iron rim
    cb(sh, 5.6, 17.4, SZ + 0.05, 8.2, 0.6, 0.7, 'iron')                                                   # rim top
    cb(sh, 5.6, 9.6, SZ - 0.2, 7.4, 1.2, 0.3, 'iron')                                                     # crest bar
    cb(sh, 5.6, 10.8, SZ - 0.2, 3.6, 1.6, 0.3, 'steel_l')                                                 # tower crest
    for x in (-1.2, 0.0, 1.2):
        cb(sh, 5.6 + x, 12.4, SZ - 0.2, 0.8, 1.0, 0.3, 'steel_l')                                         # battlements
    cb(sh, 5.6, 14.6, SZ - 0.15, 7.6, 0.5, 0.2, 'iron')                                                   # upper band
    sp = m.bone('spear', [-4.5, 9.8, 0], root)
    cb(sp, -4.5, 0.0, -0.9, 0.8, 30.0, 0.8, 'grip', decals={'north': [('lerp', '#4a2a16', 0.6, 1.0, 'y')]})   # long shaft
    cb(sp, -4.5, 29.6, -0.9, 1.4, 1.2, 1.4, 'gold')                                                       # collar
    for (w, h, y) in ((1.6, 1.4, 30.6), (2.8, 2.0, 32.0), (2.4, 2.0, 34.0), (1.4, 1.8, 36.0), (0.6, 1.2, 37.8)):
        cb(sp, -4.5, y, -0.9, w, h, 0.6, 'blade', decals={'north': [('rect', 0.42, 0, 0.58, 1, '#9aa2ac')]})   # leaf spear head
    m.hitbox(0.8, 1.6)
    return m


def prince():
    """Prince (same pony as the Dark Prince): gold armour, open helm with a hinged barred visor (raised; lowered on charge), moustache + goatee, team-striped lance with pennant. Base:: bucket helm with rivets + eye slit, team plume, dark steel cuirass, chainmail,
    spiked block mace, wooden crown shield with steel rim, riding a brown pony with blond mane, bridle + team saddle cloth"""
    m = new_model('clash_prince')
    m.mats_({'steel': ('#d0a040', 'metal'), 'steel_l': ('#ecc860', 'metal'), 'mail': ('#b8c0c8', 'metal'), 'stripe': ('#f4f4f4', 'cloth'), 'beard': ('#4a2a1a', 'hair'), 'skin': ('#e8a878', 'skin'),
             'pony': ('#7a4a32', 'fur'), 'pony_d': ('#5a3424', 'fur'), 'muzzle': ('#d8906a', 'skin'), 'mane': ('#e8cc6a', 'hair'),
             'strap': ('#8a3a2a', 'leather'), 'tc': ('#efefef', 'cloth'), 'wood': ('#7a4a2a', 'wood', {'planks': True}),
             'gold': ('#e8b830', 'metal'), 'grip': ('#5a3a22', 'leather'), 'hoof': ('#3a2a20', 'plain'), 'eye': ('#ffffff', 'plain')})
    mail = [('px', i / 6, j / 6, '#5a626a') for i in range(0, 6, 2) for j in range(0, 6, 2)]
    root = m.bone('root', [0, 0, 0])
    # ---- pony: vanilla Minecraft horse proportions, yellow mane/tail, forelock over the face, full saddle + bridle
    pony = m.bone('pony', [0, 11, 0], root)
    cb(pony, 0, 11.0, 1.0, 10.0, 10.0, 22.0, 'pony')                                  # body 10x10x22
    for i, (lx, lz) in enumerate(((3.0, -7.0), (-3.0, -7.0), (3.0, 10.0), (-3.0, 10.0))):
        lg = m.bone('leg_%d' % i, [lx, 11, lz], pony)
        cb(lg, lx, 3.0, lz, 4.0, 8.0, 4.0, 'pony')                                        # leg 4x11x4
        cb(lg, lx, 0.0, lz, 4.0, 3.0, 4.0, 'pony_d', decals={f: [('rect', 0, 0.75, 1, 1, '#2a1a12')] for f in ('north', 'south', 'east', 'west')})   # lower leg + hoof
    nk = m.bone('pony_head', [0, 18, -8], pony)
    ro = dict(rot=('x', -22.5), rot_origin=[0, 18, -8])
    cb(nk, 0, 17.0, -10.5, 4.0, 12.0, 7.0, 'pony', **ro)                                # neck 4x12x7
    cb(nk, 0, 26.0, -14.0, 6.0, 5.0, 7.0, 'pony', **ro)                                 # head 6x5x7
    cb(nk, 0, 25.0, -19.5, 4.0, 5.0, 5.0, 'pony',                                       # muzzle 4x5x5
       decals={'north': pix(["....", "....", "k..k", "....", ".kk."], {'k': '#3a2018'})}, **ro)
    for sx in (1, -1):
        cb(nk, sx * 2.0, 30.6, -12.0, 2.0, 3.0, 1.0, 'pony', **ro)                         # ears
        cb(nk, sx * 3.05, 28.6, -15.4, 0.2, 1.0, 1.0, 'eye', decals={'east': pix(["k"], {'k': '#1a1010'}), 'west': pix(["k"], {'k': '#1a1010'})}, **ro)
    cb(nk, 0, 18.0, -6.8, 2.0, 12.6, 1.8, 'mane', **ro)                                  # yellow mane down the neck
    cb(nk, 0, 30.6, -11.6, 2.4, 1.0, 3.0, 'mane', **ro)
    cb(nk, 0, 30.6, -15.0, 6.4, 1.4, 4.4, 'mane', **ro)                                  # thick tuft on top of the head
    for dx, h in ((-2.4, 2.6), (-1.2, 3.6), (0.0, 4.2), (1.2, 3.4), (2.4, 2.4)):          # fringe hanging over the forehead
        cb(nk, dx, 31.4 - h, -17.9, 1.3, h + 0.6, 1.0, 'mane', decals={'north': [('rect', 0.4, 0, 0.6, 1, '#c8a850')]}, **ro)
    tcr = m.bone('tc_reins', [0, 18, -8], nk)                                            # bridle (team)
    cb(tcr, 0, 27.0, -22.15, 4.4, 1.0, 0.3, 'tc', **ro)                                   # noseband
    for sx in (1, -1):
        cb(tcr, sx * 2.15, 25.4, -19.5, 0.3, 1.0, 5.2, 'tc', **ro)
        cb(tcr, sx * 3.15, 26.0, -14.5, 0.3, 5.0, 1.0, 'tc', **ro)                          # cheek straps
        cb(tcr, sx * 2.3, 25.6, -20.6, 0.5, 1.6, 1.6, 'steel_l', **ro)                      # bit rings
        cb(tcr, sx * 3.2, 20.0, -6.0, 0.3, 0.8, 9.0, 'tc')                                  # reins to the rider
    tl = m.bone('tail', [0, 20, 12], pony)
    cb(tl, 0, 6.0, 13.6, 3.0, 14.0, 4.0, 'mane', rot=('x', -22.5), rot_origin=[0, 20, 12],
       decals={'south': [('rect', 0.45, 0, 0.55, 1, '#c8a850')]})                       # yellow tail
    sad = m.bone('tc_saddle', [0, 21, 1], pony)
    trim = [('rect', 0, 0.85, 1, 1, '#c8c8c8')]
    cb(sad, 0, 21.0, 1.0, 10.8, 0.4, 10.0, 'tc')                                         # saddle cloth
    for sx in (1, -1):
        cb(sad, sx * 5.2, 15.0, 1.0, 0.4, 6.0, 10.0, 'tc', decals={'east': trim, 'west': trim})
    cb(pony, 0, 21.4, 1.0, 8.0, 1.0, 8.0, 'strap')                                      # filled leather saddle seat
    cb(pony, 0, 21.4, -3.2, 6.0, 2.4, 1.4, 'strap'); cb(pony, 0, 21.4, 5.2, 7.0, 2.2, 1.4, 'strap')   # pommel + cantle
    for sx in (1, -1):
        cb(pony, sx * 5.15, 11.0, 0.0, 0.3, 10.6, 1.4, 'strap')                            # girth
    # ---- rider (HQ)
    body = m.bone('body', [0, 16, 1], pony)
    scale = [('px', i / 8, j / 8, '#8a929a') for i in range(0, 8, 2) for j in range(1, 8, 2)] + [('px', i / 8, j / 8, '#dfe4ea') for i in range(1, 8, 2) for j in range(0, 8, 2)]
    for sx in (1, -1):
        cb(body, sx * 4.4, 14.2, -0.6, 3.2, 3.0, 6.4, 'mail', decals={'east': scale, 'west': scale, 'up': scale, 'north': scale})   # thighs astride
        cb(body, sx * 6.0, 8.0, -2.4, 2.8, 6.6, 3.0, 'mail', decals={'east': scale, 'west': scale, 'north': scale, 'south': scale})   # shins down the flanks
        cb(body, sx * 6.1, 6.2, -2.8, 3.2, 2.0, 4.2, 'grip')                                 # boots
        cb(body, sx * 6.1, 5.6, -2.8, 3.4, 0.6, 3.0, 'steel_l')                              # stirrup
    cb(body, 0, 15.2, 1.0, 7.2, 3.0, 4.6, 'mail', decals={'north': scale, 'south': scale})   # mail skirt
    cb(body, 0, 17.4, 1.0, 7.8, 1.4, 5.0, 'grip')                                        # belt
    cb(body, 0, 17.2, -1.6, 2.0, 1.8, 0.4, 'gold', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#8a6a20')]})   # buckle
    cb(body, 0, 18.8, 1.0, 7.6, 5.8, 4.6, 'steel', decals={'north': [('rect', 0.47, 0, 0.53, 1, '#8a929a'), ('rect', 0.1, 0.0, 0.9, 0.12, '#8a929a')]})   # breastplate
    cb(body, 0, 19.2, -1.4, 5.0, 4.0, 0.6, 'steel_l')                                     # chest ridge plate
    for sx in (1, -1):
        cb(body, sx * 4.5, 22.0, 1.0, 3.4, 2.8, 5.4, 'steel')                              # big rounded pauldrons
        cb(body, sx * 4.6, 24.6, 1.0, 2.6, 0.8, 4.4, 'steel_l')
    hd = m.bone('head', [0, 24.4, 1], body)
    face = pix(["........", "........", "........", ".wb..bw.", "........", "........", "........", "........"], {'w': '#ffffff', 'b': '#3a2a1a'})
    cb(hd, 0, 24.4, 1.0, 6.4, 7.0, 6.4, 'skin', decals={'north': face}, dens=2)                             # face
    cb(hd, 0, 27.4, -2.4, 1.4, 1.6, 1.0, 'skin', decals={'north': [('shade', 0, 0, 1, 1, 0.9)]})          # nose
    for sx in (1, -1):
        cb(hd, sx * 1.3, 26.6, -2.45, 2.4, 0.7, 0.4, 'beard', rot=('z', -sx * 22.5), rot_origin=[sx * 0.4, 27.0, -2.45])   # curled moustache
        cb(hd, sx * 1.6, 29.0, -2.35, 2.0, 0.5, 0.2, 'beard')                                                # brows
    cb(hd, 0, 24.0, -2.4, 1.2, 1.8, 0.6, 'beard')                                                          # goatee
    HM = {g: [('shade', 0, 0, 1, 0.15, 1.2), ('shade', 0, 0.85, 1, 1, 0.8)] for g in ('north', 'south', 'east', 'west')}
    cb(hd, 0, 30.0, 1.0, 7.8, 3.6, 7.8, 'steel', decals=HM)                                                  # helm crown
    cb(hd, 0, 33.6, 1.0, 6.2, 0.8, 6.2, 'steel_l')
    cb(hd, 0, 23.6, 4.4, 7.8, 6.4, 0.8, 'steel', decals=HM)                                                  # back
    for sx in (1, -1):
        cb(hd, sx * 3.7, 23.6, 1.6, 0.6, 6.4, 6.6, 'steel', decals=HM)                                       # cheek guards
        cb(hd, sx * 4.1, 29.0, -0.8, 0.6, 1.6, 1.6, 'steel_l')                                               # visor hinge
    cb(hd, 0, 33.4, -2.0, 1.0, 1.0, 3.0, 'steel_l')                                                          # crest
    vs = m.bone('visor', [0, 29.8, -0.8], hd)                                                             # hinged barred visor
    cb(vs, 0, 26.0, -3.2, 7.6, 4.4, 0.6, 'steel', decals={'north': [('rect', x0, 0.15, x0 + 0.08, 0.85, '#1a1612') for x0 in (0.16, 0.34, 0.58, 0.76)] + [('shade', 0, 0, 1, 0.15, 1.2)]})
    for sx in (1, -1):
        cb(vs, sx * 3.7, 26.4, -1.8, 0.6, 3.4, 2.6, 'steel')                                                 # visor side arms to the hinge
    pl = m.bone('tc_plume', [0, 33.8, 1.0], hd)
    cb(pl, 0, 33.8, 1.2, 1.4, 1.4, 1.4, 'steel_l')
    for k, (y, z, h, d) in enumerate(((35.0, 1.4, 3.0, 2.0), (37.4, 2.6, 2.4, 2.6), (38.6, 4.8, 2.0, 2.6), (38.0, 7.0, 1.8, 2.4), (36.6, 8.6, 1.8, 1.8), (35.6, 9.8, 1.4, 1.4))):
        cb(pl, 0, y, z, 1.8 - k * 0.15, h, d, 'tc', decals={'east': [('rect', 0, 0.8, 1, 1, '#c8c8c8')], 'west': [('rect', 0, 0.8, 1, 1, '#c8c8c8')]})   # thick curling plume
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.4
        a = m.bone('arm_' + side, [x, 23.0, 1.0], body)
        cb(a, x, 19.6, 1.0, 2.6, 3.6, 2.8, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # mail sleeve
        cb(a, x, 16.6, 1.0, 2.8, 3.2, 3.0, 'steel')                                          # bracer
        cb(a, x, 16.0, 1.0, 3.2, 0.8, 3.4, 'steel_l')
        cb(a, x, 13.6, 0.8, 3.0, 2.8, 3.2, 'steel', decals={'north': pix(["k.k.k", "....."], {'k': '#3a4048'})})   # gauntlet fist
        cb(a, x - sx * 1.6, 14.6, -0.4, 0.8, 1.6, 1.0, 'steel_l')                           # thumb
    ln = m.bone('lance', [5.4, 14.8, 1.0], m.by_name('arm_r'))                              # long lance couched forward
    tl = m.bone('tc_lance', [5.4, 14.8, 1.0], ln)
    cb(ln, 5.4, 14.3, 1.2, 1.6, 1.6, 6.0, 'grip')                                                          # grip + butt (through the fist, touching the guard)
    cb(ln, 5.4, 14.0, 4.6, 2.0, 2.0, 1.0, 'mail')                                                          # butt cap
    cb(ln, 5.4, 11.9, -2.4, 6.4, 6.4, 1.4, 'mail')                                                         # round vamplate guard
    cb(ln, 5.4, 12.6, -3.4, 5.0, 5.0, 1.0, 'mail')
    for k in range(9):
        w = 3.4 - k * 0.2
        cb(tl if k % 2 == 0 else ln, 5.4, 15.1 - w / 2, -3.9 - 1.8 - k * 3.6, w, w, 3.6, 'tc' if k % 2 == 0 else 'stripe')   # team-striped shaft, flush segments
    z = -3.9 - 9 * 3.6
    for (w, d) in ((3.6, 2.4), (2.6, 2.4), (1.6, 2.4), (0.7, 1.8)):
        cb(ln, 5.4, 15.1 - w / 2, z - d / 2, w, w, d, 'mail'); z -= d                                       # steel cone tip, flush
    pn = m.bone('tc_pennant', [5.4, 16.8, -26.0], ln)
    for (y, h, zz) in ((16.6, 5.0, -26.0), (17.8, 3.6, -23.4), (18.6, 2.2, -21.2)):
        cb(pn, 5.4, y, zz, 0.3, h, 2.6, 'tc')                                                               # pennant flag
    DY = 7.2                                                                         # rider sits on the saddle (seat ~22.4)
    rider = set()
    def sub(bn):
        rider.add(bn.name); [sub(c) for c in bn.children]
    sub(m.by_name('body'))
    for bn in m.bones:
        if bn.name in rider:
            bn.origin[1] += DY
            for c in bn.cubes:
                c['frm'][1] += DY; c['to'][1] += DY; c['rot_origin'][1] += DY
    m.hitbox(1.5, 2.6)
    shade_pass(m, ('pony', 'steel', 'wood', 'mane'))
    VUP = [-100, 0, 0]                                                                       # visor raised; [0,0,0] = lowered
    hold = {'arm_r': {'rotation': loop([[-20, 0, 0], [-23, 0, 0]], 2.0)}, 'arm_l': {'rotation': loop([[-10, 0, 0], [-12, 0, 0]], 2.0)},
            'pony_head': {'rotation': loop([[0, 0, 0], [6, 0, 0]], 2.0)}, 'visor': {'rotation': loop([VUP, VUP], 2.0)}}
    m.anim('idle', 2.0, 'loop', hold)
    gal = {('leg_%d' % i): {'rotation': loop([[-35 if i in (0, 3) else 35, 0, 0], [35 if i in (0, 3) else -35, 0, 0]], 0.5)} for i in range(4)}
    gal['pony'] = {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.25)}
    gal.update({k: {'rotation': loop([v['rotation'][0][1], v['rotation'][0][1]], 0.5)} for k, v in hold.items() if k.startswith('arm') or k == 'visor'})
    m.anim('walk', 0.5, 'loop', gal)
    ch = {('leg_%d' % i): {'rotation': loop([[-50 if i in (0, 3) else 50, 0, 0], [50 if i in (0, 3) else -50, 0, 0]], 0.3)} for i in range(4)}
    ch['pony'] = {'position': loop([[0, 0, 0], [0, 1.6, 0]], 0.15), 'rotation': loop([[4, 0, 0], [4, 0, 0]], 0.3)}
    ch['visor'] = {'rotation': loop([[0, 0, 0], [0, 0, 0]], 0.3)}                                 # visor slammed down for the charge
    ch['arm_r'] = {'rotation': loop([[-8, 0, 0], [-8, 0, 0]], 0.3)}                               # lance levelled
    ch['body'] = {'rotation': loop([[10, 0, 0], [10, 0, 0]], 0.3)}
    m.anim('charge', 0.3, 'loop', ch)
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 0]), (0.15, [-10, 0, 0]), (0.25, [-14, 0, 0]), (0.6, [-20, 0, 0])],
                                             'position': [(0, [0, 0, 0]), (0.15, [0, 0, 3]), (0.25, [0, 0, -5]), (0.6, [0, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.15, [-6, 0, 0]), (0.25, [10, 0, 0]), (0.6, [0, 0, 0])]},
                                   'visor': {'rotation': [(0, VUP), (0.6, VUP)]}})
    common_tail(m, hit_bone='pony')
    return m



def dark_prince():
    """HQ vanilla-like Dark Prince: bucket helm with rivets + eye slit, team plume, dark steel cuirass, chainmail,
    spiked block mace, wooden crown shield with steel rim, riding a brown pony with blond mane, bridle + team saddle cloth"""
    m = new_model('clash_dark_prince')
    m.mats_({'steel': ('#34383e', 'metal'), 'steel_l': ('#5a6068', 'metal'), 'mail': ('#464c54', 'metal'), 'skin': ('#e8a878', 'skin'),
             'pony': ('#7a4a32', 'fur'), 'pony_d': ('#5a3424', 'fur'), 'muzzle': ('#d8906a', 'skin'), 'mane': ('#e8cc6a', 'hair'),
             'strap': ('#8a3a2a', 'leather'), 'tc': ('#efefef', 'cloth'), 'wood': ('#7a4a2a', 'wood', {'planks': True}),
             'gold': ('#e8b830', 'metal'), 'grip': ('#5a3a22', 'leather'), 'hoof': ('#3a2a20', 'plain'), 'eye': ('#ffffff', 'plain')})
    mail = [('px', i / 6, j / 6, '#5a626a') for i in range(0, 6, 2) for j in range(0, 6, 2)]
    root = m.bone('root', [0, 0, 0])
    # ---- pony: vanilla Minecraft horse proportions, yellow mane/tail, forelock over the face, full saddle + bridle
    pony = m.bone('pony', [0, 11, 0], root)
    cb(pony, 0, 11.0, 1.0, 10.0, 10.0, 22.0, 'pony')                                  # body 10x10x22
    for i, (lx, lz) in enumerate(((3.0, -7.0), (-3.0, -7.0), (3.0, 10.0), (-3.0, 10.0))):
        lg = m.bone('leg_%d' % i, [lx, 11, lz], pony)
        cb(lg, lx, 3.0, lz, 4.0, 8.0, 4.0, 'pony')                                        # leg 4x11x4
        cb(lg, lx, 0.0, lz, 4.0, 3.0, 4.0, 'pony_d', decals={f: [('rect', 0, 0.75, 1, 1, '#2a1a12')] for f in ('north', 'south', 'east', 'west')})   # lower leg + hoof
    nk = m.bone('pony_head', [0, 18, -8], pony)
    ro = dict(rot=('x', -22.5), rot_origin=[0, 18, -8])
    cb(nk, 0, 17.0, -10.5, 4.0, 12.0, 7.0, 'pony', **ro)                                # neck 4x12x7
    cb(nk, 0, 26.0, -14.0, 6.0, 5.0, 7.0, 'pony', **ro)                                 # head 6x5x7
    cb(nk, 0, 25.0, -19.5, 4.0, 5.0, 5.0, 'pony',                                       # muzzle 4x5x5
       decals={'north': pix(["....", "....", "k..k", "....", ".kk."], {'k': '#3a2018'})}, **ro)
    for sx in (1, -1):
        cb(nk, sx * 2.0, 30.6, -12.0, 2.0, 3.0, 1.0, 'pony', **ro)                         # ears
        cb(nk, sx * 3.05, 28.6, -15.4, 0.2, 1.0, 1.0, 'eye', decals={'east': pix(["k"], {'k': '#1a1010'}), 'west': pix(["k"], {'k': '#1a1010'})}, **ro)
    cb(nk, 0, 18.0, -6.8, 2.0, 12.6, 1.8, 'mane', **ro)                                  # yellow mane down the neck
    cb(nk, 0, 30.6, -11.6, 2.4, 1.0, 3.0, 'mane', **ro)
    cb(nk, 0, 30.6, -15.0, 6.4, 1.4, 4.4, 'mane', **ro)                                  # thick tuft on top of the head
    for dx, h in ((-2.4, 2.6), (-1.2, 3.6), (0.0, 4.2), (1.2, 3.4), (2.4, 2.4)):          # fringe hanging over the forehead
        cb(nk, dx, 31.4 - h, -17.9, 1.3, h + 0.6, 1.0, 'mane', decals={'north': [('rect', 0.4, 0, 0.6, 1, '#c8a850')]}, **ro)
    tcr = m.bone('tc_reins', [0, 18, -8], nk)                                            # bridle (team)
    cb(tcr, 0, 27.0, -22.15, 4.4, 1.0, 0.3, 'tc', **ro)                                   # noseband
    for sx in (1, -1):
        cb(tcr, sx * 2.15, 25.4, -19.5, 0.3, 1.0, 5.2, 'tc', **ro)
        cb(tcr, sx * 3.15, 26.0, -14.5, 0.3, 5.0, 1.0, 'tc', **ro)                          # cheek straps
        cb(tcr, sx * 2.3, 25.6, -20.6, 0.5, 1.6, 1.6, 'steel_l', **ro)                      # bit rings
        cb(tcr, sx * 3.2, 20.0, -6.0, 0.3, 0.8, 9.0, 'tc')                                  # reins to the rider
    tl = m.bone('tail', [0, 20, 12], pony)
    cb(tl, 0, 6.0, 13.6, 3.0, 14.0, 4.0, 'mane', rot=('x', -22.5), rot_origin=[0, 20, 12],
       decals={'south': [('rect', 0.45, 0, 0.55, 1, '#c8a850')]})                       # yellow tail
    sad = m.bone('tc_saddle', [0, 21, 1], pony)
    trim = [('rect', 0, 0.85, 1, 1, '#c8c8c8')]
    cb(sad, 0, 21.0, 1.0, 10.8, 0.4, 10.0, 'tc')                                         # saddle cloth
    for sx in (1, -1):
        cb(sad, sx * 5.2, 15.0, 1.0, 0.4, 6.0, 10.0, 'tc', decals={'east': trim, 'west': trim})
    cb(pony, 0, 21.4, 1.0, 8.0, 1.0, 8.0, 'strap')                                      # filled leather saddle seat
    cb(pony, 0, 21.4, -3.2, 6.0, 2.4, 1.4, 'strap'); cb(pony, 0, 21.4, 5.2, 7.0, 2.2, 1.4, 'strap')   # pommel + cantle
    for sx in (1, -1):
        cb(pony, sx * 5.15, 11.0, 0.0, 0.3, 10.6, 1.4, 'strap')                            # girth
    # ---- rider (HQ)
    body = m.bone('body', [0, 16, 1], pony)
    scale = [('px', i / 8, j / 8, '#4a5058') for i in range(0, 8, 2) for j in range(1, 8, 2)] + [('px', i / 8, j / 8, '#9aa2aa') for i in range(1, 8, 2) for j in range(0, 8, 2)]
    for sx in (1, -1):
        cb(body, sx * 4.4, 14.2, -0.6, 3.2, 3.0, 6.4, 'mail', decals={'east': scale, 'west': scale, 'up': scale, 'north': scale})   # thighs astride
        cb(body, sx * 6.0, 8.0, -2.4, 2.8, 6.6, 3.0, 'mail', decals={'east': scale, 'west': scale, 'north': scale, 'south': scale})   # shins down the flanks
        cb(body, sx * 6.1, 6.2, -2.8, 3.2, 2.0, 4.2, 'grip')                                 # boots
        cb(body, sx * 6.1, 5.6, -2.8, 3.4, 0.6, 3.0, 'steel_l')                              # stirrup
    cb(body, 0, 15.2, 1.0, 7.2, 3.0, 4.6, 'mail', decals={'north': scale, 'south': scale})   # mail skirt
    cb(body, 0, 17.4, 1.0, 7.8, 1.4, 5.0, 'grip')                                        # belt
    cb(body, 0, 17.2, -1.6, 2.0, 1.8, 0.4, 'gold', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#8a6a20')]})   # buckle
    cb(body, 0, 18.8, 1.0, 7.6, 5.8, 4.6, 'steel', decals={'north': [('rect', 0.47, 0, 0.53, 1, '#8a929a'), ('rect', 0.1, 0.0, 0.9, 0.12, '#8a929a')]})   # breastplate
    cb(body, 0, 19.2, -1.4, 5.0, 4.0, 0.6, 'steel_l')                                     # chest ridge plate
    for sx in (1, -1):
        cb(body, sx * 4.5, 22.0, 1.0, 3.4, 2.8, 5.4, 'steel')                              # big rounded pauldrons
        cb(body, sx * 4.6, 24.6, 1.0, 2.6, 0.8, 4.4, 'steel_l')
    hd = m.bone('head', [0, 24.4, 1], body)
    face = [('rect', 0.1, 0.46, 0.9, 0.66, '#e8a878'), ('rect', 0.15, 0.46, 0.4, 0.5, '#6a3a2a'), ('rect', 0.6, 0.46, 0.85, 0.5, '#6a3a2a'),
            ('px', 0.28, 0.55, '#ffffff'), ('px', 0.33, 0.55, '#2a1a10'), ('px', 0.67, 0.55, '#2a1a10'), ('px', 0.72, 0.55, '#ffffff'),
            ('rect', 0.45, 0.55, 0.55, 0.78, '#c87a5a'), ('rect', 0.42, 0.72, 0.58, 0.78, '#1a1210'),
            ('rect', 0.48, 0, 0.52, 0.46, '#8a929a'), ('rect', 0.48, 0.78, 0.52, 1, '#8a929a')]
    cb(hd, 0, 24.2, 1.0, 7.2, 9.0, 7.2, 'steel', decals={'north': face})                # tall bucket helm, eye + mouth slots
    for y in (24.4, 30.8, 32.6):
        cb(hd, 0, y, 1.0, 7.6, 0.8, 7.6, 'steel_l')                                        # bands
    cb(hd, 0, 33.2, 1.0, 6.4, 0.6, 6.4, 'steel')                                         # flat top
    for (x, y) in ((-2.8, 31.2), (0.0, 31.2), (2.8, 31.2), (-2.8, 24.8), (2.8, 24.8)):
        cb(hd, x, y, -2.75, 0.9, 0.9, 0.4, 'steel_l')                                      # rivets
    for sx in (1, -1):
        cb(hd, sx * 3.75, 31.2, 1.0, 0.4, 0.9, 0.9, 'steel_l'); cb(hd, sx * 3.75, 24.8, 1.0, 0.4, 0.9, 0.9, 'steel_l')
    pl = m.bone('tc_plume', [0, 33.8, 1.0], hd)
    cb(pl, 0, 33.8, 1.2, 1.4, 1.4, 1.4, 'steel_l')
    for k, (y, z, h, d) in enumerate(((35.0, 1.4, 3.0, 2.0), (37.4, 2.6, 2.4, 2.6), (38.6, 4.8, 2.0, 2.6), (38.0, 7.0, 1.8, 2.4), (36.6, 8.6, 1.8, 1.8), (35.6, 9.8, 1.4, 1.4))):
        cb(pl, 0, y, z, 1.8 - k * 0.15, h, d, 'tc', decals={'east': [('rect', 0, 0.8, 1, 1, '#c8c8c8')], 'west': [('rect', 0, 0.8, 1, 1, '#c8c8c8')]})   # thick curling plume
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.4
        a = m.bone('arm_' + side, [x, 23.0, 1.0], body)
        cb(a, x, 19.6, 1.0, 2.6, 3.6, 2.8, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # mail sleeve
        cb(a, x, 16.6, 1.0, 2.8, 3.2, 3.0, 'steel')                                          # bracer
        cb(a, x, 16.0, 1.0, 3.2, 0.8, 3.4, 'steel_l')
        cb(a, x, 13.6, 0.8, 3.0, 2.8, 3.2, 'steel', decals={'north': pix(["k.k.k", "....."], {'k': '#3a4048'})})   # gauntlet fist
        cb(a, x - sx * 1.6, 14.6, -0.4, 0.8, 1.6, 1.0, 'steel_l')                           # thumb
    mace = m.bone('mace', [5.4, 14.8, 1.0], m.by_name('arm_r'))
    cb(mace, 5.4, 14.6, -2.0, 1.0, 1.0, 7.0, 'grip', decals={'up': [('rect', 0, k, 1, k + 0.08, '#3a2410') for k in (0.2, 0.5, 0.8)]})   # wrapped haft
    cb(mace, 5.4, 14.4, 2.0, 1.4, 1.4, 1.2, 'steel_l')                                   # pommel
    cb(mace, 5.4, 12.0, -7.8, 5.6, 5.6, 5.6, 'steel')                                    # block head
    for (dx, dy, dz) in ((3.3, 2.8, 0), (-3.3, 2.8, 0), (0, 6.1, 0), (0, -0.5, 0), (0, 2.8, -3.3), (0, 2.8, 3.3)):
        w = 2.4 if dx == 0 and dz == 0 else 2.4
        cb(mace, 5.4 + dx, 12.0 + dy - (w / 2 if dy not in (6.1, -0.5) else (0 if dy == 6.1 else w / 2)), -7.8 + dz, w if dx == 0 else 1.0, w if dy not in (6.1, -0.5) else 1.0, w if dz == 0 else 1.0, 'steel_l')   # pyramid spike bases
        cb(mace, 5.4 + dx * 1.15, 12.0 + dy - 0.6 + (0.4 if dy == 6.1 else -0.2 if dy == -0.5 else 0), -7.8 + dz * 1.15, 1.2, 1.2, 1.2, 'steel_l')   # spike tips
    sh = m.bone('shield', [-6.6, 18, 1], m.by_name('arm_l'))
    planks = [('rect', 0, k, 1, k + 0.03, '#5a3418') for k in (0.33, 0.66)]
    cb(sh, -7.0, 12.4, 1.0, 0.8, 8.6, 8.0, 'wood', decals={'west': planks})              # wooden board
    for dz, h in ((-3.0, 3.0), (0.0, 4.0), (3.0, 3.0)):                                  # crown-shaped top: three prongs
        cb(sh, -7.0, 21.0, 1.0 + dz, 0.8, h, 2.0, 'wood', decals={'west': [('rect', 0, 0.33, 1, 0.36, '#5a3418')]})
    cb(sh, -6.4, 11.8, 1.0, 0.6, 9.6, 9.0, 'steel_l')                                     # steel backing
    for dz in (-4.4, 4.4):
        cb(sh, -7.15, 11.8, 1.0 + dz, 0.9, 13.0, 0.9, 'steel_l')                            # side rims (run up the outer prongs)
    cb(sh, -7.15, 11.6, 1.0, 0.9, 0.9, 9.6, 'steel_l')                                    # bottom rim
    for dz, h in ((-3.0, 3.0), (0.0, 4.0), (3.0, 3.0)):
        cb(sh, -7.15, 21.0 + h - 0.8, 1.0 + dz, 0.9, 0.8, 2.6, 'steel_l')                   # prong tips
    for dz in (-1.5, 1.5):
        cb(sh, -7.15, 21.0, 1.0 + dz, 0.9, 0.8, 1.2, 'steel_l')                             # notches between prongs
    cb(sh, -7.6, 14.6, 1.0, 0.6, 1.8, 5.0, 'gold', decals={'west': [('rect', 0, 0.4, 1, 0.6, '#b88a20')]})   # gold crown inlay: band
    for dz, h in ((-2.0, 2.0), (0.0, 2.6), (2.0, 2.0)):
        cb(sh, -7.6, 16.4, 1.0 + dz, 0.6, h, 1.0, 'gold')                                   # crown points
        cb(sh, -7.7, 16.4 + h, 1.0 + dz, 0.6, 0.7, 0.7, 'gold')                             # point balls
    DY = 7.2                                                                         # rider sits on the saddle (seat ~22.4)
    rider = set()
    def sub(bn):
        rider.add(bn.name); [sub(c) for c in bn.children]
    sub(m.by_name('body'))
    for bn in m.bones:
        if bn.name in rider:
            bn.origin[1] += DY
            for c in bn.cubes:
                c['frm'][1] += DY; c['to'][1] += DY; c['rot_origin'][1] += DY
    m.hitbox(1.5, 2.6)
    shade_pass(m, ('pony', 'steel', 'wood', 'mane'))
    hold = {'arm_r': {'rotation': loop([[-30, 0, 0], [-34, 0, 0]], 2.0)}, 'arm_l': {'rotation': loop([[-10, 0, 0], [-12, 0, 0]], 2.0)},
            'pony_head': {'rotation': loop([[0, 0, 0], [6, 0, 0]], 2.0)}}
    m.anim('idle', 2.0, 'loop', hold)
    gal = {('leg_%d' % i): {'rotation': loop([[-35 if i in (0, 3) else 35, 0, 0], [35 if i in (0, 3) else -35, 0, 0]], 0.5)} for i in range(4)}
    gal['pony'] = {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.25)}
    gal.update({k: {'rotation': loop([v['rotation'][0][1], v['rotation'][0][1]], 0.5)} for k, v in hold.items() if k.startswith('arm')})
    m.anim('walk', 0.5, 'loop', gal)
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 0]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, -10]), (0.6, [-30, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-8, 15, 0]), (0.35, [12, -15, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m, hit_bone='pony')
    return m



def electro_spirit():
    """HQ vanilla-like Electro Spirit: round blue-violet flame body fading pink at the flame tips, big toothy grin,
    glowing eyes, stubby arms/legs, crackling electric zigzags"""
    m = new_model('clash_electro_spirit')
    m.mats_({'body': ('#6a6ae0', 'soft'), 'body_d': ('#5050c0', 'soft'), 'flame': ('#a07ae8', 'soft'), 'tip': ('#d890e8', 'soft'),
             'mouth': ('#2a1a40', 'plain'), 'tooth': ('#f6f4f0', 'bone'), 'eye': ('#f0e8ff', 'glow'), 'zap': ('#e8f4ff', 'glow'), 'iris': ('#c060e0', 'glow')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    grad = lambda c, a0, a1: [('lerp', c, a0, a1, 'y')]
    G = {f: grad('#8a7ae8', 0.6, 0.0) for f in ('south', 'east', 'west')}
    cb(body, 0, 2.4, 0.5, 8.0, 7.0, 6.0, 'body', decals=G)                              # round body (back part)
    cb(body, 0, 2.4, -3.0, 8.0, 4.2, 1.0, 'body')                                       # face plate below the eyes
    cb(body, 0, 9.0, -3.0, 8.0, 0.4, 1.0, 'body')                                       # above the eyes
    for x, w in ((-3.55, 0.9), (0.0, 1.4), (3.55, 0.9)):
        cb(body, x, 6.6, -3.0, w, 2.4, 1.0, 'body')                                     # between / beside the sockets
    cb(body, 0, 1.8, 0.6, 6.6, 8.4, 5.4, 'body')
    cb(body, 0, 3.0, 0.6, 8.8, 5.0, 5.4, 'body')
    fl = m.bone('flame', [0, 10, 0], body)                                              # flame top, violet -> pink tips
    cb(fl, 0, 9.0, 0.2, 6.4, 2.6, 5.6, 'flame', decals={f: grad('#6a6ae0', 0.0, 0.6) for f in ('north', 'south', 'east', 'west')})
    for (x, z, h, w) in ((-1.6, 0.4, 3.2, 2.4), (1.4, -0.6, 4.2, 2.6), (0.2, 1.4, 2.6, 2.2), (2.6, 1.0, 2.0, 1.6)):
        cb(fl, x, 11.4, z, w, h, w, 'tip', decals={f: grad('#a07ae8', 1.0, 0.0) for f in ('north', 'south', 'east', 'west')})
    cb(fl, 1.6, 15.4, -0.6, 1.2, 1.4, 1.2, 'tip')
    cb(body, 0, 3.4, -3.55, 6.0, 3.2, 0.3, 'mouth')                                     # big grin
    for k, x in enumerate((-2.2, -0.75, 0.75, 2.2)):
        cb(body, x, 5.6, -3.7, 1.2, 1.0, 0.3, 'tooth')                                   # upper teeth
    for x in (-1.5, 0.0, 1.5):
        cb(body, x, 3.4, -3.7, 1.1, 0.9, 0.3, 'tooth')                                   # lower teeth
    for sx in (1, -1):
        cb(body, sx * 1.9, 6.6, -2.4, 2.4, 2.4, 0.2, 'eye', decals={'north': [('rect', 0.2, 0.2, 0.8, 0.8, '#c060e0'), ('rect', 0.35, 0.35, 0.65, 0.65, '#2a1040'), ('px', 0.4, 0.4, '#ffffff')]})   # glowing eyes: white, violet iris, dark pupil
        cb(body, sx * 1.9, 9.1, -3.55, 2.4, 0.5, 0.3, 'body_d')                         # brows
        cb(body, sx * 1.9, 7.0, -2.6, 1.6, 1.6, 0.2, 'iris')                               # 3D violet iris
        cb(body, sx * 1.9, 7.35, -2.75, 0.9, 0.9, 0.2, 'mouth')                              # dark pupil
        cb(body, sx * 1.9 - 0.25, 7.85, -2.87, 0.4, 0.4, 0.1, 'eye')                         # glint
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.2, 6, 0], body)
        cb(a, sx * 5.0, 3.6, 0, 1.8, 2.8, 1.8, 'body')                                   # stubby arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0, 0, 2.4, 2.4, 2.6, 'body_d')                                  # stubby legs
    bd = m.bone('zap_beard', [0, 6.4, -3.8], body)                                       # electric zigzag moustache
    for k, (x, y) in enumerate(((-4.6, 6.0), (-3.6, 6.6), (-2.6, 6.0), (-1.4, 6.8), (-0.4, 6.2), (0.6, 6.8), (1.6, 6.0), (2.8, 6.6), (3.8, 6.0), (4.8, 6.6))):
        cb(bd, x, y, -3.85, 1.2, 0.5, 0.3, 'zap')
        if k % 2 == 0:
            cb(bd, x + 0.45, y, -3.85, 0.4, 0.9, 0.3, 'zap')
    for sx in (1, -1):
        cb(bd, sx * 5.4, 5.0, -3.0, 0.4, 1.6, 0.4, 'zap'); cb(bd, sx * 5.8, 4.6, -2.6, 0.4, 0.4, 1.0, 'zap')   # crackling ends
    zp = m.bone('zaps', [0, 6, 0], body)                                                 # electric zigzags (pulse)
    for (x, y, z, w, h, d) in ((-4.8, 8.0, -1.0, 0.4, 2.0, 0.4), (-5.2, 9.6, -0.6, 0.4, 0.4, 1.6), (4.6, 10.6, 0.8, 0.4, 2.2, 0.4),
                               (5.0, 12.4, 0.2, 0.4, 0.4, 1.4), (-2.0, 15.0, 0.6, 1.6, 0.4, 0.4), (-2.6, 15.4, 0.4, 0.4, 1.4, 0.4)):
        cb(zp, x, y, z, w, h, d, 'zap')
    m.hitbox(0.6, 1.0)
    shade_pass(m, ('body',))
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.6, 0]], 0.8), 'scale': loop([[1, 1, 1], [1.04, 0.97, 1.04]], 0.8)},
                                 'flame': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 0.4)}, 'zaps': {'scale': loop([[1, 1, 1], [0, 0, 0], [1.2, 1.2, 1.2]], 0.3)},
                                 'zap_beard': {'scale': loop([[1, 1, 1], [1.08, 0.7, 1], [1, 1.2, 1]], 0.2)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.2)}, 'flame': {'rotation': loop([[10, 0, 0], [16, 0, 0]], 0.2)},
                                 'arm_r': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], 0.4)}, 'arm_l': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], 0.4)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]},
                                   'zaps': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m



def fire_spirit():
    """HQ vanilla-like Fire Spirit: charred dark round body with glowing cracks, big recessed glowing eyes,
    heavy brow ridge, tall layered flame (red -> orange -> yellow), stubby glowing-tipped limbs"""
    m = new_model('clash_fire_spirit')
    m.mats_({'char': ('#4a2416', 'soft'), 'char_d': ('#2e140c', 'soft'), 'glow': ('#ff9a30', 'glow'), 'eye': ('#fff4c8', 'glow'),
             'iris': ('#ffb040', 'glow'), 'f1': ('#e8401a', 'glow'), 'f2': ('#ff8a20', 'glow'), 'f3': ('#ffd050', 'glow'), 'void': ('#1a0a06', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    cracks = [('rect', 0.2, 0.3, 0.22, 0.7, '#ff7a20'), ('rect', 0.22, 0.68, 0.4, 0.7, '#ff7a20'), ('rect', 0.7, 0.2, 0.72, 0.5, '#ff7a20')]
    G = {f: [('lerp', '#7a3a1a', 0.0, 0.5, 'y')] + cracks for f in ('south', 'east', 'west')}
    cb(body, 0, 2.4, 0.5, 8.0, 7.0, 6.0, 'char', decals=G)                              # body (back part)
    cb(body, 0, 1.8, 0.6, 6.6, 8.4, 5.4, 'char'); cb(body, 0, 3.0, 0.6, 8.8, 5.0, 5.4, 'char')
    cb(body, 0, 2.4, -3.0, 8.0, 4.2, 1.0, 'char', decals={'north': [('lerp', '#2e140c', 0.0, 0.6, 'y')]})   # lower face
    cb(body, 0, 9.0, -3.0, 8.0, 0.4, 1.0, 'char')
    for x, w in ((-3.55, 0.9), (0.0, 1.4), (3.55, 0.9)):
        cb(body, x, 6.6, -3.0, w, 2.4, 1.0, 'char')
    for sx in (1, -1):
        cb(body, sx * 1.9, 6.6, -2.4, 2.4, 2.4, 0.2, 'eye')                               # recessed glowing eyes
        cb(body, sx * 1.9 + sx * 0.4, 7.2, -2.6, 0.9, 1.1, 0.2, 'iris')                    # amber pupil looking aside
        cb(body, sx * 2.0, 9.0, -3.7, 3.0, 1.0, 1.4, 'char_d')                            # heavy brow ridge
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.2, 6, 0], body)
        cb(a, sx * 5.0, 3.8, 0, 1.8, 2.8, 1.8, 'char'); cb(a, sx * 5.0, 3.2, 0, 1.6, 0.8, 1.6, 'glow')   # arms with glowing tips
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0.6, 0, 2.4, 1.8, 2.6, 'char_d'); cb(lg, sx * 1.8, 0, 0, 2.2, 0.6, 2.4, 'glow')
    cb(body, 0, 9.4, 0.6, 8.2, 0.6, 6.0, 'char_d')                                       # charred crown
    fl = m.bone('flame', [0, 10, 0], body)                                              # layered flame
    for (x, z, h, w, mat) in ((0, 0.6, 2.4, 5.6, 'f1'), (-1.8, 0.6, 5.0, 2.6, 'f1'), (1.6, 0.0, 6.2, 2.8, 'f1'), (0.0, 1.8, 4.0, 2.6, 'f1'),
                              (-0.4, 0.2, 7.0, 2.0, 'f2'), (2.2, 1.2, 4.6, 1.8, 'f2'), (-2.4, -0.4, 3.6, 1.6, 'f2'),
                              (0.4, -0.2, 8.4, 1.2, 'f3'), (-1.6, 0.8, 5.6, 1.0, 'f3'), (2.6, 0.4, 6.0, 0.8, 'f3')):
        cb(fl, x, 10.0, z, w, h, w * 0.85, mat)
    for (x, y, z) in ((1.0, 19.4, 0.0), (-1.6, 16.8, 0.8), (2.8, 17.2, 0.6)):
        cb(fl, x, y, z, 0.6, 0.8, 0.6, 'f3')                                              # embers
    m.hitbox(0.6, 1.0)
    shade_pass(m, ('char',))
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.6, 0]], 0.8)},
                                 'flame': {'scale': loop([[1, 1, 1], [1.05, 1.15, 1.05], [0.97, 0.95, 0.97]], 0.3), 'rotation': loop([[0, 0, 4], [0, 0, -4]], 0.4)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.2)}, 'flame': {'rotation': loop([[12, 0, 0], [18, 0, 0]], 0.2)},
                                 'arm_r': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], 0.4)}, 'arm_l': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], 0.4)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]},
                                   'flame': {'scale': [(0, [1, 1, 1]), (0.25, [1.6, 1.8, 1.6]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m



def ice_spirit():
    """Ice Spirit: round snowball body, recessed cyan eyes, huge open grin with ice teeth, ice-crystal spikes, crystal arms/feet"""
    m = new_model('clash_ice_spirit')
    m.mats_({'snow': ('#f2f4f8', 'soft'), 'ice': ('#58c0f0', 'gem'), 'ice_l': ('#a8e4ff', 'gem'), 'mouth': ('#3a3aa0', 'plain'),
             'eye': ('#7ad8f8', 'glow'), 'tooth': ('#bce8ff', 'gem')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    cb(body, 0, 2.0, 0.6, 9.0, 9.0, 7.6, 'snow')                                        # snowball (back)
    cb(body, 0, 1.2, 0.6, 7.0, 10.6, 6.0, 'snow'); cb(body, 0, 3.2, 0.6, 10.4, 6.6, 6.0, 'snow')
    cb(body, 0, 9.0, -3.6, 9.0, 2.0, 1.0, 'snow')                                       # forehead
    for x, w in ((-4.15, 0.7), (0.0, 1.4), (4.15, 0.7)):
        cb(body, x, 6.6, -3.6, w, 2.4, 1.0, 'snow')
    for sx in (1, -1):
        cb(body, sx * 2.25, 6.6, -3.35, 3.1, 2.4, 0.2, 'eye')                               # recessed eyes
    cb(body, 0, 1.6, -3.6, 9.0, 1.4, 1.0, 'snow')                                       # chin
    for sx in (1, -1):
        cb(body, sx * 4.1, 3.0, -3.6, 0.8, 3.6, 1.0, 'snow')
    cb(body, 0, 3.0, -3.3, 7.4, 3.6, 0.2, 'mouth')                                      # big open mouth
    for x in (-2.7, -0.9, 0.9, 2.7):
        cb(body, x, 5.6, -3.4, 1.5, 1.0, 1.2, 'tooth')                                    # upper ice teeth
    for x in (-1.8, 0.0, 1.8):
        cb(body, x, 3.0, -3.4, 1.4, 0.9, 1.2, 'tooth')                                    # lower
    sp = m.bone('crystals', [0, 10, 0], body)
    for (x, y, z, w, h, r) in ((-3.0, 10.4, 0.6, 2.0, 4.0, ('z', 22.5)), (0.4, 10.8, 1.0, 2.4, 5.0, None), (3.2, 10.2, 0.4, 2.0, 3.6, ('z', -22.5)),
                               (-5.2, 6.0, 1.2, 1.8, 3.4, ('z', 45)), (5.4, 5.4, 1.4, 1.8, 3.2, ('z', -45)), (0.0, 7.0, 4.4, 2.0, 3.6, ('x', -45))):
        cb(sp, x, y, z, w, h, w, 'ice', rot=r, rot_origin=[x, y, z], decals={'north': [('rect', 0.2, 0.0, 0.4, 1, '#a8e4ff')]})
    for sx in (1, -1):
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 5.0, 5, 0], body)
        cb(a, sx * 6.6, 4.4, -0.4, 3.0, 1.6, 1.8, 'ice'); cb(a, sx * 8.2, 4.8, -0.4, 1.2, 2.2, 1.6, 'ice_l')   # crystal arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0, 0.4, 1.6, 2.6, 1.6, 'ice')                                     # crystal feet
    m.hitbox(0.6, 1.0)
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.8)}, 'crystals': {'rotation': loop([[0, 0, 3], [0, 0, -3]], 0.8)},
                                 'arm_r': {'rotation': loop([[0, 0, -10], [0, 0, 10]], 0.8)}, 'arm_l': {'rotation': loop([[0, 0, 10], [0, 0, -10]], 0.8)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 0.2)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m



def heal_spirit():
    """Heal Spirit: glowing yellow gummy body with a pointy tip, recessed orange eye sockets with glowing pupils,
    huge open mouth, one buck tooth, big red tongue hanging out, stubby arms and legs"""
    m = new_model('clash_heal_spirit')
    m.mats_({'y': ('#f8d838', 'soft'), 'y_d': ('#e0b020', 'soft'), 'sock': ('#f0a020', 'glow'), 'pupil': ('#fff4a0', 'glow'),
             'mouth': ('#a0401a', 'plain'), 'tongue': ('#e04838', 'skin'), 'tooth': ('#fff8e0', 'bone')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    cb(body, 0, 2.0, 0.6, 9.0, 9.4, 7.0, 'y')                                          # body (back)
    cb(body, 0, 1.4, 0.6, 7.4, 10.8, 5.6, 'y'); cb(body, 0, 3.0, 0.6, 10.2, 7.0, 5.6, 'y')
    cb(body, 1.4, 12.2, 0.6, 2.4, 1.6, 2.4, 'y'); cb(body, 2.2, 13.8, 0.6, 1.2, 1.2, 1.2, 'y')   # pointy tip
    cb(body, 0, 9.4, -3.3, 9.0, 1.6, 1.0, 'y')                                          # forehead
    for x, w in ((-4.15, 0.7), (0.0, 1.4), (4.15, 0.7)):
        cb(body, x, 7.0, -3.3, w, 2.4, 1.0, 'y')
    for sx in (1, -1):
        cb(body, sx * 2.25, 7.0, -2.9, 3.1, 2.4, 0.2, 'sock')                              # recessed orange sockets
        cb(body, sx * 2.25, 7.6, -3.1, 1.2, 1.2, 0.2, 'pupil')                             # glowing pupils
    cb(body, 0, 1.8, -3.3, 9.0, 1.4, 1.0, 'y')                                          # chin
    for sx in (1, -1):
        cb(body, sx * 4.1, 3.2, -3.3, 0.8, 3.8, 1.0, 'y')
    cb(body, 0, 3.2, -2.9, 7.4, 3.8, 0.2, 'mouth')                                      # big open mouth
    cb(body, -1.6, 6.0, -3.3, 1.4, 1.0, 1.0, 'tooth')                                   # buck tooth
    tg = m.bone('tongue', [1.0, 3.6, -3.4], body)
    cb(tg, 1.0, 3.2, -4.2, 3.4, 0.8, 2.6, 'tongue', decals={'up': [('rect', 0.48, 0, 0.52, 1, '#b83020')]})
    cb(tg, 1.0, 0.8, -5.4, 3.4, 3.0, 0.8, 'tongue', decals={'north': [('rect', 0.48, 0, 0.52, 0.8, '#b83020')]})   # tongue hanging out
    for sx in (1, -1):
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.8, 7, 0], body)
        cb(a, sx * 6.0, 5.6, 0.4, 2.4, 3.0, 2.2, 'y'); cb(a, sx * 7.0, 7.2, 0.4, 1.4, 1.6, 1.6, 'y')   # waving arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.9, 2, 0], root)
        cb(lg, sx * 1.9, 0, 0.4, 2.8, 2.6, 3.0, 'y_d')
    m.hitbox(0.7, 0.9)
    shade_pass(m, ('y',))
    m.anim('idle', 1.0, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.8, 0]], 1.0)}, 'tongue': {'rotation': loop([[0, 0, 0], [12, 0, 0]], 0.5)},
                                 'arm_r': {'rotation': loop([[0, 0, -15], [0, 0, 15]], 1.0)}, 'arm_l': {'rotation': loop([[0, 0, 15], [0, 0, -15]], 1.0)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 0.2)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m



def giant():
    """HQ vanilla-like Giant: bald head, ginger hair ring + big bushy beard/moustache, heavy brow, big nose,
    laced leather vest, team belt with brass buckle, dark shorts, huge fists, bare feet"""
    m = new_model('clash_giant')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'beard': ('#d8783a', 'hair'), 'beard_d': ('#b45a24', 'hair'),
             'vest': ('#8a5a36', 'leather'), 'vest_d': ('#6a4224', 'leather'), 'lace': ('#d8c0a0', 'rope'), 'belt': ('#efefef', 'leather'),
             'brass': ('#c89a40', 'metal'), 'shorts': ('#4a3428', 'cloth'), 'eyew': ('#ffffff', 'plain'), 'mouthd': ('#5a2a1a', 'plain')})
    D = '#c88a64'
    r = Rig(m, 1.75); B = r.box
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = r.bone('leg_' + side, [x, 11, 0], root)
        B(lg, x, 1.2, 0, 4.0, 9.8, 4.0, 'skin')
        B(lg, x, 8.0, 0, 4.4, 3.4, 4.4, 'shorts')                                         # shorts legs
        B(lg, x, 0, -0.6, 4.4, 1.4, 5.4, 'skin_d', decals={'north': pix(["k.k.k.k", "......."], {'k': D})})   # bare feet + toes
    body = r.bone('body', [0, 11, 0], root)
    lace = pix(["...k...", "..k.k..", "...k...", "..k.k..", "...k...", "..k.k..", "...k..."], {'k': '#d8c0a0'})
    B(body, 0, 11.0, 0, 9.0, 3.0, 5.0, 'shorts')
    B(body, 0, 13.6, 0, 9.6, 11.0, 5.4, 'vest', decals={'north': [('rect', 0.42, 0, 0.58, 1, '#eeb08a')] + lace, 'south': [('shade', 0, 0.8, 1, 1, 0.8)]})   # laced vest open at the chest
    B(body, 0, 12.6, -0.1, 10.0, 1.4, 5.6, 'vest_d', decals={'north': pix(["k.k.k.k.k"], {'k': '#5a3418'})})   # ragged hem
    tc = r.bone('tc_belt', [0, 14, 0], body)
    B(tc, 0, 13.6, 0, 10.0, 1.8, 5.8, 'belt')                                            # team belt
    B(body, 0, 13.4, -2.95, 2.4, 2.2, 0.3, 'brass', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#6a4a18')]})   # buckle
    for sx in (1, -1):
        B(body, sx * 4.0, 23.6, 0, 3.6, 1.2, 5.6, 'vest_d')                              # shoulder seams
    hd = r.bone('head', [0, 24.6, -0.4], body)
    B(hd, 0, 24.6, -0.4, 7.4, 7.4, 7.0, 'skin', decals={'up': [('rect', 0.3, 0.3, 0.7, 0.7, '#f8c8a0')]})   # bald head
    for sx in (1, -1):
        B(hd, sx * 1.8, 27.4, -4.0, 1.8, 1.2, 0.2, 'eyew', decals={'north': [('rect', 0.5 if sx > 0 else 0.0, 0, 1.0 if sx > 0 else 0.5, 1, '#3a6aa8')]})   # eyes: white + blue
        B(hd, sx * 1.9, 28.6, -4.1, 2.6, 0.8, 0.5, 'beard_d')                              # ginger eyebrows
        B(hd, sx * 3.8, 26.0, 1.2, 0.4, 3.6, 2.6, 'beard')                                 # side hair behind the ears
        B(hd, sx * 3.9, 27.0, 0.4, 0.4, 1.6, 1.4, 'skin')                                  # ears
    B(hd, 0, 26.0, 3.15, 7.6, 3.6, 0.4, 'beard')                                         # back hair ring
    B(hd, 0, 26.0, -4.4, 1.8, 2.0, 1.0, 'skin_d')                                        # big nose
    for sx in (1, -1):
        B(hd, sx * 3.75, 24.6, -1.6, 0.4, 3.2, 3.4, 'beard')                                # short sideburns on the face
    B(hd, 0, 24.0, -3.95, 7.6, 0.9, 0.3, 'beard')                                        # trimmed beard along the jaw line
    B(hd, 0, 23.6, -3.6, 4.4, 1.0, 1.0, 'beard')                                         # short chin
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.6
        a = r.bone('arm_' + side, [x, 23.0, 0], body)
        B(a, x, 18.6, 0, 4.4, 5.6, 4.4, 'skin')                                           # huge shoulders / biceps
        B(a, x, 12.6, 0, 3.8, 6.0, 3.8, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.7, D)]})
        B(a, x, 9.6, -0.2, 4.6, 3.4, 4.6, 'skin_d', decals={'north': pix(["k.k.k", ".....", "....."], {'k': D})})   # big fist
    WX, LS = 1.25, 1.6
    for bn in m.bones:
        if bn.name == 'root': continue
        leg = bn.name.startswith('leg_')
        for c in bn.cubes:
            if not leg and bn.name != 'head':
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][0] *= WX
            if leg:
                if c['to'][1] > 3: c['to'][1] -= LS
                if c['frm'][1] > 3: c['frm'][1] -= LS
            else:
                for k in ('frm', 'to', 'rot_origin'):
                    c[k][1] -= LS * 1.0
        if not leg and bn.name != 'head': bn.origin[0] *= WX
        bn.origin[1] -= LS if bn.name != 'root' else 0
    m.hitbox(2.2, 3.6)
    shade_pass(m, ('skin', 'vest'))
    mc_idle(m, 2.4)
    mc_walk(m, 1.4, 22)
    m.anim('attack', 1.2, 'once', {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.4, [-150, 0, 10]), (0.6, [-20, 0, 0]), (1.2, [0, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.4, [-8, 10, 0]), (0.6, [12, -8, 0]), (1.2, [0, 0, 0])]}})
    common_tail(m)
    return m



def electro_wizard_prev():
    """Electro Wizard: spiky zig-zag black/blue hair, zig-zag moustache + thick brows, big grin, team robe with gold
    lapels, olive belt + gold buckle, wristbands, crackling electricity on both hands"""
    m = new_model('clash_electro_wizard')
    m.mats_({'skin': ('#e8b08c', 'skin'), 'hair': ('#1e2230', 'hair'), 'hair_b': ('#3a5ad8', 'hair'), 'robe': ('#efefef', 'cloth'),
             'gold': ('#e0b030', 'metal'), 'belt': ('#5a5a3a', 'leather'), 'pants': ('#2a2a38', 'cloth'), 'boot': ('#2a1a12', 'leather'),
             'zap': ('#c8f4ff', 'glow'), 'eye': ('#ffffff', 'plain')})
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 2, 2, 0, 4, 10, 4, 'pants'); cb(lg, sx * 2, 0, -0.3, 4.2, 2.6, 4.6, 'boot')
    body = m.bone('body', [0, 12, 0], root)
    tc = m.bone('tc_robe', [0, 12, 0], body)
    cb(tc, 0, 10.0, 0, 8.4, 14.0, 4.4, 'robe', decals={'north': [('rect', 0.45, 0, 0.55, 1, '#c8c8c8')]})   # team robe
    for sx in (1, -1):
        cb(body, sx * 1.6, 15.0, -2.35, 1.2, 9.0, 0.4, 'gold', rot=('z', sx * 22.5), rot_origin=[sx * 1.6, 24, -2.35])   # gold lapels
        cb(body, sx * 3.6, 22.0, 0.2, 1.2, 3.6, 4.6, 'gold')                               # gold collar
    cb(body, 0, 13.4, 0, 8.8, 1.8, 4.8, 'belt'); cb(body, 0, 13.2, -2.5, 2.4, 2.2, 0.3, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#5a5a3a')]})
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".we..ew.", "........", "........", ".tttttt.", "........"], {'w': '#ffffff', 'e': '#3a8ad8', 't': '#f8f6ee'})
    cb(hd, 0, 24, 0, 8, 8, 8, 'skin', decals={'north': face})
    cb(hd, 0, 27.6, -4.3, 1.6, 2.2, 1.0, 'skin')                                          # nose
    for sx in (1, -1):
        cb(hd, sx * 2.0, 29.4, -4.2, 3.4, 1.0, 0.6, 'hair'); cb(hd, sx * 3.4, 29.0, -4.2, 1.0, 0.8, 0.6, 'hair')   # thick brows
        for k in range(3):                                                                # zig-zag moustache
            cb(hd, sx * (1.0 + k * 1.2), 26.4 - (k % 2) * 0.6, -4.3, 1.2, 0.8, 0.6, 'hair')
    hair = m.bone('hair', [0, 32, 0], hd)
    cb(hair, 0, 31.6, 0.6, 8.6, 1.6, 7.6, 'hair'); cb(hair, 0, 27.0, 3.9, 8.6, 5.0, 0.8, 'hair')
    for (x, y, z, h, r) in ((-3.6, 32.6, 0, 3.6, ('z', 45)), (-1.4, 33.0, -1.6, 4.4, ('z', 22.5)), (1.2, 33.0, -1.0, 4.8, ('z', -22.5)),
                            (3.6, 32.4, 0.4, 3.6, ('z', -45)), (0.0, 32.8, 2.4, 4.0, ('x', -22.5)), (-2.6, 32.4, 2.6, 3.0, ('x', -45)),
                            (2.8, 32.4, 2.8, 3.0, ('x', -45)), (-4.6, 28.0, 1.0, 3.2, ('z', 45)), (4.6, 28.0, 1.0, 3.2, ('z', -45))):
        cb(hair, x, y, z, 1.6, h, 1.6, 'hair', rot=r, rot_origin=[x, y, z], decals={'north': [('rect', 0.3, 0, 0.5, 1, '#3a5ad8')]})   # spiky electric hair
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5, 22, 0], body)
        sl = m.bone('tc_sleeve_' + side, [sx * 5, 22, 0], a)
        cb(sl, sx * 6, 15, 0, 4, 7, 4, 'robe'); cb(a, sx * 6, 12, 0, 3.6, 3, 3.6, 'skin')
        cb(sl, sx * 6, 13.6, 0, 4.2, 1.4, 4.2, 'robe')                                      # wristband
        z = m.bone('zap_' + side, [sx * 6, 11, 0], a)
        for (dx, y, dz, w, h, d) in ((0.8, 10.0, -1.4, 0.4, 2.2, 0.4), (1.4, 9.0, -0.8, 0.4, 0.4, 1.6), (-1.2, 9.4, 1.0, 0.4, 2.0, 0.4),
                                     (0.0, 8.0, -2.4, 0.4, 0.4, 2.0), (-0.6, 7.2, 0.6, 1.6, 0.4, 0.4)):
            cb(z, sx * 6 + dx * 2, 11 - (11 - y) * 2, dz * 2, w * 1.6 if w < 1 else w * 2, h * 2 if h > 1 else h * 1.6, d * 2 if d > 1 else d * 1.6, 'zap')
    m.hitbox(0.9, 2.1)
    shade_pass(m, ('skin', 'robe'))
    zl = {'zap_r': {'scale': loop([[1, 1, 1], [0.2, 0.2, 0.2], [1.3, 1.3, 1.3]], 0.25)}, 'zap_l': {'scale': loop([[0.6, 0.6, 0.6], [1.3, 1.3, 1.3], [0, 0, 0]], 0.25)}}
    mc_idle(m, 2.0, extra=dict(zl)); mc_walk(m, 0.7, 30, extra=dict(zl))
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.2, [-90, 15, 0]), (0.5, [-90, 15, 0]), (0.6, [0, 0, 0])]},
                                   'arm_l': {'rotation': [(0, [0, 0, 0]), (0.2, [-90, -15, 0]), (0.5, [-90, -15, 0]), (0.6, [0, 0, 0])]},
                                   'zap_r': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.6, [1, 1, 1])]}, 'zap_l': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.6, [1, 1, 1])]}})
    common_tail(m)
    return m



def _elixir_brute(name, S, hb):
    """HQ vanilla-like Elixir Golem body: magenta gummy gorilla build, small blocky head with glowing angry eyes,
    huge shoulders/arms, drips, spiked team wristbands, short legs with toes"""
    m = new_model(name)
    m.mats_({'ex': ('#c040d8', 'soft'), 'ex_d': ('#9a28b0', 'soft'), 'ex_l': ('#e070f0', 'soft'), 'eye': ('#ffd0ff', 'glow'),
             'band': ('#efefef', 'leather'), 'spike': ('#c8ccd4', 'metal')})
    r = Rig(m, S); B = r.box
    drip = lambda: [('rect', 0.2, 0.6, 0.28, 1.0, '#9a28b0'), ('rect', 0.6, 0.7, 0.68, 1.0, '#9a28b0')]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = r.bone('leg_' + side, [x, 9, 0], root)
        B(lg, x, 1.0, 0, 4.4, 8.0, 4.6, 'ex')
        B(lg, x, 0, -0.6, 5.0, 1.4, 6.0, 'ex_d', decals={'north': pix(["k.k.k.k", "......."], {'k': '#8a2098'})})   # feet + toes
    body = r.bone('body', [0, 9, 0], root)
    B(body, 0, 8.6, 0.4, 10.4, 6.0, 7.0, 'ex', decals={'north': drip(), 'south': drip()})      # pot belly
    B(body, 0, 14.0, 0.8, 15.0, 8.4, 8.4, 'ex', decals={'north': [('rect', 0.48, 0.2, 0.52, 0.7, '#9a28b0')] + drip()})   # huge chest
    for sx in (1, -1):
        B(body, sx * 3.6, 22.2, 1.6, 4.0, 1.4, 5.4, 'ex', rot=('z', -sx * 22.5), rot_origin=[sx * 1.6, 22.6, 1.6])   # sloped trapezius to the neck
    for (x, y) in ((-4.0, 13.8), (3.0, 14.2), (5.6, 10.0)):
        B(body, x, y, -3.7, 1.0, 1.6, 0.6, 'ex_l')                                           # drip blobs
    hd = r.bone('head', [0, 23.5, -1.4], body)
    B(hd, 0, 22.4, -1.6, 5.2, 5.6, 5.2, 'ex', decals={'north': pix(["......", "......", ".k..k.", "......", "......", "......"], {'k': '#7a1890'})})
    B(hd, 1.0, 28.0, -0.8, 2.0, 1.6, 2.0, 'ex')                                          # pointy top
    for sx in (1, -1):
        B(hd, sx * 1.3, 24.4, -4.3, 1.6, 0.8, 0.3, 'eye')                                    # glowing angry eyes
        B(hd, sx * 1.3, 25.1, -4.35, 2.2, 0.7, 0.6, 'ex_d', rot=('z', sx * 22.5), rot_origin=[sx * 1.3, 25.45, -4.35])   # angry brows (inner ends down)
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 10.2
        a = r.bone('arm_' + side, [x, 21.5, 1], body)
        B(a, x, 15.0, 1.0, 5.6, 7.0, 5.6, 'ex', decals={'north': drip()})                    # upper arm
        B(a, x, 7.4, 0.6, 6.4, 7.6, 6.4, 'ex', decals={'north': drip(), 'east': drip(), 'west': drip()})   # thick forearm
        tc = r.bone('tc_band_' + side, [x, 9, 1], a)
        B(tc, x, 8.4, 0.6, 7.2, 2.6, 7.2, 'band')                                            # team wristband
        for (dx, dz) in ((sx * 3.8, 0), (0, -3.8), (0, 3.8), (-sx * 3.8, 0)):
            B(a, x + dx * 1.1, 8.8, 0.6 + dz * 1.1, 1.8, 1.8, 1.8, 'spike'); B(a, x + dx * 1.3, 9.2, 0.6 + dz * 1.3, 0.9, 1.0, 0.9, 'spike')                               # spikes
        B(a, x, 3.0, 0.2, 6.0, 4.6, 6.0, 'ex_d', decals={'north': pix(["k.k.k", ".....", "....."], {'k': '#7a1890'})})   # big fist
    m.hitbox(*hb)
    shade_pass(m, ('ex',))
    mc_idle(m, 2.4); mc_walk(m, 1.4, 20)
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.4, [-160, 0, 0]), (0.6, [-20, 0, 0]), (1.2, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    slam['body'] = {'rotation': [(0, [0, 0, 0]), (0.4, [-10, 0, 0]), (0.6, [18, 0, 0]), (1.2, [0, 0, 0])]}
    m.anim('attack', 1.2, 'once', slam)
    common_tail(m)
    return m


def elixir_golem():
    return _elixir_brute('clash_elixir_golem', 1.25, (2.0, 2.8))


def elixir_golemite():
    return _elixir_brute('clash_elixir_golemite', 0.75, (1.3, 1.6))


def elixir_blob():
    """small elixir gummy blob with the golem's face and a tiny team wristband-ribbon"""
    m = new_model('clash_elixir_blob')
    m.mats_({'ex': ('#c040d8', 'soft'), 'ex_d': ('#9a28b0', 'soft'), 'eye': ('#ffd0ff', 'glow'), 'band': ('#efefef', 'leather')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 3, 0], root)
    cb(body, 0, 0, 0, 7.0, 5.0, 7.0, 'ex'); cb(body, 0, 0, 0, 5.6, 6.4, 5.6, 'ex'); cb(body, 0.8, 6.4, 0.4, 2.0, 1.4, 2.0, 'ex')
    for sx in (1, -1):
        cb(body, sx * 1.4, 3.6, -3.6, 1.4, 0.8, 0.2, 'eye')
        cb(body, sx * 1.4, 4.6, -3.65, 1.8, 0.5, 0.3, 'ex_d')
    cb(body, 0, 1.6, -3.55, 3.0, 0.8, 0.1, 'ex_d')                                         # mouth
    tc = m.bone('tc_ribbon', [0, 2, 0], body)
    cb(tc, 0, 1.2, 0, 7.2, 1.0, 7.2, 'band')
    m.hitbox(0.7, 0.7)
    shade_pass(m, ('ex',))
    m.anim('idle', 1.0, 'loop', {'body': {'scale': loop([[1, 1, 1], [1.08, 0.9, 1.08]], 1.0)}})
    m.anim('walk', 0.5, 'loop', {'root': {'position': loop([[0, 0, 0], [0, 2.0, 0]], 0.25)}, 'body': {'scale': loop([[1.1, 0.85, 1.1], [0.92, 1.1, 0.92]], 0.25)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.25, 0.8, 1.25]), (0.3, [0.85, 1.2, 0.85]), (0.5, [1, 1, 1])]},
                                   'root': {'position': [(0, [0, 0, 0]), (0.3, [0, 1, -2]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m



def _rock_golem(name, S, hb):
    """HQ vanilla-like Golem: hunched stack of faceted boulders, small head sunk between huge shoulders,
    glowing magenta eyes under a heavy brow, long rock arms with big boulder fists, short stubby legs, team rune on the chest"""
    m = new_model(name)
    m.mats_({'rock': ('#b4aa9e', 'stone'), 'rock_d': ('#968c80', 'stone'), 'rock_l': ('#c8beb2', 'stone'), 'cry': ('#f4f8ff', 'gem'), 'eye': ('#ff60e8', 'glow'),
             'void': ('#2a2420', 'plain'), 'rune': ('#efefef', 'glow')})
    r = Rig(m, S); B = r.box
    root = m.bone('root', [0, 0, 0])
    def boulder(bone, x, y, z, w, h, d, mat='rock'):
        B(bone, x, y + 0.6, z, w, h - 1.2, d, mat); B(bone, x, y, z, w - 1.2, h, d - 1.2, mat)   # chamfered rock chunk
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.4
        lg = r.bone('leg_' + side, [x, 8, 0.6], root)
        boulder(lg, x, 3.0, 0.6, 4.6, 5.0, 4.6, 'rock_d')
        boulder(lg, x, 0, 0.0, 5.4, 3.2, 6.2)                                              # stubby rock feet
    body = r.bone('body', [0, 8, 0], root)
    boulder(body, 0, 7.0, 1.2, 9.0, 5.4, 7.0, 'rock_d')                                   # hips
    boulder(body, 0, 11.6, 0.4, 14.0, 8.0, 9.6)                                           # massive chest
    boulder(body, -3.6, 18.4, 1.6, 7.0, 4.0, 7.4, 'rock_l'); boulder(body, 3.8, 18.6, 1.0, 7.0, 4.2, 7.4)   # hunched shoulder humps
    boulder(body, 0, 19.6, 3.4, 8.0, 3.0, 5.0, 'rock_d')                                  # back hump
    tc = r.bone('tc_rune', [0, 20, 2], body)                                           # team-coloured crystals on the back + shoulders
    for (x, y, z, w, h, rot) in ((0.0, 21.0, 2.6, 2.6, 5.0, None), (-1.8, 20.6, 3.6, 1.8, 3.6, ('z', 22.5)), (2.0, 20.6, 3.4, 2.0, 4.0, ('z', -22.5)),
                                 (1.0, 20.4, 5.0, 1.4, 2.6, ('x', -22.5)), (-9.6, 19.6, 1.2, 1.6, 3.2, ('z', 22.5)), (-8.8, 19.4, 2.4, 1.0, 2.0, None),
                                 (9.6, 19.8, 1.2, 1.8, 3.6, ('z', -22.5)), (10.6, 19.4, 0.4, 1.2, 2.4, ('z', -45))):
        B(tc, x, y, z, w, h, w, 'cry', **(dict(rot=rot, rot_origin=[x, y, z]) if rot else {}),
          decals={'north': [('rect', 0.15, 0, 0.35, 1, '#ffffff')], 'east': [('shade', 0, 0, 1, 1, 0.8)]})
    hd = r.bone('head', [0, 17, -3.6], body)
    boulder(hd, 0, 14.6, -4.6, 6.4, 5.6, 5.4)                                            # head sunk between shoulders
    B(hd, 0, 18.2, -7.0, 6.8, 1.6, 1.4, 'rock_l')                                         # heavy brow
    for sx in (1, -1):
        B(hd, sx * 1.6, 17.0, -7.35, 2.0, 1.0, 0.2, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 1.6, 17.5, -7.35])   # angry glowing eyes
    B(hd, 0, 14.6, -7.1, 5.8, 1.8, 1.0, 'rock_d', decals={'north': pix(["k.k.k.k", "......."], {'k': '#3a3430'})})   # jaw with crack-teeth
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.6
        a = r.bone('arm_' + side, [x, 19, 1], body)
        boulder(a, x, 14.6, 1.0, 5.6, 5.6, 5.6, 'rock_l')                                  # shoulder boulder
        boulder(a, x + sx * 0.4, 8.6, 0.6, 4.6, 6.6, 4.6)                                  # upper arm
        boulder(a, x + sx * 0.6, 3.4, 0.2, 5.0, 5.8, 5.0, 'rock_d')                         # forearm
        boulder(a, x + sx * 0.6, -1.6, -0.2, 6.6, 5.6, 6.6)                                # huge fist (knuckles near the ground)
        B(a, x + sx * 0.6, 1.2, -3.55, 5.2, 0.5, 0.3, 'void')                              # finger cracks
    m.hitbox(*hb)
    shade_pass(m, ('rock',))
    mc_idle(m, 3.0, extra={'body': {'rotation': loop([[12, 0, 0], [14, 0, 0]], 3.0)}})
    mc_walk(m, 1.2, 18, extra={'body': {'rotation': loop([[14, 0, -3], [14, 0, 3]], 1.2)}})
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [-150, 0, 0]), (0.55, [-15, 0, 0]), (1.0, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    slam['body'] = {'rotation': [(0, [12, 0, 0]), (0.35, [0, 0, 0]), (0.55, [26, 0, 0]), (1.0, [12, 0, 0])]}
    m.anim('attack', 1.0, 'once', slam)
    common_tail(m)
    return m


def golem():
    return _rock_golem('clash_golem', 1.5, (2.4, 3.0))


def golemite():
    return _rock_golem('clash_golemite', 0.75, (1.2, 1.5))



def ice_golem():
    """HQ vanilla-like Ice Golem: lumpy snow body, ice-crystal mohawk, glowing icy eyes, black rock nose,
    big toothy underbite, huge ice-crystal forearms + fists, black rock feet, team-coloured ice core crystals on the back"""
    m = new_model('clash_ice_golem')
    m.mats_({'snow': ('#eef2f8', 'soft'), 'snow_d': ('#d0d8e6', 'soft'), 'ice': ('#78c8f0', 'gem'), 'ice_l': ('#b8e6ff', 'gem'),
             'coal': ('#2a2a30', 'stone'), 'eye': ('#70e0ff', 'glow'), 'tooth': ('#ffffff', 'bone'), 'cry': ('#f4f8ff', 'gem'), 'vest': ('#d8d8d8', 'stone')})
    r = Rig(m, 1.0); B = r.box
    def lump(bone, x, y, z, w, h, d, mat='snow'):
        B(bone, x, y + 0.8, z, w, h - 1.6, d, mat); B(bone, x, y, z, w - 1.6, h, d - 1.6, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = r.bone('leg_' + side, [x, 8, 0.6], root)
        lump(lg, x, 2.6, 0.6, 4.6, 5.6, 4.6)
        lump(lg, x, 0, 0.0, 5.2, 2.8, 6.0, 'coal')                                         # black rock feet
    body = r.bone('body', [0, 8, 0], root)
    lump(body, 0, 7.4, 1.0, 10.0, 5.6, 7.4, 'snow_d')                                     # hips
    lump(body, 0, 12.0, 0.4, 15.0, 8.4, 9.6)                                              # big chest
    lump(body, 0, 19.6, 2.4, 10.0, 3.4, 6.0, 'snow_d')                                    # hunched back
    tc = r.bone('tc_core', [0, 16, 0], body)                                              # team-coloured fur vest over the chest
    fur = [('rect', 0, 0.85, 1, 1, '#b8b8b8')] + [('px', i / 8, 0.95, '#ffffff') for i in range(0, 8, 2)]
    B(tc, 0, 11.4, 5.3, 15.4, 9.0, 0.8, 'vest', decals={'south': fur})                     # back panel
    for sx in (1, -1):
        B(tc, sx * 7.7, 11.4, 0.4, 0.8, 9.0, 9.6, 'vest', decals={'east': fur, 'west': fur})   # sides
        B(tc, sx * 5.0, 11.4, -4.5, 5.2, 9.0, 0.8, 'vest', decals={'north': fur})            # open front flaps
        B(tc, sx * 4.6, 20.2, 0.4, 5.6, 1.2, 10.4, 'vest')                                  # over the shoulders
    B(body, 0, 15.0, -4.95, 1.2, 1.2, 0.3, 'coal'); B(body, 0, 12.6, -4.95, 1.2, 1.2, 0.3, 'coal')   # toggles
    hd = r.bone('head', [0, 18, -3.6], body)
    lump(hd, 0, 15.6, -4.4, 7.0, 6.4, 5.8)                                               # head sunk between the shoulders
    for (x, z, h, w, rot) in ((0.0, -6.2, 4.6, 2.2, ('x', 22.5)), (-1.8, -5.6, 3.8, 1.8, ('z', 22.5)), (1.8, -5.6, 4.0, 1.8, ('z', -22.5)),
                              (0.0, -4.0, 5.4, 2.4, None), (-2.0, -3.4, 4.2, 2.0, ('z', 22.5)), (2.0, -3.4, 4.4, 2.0, ('z', -22.5)),
                              (0.0, -1.8, 4.8, 2.2, ('x', -22.5)), (-1.4, -2.4, 3.0, 1.4, ('z', 45)), (1.4, -2.4, 3.2, 1.4, ('z', -45))):
        B(hd, x, 21.4, z, w, h, w, 'ice', **(dict(rot=rot, rot_origin=[x, 21.4, z]) if rot else {}),
          decals={'north': [('rect', 0.15, 0, 0.35, 1, '#d8f4ff')], 'east': [('shade', 0, 0, 1, 1, 0.85)]})   # ice-crystal hair
    for sx in (1, -1):
        B(hd, sx * 1.8, 19.4, -7.4, 1.8, 0.7, 0.2, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 1.8, 19.75, -7.4])   # icy glowing eyes
        B(hd, sx * 1.8, 20.2, -7.5, 2.4, 0.8, 0.6, 'snow_d')                               # brows
    B(hd, 0, 17.6, -7.8, 2.0, 2.0, 1.2, 'coal')                                           # black rock nose
    B(hd, 0, 15.0, -7.6, 6.4, 2.4, 1.6, 'snow', decals={'north': pix(["t.t.t.t", "ttttttt", "......."], {'t': '#ffffff'})})   # underbite with teeth
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.8
        a = r.bone('arm_' + side, [x, 19, 1], body)
        lump(a, x, 14.4, 1.0, 5.6, 5.6, 5.6)                                               # snow shoulder
        lump(a, x + sx * 0.3, 9.4, 0.6, 4.4, 5.6, 4.4, 'snow_d')                            # upper arm
        B(a, x + sx * 0.6, 2.6, 0.2, 5.6, 7.4, 5.6, 'ice', decals={f: [('rect', 0.2, 0, 0.3, 1, '#b8e6ff'), ('rect', 0.6, 0.3, 0.68, 1, '#5aa8d8')] for f in ('north', 'south', 'east', 'west')})   # ice forearm
        B(a, x + sx * 0.6, -1.4, -0.4, 6.8, 4.6, 6.8, 'ice')                                # big ice fist
        for dz in (-2.4, -0.8, 0.8, 2.4):
            B(a, x + sx * 0.6, -2.2, -3.8 + (dz + 2.4) * 0 + 0, 1.4, 1.6, 1.4, 'ice_l') if False else None
        for dx in (-2.2, -0.7, 0.8, 2.3):
            B(a, x + sx * 0.6 + dx, -2.0, -4.0, 1.3, 2.0, 1.2, 'ice_l')                     # crystal knuckles
        B(a, x + sx * 0.6, 7.6, 2.6, 2.0, 2.6, 1.4, 'ice_l', rot=('x', -22.5), rot_origin=[x, 7.6, 2.6])   # crystal shard on the back of the arm
    m.hitbox(1.6, 2.2)
    shade_pass(m, ('snow',))
    mc_idle(m, 2.4, extra={'body': {'rotation': loop([[12, 0, 0], [14, 0, 0]], 2.4)}})
    mc_walk(m, 1.0, 20, extra={'body': {'rotation': loop([[14, 0, -3], [14, 0, 3]], 1.0)}})
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [-150, 0, 0]), (0.55, [-15, 0, 0]), (1.0, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    m.anim('attack', 1.0, 'once', slam)
    common_tail(m)
    return m



def fine_sword(m, bone, x, y, z, L=10.0, gold='gold', grip='grip', k=1.0):
    """detailed sword held at (x,y,z), blade pointing -Z: wrapped grip, round pommel, curved cross-guard,
    blade with bevelled edges + central fuller + tapered tip"""
    _cb = globals()['cb']
    def cb(b, cx, cy, cz, w, h, d, mat, **kw):                                         # scale about the grip point
        return _cb(b, x + (cx - x) * k, y + (cy - y) * k, z + (cz - z) * k, w * k, h * k, d * k, mat, **kw)
    m.mats_({'blade': ('#c8d0d8', 'metal'), 'blade_l': ('#eef2f6', 'metal'), 'blade_d': ('#8a929c', 'metal')})
    wrap = [('rect', 0, k, 1, k + 0.12, '#3a2410') for k in (0.1, 0.4, 0.7)]
    cb(bone, x, y - 0.45, z + 0.4, 0.9, 0.9, 3.2, grip, decals={f: wrap for f in ('up', 'down', 'east', 'west')})   # wrapped grip
    cb(bone, x, y - 0.65, z + 2.4, 1.3, 1.3, 1.0, gold)                                     # pommel
    cb(bone, x, y - 0.4, z + 3.0, 0.8, 0.8, 0.4, gold)
    cb(bone, x, y - 0.5, z - 1.5, 1.0, 1.0, 0.8, gold)                                      # guard centre
    cb(bone, x, y - 2.3, z - 1.5, 0.9, 4.6, 0.7, gold)                                      # cross-guard (across the blade)
    for sx in (1, -1):
        cb(bone, x, y + sx * 2.3 - 0.45, z - 1.9, 0.9, 0.7, 1.0, gold)                         # curled guard tips
    side = [('rect', 0, 0.42, 0.85, 0.58, '#8a929c'), ('rect', 0, 0, 1, 0.14, '#eef2f6'), ('rect', 0, 0.86, 1, 1, '#eef2f6')]
    cb(bone, x, y - 1.2, z - 1.9 - L / 2, 0.6, 2.4, L, 'blade', decals={'east': side, 'west': side})   # broad blade + fuller + bright edges
    cb(bone, x, y - 0.8, z - 1.9 - L - 0.7, 0.5, 1.6, 1.4, 'blade_l')                        # tapering tip
    cb(bone, x, y - 0.4, z - 1.9 - L - 1.7, 0.4, 0.8, 0.8, 'blade_l')


def knight():
    """HQ vanilla-like Knight: chainmail coif, blond curled moustache + brows, big nose, steel breastplate,
    team sash + team belt with gold buckle, chainmail skirt/sleeves, brown boots, fine sword"""
    m = new_model('clash_knight')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'mail': ('#8a929a', 'metal'), 'plate': ('#c8d0d8', 'metal'),
             'plate_d': ('#9aa4ae', 'metal'), 'hair': ('#f0c838', 'hair'), 'tc': ('#efefef', 'cloth'), 'gold': ('#e8b830', 'metal'),
             'boot': ('#6a4426', 'leather'), 'grip': ('#6a4426', 'leather'), 'eye': ('#ffffff', 'plain'), 'iris': ('#3a6aa8', 'plain')})
    scale = [('px', i / 8, j / 8, '#5a626a') for i in range(0, 8, 2) for j in range(0, 8, 2)] + [('px', i / 8, j / 8, '#b0b8c0') for i in range(1, 8, 2) for j in range(1, 8, 2)]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 10, 0], root)
        cb(lg, sx * 2, 1.6, 0, 3.6, 8.4, 3.6, 'skin')
        cb(lg, sx * 2, 0, -0.4, 4.2, 2.2, 5.0, 'boot', decals={'up': [('rect', 0.2, 0.5, 0.8, 0.7, '#9aa4ae')]})
    body = m.bone('body', [0, 10, 0], root)
    cb(body, 0, 7.4, 0, 9.0, 5.2, 5.0, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # chainmail skirt
    cb(body, 0, 12.0, 0, 9.4, 9.0, 5.4, 'plate', decals={'north': [('rect', 0.48, 0, 0.52, 1, '#9aa4ae'), ('shade', 0, 0.8, 1, 1, 0.85)]})   # breastplate
    cb(body, 0, 19.6, 0, 8.0, 1.2, 4.6, 'plate_d')                                          # gorget
    tc = m.bone('tc_surcoat', [0, 14, 0], body)
    cb(tc, 0, 11.6, 0, 9.8, 2.0, 5.8, 'tc')                                                  # team belt
    cb(tc, 0, 14.6, -2.85, 10.6, 1.8, 0.3, 'tc', rot=('z', -45), rot_origin=[0, 15.5, -2.85])   # team sash across the chest
    cb(tc, 0, 14.6, 2.85, 10.6, 1.8, 0.3, 'tc', rot=('z', 45), rot_origin=[0, 15.5, 2.85])
    cb(body, 2.0, 11.4, -2.95, 2.6, 2.4, 0.3, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#3a6ae0')]})   # gold buckle
    hd = m.bone('head', [0, 20.6, 0], body)
    cb(hd, 0, 20.6, 0, 7.0, 7.0, 7.0, 'skin', decals={'north': pix([".......", ".......", ".......", ".we.ew.", ".......", ".......", "......."], {'w': '#ffffff', 'e': '#3a6aa8'})})
    cb(hd, 0, 23.0, -3.9, 1.4, 1.8, 1.0, 'skin_d')                                          # big nose
    hr = m.bone('hair', [0, 21, 0], hd)
    cb(hr, 0, 20.4, 0.3, 7.6, 7.8, 7.4, 'mail', decals={'north': [('rect', 0.12, 0.05, 0.88, 0.95, '#00000000')] if False else scale, 'east': scale, 'west': scale, 'south': scale, 'up': scale}, inflate=0)   # mail coif (front cut away below)
    cb(hr, 0, 20.4, -3.55, 6.0, 6.0, 0.2, 'skin')                                           # face opening
    for sx in (1, -1):
        cb(hr, sx * 1.6, 23.6, -3.7, 2.0, 1.0, 0.2, 'eye')                                     # eye white
        cb(hr, sx * 1.6, 23.6, -3.8, 0.8, 1.0, 0.2, 'iris')                                    # centred blue pupil
    for sx in (1, -1):
        cb(hr, sx * 1.7, 25.4, -3.9, 2.2, 0.8, 0.6, 'hair')                                   # blond brows
        cb(hr, sx * 1.3, 22.0, -4.0, 2.4, 0.9, 0.8, 'hair')                                   # moustache
        cb(hr, sx * 2.8, 21.6, -4.0, 0.9, 1.2, 0.8, 'hair'); cb(hr, sx * 3.3, 22.6, -4.0, 0.8, 0.9, 0.8, 'hair')   # curled tips
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5.6, 19.4, 0], body)
        cb(a, sx * 6.2, 15.4, 0, 3.6, 4.6, 3.6, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # mail sleeve
        cb(a, sx * 6.2, 18.2, 0, 4.2, 2.0, 4.6, 'plate_d')                                     # pauldron
        cb(a, sx * 6.2, 11.0, 0, 3.2, 4.6, 3.2, 'skin')
        cb(a, sx * 6.2, 9.4, -0.2, 3.4, 2.2, 3.4, 'skin_d')                                     # fist
    sw = m.bone('sword', [6.2, 10.4, 0], m.by_name('arm_r'))
    fine_sword(m, sw, 6.2, 10.6, 0.0, L=12.0, k=1.3)
    m.hitbox(0.9, 1.9)
    shade_pass(m, ('skin', 'plate'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-25, 0, 4], [-28, 0, 6]], 2.0)}})
    mc_walk(m, 0.8, 30, arm_r=False, extra={'arm_r': {'rotation': loop([[-25, 0, 4], [-35, 0, 4]], 0.8)}})
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-25, 0, 4]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, 0]), (0.6, [-25, 0, 4])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-6, 10, 0]), (0.35, [10, -10, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m)
    return m



def lava_hound():
    """HQ Lava Hound: glowing lava core sphere wrapped in separate dark rock plates (lava glows through the gaps),
    plated round head with horns + glowing eyes/mouth, bat wings with finger bones and lava-lit membranes,
    segmented clawed legs hanging down, plated tail"""
    import math, random
    rng = random.Random(4)
    m = new_model('clash_lava_hound')
    m.mats_({'rock': ('#3e3634', 'stone'), 'rock_l': ('#564c48', 'stone'), 'rock_d': ('#2a2422', 'stone'), 'lava': ('#ff7a14', 'glow'),
             'lava_y': ('#ffc040', 'glow'), 'eye': ('#ffd060', 'glow'), 'mem': ('#5a2418', 'leather', {'stitch': False})})

    def sphere_core(bone, c, R, mat='lava', n=7):
        h = 2 * R / n
        for i in range(n):
            yc = -R + h * (i + 0.5); rr = max(1.0, (R * R - yc * yc) ** 0.5)
            for rot in (None, ('y', 45)):
                kw = dict(rot=rot, rot_origin=[c[0], c[1] + yc, c[2]]) if rot else {}
                cb(bone, c[0], c[1] + yc - h / 2, c[2], 2 * rr, h, 0.83 * rr, mat, **kw)
                cb(bone, c[0], c[1] + yc - h / 2, c[2], 0.83 * rr, h, 2 * rr, mat, **kw)

    def plates(bone, c, R, n, size, skip=lambda d: False, sx=1.0, sy=1.0, sz=1.0):
        ga = math.pi * (3 - 5 ** 0.5)
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / n; r = (1 - y * y) ** 0.5; th = ga * i
            d = (math.cos(th) * r, y, math.sin(th) * r)
            if skip(d):
                continue
            ax = max(range(3), key=lambda k: abs(d[k]))
            s = size * rng.uniform(0.85, 1.1); t = 1.4
            dims = [s, s * rng.uniform(0.75, 1.0), s]; dims[ax] = t
            p = [c[0] + d[0] * (R - 0.7) * sx, c[1] + d[1] * (R - 0.7) * sy, c[2] + d[2] * (R - 0.7) * sz]
            mat = rng.choice(('rock', 'rock', 'rock_l', 'rock_d'))
            cb(bone, p[0], p[1] - dims[1] / 2, p[2], dims[0], dims[1], dims[2], mat,
               decals={'north': [('rect', 0.1, 0.1, 0.4, 0.3, '#665a54')], 'up': [('shade', 0, 0, 1, 1, 1.12)]})

    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 16, 2], root)
    BC, BR = (0, 16, 3), 9.0
    sphere_core(body, BC, BR - 1.2)
    plates(body, BC, BR, 70, 5.0)
    for (x, y, z, h) in ((-2.0, 24.6, 4.0, 2.6), (2.4, 25.0, 7.0, 2.2), (0.0, 24.4, 0.0, 2.0)):
        cb(body, x, y, z, 2.0, h, 2.0, 'rock_l')                                           # back spikes
    nk = m.bone('neck', [0, 17, -6], body)
    hd = m.bone('head', [0, 17, -9], nk)
    HC, HR = (0, 17, -11.5), 6.0
    sphere_core(hd, HC, HR - 1.0, n=5)
    plates(hd, HC, HR, 26, 4.2, skip=lambda d: d[2] < -0.55 and abs(d[1]) < 0.5)
    cb(hd, 0, 13.4, -16.4, 9.0, 6.6, 2.0, 'rock', decals={'north': [('rect', 0.1, 0.05, 0.9, 0.12, '#2a2422')]})   # face plate
    cb(hd, 0, 20.2, -16.8, 9.4, 1.6, 2.6, 'rock_l')                                        # heavy brow
    cb(hd, 0, 21.6, -14.0, 2.4, 2.4, 2.4, 'rock_l')                                        # forehead knob
    for sx in (1, -1):
        cb(hd, sx * 2.4, 17.8, -17.45, 2.8, 1.6, 0.3, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 2.4, 18.6, -17.45])   # glowing eyes
        cb(hd, sx * 2.4, 17.4, -17.3, 3.6, 2.6, 0.2, 'lava')                                # glow around the eyes
        h1 = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 4.4, 20.5, -12], hd)
        cb(h1, sx * 5.0, 20.0, -12.0, 2.6, 2.6, 2.6, 'rock_l')
        h2 = m.bone('horn2_' + ('r' if sx > 0 else 'l'), [sx * 5.6, 22.5, -12], h1)
        cb(h2, sx * 5.8, 22.4, -11.4, 1.6, 2.0, 1.6, 'rock'); cb(h2, sx * 6.0, 24.2, -10.8, 0.9, 1.2, 0.9, 'rock_d')
    mw = m.bone('maw', [0, 14, -17], hd)
    cb(mw, 0, 14.0, -17.5, 6.4, 1.0, 0.3, 'lava_y')                                        # glowing mouth seam
    jw = m.bone('jaw', [0, 14, -12], hd)
    cb(jw, 0, 11.0, -14.4, 8.0, 3.0, 5.6, 'rock', decals={'north': pix(["k.k.k.k"], {'k': '#ff7a14'})})
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 4.0, 27.0, 3.0], body)
        ro = dict(rot=('z', -sx * 45), rot_origin=[sx * 4.0, 27.0, 3.0])
        cb(w, sx * 10.0, 26.0, 3.0, 12.0, 2.2, 2.2, 'rock', **ro)                              # wing arm
        cb(w, sx * 4.6, 25.6, 3.0, 2.6, 2.6, 2.6, 'rock_l')                                   # shoulder joint
        w2 = m.bone('wing_' + side + '2', [sx * 4.0, 27.0, 3.0], w)
        for k, (zz, L) in enumerate(((3.6, 9.0), (7.0, 8.0), (10.0, 6.0))):                   # finger bones fanning back
            cb(w2, sx * 13.6, 26.6, 3.0 + zz / 2, 1.0, 1.0, zz + 1, 'rock_d', **ro)
        cb(w2, sx * 10.4, 26.6, 7.6, 12.0, 0.5, 11.0, 'mem',
           decals={f: [('lerp', '#ff6a14', 0.1, 0.9, 'y'), ('rect', 0.0, 0.48, 1, 0.52, '#3a1a10')] for f in ('up', 'down')}, **ro)   # lava-lit membrane
        wt = m.bone('wingtip_' + side, [sx * 14, 24, 3], w)
        cb(wt, sx * 14.6, 26.0, 2.6, 2.4, 2.4, 2.4, 'rock', **ro); cb(wt, sx * 15.2, 28.0, 1.6, 0.8, 1.8, 0.8, 'rock_d', **ro)   # wrist claw
    for (n, x, z) in (('leg_fr', 4.2, -3.0), ('leg_fl', -4.2, -3.0), ('leg_br', 5.0, 8.0), ('leg_bl', -5.0, 8.0)):
        lg = m.bone(n, [x, 10, z], body)
        cb(lg, x, 6.8, z, 3.0, 3.6, 3.0, 'rock', decals={f: [('rect', 0, 0.45, 1, 0.55, '#ff7a14')] for f in ('north', 'south', 'east', 'west')})
        cb(lg, x, 4.4, z, 2.2, 2.4, 2.2, 'rock_l')
        cb(lg, x, 3.4, z - 0.4, 2.8, 1.0, 2.8, 'rock_d')
        for dx in (-0.9, 0.0, 0.9):
            cb(lg, x + dx, 2.4, z - 1.6, 0.6, 1.2, 0.8, 'rock_d')                              # claws
    t1 = m.bone('tail', [0, 12, 11], body)
    cb(t1, 0, 10.6, 12.8, 4.0, 4.0, 4.0, 'rock', decals={f: [('rect', 0, 0.45, 1, 0.55, '#ff7a14')] for f in ('east', 'west', 'up')})
    t2 = m.bone('tail2', [0, 11.4, 14.8], t1); cb(t2, 0, 10.2, 16.0, 3.0, 3.0, 3.0, 'rock_l')
    t3 = m.bone('tail3', [0, 11, 17.4], t2); cb(t3, 0, 10.0, 18.6, 1.8, 1.8, 2.6, 'rock_d'); cb(t3, 0, 11.6, 18.6, 0.8, 1.4, 0.8, 'rock_d')
    m.hitbox(2.2, 2.4)
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, 0, -a], [0, 0, a * 0.5]], L)}, 'wing_l': {'rotation': loop([[0, 0, a], [0, 0, -a * 0.5]], L)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.4, 0]], 2.0)}, 'tail': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 2.0)}}
    idle.update(flap(0.6, 30))
    m.anim('idle', 2.0, 'loop', idle)
    walk = dict(idle); walk.update(flap(0.4, 40)); walk['body'] = {'rotation': loop([[8, 0, 0], [8, 0, 0]], 0.6)}
    m.anim('walk', 0.6, 'loop', walk)
    m.anim('attack', 1.3, 'once', {'head': {'rotation': [(0, [0, 0, 0]), (0.4, [-15, 0, 0]), (0.6, [12, 0, 0]), (1.3, [0, 0, 0])]},
                                   'jaw': {'rotation': [(0, [0, 0, 0]), (0.5, [25, 0, 0]), (0.8, [25, 0, 0]), (1.3, [0, 0, 0])]}})
    common_tail(m)
    return m


def miner():
    """HQ vanilla-like Miner: dark mining helmet with brim + candle lamp, big grin, brown hair/sideburns,
    team sleeveless shirt, leather suspenders + belt with brass buckle, blue-ish trousers, boots, shovel"""
    m = new_model('clash_miner')
    m.mats_({'skin': ('#e8a878', 'skin'), 'skin_d': ('#c88a5e', 'skin'), 'hair': ('#6a3a1e', 'hair'), 'helm': ('#3a4048', 'metal'),
             'helm_l': ('#5a626c', 'metal'), 'wax': ('#f0e6c8', 'bone'), 'flame': ('#ffc040', 'glow'), 'tc': ('#efefef', 'cloth'),
             'strap': ('#6a4224', 'leather'), 'brass': ('#c89a40', 'metal'), 'pants': ('#3a5aa8', 'cloth'), 'boot': ('#4a3020', 'leather'),
             'wood': ('#7a4a26', 'wood'), 'steel': ('#3a4048', 'metal'), 'steel_l': ('#6a727c', 'metal'), 'core': ('#fff8e0', 'glow'),
             'glowo': ('#ff9a30', 'glow'), 'sack': ('#8a6a44', 'cloth'), 'coal': ('#26262a', 'stone'), 'coal_l': ('#45454c', 'stone')})
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        tp = lg
        cb(tp, sx * 2, 2.4, 0, 4, 9.6, 4, 'pants', decals={'north': [('shade', 0, 0, 1, 1, 0.85)]})   # trousers (team, darker)
        cb(lg, sx * 2, 0, -0.3, 4.4, 2.8, 4.8, 'boot')
    body = m.bone('body', [0, 12, 0], root)
    tc = m.bone('tc_shirt', [0, 12, 0], body)
    cb(tc, 0, 12, 0, 8.4, 12, 4.4, 'tc')                                                   # team sleeveless shirt
    for sx in (1, -1):
        cb(body, sx * 2.6, 15.6, -2.3, 1.2, 8.4, 0.3, 'strap'); cb(body, sx * 2.6, 15.6, 2.3, 1.2, 8.4, 0.3, 'strap')   # suspenders
        cb(body, sx * 2.6, 23.6, 0, 1.2, 0.5, 4.8, 'strap')
    cb(body, 0, 12.4, 0, 8.8, 1.6, 4.8, 'strap'); cb(body, 1.6, 12.2, -2.5, 2.0, 2.0, 0.3, 'brass')   # belt + buckle
    cb(body, -3.2, 10.6, -1.8, 2.0, 2.4, 1.6, 'strap')                                       # pouch
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", "........", ".tttttt.", "..kkkk.."],
               {'k': '#4a2a14', 'w': '#ffffff', 'b': '#3a2a1a', 't': '#f8f6ee'})
    cb(hd, 0, 24, 0, 8, 8, 8, 'skin', decals={'north': face})
    cb(hd, 0, 27.0, -4.4, 1.6, 2.0, 1.0, 'skin_d')                                           # nose
    for sx in (1, -1):
        cb(hd, sx * 4.15, 25.4, 0.4, 0.4, 3.4, 4.0, 'hair')                                   # sideburns
    cb(hd, 0, 26.6, 4.15, 8.2, 3.0, 0.4, 'hair')
    hm = m.bone('helmet', [0, 30, 0], hd)
    cb(hm, 0, 29.6, 0.2, 8.8, 3.4, 8.8, 'helm'); cb(hm, 0, 33.0, 0.2, 7.0, 0.8, 7.0, 'helm')   # domed helmet
    cb(hm, 0, 29.4, 0.2, 10.6, 0.6, 10.6, 'helm_l')                                          # wide brim
    cb(hm, 0, 30.4, -4.7, 3.4, 3.0, 0.8, 'brass')                                            # brass lamp plate
    cb(hm, 0, 31.4, -5.4, 2.4, 1.4, 1.0, 'brass')                                            # candle cup
    cb(hm, 0, 32.8, -5.4, 1.8, 1.8, 1.2, 'wax', decals={'north': [('rect', 0.2, 0.6, 0.45, 1, '#ffffff')]})   # candle
    cb(hm, 0.5, 32.0, -6.0, 0.6, 1.0, 0.4, 'wax')                                            # wax drip
    cb(hm, 0, 34.6, -5.4, 0.9, 1.2, 0.9, 'flame'); cb(hm, 0, 35.6, -5.4, 0.5, 0.8, 0.5, 'core')   # flame + hot tip
    cb(hm, 0, 34.4, -5.4, 1.6, 1.0, 1.6, 'glowo')                                            # glow halo
    for dx in (-3.2, 3.2):
        cb(hm, dx, 30.0, 0.2, 0.6, 0.6, 9.0, 'helm_l')                                       # helmet ribs
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5, 22, 0], body)
        sl = m.bone('tc_sleeve_' + side, [sx * 5, 22, 0], a)
        cb(sl, sx * 6, 21.0, 0, 4.2, 3.0, 4.2, 'tc')                                          # short sleeve
        cb(a, sx * 6, 12, 0, 4, 9, 4, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.7, '#c88a5e')]})   # big bare arms
        cb(a, sx * 6, 11.2, -0.2, 4.2, 2.2, 4.2, 'skin_d')                                      # fist
    sh = m.bone('pickaxe', [6, 12.4, 0], m.by_name('arm_r'))                                  # shovel (kept bone name), held upright
    wood = [('rect', 0, k, 1, k + 0.05, '#5a3418') for k in (0.25, 0.6)]
    cb(sh, 6, 8.0, -3.0, 1.0, 22.0, 1.0, 'wood', decals={f: wood for f in ('north', 'south', 'east', 'west')})   # long handle
    cb(sh, 6, 7.2, -3.0, 2.0, 0.8, 1.2, 'wood'); cb(sh, 6, 6.4, -3.0, 2.6, 0.8, 1.2, 'wood')   # D-grip end
    cb(sh, 6, 29.6, -3.0, 1.4, 2.4, 1.4, 'steel')                                            # socket
    cb(sh, 6, 29.0, -3.0, 1.8, 0.6, 1.6, 'steel_l')                                          # rivet band
    cb(sh, 6, 31.6, -3.0, 7.0, 7.0, 0.6, 'steel',                                            # spade blade, face forward
       decals={'north': [('rect', 0, 0, 0.12, 1, '#6a727c'), ('rect', 0.88, 0, 1, 1, '#6a727c'), ('rect', 0.45, 0.1, 0.55, 0.8, '#2a3038')]})
    cb(sh, 6, 38.6, -3.0, 5.0, 1.4, 0.6, 'steel'); cb(sh, 6, 40.0, -3.0, 2.6, 1.2, 0.6, 'steel_l')   # pointed tip
    # backpack: canvas sack with leather straps, full of mined coal
    bp = m.bone('backpack', [0, 18, 2.4], body)
    cb(bp, 0, 13.0, 4.6, 7.0, 9.0, 4.2, 'sack', decals={'south': [('rect', 0.1, 0.3, 0.9, 0.36, '#6a4a2a'), ('rect', 0.45, 0.36, 0.55, 0.6, '#c89a40')]})
    cb(bp, 0, 21.6, 4.6, 6.4, 0.8, 3.6, 'strap')                                             # drawstring rim
    for (x, y, z, w) in ((-2.0, 22.2, 4.0, 2.2), (0.4, 22.6, 5.4, 2.6), (2.2, 22.0, 3.8, 2.0), (-0.6, 24.0, 4.6, 1.8), (1.4, 23.6, 4.4, 1.4)):
        cb(bp, x, y, z, w, w * 0.9, w, 'coal' if w > 1.9 else 'coal_l', decals={'up': [('rect', 0.2, 0.2, 0.45, 0.45, '#5a5a62')]})   # heaped coal lumps
    for sx in (1, -1):
        cb(bp, sx * 2.6, 13.6, 2.6, 1.2, 0.8, 0.8, 'strap')                                     # straps to the suspenders
    m.hitbox(0.9, 2.1)
    shade_pass(m, ('skin', 'tc'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-20, 0, 4], [-22, 0, 6]], 2.0)}})
    mc_walk(m, 0.75, 32, arm_r=False, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-40, 0, 4]], 0.75)}})
    m.anim('attack', 0.65, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 4]), (0.25, [-160, 0, 10]), (0.4, [-10, 0, 0]), (0.65, [-30, 0, 4])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-8, 10, 0]), (0.4, [12, -8, 0]), (0.65, [0, 0, 0])]}})
    m.anim('deploy', 0.9, 'once', {'root': {'position': [(0, [0, -30, 0]), (0.5, [0, 3, 0]), (0.7, [0, 0, 0]), (0.9, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'body': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', {'root': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])], 'position': [(0, [0, 0, 0]), (0.9, [0, -8, 0])]}})
    return m



def minion():
    """HQ Minion (from the Sketchfab reference): pear-shaped body, head pushed forward with a long snout + wide grin,
    big side eyes, horns rising from the back of the skull with dark ring bases, small bat wings high on the back,
    long arms in ragged team sleeves (forearm + hand) with claws poking out, short legs with 2-toe feet, little tail"""
    m = new_model('clash_minion')
    m.mats_({'skin': ('#4a9ae0', 'skin'), 'skin_d': ('#2e6ab8', 'skin'), 'skin_l': ('#78c0f4', 'skin'), 'horn': ('#2a4a98', 'skin'),
             'wing': ('#3a78d0', 'leather', {'stitch': False}), 'rib': ('#1e3470', 'leather'), 'mitt': ('#e6e0f0', 'cloth'),
             'claw': ('#5aa0e8', 'bone'), 'eye': ('#ffffff', 'plain'), 'iris': ('#c02a8a', 'plain'), 'pupil': ('#1a0a1a', 'plain'),
             'mouth': ('#14203a', 'plain'), 'tooth': ('#f4f8ff', 'bone')})
    spk = [('px', 0.2, 0.3, '#6a6ac8'), ('px', 0.7, 0.75, '#6a6ac8')]
    def rb(b, x, y, z, w, h, d, mat, r=0.6, **kw):
        cb(b, x, y + r, z, w, h - 2 * r, d, mat, **kw); cb(b, x, y, z, w - 2 * r, h, d - 2 * r, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.5, 5, 0.6], root)
        rb(lg, sx * 1.5, 2.2, 0.6, 2.2, 3.0, 2.4, 'skin')
        cb(lg, sx * 1.5, 0.6, 0.8, 1.6, 1.8, 1.8, 'skin')
        for dx in (-0.45, 0.45):
            cb(lg, sx * 1.5 + dx, 0, -0.4, 0.8, 0.9, 2.4, 'skin_d')                          # two toes
    body = m.bone('body', [0, 5, 0], root)
    rb(body, 0, 4.4, 0.6, 5.8, 4.6, 4.8, 'skin', r=0.8, decals={'north': [('rect', 0.2, 0, 0.8, 1, '#78c0f4')] + spk, 'south': spk})   # round belly
    rb(body, 0, 8.4, 0.2, 6.4, 3.6, 4.4, 'skin', decals={'north': spk, 'south': spk})        # chest
    cb(body, 0, 11.4, 0.0, 7.4, 1.6, 4.0, 'skin')                                           # shoulders
    tl = m.bone('tail', [0, 5, 3], body)
    cb(tl, 0, 5.0, 3.4, 1.0, 1.6, 1.4, 'skin'); cb(tl, 0, 4.2, 4.0, 0.7, 1.0, 0.9, 'skin_d')
    hd = m.bone('head', [0, 12.4, -1.0], body)
    rb(hd, 0, 12.2, -0.6, 6.0, 5.4, 5.6, 'skin', r=0.8)                                     # skull
    rb(hd, 0, 12.4, -3.6, 4.6, 3.2, 2.4, 'skin', r=0.5)                                     # short snout
    cb(hd, 0, 14.2, -4.9, 2.4, 1.0, 0.6, 'skin_l', decals={'north': pix(["k..k"], {'k': '#14203a'})})   # nose + nostrils
    cb(hd, 0, 13.0, -4.85, 3.6, 0.5, 0.2, 'mouth')                                          # wide grin (front)
    for sx in (1, -1):
        cb(hd, sx * 2.35, 12.9, -3.8, 0.2, 0.5, 2.0, 'mouth')                               # grin runs along the sides
        cb(hd, sx * 2.45, 13.4, -3.6, 0.2, 0.5, 0.5, 'tooth')
        cb(hd, sx * 2.6, 15.0, -2.4, 1.0, 2.0, 2.0, 'eye')                                  # big eyes on the sides of the head
        cb(hd, sx * 2.7, 15.2, -3.0, 0.9, 1.4, 1.0, 'iris'); cb(hd, sx * 2.75, 15.5, -3.2, 0.9, 0.8, 0.5, 'pupil')
        cb(hd, sx * 2.4, 17.0, -2.4, 1.6, 0.5, 2.6, 'skin_d', rot=('z', sx * 22.5), rot_origin=[sx * 2.4, 17.2, -2.4])   # brow ridge
        h = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 17.4, 0.6], hd)
        cb(h, sx * 1.9, 17.2, 0.6, 2.2, 0.8, 2.2, 'skin_d')                                  # dark ring base
        cb(h, sx * 1.9, 18.0, 0.6, 1.8, 2.4, 1.8, 'horn')                                   # straight horn base
        cb(h, sx * 2.1, 20.4, 0.8, 1.3, 2.0, 1.3, 'horn')
        cb(h, sx * 2.3, 22.4, 1.0, 0.8, 1.4, 0.8, 'horn')                                   # tapering tip, slight outward lean
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 3.4, 11.6, 0], body)
        cb(a, sx * 4.3, 7.6, 0, 1.9, 4.4, 1.9, 'skin', decals={'north': spk})                  # long upper arm
        tc = m.bone('tc_mitt_' + side, [sx * 4.4, 7.6, 0], a)
        rb(tc, sx * 4.5, 2.4, -0.4, 3.4, 5.6, 3.6, 'mitt', r=0.5,
           decals={'north': [('rect', 0, 0, 1, 0.12, '#c8c0d8')], 'south': [('rect', 0, 0, 1, 0.12, '#c8c0d8')]})   # ragged sleeve over forearm + hand
        for (dx, dz) in ((-1.0, -1.6), (0.9, 1.4), (1.2, -1.2)):
            cb(tc, sx * 4.5 + dx, 7.8, dz, 1.0, 0.7, 1.0, 'mitt')                             # torn top edge
        for dx in (-1.1, -0.1, 0.9):
            cb(a, sx * 4.5 + dx, 1.0, -1.6, 0.7, 1.8, 0.8, 'claw')                             # claws poking out the bottom
        cb(a, sx * 4.5 - sx * 1.6, 2.4, -1.2, 0.7, 1.4, 0.7, 'claw')                          # thumb claw
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 1.6, 12.0, 2.6], body)                              # wings high on the back, spread up/out
        ro = dict(rot=('z', sx * 45), rot_origin=[sx * 1.6, 12.0, 2.6])
        cb(w, sx * 5.6, 12.0, 2.8, 8.0, 1.0, 1.0, 'rib', **ro)                                  # leading edge bone
        for (x0, x1, h) in ((1.6, 4.4, 4.4), (4.4, 7.2, 5.2), (7.2, 9.6, 4.0)):
            cb(w, sx * (x0 + x1) / 2, 12.2 - h, 2.9, x1 - x0, h, 0.3, 'wing',
               decals={f: [('lerp', '#2a5ab0', 0.0, 0.7, 'y'), ('rect', 0.85, 0, 1, 1, '#1e3470'), ('rect', 0, 0.88, 1, 1, '#1e3470')] for f in ('north', 'south')}, **ro)
        cb(w, sx * 9.8, 11.4, 2.8, 0.8, 1.6, 0.8, 'rib', **ro)
    m.bone('tc_bandana', [0, 13, 0], body)
    m.hitbox(0.6, 1.2)
    shade_pass(m, ('skin',))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -12, -a], [0, 12, a * 0.5]], L)}, 'wing_l': {'rotation': loop([[0, 12, a], [0, -12, -a * 0.5]], L)}}
    hang = {'arm_r': {'rotation': loop([[-20, 0, 18], [-24, 0, 20]], 0.64)}, 'arm_l': {'rotation': loop([[-20, 0, -18], [-24, 0, -20]], 0.64)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.64)}, 'tail': {'rotation': loop([[0, 15, 0], [0, -15, 0]], 0.64)},
            'body': {'rotation': loop([[12, 0, 0], [12, 0, 0]], 0.64)}, 'head': {'rotation': loop([[-10, 0, 0], [-10, 0, 0]], 0.64)}}
    idle.update(flap(0.32, 40)); idle.update(hang)
    m.anim('idle', 0.64, 'loop', idle)
    walk = dict(idle); walk['body'] = {'rotation': loop([[25, 0, 0], [25, 0, 0]], 0.32)}; walk['head'] = {'rotation': loop([[-20, 0, 0], [-20, 0, 0]], 0.32)}
    walk.update(flap(0.16, 45)); walk['root'] = {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.32)}
    m.anim('walk', 0.32, 'loop', walk)
    m.anim('attack', 0.5, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 18]), (0.15, [-130, 0, 10]), (0.3, [-30, 0, 0]), (0.5, [-20, 0, 18])]},
                                   'body': {'rotation': [(0, [12, 0, 0]), (0.15, [0, 10, 0]), (0.3, [25, -10, 0]), (0.5, [12, 0, 0])]}})
    common_tail(m)
    return m


def mega_minion():
    """Mega Minion as in the reference: tall rounded bucket helm with a wide visor slot split by a centre bar and glowing
    eyes inside, big crystal horns sweeping out then up, small crystal bat wings spread above the shoulders, round
    breastplate, huge rounded pauldrons with mauve inlays, mauve belt, team cloth skirt tabs + elbow sleeves, big
    spread-finger gauntlets, thin legs with talon feet. Horns/eyes/wings = soft team colour, cloth = team colour."""
    m = new_model('clash_mega_minion')
    m.mats_({'steel': ('#a8b0b8', 'metal'), 'steel_d': ('#7a828c', 'metal'), 'steel_l': ('#ccd2d8', 'metal'), 'mauve': ('#9a8494', 'metal'),
             'mail': ('#7a828c', 'metal'), 'tc': ('#efefef', 'cloth'), 'soft': ('#f4f4f4', 'gem'), 'void': ('#10141c', 'plain'),
             'leg': ('#4a6ab8', 'skin'), 'claw': ('#c4ccd4', 'metal')})
    mail = [('px', i / 6, j / 6, '#4a525c') for i in range(0, 6, 2) for j in range(0, 6, 2)]
    def rb(b, x, y, z, w, h, d, mat, r=0.7, **kw):
        cb(b, x, y + r, z, w, h - 2 * r, d, mat, **kw); cb(b, x, y, z, w - 2 * r, h, d - 2 * r, mat); cb(b, x, y + r * 0.5, z, w - r, h - r, d + 0.02, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.6, 6, 0.6], root)
        cb(lg, sx * 1.6, 2.4, 0.6, 1.4, 3.8, 1.4, 'leg')                                       # thin legs
        cb(lg, sx * 1.6, 1.2, 0.6, 1.8, 1.4, 1.8, 'leg')
        for dx in (-0.5, 0.5):
            cb(lg, sx * 1.6 + dx, 0, -0.2, 0.7, 1.4, 1.8, 'claw')                                # talon toes
        cb(lg, sx * 1.6, 0.2, 1.6, 0.6, 1.0, 1.0, 'claw')
    body = m.bone('body', [0, 6, 0], root)
    tc = m.bone('tc_loin', [0, 8, 0], body)
    for x in (-2.4, 0.0, 2.4):
        cb(tc, x, 4.6, -2.8, 2.2, 3.4, 0.4, 'tc'); cb(tc, x, 4.8, 3.6, 2.2, 3.2, 0.4, 'tc')        # cloth skirt tabs
    cb(body, 0, 5.4, 0.4, 7.6, 2.8, 5.6, 'mail', decals={f: mail for f in ('north', 'south', 'east', 'west')})
    cb(body, 0, 7.8, 0.4, 9.2, 1.6, 6.6, 'mauve', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.8, '#c8b8c4')]})   # mauve belt
    rb(body, 0, 9.2, 0.4, 9.6, 7.4, 7.0, 'steel', decals={'north': [('rect', 0.47, 0, 0.53, 1, '#ccd2d8'), ('shade', 0, 0.7, 1, 1, 0.85)]})   # round breastplate
    for sx in (1, -1):
        rb(body, sx * 6.4, 12.8, 0.4, 5.6, 4.6, 7.8, 'steel', r=1.0)                              # huge round pauldron
        cb(body, sx * 6.4, 13.6, -3.55, 3.8, 2.6, 0.4, 'mauve'); cb(body, sx * 9.25, 13.6, 0.4, 0.4, 2.6, 5.4, 'mauve')   # mauve inlays
        cb(body, sx * 6.4, 17.2, 0.4, 4.0, 0.6, 6.0, 'steel_l')
    hd = m.bone('head', [0, 16.6, -0.4], body)
    hm = m.bone('helmet', [0, 16.6, -0.4], hd)
    rb(hm, 0, 15.8, 0.0, 7.6, 7.6, 7.0, 'steel', r=0.9)                                     # helm shell
    rb(hm, 0, 22.6, 0.0, 6.2, 1.8, 5.8, 'steel', r=0.6)                                      # rounded dome
    cb(hm, 0, 24.2, 0.0, 1.0, 0.6, 5.0, 'steel_l')                                          # crest ridge
    # shield-shaped faceplate: wide at the brow, narrowing to the chin
    for (y, w) in ((21.0, 7.6), (19.6, 7.4), (18.2, 6.8), (16.8, 6.0), (15.6, 4.8), (14.8, 3.2)):
        cb(hm, 0, y, -3.9, w, 1.4 if y > 15 else 0.8, 1.0, 'steel', decals={'north': [('shade', 0, 0, 1, 1, 0.95)]})
    for sx in (1, -1):
        cb(hm, sx * 1.9, 20.9, -4.55, 3.6, 0.9, 0.6, 'steel_l', rot=('z', sx * 22.5), rot_origin=[sx * 1.9, 21.35, -4.55])   # angry V brow
    cb(hm, 0, 19.0, -4.45, 6.2, 1.5, 0.2, 'void')                                           # eye slit
    ey = m.bone('ts_eyes', [0, 19, -4], hm)
    for sx in (1, -1):
        cb(ey, sx * 1.7, 19.2, -4.5, 1.8, 1.0, 0.2, 'soft')                                   # glowing eyes in the slit
    cb(hm, 0, 15.2, -4.5, 1.2, 4.6, 0.8, 'steel_l')                                         # centre nose ridge
    for x in (-2.0, -1.2, 1.2, 2.0):
        cb(hm, x, 15.8, -4.45, 0.5, 2.2, 0.2, 'void')                                         # breathing slits
    for sx in (1, -1):
        cb(hm, sx * 3.9, 15.4, -1.4, 0.6, 5.0, 4.4, 'steel_d')                                # cheek guards
        for (y, z) in ((20.4, -2.0), (16.6, -2.0)):
            cb(hm, sx * 4.25, y, z, 0.3, 0.7, 0.7, 'steel_l')                                   # side rivets
    for x in (-3.0, 3.0):
        cb(hm, x, 17.0, -4.5, 0.6, 0.6, 0.3, 'steel_l')                                        # faceplate rivets
    hn = m.bone('ts_horns', [0, 23, 0], hm)
    for sx in (1, -1):
        for (dx, dy, dz, w, h) in ((4.0, 22.0, -0.2, 2.4, 2.0), (5.4, 22.8, -0.2, 2.2, 2.0), (6.4, 24.2, 0.0, 1.9, 2.2),
                                   (6.8, 26.2, 0.2, 1.6, 2.2), (6.8, 28.2, 0.6, 1.2, 2.0), (6.4, 30.0, 1.0, 0.8, 1.4)):
            cb(hn, sx * dx, dy, dz, w, h, w, 'soft', decals={'north': [('rect', 0.15, 0, 0.4, 1, '#ffffff')], 'east': [('shade', 0, 0, 1, 1, 0.8)]})   # horns: out, then up
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 6.4, 14, 0.4], body)
        cb(a, sx * 7.0, 9.4, 0.4, 2.8, 3.6, 2.8, 'leg')                                          # upper arm
        sl = m.bone('tc_sleeve_' + side, [sx * 7, 9, 0.4], a)
        cb(sl, sx * 7.0, 8.0, 0.4, 3.6, 2.0, 3.6, 'tc')                                          # cloth elbow sleeve
        rb(a, sx * 7.2, 4.0, 0.2, 4.4, 4.4, 4.4, 'steel', r=0.6)                                 # bracer
        cb(a, sx * 7.2, 7.6, 0.2, 4.8, 0.8, 4.8, 'steel_l')
        rb(a, sx * 7.4, 0.8, -0.4, 4.8, 3.6, 4.6, 'steel_d', r=0.5)                               # gauntlet hand
        for k, dx in enumerate((-1.7, -0.6, 0.5, 1.6)):
            cb(a, sx * 7.4 + dx, -1.2, -2.0 - (0.4 if k in (1, 2) else 0), 0.9, 2.6, 1.0, 'steel', decals={'north': [('rect', 0, 0.45, 1, 0.55, '#4a525c')]})   # spread fingers
            cb(a, sx * 7.4 + dx, -1.8, -2.6 - (0.4 if k in (1, 2) else 0), 0.7, 0.8, 0.9, 'claw')   # claw tips
        cb(a, sx * 7.4 - sx * 2.8, 1.2, -1.6, 1.0, 2.2, 1.0, 'steel')                           # thumb
    for sx, side in ((1, 'r'), (-1, 'l')):                                              # bat wings spread up/out behind the shoulders
        w = m.bone('wing_' + side, [sx * 2.4, 18.6, 4.4], body)
        tw = m.bone('ts_wing_' + side, [sx * 2.4, 18.6, 4.4], w)
        Z = 5.0
        def wcb(b, x, y, z, w_, h, d, mat, **kw):                                        # whole wing 1.8x about the shoulder
            k = 1.15
            return cb(b, x * k, 18.6 + (y - 18.6) * k, z, w_ * k, h * k, d, mat, **kw)
        for (x, y, wd, h) in ((3.2, 19.0, 2.0, 1.2), (5.0, 20.2, 2.2, 1.2), (6.8, 21.6, 2.2, 1.2), (8.6, 23.0, 2.2, 1.2), (10.2, 24.2, 1.6, 1.2)):
            wcb(w, sx * x, y, Z, wd, h, 1.0, 'steel_d')                                          # leading-edge arm bone (stepped)
        wcb(w, sx * 11.2, 25.2, Z, 0.8, 1.4, 0.8, 'claw')                                        # wing claw
        for (fx, ytop, ybot) in ((5.4, 20.6, 15.6), (8.0, 22.8, 15.0), (10.4, 24.2, 16.8)):
            wcb(w, sx * fx, ybot, Z - 0.1, 0.6, ytop - ybot, 0.6, 'steel_d')                       # finger bones
        for (x0, x1, ytop, ybot) in ((2.4, 5.4, 19.4, 16.6), (5.4, 8.0, 21.0, 16.4), (8.0, 10.4, 23.4, 17.6)):
            wcb(tw, sx * (x0 + x1) / 2, ybot, Z, x1 - x0, ytop - ybot, 0.3, 'soft',
               decals={f: [('shade', 0, 0, 1, 0.3, 1.06), ('shade', 0, 0.7, 1, 1, 0.9)] for f in ('north', 'south')})   # membrane panels
            wcb(tw, sx * (x0 + x1) / 2, ybot - 0.7, Z, (x1 - x0) * 0.45, 0.7, 0.3, 'soft')               # scalloped lower edge
    m.hitbox(1.0, 1.6)
    shade_pass(m, ('steel',))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -a, 0], [0, a * 0.4, 0]], L)}, 'wing_l': {'rotation': loop([[0, a, 0], [0, -a * 0.4, 0]], L)}}
    hang = {'arm_r': {'rotation': loop([[-20, 0, 25], [-24, 0, 27]], 1.0)}, 'arm_l': {'rotation': loop([[-20, 0, -25], [-24, 0, -27]], 1.0)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 1.0)}}; idle.update(flap(0.5, 35)); idle.update(hang)
    m.anim('idle', 1.0, 'loop', idle)
    walk = dict(idle); walk['body'] = {'rotation': loop([[15, 0, 0], [15, 0, 0]], 0.6)}; walk.update(flap(0.3, 40))
    m.anim('walk', 0.6, 'loop', walk)
    m.anim('attack', 0.75, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 25]), (0.25, [-140, 0, 10]), (0.4, [-30, 0, 0]), (0.75, [-20, 0, 25])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-10, 10, 0]), (0.4, [15, -10, 0]), (0.75, [0, 0, 0])]}})
    common_tail(m)
    return m


SKULL = ["..xxxxxx..", ".xxxxxxxx.", "xxxxxxxxxx", "xxxxxxxxxx", "x..xxxx..x", "x..xxxx..x", "xxxxx.xxxx",
         ".xxx..xxx.", "..xxxxxx..", "..x.x.xx.."]


def _staves(vertical, skull=False, flip=False, base=(150, 92, 50), seam=(92, 52, 26), upright=False):
    """wooden barrel staves; seams run along the rocket axis. optional painted white skull (nose = image top or right)"""
    def f(img, rng):
        import numpy as _np, random as _r
        h, w, _ = img.shape
        R = _r.Random(h * 77 + w + (1 if vertical else 0))
        img[:] = _np.array(base, float)
        n = w if vertical else h
        pos = 0
        while pos < n:
            sw = R.choice((5, 6, 7))
            tone = 1.0 + R.uniform(-0.07, 0.07)
            sl = (slice(None), slice(pos, pos + sw)) if vertical else (slice(pos, pos + sw), slice(None))
            img[sl] *= tone
            for _ in range(3):                                                   # grain
                g = R.randrange(pos, min(n, pos + sw))
                a0 = R.randrange(0, (h if vertical else w)); L = R.randint(3, 9)
                if vertical: img[a0:a0 + L, g] *= 0.86
                else: img[g, a0:a0 + L] *= 0.86
            e = min(n, pos + sw) - 1
            if vertical: img[:, e] = _np.array(seam, float); img[:, pos] *= 1.1
            else: img[e, :] = _np.array(seam, float); img[pos, :] *= 1.1
            pos += sw
        if skull:
            A = _np.array([list(r) for r in SKULL])
            S = SKULL if upright else [''.join(r) for r in _np.rot90(A, -1 if flip else 1)]   # skull top -> image left (flip: right)
            sc = max(1, min(2, h // 10, w // 10))
            H, W = len(S) * sc, len(S[0]) * sc
            y0, x0 = (h - H) // 2, (w - W) // 2
            for j, row in enumerate(S):
                for i, ch in enumerate(row):
                    if ch == 'x':
                        img[y0 + j * sc:y0 + (j + 1) * sc, x0 + i * sc:x0 + (i + 1) * sc] = _np.array([238, 234, 222.0])
        img[:] = _np.clip(img, 0, 255)
    return f


def _folds(dark=0.82, light=1.1, period=3):
    """soft cloth folds: gentle vertical light/dark bands + darker bottom"""
    def f(img, rng):
        import numpy as _np, math as _mm
        h, w, _ = img.shape
        xs = _np.array([1.0 + (light - 1.0) * max(0, _mm.sin(i * 2 * _mm.pi / (period * 2))) - (1.0 - dark) * max(0, -_mm.sin(i * 2 * _mm.pi / (period * 2)))
                        for i in range(w)])
        img[:] = img * xs.reshape(1, w, 1)
        img[:] = img * _np.linspace(1.05, 0.88, h).reshape(h, 1, 1)
        img[:] = _np.clip(img, 0, 255)
    return f


def witch():
    """Witch (HQ, after the art): big rounded purple hood with a drooping point and dark lining, hood stoles down the
    front, long tattered cape, pale lavender face with glowing pink eyes, dark grey bodice with lighter V panel, brown
    belt with a big gold skull buckle, flared pink skirt dissolving into long tattered strips, angular gold pauldrons,
    dark gauntlets with gold rims + claws (team cuffs), twisted staff with rope grip and a ram-horned skull, green wisp."""
    import random as _r
    m = new_model('clash_witch')
    m.mats_({'skin': ('#dccbe0', 'soft'), 'skin_d': ('#bba8c4', 'soft'), 'hood': ('#6a5ad0', 'soft'), 'hood_l': ('#8070e0', 'soft'),
             'hood_d': ('#4a3c9e', 'soft'), 'lining': ('#2a2050', 'soft'), 'bodice': ('#56585f', 'soft'), 'bodice_l': ('#7a7c84', 'soft'),
             'skirt': ('#cc80ae', 'soft'), 'skirt_d': ('#9a5292', 'soft'), 'skirt_dd': ('#74407e', 'soft'), 'belt': ('#6a4630', 'soft'),
             'gold': ('#d8ac4c', 'soft'), 'gold_d': ('#a87c2c', 'soft'), 'glove': ('#45474f', 'soft'), 'tc': ('#eeeeee', 'cloth'),
             'boot': ('#3a3a40', 'soft'), 'shaft': ('#4a2e20', 'soft'), 'shaft_l': ('#6c4630', 'soft'), 'rope': ('#a88a5a', 'rope'),
             'bone': ('#e8dec6', 'soft'), 'bone_d': ('#c4b89c', 'soft'), 'horn': ('#b8986a', 'soft'), 'horn_d': ('#8a6c46', 'soft'),
             'eye': ('#ff4ad6', 'glow'), 'glowpink': ('#a46ab8', 'plain'), 'wisp': ('#7ff0c8', 'glow'), 'hole': ('#2e2620', 'plain')})
    CL = lambda *e: {g: [('fn', _folds())] + list(e) for g in ('north', 'south', 'east', 'west')}
    S = 'skin'
    R = _r.Random(7)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 1.8, 1.0, -0.6, 2.4, 5.0, 2.6, 'boot')                                               # dark pointy boots
    body = m.bone('body', [0, 12, 0], root)
    hem = ('lerp', '#7a4282', 0.45, 1.0, 'y')
    cb(body, 0, 8.0, 0.2, 7.8, 4.2, 5.0, 'skirt', decals=CL())                                             # skirt top
    cb(body, 0, 3.0, 0.2, 9.4, 5.0, 6.2, 'skirt', decals=CL(hem))                                          # flared skirt
    for x in (-3.9, -2.2, -0.6, 1.0, 2.6, 4.0):                                                              # tattered strips, front + back
        for z, mats in ((-2.95, ('skirt_d', 'skirt')), (3.35, ('skirt_d', 'skirt_dd'))):
            h = R.choice((2.6, 3.6, 4.8, 5.8))
            cb(body, x, 3.0 - h, z, 1.5, h, 0.5, R.choice(mats), decals={'north': [('lerp', '#6a3878', 0.3, 1.0, 'y')], 'south': [('lerp', '#6a3878', 0.3, 1.0, 'y')]})
    for sx in (1, -1):
        for z in (-1.8, 0.2, 2.2):
            h = R.choice((2.8, 4.0, 5.2))
            cb(body, sx * 4.45, 3.0 - h, z, 0.5, h, 1.6, R.choice(('skirt_d', 'skirt')), decals={'east': [('lerp', '#6a3878', 0.3, 1.0, 'y')], 'west': [('lerp', '#6a3878', 0.3, 1.0, 'y')]})
    cb(body, 0, 12.0, 0, 7.0, 10.6, 3.8, 'bodice', decals={'north': [('rect', 0.38, 0.0, 0.62, 1.0, '#7a7c84'), ('rect', 0.49, 0, 0.51, 1, '#3e4046'), ('lerp', '#3e4046', 0.7, 1.0, 'y')]})   # bodice + V panel
    cb(body, 0, 21.8, -1.95, 2.6, 0.8, 0.1, 'skin')                                                         # neckline
    cb(body, 0, 11.6, 0, 7.6, 1.6, 4.4, 'belt')                                                            # belt
    sk = pix(["........", ".kk..kk.", ".kk..kk.", "...kk...", "........", ".k.k.k.."], {'k': '#5a4020'})
    cb(body, 0, 10.8, -2.4, 3.2, 3.4, 0.6, 'gold', decals={'north': sk, 'up': [('shade', 0, 0, 1, 1, 1.12)]})  # big gold skull buckle
    cb(body, 0, 10.2, -2.4, 2.0, 0.8, 0.6, 'gold_d')
    td = m.bone('tc_dress', [0, 12, 0], body)
    for sx in (1, -1):
        cb(td, sx * 2.6, 10.6, -2.25, 1.0, 2.2, 0.3, 'tc')                                                  # little team tassels on the belt
    cp = m.bone('cape', [0, 24, 2.6], body)
    cb(cp, 0, 1.6, 3.0, 9.8, 21.4, 0.9, 'hood', decals={'south': [('fn', _folds(0.78, 1.12, 2)), ('lerp', '#3e3290', 0.6, 1.0, 'y')]})   # long cape
    for x in (-4.0, -1.6, 0.8, 3.2):
        h = R.choice((3.0, 4.4, 5.6))
        cb(cp, x, 1.6 - h, 3.0, 2.2, h, 0.9, R.choice(('hood_d', 'hood')))                                   # ragged cape tails
    for sx in (1, -1):
        cb(cp, sx * 4.6, 3.0, 1.2, 0.8, 19.6, 3.6, 'hood', decals={'east': [('fn', _folds())], 'west': [('fn', _folds())]})
        cb(body, sx * 2.9, 11.0, -2.2, 1.6, 12.0, 0.5, 'hood', decals={'north': [('fn', _folds(0.85, 1.1, 1))]})   # hood stoles down the front
        cb(body, sx * 2.9, 9.0, -2.2, 1.2, 2.0, 0.5, 'hood_d')
    hd = m.bone('head', [0, 24, 0], body)
    face = [('rect', 0.4, 0.8, 0.6, 0.85, '#8a4a86'), ('rect', 0.44, 0.85, 0.56, 0.88, '#b07ab0')]
    cb(hd, 0, 24.4, 0.2, 6.8, 7.2, 6.8, S, decals={'north': face + [('shade', 0, 0, 1, 0.38, 0.5), ('shade', 0, 0.38, 1, 0.5, 0.75)],
                                                   'east': [('shade', 0, 0, 1, 0.5, 0.6)], 'west': [('shade', 0, 0, 1, 0.5, 0.6)]})   # face, upper half in hood shadow
    cb(hd, 0, 23.6, -1.4, 4.4, 1.0, 3.8, S)                                                                 # narrow chin
    cb(hd, 0, 26.8, -3.3, 0.8, 1.0, 0.4, 'skin_d')                                                          # little nose
    for sx in (1, -1):
        cb(hd, sx * 1.7, 27.6, -3.2, 1.8, 1.4, 0.1, 'eye', decals={'north': [('rect', 0.3, 0.25, 0.7, 0.7, '#ffd0f4')]})   # big glowing eyes
    ho = m.bone('hood', [0, 24, 0], hd)
    def rnd(b, x, y, z, w, h, d, c, mat, **kw):
        cb(b, x, y, z, w, h, d - 2 * c, mat, **kw); cb(b, x, y, z, w - 2 * c, h, d, mat, **kw)
    HL = lambda: {g: [('lerp', '#8c7ce8', 0.0, 0.5, 'y'), ('fn', _folds(0.86, 1.08, 2))] for g in ('north', 'south', 'east', 'west')}
    for sx in (1, -1):
        cb(ho, sx * 4.4, 21.4, 0.6, 1.4, 10.4, 8.4, 'hood', decals=HL())                                     # hood sides
        cb(ho, sx * 3.75, 21.8, -3.35, 0.3, 9.8, 0.6, 'lining')                                             # dark lining at the opening
        cb(ho, sx * 4.2, 21.4, -3.9, 1.6, 10.0, 0.8, 'hood_l', decals={'north': [('lerp', '#5a4ab8', 0.6, 1.0, 'y')]})   # rolled front edge
    cb(ho, 0, 21.4, 4.6, 9.6, 10.4, 1.2, 'hood_d', decals=HL())                                             # back
    cb(ho, 0, 31.6, 0.6, 10.2, 2.4, 9.8, 'hood', decals={**HL(), 'up': [('shade', 0, 0, 1, 1, 1.1)]})       # boxy hood top
    cb(ho, 0, 30.4, -4.2, 9.2, 1.6, 2.0, 'hood_l', decals={'north': [('lerp', '#4a3ca0', 0.4, 1.0, 'y')], 'up': [('shade', 0, 0, 1, 1, 1.1)]})   # brim
    for (w, yb) in ((3.2, 29.6), (1.4, 28.8)):
        cb(ho, 0, yb, -4.5, w, 30.4 - yb, 2.4, 'hood', decals={'north': [('lerp', '#5a4ab8', 0.5, 1.0, 'y')]})   # V peak dipping between the eyes
    cb(ho, 0, 30.2, -3.4, 6.6, 0.4, 0.4, 'lining')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.5
        a = m.bone('arm_' + side, [x, 22.5, 0], body)
        cb(a, x + sx * 0.3, 20.6, 0, 4.0, 2.6, 4.4, 'gold', decals={'up': [('shade', 0, 0, 1, 1, 1.15)], 'north': [('lerp', '#a87c2c', 0.5, 1.0, 'y')]})   # pauldron
        cb(a, x + sx * 0.5, 22.6, 0, 3.0, 1.2, 3.4, 'gold')
        cb(a, x + sx * 2.2, 21.4, 0, 1.0, 1.4, 1.4, 'gold_d')                                               # pauldron spike
        cb(a, x + sx * 2.9, 21.7, 0, 0.6, 0.8, 0.8, 'gold_d')
        cb(a, x, 15.0, 0, 2.6, 5.8, 2.6, S, decals={g: [('lerp', '#bba8c4', 0.5, 1.0, 'y')] for g in ('north', 'south', 'east', 'west')})   # pale arm
        gl = m.bone('tc_glove_' + side, [x, 14, 0], a)
        cb(a, x, 9.2, 0, 3.0, 6.0, 3.0, 'glove', decals={g: [('shade', 0, 0, 0.3, 1, 1.15)] for g in ('north', 'south')})   # gauntlet
        cb(a, x, 14.6, 0, 3.6, 1.0, 3.6, 'gold')                                                           # gold rim
        cb(gl, x, 13.6, 0, 3.4, 1.0, 3.4, 'tc')                                                             # team cuff
        for k in (-0.9, 0.0, 0.9):
            cb(a, x + k, 8.0, -0.9, 0.5, 1.4, 0.5, 'glove')                                                 # claws
    st = m.bone('staff', [5.5, 13.5, -2.6], m.by_name('arm_r'))
    SX = 1.8
    for i, y in enumerate(range(0, 36, 2)):
        cb(st, 5.5 + SX + (0.3 if i % 2 else -0.3), y, -2.6 + (0.2 if i % 3 == 0 else -0.2), 1.6, 2.0, 1.6, 'shaft' if i % 2 else 'shaft_l')   # twisted staff
    for y in (11.4, 12.4, 13.4):
        cb(st, 5.5 + SX, y, -2.6, 2.0, 0.8, 2.0, 'rope')                                                    # rope grip
    ob = m.bone('orb', [5.5, 39.2, -2.7], st)
    X0, Z0 = 5.5 + SX, -2.7
    sk2 = pix(["........", "........", ".kkk.kkk", ".kkk.kkk", "........", "...kk...", "........", "........"], {'k': '#2e2620'})
    cb(ob, X0, 36.4, Z0, 6.4, 5.4, 6.4, 'bone', decals={'north': sk2, 'up': [('shade', 0, 0, 1, 1, 1.08)]})     # skull cranium
    cb(ob, X0, 41.8, Z0 + 0.4, 5.0, 0.9, 5.0, 'bone')
    cb(ob, X0, 34.6, Z0 - 0.6, 4.4, 1.8, 4.6, 'bone_d', decals={'north': pix(["k.k.k.k", "......."], {'k': '#2e2620'})})   # teeth + jaw
    for sx in (1, -1):                                                                                      # spiral ram horns
        for (dx, dy, dz, s, mat) in ((3.4, 40.4, 0.0, 2.4, 'horn'), (5.0, 41.0, 1.0, 2.3, 'horn'), (6.6, 40.2, 1.6, 2.2, 'horn_d'),
                                     (7.4, 38.4, 1.2, 2.0, 'horn'), (7.0, 36.6, 0.0, 1.8, 'horn'), (6.0, 35.6, -1.2, 1.5, 'horn_d'), (5.0, 36.0, -2.0, 1.0, 'horn')):
            cb(ob, X0 + sx * dx, dy - s / 2, Z0 + dz, s, s, s, mat, decals={'up': [('shade', 0, 0, 1, 1, 1.12)]})
    wl = m.by_name('arm_l')
    cb(wl, -5.5, 7.4, -3.2, 2.8, 2.8, 2.8, 'wisp'); cb(wl, -5.0, 10.0, -3.0, 1.4, 1.6, 1.4, 'wisp'); cb(wl, -6.0, 6.6, -4.2, 1.0, 1.0, 1.0, 'wisp')   # green wisp
    m.hitbox(0.8, 2.4)
    return m


def goblin():
    """Goblin: big bald green head, long pointy ears, bushy brows, cheeky grin + long nose, skinny green body,
    team-colour suspenders over brown knee shorts, curly pointed shoes, steel dagger in the left hand."""
    m = new_model('clash_goblin')
    m.mats_({'skin': ('#8cc63c', 'skin'), 'skin_d': ('#6fa62c', 'skin'), 'brow': ('#5a8a24', 'hair'), 'nose': ('#c8b878', 'skin'),
             'ear_in': ('#d8b890', 'skin'), 'shorts': ('#5a4634', 'cloth'), 'shorts_d': ('#463626', 'cloth'), 'shoe': ('#9a6a3e', 'leather'),
             'shoe_d': ('#7a5030', 'leather'), 'tc': ('#efefef', 'cloth'), 'btn': ('#d8c08a', 'metal'), 'blade': ('#c8ced6', 'metal'),
             'blade_d': ('#9aa2ac', 'metal'), 'grip': ('#6a3e22', 'wood'), 'brass': ('#c89a48', 'metal')})
    S = 'skin'
    allb = m.bone('all', [0, 0, 0])
    for sx, side in ((1, 'right'), (-1, 'left')):
        x = sx * 2.0
        lg = m.bone(side + '_leg', [x, 7.5, 0], allb)
        cb(lg, x, 4.4, 0, 3.4, 3.6, 3.6, 'shorts', decals={f: [('shade', 0, 0, 1, 0.2, 0.85)] for f in ('north', 'south', 'east', 'west')})   # baggy shorts leg
        cb(lg, x, 4.0, 0, 3.6, 0.8, 3.8, 'shorts_d')                                                     # rolled cuff
        cb(lg, x, 1.4, 0, 2.0, 2.8, 2.0, S)                                                                # skinny shin
        cb(lg, x, 0, -0.8, 2.8, 1.6, 4.6, 'shoe', decals={'up': [('shade', 0, 0, 1, 0.3, 1.1)]})            # long shoe
        cb(lg, x, 0.6, -3.4, 1.8, 1.0, 1.2, 'shoe'); cb(lg, x, 1.4, -4.0, 1.2, 1.0, 1.0, 'shoe_d')          # curled pointy toe
    body = m.bone('body', [0, 8, 0], allb)
    cb(body, 0, 7.4, 0, 7.4, 3.0, 4.4, 'shorts', decals={'north': [('rect', 0, 0, 1, 0.25, '#463626')]})      # shorts waist
    cb(body, 0, 10.2, 0, 6.6, 7.0, 3.8, S, decals={'north': [('rect', 0.48, 0.55, 0.52, 0.62, '#6fa62c'), ('lerp', '#7ab634', 0.6, 1.0, 'y')]})   # skinny torso (navel)
    cb(body, 0, 10.0, -0.3, 6.0, 2.6, 3.8, S)                                                            # little pot belly
    st = m.bone('tc_straps', [0, 12, 0], body)
    for sx in (1, -1):
        cb(st, sx * 2.1, 10.0, -2.4, 1.4, 7.4, 0.4, 'tc', decals={'north': [('rect', 0, 0, 0.15, 1, '#c8c8c8'), ('rect', 0.85, 0, 1, 1, '#c8c8c8')]})   # team suspenders, front
        cb(st, sx * 1.6, 10.0, 2.1, 1.4, 7.4, 0.4, 'tc')                                                   # back
        cb(st, sx * 2.1, 17.2, 0, 1.4, 0.5, 4.9, 'tc')                                                     # over the shoulder
        cb(body, sx * 2.1, 9.6, -2.75, 1.0, 1.2, 0.4, 'btn')                                               # brass clips at the waistband
        cb(body, sx * 1.6, 9.6, 2.45, 1.0, 1.2, 0.4, 'btn')
    hd = m.bone('head', [0, 17, 0], body)
    face = pix(["........", "........", "........", ".wb..wb.", "........", "........", "........", "........"], {'w': '#ffffff', 'b': '#4a2e1a'})
    face += [('rect', 0.24, 0.7, 0.3, 0.74, '#4a2414'), ('rect', 0.7, 0.7, 0.76, 0.74, '#4a2414'),             # friendly grin
             ('rect', 0.3, 0.74, 0.7, 0.8, '#4a2414'), ('rect', 0.34, 0.74, 0.66, 0.77, '#ffffff'), ('rect', 0.42, 0.8, 0.58, 0.83, '#4a2414')]
    cb(hd, 0, 17, -0.4, 8.4, 8.4, 8.0, S, decals={'north': face, 'up': [('shade', 0, 0, 1, 1, 1.06)]}, dens=2)   # big bald head
    for sx in (1, -1):
        cb(hd, sx * 2.0, 23.0, -4.6, 2.8, 0.9, 0.8, 'brow')                                               # bushy brows (relaxed)
    cb(hd, 0, 19.4, -5.2, 1.6, 2.2, 1.6, 'nose'); cb(hd, 0, 19.6, -6.4, 1.2, 1.4, 1.2, 'nose')                    # long nose
    for sx in (1, -1):                                                                                      # long pointy ears
        cb(hd, sx * 5.0, 19.6, -0.2, 1.6, 4.4, 1.2, S); cb(hd, sx * 6.6, 20.4, -0.2, 2.0, 3.8, 1.0, S)          # big leaf ears
        cb(hd, sx * 8.4, 21.4, -0.2, 2.0, 2.8, 0.9, S); cb(hd, sx * 10.0, 22.6, -0.2, 1.6, 1.8, 0.8, S)
        cb(hd, sx * 11.2, 23.8, -0.2, 1.0, 1.2, 0.6, 'skin_d')
        cb(hd, sx * 7.4, 20.8, -0.75, 3.6, 2.4, 0.1, 'ear_in')                                            # pinkish inner ear
    for sx, side in ((1, 'right'), (-1, 'left')):
        x = sx * 4.95
        a = m.bone(side + '_arm', [x, 16.5, -0.4], body)
        cb(a, x, 9.4, -0.4, 2.2, 7.4, 2.2, S, decals={f: [('lerp', '#7ab634', 0.7, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # skinny arm
        cb(a, x, 8.6, -0.4, 2.8, 2.2, 2.8, S)                                                            # hand
    dg = m.bone('dagger', [-4.95, 10, -0.4], m.by_name('left_arm'))
    cb(dg, -4.95, 8.8, 0.6, 1.0, 1.0, 2.4, 'grip')                                                       # grip in the fist
    cb(dg, -4.95, 8.8, 2.0, 1.4, 1.4, 0.8, 'brass')                                                      # pommel
    cb(dg, -4.95, 7.9, -2.0, 1.2, 2.8, 0.9, 'brass')                                                     # cross guard
    for (h, d, z) in ((2.6, 2.6, -3.7), (2.0, 2.0, -6.0), (1.2, 1.8, -7.9), (0.5, 1.2, -9.4)):
        cb(dg, -4.95, 9.3 - h / 2, z, 0.4, h, d, 'blade', decals={'east': [('rect', 0, 0.45, 1, 0.55, '#9aa2ac')], 'west': [('rect', 0, 0.45, 1, 0.55, '#9aa2ac')]})   # tapering blade
    m.hitbox(0.7, 1.4)
    return m


def lumberjack():
    """Lumberjack: huge orange beard + moustache, tongue out, white fur ushanka with team ear-flaps and a purple gem,
    bare muscular chest, belt with gold buckle, purple shorts, blue flip-flops, team wristbands, hatchet held forward,
    rage-potion bottle on the left shoulder."""
    m = new_model('clash_lumberjack')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d0906c', 'skin'), 'beard': ('#e88a2a', 'hair'), 'beard_d': ('#c86c1a', 'hair'),
             'fur': ('#e4e8ee', 'fur'), 'fur_d': ('#c4cad2', 'fur'), 'tc': ('#efefef', 'cloth'), 'gem': ('#b04ae0', 'glow'),
             'shorts': ('#6a4a8a', 'cloth'), 'belt': ('#6a4026', 'leather'), 'gold': ('#e2b23a', 'metal'), 'sandal': ('#4aa8d8', 'leather'),
             'tongue': ('#e05a7a', 'skin'), 'wood': ('#7a4a2a', 'wood'), 'steel': ('#a8b0b8', 'metal'), 'steel_l': ('#d4dae0', 'metal'),
             'glass': ('#c050f0', 'glow'), 'glass_l': ('#e8a0ff', 'glow'), 'cork': ('#a87a4a', 'wood')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.0
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 6.4, 0, 4.0, 5.6, 4.0, 'shorts')                                                   # purple shorts
        cb(lg, x, 0.8, 0, 3.4, 5.8, 3.4, S)                                                          # bare legs
        cb(lg, x, 0, -0.6, 3.8, 0.8, 5.0, 'sandal'); cb(lg, x, 0.8, -1.4, 0.8, 0.8, 0.6, 'sandal')     # flip-flops
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 12.0, 0.2, 9.6, 12.4, 5.6, S, decals={'north': [('rect', 0.49, 0.1, 0.51, 0.75, '#c8866a'), ('rect', 0.12, 0.34, 0.47, 0.38, '#c8866a'),
                                                             ('rect', 0.53, 0.34, 0.88, 0.38, '#c8866a'), ('rect', 0.3, 0.5, 0.7, 0.52, '#d0906c'),
                                                             ('rect', 0.3, 0.62, 0.7, 0.64, '#d0906c'), ('lerp', '#d8987a', 0.75, 1.0, 'y')]})   # broad chest, pecs + abs
    cb(body, 0, 19.6, -0.4, 10.4, 4.4, 5.6, S, decals={'north': [('shade', 0, 0.85, 1, 1, 0.85)]})       # bulging pecs
    cb(body, 0, 24.0, 0.4, 7.0, 1.2, 4.6, S)                                                          # thick neck/traps
    cb(body, 0, 12.0, 0.2, 10.0, 2.0, 6.0, 'belt')                                                       # belt
    cb(body, 0, 11.8, -3.0, 2.8, 2.4, 0.4, 'gold', decals={'north': [('rect', 0.25, 0.3, 0.75, 0.7, '#6a4026')]})   # gold buckle
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".wb..bw.", "........", "........", "........", "........"], {'w': '#ffffff', 'b': '#3a6aa8'})
    face += [('rect', 0.1, 0.55, 0.3, 0.65, '#f09090'), ('rect', 0.7, 0.55, 0.9, 0.65, '#f09090')]
    cb(hd, 0, 24, 0, 8, 8, 8, S, decals={'north': face}, dens=2)
    cb(hd, 0, 26.6, -4.4, 2.0, 1.8, 1.2, 'skin_d')                                                    # nose
    cb(hd, 0, 20.2, -3.2, 8.6, 6.2, 2.8, 'beard', decals={'north': [('lerp', '#c86c1a', 0.5, 1.0, 'y'), ('rect', 0.3, 0, 0.32, 0.8, '#c86c1a'), ('rect', 0.68, 0, 0.7, 0.8, '#c86c1a')]})   # huge beard
    cb(hd, 0, 18.6, -2.6, 5.4, 1.8, 2.2, 'beard_d')                                                   # pointed beard tip
    for sx in (1, -1):
        cb(hd, sx * 4.1, 23.0, 0, 0.6, 4.0, 6.0, 'beard')                                             # sideburns
        cb(hd, sx * 2.0, 25.0, -4.6, 3.6, 1.2, 1.0, 'beard', rot=('z', -sx * 22.5), rot_origin=[sx * 2.0, 25.6, -4.6])   # moustache
    cb(hd, 0, 23.0, -4.7, 2.4, 1.6, 0.8, 'tongue')                                                    # tongue out
    cb(hd, 0, 24.0, -4.65, 3.0, 0.8, 0.4, 'beard_d')                                                  # mouth shadow
    cb(hd, 0, 31.0, 0, 9.4, 3.4, 9.4, 'fur', decals={f: [('lerp', '#ffffff', 0.0, 0.4, 'y')] for f in ('north', 'south', 'east', 'west')})   # fur ushanka crown
    cb(hd, 0, 30.4, -4.9, 9.6, 1.4, 1.0, 'fur_d')                                                     # front brim
    th = m.bone('tc_hat', [0, 30, 0], hd)
    for sx in (1, -1):
        cb(th, sx * 4.9, 25.4, 0, 0.8, 4.8, 5.0, 'tc')                                                # team ear flaps
    cb(th, 0, 30.0, -5.05, 9.8, 0.6, 0.4, 'tc')                                                       # team band
    cb(hd, 0, 31.8, -5.0, 1.6, 1.6, 0.4, 'gem')                                                       # purple gem
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.0
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x + sx * 1.0, 18.4, 0, 5.0, 5.0, 5.0, S, decals={'up': [('shade', 0, 0, 1, 1, 1.06)]})        # big round shoulder
        cb(a, x + sx * 1.0, 14.6, 0, 4.4, 4.2, 4.4, S, decals={'north': [('shade', 0, 0.8, 1, 1, 0.88)]})   # bulging upper arm
        cb(a, x + sx * 1.0, 9.4, 0, 4.6, 5.4, 4.6, S, decals={'north': [('lerp', '#d0906c', 0.6, 1.0, 'y')]})   # thick forearm + fist
        if side == 'l':                                                                     # hand curled over the top of the bottle
            cb(a, -8.6, 8.8, -1.0, 2.8, 2.4, 4.4, S)                                          # palm over the bottle (arm raised sideways)
            cb(a, -10.0, 10.0, -1.0, 1.6, 3.0, 4.2, S, decals={'west': pix(["......", "k.k.k.", "......"], {'k': '#d0906c'})})   # curled fingers
        tb = m.bone('tc_band_' + side, [x, 14, 0], a)
        cb(tb, x + sx * 1.0, 12.2, 0, 5.0, 1.6, 5.0, 'tc')                                              # team wristband
    ax = m.bone('axe', [6.0, 13.0, -0.2], m.by_name('arm_r'))
    Y = 11.6
    cb(ax, 6.0, Y - 0.6, -4.4, 1.2, 1.2, 13.0, 'wood', decals={f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})   # haft held forward
    cb(ax, 6.0, Y - 1.2, -11.6, 1.8, 2.6, 3.0, 'steel', decals={'up': [('shade', 0, 0, 1, 1, 1.12)]})   # axe head
    cb(ax, 6.0, Y - 4.8, -12.2, 0.8, 3.8, 4.2, 'steel', decals={'east': [('lerp', '#d4dae0', 0.6, 1.0, 'y')], 'west': [('lerp', '#d4dae0', 0.6, 1.0, 'y')]})   # blade
    cb(ax, 6.0, Y - 5.4, -12.2, 0.6, 0.8, 4.8, 'steel_l')                                              # bright edge
    cb(ax, 6.0, Y - 0.4, -11.6, 1.4, 0.6, 1.6, 'wood')                                                 # haft end poking out
    fl = m.bone('flask', [-5.0, 24.0, 1.0], body)                                             # rage potion resting on the left shoulder
    # big bottle lying on the shoulder (front-to-back), held from behind by the raised left hand
    for (w, h) in ((7.0, 5.6), (5.6, 7.6), (6.4, 6.8)):
        cb(fl, -7.0, 29.6 - h / 2, -1.6, w, h, 9.0, 'glass', decals={'up': [('rect', 0.15, 0.1, 0.35, 0.9, '#f0c8ff')], 'east': [('rect', 0.1, 0.15, 0.9, 0.3, '#f0c8ff')], 'west': [('rect', 0.1, 0.15, 0.9, 0.3, '#f0c8ff')]})
    cb(fl, -7.0, 26.2, 3.0, 6.0, 6.8, 0.3, 'gold')                                                     # gold base rim
    cb(fl, -7.0, 26.6, 3.2, 5.2, 6.0, 0.2, 'cork')                                                     # bottom
    cb(fl, -7.0, 28.2, -7.0, 2.8, 2.8, 1.8, 'glass_l'); cb(fl, -7.0, 28.0, -8.6, 3.2, 3.2, 1.4, 'cork')   # neck + cork pointing forward
    m.hitbox(0.8, 2.2)
    return m


def _scales(img, rng):
    """chainmail fish-scale pattern"""
    import numpy as _np
    h, w, _ = img.shape
    base = img.copy()
    for y in range(h):
        for x in range(w):
            cx = (x + (2 if (y // 3) % 2 else 0)) % 4
            cy = y % 3
            d = abs(cx - 1.5) + cy * 0.7
            img[y, x] = base[y, x] * (1.18 - 0.14 * d)
            if cy == 2 and cx in (0, 3): img[y, x] = base[y, x] * 0.6
    img[:] = _np.clip(img, 0, 255)


def mega_knight():
    """Mega Knight: hulking dark-steel knight. Bucket helm with a rivet band, eye slit (face + blue eyes) and a barred
    grille visor, team plume; huge V gorget collar, broad chest plate, team belt with a big gold buckle, chainmail skirt and
    sleeves, armoured boots with round knee guards; a giant spiked mace-fist on each arm."""
    m = new_model('clash_mega_knight')
    m.mats_({'steel': ('#3e464e', 'soft'), 'steel_l': ('#5e6a74', 'soft'), 'steel_d': ('#2a3036', 'soft'), 'mail': ('#8a929a', 'soft'),
             'skin': ('#e8b08c', 'skin'), 'void': ('#121418', 'plain'), 'eye': ('#ffffff', 'plain'), 'iris': ('#3a8ad8', 'plain'),
             'gold': ('#e2b23a', 'metal'), 'tc': ('#efefef', 'cloth')})
    MT = lambda t=1.2, b=0.8: {g: [('shade', 0, 0, 1, 0.15, t), ('shade', 0, 0.8, 1, 1, b)] for g in ('north', 'south', 'east', 'west')}
    ML = lambda: {g: [('fn', _scales)] for g in ('north', 'south', 'east', 'west')}
    def rnd(bn, x, y, z, w, h, d, c, mat, **kw):
        cb(bn, x, y, z, w, h, d - 2 * c, mat, **kw); cb(bn, x, y, z, w - 2 * c, h, d, mat, **kw); cb(bn, x, y + c * 0.5, z, w - c, h - c, d - c, mat, **kw)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.4
        lg = m.bone('leg_' + side, [x, 19.2, 0], root)
        rnd(lg, x, 5.0, 0, 6.8, 14.0, 6.8, 1.2, 'steel', decals=MT())                                 # greave
        rnd(lg, x, 0, -0.8, 8.4, 5.4, 10.6, 1.8, 'steel', decals=MT(1.25, 0.75))                       # big armoured boot
        cb(lg, x, 0, -6.0, 6.4, 2.6, 1.2, 'steel_d')                                                    # toe cap
        for (h, d) in ((4.2, 2.4), (2.4, 4.2), (3.6, 3.6)):
            cb(lg, x + sx * 3.6, 8.2 - h / 2, 0.4, 1.0, h, d, 'steel_l')                               # round knee/ankle wheel
        rnd(lg, x, 13.4, -0.4, 7.4, 4.6, 7.6, 1.4, 'steel_l', decals=MT())                             # knee guard
    body = m.bone('body', [0, 19.2, 0], root)
    cb(body, 0, 15.2, 0.2, 17.0, 6.4, 11.0, 'mail', decals=ML(), dens=2)                                # chainmail skirt
    tb = m.bone('tc_belt', [0, 19.2, 0], body)
    cb(tb, 0, 21.0, 0.2, 18.0, 3.6, 12.0, 'tc', decals={g: [('shade', 0, 0, 1, 0.2, 1.2)] for g in ('north', 'south', 'east', 'west')})   # team belt
    cb(body, 0, 20.4, -6.3, 6.4, 4.8, 0.8, 'gold', decals={'north': [('rect', 0.22, 0.22, 0.78, 0.78, '#2a3036'), ('shade', 0, 0, 1, 0.2, 1.2)]})   # big gold buckle
    rnd(body, 0, 24.6, 0.2, 18.0, 13.0, 11.6, 2.4, 'steel', decals=MT())                               # broad chest
    cb(body, 0, 25.2, -5.8, 15.0, 10.0, 1.0, 'steel_l', decals={'north': [('rect', 0.45, 0.6, 0.55, 1, '#2a3036'), ('shade', 0, 0, 1, 0.12, 1.25)]})   # chest plate with V notch
    cb(body, 0, 36.2, 0.4, 15.0, 2.4, 12.6, 'steel', decals=MT(1.3, 0.8))                              # big gorget collar
    for (y, w) in ((35.2, 12.0), (34.0, 8.0), (32.8, 4.0)):
        cb(body, 0, y, -6.6, w, 1.2, 1.4, 'steel', decals={'north': [('shade', 0, 0, 1, 0.3, 1.25)]})       # V point at the front
    for sx in (1, -1):
        cb(body, sx * 6.6, 37.4, 0.4, 1.8, 2.4, 12.0, 'steel_l')                                        # flared collar wings
    hd = m.bone('head', [0, 38.4, 0], body)
    rnd(hd, 0, 37.0, 0.2, 10.4, 12.4, 10.4, 1.6, 'steel', decals=MT(1.2, 0.85))                         # bucket helm
    cb(hd, 0, 49.4, 0.2, 8.6, 0.8, 8.6, 'steel_l')                                                     # flat top
    cb(hd, 0, 46.2, 0.2, 10.8, 1.4, 10.8, 'steel_l', decals={g: [('rect', x0, 0.3, x0 + 0.06, 0.7, '#1a1e22') for x0 in (0.1, 0.3, 0.5, 0.7, 0.88)] for g in ('north', 'south', 'east', 'west')})   # rivet band
    cb(hd, 0, 42.4, -4.95, 7.4, 2.4, 0.3, 'skin', decals={'north': [('rect', 0.1, 0.25, 0.4, 0.9, '#ffffff'), ('rect', 0.6, 0.25, 0.9, 0.9, '#ffffff'),
                                                              ('rect', 0.2, 0.25, 0.34, 0.9, '#2a6ac8'), ('rect', 0.66, 0.25, 0.8, 0.9, '#2a6ac8'),
                                                              ('rect', 0, 0, 1, 0.25, '#b07a5a')]}, dens=4)   # face in the slit: eyes clearly visible
    for sx in (1, -1):
        cb(hd, sx * 2.0, 44.9, -5.2, 3.0, 0.7, 0.5, 'steel_l', rot=('z', sx * 22.5), rot_origin=[sx * 2.0, 45.25, -5.2])   # angry V brow ridge above the eyes
    cb(hd, 0, 45.4, -5.1, 9.0, 0.8, 0.4, 'steel_d')                                                    # brow line
    cb(hd, 0, 36.6, -5.4, 9.6, 6.4, 1.2, 'steel', decals={'north': [('rect', x0, 0.1, x0 + 0.08, 0.85, '#121418') for x0 in (0.14, 0.32, 0.5, 0.68, 0.84)]})   # barred grille visor
    for sx in (1, -1):
        cb(hd, sx * 5.6, 38.6, -2.4, 1.2, 3.0, 3.0, 'steel_d')                                          # visor hinge bolts
    pl = m.bone('tc_plume', [0, 51.2, 0], hd)
    cb(pl, 0, 50.2, 0.2, 1.4, 1.4, 1.4, 'steel_d')                                                     # plume socket
    for (y, z, h, d) in ((51.4, 0.2, 2.6, 1.6), (53.6, 0.8, 2.2, 1.8), (55.4, 1.8, 1.6, 2.0), (56.4, 3.2, 1.2, 1.8), (55.6, 4.4, 1.6, 1.2)):
        cb(pl, 0, y, z, 1.4, h, d, 'tc')                                                               # curled team plume
    for sx, side in ((1, 'r'), (-1, 'l')):
        X = sx * 11.0
        a = m.bone('arm_' + side, [sx * 8.0, 35.2, 0], body)
        rnd(a, X, 30.0, 0.2, 6.4, 7.0, 7.0, 1.4, 'mail', decals=ML(), dens=2)                           # chainmail sleeve
        cb(a, X + sx * 1.2, 23.6, 0.2, 4.6, 6.8, 4.6, 'skin', decals={'north': [('lerp', '#c88866', 0.8, 1.0, 'y')]})   # bare forearm
        cb(a, X + sx * 1.6, 21.2, 0.2, 6.2, 2.4, 6.2, 'steel_d')                                                   # gauntlet cuff
        # giant spiked mace-fist
        C = 15.0
        X = X + sx * 4.6
        for (w, h, d) in ((12.4, 8.4, 8.4), (8.4, 12.4, 8.4), (8.4, 8.4, 12.4), (11.0, 11.0, 6.4), (6.4, 11.0, 11.0), (11.0, 6.4, 11.0), (10.6, 10.6, 10.6)):
            cb(a, X, C - h / 2, 0.2, w, h, d, 'steel', decals={g: [('shade', 0, 0, 1, 0.3, 1.15), ('shade', 0, 0.75, 1, 1, 0.8)] for g in ('north', 'south', 'east', 'west', 'up')})
        for (dx, dy, dz) in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            o = 5.8
            for (s_, l_) in ((4.6, 1.6), (3.2, 1.6), (1.8, 1.4), (0.6, 1.0)):
                w_, h_, d_ = (l_ if dx else s_), (l_ if dy else s_), (l_ if dz else s_)
                cb(a, X + dx * (o + l_ / 2), C + dy * (o + l_ / 2) - h_ / 2, 0.2 + dz * (o + l_ / 2), w_, h_, d_, 'steel_l')   # pyramid spikes
                o += l_
    def in_head(bn):
        while bn is not None:
            if bn.name == 'head': return True
            bn = bn.parent
        return False
    KX = 1.2                                                                                  # bulkier: wider everywhere but the helm
    for bn in m.bones:
        if in_head(bn): continue
        bn.origin[0] *= KX
        for c in bn.cubes:
            for key in ('frm', 'to', 'rot_origin'):
                c[key][0] *= KX
    m.hitbox(2.6, 3.6)
    return m


def inferno_dragon():
    """Inferno Dragon: the baby dragon body (green, tan spikes made orange, leathery brown wings) wearing a riveted steel
    helmet with eye windows, a toothed jaw-guard visor and side gears, a wooden fuel keg strapped on its back with a brass
    pipe running to the helmet, and a fiery glow in the mouth."""
    m = new_model('clash_inferno_dragon')
    root = m.bone('root', [0, 0, 0])
    src = baby_dragon()
    names = {b.name: (b.name.replace('ts_', 'x_') if b.name != 'jaw' else 'mouth') for b in src.bones if b.name not in ('root', 'tc_scarf', 'hitbox')}
    made = clone_into(m, src, root, names)
    pre = 'cl_baby_dragon_'
    m.mats[pre + 'tan'] = ('#d0783a', 'skin', {}); m.mats[pre + 'wing'] = ('#9a5434', 'leather', {'stitch': False})
    m.mats[pre + 'wing_m'] = ('#c47a50', 'leather', {'stitch': False})
    m.mats[pre + 'eye'] = ('#ffc040', 'glow', {})                                           # glowing inferno eyes
    m.mats_({'steel': ('#4e5a64', 'soft'), 'steel_l': ('#76848e', 'soft'), 'steel_d': ('#353d45', 'soft'), 'void': ('#16181c', 'plain'),
             'tooth': ('#e8ecf0', 'soft'), 'wood': ('#a8703a', 'soft'), 'band': ('#9aa2aa', 'soft'), 'brass': ('#d8aa3a', 'metal'),
             'fire': ('#ffb030', 'glow'), 'fire_o': ('#ff6a1a', 'glow'), 'tc': ('#efefef', 'cloth')})
    hd, body = made['head'], made['body']
    MT = {g: [('shade', 0, 0, 1, 0.15, 1.2), ('shade', 0, 0.8, 1, 1, 0.8)] for g in ('north', 'south', 'east', 'west')}
    ED = {g: [('shade', 0, 0, 1, 0.2, 1.25), ('shade', 0, 0.8, 1, 1, 0.75)] for g in ('north', 'south', 'east', 'west')}
    SL = lambda rects: {**ED, 'up': [('rect', x0, z0, x1, z1, '#16181c') for (x0, z0, x1, z1) in rects]}
    # rounded steel shell over the top/back of the head, open at the face, windows on top
    cb(hd, 0, 23.4, -3.2, 12.0, 1.8, 12.4, 'steel', decals=SL([(0.12, 0.08, 0.3, 0.3), (0.41, 0.08, 0.59, 0.3), (0.7, 0.08, 0.88, 0.3),
                                                            (0.2, 0.45, 0.4, 0.65), (0.6, 0.45, 0.8, 0.65)]))   # top plate with windows
    cb(hd, 0, 25.2, -3.0, 9.6, 0.8, 10.4, 'steel', decals=SL([(0.3, 0.55, 0.45, 0.8), (0.55, 0.55, 0.7, 0.8)]))   # rounded crown
    cb(hd, 0, 22.6, -9.9, 12.6, 3.4, 1.4, 'steel', decals={**ED, 'north': [('rect', 0.12, 0.2, 0.3, 0.55, '#16181c'), ('rect', 0.41, 0.2, 0.59, 0.55, '#16181c'),
                                                                    ('rect', 0.7, 0.2, 0.88, 0.55, '#16181c'), ('shade', 0, 0, 1, 0.15, 1.3)]})   # thick front rim over the brow
    for sx in (1, -1):
        cb(hd, sx * 6.15, 18.2, 0.2, 0.9, 5.8, 6.0, 'steel', decals=ED)                               # side plates behind the eyes
        cb(hd, sx * 6.15, 22.2, -6.6, 0.9, 1.6, 6.8, 'steel', decals=ED)                              # side rim above the eyes
        cb(hd, sx * 6.15, 17.2, -1.6, 0.9, 1.4, 3.0, 'steel_d')                                       # down to the hinge
        cb(hd, sx * 6.65, 20.4, 1.6, 0.3, 0.8, 0.8, 'steel_l')                                        # rivets
        cb(hd, sx * 6.0, 25.0, -9.4, 0.8, 0.8, 0.6, 'steel_l')
    cb(hd, 0, 18.2, 3.4, 12.2, 7.0, 0.9, 'steel', decals=ED)                                          # back plate
    GX, GY, GZ = 6.8, 16.6, -1.6
    for sx in (1, -1):
        for (h, d) in ((4.0, 1.8), (1.8, 4.0), (3.2, 3.2)):
            cb(hd, sx * GX, GY - h / 2, GZ, 0.8, h, d, 'steel_d')                                     # gear
        for (dy, dz) in ((2.4, 0), (-2.4, 0), (0, 2.4), (0, -2.4)):
            cb(hd, sx * GX, GY + dy - 0.4, GZ + dz, 0.8, 0.8, 0.8, 'steel_d')                        # gear teeth
        cb(hd, sx * (GX + 0.5), GY - 0.6, GZ, 0.4, 1.2, 1.2, 'steel_l')                              # hub
    mo = made['jaw']
    MTJ = {g: [('shade', 0, 0, 1, 0.15, 1.25), ('shade', 0, 0.8, 1, 1, 0.8)] for g in ('north', 'south', 'east', 'west')}
    cb(mo, 0, 12.8, -7.4, 12.0, 2.4, 9.0, 'steel', decals=MTJ)                                      # all-steel jaw guard
    for sx in (1, -1):
        cb(mo, sx * 6.2, 13.4, -4.4, 0.8, 3.6, 6.4, 'steel', decals=MTJ)                              # guard side plates
        cb(mo, sx * 6.4, 14.8, -2.0, 0.8, 2.4, 2.2, 'steel_d')                                      # arm up to the gear hinge
    for i_, x in enumerate((-4.8, -2.4, 0, 2.4, 4.8)):
        h = 1.6 + (i_ % 2) * 0.8
        cb(mo, x, 15.2, -11.6, 2.0, h, 0.8, 'steel', decals={'north': [('rect', 0, 0, 1, 0.25, '#d8e0e8')]})   # jagged steel teeth on the rim
        cb(mo, x, 15.2 + h, -11.6, 0.8, 0.6, 0.8, 'steel_l')
    for sx in (1, -1):
        cb(mo, sx * 4.6, 13.4, -11.95, 0.8, 0.8, 0.3, 'steel_l')                                    # rivets
        cb(mo, sx * 1.6, 13.4, -11.95, 0.8, 0.8, 0.3, 'steel_l')
    cb(mo, 0, 15.4, -8.0, 7.6, 1.2, 4.6, 'fire_o'); cb(mo, 0, 16.4, -9.0, 5.6, 1.4, 2.0, 'fire')       # fiery glow in the mouth
    tk = m.bone('tc_tank', [0, 18, 3], body)
    for (h, d) in ((8.4, 5.6), (5.6, 8.4), (7.4, 7.4)):
        cb(body, 0, 17.6, 5.6, h * 0.0 + 8.0, h, d, 'wood', decals={g: [('fn', _staves(True, base=(176, 112, 58), seam=(110, 66, 30)))] for g in ('north', 'south', 'up', 'down')}) if False else None
    for (w, d) in ((8.0, 5.0), (5.0, 8.0), (7.0, 7.0)):                                                 # upright keg on the back
        cb(body, 0, 13.6, 7.6, w, 10.0, d, 'wood', decals={g: [('fn', _staves(False, base=(176, 112, 58), seam=(110, 66, 30)))] for g in ('north', 'south', 'east', 'west')})
    for y in (15.2, 21.0):
        for (w, d) in ((8.4, 5.4), (5.4, 8.4), (7.4, 7.4)):
            cb(tk, 0, y, 7.6, w, 1.0, d, 'tc')                                                         # team hoops
    cb(body, 0, 23.6, 7.6, 5.0, 0.6, 5.0, 'band')                                                     # lid
    for (x, y, z, w, h, d) in ((0, 23.8, 7.6, 1.4, 2.4, 1.4), (0, 25.6, 5.4, 1.4, 1.4, 4.4), (0, 25.0, 3.0, 1.4, 1.4, 1.4)):
        cb(body, x, y, z, w, h, d, 'brass')                                                            # brass pipe to the helmet
    m.hitbox(1.2, 1.6)
    return m


def magic_archer():
    """Magic Archer: slicked grey hair with swept tufts, black eye mask with glowing eyes, grey stubble beard, green tunic
    with laced front, leather pauldrons, gloves and belt with triangular buckle, team cape + collar, brown pants and
    boots, glowing magic bow with team-tinted limbs and a glowing arrow, quiver on the back."""
    m = new_model('clash_magic_archer')
    m.mats_({'skin': ('#e8b090', 'skin'), 'skin_d': ('#cc9070', 'skin'), 'hair': ('#b8bcc4', 'hair'), 'hair_d': ('#8e929a', 'hair'),
             'beard': ('#22201e', 'hair'), 'eyeglow': ('#9ee8ff', 'glow'), 'glow': ('#ffffff', 'glow'), 'green': ('#4a8a3a', 'cloth'), 'green_d': ('#36682a', 'cloth'),
             'leather': ('#7a4a2a', 'leather'), 'leather_d': ('#5a3420', 'leather'), 'gold': ('#d8a848', 'metal'), 'pants': ('#5a3e2c', 'cloth'),
             'boot': ('#4a3020', 'leather'), 'tc': ('#efefef', 'cloth'), 'bow': ('#bff4ff', 'glow'), 'aura': ('#7fe0ff', 'glow'), 'string': ('#ffffff', 'glow')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.0
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 4.0, 0, 3.8, 8.0, 3.8, 'pants', decals={f: [('fn', _folds())] for f in ('north', 'south', 'east', 'west')})   # pants
        cb(lg, x, 0, -0.4, 4.0, 5.0, 4.6, 'boot', decals={'up': [('shade', 0, 0, 1, 1, 1.2)]})          # boots
        cb(lg, x, 4.4, 0, 4.4, 1.2, 4.4, 'leather_d')                                                   # cuffs
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 10.0, 0, 8.4, 4.0, 4.8, 'green_d', decals={f: [('fn', _folds())] for f in ('north', 'south', 'east', 'west')})   # tunic skirt
    cb(body, 0, 13.8, 0, 8.0, 10.2, 4.2, 'green', decals={'north': [('rect', 0.46, 0, 0.54, 1, '#2a4e20'), ('fn', _folds(0.9, 1.05, 2))]})   # green tunic
    for y in (16.0, 18.0, 20.0, 22.0):
        cb(body, 0, y, -2.2, 2.0, 0.4, 0.2, 'leather_d')                                                # laces
    cb(body, 0, 13.6, 0, 8.8, 1.8, 5.2, 'leather')                                                       # belt
    for (w, y) in ((2.8, 13.0), (1.8, 12.4), (0.8, 11.8)):
        cb(body, 0, y, -2.75, w, 0.8, 0.4, 'gold')                                                      # triangular buckle
    cb(body, 0, 22.8, 0.2, 8.6, 1.6, 5.0, 'leather_d')                                                   # leather collar strap
    tc = m.bone('tc_cape', [0, 24, 2], body)
    cb(tc, 0, 8.0, 2.6, 8.8, 15.8, 0.7, 'tc', decals={'south': [('fn', _folds(0.8, 1.1, 2)), ('lerp', '#c0c0c0', 0.6, 1.0, 'y')]})   # team cape
    cb(tc, 0, 23.2, 0.8, 9.4, 1.8, 5.2, 'tc')                                                            # cape collar
    for sx in (1, -1):
        cb(tc, sx * 3.0, 22.0, -2.4, 2.6, 1.6, 0.6, 'tc', rot=('z', sx * 22.5), rot_origin=[sx * 3.0, 22.8, -2.4])   # collar points
    qv = m.bone('quiver', [0, 20, 3], body)
    cb(qv, 2.0, 15.0, 3.6, 2.6, 8.0, 2.6, 'leather', rot=('z', -22.5), rot_origin=[2.0, 19, 3.6])
    for dx in (-0.6, 0.6):
        cb(qv, 2.0 + dx, 23.0, 3.6, 0.5, 2.6, 0.5, 'glow', rot=('z', -22.5), rot_origin=[2.0, 19, 3.6])   # glowing arrows
    hd = m.bone('head', [0, 24, 0], body)
    cb(hd, 0, 24, 0, 8, 8, 8, S, dens=2)
    for sx in (1, -1):
        cb(hd, sx * 1.8, 27.4, -4.05, 1.8, 1.0, 0.2, 'glow')                                               # glowing white eyes
        cb(hd, sx * 1.8, 27.2, -4.02, 2.4, 1.4, 0.1, 'eyeglow')                                            # soft glow around them
        cb(hd, sx * 1.6, 28.6, -4.3, 2.8, 1.6, 1.0, 'beard', decals={'up': [('shade', 0, 0, 1, 1, 1.25)]})   # bushy sage brows
        cb(hd, sx * 3.4, 29.0, -4.2, 1.6, 1.2, 1.0, 'beard', rot=('z', -sx * 22.5), rot_origin=[sx * 2.8, 29.6, -4.2])   # short outer end
        cb(hd, sx * 1.2, 30.0, -4.1, 1.6, 0.6, 0.8, 'hair_d')                                              # grey streaks
        cb(hd, sx * 4.15, 23.6, -3.0, 0.4, 3.2, 1.6, 'beard')                                              # black sideburns into beard
        cb(hd, sx * 4.15, 28.8, 1.6, 0.4, 2.8, 5.0, 'hair')                                                # short grey hair at the sides
        cb(hd, sx * 1.6, 25.2, -4.2, 2.6, 0.9, 0.6, 'beard')                                               # moustache
    cb(hd, 0, 23.6, -4.15, 7.4, 2.0, 0.6, 'beard', decals={'north': [('rect', 0.32, 0.0, 0.68, 0.3, '#a85a4a')]})   # short black beard + mouth
    cb(hd, 0, 22.8, -3.8, 4.4, 1.2, 1.0, 'beard')                                                          # chin tuft
    cb(hd, 0, 26.0, -4.4, 1.6, 2.0, 1.0, 'skin_d')                                                       # nose
    cb(hd, 0, 31.6, 0.4, 8.6, 1.4, 8.6, 'hair', decals={'up': [('rect', 0, 0.3, 1, 0.36, '#8e929a'), ('rect', 0, 0.6, 1, 0.66, '#8e929a')]})   # slicked back hair
    cb(hd, 0, 26.0, 4.2, 8.4, 6.6, 0.8, 'hair')
    for sx in (1, -1):
        cb(hd, sx * 3.2, 32.6, -2.6, 2.4, 1.4, 2.4, 'hair', rot=('z', -sx * 22.5), rot_origin=[sx * 3.2, 33, -2.6])   # swept tufts
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.0
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x, 16.4, 0, 3.6, 5.6, 3.6, S, decals={'north': [('lerp', '#cc9070', 0.8, 1.0, 'y')]})      # bare upper arm
        cb(a, x + sx * 0.2, 20.0, 0, 4.4, 3.2, 4.6, 'leather', decals={'up': [('shade', 0, 0, 1, 1, 1.15)]})   # leather pauldron
        cb(a, x, 10.0, 0, 3.8, 6.6, 3.8, 'leather', decals={'north': [('lerp', '#5a3420', 0.6, 1.0, 'y')]})   # long glove
        cb(a, x, 15.8, 0, 4.2, 1.2, 4.2, 'leather_d')
    bw = m.bone('bow', [-6, 10, -1], m.by_name('arm_l'))
    tb = m.bone('tc_bow_limbs', [-6, 10, -1], bw)
    K = 1.35                                                                                 # bigger glowing magic bow
    Y = lambda d: 10 + d * K
    cb(bw, -6, Y(-1.8), -1.0, 1.6, 3.6 * K, 1.8, 'leather_d')                               # grip
    cb(tb, -6, Y(-0.4), -1.0, 1.8, 1.0, 2.0, 'tc'); cb(tb, -6, Y(-2.2), -1.0, 1.8, 1.0, 2.0, 'tc')   # team wraps on the grip
    segs = [(2.0, -0.4, 1.4), (3.8, -1.0, 1.2), (5.6, -1.4, 1.1), (7.4, -1.4, 1.0), (9.0, -0.8, 0.9), (10.2, 0.2, 0.8)]
    for sy in (1, -1):
        for j_, (dy, dz, th) in enumerate(segs):
            h = (1.9 if j_ < 5 else 1.3) * K
            yb = Y(dy) if sy > 0 else Y(-dy) - h
            cb(bw, -6, yb, -1.0 + dz * K, 1.2, h, th * K, 'bow', decals={g: [('rect', 0.1, 0, 0.35, 1, '#ffffff')] for g in ('north', 'south', 'east', 'west')})   # glowing limbs
            cb(bw, -6, yb, -1.0 + dz * K, 1.7, h, th * K * 0.5, 'aura')                           # glow halo
        ty = Y(11.4) if sy > 0 else Y(-12.6)
        for (w, hh) in ((2.2, 1.0), (1.2, 2.2)):
            cb(bw, -6, ty + (0.6 - hh / 2), 0.0, w * 0.6, hh, w, 'glow')                       # star-shaped glowing tips
        for (dx, dy, dz) in ((0.6, 1.8, -1.2), (-0.4, 2.6, 0.8), (0.2, -1.4, 1.6)):
            cb(bw, -6 + dx, ty + dy * sy, dz, 0.4, 0.4, 0.4, 'glow')                            # sparkles
    cb(bw, -6, Y(-11.8), 0.6, 0.3, 23.6 * K, 0.3, 'string')                                   # glowing string
    ar = m.bone('arrow_tip', [-6, 10, -3], bw)
    cb(ar, -6.9, 11.2, -5.2, 0.6, 0.6, 13.0, 'glow')                                          # glowing arrow
    cb(ar, -6.9, 10.9, -5.2, 1.2, 1.2, 13.0, 'aura')                                          # arrow glow halo
    for (w, d, z) in ((2.2, 1.0, -12.0), (1.4, 1.0, -13.0), (0.6, 0.8, -13.8)):
        cb(ar, -6.9, 11.5 - w / 2, z, 0.6, w, d, 'bow')                                       # arrowhead
    for z in (0.4, 1.4):
        cb(ar, -6.9, 10.6, z, 0.3, 1.8, 0.8, 'bow')                                           # glowing fletching
    m.hitbox(0.8, 2.2)
    return m


def electro_wizard():
    """Electro Wizard: wild spiky black hair, huge black brows + handlebar moustache, cyan eyes, gritted teeth, team vest
    with gold trim + high flared collar over a navy shirt, brown belt + gold buckle, navy pants, black boots, team
    wristbands, grey gloves crackling with lightning."""
    m = new_model('clash_electro_wizard')
    m.mats_({'skin': ('#f0c0a4', 'skin'), 'skin_d': ('#d8a088', 'skin'), 'hair': ('#1e2026', 'hair'), 'hair_l': ('#3a3e48', 'hair'),
             'tc': ('#efefef', 'cloth'), 'gold': ('#e8c050', 'metal'), 'navy': ('#22325a', 'cloth'), 'belt': ('#7a5236', 'leather'),
             'boot': ('#26262a', 'leather'), 'glove': ('#4a4c54', 'leather'), 'zap': ('#aef4ff', 'glow'), 'zap_w': ('#ffffff', 'glow')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.55
        lg = m.bone('leg_' + side, [x, 11, 0], root)
        cb(lg, x, 4.0, 0, 3.8, 7.4, 3.8, 'navy', decals={f: [('fn', _folds())] for f in ('north', 'south', 'east', 'west')})   # navy pants
        cb(lg, x, 0, -0.4, 4.0, 4.4, 4.6, 'boot', decals={'up': [('shade', 0, 0, 1, 1, 1.2)]})          # black boots
        cb(lg, x, 0, -2.4, 3.0, 1.4, 1.2, 'boot')
    body = m.bone('body', [0, 11, 0], root)
    cb(body, 0, 10.0, 0, 7.6, 12.4, 4.2, 'navy', decals={'north': [('rect', 0.47, 0.75, 0.53, 1, '#141e38')]})   # navy shirt
    cb(body, 0, 13.0, 0, 8.6, 2.2, 5.0, 'belt')                                                          # belt
    cb(body, 0, 12.8, -2.65, 3.0, 2.6, 0.4, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#7a5236')]})   # buckle
    tm = m.bone('tc_mantle', [0, 22.5, 0], body)
    for sx in (1, -1):
        cb(tm, sx * 3.1, 8.6, -0.1, 2.4, 13.8, 4.8, 'tc', decals={'north': [('rect', 0.0 if sx > 0 else 0.8, 0, 0.2 if sx > 0 else 1.0, 1, '#e8c050'), ('rect', 0, 0, 1, 0.06, '#e8c050')]})   # open team vest with gold edge
        cb(tm, sx * 4.6, 21.6, 0.4, 3.6, 3.2, 5.8, 'tc', rot=('z', sx * 22.5), rot_origin=[sx * 3.0, 21.4, 0.4],
           decals={g: [('rect', 0, 0, 1, 0.15, '#e8c050')] for g in ('north', 'south', 'east', 'west', 'up')})   # flared shoulder collar
    cb(tm, 0, 8.6, 2.45, 8.8, 13.8, 0.6, 'tc', decals={'south': [('rect', 0, 0, 1, 0.06, '#e8c050')]})   # vest back
    for sx in (1, -1):                                                                                   # gold trim (separate so it stays gold)
        cb(body, sx * 2.0, 8.6, -2.55, 0.6, 13.8, 0.2, 'gold')                                          # front edges
        cb(body, sx * 3.1, 8.4, -0.1, 2.6, 0.5, 5.0, 'gold')                                            # hem
        cb(body, sx * 5.2, 21.2, 0.4, 3.6, 0.5, 6.0, 'gold', rot=('z', sx * 22.5), rot_origin=[sx * 3.0, 21.4, 0.4])   # collar rim
    cb(body, 0, 24.6, 2.2, 8.6, 0.5, 1.2, 'gold')
    cb(tm, 0, 20.6, 2.2, 8.4, 4.0, 1.0, 'tc', decals={g: [('rect', 0, 0, 1, 0.15, '#e8c050')] for g in ('north', 'south', 'up')})   # high collar behind the neck
    hd = m.bone('head', [0, 22.5, 0], body)
    face = pix(["........", "........", "........", "........", ".wb..bw.", "........", "........", "........"], {'w': '#ffffff', 'b': '#2ab8e0'})
    face += [('rect', 0.28, 0.8, 0.72, 0.87, '#ffffff'), ('rect', 0.28, 0.83, 0.72, 0.84, '#7a2a2a')]   # gritted teeth
    cb(hd, 0, 22.6, -0.2, 7.8, 8.4, 7.6, S, decals={'north': face}, dens=2)
    cb(hd, 0, 26.0, -4.2, 2.0, 2.6, 1.4, 'skin_d')                                                       # big nose
    for sx in (1, -1):
        cb(hd, sx * 2.0, 28.4, -4.1, 3.6, 1.4, 0.8, 'hair', rot=('z', sx * 22.5), rot_origin=[sx * 2.0, 29.1, -4.1])   # huge angry brows
        cb(hd, sx * 2.0, 24.6, -4.2, 3.4, 1.2, 0.9, 'hair')                                              # handlebar moustache
        cb(hd, sx * 3.8, 25.2, -4.1, 1.2, 1.6, 0.8, 'hair')                                              # curled-up tips
        cb(hd, sx * 3.95, 26.0, 0.6, 0.6, 4.4, 4.6, 'hair')                                              # sideburns
    hr = m.bone('hair', [0, 30.2, 0], hd)
    cb(hr, 0, 30.4, 0.4, 8.6, 2.4, 8.4, 'hair')                                                          # hair mass
    cb(hr, 0, 24.0, 4.0, 8.4, 7.0, 1.0, 'hair')                                                          # back
    HD = {g: [('rect', 0.1, 0, 0.35, 1, '#3a3e48')] for g in ('north', 'south', 'east', 'west')}
    spikes = [(0, 0.4, 32.2, 9.0, None, 0), (-2.4, -1.6, 32.2, 7.6, 'z', 22.5), (2.4, -1.6, 32.2, 7.6, 'z', -22.5),
              (-3.8, 0.4, 31.6, 8.0, 'z', 45), (3.8, 0.4, 31.6, 8.0, 'z', -45), (0, 3.4, 31.6, 8.4, 'x', -45),
              (-2.6, 2.8, 32.0, 7.0, 'x', -22.5), (2.6, 2.8, 32.0, 7.0, 'x', -22.5), (0, -3.2, 31.8, 6.0, 'x', 22.5),
              (-4.0, 0.6, 28.4, 7.4, 'z', 45), (4.0, 0.6, 28.4, 7.4, 'z', -45), (-4.0, 3.0, 26.0, 6.4, 'z', 45), (4.0, 3.0, 26.0, 6.4, 'z', -45),
              (-2.0, 4.0, 27.6, 7.0, 'x', -45), (2.0, 4.0, 27.6, 7.0, 'x', -45), (0, 4.0, 24.6, 6.0, 'x', -45)]
    for (x, z, y0, H, ang_ax, ang) in spikes:
        kw = dict(rot=(ang_ax, ang), rot_origin=[x, y0, z]) if ang_ax else {}
        y = y0
        for k, (fw, fh) in enumerate(((2.6, 0.34), (1.9, 0.28), (1.2, 0.22), (0.6, 0.16))):             # long jagged spikes in every direction
            cb(hr, x + (0.4 if k == 1 else -0.3 if k == 2 else 0.2 if k == 3 else 0), y, z, fw, H * fh, fw, 'hair', decals=HD, **kw)
            y += H * fh
    sp = m.bone('sparks', [0, 33.6, 0], hd)
    for (x, y, z) in ((3.6, 36.6, -1.0), (-3.8, 35.4, 0.6), (0.6, 38.6, 1.4)):
        cb(sp, x, y, z, 0.5, 1.8, 0.5, 'zap'); cb(sp, x + 0.5, y + 1.6, z, 1.2, 0.5, 0.5, 'zap')        # little zaps in the hair
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.8
        a = m.bone('arm_' + side, [sx * 6.75, 21.3, 0], body)
        cb(a, x, 13.6, 0, 3.2, 7.6, 3.2, S, decals={'north': [('lerp', '#d8a088', 0.8, 1.0, 'y')]})       # bare arms
        tw = m.bone('tc_wrist_' + side, [x, 13, 0], a)
        cb(tw, x, 12.2, 0, 3.8, 1.8, 3.8, 'tc')                                                           # team wristband
        cb(a, x, 8.6, 0, 3.4, 3.8, 3.4, 'glove', decals={'north': [('rect', 0, 0.7, 1, 1, '#2a2c32')]})  # grey glove
        ob = m.bone('orb_' + side, [sx * 6.75, 9.1, -2], a)
        for (dx, dy, dz, w, h, d) in ((0, 7.0, -2.2, 0.6, 3.2, 0.6), (0.8, 9.8, -2.2, 1.8, 0.6, 0.6), (1.6, 10.2, -2.6, 0.6, 2.6, 0.6),
                                      (-1.4, 6.4, -1.0, 0.6, 2.4, 0.6), (-2.2, 8.4, -1.0, 1.6, 0.6, 0.6), (0.4, 5.6, -3.2, 0.6, 0.6, 2.4),
                                      (sx * 2.2, 8.2, 0.4, 2.4, 0.6, 0.6), (sx * 3.2, 8.8, 0.4, 0.6, 2.0, 0.6)):
            cb(ob, x + dx, dy, dz, w * 1.6 if w < 1 else w, h * 1.0, d * 1.6 if d < 1 else d, 'zap')         # crackling lightning bolts
        cb(ob, x, 7.6, -2.0, 1.6, 1.6, 1.6, 'zap_w')                                                     # bright core
    m.hitbox(0.9, 2.3)
    return m


def ice_wizard():
    """Ice Wizard: spiky icy hair, frosty brows + goatee, team shirt/trousers/belt, dark leather fur-trimmed vest with
    hood at the back, icy hands holding ice shards, black boots."""
    m = new_model('clash_ice_wizard')
    m.mats_({'skin': ('#f0c0a4', 'skin'), 'skin_d': ('#d8a088', 'skin'), 'ice': ('#9ad8f4', 'gem'), 'ice_l': ('#d8f4ff', 'glow'),
             'ice_d': ('#5ab0e0', 'gem'), 'vest': ('#4a4648', 'leather'), 'vest_d': ('#36332f', 'leather'), 'fur': ('#bdb6aa', 'fur'),
             'fur_d': ('#9a9488', 'fur'), 'tc': ('#efefef', 'cloth'), 'gold': ('#e2b23a', 'metal'), 'boot': ('#26262a', 'leather')})
    S = 'skin'
    FUR = lambda: {f: [('fn', _folds(0.85, 1.1, 1))] for f in ('north', 'south', 'east', 'west', 'up')}
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.2
        lg = m.bone('leg_' + side, [x, 9, 0], root)
        tl = m.bone('tc_leg_' + side, [x, 9, 0], lg)
        cb(tl, x, 3.0, 0, 3.6, 6.0, 3.6, 'tc', decals={f: [('lerp', '#c8c8c8', 0.6, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # team trousers
        cb(lg, x, 0, -0.4, 3.8, 3.4, 4.6, 'boot', decals={'up': [('shade', 0, 0, 1, 1, 1.2)]})          # black boots
        cb(lg, x, 3.0, 0, 4.0, 0.8, 4.0, 'boot')
    body = m.bone('body', [0, 9, 0], root)
    tb = m.bone('tc_body', [0, 9, 0], body)
    cb(tb, 0, 9.0, 0, 7.4, 11.0, 4.2, 'tc')                                                              # team shirt
    cb(tb, 0, 10.8, 0, 8.6, 1.8, 5.4, 'tc', decals={f: [('shade', 0, 0, 1, 1, 0.85)] for f in ('north', 'south', 'east', 'west')})   # team belt
    cb(body, 0, 10.6, -2.85, 2.8, 2.2, 0.4, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#4a3a20')]})   # gold buckle
    for sx in (1, -1):                                                                                   # open leather vest panels
        cb(body, sx * 3.4, 6.4, -0.1, 1.8, 13.6, 4.8, 'vest', decals={'north': [('lerp', '#36332f', 0.7, 1.0, 'y')]})
        cb(body, sx * 2.6, 7.2, -2.55, 1.2, 12.0, 0.9, 'fur', decals=FUR())                               # fur trim down the front
        cb(body, sx * 3.0, 6.0, -0.1, 3.0, 1.2, 5.2, 'fur', decals=FUR())                                 # fur hem
    cb(body, 0, 6.4, 2.4, 8.4, 13.6, 0.8, 'vest', decals={'south': [('lerp', '#36332f', 0.6, 1.0, 'y')]})   # vest back
    cb(body, 0, 6.0, 2.5, 8.6, 1.2, 1.2, 'fur', decals=FUR())
    cb(body, 0, 19.0, 0.4, 9.0, 2.4, 6.2, 'fur', decals=FUR())                                            # big fur collar
    for sx in (1, -1):
        cb(body, sx * 3.6, 16.4, -2.2, 1.8, 3.2, 1.4, 'fur', decals=FUR())
    cb(body, 0, 15.4, 3.6, 6.4, 5.0, 1.6, 'vest_d')                                                      # hood bunched at the back
    hd = m.bone('head', [0, 20, 0], body)
    face = pix(["........", "........", "........", "........", ".wb..bw.", ".wb..bw.", "........", "........"], {'w': '#ffffff', 'b': '#3a8ad8'})
    cb(hd, 0, 20.6, 0, 7.6, 8.0, 7.4, S, decals={'north': face}, dens=2)
    cb(hd, 0, 23.8, -4.0, 1.8, 2.2, 1.0, 'skin_d')                                                       # nose
    for sx in (1, -1):
        cb(hd, sx * 2.1, 26.2, -3.95, 3.2, 1.2, 0.8, 'ice_l', rot=('z', sx * 22.5), rot_origin=[sx * 2.1, 26.8, -3.95],
           decals={'north': [('shade', 0, 0.6, 1, 1, 0.85)]})                                            # thick frosty brows (angry)
        cb(hd, sx * 1.6, 22.6, -4.0, 2.6, 1.0, 0.8, 'ice', decals={'north': [('shade', 0, 0.5, 1, 1, 0.85)]})   # moustache wings
        cb(hd, sx * 2.9, 21.4, -4.0, 0.9, 1.6, 0.8, 'ice')                                                # drooping ends
    cb(hd, 0, 21.4, -4.05, 1.4, 0.5, 0.2, 'void' if False else 'skin_d')                                 # mouth gap
    cb(hd, 0, 19.2, -3.9, 2.4, 1.6, 1.0, 'ice_d'); cb(hd, 0, 18.0, -3.6, 1.4, 1.4, 0.8, 'ice_d')          # separate pointed goatee
    cb(hd, 0, 26.8, 0.6, 8.0, 1.2, 7.6, 'ice_d')                                                         # hair base
    HB = {g: [('fn', _folds(0.85, 1.1, 1)), ('lerp', '#9ad8f4', 0.0, 0.3, 'y')] for g in ('north', 'south', 'east', 'west')}
    cb(hd, 0, 20.4, 3.9, 8.0, 7.8, 0.8, 'ice_d', decals=HB)                                               # icy hair covering the back
    for sx in (1, -1):
        cb(hd, sx * 3.95, 23.6, 1.6, 0.8, 4.6, 4.6, 'ice_d', decals=HB)                                    # hair over the sides
    for (x_, y_, h_) in ((-2.4, 21.0, 3.6), (0, 20.4, 4.4), (2.4, 21.0, 3.6), (-1.2, 24.6, 3.0), (1.2, 24.6, 3.0)):   # backward spikes
        z_ = 4.3
        for k, (fw, fh) in enumerate(((1.0, 0.45), (0.6, 0.35), (0.3, 0.2))):
            cb(hd, x_, y_ - 1.2 * fw, z_, 2.4 * fw, 2.4 * fw, h_ * fh, 'ice' if k < 2 else 'ice_l', decals={g: [('rect', 0.12, 0, 0.4, 1, '#e8f8ff')] for g in ('north', 'east', 'west', 'south', 'up', 'down')})
            z_ += h_ * fh
    SP = {g: [('rect', 0.12, 0, 0.4, 1, '#e8f8ff'), ('shade', 0.6, 0, 1, 1, 0.82)] for g in ('north', 'east', 'west', 'south')}
    for (x, z, H, W, rx, rz) in ((0, -1.6, 9.0, 3.0, 0, 0), (-2.4, -1.0, 7.4, 2.6, 0, 22.5), (2.4, -1.0, 7.4, 2.6, 0, -22.5),
                                 (0, 1.4, 8.4, 3.0, -22.5, 0), (-2.6, 1.8, 6.6, 2.4, -22.5, 22.5), (2.6, 1.8, 6.6, 2.4, -22.5, -22.5),
                                 (0, 3.4, 6.0, 2.6, -45, 0), (-3.4, -0.6, 5.0, 2.0, 0, 45), (3.4, -0.6, 5.0, 2.0, 0, -45)):
        rot = None
        if rx and rz: rot = ('x', rx)
        elif rx: rot = ('x', rx)
        elif rz: rot = ('z', rz)
        kw = dict(rot=rot, rot_origin=[x, 27.6, z]) if rot else {}
        y = 27.6
        for k, (fw, fh) in enumerate(((1.0, 0.34), (0.72, 0.28), (0.46, 0.22), (0.22, 0.16))):       # tapering ice spike
            cb(hd, x, y, z, W * fw, H * fh, W * fw, 'ice' if k < 2 else 'ice_l', decals=SP, **kw)
            y += H * fh
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.6
        a = m.bone('arm_' + side, [sx * 6.5, 18, 0], body)
        cb(a, x, 14.0, 0, 3.4, 4.4, 3.4, 'tc' if False else S)                                            # bare upper arm
        cb(a, x, 16.6, 0, 3.8, 2.6, 3.8, 'vest')                                                          # short sleeve cap
        cb(a, x, 8.8, 0, 3.2, 5.2, 3.2, 'ice', decals={f: [('lerp', '#f0c0a4', 0.0, 0.0, 'y'), ('lerp', '#f0c0a4', 0.0, 0.0, 'y')] for f in ('north',)})   # frozen icy forearm + hand
        cb(a, x, 12.4, 0, 3.3, 1.8, 3.3, 'ice_d')
        fr = m.bone('frost_' + side, [sx * 6.5, 7.5, -1], a)
        for (dx, dz, h, w) in ((0, -1.2, 4.4, 1.4), (-0.8, -0.2, 3.4, 1.2), (0.8, -0.6, 3.0, 1.0), (0.2, 0.6, 2.4, 1.0)):
            cb(fr, x + dx, 5.6, dz - 1.0, w, h * 0.6, w, 'ice', decals={'north': [('rect', 0.15, 0, 0.45, 1, '#d8f4ff')]})   # ice shards in the palm
            cb(fr, x + dx, 5.6 + h * 0.6, dz - 1.0, w * 0.55, h * 0.4, w * 0.55, 'ice_l')
    m.hitbox(0.8, 2.2)
    return m


def bandit():
    """Bandit: green hood + long cape, white bob with blunt bangs, black eye mask with blue eyes, team dress with belt +
    gold buckle, brown gloves and boots, wooden club in the right hand."""
    m = new_model('clash_bandit')
    m.mats_({'skin': ('#f2c0a0', 'skin'), 'skin_d': ('#d8a080', 'skin'), 'hair': ('#eceef2', 'hair'), 'hair_d': ('#c4c8d0', 'hair'),
             'mask': ('#26282e', 'soft'), 'hood': ('#3e7a3a', 'soft'), 'hood_d': ('#2c5a2a', 'soft'), 'tc': ('#efefef', 'cloth'),
             'belt': ('#6a4026', 'leather'), 'gold': ('#e2b23a', 'metal'), 'glove': ('#6a3e26', 'leather'), 'boot': ('#6a3e26', 'leather'),
             'wood': ('#a8703a', 'soft')})
    S = 'skin'
    FD = lambda: {f: [('fn', _folds())] for f in ('north', 'south', 'east', 'west')}
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.8
        lg = m.bone('leg_' + side, [x, 9, 0], root)
        cb(lg, x, 3.4, 0, 2.6, 5.6, 2.6, S, decals={'north': [('lerp', '#d8a080', 0.8, 1.0, 'y')]})       # legs
        cb(lg, x, 0, -0.3, 3.2, 3.6, 3.4, 'boot', decals={'up': [('shade', 0, 0, 1, 1, 1.1)]})          # boots
        cb(lg, x, 3.2, 0, 3.8, 1.2, 3.8, 'boot', decals={f: [('shade', 0, 0, 1, 0.3, 1.2)] for f in ('north', 'south', 'east', 'west')})   # folded cuffs
        cb(lg, x, 1.6, -1.75, 3.3, 0.5, 0.2, 'belt'); cb(lg, x + sx * 0.6, 1.5, -1.9, 0.6, 0.7, 0.2, 'gold')   # strap + buckle
        cb(lg, x, 0, -1.6, 2.8, 1.2, 1.0, 'boot')                                                       # toe
    body = m.bone('body', [0, 9, 0], root)
    tb = m.bone('tc_body', [0, 9, 0], body)
    cb(tb, 0, 6.6, 0, 7.6, 5.0, 4.6, 'tc', decals={f: [('fn', _folds()), ('lerp', '#c8c8c8', 0.7, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # flared dress skirt
    cb(tb, 0, 11.6, 0, 6.8, 7.4, 3.8, 'tc', decals={'north': [('rect', 0.42, 0.8, 0.58, 1, '#f2c0a0')]})   # bodice
    cb(body, 0, 11.4, 0, 7.4, 1.4, 4.4, 'belt')                                                         # belt
    cb(body, 0, 11.2, -2.3, 2.2, 1.8, 0.3, 'gold', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#6a4026')]})
    cb(tb, 0, 6.4, 0, 8.0, 0.8, 5.0, 'tc', decals={f: [('shade', 0, 0, 1, 1, 0.7)] for f in ('north', 'south', 'east', 'west')})   # dark hem band
    cb(body, 1.8, 7.2, -2.45, 0.6, 4.0, 0.2, 'belt')                                                     # skirt slit trim
    for y_ in (13.0, 14.4, 15.8):
        cb(body, 0, y_, -1.98, 0.6, 0.6, 0.2, 'gold')                                                   # bodice buttons
    cb(body, 0, 14.6, -0.1, 7.2, 0.8, 4.2, 'belt', rot=('z', -45), rot_origin=[0, 14.6, -0.1])          # cross strap
    cb(body, -3.0, 9.6, -1.4, 2.2, 2.4, 1.6, 'belt', decals={'north': [('rect', 0, 0, 1, 0.3, '#4e2c1a'), ('rect', 0.4, 0.3, 0.6, 0.5, '#e2b23a')]})   # belt pouch
    cb(body, 3.4, 8.8, -0.4, 1.0, 3.4, 1.4, 'belt')                                                      # dagger sheath
    cb(body, 3.4, 12.2, -0.4, 1.2, 0.8, 1.6, 'gold'); cb(body, 3.4, 13.0, -0.4, 0.8, 1.4, 0.8, 'glove')   # dagger hilt
    cb(body, 0, 16.8, -0.2, 6.0, 1.4, 4.6, 'hood_d')                                                     # dark neck scarf
    for sx in (1, -1):
        cb(body, sx * 3.4, 16.2, 0.4, 3.0, 2.2, 4.8, 'hood', decals={'up': [('shade', 0, 0, 1, 1, 1.1)]})   # cape draped over the shoulders
    cb(body, 0, 16.2, 2.4, 8.4, 2.4, 1.2, 'hood')
    tp = m.bone('tc_patch', [0, 13, 2.9], body)
    cb(tp, 0, 13.6, 2.15, 2.4, 1.4, 0.2, 'tc')                                                         # little team clasp
    cb(body, 0, 2.2, 2.6, 8.8, 16.8, 0.7, 'hood', decals={'south': [('fn', _folds(0.8, 1.12, 2)), ('lerp', '#2c5a2a', 0.6, 1.0, 'y')]})   # long green cape
    for sx in (1, -1):
        cb(body, sx * 4.2, 3.0, 1.4, 0.6, 15.0, 2.4, 'hood_d')
    hd = m.bone('head', [0, 19, 0], body)
    face = pix(["........", "........", "........", "........", "........", "........", "...rr...", "........"], {'r': '#c25a5a'})
    cb(hd, 0, 19, 0, 7.6, 7.6, 7.4, S, decals={'north': face}, dens=2)
    cb(hd, 0, 22.4, -3.75, 7.8, 1.8, 0.2, 'mask', decals={'north': [('rect', 0.12, 0.2, 0.38, 0.8, '#ffffff'), ('rect', 0.62, 0.2, 0.88, 0.8, '#ffffff'),
                                                              ('rect', 0.22, 0.2, 0.34, 0.8, '#3a7ad8'), ('rect', 0.66, 0.2, 0.78, 0.8, '#3a7ad8')]}, dens=3)   # eye mask
    cb(hd, 0, 24.6, -3.8, 7.8, 1.6, 0.4, 'hair', decals={'north': [('rect', 0, 0.8, 1, 1, '#c4c8d0')]})   # blunt bangs
    for sx in (1, -1):
        cb(hd, sx * 3.9, 19.4, -1.2, 1.4, 6.8, 5.4, 'hair', decals={'north': [('rect', 0, 0, 1, 1, '#eceef2')], 'east': [('fn', _folds(0.9, 1.05, 1))], 'west': [('fn', _folds(0.9, 1.05, 1))]})   # white bob sides
    cb(hd, 0, 19.6, 3.4, 8.0, 6.6, 1.0, 'hair')
    cb(hd, 0, 26.6, 0.2, 7.8, 0.8, 7.6, 'hair', decals={'up': [('fn', _folds(0.92, 1.05, 1))]})                # white hair on the crown (under the hood)
    pt = m.bone('ponytail', [0, 24, 4.8], hd)                                                            # (kept bone) hood
    HD = {f: [('fn', _folds(0.85, 1.08, 2)), ('lerp', '#5a9a52', 0.0, 0.3, 'y')] for f in ('north', 'south', 'east', 'west', 'up')}
    cb(pt, 0, 26.6, 0.2, 10.2, 2.0, 8.8, 'hood', decals=HD)                                               # hood top
    cb(pt, 0, 28.8, 1.4, 6.0, 1.0, 6.0, 'hood', decals=HD)                                               # peak
    for sx in (1, -1):
        cb(pt, sx * 5.0, 18.6, 1.4, 0.8, 9.6, 6.6, 'hood', decals=HD)                                    # hood sides
        cb(pt, sx * 4.7, 18.8, -1.9, 0.4, 8.8, 0.4, 'hood_d')                                            # dark rim
    cb(pt, 0, 18.4, 4.6, 9.6, 10.4, 0.8, 'hood', decals=HD)
    cb(pt, 0, 26.2, -4.2, 9.6, 0.8, 1.0, 'hood_d')                                                       # brim shadow
    cb(pt, 0, 17.6, 1.6, 9.0, 1.6, 6.0, 'hood_d')                                                        # collar drape
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.6
        a = m.bone('arm_' + side, [x, 17, 0], body)
        ta = m.bone('tc_arm_' + side, [x, 17, 0], a)
        cb(ta, x, 12.6, 0, 2.6, 5.0, 2.6, 'tc')                                                          # team sleeve
        cb(a, x, 8.4, 0, 3.0, 4.6, 3.0, 'glove', decals={'north': [('lerp', '#4e2c1a', 0.7, 1.0, 'y')]})   # brown glove
        cb(a, x, 11.6, 0, 3.8, 1.8, 3.8, 'glove', decals={f: [('shade', 0, 0, 1, 0.25, 1.2)] for f in ('north', 'south', 'east', 'west')})   # flared gauntlet cuff
        cb(a, x, 14.0, 0, 2.8, 0.5, 2.8, 'belt')                                                        # arm band
    cl = m.bone('club', [5.5, 12, -1], m.by_name('arm_r'))
    cb(cl, 4.6, 8.8, -1.0, 1.4, 1.4, 4.0, 'wood', decals={f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})   # handle
    cb(cl, 4.6, 8.4, -6.2, 2.2, 2.2, 6.4, 'wood', decals={f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})   # thick club head
    cb(cl, 4.6, 8.3, -9.5, 2.4, 2.4, 0.2, 'wood', decals={'north': [('ering', 0.5, 0.5, 0.4, 0.4, 0.15, '#6a4026')]})   # end grain swirl
    m.hitbox(0.7, 1.8)
    return m


def wall_breaker():
    """Wall Breaker: skinny skeleton running with a big banded powder keg held overhead in both bony hands; big skull with
    deep sockets and a gaping toothy grin, team bandana with flapping tails, lit fuse sparking at the keg end."""
    m = new_model('clash_wall_breaker')
    m.mats_({'bone': ('#ece6d6', 'soft'), 'bone_d': ('#c8c0ac', 'soft'), 'void': ('#1c1a1a', 'plain'), 'tooth': ('#f8f4ea', 'soft'),
             'tc': ('#efefef', 'cloth'), 'wood': ('#b8743a', 'soft'), 'band': ('#8a929c', 'soft'), 'band_l': ('#b8c0ca', 'soft'),
             'fuse': ('#c8a060', 'rope'), 'spark': ('#ffd040', 'glow'), 'spark_w': ('#fff6c0', 'glow')})
    B = 'bone'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.1
        lg = m.bone('leg_' + side, [x, 6.6, 0], root)
        cb(lg, x, 3.6, 0, 0.9, 3.2, 0.9, B); cb(lg, x, 3.2, 0, 1.4, 0.9, 1.3, 'bone_d')                  # thigh + knee
        cb(lg, x, 0.8, 0, 0.9, 2.6, 0.9, B)                                                              # shin
        cb(lg, x, 0, -0.5, 1.4, 0.9, 2.4, B)                                                             # foot
    body = m.bone('body', [0, 6.6, 0], root)
    cb(body, 0, 6.2, 0, 3.4, 1.2, 1.8, 'bone_d')                                                         # pelvis
    cb(body, 0, 7.4, 0.3, 0.9, 3.6, 0.9, B)                                                              # spine
    for (y, w) in ((8.4, 3.4), (9.5, 4.0), (10.6, 4.2)):
        cb(body, 0, y, 0.1, w, 0.7, 2.6, B, decals={'north': [('rect', 0.45, 0, 0.55, 1, '#c8c0ac')]})    # ribs
    cb(body, 0, 11.6, 0.1, 5.0, 0.7, 1.4, 'bone_d')                                                      # collarbone
    hd = m.bone('head', [0, 13.2, 0], body)
    cb(hd, 0, 13.6, 0, 7.0, 5.6, 6.4, B, dens=2)                                                          # big skull
    for sx in (1, -1):
        cb(hd, sx * 1.7, 15.2, -3.25, 2.4, 2.4, 0.2, 'void'); cb(hd, sx * 1.7, 15.5, -3.3, 1.8, 1.8, 0.2, 'void')   # big round eye sockets
    cb(hd, 0, 14.0, -3.25, 0.8, 1.0, 0.2, 'void')                                                        # nose hole
    cb(hd, 0, 12.4, -0.4, 5.4, 1.4, 5.2, B)                                                              # cheekbones
    cb(hd, 0, 11.0, -1.4, 4.6, 1.6, 3.6, B, decals={'north': [('rect', 0.1, 0, 0.9, 0.35, '#f8f4ea'), ('rect', 0.1, 0.35, 0.9, 0.55, '#1c1a1a')]})   # dropped jaw (gaping grin)
    cb(hd, 0, 12.7, -3.25, 4.4, 0.8, 0.2, 'tooth', decals={'north': [('rect', 0.24, 0, 0.27, 1, '#9a9282'), ('rect', 0.49, 0, 0.51, 1, '#9a9282'), ('rect', 0.73, 0, 0.76, 1, '#9a9282')]})   # upper teeth
    cb(hd, 0, 12.1, -3.1, 3.6, 0.6, 0.4, 'void')                                                         # open mouth
    bd = m.bone('tc_bandana', [0, 16.5, 0], hd)
    cb(bd, 0, 18.4, 0.2, 7.4, 1.4, 6.8, 'tc')                                                            # team bandana
    cb(bd, -0.6, 19.4, 0.6, 5.4, 0.6, 5.2, 'tc')
    cb(bd, -3.0, 17.4, 3.6, 1.2, 1.4, 1.0, 'tc')                                                         # knot
    cb(bd, -3.6, 15.6, 4.2, 1.2, 2.8, 0.4, 'tc', rot=('x', 22.5), rot_origin=[-3.6, 17.4, 4.2])           # flapping tails
    cb(bd, -2.4, 15.2, 4.4, 1.2, 3.0, 0.4, 'tc', rot=('x', 45), rot_origin=[-2.4, 17.4, 4.4])
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 2.75, 12.1, 0], body)
        cb(a, sx * 3.0, 11.6, 0, 1.6, 1.6, 1.6, 'bone_d')                                                # shoulder knob
        cb(a, sx * 3.6, 12.4, 0, 0.9, 4.0, 0.9, B, rot=('z', -sx * 22.5), rot_origin=[sx * 3.0, 12.4, 0])  # upper arm up and out
        cb(a, sx * 4.5, 16.0, 0, 1.4, 1.2, 1.2, 'bone_d')                                                # elbow
        cb(a, sx * 4.5, 16.8, 0, 0.9, 4.6, 0.9, B)                                                       # forearm up
        cb(a, sx * 4.5, 21.2, 0, 1.8, 1.4, 1.8, B)                                                       # palm under the keg
        for k in (-0.5, 0.5):
            cb(a, sx * 4.5 + k * 0.6, 22.4, -0.7 + k * 1.4, 0.5, 1.2, 0.5, B)                          # finger bones
    kg = m.bone('bomb', [0, 22.0, 0], root)
    C = 26.0
    def stv(seed):                                                                          # clean staves: light/dark boards + grain + edge highlight
        def fn(img, rng):
            import numpy as _np, random as _r
            h, w, _ = img.shape
            R_ = _r.Random(seed * 97 + h * 7 + w)
            img[:] = _np.array([188, 118, 60.0])
            y = 0
            while y < h:
                sw = 4
                img[y:y + sw] *= R_.choice((0.92, 1.0, 1.06))
                img[y:min(h, y + 1)] *= 1.15
                if y + sw - 1 < h: img[y + sw - 1] = _np.array([112, 62, 28.0])
                for _ in range(3):
                    gy = R_.randrange(y, min(h, y + sw)); gx = R_.randrange(0, w); L = R_.randint(3, 8)
                    img[gy, gx:gx + L] *= 0.88
                y += sw
            img[:] = _np.clip(img, 0, 255)
        return fn
    def ring(b, x, w, R, r, mat, **kw):                                                    # octagonal section lying along x
        for (h, d) in ((2 * R, 2 * R - 2 * r), (2 * R - 2 * r, 2 * R), (2 * R - r * 0.9, 2 * R - r * 0.9)):
            cb(b, x, C - h / 2, 0, w, h, d, mat, **kw)
    for (x, w, R) in ((0, 4.0, 4.6), (-3.2, 2.4, 4.4), (3.2, 2.4, 4.4), (-5.4, 2.0, 4.0), (5.4, 2.0, 4.0)):   # bulging belly
        ring(kg, x, w, R, R * 0.36, 'wood', decals={g: [('fn', stv(int(x * 10) + 50))] for g in ('north', 'south', 'up', 'down')}, dens=2)
    for x in (-4.4, 4.4):                                                                  # thick steel hoops with rivets
        ring(kg, x, 1.2, 4.75, 1.7, 'band', decals={g: [('shade', 0, 0, 1, 0.3, 1.3), ('shade', 0, 0.75, 1, 1, 0.75)] for g in ('north', 'south', 'up', 'down')})
        for (y, z) in ((C + 4.75, 0), (C - 4.75 - 0.4, 0), (C - 0.2, 4.75), (C - 0.2, -4.75 - 0.4)):
            cb(kg, x, y, z + (0.2 if z > 0 else 0), 0.6, 0.4, 0.4, 'band_l')
    for sx in (1, -1):
        ring(kg, sx * 6.3, 0.6, 3.6, 1.3, 'band', decals={g: [('shade', 0, 0, 1, 0.3, 1.3)] for g in ('north', 'south', 'up', 'down')})   # end rim hoops
        cb(kg, sx * 6.62, C - 3.0, 0, 0.1, 6.0, 4.4, 'wood', decals={g: [('fn', stv(9)), ('ering', 0.5, 0.5, 0.42, 0.42, 0.12, '#7a4420')] for g in ('east', 'west')}, dens=2)   # end lid
        cb(kg, sx * 6.62, C - 2.2, 0, 0.1, 4.4, 6.0, 'wood', decals={g: [('fn', stv(9))] for g in ('east', 'west')}, dens=2)
    cb(kg, 6.9, C - 0.8, 0, 0.8, 1.6, 1.6, 'band_l')                                       # brass fuse plug
    pts = [(7.6, 0.0, 0.0), (8.4, 0.3, 0.2), (9.1, 0.9, 0.4), (9.6, 1.7, 0.5), (9.8, 2.6, 0.4), (9.6, 3.5, 0.1), (9.1, 4.2, -0.2)]
    for i, (x, y, z) in enumerate(pts):                                                     # twisted fuse curling up and back
        cb(kg, x, C + y - 0.4, z, 0.9, 0.9, 0.9, 'fuse', decals={g: [('rect', 0, 0.45, 1, 0.6, '#8a6a3a')] for g in ('north', 'south', 'east', 'west')})
    cb(kg, 8.7, C + 4.5, -0.4, 0.8, 0.8, 0.8, 'void')                                       # burnt tip
    sp = m.bone('spark', [8.6, C + 5.4, -0.4], kg)
    cb(sp, 8.6, C + 4.6, -0.4, 2.0, 2.0, 2.0, 'spark'); cb(sp, 8.6, C + 5.0, -0.4, 1.2, 1.2, 1.2, 'spark_w')   # flame core
    for (dx, dy, dz) in ((1.6, 1.0, 0), (-1.6, 0.8, 0), (0, 2.2, 0), (0, 1.0, 1.6), (0, 1.0, -1.6), (1.2, 2.0, 1.0), (-1.2, 2.0, -1.0)):
        cb(sp, 8.6 + dx, C + 4.6 + dy, -0.4 + dz, 0.5, 0.5, 0.5, 'spark')                # spark burst
    m.hitbox(0.7, 2.0)
    return m


def pekka():
    """P.E.K.K.A: hulking dark steel-blue knight. Small bucket helm with a central slit and two angled glowing eyes,
    huge horns sweeping out and up, broad shield-shaped chest plate with a centre ridge, layered tassets, enormous
    pauldrons with spikes, segmented arms with spiked gauntlets, stubby armoured legs; long sword in the right hand.
    Horns, spikes and eyes = soft team colour."""
    m = new_model('clash_pekka')
    m.mats_({'steel': ('#5e6c84', 'soft'), 'steel_l': ('#7c8ca6', 'soft'), 'steel_d': ('#46526a', 'soft'), 'under': ('#2c323e', 'soft'),
             'void': ('#101218', 'plain'), 'soft': ('#f4f4f4', 'gem'), 'blade': ('#b8c0ca', 'metal'), 'blade_l': ('#e2e6ec', 'metal'),
             'grip': ('#2a3a6a', 'leather'), 'tc': ('#efefef', 'cloth')})
    MT = lambda t=1.2, b=0.8: {f: [('lerp', '#8494ae', 0.0, 0.0, 'y'), ('shade', 0, 0, 1, 0.18, t), ('shade', 0, 0.8, 1, 1, b)] for f in ('north', 'south', 'east', 'west')}
    def rnd(bn, x, y, z, w, h, d, c, mat, **kw):                                                     # chamfered box
        cb(bn, x, y, z, w, h, d - 2 * c, mat, **kw); cb(bn, x, y, z, w - 2 * c, h, d, mat, **kw); cb(bn, x, y + c * 0.5, z, w - c, h - c, d - c, mat, **kw)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.0
        lg = m.bone('leg_' + side, [x, 19.2, 0.6], root)
        cb(lg, x, 6.0, 0.6, 6.0, 13.0, 6.0, 'under')                                                     # dark under-armour leg
        rnd(lg, x, 0, -0.4, 7.6, 6.0, 10.0, 1.6, 'steel', decals=MT())                                 # armoured boot
        cb(lg, x, 0, -5.4, 5.0, 2.6, 1.6, 'steel_d')                                                    # pointed toe
        rnd(lg, x, 8.6, -0.2, 7.0, 4.0, 7.0, 1.2, 'steel_l', decals=MT())                               # knee guard
        cb(lg, x, 9.4, -3.8, 2.4, 2.4, 0.6, 'steel')                                                    # knee boss
        cb(lg, x, 6.0, -0.4, 7.8, 1.0, 10.2, 'steel_d')                                                 # boot rim
        for y in (13.4, 15.6):
            cb(lg, x, y, 0.6, 6.6, 0.8, 6.6, 'steel_d')                                                 # thigh bands
    body = m.bone('body', [0, 19.2, 0.6], root)
    rnd(body, 0, 19.0, 1.0, 22.0, 18.0, 14.0, 3.2, 'steel', decals=MT(1.15, 0.85))                     # barrel torso
    PL = {'north': [('rect', 0.485, 0, 0.515, 1, '#8a9ab4'), ('shade', 0, 0, 0.485, 1, 1.08), ('shade', 0.515, 0, 1, 1, 0.92), ('shade', 0, 0, 1, 0.08, 1.2)]}
    cb(body, 0, 25.0, -6.6, 19.0, 11.0, 1.8, 'steel', decals=PL)                                         # shield-shaped chest plate
    cb(body, 0, 21.4, -6.4, 15.4, 3.8, 1.8, 'steel', decals=PL)
    cb(body, 0, 19.2, -6.0, 10.0, 2.4, 1.6, 'steel', decals=PL)
    cb(body, 0, 36.0, -6.4, 15.0, 1.0, 1.6, 'steel_l')                                                   # top edge
    cb(body, 0, 28.8, -7.7, 19.4, 0.8, 0.4, 'steel_d')                                                   # plate seam
    for (x, y) in ((-8.0, 34.4), (8.0, 34.4), (-8.6, 26.0), (8.6, 26.0), (-6.4, 21.2), (6.4, 21.2)):
        cb(body, x, y, -7.7, 1.0, 1.0, 0.5, 'steel_l')                                                   # plate rivets
    for sx in (1, -1):
        cb(body, sx * 11.2, 21.0, 1.0, 0.8, 13.0, 10.0, 'steel_d', decals={'east': [('shade', 0, 0, 1, 0.1, 1.2)], 'west': [('shade', 0, 0, 1, 0.1, 1.2)]})   # side plates
    cb(body, 0, 21.0, 8.2, 18.0, 14.0, 0.8, 'steel_d', decals={'south': [('rect', 0.48, 0, 0.52, 1, '#5e6c84'), ('rect', 0, 0.5, 1, 0.54, '#2c323e')]})   # back plate
    for sx in (1, -1):
        cb(body, sx * 5.2, 30.0, -7.7, 1.2, 1.2, 0.4, 'steel_l')                                         # rivets
        cb(body, sx * 5.0, 24.0, -7.5, 1.2, 1.2, 0.4, 'steel_l')
    cb(body, 0, 36.6, 0.0, 12.0, 2.2, 10.0, 'steel_d')                                                    # gorget
    tt = m.bone('tc_trim', [0, 19.2, 0.6], body)
    cb(tt, 0, 18.0, 0.8, 22.4, 1.6, 14.4, 'tc')                                                           # team belt
    for i, x in enumerate((-7.2, -2.4, 2.4, 7.2)):
        cb(body, x, 12.6, -5.6, 4.4, 5.6, 1.4, 'steel_d' if i % 2 else 'steel', decals={'north': [('fn', _soft_metal(1.2, 0.8))]})   # front tassets
        cb(body, x, 12.6, 7.2, 4.4, 5.6, 1.2, 'steel_d')                                                  # back tassets
    for sx in (1, -1):
        cb(body, sx * 10.6, 12.6, 0.8, 1.2, 5.6, 10.0, 'steel_d')
    hd = m.bone('head', [0, 37.8, -1.2], body)
    rnd(hd, 0, 36.6, -0.8, 10.6, 12.0, 10.4, 2.0, 'steel', decals=MT(1.2, 0.85))                         # big bucket helm
    rnd(hd, 0, 48.4, -0.8, 9.0, 1.4, 8.8, 2.0, 'steel', decals=MT())                                       # rounded dome
    rnd(hd, 0, 49.8, -0.8, 6.6, 0.8, 6.4, 1.6, 'steel_l')
    cb(hd, 0, 35.6, -0.8, 11.8, 1.6, 11.6, 'steel_d', decals={f: [('shade', 0, 0, 1, 0.3, 1.2)] for f in ('north', 'south', 'east', 'west')})   # flared lower rim
    FP = {'north': [('shade', 0, 0, 1, 0.12, 1.25), ('shade', 0, 0.85, 1, 1, 0.8)]}
    for sx in (1, -1):                                                                                       # pointed (V) faceplate
        cb(hd, sx * 2.5, 36.4, -6.0, 5.4, 11.6, 1.4, 'steel', decals=FP, rot=('y', -sx * 22.5), rot_origin=[0, 42, -7.0])
    cb(hd, 0, 36.2, -7.4, 1.6, 13.4, 1.4, 'steel_l', decals={'north': [('shade', 0, 0, 1, 1, 1.12)]})            # centre rib from crest to chin
    cb(hd, 0, 49.0, -0.8, 1.6, 1.8, 10.6, 'steel_l')                                                       # crest over the dome
    ey = m.bone('ts_eyes', [0, 44, -6], hd)
    for sx in (1, -1):
        cb(hd, sx * 2.8, 42.0, -7.1, 3.8, 2.8, 0.4, 'void', rot=('z', sx * 22.5), rot_origin=[sx * 2.8, 43.4, -7.1])   # deep angled eye sockets
        cb(ey, sx * 2.8, 42.6, -7.35, 2.8, 1.4, 0.2, 'soft', rot=('z', sx * 22.5), rot_origin=[sx * 2.8, 43.3, -7.35])   # glowing eyes
        cb(hd, sx * 2.9, 45.4, -7.2, 4.4, 1.2, 1.0, 'steel_l', rot=('z', sx * 22.5), rot_origin=[sx * 2.9, 46.0, -7.2])   # angry brow plates
        cb(hd, sx * 2.4, 37.0, -7.0, 2.6, 0.5, 0.3, 'void')                                                 # breathing slits
        cb(hd, sx * 2.4, 38.4, -7.0, 2.6, 0.5, 0.3, 'void')
        cb(hd, sx * 5.4, 39.0, -0.8, 0.8, 7.0, 7.6, 'steel_d', decals={'east': [('shade', 0, 0, 1, 0.15, 1.2)], 'west': [('shade', 0, 0, 1, 0.15, 1.2)]})   # side plates
        for y in (40.0, 44.6):
            cb(hd, sx * 5.9, y, -3.2, 0.4, 0.9, 0.9, 'steel_l')                                             # rivets
        cb(hd, sx * 5.6, 43.4, -0.8, 1.4, 3.4, 3.4, 'steel_l')                                              # horn sockets
    hn = m.bone('ts_horns', [0, 45, -1.4], hd)
    for sx in (1, -1):                                                                                    # big horns, out then up
        for (dx, dy, w, h) in ((6.4, 42.8, 3.6, 3.6), (7.6, 43.2, 3.6, 3.6), (9.8, 43.8, 3.4, 3.4), (11.8, 44.8, 3.2, 3.2), (13.4, 46.4, 3.0, 3.2),
                               (14.6, 48.4, 2.6, 3.0), (15.4, 50.6, 2.2, 2.8), (15.8, 52.8, 1.6, 2.4), (15.8, 54.8, 1.0, 1.6)):
            cb(hn, sx * dx, dy, -1.4, w, h, w, 'soft', decals={'north': [('rect', 0.15, 0, 0.35, 1, '#ffffff')], 'up': [('shade', 0, 0, 1, 1, 1.1)], 'down': [('shade', 0, 0, 1, 1, 0.75)], 'east': [('shade', 0, 0, 1, 1, 0.85)], 'west': [('shade', 0, 0, 1, 1, 0.85)]})
    for sx, side in ((1, 'r'), (-1, 'l')):
        X = sx * 14.4
        a = m.bone('arm_' + side, [X, 34.8, 0.6], body)
        rnd(a, X + sx * 0.6, 31.0, 0.6, 10.4, 8.0, 13.0, 2.4, 'steel', decals=MT())                     # huge pauldron
        cb(a, X + sx * 0.6, 30.4, 0.6, 11.0, 1.2, 13.6, 'steel_d')                                       # pauldron rim
        cb(a, X + sx * 0.6, 37.0, 0.6, 8.0, 1.0, 9.0, 'steel_l')
        rnd(a, X + sx * 1.2, 28.2, 0.6, 9.6, 3.0, 11.8, 2.0, 'steel_d', decals=MT())                  # second pauldron tier
        cb(a, X + sx * 1.2, 27.8, 0.6, 10.0, 0.6, 12.2, 'under')
        cb(a, X + sx * 0.6, 34.6, -5.95, 6.0, 2.4, 0.2, 'steel_l', decals={'north': [('rect', 0.1, 0.3, 0.9, 0.7, '#46526a')]})   # engraved panel
        cb(a, X + sx * 0.4, 24.0, 0.6, 5.0, 7.0, 5.0, 'under')                                           # dark upper arm
        for y in (25.0, 27.4):
            cb(a, X + sx * 0.4, y, 0.6, 5.8, 1.2, 5.8, 'steel_d')                                        # segment bands
        rnd(a, X + sx * 0.6, 16.6, 0.6, 7.0, 7.6, 7.4, 1.4, 'steel', decals=MT())                      # gauntlet
        rnd(a, X + sx * 0.6, 12.4, 0.0, 7.4, 4.6, 7.8, 1.4, 'steel_d', decals=MT())                    # fist
        cb(a, X + sx * 0.6, 23.6, 0.6, 7.6, 1.2, 7.8, 'steel_l')                                         # gauntlet cuff
        for k in (-2.4, -0.8, 0.8, 2.4):
            cb(a, X + sx * 0.6 + k, 12.0, -3.9, 1.4, 3.4, 0.6, 'steel', decals={'north': [('rect', 0, 0.45, 1, 0.55, '#2c323e')]})   # finger plates
        sp = m.bone('ts_spikes_' + side, [X, 28, 0.6], a)
        for (y, z) in ((38.0, -2.0), (38.0, 3.2)):                                                       # pauldron spikes (up)
            for (w, h, o) in ((2.4, 1.6, 0), (1.6, 1.6, 1.6), (0.8, 1.4, 3.2)):
                cb(sp, X + sx * 1.6, y + o, z, w, h, w, 'soft')
        for (w, d, o) in ((2.2, 1.4, 0), (1.4, 1.4, 1.4), (0.6, 1.2, 2.8)):                             # pauldron spike (outward)
            cb(sp, X + sx * (6.0 + o + d / 2), 34.0 - w / 2, 0.6, d, w, w, 'soft')
        for y in (16.0, 19.0, 22.0):                                                                     # gauntlet spikes (outward)
            for (w, d, o) in ((1.8, 1.2, 0), (1.0, 1.2, 1.2)):
                cb(sp, X + sx * (4.2 + o + d / 2), y - w / 2, 0.6, d, w, w, 'soft')
    hr = m.bone('hand_r', [15.0, 14.4, 0.0], m.by_name('arm_r'))
    sw = m.bone('sword', [15.0, 14.4, 0.0], hr)
    SR = dict(rot=('x', SWORD_TILT), rot_origin=[15.0, 14.4, 0.0])
    cb(sw, 15.0, 13.2, 3.6, 2.0, 2.0, 1.4, 'steel_d', **SR)                                              # pommel
    cb(sw, 15.0, 13.6, 0.0, 1.6, 1.6, 6.0, 'grip', **SR)                                                 # grip through the fist
    cb(sw, 15.0, 11.6, -3.6, 2.6, 5.6, 1.4, 'steel_d', **SR)                                             # guard
    cb(sw, 15.0, 12.4, -15.6, 1.2, 4.2, 23.0, 'blade', decals={'east': [('rect', 0, 0.45, 1, 0.55, '#8a929c'), ('lerp', '#e2e6ec', 0.0, 0.3, 'y')],
                                                              'west': [('rect', 0, 0.45, 1, 0.55, '#8a929c'), ('lerp', '#e2e6ec', 0.0, 0.3, 'y')]}, **SR)   # long blade
    cb(sw, 15.0, 13.2, -28.0, 1.2, 2.6, 1.8, 'blade_l', **SR)                                            # tip
    m.hitbox(2.4, 3.6)
    return m


SWORD_TILT = -45


def hunter():
    """Hunter: burly man with a big black moustache, dark shades, team pillbox fur hat, black hair tail with feathers,
    team tunic + sleeves under a brown leather vest and cape, belt, big brown gloves + stitched boots, chewing the fuse cord
    of a double-barrel scattergun held at the hip."""
    m = new_model('clash_hunter')
    m.mats_({'skin': ('#eab48e', 'skin'), 'skin_d': ('#cf9672', 'skin'), 'tc': ('#efefef', 'cloth'), 'tc_d': ('#c8c8c8', 'cloth'),
             'leather': ('#6a4230', 'leather'), 'leather_d': ('#4e2e20', 'leather'), 'pants': ('#3e4a66', 'cloth'), 'boot': ('#5a3424', 'leather'),
             'hair': ('#1e1e22', 'hair'), 'feather': ('#e8e8e8', 'soft'), 'shade': ('#141418', 'plain'), 'steel': ('#9aa2aa', 'metal'),
             'steel_d': ('#5e666e', 'metal'), 'rope': ('#c8a060', 'rope'), 'gold': ('#d8aa48', 'metal'), 'wood': ('#8a5530', 'soft')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 4.4, 0, 4.2, 7.6, 4.4, 'pants')                                                       # trousers
        cb(lg, x, 0, -0.6, 4.8, 5.0, 5.8, 'boot', decals={'north': [('rect', 0, 0.8, 1, 0.86, '#3a2018')], 'up': [('shade', 0, 0, 1, 1, 1.1)]})   # big stitched boots
    body = m.bone('body', [0, 12, 0], root)
    tb = m.bone('tc_body', [0, 12, 0], body)
    cb(tb, 0, 9.0, 0, 11.4, 15.4, 7.0, 'tc', decals={'north': [('lerp', '#c8c8c8', 0.7, 1.0, 'y')]})       # team tunic
    cb(body, 0, 11.6, 0, 12.0, 2.0, 7.6, 'leather_d')                                                  # belt
    cb(body, 0, 11.4, -3.9, 2.2, 2.4, 0.4, 'gold')
    for sx in (1, -1):
        cb(body, sx * 4.4, 13.6, -0.2, 3.4, 10.8, 7.6, 'leather', decals={'north': [('lerp', '#4e2e20', 0.6, 1.0, 'y')]})   # leather vest panels
    cb(body, 0, 22.4, 0.2, 12.4, 2.6, 7.8, 'leather')                                                  # vest yoke over the shoulders
    cb(body, 0, 6.0, 4.2, 12.0, 18.4, 0.8, 'leather', decals={'south': [('lerp', '#4e2e20', 0.5, 1.0, 'y')]})   # cape down the back
    cb(body, 0, 4.6, 4.4, 9.0, 1.6, 0.6, 'leather_d')
    hd = m.bone('head', [0, 26, 0], body)
    cb(hd, 0, 25.0, -0.4, 9.0, 9.6, 8.6, S, dens=2)                                                     # big head
    cb(hd, 0, 30.2, -4.8, 8.2, 1.6, 0.4, 'shade', decals={'north': [('rect', 0.1, 0.1, 0.25, 0.4, '#5a5a66'), ('rect', 0.6, 0.1, 0.75, 0.4, '#5a5a66')]})   # dark shades
    cb(hd, 0, 27.0, -5.2, 2.2, 2.6, 1.6, 'skin_d')                                                      # nose
    for sx in (1, -1):                                                                                  # big black moustache
        cb(hd, sx * 1.8, 25.8, -5.0, 3.4, 1.4, 1.0, 'hair')
        cb(hd, sx * 3.6, 24.6, -4.9, 1.6, 1.8, 0.9, 'hair')
    cb(hd, 0, 23.6, -4.8, 2.6, 1.0, 0.4, 'skin_d')                                                      # chin
    for sx in (1, -1):
        cb(hd, sx * 4.6, 28.0, 2.4, 0.4, 3.6, 3.4, 'hair')                                              # black hair behind the ears
    ct = m.bone('cap_tail', [0, 34, 5], hd)
    cb(ct, 0, 28.0, 4.6, 7.0, 6.4, 1.6, 'hair')                                                         # hair at the back
    cb(ct, 0, 26.0, 5.6, 3.6, 3.6, 2.0, 'hair')                                                         # tied tail
    for (x, y, r) in ((-1.6, 29.6, -22.5), (1.4, 30.2, 22.5), (0.0, 31.0, 0)):
        cb(ct, x, y, 6.0, 1.2, 4.2, 0.4, 'feather', decals={'south': [('rect', 0, 0.6, 1, 1, '#1e1e22')]},
           **(dict(rot=('z', r), rot_origin=[x, y, 6.0]) if r else {}))                                # feathers
    tcap = m.bone('tc_cap', [0, 35, 0], hd)
    cb(tcap, 0, 33.4, -0.2, 9.6, 4.6, 9.2, 'tc', decals={f: [('fn', _folds(0.9, 1.06, 1))] for f in ('north', 'south', 'east', 'west')})   # team fur pillbox hat
    cb(tcap, 0, 38.0, -0.2, 8.8, 0.6, 8.4, 'tc_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 7.0
        a = m.bone('arm_' + side, [x, 24, 0], body)
        ta = m.bone('tc_arm_' + side, [x, 24, 0], a)
        cb(ta, x, 17.4, 0, 4.4, 7.4, 4.4, 'tc')                                                         # team sleeve
        cb(a, x, 21.0, 0, 5.0, 3.8, 5.0, 'leather')                                                     # leather shoulder
        cb(a, x, 11.6, 0, 5.0, 6.0, 5.0, 'leather', decals={'north': [('lerp', '#4e2e20', 0.6, 1.0, 'y')]})   # big glove
        cb(a, x, 17.0, 0, 5.4, 1.2, 5.4, 'leather_d')                                                   # glove cuff
    PX, PY, PZ = 2.5, 19.0, -8.0                                                                # shotgun pivot = right hand on the wrist of the stock
    g = m.bone('gun', [PX, PY, PZ], body)                                                       # aimed by animation: yaw -45 (across), pitch down at rest
    WD = {f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    MT = {f: [('fn', _soft_metal(1.2, 0.8))] for f in ('north', 'south', 'east', 'west', 'up')}
    cb(g, PX, PY - 1.6, PZ + 2.6, 2.4, 3.0, 4.6, 'wood', decals=WD)                                   # butt stock
    cb(g, PX, PY - 1.0, PZ - 0.6, 2.0, 2.0, 2.4, 'wood', decals=WD)                                   # wrist (right hand)
    cb(g, PX, PY - 1.2, PZ - 3.0, 2.8, 2.6, 2.6, 'steel_d', decals=MT)                                # receiver
    cb(g, PX, PY + 0.2, PZ - 2.6, 0.8, 0.8, 1.2, 'steel')                                             # hammers
    for sx in (1, -1):
        cb(g, PX + sx * 0.75, PY - 0.6, PZ - 10.4, 1.5, 1.5, 12.0, 'steel', decals={'up': [('rect', 0.3, 0, 0.6, 1, '#d4dae0')], 'east': [('fn', _soft_metal(1.2, 0.8))], 'west': [('fn', _soft_metal(1.2, 0.8))]})   # side-by-side barrels
    cb(g, PX, PY - 1.6, PZ - 6.4, 2.6, 1.4, 5.2, 'wood', decals=WD)                                   # fore-end (left hand)
    cb(g, PX, PY - 0.8, PZ - 13.8, 3.4, 1.8, 0.6, 'steel_d')                                          # barrel band
    mz = m.bone('muzzle', [PX, PY, PZ - 16.4], g)
    for sx in (1, -1):
        cb(mz, PX + sx * 0.75, PY - 0.7, PZ - 16.6, 1.7, 1.7, 0.5, 'steel_d', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#1a1a1e')]})   # muzzles
    K, Pv = 1.6, [PX, PY, PZ]                                                                  # chunkier shotgun, scaled about the grip
    for bn in (g, mz):
        if bn is mz:
            bn.origin = [Pv[i] + (bn.origin[i] - Pv[i]) * K for i in range(3)]
        for c in bn.cubes:
            for key in ('frm', 'to', 'rot_origin'):
                c[key] = [Pv[i] + (c[key][i] - Pv[i]) * K for i in range(3)]
    m.hitbox(1.0, 2.6)
    return m


def valkyrie():
    """Valkyrie: big wild orange hair with fringe, blue eyes + fierce brows, dark leather crop top with gold collar,
    bare midriff, ragged leather skirt with team belt, knee boots with gold cuffs, team wrist wraps, heavy axe held forward."""
    m = new_model('clash_valkyrie')
    m.mats_({'skin': ('#f2b892', 'skin'), 'skin_d': ('#d89878', 'skin'), 'hair': ('#f06a1e', 'hair'), 'hair_d': ('#c84e10', 'hair'),
             'hair_l': ('#ff9040', 'hair'), 'leather': ('#4e3a34', 'leather'), 'leather_d': ('#3a2a26', 'leather'), 'gold': ('#e2b23a', 'metal'),
             'boot': ('#4a3a40', 'leather'), 'tc': ('#efefef', 'cloth'), 'wood': ('#8a5530', 'wood'), 'blade': ('#aab2bc', 'metal'),
             'blade_l': ('#dfe4ea', 'metal'), 'blade_d': ('#6e7680', 'metal')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.0
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 5.6, 0, 3.4, 6.6, 3.4, S, decals={'north': [('lerp', '#d89878', 0.8, 1.0, 'y')]})       # bare thighs
        cb(lg, x, 0, -0.2, 3.8, 6.0, 3.8, 'boot', decals={'north': [('rect', 0.45, 0.1, 0.55, 0.9, '#3a2a30')]})   # knee boots
        cb(lg, x, 5.4, 0, 4.2, 1.2, 4.2, 'gold')                                                        # gold boot cuff
        cb(lg, x, 0, -1.4, 3.6, 1.2, 1.4, 'boot')                                                       # toe
    body = m.bone('body', [0, 12, 0], root)
    import random as _r
    R = _r.Random(4)
    cb(body, 0, 9.4, 0, 8.4, 3.4, 4.6, 'leather', decals={f: [('lerp', '#3a2a26', 0.5, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # skirt
    for i, x in enumerate((-3.4, -1.7, 0, 1.7, 3.4)):
        h = R.choice((1.2, 2.0, 2.6))
        cb(body, x, 9.4 - h, -2.1, 1.6, h, 0.4, 'leather_d' if i % 2 else 'leather')                    # ragged hem
        cb(body, x, 9.4 - h, 2.1, 1.6, h, 0.4, 'leather')
    ts = m.bone('tc_suit', [0, 12, 0], body)
    cb(ts, 0, 12.2, 0, 8.6, 1.2, 4.8, 'tc')                                                            # team belt
    cb(body, 0, 13.4, 0, 7.4, 4.4, 3.8, S, decals={'north': [('rect', 0.48, 0.3, 0.52, 0.5, '#d89878')]})   # bare midriff
    cb(body, 0, 17.8, 0, 8.0, 5.0, 4.4, 'leather', decals={'north': [('rect', 0.45, 0.6, 0.55, 1, '#f2b892'), ('lerp', '#3a2a26', 0.7, 1.0, 'y')]})   # leather crop top
    cb(body, 0, 22.6, 0, 6.4, 0.8, 4.0, 'gold')                                                         # gold collar
    for sx in (1, -1):
        cb(body, sx * 2.6, 20.0, -2.25, 0.6, 2.8, 0.3, 'gold', rot=('z', sx * 22.5), rot_origin=[sx * 2.6, 22.8, -2.25])   # gold straps
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", "........", "...rr...", "........"],
               {'k': '#a8400e', 'w': '#ffffff', 'b': '#2a7ad8', 'r': '#c8505a'})
    cb(hd, 0, 24, 0, 8, 8, 8, S, decals={'north': face}, dens=2)
    cb(hd, 0, 30.8, 0.4, 9.4, 3.0, 9.0, 'hair', decals={'up': [('rect', 0.2, 0.2, 0.4, 0.8, '#ff9040')], 'north': [('lerp', '#c84e10', 0.6, 1.0, 'y')]})   # wild hair top
    cb(hd, 0, 33.4, 0.0, 6.4, 1.2, 6.4, 'hair_l')                                                       # messy crown
    for (x, w, h) in ((-3.0, 2.4, 2.0), (-0.6, 2.4, 2.8), (1.8, 2.2, 2.2), (3.6, 1.6, 1.6)):
        cb(hd, x, 31.6 - h + 0.4, -4.4, w, h, 1.0, 'hair')                                              # swept fringe
    for sx in (1, -1):
        cb(hd, sx * 4.6, 23.6, 0.6, 1.4, 7.6, 8.6, 'hair', decals={'north': [('lerp', '#c84e10', 0.5, 1.0, 'y')]})   # big puffed sides
        cb(hd, sx * 5.4, 23.0, 1.4, 1.4, 4.4, 5.0, 'hair_d')                                            # flicked ends
        cb(hd, sx * 5.6, 30.6, 0.4, 1.4, 2.0, 6.0, 'hair_l')
    cb(hd, 0, 22.4, 4.6, 9.2, 9.6, 1.4, 'hair', decals={'south': [('lerp', '#c84e10', 0.6, 1.0, 'y')]})   # back
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.0
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x + sx * 0.6, 12.0, 0, 3.2, 10.6, 3.2, S, decals={'north': [('lerp', '#d89878', 0.8, 1.0, 'y')]})   # bare arm
        tw = m.bone('tc_wrist_' + side, [x + sx, 14, 0], a)
        cb(a, x + sx * 0.6, 12.6, 0, 3.6, 2.4, 3.6, 'leather')                                          # leather wrist wrap
        cb(tw, x + sx * 0.6, 14.8, 0, 3.7, 0.8, 3.7, 'tc')                                              # team band
    ax = m.bone('axe', [6.0, 13.0, -0.2], m.by_name('arm_r'))
    Y = 12.4
    cb(ax, 5.6, Y - 0.6, -5.6, 1.4, 1.4, 17.0, 'wood', decals={f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})   # haft held forward
    cb(ax, 5.6, Y - 1.2, 3.0, 2.0, 2.0, 1.4, 'blade_d')                                                 # pommel
    cb(ax, 5.6, Y - 1.6, -12.8, 2.2, 3.2, 3.2, 'blade_d')                                               # head socket
    for sy in (1, -1):                                                                                   # matching double blades (up + down)
        for (dy, h, d) in ((1.6, 2.4, 4.4), (3.4, 2.2, 6.6), (5.2, 2.0, 7.6), (6.8, 1.4, 6.6)):
            cb(ax, 5.6, Y - 0.8 + sy * (dy + 0.8) - h / 2, -12.8, 0.8, h, d, 'blade', decals={'east': [('lerp', '#dfe4ea', 0.0, 0.3, 'y')], 'west': [('lerp', '#dfe4ea', 0.0, 0.3, 'y')]})
    m.hitbox(0.8, 2.2)
    return m


def elixir_collector():
    """Elixir Collector: bevelled stone base, team plinths, octagonal wooden stave collars around a glass tank of glowing
    pink elixir, steel rings, team cap, grey pipe looping over to a wooden side pump with a valve wheel, elixir puddles."""
    m = new_model('clash_elixir_collector')
    m.mats_({'stone': ('#c4c4c2', 'soft'), 'stone_d': ('#a0a09e', 'soft'), 'wood': ('#a8703a', 'soft'), 'wood_d': ('#7e5028', 'soft'),
             'steel': ('#9aa2aa', 'soft'), 'steel_d': ('#6e747c', 'soft'), 'pipe': ('#a4aab0', 'soft'), 'tc': ('#efefef', 'cloth'),
             'elixir': ('#e040e8', 'glow'), 'elixir_l': ('#f6a0ff', 'glow'), 'glass': ('#cfeaf2', 'soft'), 'bubble': ('#ffd8ff', 'glow')})
    def octo(b, x, y, z, R, h, mat, r=None, **kw):
        r = R * 0.3 if r is None else r
        cb(b, x, y, z, 2 * R, h, 2 * R - 2 * r, mat, **kw); cb(b, x, y, z, 2 * R - 2 * r, h, 2 * R, mat, **kw)
    ST = lambda: {f: [('fn', _stone)] for f in ('north', 'south', 'east', 'west', 'up')}
    MT = lambda: {f: [('fn', _soft_metal(1.15, 0.85))] for f in ('north', 'south', 'east', 'west')}
    WD = lambda: {f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up')}
    def staves(b, y, h, R, w):                                                                 # ring of separate wooden blocks
        import math as _m
        for k in range(8):
            a = k * _m.pi / 4
            x, z = _m.cos(a) * R, _m.sin(a) * R
            rk = dict(rot=('y', 45), rot_origin=[x, y, z]) if k % 2 else {}
            cb(b, x, y, z, w if k % 4 in (1, 3) or k % 4 == 2 else 3.2, h, 3.2 if k % 4 in (1, 3) or k % 4 == 2 else w, 'wood', decals=WD(), **rk) if False else \
                cb(b, x, y, z, 3.4 if k % 4 == 0 else w, h, w if k % 4 == 0 else 3.4, 'wood', decals=WD(), **rk)
    root = m.bone('root', [0, 0, 0])
    fr = m.bone('frame', [0, 0, 0], root)
    octo(fr, 0, 0, 0, 20.4, 2.6, 'stone_d', r=6.0, decals=ST())                                        # bevelled stone base
    octo(fr, 0, 2.6, 0, 19.4, 0.8, 'stone', r=5.6, decals=ST())
    tb = m.bone('tc_seal_base', [0, 6, 0], fr)
    octo(tb, 0, 3.4, 0, 12.4, 2.0, 'tc', r=3.8)                                                  # team plinth under the tank
    octo(tb, 13.4, 3.4, 0, 5.4, 2.0, 'tc', r=1.6)                                                    # team plinth under the pump
    for (x, z, s) in ((-14.0, 13.0, 3.4), (-11.0, 15.4, 1.6)):
        cb(fr, x, 3.4, z, s, 0.4, s * 0.8, 'elixir_l')                                                 # elixir puddles
    staves(fr, 5.4, 6.4, 8.8, 6.6)                                                                     # lower wooden collar
    octo(fr, 0, 11.8, 0, 8.6, 2.2, 'steel', r=2.4, decals=MT())                                  # steel ring
    for b_ in fr.cubes[-16:]:
        pass
    tk = m.bone('tank', [0, 14, 0], root)
    octo(tk, 0, 14.0, 0, 7.4, 9.0, 'elixir', r=2.0, decals={f: [('lerp', '#ff9cff', 0.0, 0.25, 'y')] for f in ('north', 'south', 'east', 'west')})   # glowing elixir
    octo(tk, 0, 23.0, 0, 7.4, 7.6, 'glass', r=2.0, decals={f: [('rect', 0.15, 0, 0.22, 1, '#ffffff'), ('rect', 0.7, 0, 0.74, 1, '#ffffff')] for f in ('north', 'south', 'east', 'west')})   # glass above
    gc = m.bone('glow_core', [0, 23, 0], tk)
    octo(gc, 0, 22.8, 0, 6.6, 0.6, 'elixir_l', r=1.8)                                            # liquid surface
    bb = m.bone('bubbles', [0, 16, 0], tk)
    for (x, y, z, s) in ((-3.6, 23.2, 0.4, 1.0), (0.2, 23.4, -3.0, 0.8), (-1.0, 23.1, 2.2, 0.7)):
        cb(bb, x, y, z, s, s, s, 'bubble')
    ld = m.bone('lid', [0, 32, 0], root)
    staves(ld, 30.6, 5.0, 8.6, 6.2)                                                                    # upper wooden collar
    tt = m.bone('tc_seal_top', [0, 37, 0], ld)
    octo(tt, 0, 30.2, 0, 8.0, 0.8, 'steel_d', r=2.2)
    octo(tt, 0, 35.6, 0, 7.4, 1.4, 'tc', r=2.0)                                                  # team cap
    octo(tt, 0, 37.0, 0, 5.4, 1.2, 'tc', r=1.6)
    # pipe: up out of the cap, over, and down into the pump
    PM = {f: [('fn', _soft_metal(1.2, 0.8))] for f in ('north', 'south', 'east', 'west', 'up')}
    cb(ld, 0.0, 38.2, 0, 3.0, 4.0, 3.0, 'pipe', decals=PM)
    cb(ld, 6.7, 40.4, 0, 16.4, 3.0, 3.0, 'pipe', decals=PM)                                         # across the top
    cb(ld, 12.4, 18.0, -1.0 + 5.0, 3.0, 25.4, 3.0, 'pipe', decals=PM) if False else None
    cb(ld, 13.4, 17.6, 0, 3.0, 23.0, 3.0, 'pipe', decals=PM)                                        # down into the pump
    for y in (39.6, 17.6):
        cb(ld, 13.4, y, 0, 3.6, 0.8, 3.6, 'steel_d')                                                 # pipe joints
    # side pump with valve wheel
    octo(fr, 13.4, 5.4, 0, 3.6, 12.2, 'wood', r=1.0, decals=WD())                              # wooden pump body
    octo(fr, 13.4, 11.2, 0, 3.9, 1.8, 'steel', r=1.0, decals=MT())                                   # steel band
    lv = m.bone('lever', [18.5, 19, 0], fr)
    for (dy, dz, h, d) in ((3.6, 0, 1.0, 6.0), (-3.6, 0, 1.0, 6.0), (0, 3.4, 6.0, 1.0), (0, -3.4, 6.0, 1.0)):
        cb(lv, 17.2, 12.6 + dy - h / 2, dz, 1.0, h, d, 'wood_d', decals=WD())                    # valve wheel rim
    cb(lv, 17.2, 12.1, 0, 0.8, 1.0, 6.0, 'wood_d'); cb(lv, 17.2, 9.6, 0, 0.8, 6.0, 1.0, 'wood_d')  # spokes
    cb(lv, 16.6, 11.8, 0, 2.4, 1.6, 1.6, 'steel')                                                    # hub
    m.hitbox(2.6, 2.6)
    return m


def dart_goblin():
    """Dart Goblin: little green goblin behind a tall carved plank mask with team-painted eye rings and red pupils,
    a fan of big jungle leaves on top, pointy ears, brown shorts + leaf skirt, both hands on a long blowpipe."""
    m = new_model('clash_dart_goblin')
    m.mats_({'skin': ('#8cc63c', 'skin'), 'skin_d': ('#6fa62c', 'skin'), 'wood': ('#c88a46', 'soft'), 'wood_d': ('#9a6430', 'soft'),
             'void': ('#14161a', 'plain'), 'red': ('#e02a2a', 'glow'), 'tc': ('#efefef', 'cloth'), 'leaf': ('#3a8a2e', 'soft'),
             'leaf_d': ('#2a6a22', 'soft'), 'shorts': ('#7a5232', 'cloth'), 'pipe': ('#d0b070', 'soft'), 'pipe_d': ('#a88848', 'soft')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.5, 4, 0], root)
        cb(lg, sx * 1.5, 1.4, 0, 2.2, 2.8, 2.4, 'shorts')                                              # brown shorts leg
        cb(lg, sx * 1.5, 0, -0.5, 2.0, 1.4, 3.0, S)                                                     # little green foot
    body = m.bone('body', [0, 4, 0], root)
    cb(body, 0, 4.0, 0, 5.0, 6.0, 3.6, S, decals={'north': [('lerp', '#6fa62c', 0.7, 1.0, 'y'), ('rect', 0.45, 0.6, 0.55, 0.66, '#6fa62c')]})   # small torso
    cb(body, 0, 4.4, -0.4, 4.4, 3.0, 3.6, S)                                                        # pot belly
    sk = m.bone('skirt', [0, 6, 0], body)
    for i, x in enumerate((-2.0, -0.7, 0.7, 2.0)):
        cb(sk, x, 3.0, -1.9, 1.3, 2.8 - (i % 2) * 0.6, 0.4, 'leaf' if i % 2 else 'leaf_d')                # leaf skirt
    cb(sk, 0, 4.4, 0, 5.4, 1.4, 4.0, 'shorts')                                                          # waistband
    hd = m.bone('head', [0, 10, 0], body)
    cb(hd, 0, 10.0, 0.4, 5.6, 5.2, 5.0, S)                                                              # head behind the mask
    for sx, side in ((1, 'r'), (-1, 'l')):
        e = m.bone('ear_' + side, [sx * 3, 13, 0], hd)
        cb(e, sx * 3.4, 12.0, 0.4, 1.4, 2.0, 0.8, S); cb(e, sx * 4.8, 12.6, 0.4, 1.6, 1.2, 0.6, S); cb(e, sx * 6.0, 13.2, 0.4, 1.0, 0.8, 0.5, 'skin_d')   # pointy ears
    mk = m.bone('mask', [0, 13, -3], hd)
    planks = [('fn', _staves(True, base=(204, 140, 72), seam=(130, 82, 40)))]
    MZ = -2.9
    cb(mk, 0, 9.4, MZ, 7.0, 8.8, 1.2, 'wood', decals={'north': planks, 'south': planks, 'up': [('fn', _soft_wood)]})   # thick plank mask
    cb(mk, 0, 18.2, MZ, 6.2, 0.8, 1.2, 'wood', decals={'north': planks})                                # slightly narrower top
    for x, h in ((-2.9, 1.4), (-1.5, 0.6), (-0.2, 1.8), (1.2, 0.8), (2.7, 1.2)):
        cb(mk, x, 9.4 - h, MZ, 1.4, h, 1.2, 'wood', decals={'north': planks})                             # ragged plank ends
    for x in (-1.8, 0.6, 2.4):
        cb(mk, x, 9.0, MZ - 0.65, 0.2, 9.4, 0.1, 'wood_d')                                                # carved grooves
    tp = m.bone('tc_paint', [0, 14, -4], mk)
    for sx in (1, -1):
        X = sx * 1.75
        cb(tp, X, 12.2, MZ - 0.68, 2.2, 3.8, 0.1, 'tc'); cb(tp, X, 12.6, MZ - 0.68, 3.0, 3.0, 0.1, 'tc')   # round team paint rings
        cb(tp, X, 12.9, MZ - 0.72, 2.6, 2.4, 0.06, 'tc')
        cb(mk, X, 13.0, MZ - 0.75, 1.8, 2.2, 0.1, 'void'); cb(mk, X, 13.3, MZ - 0.75, 2.2, 1.6, 0.1, 'void')   # deep round eye holes
        cb(mk, X, 13.6, MZ - 0.8, 1.0, 1.0, 0.1, 'red')                                                    # red glowing pupils
    cb(tp, 0, 10.0, MZ - 0.68, 2.6, 2.2, 0.1, 'tc')                                                       # paint ring round the mouth hole
    cb(mk, 0, 10.4, MZ - 0.72, 1.6, 1.4, 0.1, 'void')
    hdr = m.bone('headdress', [0, 16, 0], hd)                                                             # leaves bound to the back of the mask
    LZ = MZ + 1.0
    widths = (2.0, 4.4, 6.0, 6.6, 6.4, 5.4, 3.8, 2.0, 0.8)
    LD = lambda ax: {g: [('rect', 0.47, 0, 0.53, 1, '#24601e') if ax == 'v' else ('rect', 0, 0.47, 1, 0.53, '#24601e'),
                         ('lerp', '#62b246', 0.1, 0.7, 'x' if ax == 'v' else 'y')] for g in ('north', 'south')}
    O = (0, 16.0)
    for n, (kind, ang, sc) in enumerate((('h', -1, 0.8), ('h', 1, 0.8), ('v', -22.5, 0.95), ('v', 22.5, 0.95), ('v', 0, 1.05))):
        z = LZ + 1.4 - n * 0.35
        if kind == 'v':                                                                                 # leaves fanning upward
            rk = dict(rot=('z', ang), rot_origin=[0, 16.0, z]) if ang else {}
            y = 16.0
            for w in widths:
                h = 1.35 * sc
                cb(hdr, 0, y, z, w * sc, h, 0.4, 'leaf_d' if n == 4 else 'leaf', decals=LD('v'), **rk)
                y += h
        else:                                                                                           # side leaves lying out, tipped up 22.5
            s_ = ang
            rk = dict(rot=('z', s_ * 22.5), rot_origin=[0, 16.6, z])
            x = 0.0
            for w in widths:
                L = 1.35 * sc
                cb(hdr, s_ * (x + L / 2), 16.6 - w * sc / 2, z, L, w * sc, 0.4, 'leaf', decals=LD('h'), **rk)
                x += L
    cb(hdr, 0, 16.0, LZ, 3.0, 1.6, 1.0, 'shorts')                                                          # binding cord
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 3.5, 9.5, 0], body)
        cb(a, sx * 3.1, 8.4, -1.4, 1.8, 1.8, 3.4, S)                                                     # upper arm
        cb(a, sx * 2.4, 8.8, -3.8, 1.7, 1.7, 2.4, S)                                                     # forearm
        cb(a, sx * 1.3, 9.9, -5.6 - (1.6 if sx > 0 else 0), 2.0, 2.2, 2.0, S)                             # hands wrapped round the pipe
    pp = m.bone('pipe', [0, 11.5, -4], body)
    cb(pp, 0, 10.7, -10.6, 1.6, 1.6, 13.6, 'pipe', decals={f: [('lerp', '#e0c888', 0.0, 0.4, 'y')] for f in ('east', 'west')})   # long bamboo blowpipe
    for z in (-6.2, -10.4, -14.6):
        cb(pp, 0, 10.5, z, 2.0, 2.0, 0.6, 'pipe_d')                                                     # bamboo nodes
    cb(pp, 0, 10.4, -4.0, 2.2, 2.2, 1.0, 'pipe_d')                                                      # mouthpiece
    mz = m.bone('muzzle', [0, 11.5, -18.8], pp)
    cb(mz, 0, 10.1, -18.4, 2.8, 2.8, 1.4, 'pipe', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#2a1e10')]})   # flared muzzle
    m.hitbox(0.6, 1.4)
    return m


def royal_hog():
    """Royal Hog: stocky pink hog in a little silver knight helm with visor slits + team plume, angry eyes under the
    helm, big snout with nostrils, ivory tusks, floppy ears, team saddle blanket with gold trim, curly tail, dark hooves."""
    m = new_model('clash_royal_hog')
    m.mats_({'pig': ('#e9a0a0', 'skin'), 'pig_d': ('#cc8080', 'skin'), 'snout': ('#f0b4b4', 'skin'), 'hoof': ('#4a3028', 'leather'),
             'tusk': ('#efe6cc', 'soft'), 'steel': ('#aeb6be', 'metal'), 'steel_d': ('#7c848e', 'metal'), 'steel_l': ('#d4dae0', 'metal'),
             'tc': ('#efefef', 'cloth'), 'gold': ('#e2b23a', 'metal'), 'void': ('#1a1c20', 'plain')})
    PG = lambda: {f: [('lerp', '#cc8080', 0.65, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')}
    root = m.bone('root', [0, 0, 0])
    for name, (x, z) in (('fl_leg', (-3, -5)), ('fr_leg', (3, -5)), ('bl_leg', (-3, 5)), ('br_leg', (3, 5))):
        lg = m.bone(name, [x, 6, z], root)
        cb(lg, x, 1.6, z, 3.4, 5.0, 3.4, 'pig', decals=PG())                                        # stubby leg
        cb(lg, x, 0, z - 0.2, 3.6, 1.8, 3.8, 'hoof', decals={'north': [('rect', 0.47, 0, 0.53, 1, '#2a1a14')]})   # split hoof
    body = m.bone('body', [0, 10, 0], root)
    cb(body, 0, 5.4, 0.2, 10.4, 8.6, 15.0, 'pig', decals={**PG(), 'up': [('shade', 0, 0, 1, 1, 1.05)]})   # round body
    cb(body, 0, 6.4, 0.2, 11.0, 6.6, 13.6, 'pig')                                                    # belly roundness
    sb = m.bone('tc_saddle', [0, 14, 0], body)
    cb(sb, 0, 9.0, 0.6, 11.4, 5.2, 7.6, 'tc', decals={f: [('rect', 0, 0.85, 1, 1, '#e2b23a')] for f in ('east', 'west')})   # team saddle blanket
    cb(sb, 0, 14.0, 0.6, 9.0, 0.4, 7.6, 'tc')
    for sx in (1, -1):
        cb(body, sx * 5.75, 8.6, 0.6, 0.3, 0.8, 7.8, 'gold')                                          # gold trim
    tl = m.bone('tail', [0, 12, 8], body)
    cb(tl, 0, 11.6, 7.9, 0.8, 0.8, 0.8, 'pig_d'); cb(tl, 0.6, 12.2, 8.4, 0.8, 1.2, 0.8, 'pig_d'); cb(tl, 0, 13.0, 8.8, 1.2, 0.8, 0.8, 'pig_d')   # curly tail
    hd = m.bone('head', [0, 10, -8], body)
    face = pix(["........", "........", "........", "........", ".kk..kk.", ".wb..bw.", "........", "........"], {'k': '#5a2a2a', 'w': '#ffffff', 'b': '#2a1a10'})
    cb(hd, 0, 6.6, -10.2, 9.0, 8.4, 7.2, 'pig', decals={'north': face, **{f: [('lerp', '#cc8080', 0.7, 1.0, 'y')] for f in ('east', 'west')}})   # big head
    cb(hd, 0, 7.6, -14.6, 4.8, 3.6, 1.8, 'snout', decals={'north': [('rect', 0.22, 0.3, 0.4, 0.7, '#7a3a3a'), ('rect', 0.6, 0.3, 0.78, 0.7, '#7a3a3a')]})   # snout
    for sx in (1, -1):
        cb(hd, sx * 2.9, 6.4, -14.4, 0.9, 2.8, 0.9, 'tusk'); cb(hd, sx * 2.9, 9.0, -14.6, 0.7, 0.8, 0.7, 'tusk')   # upturned tusks
        cb(hd, sx * 4.9, 12.2, -9.0, 1.6, 2.4, 2.6, 'pig_d', rot=('z', sx * -22.5), rot_origin=[sx * 4.5, 13.4, -9.0])   # floppy ears
    # knight helm
    cb(hd, 0, 11.4, -10.0, 9.6, 3.8, 7.8, 'steel', decals={'north': [('rect', 0.12, 0.2, 0.42, 0.45, '#1a1c20'), ('rect', 0.58, 0.2, 0.88, 0.45, '#1a1c20'),
                                                                     ('shade', 0, 0, 1, 0.15, 1.2)], 'up': [('shade', 0, 0, 1, 1, 1.1)]}, dens=2)   # helm with visor slits
    cb(hd, 0, 15.2, -10.0, 7.2, 1.2, 6.0, 'steel')                                                    # rounded dome
    cb(hd, 0, 15.6, -10.0, 1.2, 1.4, 7.0, 'steel_l')                                                  # crest ridge
    cb(hd, 0, 11.2, -14.0, 9.8, 0.6, 0.4, 'steel_d')                                                 # rim
    for sx in (1, -1):
        cb(hd, sx * 3.6, 12.6, -14.0, 0.8, 0.8, 0.3, 'steel_l')                                       # rivets
    pl = m.bone('tc_plume', [0, 15, -12], hd)
    for (z, y, h) in ((-10.0, 16.8, 2.4), (-8.6, 17.6, 2.4), (-7.0, 17.8, 2.0), (-5.6, 17.0, 1.8)):
        cb(pl, 0, y, z, 1.4, h, 1.6, 'tc')                                                            # team plume sweeping back
    m.hitbox(0.9, 1.2)
    return m


def executioner():
    """Executioner: chubby bare-chested brute in a black stitched leather hood with eye holes, big red nose, team kilt
    with notched hem, wide belt with gold buckle, black pants + boots, long black gloves, huge double-bladed axe."""
    m = new_model('clash_executioner')
    m.mats_({'skin': ('#e8a882', 'skin'), 'skin_d': ('#c88866', 'skin'), 'hood': ('#2a2a30', 'leather'), 'hood_l': ('#3e3e46', 'leather'),
             'nose': ('#e0605a', 'skin'), 'pants': ('#2e2e34', 'cloth'), 'boot': ('#222226', 'leather'), 'tc': ('#e6e6e6', 'cloth'),
             'tc_d': ('#bcbcbc', 'cloth'), 'belt': ('#6a4026', 'leather'), 'gold': ('#e2b23a', 'metal'), 'glove': ('#2a2a30', 'leather'),
             'wood': ('#6a4026', 'wood'), 'blade': ('#b4bcc6', 'metal'), 'blade_l': ('#dfe4ea', 'metal'), 'blade_d': ('#7e8690', 'metal')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = m.bone('leg_' + side, [x, 14.4, 0], root)
        tp = m.bone('tc_pants_' + side, [x, 14.4, 0], lg)
        cb(lg, x, 3.6, 0, 3.8, 10.8, 3.8, 'pants')                                                    # black pants
        cb(lg, x, 0, -0.5, 4.2, 3.8, 4.8, 'boot', decals={'up': [('shade', 0, 0, 1, 1, 1.1)]})          # boots
        cb(lg, x, 3.2, 0, 4.4, 1.0, 4.4, 'hood_l')
    body = m.bone('body', [0, 14.4, 0], root)
    kt = m.bone('tc_kilt', [0, 14.4, 0], body)
    cb(kt, 0, 10.0, 0, 11.6, 5.0, 7.4, 'tc', decals={f: [('lerp', '#c4c4c4', 0.5, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # team kilt
    for i, x in enumerate((-4.8, -2.4, 0.0, 2.4, 4.8)):
        for z in (-3.75, 3.75):
            cb(kt, x, 8.6, z, 1.6, 1.4, 0.3, 'tc_d' if i % 2 else 'tc')                                  # notched hem tabs
    for sx in (1, -1):
        for z in (-1.8, 1.8):
            cb(kt, sx * 5.85, 8.6, z, 0.3, 1.4, 1.6, 'tc')
    cb(body, 0, 15.0, 0, 12.0, 2.6, 7.8, 'belt', decals={'north': [('rect', 0, 0.45, 1, 0.55, '#4a2a16')]})     # wide belt
    cb(body, 0, 14.8, -4.0, 3.6, 3.0, 0.5, 'gold', decals={'north': [('rect', 0.25, 0.3, 0.75, 0.7, '#6a4026')]})   # gold buckle
    cb(body, 0, 17.6, 0.2, 11.0, 11.2, 7.2, S, decals={'north': [('rect', 0.48, 0.15, 0.52, 0.5, '#c88866'), ('lerp', '#d29270', 0.6, 1.0, 'y')]})   # chubby bare chest
    cb(body, 0, 17.0, -0.5, 10.0, 6.0, 7.2, S)                                                          # pot belly
    hd = m.bone('head', [0, 28.8, 0], body)
    cb(hd, 0, 28.6, -0.2, 8.4, 8.6, 8.0, S, dens=2, decals={'north': [('rect', 0.3, 0.85, 0.7, 0.9, '#8a3a32'), ('rect', 0.36, 0.82, 0.64, 0.85, '#ffffff')]})   # face (mouth)
    cb(hd, 0, 32.6, -4.6, 8.8, 4.8, 0.8, 'hood', decals={'north': [('rect', 0.12, 0.25, 0.42, 0.6, '#f2e6dc'), ('rect', 0.58, 0.25, 0.88, 0.6, '#f2e6dc'),
                                                               ('rect', 0.22, 0.3, 0.36, 0.55, '#3a5aa8'), ('rect', 0.64, 0.3, 0.78, 0.55, '#3a5aa8'),
                                                               ('rect', 0.48, 0, 0.52, 0.2, '#56565e')]}, dens=2)   # mask with eye holes + stitched seam
    cb(hd, 0, 36.8, 0.2, 9.2, 1.4, 9.0, 'hood', decals={'up': [('rect', 0.47, 0, 0.53, 1, '#56565e')]})           # hood top
    for sx in (1, -1):
        cb(hd, sx * 4.4, 27.0, 0.2, 0.8, 10.0, 8.6, 'hood')                                             # hood sides
        cb(hd, sx * 3.8, 26.2, -3.4, 1.8, 3.2, 2.2, 'hood_l')                                           # cheek flaps
    cb(hd, 0, 27.0, 4.4, 9.2, 10.0, 0.8, 'hood')
    cb(hd, 0, 30.6, -5.0, 2.4, 2.2, 1.8, 'nose'); cb(hd, 0, 31.2, -5.6, 1.6, 1.4, 1.0, 'nose')            # big red nose
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.0
        a = m.bone('arm_' + side, [x, 26.4, 0], body)
        cb(a, x + sx * 0.4, 22.0, 0, 4.0, 6.6, 4.0, S, decals={f: [('lerp', '#c88866', 0.7, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # bare upper arm
        cb(a, x + sx * 0.4, 14.4, 0, 4.4, 7.8, 4.4, 'glove', decals={f: [('shade', 0, 0, 0.3, 1, 1.2)] for f in ('north', 'south')})   # long black glove
        cb(a, x + sx * 0.4, 21.6, 0, 4.8, 1.2, 4.8, 'hood_l')                                           # glove cuff
        cb(a, x + sx * 0.4, 12.6, -0.6, 4.6, 2.2, 4.6, 'glove')                                          # fist
    ax = m.bone('axe', [7.2, 15.6, -0.24], m.by_name('arm_r'))
    Y = 13.7                                                                                  # fist centre
    cb(ax, 6.4, Y - 0.7, -5.6, 1.4, 1.4, 19.0, 'wood', decals={f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')})   # haft gripped in the fist, pointing forward
    cb(ax, 6.4, Y - 1.0, 3.8, 2.0, 2.0, 1.2, 'blade_d')                                                  # pommel cap
    cb(ax, 6.4, Y - 1.4, -14.6, 2.2, 2.8, 2.6, 'blade_d')                                                # head socket
    for sy in (1, -1):                                                                                   # double crescent blades (up + down)
        for (dy, h, d) in ((1.4, 2.0, 5.0), (3.0, 1.8, 7.4), (4.6, 1.8, 9.4), (6.2, 1.2, 8.0)):
            y0 = Y + sy * dy - h / 2
            cb(ax, 6.4, y0, -14.6, 0.8, h, d, 'blade' if dy < 6 else 'blade_l', decals={'east': [('lerp', '#dfe4ea', 0.0, 0.3, 'y')], 'west': [('lerp', '#dfe4ea', 0.0, 0.3, 'y')]})
    m.hitbox(1.0, 2.6)
    return m


def goblin_brawler():
    """Goblin Brawler: hulking hunched goblin, small head with a huge unibrow, big nose + cheeky grin, pointy ears,
    massive arms with bandaged fists, shoulder tattoo, team suspenders, brown shorts, bare green shins + big feet."""
    m = new_model('clash_goblin_brawler')
    m.mats_({'skin': ('#9ccc3e', 'skin'), 'skin_d': ('#7aa82c', 'skin'), 'brow': ('#4e7e1e', 'hair'), 'nose': ('#d0a868', 'skin'),
             'shorts': ('#5a4634', 'cloth'), 'shorts_d': ('#463626', 'cloth'), 'wrap': ('#e8dcc0', 'cloth'), 'wrap_d': ('#c8b898', 'cloth'),
             'tc': ('#efefef', 'cloth'), 'btn': ('#d8c08a', 'metal'), 'ear_in': ('#d8b890', 'skin')})
    S = 'skin'
    SK = lambda: {f: [('lerp', '#7aa82c', 0.65, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')}
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.25
        lg = m.bone('leg_' + side, [x, 13, 0], root)
        cb(lg, x, 6.0, 0, 5.4, 7.0, 5.6, 'shorts', decals={f: [('shade', 0, 0, 1, 0.2, 0.85)] for f in ('north', 'south', 'east', 'west')})   # shorts legs
        cb(lg, x, 6.0, 0, 5.8, 1.0, 6.0, 'shorts_d')                                                  # rolled hem
        tl = m.bone('tc_shorts_' + side, [x, 13, 0], lg)
        cb(lg, x, 1.6, 0, 3.6, 4.4, 3.6, S)                                                            # green shins
        cb(lg, x, 0, -0.8, 4.4, 1.8, 6.0, S, decals={'north': pix(["k.k.k.", "......"], {'k': '#7aa82c'})})   # big bare feet
    body = m.bone('body', [0, 13, 0], root)
    cb(body, 0, 12.0, 0, 11.4, 4.2, 7.0, 'shorts', decals={'north': [('rect', 0, 0, 1, 0.25, '#463626')]})   # shorts waist
    cb(body, 0, 15.6, 0.4, 13.0, 7.0, 8.4, S, decals=SK())                                               # belly
    cb(body, 0, 21.0, 0.2, 16.0, 7.4, 9.6, S, decals={'north': [('rect', 0.48, 0.1, 0.52, 0.9, '#7aa82c'), ('shade', 0, 0.7, 1, 1, 0.85)], **{f: [('lerp', '#7aa82c', 0.6, 1.0, 'y')] for f in ('east', 'west', 'south')}})   # massive chest
    cb(body, 0, 27.6, 1.0, 11.0, 2.0, 7.0, S)                                                            # traps
    ts = m.bone('tc_shorts', [0, 13, 0], body)
    for sx in (1, -1):
        cb(ts, sx * 3.6, 15.4, -4.85, 1.8, 13.0, 0.4, 'tc')                                               # team suspenders, front
        cb(ts, sx * 3.0, 15.4, 5.05, 1.8, 13.0, 0.4, 'tc')                                                # back
        cb(ts, sx * 3.4, 28.4, 0.2, 1.8, 0.5, 10.4, 'tc')
        cb(body, sx * 3.6, 15.0, -5.2, 1.2, 1.4, 0.4, 'btn')
    hd = m.bone('head', [0, 28.6, 0], body)
    face = pix(["........", "........", "........", ".wb..bw.", "........", "........", "........", "........"], {'w': '#fff2a0', 'b': '#3a2a10'})
    face += [('rect', 0.26, 0.72, 0.32, 0.76, '#4a2414'), ('rect', 0.68, 0.72, 0.74, 0.76, '#4a2414'),
             ('rect', 0.32, 0.76, 0.68, 0.82, '#4a2414'), ('rect', 0.36, 0.76, 0.64, 0.79, '#ffffff')]
    cb(hd, 0, 28.6, -2.6, 8.0, 7.6, 7.6, S, decals={'north': face, 'up': [('shade', 0, 0, 1, 1, 1.06)]}, dens=2)   # small head
    cb(hd, 0, 33.8, -6.7, 7.6, 1.2, 1.2, 'brow', decals={'north': [('rect', 0, 0.6, 1, 1, '#3e6a16')]})        # huge unibrow
    cb(hd, 0, 30.6, -7.2, 2.2, 2.4, 1.8, 'nose'); cb(hd, 0, 30.8, -8.2, 1.6, 1.6, 1.0, 'nose')                    # big nose
    for sx, side in ((1, 'r'), (-1, 'l')):
        e = m.bone('ear_' + side, [sx * 5.2, 33.8, 0], hd)
        cb(e, sx * 4.6, 31.2, -2.6, 1.4, 3.6, 1.2, S); cb(e, sx * 6.0, 32.0, -2.6, 1.8, 2.8, 1.0, S)              # pointy ears
        cb(e, sx * 7.4, 33.0, -2.6, 1.4, 1.6, 0.8, 'skin_d')
        cb(e, sx * 5.8, 32.2, -3.15, 2.0, 1.8, 0.1, 'ear_in')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.75
        a = m.bone('arm_' + side, [x, 26.0, 0], body)
        cb(a, x, 22.6, 0, 7.4, 6.4, 7.4, S, decals={'up': [('shade', 0, 0, 1, 1, 1.08)], 'east' if sx > 0 else 'west':
                                                      [('rect', 0.2, 0.3, 0.8, 0.4, '#5a8a2a'), ('rect', 0.3, 0.5, 0.7, 0.6, '#5a8a2a')] if sx > 0 else []})   # huge shoulder (tattoo on the right)
        cb(a, x, 17.4, 0, 6.2, 5.6, 6.2, S, decals=SK())                                                 # upper arm
        cb(a, x, 13.6, -0.4, 6.8, 4.0, 6.8, S, decals=SK())                                              # forearm
        f = m.bone('fist_' + side, [x, 13.0, 0], a)
        cb(f, x, 7.2, -0.6, 7.6, 6.4, 7.6, S, decals={'north': pix(["......", ".k.k.k", "......", "......"], {'k': '#7aa82c'})})   # big fist
        cb(f, x, 10.6, -0.6, 8.0, 2.6, 8.0, 'wrap', decals={f2: [('rect', 0, 0.45, 1, 0.55, '#c8b898')] for f2 in ('north', 'south', 'east', 'west')})   # bandage wrap
        cb(f, x + sx * 1.0, 9.4, -4.6, 1.4, 1.0, 0.4, 'wrap_d')                                         # loose bandage end
    m.hitbox(1.2, 3.0)
    return m


def goblin_cage():
    """Goblin Cage: chunky wooden frame with steel corner brackets (pyramid studs), thick steel bars on every side,
    plank roof with a steel padlock plate on the front, team banners + team plate; a brawny goblin inside gripping the bars."""
    m = new_model('clash_goblin_cage')
    m.mats_({'wood': ('#a8703a', 'soft'), 'wood_d': ('#7e5028', 'soft'), 'steel': ('#9aa0a8', 'soft'), 'steel_l': ('#c2c8ce', 'soft'),
             'steel_d': ('#6e747c', 'soft'), 'key': ('#26282c', 'plain'), 'tc': ('#efefef', 'cloth'), 'skin': ('#9ccc3e', 'skin'),
             'skin_d': ('#7aa82c', 'skin'), 'brow': ('#5a8a24', 'hair'), 'nose': ('#d0b070', 'skin'), 'shorts': ('#5a4634', 'cloth'),
             'wrap': ('#e8dcc0', 'cloth')})
    WD = lambda: {f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    MT = lambda: {f: [('fn', _soft_metal(1.15, 0.85))] for f in ('north', 'south', 'east', 'west')}
    root = m.bone('root', [0, 0, 0])
    fr = m.bone('frame', [0, 0, 0], root)
    H = 34.0
    for sx in (1, -1):
        for sz in (1, -1):
            cb(fr, sx * 20, 0, sz * 20, 5.0, H, 5.0, 'wood', decals=WD())                               # corner posts
            cb(fr, sx * 20.4, 0, sz * 20.4, 7.0, 6.0, 7.0, 'steel', decals=MT())                        # steel corner bracket
            for (fx, fz) in ((sx * 23.95, sz * 20.4), (sx * 20.4, sz * 23.95)):
                w = (0.6, 2.6) if abs(fx) > 23 else (2.6, 0.6)
                cb(fr, fx + (sx * 0.3 if abs(fx) > 23 else 0), 1.7, fz + (sz * 0.3 if abs(fz) > 23 else 0), w[0], 2.6, w[1], 'steel_l')   # pyramid stud
    for sz in (1, -1):
        cb(fr, 0, 0, sz * 20, 35.0, 4.0, 4.0, 'wood_d', decals=WD())                                     # bottom beams
        cb(fr, 0, H - 4.0, sz * 20, 45.0, 4.0, 4.0, 'wood', decals=WD())                                 # top beams
    for sx in (1, -1):
        cb(fr, sx * 20, 0, 0, 4.0, 4.0, 35.0, 'wood_d', decals=WD())
        cb(fr, sx * 20, H - 4.0, 0, 4.0, 4.0, 45.0, 'wood', decals=WD())
    tp = m.bone('tc_plate', [0, 2, -23], fr)
    cb(tp, 0, 0.8, -22.2, 10.0, 2.4, 0.4, 'tc')                                                         # team plate on the front beam
    for name, (ox, oz), axis in (('bars_f', (0, -19), 'x'), ('bars_b', (0, 19), 'x'), ('bars_r', (19, 0), 'z'), ('bars_l', (-19, 0), 'z')):
        bb = m.bone(name, [ox, 5, oz], root)
        for k in ((-13.0, -6.6, 6.6, 13.0) if name == 'bars_f' else (-9.0, -3.0, 3.0, 9.0)):
            x, z = (k, oz) if axis == 'x' else (ox, k)
            cb(bb, x, 4.0, z, 2.6, H - 8.0, 2.6, 'steel', decals={f: [('rect', 0.0, 0, 0.25, 1, '#c2c8ce')] for f in ('north', 'south', 'east', 'west')})   # thick steel bars
    rf = m.bone('roof', [0, 38, 0], root)
    cb(rf, 0, H, 0, 46.0, 3.0, 46.0, 'wood', decals={'up': [('fn', _staves(True, base=(168, 112, 58), seam=(110, 70, 34)))], **{f: [('fn', _soft_wood)] for f in ('north', 'south', 'east', 'west')}})   # plank roof
    cb(rf, 0, H + 3.0, 0, 40.0, 1.2, 40.0, 'wood_d')
    cb(rf, 0, H - 1.0, -23.6, 11.0, 7.0, 2.4, 'steel', decals={'north': [('fn', _soft_metal(1.15, 0.85)), ('rect', 0.44, 0.3, 0.56, 0.55, '#26282c'), ('rect', 0.47, 0.55, 0.53, 0.75, '#26282c')]})   # padlock plate + keyhole
    for sx, side in ((1, 'r'), (-1, 'l')):
        bn = m.bone('tc_banner_' + side, [sx * 22, 38, 0], rf)
        cb(bn, sx * 23.3, H - 9.0, 0, 0.4, 8.0, 7.0, 'tc')                                               # team banners on the sides
        cb(bn, sx * 23.3, H - 10.6, -2.0, 0.4, 1.6, 2.4, 'tc'); cb(bn, sx * 23.3, H - 10.6, 2.0, 0.4, 1.6, 2.4, 'tc')
    # brawny goblin inside
    gb = m.bone('gob', [0, 5, -8], root)
    cb(gb, 0, 4.0, -4.0, 9.0, 6.0, 7.0, 'shorts')                                                       # crouched hips
    cb(gb, 0, 10.0, -5.0, 12.0, 11.0, 7.0, 'skin', decals={'north': [('lerp', '#7aa82c', 0.6, 1.0, 'y')]})   # broad chest
    ts = m.bone('tc_strap', [0, 22, -8], gb)
    for sx in (1, -1):
        cb(ts, sx * 3.0, 10.0, -8.7, 1.6, 11.0, 0.4, 'tc')                                               # team suspenders
    hd = m.bone('gob_head', [0, 28, -8], gb)
    face = pix(["........", "........", "........", ".wb..wb.", "........", "........", "........", "........"], {'w': '#fff2a0', 'b': '#3a2a10'})
    face += [('rect', 0.28, 0.74, 0.72, 0.8, '#4a2414'), ('rect', 0.34, 0.74, 0.66, 0.77, '#ffffff')]
    cb(hd, 0, 20.4, -7.0, 9.0, 8.4, 8.4, 'skin', decals={'north': face}, dens=2)                         # big head
    cb(hd, 0, 25.6, -11.4, 7.6, 1.2, 1.0, 'brow')                                                        # one big unibrow
    cb(hd, 0, 22.8, -11.8, 2.0, 2.4, 1.6, 'nose')
    for sx in (1, -1):
        cb(hd, sx * 5.4, 24.6, -7.0, 1.8, 3.4, 1.0, 'skin'); cb(hd, sx * 7.0, 26.0, -7.0, 1.8, 2.4, 0.8, 'skin_d')   # pointy ears
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('gob_arm_' + side, [sx * 9, 25, -7], gb)
        cb(a, sx * 9.4, 14.0, -9.0, 4.0, 8.0, 4.0, 'skin')                                             # big arm reaching for the bars
        cb(a, sx * 9.4, 12.0, -12.6, 4.4, 4.4, 4.4, 'skin')                                             # fist on the bars
        cb(a, sx * 9.4, 12.0, -10.8, 4.8, 4.6, 1.6, 'wrap')                                              # bandage wrap
    for bn in m.bones:                                                                   # goblin presses up against the front bars
        if bn.name in ('gob', 'tc_strap', 'gob_head', 'gob_arm_r', 'gob_arm_l'):
            for c in bn.cubes:
                for key in ('frm', 'to', 'rot_origin'):
                    c[key] = [c[key][0] * 1.2, (c[key][1] - 2) * 1.08 - 1.0, (c[key][2] + 4.0) * 1.1 - 8.4]
    m.hitbox(2.6, 2.6)
    return m


def spear_goblin():
    """Spear Goblin (goblin rig x1.18): team bandana, leather pack straps, spear in hand, spare spears + round shield on the back. Base: big bald green head, long pointy ears, bushy brows, cheeky grin + long nose, skinny green body,
    team-colour suspenders over brown knee shorts, curly pointed shoes, steel dagger in the left hand."""
    m = new_model('clash_spear_goblin')
    m.mats_({'skin': ('#8cc63c', 'skin'), 'skin_d': ('#6fa62c', 'skin'), 'brow': ('#5a8a24', 'hair'), 'nose': ('#c8b878', 'skin'),
             'ear_in': ('#d8b890', 'skin'), 'shorts': ('#5a4634', 'cloth'), 'shorts_d': ('#463626', 'cloth'), 'shoe': ('#9a6a3e', 'leather'),
             'shoe_d': ('#7a5030', 'leather'), 'tc': ('#efefef', 'cloth'), 'strap': ('#6a4830', 'leather'), 'shield': ('#8a9098', 'metal'), 'shield_d': ('#6a7078', 'metal'), 'wood': ('#a8703a', 'wood'), 'btn': ('#d8c08a', 'metal'), 'blade': ('#c8ced6', 'metal'),
             'blade_d': ('#9aa2ac', 'metal'), 'grip': ('#6a3e22', 'wood'), 'brass': ('#c89a48', 'metal')})
    S = 'skin'
    allb = m.bone('all', [0, 0, 0])
    for sx, side in ((1, 'right'), (-1, 'left')):
        x = sx * 2.0
        lg = m.bone(side + '_leg', [x, 7.5, 0], allb)
        cb(lg, x, 4.4, 0, 3.4, 3.6, 3.6, 'shorts', decals={f: [('shade', 0, 0, 1, 0.2, 0.85)] for f in ('north', 'south', 'east', 'west')})   # baggy shorts leg
        cb(lg, x, 4.0, 0, 3.6, 0.8, 3.8, 'shorts_d')                                                     # rolled cuff
        cb(lg, x, 1.4, 0, 2.0, 2.8, 2.0, S)                                                                # skinny shin
        cb(lg, x, 0, -0.8, 2.8, 1.6, 4.6, 'shoe', decals={'up': [('shade', 0, 0, 1, 0.3, 1.1)]})            # long shoe
        cb(lg, x, 0.6, -3.4, 1.8, 1.0, 1.2, 'shoe'); cb(lg, x, 1.4, -4.0, 1.2, 1.0, 1.0, 'shoe_d')          # curled pointy toe
    body = m.bone('body', [0, 8, 0], allb)
    cb(body, 0, 7.4, 0, 7.4, 3.0, 4.4, 'shorts', decals={'north': [('rect', 0, 0, 1, 0.25, '#463626')]})      # shorts waist
    cb(body, 0, 10.2, 0, 6.6, 7.0, 3.8, S, decals={'north': [('rect', 0.48, 0.55, 0.52, 0.62, '#6fa62c'), ('lerp', '#7ab634', 0.6, 1.0, 'y')]})   # skinny torso (navel)
    cb(body, 0, 10.0, -0.3, 6.0, 2.6, 3.8, S)                                                            # little pot belly
    st = m.bone('straps', [0, 12, 0], body)
    for sx in (1, -1):
        cb(st, sx * 2.1, 10.0, -2.4, 1.4, 7.4, 0.4, 'strap', decals={'north': [('rect', 0, 0, 0.15, 1, '#4a3020'), ('rect', 0.85, 0, 1, 1, '#4a3020')]})   # leather pack straps, front
        cb(st, sx * 1.6, 10.0, 2.1, 1.4, 7.4, 0.4, 'strap')                                                   # back
        cb(st, sx * 2.1, 17.2, 0, 1.4, 0.5, 4.9, 'strap')                                                     # over the shoulder
        cb(body, sx * 2.1, 9.6, -2.75, 1.0, 1.2, 0.4, 'btn')                                               # brass clips at the waistband
        cb(body, sx * 1.6, 9.6, 2.45, 1.0, 1.2, 0.4, 'btn')
    hd = m.bone('head', [0, 17, 0], body)
    face = pix(["........", "........", "........", ".wb..wb.", "........", "........", "........", "........"], {'w': '#ffffff', 'b': '#4a2e1a'})
    face += [('rect', 0.24, 0.7, 0.3, 0.74, '#4a2414'), ('rect', 0.7, 0.7, 0.76, 0.74, '#4a2414'),             # friendly grin
             ('rect', 0.3, 0.74, 0.7, 0.8, '#4a2414'), ('rect', 0.34, 0.74, 0.66, 0.77, '#ffffff'), ('rect', 0.42, 0.8, 0.58, 0.83, '#4a2414')]
    cb(hd, 0, 17, -0.4, 8.4, 8.4, 8.0, S, decals={'north': face, 'up': [('shade', 0, 0, 1, 1, 1.06)]}, dens=2)   # big bald head
    for sx in (1, -1):
        cb(hd, sx * 2.0, 23.0, -4.6, 2.8, 0.9, 0.8, 'brow')                                               # bushy brows (relaxed)
    cb(hd, 0, 19.4, -5.2, 1.6, 2.2, 1.6, 'nose'); cb(hd, 0, 19.6, -6.4, 1.2, 1.4, 1.2, 'nose')                    # long nose
    bd = m.bone('xtc_bandana', [0, 24, 0], hd)
    cb(bd, 0, 23.0, -0.4, 8.8, 1.8, 8.4, 'tc', decals={'north': [('shade', 0, 0.8, 1, 1, 0.8)]})          # team bandana
    cb(bd, 0.8, 22.0, 4.0, 1.2, 2.0, 0.8, 'tc'); cb(bd, -0.6, 21.6, 4.1, 1.0, 2.2, 0.6, 'tc')              # knot tails
    for sx in (1, -1):                                                                                      # long pointy ears
        cb(hd, sx * 5.0, 19.6, -0.2, 1.6, 4.4, 1.2, S); cb(hd, sx * 6.6, 20.4, -0.2, 2.0, 3.8, 1.0, S)          # big leaf ears
        cb(hd, sx * 8.4, 21.4, -0.2, 2.0, 2.8, 0.9, S); cb(hd, sx * 10.0, 22.6, -0.2, 1.6, 1.8, 0.8, S)
        cb(hd, sx * 11.2, 23.8, -0.2, 1.0, 1.2, 0.6, 'skin_d')
        cb(hd, sx * 7.4, 20.8, -0.75, 3.6, 2.4, 0.1, 'ear_in')                                            # pinkish inner ear
    for sx, side in ((1, 'right'), (-1, 'left')):
        x = sx * 4.95
        a = m.bone(side + '_arm', [x, 16.5, -0.4], body)
        cb(a, x, 9.4, -0.4, 2.2, 7.4, 2.2, S, decals={f: [('lerp', '#7ab634', 0.7, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # skinny arm
        cb(a, x, 8.6, -0.4, 2.8, 2.2, 2.8, S)                                                            # hand
    SPT = 22.5                                                                             # spear tilted outwards
    sp = m.bone('spear', [-4.95, 10, -0.4], m.by_name('left_arm'))
    cb(sp, -4.95, -1.0, -1.0, 1.0, 21.0, 1.0, 'wood', rot=('z', SPT), rot_origin=[-4.95, 9, -1.0], decals={'north': [('lerp', '#7a4e26', 0.6, 1.0, 'y')]})   # long shaft held upright
    tw = m.bone('xtc_wrap', [-4.95, 20, -1.0], sp)
    cb(tw, -4.95, 17.6, -1.0, 1.8, 2.4, 1.8, 'tc', rot=('z', SPT), rot_origin=[-4.95, 9, -1.0])                                                       # team cloth wrap
    for (w, h, y) in ((2.2, 1.6, 20.0), (2.8, 2.2, 21.4), (2.0, 2.0, 23.4), (1.0, 1.6, 25.2)):
        cb(sp, -4.95, y, -1.0, w, h, 0.6, 'blade', rot=('z', SPT), rot_origin=[-4.95, 9, -1.0], decals={'north': [('rect', 0.45, 0, 0.55, 1, '#9aa2ac')]})   # leaf spear point
    Q = dict(rot=('z', -22.5), rot_origin=[2.2, 9.0, 3.4])                                       # javelin quiver slung on the back
    cb(body, 2.2, 6.6, 3.4, 3.2, 10.0, 3.0, 'strap', decals={f: [('fn', _soft_wood), ('rect', 0, 0.1, 1, 0.16, '#4a3020')] for f in ('north', 'south', 'east', 'west')}, **Q)
    cb(body, 2.2, 16.4, 3.4, 3.6, 0.8, 3.4, 'shoe_d', **Q)                                      # quiver rim
    cb(body, 2.2, 6.2, 3.4, 3.6, 0.8, 3.4, 'shoe_d', **Q)                                       # quiver base
    for (dx, dz, L) in ((-0.8, -0.6, 6.0), (0.7, 0.4, 7.2), (-0.2, 0.9, 5.2)):
        cb(body, 2.2 + dx, 17.0, 3.4 + dz, 0.6, L, 0.6, 'wood', **Q)                             # javelin shafts
        for (w, h, y) in ((1.6, 1.0, 17.0 + L), (2.0, 1.4, 18.0 + L), (1.2, 1.4, 19.4 + L), (0.5, 1.0, 20.8 + L)):
            cb(body, 2.2 + dx, y, 3.4 + dz, w, h, 0.4, 'blade', **Q)                             # javelin points
    bk = m.bone('xtc_quiver_wrap', [2.2, 12, 3.4], body)
    for y in (9.0, 13.4):
        cb(bk, 2.2, y, 3.4, 3.5, 1.2, 3.3, 'tc', **Q)                                            # team cloth bands
    for (w, h) in ((5.0, 3.8), (3.8, 5.0)):
        cb(body, -2.0, 12.4 - h / 2, 2.6, w, h, 0.7, 'shield', decals={'south': [('lerp', '#aab0b8', 0.0, 0.4, 'y')]})   # round shield on the back
    cb(body, -2.0, 11.6, 3.0, 1.4, 1.4, 0.5, 'shield_d')
    K = 1.18                                                                              # spear goblin is a bigger goblin
    for bn in m.bones:
        bn.origin = [v * K for v in bn.origin]
        for c in bn.cubes:
            c['frm'] = [v * K for v in c['frm']]; c['to'] = [v * K for v in c['to']]; c['rot_origin'] = [v * K for v in c['rot_origin']]
    m.hitbox(0.8, 1.6)
    return m


def night_witch():
    """Night Witch (from the witch rig): charcoal hood + cape, navy tattered dress, cyan glowing eyes + gem, bat-axe crystal staff. : big rounded purple hood with a drooping point and dark lining, hood stoles down the
    front, long tattered cape, pale lavender face with glowing pink eyes, dark grey bodice with lighter V panel, brown
    belt with a big gold skull buckle, flared pink skirt dissolving into long tattered strips, angular gold pauldrons,
    dark gauntlets with gold rims + claws (team cuffs), twisted staff with rope grip and a ram-horned skull, green wisp."""
    import random as _r
    m = new_model('clash_night_witch')
    m.mats_({'skin': ('#d4c4e4', 'soft'), 'skin_d': ('#b4a4cc', 'soft'), 'hood': ('#45454f', 'soft'), 'hood_l': ('#5a5a66', 'soft'),
             'hood_d': ('#33333b', 'soft'), 'lining': ('#1a1a20', 'soft'), 'bodice': ('#3a3a42', 'soft'), 'bodice_l': ('#55555e', 'soft'),
             'skirt': ('#2e3a8c', 'soft'), 'skirt_d': ('#3c4aa8', 'soft'), 'skirt_dd': ('#24306e', 'soft'), 'belt': ('#8a8e98', 'soft'),
             'gold': ('#b8bec8', 'soft'), 'gold_d': ('#8a909a', 'soft'), 'glove': ('#45474f', 'soft'), 'tc': ('#eeeeee', 'cloth'),
             'boot': ('#3a3a40', 'soft'), 'shaft': ('#2e2a36', 'soft'), 'shaft_l': ('#463f52', 'soft'), 'rope': ('#5a5a66', 'soft'),
             'bone': ('#e8dec6', 'soft'), 'bone_d': ('#c4b89c', 'soft'), 'horn': ('#b8986a', 'soft'), 'horn_d': ('#8a6c46', 'soft'),
             'eye': ('#5ef0ff', 'glow'), 'glowpink': ('#a46ab8', 'plain'), 'wisp': ('#7ff0c8', 'glow'), 'hole': ('#2e2620', 'plain')})
    CL = lambda *e: {g: [('fn', _folds())] + list(e) for g in ('north', 'south', 'east', 'west')}
    S = 'skin'
    R = _r.Random(7)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        cb(lg, sx * 1.8, 1.0, -0.6, 2.4, 5.0, 2.6, 'boot')                                               # dark pointy boots
    body = m.bone('body', [0, 12, 0], root)
    hem = ('lerp', '#4a5ac8', 0.55, 1.0, 'y')
    cb(body, 0, 8.0, 0.2, 7.8, 4.2, 5.0, 'skirt', decals=CL())                                             # skirt top
    cb(body, 0, 3.0, 0.2, 9.4, 5.0, 6.2, 'skirt', decals=CL(hem))                                          # flared skirt
    for x in (-3.9, -2.2, -0.6, 1.0, 2.6, 4.0):                                                              # tattered strips, front + back
        for z, mats in ((-2.95, ('skirt_d', 'skirt')), (3.35, ('skirt_d', 'skirt_dd'))):
            h = R.choice((2.6, 3.6, 4.8, 5.8))
            cb(body, x, 3.0 - h, z, 1.5, h, 0.5, R.choice(mats), decals={'north': [('lerp', '#5a6ad8', 0.3, 1.0, 'y')], 'south': [('lerp', '#5a6ad8', 0.3, 1.0, 'y')]})
    for sx in (1, -1):
        for z in (-1.8, 0.2, 2.2):
            h = R.choice((2.8, 4.0, 5.2))
            cb(body, sx * 4.45, 3.0 - h, z, 0.5, h, 1.6, R.choice(('skirt_d', 'skirt')), decals={'east': [('lerp', '#5a6ad8', 0.3, 1.0, 'y')], 'west': [('lerp', '#5a6ad8', 0.3, 1.0, 'y')]})
    cb(body, 0, 12.0, 0, 7.0, 10.6, 3.8, 'bodice', decals={'north': [('rect', 0.38, 0.0, 0.62, 1.0, '#7a7c84'), ('rect', 0.49, 0, 0.51, 1, '#3e4046'), ('lerp', '#3e4046', 0.7, 1.0, 'y')]})   # bodice + V panel
    cb(body, 0, 21.8, -1.95, 2.6, 0.8, 0.1, 'skin')                                                         # neckline
    cb(body, 0, 11.6, 0, 7.6, 1.6, 4.4, 'belt')                                                            # belt
    cb(body, 0, 10.6, -2.6, 2.2, 2.6, 0.8, 'eye')                                                          # glowing gem buckle
    for sx in (1, -1):
        cb(body, sx * 2.2, 11.0, -2.45, 2.2, 1.8, 0.5, 'gold'); cb(body, sx * 3.0, 10.4, -2.45, 1.0, 0.8, 0.5, 'gold_d')   # silver bat wings
    cb(body, 0, 13.2, -1.95, 0.4, 8.4, 0.1, 'eye')                                                          # glowing seam up the bodice
    td = m.bone('tc_trim', [0, 4, 0], body)
    for sx in (1, -1):
        cb(td, sx * 4.0, 11.4, 0, 0.3, 1.0, 4.0, 'tc')                                                      # team belt ends
    cp = m.bone('cape', [0, 24, 2.6], body)
    cb(cp, 0, 1.6, 3.0, 9.8, 21.4, 0.9, 'hood', decals={'south': [('fn', _folds(0.78, 1.12, 2)), ('lerp', '#26262c', 0.6, 1.0, 'y')]})   # long cape
    for x in (-4.0, -1.6, 0.8, 3.2):
        h = R.choice((3.0, 4.4, 5.6))
        cb(cp, x, 1.6 - h, 3.0, 2.2, h, 0.9, R.choice(('hood_d', 'hood')))                                   # ragged cape tails
    for sx in (1, -1):
        cb(cp, sx * 4.6, 3.0, 1.2, 0.8, 19.6, 3.6, 'hood', decals={'east': [('fn', _folds())], 'west': [('fn', _folds())]})
        cb(body, sx * 2.9, 11.0, -2.2, 1.6, 12.0, 0.5, 'hood', decals={'north': [('fn', _folds(0.85, 1.1, 1))]})   # hood stoles down the front
        cb(body, sx * 2.9, 9.0, -2.2, 1.2, 2.0, 0.5, 'hood_d')
    hd = m.bone('head', [0, 24, 0], body)
    face = [('rect', 0.4, 0.8, 0.6, 0.85, '#8a4a86'), ('rect', 0.44, 0.85, 0.56, 0.88, '#8a7ab8')]
    cb(hd, 0, 24.4, 0.2, 6.8, 7.2, 6.8, S, decals={'north': face + [('shade', 0, 0, 1, 0.38, 0.5), ('shade', 0, 0.38, 1, 0.5, 0.75)],
                                                   'east': [('shade', 0, 0, 1, 0.5, 0.6)], 'west': [('shade', 0, 0, 1, 0.5, 0.6)]})   # face, upper half in hood shadow
    cb(hd, 0, 23.6, -1.4, 4.4, 1.0, 3.8, S)                                                                 # narrow chin
    cb(hd, 0, 26.8, -3.3, 0.8, 1.0, 0.4, 'skin_d')                                                          # little nose
    for sx in (1, -1):
        cb(hd, sx * 1.7, 27.6, -3.2, 1.8, 1.4, 0.1, 'eye', decals={'north': [('rect', 0.3, 0.25, 0.7, 0.7, '#e0fcff')]})   # big glowing eyes
    ho = m.bone('hood', [0, 24, 0], hd)
    def rnd(b, x, y, z, w, h, d, c, mat, **kw):
        cb(b, x, y, z, w, h, d - 2 * c, mat, **kw); cb(b, x, y, z, w - 2 * c, h, d, mat, **kw)
    HL = lambda: {g: [('lerp', '#64646f', 0.0, 0.5, 'y'), ('fn', _folds(0.86, 1.08, 2))] for g in ('north', 'south', 'east', 'west')}
    for sx in (1, -1):
        cb(ho, sx * 4.4, 21.4, 0.6, 1.4, 10.4, 8.4, 'hood', decals=HL())                                     # hood sides
        cb(ho, sx * 3.75, 21.8, -3.35, 0.3, 9.8, 0.6, 'lining')                                             # dark lining at the opening
        cb(ho, sx * 4.2, 21.4, -3.9, 1.6, 10.0, 0.8, 'hood_l', decals={'north': [('lerp', '#2e2e36', 0.6, 1.0, 'y')]})   # rolled front edge
    cb(ho, 0, 21.4, 4.6, 9.6, 10.4, 1.2, 'hood_d', decals=HL())                                             # back
    cb(ho, 0, 31.6, 0.6, 10.2, 2.4, 9.8, 'hood', decals={**HL(), 'up': [('shade', 0, 0, 1, 1, 1.1)]})       # boxy hood top
    cb(ho, 0, 30.4, -4.2, 9.2, 1.6, 2.0, 'hood_l', decals={'north': [('lerp', '#2e2e36', 0.4, 1.0, 'y')], 'up': [('shade', 0, 0, 1, 1, 1.1)]})   # brim
    for (w, yb) in ((3.2, 29.6), (1.4, 28.8)):
        cb(ho, 0, yb, -4.5, w, 30.4 - yb, 2.4, 'hood', decals={'north': [('lerp', '#2e2e36', 0.5, 1.0, 'y')]})   # V peak dipping between the eyes
    cb(ho, 0, 30.2, -3.4, 6.6, 0.4, 0.4, 'lining')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.5
        a = m.bone('arm_' + side, [x, 22.5, 0], body)
        cb(a, x + sx * 0.3, 20.6, 0, 4.0, 2.6, 4.4, 'gold', decals={'up': [('shade', 0, 0, 1, 1, 1.15)], 'north': [('lerp', '#8a909a', 0.5, 1.0, 'y')]})   # pauldron
        cb(a, x + sx * 0.5, 22.6, 0, 3.0, 1.2, 3.4, 'gold')
        cb(a, x + sx * 2.2, 21.4, 0, 1.0, 1.4, 1.4, 'gold_d')                                               # pauldron spike
        cb(a, x + sx * 2.9, 21.7, 0, 0.6, 0.8, 0.8, 'gold_d')
        cb(a, x, 15.0, 0, 2.6, 5.8, 2.6, S, decals={g: [('lerp', '#bba8c4', 0.5, 1.0, 'y')] for g in ('north', 'south', 'east', 'west')})   # pale arm
        cb(a, x, 9.2, 0, 3.0, 6.0, 3.0, 'glove', decals={g: [('shade', 0, 0, 0.3, 1, 1.15)] for g in ('north', 'south')})   # gauntlet
        cb(a, x, 14.6, 0, 3.6, 1.0, 3.6, 'gold')                                                           # gold rim
        cb(a, x, 13.6, 0, 3.4, 1.0, 3.4, 'gold_d')                                                         # silver cuff
        for k in (-0.9, 0.0, 0.9):
            cb(a, x + k, 8.0, -0.9, 0.5, 1.4, 0.5, 'glove')                                                 # claws
    st = m.bone('staff', [5.5, 13.5, -2.6], m.by_name('arm_r'))
    SX = 1.8
    for i, y in enumerate(range(0, 36, 2)):
        cb(st, 5.5 + SX + (0.3 if i % 2 else -0.3), y, -2.6 + (0.2 if i % 3 == 0 else -0.2), 1.6, 2.0, 1.6, 'shaft' if i % 2 else 'shaft_l')   # twisted staff
    for y in (11.4, 12.4, 13.4):
        cb(st, 5.5 + SX, y, -2.6, 2.0, 0.8, 2.0, 'rope')                                                    # rope grip
    ob = m.bone('crystal', [5.5, 40, -2.6], st)
    X0, Z0 = 5.5 + SX, -2.6
    cb(ob, X0, 35.0, Z0, 2.8, 1.4, 2.8, 'gold_d')                                                          # silver socket
    for (w, h, y) in ((3.6, 2.4, 36.4), (4.4, 2.6, 38.8), (3.4, 1.8, 41.4), (1.8, 1.0, 43.2)):
        cb(ob, X0, y, Z0, w, h, w, 'eye', decals={'north': [('rect', 0.2, 0.2, 0.45, 0.6, '#e0fcff')]})          # big cyan crystal
    for sx in (1, -1):                                                                                      # bat-wing axe blades
        cb(ob, X0 + sx * 3.4, 37.2, Z0, 2.4, 5.4, 0.8, 'gold', decals={'north': [('lerp', '#e8ecf2', 0.0, 0.4, 'y')]})
        cb(ob, X0 + sx * 5.0, 36.0, Z0, 1.6, 7.6, 0.8, 'gold', decals={'north': [('lerp', '#e8ecf2', 0.0, 0.4, 'y')]})
        cb(ob, X0 + sx * 6.1, 35.0, Z0, 0.8, 2.4, 0.8, 'gold_d'); cb(ob, X0 + sx * 6.1, 41.2, Z0, 0.8, 2.6, 0.8, 'gold_d')   # wing points
    wl = m.by_name('arm_l')
    m.hitbox(0.8, 2.4)
    return m


def _soft_metal(top=1.18, bot=0.78, spec=True):
    """brushed metal: soft vertical gradient, fine horizontal brush streaks, bright top edge, glints + a few scratches"""
    def f(img, rng):
        import numpy as _np, random as _r
        h, w, _ = img.shape
        R = _r.Random(h * 97 + w * 13 + int(top * 100))
        img[:] = img * _np.linspace(top, bot, h).reshape(h, 1, 1)
        for y in range(h):                                                         # brush streaks
            x = 0
            while x < w:
                L = R.randint(2, 6)
                img[y, x:x + L] *= R.choice((0.95, 0.98, 1.0, 1.03, 1.06))
                x += L
        if spec and h >= 3:                                                        # soft specular band
            sy = max(0, h // 4)
            img[sy, :] *= 1.15
        for _ in range(max(1, (w * h) // 90)):                                     # little glints
            x, y = R.randrange(w), R.randrange(h)
            img[y, x] = _np.minimum(img[y, x] * 1.3, 255)
        for _ in range(max(0, (w * h) // 140)):                                    # scratches
            x, y = R.randrange(w), R.randrange(h)
            for k in range(R.randint(2, 4)):
                if 0 <= x + k < w and 0 <= y + k < h: img[y + k, x + k] *= 1.18
        img[0, :] = _np.minimum(img[0, :] * 1.25, 255)                             # lit top edge
        img[-1, :] *= 0.75                                                         # shadowed bottom edge
        img[:] = _np.clip(img, 0, 255)
    return f


def _soft_wood(img, rng):
    """clean wood: a few soft grain lines, gentle light-to-dark, darker rim"""
    import numpy as _np, random as _r
    h, w, _ = img.shape
    R = _r.Random(h * 17 + w)
    img[:] = img * _np.linspace(1.1, 0.9, h).reshape(h, 1, 1)
    for _ in range(max(2, h // 3)):
        y = R.randrange(h); x0 = R.randrange(w); L = R.randint(w // 3, w)
        img[y, x0:x0 + L] *= 0.9
    img[0, :] *= 0.85; img[-1, :] *= 0.8; img[:, 0] *= 0.85; img[:, -1] *= 0.85
    img[:] = _np.clip(img, 0, 255)


def zappies():
    """Zappy (clean): rounded dark chassis with a wedge nose and two corner spikes, four big wooden octagon wheels with
    round iron hubcaps, two stacked silver donut rings with a silver ball on a neck, team pennant on a pole; sparks."""
    import math as _m
    m = new_model('clash_zappies')
    m.mats_({'body': ('#5e636b', 'soft'), 'body_l': ('#737882', 'soft'), 'body_d': ('#4a4e55', 'soft'), 'wood': ('#a06e46', 'soft'),
             'wood_d': ('#7e5434', 'soft'), 'cap': ('#3c4046', 'soft'), 'silver': ('#cfd4da', 'soft'), 'silver_d': ('#9ea6ae', 'soft'),
             'pole': ('#b4bac0', 'soft'), 'tc': ('#f0f0f0', 'cloth'), 'glow': ('#9ff0ff', 'glow')})
    root = m.bone('root', [0, 0, 0])
    lit = lambda f=1.12: {g: [('fn', _soft_metal(1.2, 0.8))] for g in ('north', 'south', 'east', 'west')}
    # wheels
    for name, (x, z) in (('wheel_r', (6.6, -4.0)), ('wheel_l', (-6.6, -4.0)), ('wheel_b', (6.6, 4.2)), ('wheel_b2', (-6.6, 4.2))):
        wb = m.bone(name, [x, 4.2, z], root)
        R, r = 4.2, 1.3
        for (h, d) in ((2 * R, 2 * R - 2 * r), (2 * R - 2 * r, 2 * R)):
            cb(wb, x, 4.2 - h / 2, z, 3.0, h, d, 'wood', decals={g: [('fn', _soft_wood)] for g in ('east', 'west', 'north', 'south', 'up', 'down')})                                               # octagon wheel
        sx = 1 if x > 0 else -1
        for (h, d) in ((4.6, 2.6), (2.6, 4.6)):
            cb(wb, x + sx * 1.3, 4.2 - h / 2, z, 0.8, h, d, 'wood_d')                                   # inner rim
        for (h, d) in ((2.4, 1.6), (1.6, 2.4)):
            cb(wb, x + sx * 1.9, 4.2 - h / 2, z, 0.8, h, d, 'cap', decals={g: [('fn', _soft_metal(1.3, 0.8))] for g in ('east', 'west')})                                     # round hubcap
    body = m.bone('body', [0, 4.2, 0], root)
    c = 2.0
    cb(body, 0, 2.6, 0.6, 9.4, 6.2, 13.0 - 2 * c, 'body', decals=lit(), dens=3); cb(body, 0, 2.6, 0.6, 9.4 - 2 * c, 6.2, 13.0, 'body', decals=lit(), dens=3)   # chamfered chassis
    cb(body, 0, 8.8, 0.6, 8.0, 0.8, 11.0, 'body_l')                                               # bevelled top
    cb(body, 0, 3.0, -6.2, 7.6, 5.0, 1.6, 'body', decals=lit(), dens=3)                                    # front plate
    cb(body, 0, 3.6, -7.2, 5.6, 3.8, 0.8, 'body_l', decals=lit(), dens=3)
    mz = m.bone('muzzle', [0, 6.7, -9.6], body)
    for s in (1, -1):
        for (w, d, z) in ((3.0, 1.0, -7.4), (2.2, 1.2, -8.5), (1.4, 1.2, -9.7), (0.6, 1.0, -10.8)):
            cb(mz, s * 3.3, 5.0 - w / 2, z, w, w, d, 'body_d', decals={'north': [('shade', 0, 0, 0.5, 0.5, 1.2)]})   # corner spikes
    # silver donuts + ball
    co = m.bone('coil', [0, 11.6, 0], body)
    cb(co, 0, 9.4, 0, 6.0, 1.0, 6.0, 'cap')                                                          # dark plate in the hole
    def donut(yc, Rm, a):
        L = 2 * Rm * _m.tan(_m.pi / 8) + a * 0.35
        for k in range(8):
            ang = k * 45
            x, z = Rm * _m.cos(_m.radians(ang)), Rm * _m.sin(_m.radians(ang))
            rk = dict(rot=('y', 45), rot_origin=[x, yc, z]) if k % 2 else {}
            along_x = (k % 4 in (2, 6)) or (k % 4 == 2)
            for (t, h, mat) in ((a, a * 0.62, 'silver'), (a * 0.62, a, 'silver_d')):
                if k % 4 == 0:   w, d = t, L                                                          # segment on the x axis runs along z
                elif k % 4 == 2: w, d = L, t
                else:            w, d = (L, t) if k in (1, 5) else (t, L)
                cb(co, x, yc - h / 2, z, w, h, d, mat, decals={**{g: [('fn', _soft_metal(1.25, 0.75))] for g in ('north', 'south', 'east', 'west')}, 'up': [('fn', _soft_metal(1.1, 1.0))]}, dens=3, **rk)
    donut(10.8, 5.6, 3.2)
    donut(13.6, 3.6, 2.4)
    cb(co, 0, 13.0, 0, 1.8, 3.4, 1.8, 'cap')                                                         # neck
    for (w, h, d) in ((5.4, 3.4, 5.4), (3.4, 5.4, 3.4), (4.6, 4.6, 4.6)):
        cb(co, 0, 18.6 - h / 2, 0, w, h, d, 'silver', decals={g: [('fn', _soft_metal(1.15, 0.85))] for g in ('north', 'south', 'east', 'west', 'up')}, dens=3)   # ball
    sp = m.bone('spark', [0, 18.3, 0], co)
    for (x, y, z, w, h, d) in ((3.8, 18.6, 0.4, 0.5, 2.2, 0.5), (-3.6, 17.4, -1.0, 0.5, 2.0, 0.5), (0.8, 21.8, -0.4, 2.0, 0.5, 0.5),
                               (-1.0, 20.8, 3.2, 0.5, 0.5, 2.0), (1.6, 17.0, -3.8, 0.5, 1.8, 0.5)):
        cb(sp, x, y, z, w, h, d, 'glow')
    tp = m.bone('tc_panel', [0, 7.5, 0], body)
    cb(body, -3.6, 9.2, 5.6, 0.7, 12.6, 0.7, 'pole')
    cb(body, -3.6, 21.8, 5.6, 1.1, 0.8, 1.1, 'silver')
    for (y, L) in ((20.2, 5.6), (19.2, 4.2), (18.2, 2.8), (17.2, 1.4)):
        cb(tp, -3.9 - L / 2, y, 5.6, L, 1.0, 0.5, 'tc')                                             # team pennant
    m.hitbox(1.2, 1.4)
    return m


def wizard():
    """Wizard: soft-team hooded open robe with white trim over a brown tunic, brown belt + gold buckle, short trimmed
    sleeves, brown wrist bands, navy trousers, brown boots, angry brows + brown goatee, fireballs in both hands."""
    m = new_model('clash_wizard')
    m.mats_({'skin': ('#eab48e', 'skin'), 'skin_d': ('#cf9672', 'skin'), 'tunic': ('#6a3e24', 'cloth'), 'tunic_d': ('#53301a', 'cloth'),
             'robe': ('#f2f2f2', 'cloth'), 'robe_d': ('#d0d0d0', 'cloth'), 'trim': ('#f4f4f0', 'cloth'), 'belt': ('#6a4026', 'leather'),
             'gold': ('#e8be3a', 'metal'), 'pants': ('#9a9ab4', 'cloth'), 'boot': ('#5a3c28', 'leather'), 'boot_l': ('#6e4a32', 'leather'),
             'beard': ('#6a3a1e', 'hair'), 'band': ('#7a4a2a', 'leather'), 'fire': ('#ffb030', 'glow'), 'fire_o': ('#ff6a1a', 'glow'), 'fire_y': ('#fff0a0', 'glow')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        tp = m.bone('tc_pants_' + side, [x, 12, 0], lg)
        cb(tp, x, 3.6, 0, 3.8, 8.4, 3.8, 'pants', decals={f: [('lerp', '#6a6a80', 0.7, 1.0, 'y')] for f in ('north', 'south', 'east', 'west')})   # team trousers (dark)
        cb(lg, x, 0, -0.3, 4.0, 4.0, 4.4, 'boot', decals={'north': [('lerp', '#3e2818', 0.0, 0.3, 'y')]})
        cb(lg, x, 3.4, 0, 4.4, 1.2, 4.4, 'boot_l')                                                      # boot cuff
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 12, 0, 7.6, 12, 4.2, 'tunic', decals={'north': [('lerp', '#53301a', 0.0, 0.25, 'y')]})            # brown tunic
    cb(body, 0, 6.0, -0.4, 3.2, 6.0, 0.4, 'tunic_d')                                                    # tunic tail between the robe flaps
    cl = m.bone('tc_cloak', [0, 24, 0], body)
    rb = m.bone('ts_robe', [0, 24, 0], cl)
    cb(rb, 0, 5.4, 2.3, 8.6, 18.6, 0.8, 'robe', decals={'south': [('lerp', '#c0c0c0', 0.0, 0.2, 'y')]})        # robe back, long
    for sx in (1, -1):
        cb(rb, sx * 4.3, 5.4, 0, 0.8, 18.6, 4.4, 'robe')                                                   # robe sides
        cb(rb, sx * 3.0, 5.4, -2.3, 2.6, 18.6, 0.8, 'robe', decals={'north': [('lerp', '#c8c8c8', 0.0, 0.15, 'y')]})   # open front panels
    for sx in (1, -1):
        cb(body, sx * 1.75, 5.4, -2.75, 0.5, 18.6, 0.2, 'trim')                                            # white trim on the opening
        cb(body, sx * 3.0, 5.2, -2.3, 2.8, 0.4, 0.9, 'trim')                                               # hem trim
        cb(body, sx * 4.3, 5.2, 0, 0.9, 0.4, 4.6, 'trim')
    cb(body, 0, 5.2, 2.3, 8.8, 0.4, 0.9, 'trim')
    cb(body, 0, 15.0, 0, 9.0, 1.6, 5.0, 'belt')                                                          # belt over the robe
    cb(body, -1.4, 14.8, -2.6, 2.4, 2.0, 0.4, 'gold', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#6a4026')]})   # buckle
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "kk....kk", ".kkk.kk.", ".wb..bw.", "...nn...", "........", "........"],
               {'k': '#4a2a16', 'w': '#ffffff', 'b': '#3a2414', 'n': '#cf9672'})
    cb(hd, 0, 24, 0, 8, 8, 8, S, decals={'north': face})
    cb(hd, 0, 23.0, -4.2, 3.0, 2.2, 1.4, 'beard', decals={'north': [('shade', 0, 0, 1, 0.3, 1.1)]})          # goatee
    cb(hd, 0, 25.4, -4.15, 5.0, 0.8, 0.4, 'beard')                                                       # moustache
    hc = m.bone('tc_hood', [0, 24, 0], hd)
    ho = m.bone('ts_hood', [0, 24, 0], hc)
    cb(ho, 0, 31.8, 0.4, 9.6, 1.0, 9.4, 'robe')                                                          # hood top
    cb(ho, 0, 32.6, 2.2, 5.0, 0.6, 5.0, 'robe')                                                          # hood peak
    for sx in (1, -1):
        cb(ho, sx * 4.6, 23.0, 0.6, 0.8, 9.0, 8.8, 'robe')                                                 # hood sides
    cb(ho, 0, 23.0, 4.6, 9.6, 9.0, 0.8, 'robe_d')                                                        # hood back
    cb(ho, 0, 19.0, 3.4, 9.0, 4.2, 1.6, 'robe')                                                          # draped neck
    cb(hd, 0, 31.4, -4.7, 9.8, 0.6, 0.5, 'trim')                                                         # hood rim trim
    for sx in (1, -1):
        cb(hd, sx * 4.75, 23.0, -4.25, 0.5, 9.0, 0.5, 'trim')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6
        a = m.bone('arm_' + side, [x, 22, 0], body)
        sl = m.bone('tc_sleeve_' + side, [x, 22, 0], a)
        ts = m.bone('ts_sleeve_' + side, [x, 22, 0], sl)
        cb(ts, x, 17.4, 0, 4.2, 6.0, 4.2, 'robe')                                                        # short wide sleeve
        cb(a, x, 17.2, 0, 4.4, 0.5, 4.4, 'trim')
        cb(a, x, 10.4, 0, 3.2, 7.0, 3.2, S)                                                              # bare forearm
        cb(a, x, 11.6, 0, 3.6, 1.6, 3.6, 'band')                                                         # wrist band
        f = m.bone('flame_' + side, [x, 10.5, 0], a)
        for (w, h, y, mat) in ((3.4, 2.4, 7.4, 'fire_o'), (2.8, 2.6, 6.0, 'fire'), (1.8, 2.0, 4.4, 'fire_y'), (0.8, 1.4, 3.0, 'fire'))[:0]:
            pass
        for (dx, w, h, y, d, mat) in ((0, 4.0, 3.6, 9.0, 4.0, 'fire_o'), (0, 3.0, 3.0, 9.4, 4.4, 'fire'), (0, 1.8, 1.8, 10.0, 4.8, 'fire_y'),
                                      (-0.6, 1.8, 2.4, 12.6, 1.8, 'fire'), (1.0, 1.2, 1.8, 12.2, 1.2, 'fire_o'), (-0.4, 0.8, 1.2, 15.0, 0.8, 'fire_y')):
            cb(f, x + dx, y, -3.8, w, h, d, mat)                                                         # round fireball with licking flames
    m.hitbox(0.8, 2.2)
    return m


def x_bow():
    """X-Bow: square stone base with team corner blocks, cog-toothed turntable and column, yoke mount, long steel stock
    with groove, curved wooden limbs with team rope wraps, taut string, cranks, heavy bolt with team fletching."""
    m = new_model('clash_x_bow')
    m.mats_({'stone': ('#9a968e', 'soft'), 'stone_l': ('#b0aca4', 'soft'), 'stone_d': ('#7c7870', 'soft'), 'steel': ('#9aa2aa', 'metal'),
             'steel_d': ('#6e757d', 'metal'), 'steel_l': ('#c2c8ce', 'metal'), 'groove': ('#3a3e44', 'plain'), 'wood': ('#9a6234', 'soft'),
             'wood_d': ('#744622', 'soft'), 'string': ('#e8d8a8', 'rope'), 'tc': ('#efefef', 'cloth'), 'tcr': ('#e4e4e4', 'rope'),
             'shaft': ('#6a4426', 'wood')})
    St = lambda *e: {f: [('fn', _stone)] + list(e) for f in ('north', 'south', 'east', 'west', 'up')}
    root = m.bone('root', [0, 0, 0])
    base = m.bone('base', [0, 0, 0], root)
    def cham(b, y, h, w, d, c, mat, x=0.0, z=0.0, **kw):
        cb(b, x, y, z, w, h, d - 2 * c, mat, **kw); cb(b, x, y, z, w - 2 * c, h, d, mat, **kw); cb(b, x, y, z, w - c, h, d - c, mat, **kw)
    cham(base, 0, 3.0, 34, 34, 1.6, 'stone_d', decals=St(('shade', 0, 0, 1, 0.2, 1.12)))         # slab
    cham(base, 3.0, 1.0, 31, 31, 1.4, 'stone', decals=St(('shade', 0, 0, 1, 0.4, 1.12)))
    tcp = m.bone('base_tc_plate', [0, 6, 0], base)
    for sx in (1, -1):
        for sz in (1, -1):
            cham(tcp, 3.0, 3.2, 6.4, 6.4, 1.8, 'tc', x=sx * 14.2, z=sz * 14.2, decals={f: [('shade', 0, 0, 1, 0.25, 1.12)] for f in ('north', 'south', 'east', 'west')})   # team corner blocks
    cham(base, 4.0, 3.0, 22, 22, 6.0, 'stone', decals=St(('shade', 0, 0, 1, 0.3, 1.12)))         # round turntable
    import math as _m
    for k in range(8):                                                                       # cog teeth
        a = k * _m.pi / 4
        x, z = _m.cos(a) * 11.6, _m.sin(a) * 11.6
        cb(base, x, 4.0, z, 3.2, 2.6, 3.2, 'stone_l', decals=St(), rot=('y', 45 if k % 2 else 0), rot_origin=[x, 5, z])
    cham(base, 7.0, 3.0, 12, 12, 3.2, 'stone_l', decals=St())                                   # column foot
    cham(base, 10.0, 4.6, 10.0, 10.0, 2.8, 'stone', decals=St(('lerp', '#7c7870', 0.7, 1.0, 'y')))  # column
    top = m.bone('top', [0, 24, 0], root)
    cb(top, 0, 24.0, 0, 9.4, 3.0, 9.4, 'steel_d', decals={f: [('shade', 0, 0, 1, 0.3, 1.15)] for f in ('north', 'south', 'east', 'west')})   # swivel plate
    for sx in (1, -1):
        cb(top, sx * 3.6, 27.0, 0, 2.2, 5.6, 6.0, 'steel', decals={'east': [('shade', 0, 0, 1, 0.2, 1.15)], 'west': [('shade', 0, 0, 1, 0.2, 1.15)]})   # yoke cheeks
        cb(top, sx * 4.9, 30.0, 0, 1.0, 2.6, 2.6, 'steel_l')                                     # axle pins
    bw = m.bone('top_bow', [0, 32, 0], top)
    cb(bw, 0, 31.0, -1.0, 6.4, 3.6, 30.0, 'steel', decals={'up': [('rect', 0.38, 0, 0.62, 1, '#3a3e44')], 'east': [('shade', 0, 0, 1, 0.25, 1.15)], 'west': [('shade', 0, 0, 1, 0.25, 1.15)]})   # stock with groove
    for sx in (1, -1):
        cb(bw, sx * 3.5, 33.2, -1.0, 0.8, 1.4, 28.0, 'steel_l')                                  # side rails
    cb(bw, 0, 30.4, -15.4, 5.0, 4.0, 2.4, 'steel_d')                                          # front cap
    cb(bw, 0, 30.6, 13.0, 7.0, 4.0, 2.6, 'steel_d')                                           # rear block
    for sx, side in ((1, 'r'), (-1, 'l')):
        ck = m.bone('top_crank_' + side, [sx * 3.6, 32, 11], bw)
        cb(ck, sx * 4.4, 30.6, 11, 1.0, 3.2, 3.2, 'steel_l'); cb(ck, sx * 4.4, 31.6, 11, 1.2, 1.2, 1.2, 'steel_d')   # crank hub
        cb(ck, sx * 5.2, 30.2, 11, 0.8, 4.6, 0.8, 'steel_d'); cb(ck, sx * 5.8, 29.4, 11, 1.4, 1.0, 1.0, 'wood_d')    # crank arm + handle
        lb = m.bone('top_limb_' + side, [sx * 4, 34.5, -13], bw)
        segs = ((5.6, -13.4, 4.0, 0), (9.6, -12.6, 4.4, 22.5), (13.2, -10.6, 4.4, 45), (15.8, -7.8, 4.0, 45), (17.4, -5.2, 2.6, 45))
        for i, (x, z, L, ang) in enumerate(segs):
            th = 4.4 - i * 0.4
            cb(lb, sx * x, 34.5 - th / 2, z, L, th, 3.6 - i * 0.3, 'wood', rot=('y', -sx * ang) if ang else None, rot_origin=[sx * x, 34.5, z],
               decals={'up': [('shade', 0, 0, 1, 0.3, 1.15)], 'north': [('shade', 0, 0.75, 1, 1, 0.85)]}) if ang else \
                cb(lb, sx * x, 34.5 - th / 2, z, L, th, 3.6, 'wood', decals={'up': [('shade', 0, 0, 1, 0.3, 1.15)]})   # curved wooden limb
        cb(lb, sx * 18.2, 33.6, -4.2, 1.8, 2.2, 1.8, 'wood_d')                                    # limb tip
        tw = m.bone('top_tc_wrap_' + side, [sx * 13.238795325112868, 34.5, -9.173165676349102], lb)
        for dz in (-0.8, 0.0, 0.8):
            cb(tw, sx * 13.2 + dz * sx * 0.7, 32.0, -10.6 + dz * 0.7 + 1.4, 1.0, 5.0, 4.4, 'tcr', rot=('y', -sx * 45), rot_origin=[sx * 13.2, 34.5, -9.2])   # team rope wrap
        sg = m.bone('top_string_' + side, [sx * 18.1885427934187, 34.8, -4.22341820804327], lb)
        L = 19.6
        cb(sg, sx * (18.19 - L / 2), 34.6, -4.22, L, 0.5, 0.5, 'string', rot=('y', sx * 22.5), rot_origin=[sx * 18.19, 34.8, -4.22])   # taut string
    bt = m.bone('top_bolt', [0, 35, -14], bw)
    cb(bt, 0, 34.6, -5.6, 1.0, 1.0, 17.0, 'shaft')                                             # bolt shaft
    for (w, d, z) in ((3.4, 1.0, -14.6), (2.4, 1.2, -15.7), (1.4, 1.2, -16.9), (0.6, 1.0, -18.0)):
        cb(bt, 0, 35.1 - w / 2, z, w * 0.5, w, d, 'steel_l')                                    # flat arrowhead
        cb(bt, 0, 35.1 - w * 0.25, z, w, w * 0.5, d, 'steel_l')
    tf = m.bone('top_tc_fletch', [0, 35, 0.10341611560762765], bt)
    cb(tf, 0, 35.0, 1.2, 0.3, 1.8, 3.6, 'tc'); cb(tf, 0, 33.4, 1.2, 0.3, 1.6, 3.6, 'tc')          # team fletching
    cb(tf, 1.0, 34.4, 1.2, 1.6, 0.3, 3.6, 'tc'); cb(tf, -1.0, 34.4, 1.2, 1.6, 0.3, 3.6, 'tc')
    def under_top(bn):
        while bn is not None:
            if bn.name == 'top': return True
            bn = bn.parent
        return False
    for bn in m.bones:                                                                       # squat: drop the whole bow 9.4 px
        if under_top(bn):
            bn.origin[1] -= 9.4
            for c in bn.cubes:
                c['frm'][1] -= 9.4; c['to'][1] -= 9.4; c['rot_origin'][1] -= 9.4
    m.hitbox(2.2, 2.0)
    return m


def _stone(img, rng):
    """worn grey stone: mottling, a few hairline cracks, lit top edge"""
    import numpy as _np, random as _r
    h, w, _ = img.shape
    R = _r.Random(h * 53 + w * 7)
    for _ in range(w * h // 5):
        x, y = R.randrange(w), R.randrange(h)
        img[y, x] *= R.choice((0.92, 0.96, 1.04, 1.08))
    for _ in range(max(1, (w * h) // 160)):                                      # cracks
        x, y = R.randrange(w), R.randrange(h)
        for _ in range(R.randint(2, 5)):
            if 0 <= x < w and 0 <= y < h: img[y, x] *= 0.7
            x += R.choice((-1, 0, 1)); y += 1
    img[0, :] *= 1.15; img[-1, :] *= 0.82
    img[:] = _np.clip(img, 0, 255)


def tombstone():
    """Tombstone (HQ): chamfered two-tier stone base on a ring of rounded pebbles, open grave box with dark pit, plank lids
    flung open, iron ring handles with pyramid bolts, arched headstone with raised rim, recessed panel, 3D skull and
    crossbones, corner studs; small team ribbon on the headstone."""
    import random as _r
    m = new_model('clash_tombstone')
    m.mats_({'stone': ('#686d75', 'soft'), 'stone_l': ('#868b93', 'soft'), 'stone_d': ('#50545b', 'soft'), 'panel': ('#9298a0', 'soft'),
             'pit': ('#1e2024', 'plain'), 'peb': ('#b0a498', 'soft'), 'peb_l': ('#c8beb2', 'soft'),
             'bone': ('#efe7d3', 'soft'), 'bone_d': ('#cfc4ac', 'soft'), 'hole': ('#2e2a26', 'plain'),
             'iron': ('#8f969e', 'metal'), 'iron_l': ('#bfc5cb', 'metal'), 'wood': ('#a0653a', 'soft'), 'wood_d': ('#6e4220', 'soft'),
             'nail': ('#5a5e64', 'metal'), 'tc': ('#f0f0f0', 'cloth')})
    St = lambda *extra: {f: [('fn', _stone)] + list(extra) for f in ('north', 'south', 'east', 'west', 'up')}
    root = m.bone('root', [0, 0, 0])
    top = m.bone('top', [0, 0, 0], root)
    def cham(y, h, w, d, c, mat, z=0.0, **kw):                                              # box with chamfered vertical corners
        cb(top, 0, y, z, w, h, d - 2 * c, mat, **kw); cb(top, 0, y, z, w - 2 * c, h, d, mat, **kw)
        cb(top, 0, y, z, w - c, h, d - c, mat, **kw)
    # ---- pebbles
    R = _r.Random(11)
    n = 30
    for i in range(n):
        t = (i + R.uniform(-0.2, 0.2)) / n
        per = 2 * (31 + 33)
        p = t * per
        if p < 31: x, z = -15.5 + p, -17.2
        elif p < 64: x, z = 15.8, -16.5 + (p - 31)
        elif p < 95: x, z = 15.5 - (p - 64), 17.2
        else: x, z = -15.8, 16.5 - (p - 95)
        w, d, h = R.uniform(2.6, 4.4), R.uniform(2.4, 3.8), R.uniform(1.3, 2.4)
        cb(top, x, 0, z, w, h, d, 'peb', decals={'up': [('shade', 0, 0, 1, 1, 1.06)], 'north': [('lerp', '#8a7e72', 0.6, 1.0, 'y')]})
        cb(top, x, h, z, w * 0.62, 0.5, d * 0.62, 'peb_l')                                    # rounded top
    # ---- base
    cham(0, 2.2, 31, 33, 2.6, 'stone_d', decals=St(('shade', 0, 0, 1, 0.2, 1.15)))
    cham(2.2, 1.2, 28.4, 30.4, 2.2, 'stone', decals=St(('shade', 0, 0, 1, 0.3, 1.15)))
    # ---- grave box
    Z0, Z1 = -13.0, 6.6
    zc, dz = (Z0 + Z1) / 2, Z1 - Z0
    cb(top, 0, 3.4, zc, 16.0, 0.9, dz - 4, 'pit')                                            # dark pit floor
    inner = ('shade', 0, 0, 1, 1, 0.55)
    for sx in (1, -1):
        cb(top, sx * 9.6, 3.4, zc, 4.0, 3.2, dz, 'stone', decals=St())                        # wall foot (wider)
        cb(top, sx * 9.4, 6.6, zc, 3.4, 2.4, dz - 0.6, 'stone', decals={**St(), ('west' if sx > 0 else 'east'): [('fn', _stone), inner]})
        cb(top, sx * 9.4, 9.0, zc, 3.0, 0.7, dz - 1.2, 'stone_l', decals=St(('shade', 0, 0, 1, 1, 1.1)))   # bevelled cap
    cb(top, 0, 3.4, Z0 + 2.0, 15.2, 3.2, 4.0, 'stone', decals=St())
    cb(top, 0, 6.6, Z0 + 2.0, 15.6, 2.4, 3.4, 'stone', decals={**St(), 'south': [('fn', _stone), inner]})
    cb(top, 0, 9.0, Z0 + 2.0, 21.6, 0.7, 3.0, 'stone_l', decals=St(('shade', 0, 0, 1, 1, 1.1)))
    # ---- iron ring handles
    for sx in (1, -1):
        X = sx * 11.7
        for zz in (-9.6, 2.2):
            for (w, h, dy) in ((1.0, 1.0, 1.6), (1.4, 2.6, 0.8), (1.0, 1.0, 0.0)):
                cb(top, X + sx * 0.5, 6.0 + dy, zz, w + 0.4, h if dy == 0.8 else 1.0, w + 1.2 if dy == 0.8 else w, 'iron_l')   # octahedral bolt
            cb(top, X + sx * 0.4, 4.4, zz, 0.8, 1.8, 0.8, 'iron')                                  # ring side
        cb(top, X + sx * 0.4, 3.8, -3.7, 0.8, 0.8, 10.6, 'iron')                                   # ring bottom
    # ---- plank lids
    wood = [('fn', _staves(True, base=(160, 101, 58), seam=(92, 56, 28)))]
    for sx, ang in ((1, 22.5), (-1, 45)):
        rk = dict(rot=('z', -sx * ang), rot_origin=[sx * 11.0, 9.7, 0])
        for k, zz in enumerate((-10.0, -5.8, -1.6)):
            cb(top, sx * 11.6, 9.7, zz, 1.2, 9.6 - (k % 2) * 0.8, 4.0, 'wood', decals={f: wood for f in ('east', 'west', 'north', 'south')}, **rk)   # planks
        for y in (11.6, 16.2):
            cb(top, sx * (11.6 + 1.0), y, -5.8, 0.9, 1.4, 12.6, 'wood_d', **rk)                  # battens
            for zz in (-10.0, -5.8, -1.6):
                cb(top, sx * (11.6 + 1.5), y + 0.4, zz, 0.2, 0.6, 0.6, 'nail', **rk)
    # ---- headstone
    HZ, FZ = 10.2, 7.6                                                                       # centre / front face z
    cb(top, 0, 3.4, HZ, 22, 2.8, 6.4, 'stone', decals=St(('shade', 0, 0, 1, 0.25, 1.15)))      # plinth
    cb(top, 0, 6.2, HZ, 18, 14.6, 5.2, 'stone', decals=St())
    cb(top, 0, 20.8, HZ, 15.4, 2.0, 5.2, 'stone', decals=St())                                # arched top steps
    cb(top, 0, 22.8, HZ, 11.6, 1.4, 5.2, 'stone', decals=St())
    cb(top, 0, 24.2, HZ, 6.8, 0.8, 5.2, 'stone', decals=St(('shade', 0, 0, 1, 1, 1.1)))
    cb(top, 0, 7.6, FZ - 0.05, 13.6, 12.8, 0.3, 'panel', decals={'north': [('fn', _stone), ('lerp', '#a8aeb6', 0.0, 0.35, 'y')]})   # recessed light panel
    for (x, y, w, h) in ((0, 20.4, 15.6, 1.2), (0, 6.6, 15.6, 1.0), (7.4, 7.6, 1.0, 12.8), (-7.4, 7.6, 1.0, 12.8)):
        cb(top, x, y, FZ - 0.5, w, h, 1.0, 'stone_l', decals={'north': [('fn', _stone), ('shade', 0, 0, 1, 0.3, 1.12)]})   # raised rim
    for sx in (1, -1):
        for (w, d) in ((1.8, 0.5), (1.1, 0.5), (0.5, 0.4)):
            pass
        cb(top, sx * 5.2, 17.9, FZ - 0.5, 1.8, 1.8, 0.6, 'iron_l'); cb(top, sx * 5.2, 18.3, FZ - 1.0, 1.0, 1.0, 0.5, 'iron_l')   # pyramid studs
    # crossbones (behind the skull)
    for s in (1, -1):
        rk = dict(rot=('z', s * 22.5), rot_origin=[0, 12.6, FZ - 1.0])
        cb(top, 0, 11.9, FZ - 1.0, 12.0, 1.4, 1.1, 'bone', decals={'up': [('shade', 0, 0, 1, 1, 1.08)]}, **rk)
        for ex in (6.2, -6.2):
            cb(top, ex, 11.2, FZ - 1.0, 1.6, 1.3, 1.3, 'bone_d', **rk); cb(top, ex, 12.9, FZ - 1.0, 1.6, 1.3, 1.3, 'bone_d', **rk)   # knobbly ends
    # 3D skull
    SZ = FZ - 2.0
    cb(top, 0, 14.2, SZ, 7.6, 5.2, 2.6, 'bone', decals={'up': [('shade', 0, 0, 1, 1, 1.06)], 'north': [('shade', 0, 0.75, 1, 1, 0.92)]})   # cranium
    cb(top, 0, 15.0, SZ + 0.2, 8.6, 3.6, 2.2, 'bone')                                        # rounded sides
    cb(top, 0, 19.4, SZ + 0.1, 6.0, 0.9, 2.2, 'bone')                                         # rounded crown
    cb(top, 0, 13.2, SZ - 0.1, 6.0, 1.2, 2.2, 'bone_d')                                       # cheekbones
    cb(top, 0, 11.6, SZ + 0.2, 4.6, 1.8, 1.8, 'bone', decals={'north': pix(["k.k.k.k.k", ".........", "........."], {'k': '#5a5248'})})   # jaw + teeth
    for sx in (1, -1):
        cb(top, sx * 1.9, 15.4, SZ - 1.32, 2.4, 2.4, 0.1, 'hole')                               # deep eye sockets
        cb(top, sx * 1.9, 17.6, SZ - 1.32, 1.6, 0.4, 0.1, 'bone_d')                              # brow shadow
    cb(top, 0, 13.9, SZ - 1.32, 1.0, 1.0, 0.1, 'hole')                                         # nose
    # team ribbon
    rb = m.bone('tc_ribbon', [0, 10, -6], top)
    cb(rb, -6.6, 21.2, FZ - 0.6, 3.6, 1.0, 0.4, 'tc', rot=('z', 22.5), rot_origin=[-6.6, 21.7, FZ - 0.6])
    cb(rb, -8.0, 18.4, FZ - 0.6, 1.0, 2.8, 0.4, 'tc'); cb(rb, -6.8, 18.8, FZ - 0.6, 1.0, 2.2, 0.4, 'tc')
    m.hitbox(2.2, 1.6)
    m.anim('idle', 3.0, 'loop', {'top': {'scale': loop([[1, 1, 1], [1.01, 1.02, 1.01]], 3.0)}})
    m.anim('attack', 0.5, 'once', {'top': {'scale': [(0, [1, 1, 1]), (0.12, [1.06, 0.94, 1.06]), (0.3, [0.98, 1.04, 0.98]), (0.5, [1, 1, 1])]}})
    m.anim('deploy', 0.8, 'once', {'root': {'position': [(0, [0, -14, 0]), (0.6, [0, 1, 0]), (0.8, [0, 0, 0])], 'scale': [(0, [0.7, 0.7, 0.7]), (0.8, [1, 1, 1])]}})
    m.anim('death', 1.0, 'once', {'root': {'position': [(0, [0, 0, 0]), (1.0, [0, -14, 0])], 'rotation': [(0, [0, 0, 0]), (1.0, [0, 0, 10])]}})
    m.anim('hit', 0.3, 'once', {'root': {'rotation': [(0, [0, 0, 0]), (0.06, [0, 0, 3]), (0.14, [0, 0, -2]), (0.3, [0, 0, 0])]}})
    return m


def sparky():
    """Sparky: wooden cart with a spiked steel plow, chunky wooden wheels, dark steel frames holding a ribbed team-colour coil,
    top handle bar, three gold rings round the barrel and an iron nub muzzle; electric sparks crackle around the rings."""
    m = new_model('clash_sparky')
    m.mats_({'wood': ('#a8723e', 'wood'), 'wood_d': ('#7e5228', 'wood'), 'iron': ('#4a4e56', 'metal'), 'iron_l': ('#7a8088', 'metal'),
             'steel': ('#9aa2aa', 'metal'), 'stud': ('#c4cad0', 'metal'), 'gold': ('#e2b23a', 'metal'), 'gold_d': ('#b8862a', 'metal'),
             'tc': ('#f0f0f0', 'cloth'), 'tc_d': ('#b4b4b4', 'cloth'), 'glow': ('#9ff0ff', 'glow'), 'core': ('#ffffff', 'glow')})
    root = m.bone('root', [0, 0, 0])
    def disc_x(b, x, y, z, R, t, mat, **kw):                                             # octagon disc facing x
        r = R * 0.3
        for (h, d) in ((2 * R, 2 * R - 2 * r), (2 * R - 2 * r, 2 * R), (2 * R - r, 2 * R - r)):
            cb(b, x, y - h / 2, z, t, h, d, mat, **kw)
    def plate_z(b, z, w, h, t, y, mat, r=1.6, **kw):                                     # octagonal plate facing z
        cb(b, 0, y - h / 2 + r, z, w, h - 2 * r, t, mat, **kw); cb(b, 0, y - h / 2, z, w - 2 * r, h, t, mat, **kw)
    for side, (x, z) in (('fr', (10.5, -6.5)), ('fl', (-10.5, -6.5)), ('br', (10.5, 7)), ('bl', (-10.5, 7))):
        wb = m.bone('wheel_' + side, [x, 5.5, z], root)
        disc_x(wb, x, 5.5, z, 4.6, 2.4, 'wood', decals={f: [('ering', 0.5, 0.5, 0.42, 0.42, 0.12, '#7e5228')] for f in ('east', 'west')})   # wooden wheel
        cb(wb, x + (1 if x > 0 else -1) * 1.4, 4.4, z, 1.2, 2.2, 2.2, 'iron')                             # iron hub
    cart = m.bone('cart', [0, 6, 0], root)
    cb(cart, 0, 4.6, 0.5, 14.0, 4.4, 20.0, 'wood_d', decals={f: [('fn', _staves(False, base=(126, 82, 40), seam=(84, 52, 24)))] for f in ('east', 'west', 'up')})   # cart bed
    for sx in (1, -1):
        cb(cart, sx * 7.6, 8.0, 1.0, 1.8, 5.2, 18.0, 'wood', decals={'east' if sx > 0 else 'west': [('fn', _staves(False, base=(168, 114, 62), seam=(110, 70, 34))),
                                                                                                    ('rect', 0.05, 0.15, 0.1, 0.3, '#4a4e56'), ('rect', 0.9, 0.15, 0.95, 0.3, '#4a4e56')]})   # side beams
        cb(cart, sx * 7.6, 10.0, 9.6, 1.8, 9.0, 2.0, 'iron')                                              # rear posts
    def scuff(img, rng):                                                                    # worn steel: mottling + bright edge wear
        import numpy as _np, random as _r
        h, w, _ = img.shape
        R = _r.Random(h * 31 + w)
        for _ in range(w * h // 6):
            x, y = R.randrange(w), R.randrange(h)
            img[y, x] *= R.choice((0.9, 0.94, 1.06, 1.1))
        img[0, :] *= 1.25; img[:, 0] *= 1.12; img[:, -1] *= 1.12; img[-1, :] *= 0.8
        img[:] = _np.clip(img, 0, 255)
    W = {f: [('fn', scuff)] for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    TZ = -16.0                                                                               # V-shaped steel prow, tip at the front
    for sx in (1, -1):
        rk = dict(rot=('y', sx * PROW_YAW), rot_origin=[0, 8, TZ])
        cb(cart, sx * 4.8, 2.8, TZ + 1.6, 9.6, 7.6, 3.2, 'iron_l', decals=W, **rk)                    # one face of the wedge
        cb(cart, sx * 4.4, 10.4, TZ + 1.8, 8.8, 1.0, 2.6, 'iron_l', decals=W, **rk)                    # bevelled top lip
        for x in (2.9, 6.6):
            for y in (4.9, 8.5):
                z = TZ
                for (w, d) in ((2.6, 0.7), (1.8, 0.7), (1.0, 0.6)):
                    cb(cart, sx * x, y - w / 2, z - d / 2, w, w, d, 'stud', decals={'north': [('shade', 0, 0, 0.5, 0.5, 1.15), ('shade', 0.5, 0.5, 1, 1, 0.82)]}, **rk)   # pyramid studs
                    z -= d
    cb(cart, 0, 2.8, TZ + 0.9, 1.6, 7.6, 1.8, 'iron', rot=('y', 45), rot_origin=[0, 8, TZ + 0.9])        # ridge at the tip
    br = m.bone('barrel', [0, 16, 6], cart)
    Y = 18.0
    for z in (-4.6, 9.0):
        plate_z(br, z, 15.6, 15.6, 2.4, Y, 'iron', decals={'north': [('shade', 0, 0, 1, 0.12, 1.2)], 'south': [('shade', 0, 0, 1, 0.12, 1.2)]})   # dark steel frames
        for (x, y) in ((-6, Y + 6), (6, Y + 6), (-6, Y - 6), (6, Y - 6)):
            cb(br, x, y - 0.6, z - 1.3, 1.2, 1.2, 0.3, 'iron_l')                                            # bolts
    cb(br, 0, Y + 7.8, 2.2, 3.0, 1.4, 14.0, 'steel', decals={'up': [('shade', 0, 0, 1, 1, 1.12)]})            # top handle bar
    for z in (-4.4, 8.8):
        cb(br, 0, Y + 7.6, z, 3.0, 1.6, 1.2, 'steel')
    co = m.bone('coil', [0, 17, -5], br)
    tco = m.bone('tc_coil', [0, 17, -5], co)
    z = -3.4
    for i in range(6):
        plate_z(tco, z + 0.6, 13.4 if i % 2 == 0 else 12.6, 13.4 if i % 2 == 0 else 12.6, 1.2, Y, 'tc' if i % 2 == 0 else 'tc_d', r=2.0)   # ribbed team coil
        z += 1.9
    plate_z(br, -8.2, 6.0, 6.0, 5.0, Y, 'iron', r=1.2)                                                     # barrel shaft
    for (zz, R) in ((-7.0, 6.2), (-10.6, 5.0), (-13.8, 3.9)):                                              # gold rings
        t = 1.4
        s = R * 0.82                                                                                     # octagonal ring
        cb(br, 0, Y + R - t, zz, s, t, t, 'gold', decals={'north': [('shade', 0, 0, 1, 0.4, 1.15)]})
        cb(br, 0, Y - R, zz, s, t, t, 'gold_d')
        cb(br, R - t / 2, Y - s / 2, zz, t, s, t, 'gold'); cb(br, -R + t / 2, Y - s / 2, zz, t, s, t, 'gold')
        for (dx, dy) in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            cx, cy = dx * (R - t / 2) * 0.72, Y + dy * (R - t / 2) * 0.72
            cb(br, cx, cy - t / 2, zz, s * 0.95, t, t, 'gold' if dy > 0 else 'gold_d', rot=('z', -45 * dx * dy), rot_origin=[cx, cy, zz])
    cb(br, 0, Y - 1.4, -13.0, 2.8, 2.8, 6.0, 'iron')                                                       # thin barrel inside the rings
    mz = m.bone('muzzle', [0, 17, -19.6], br)
    cb(mz, 0, Y - 1.8, -17.4, 3.6, 3.6, 2.6, 'iron_l', decals={'north': [('shade', 0, 0, 1, 0.3, 1.15)]})      # nub
    tw = m.bone('tower', [0, 21, 6.5], br)
    orb = m.bone('orb', [0, Y, -10], tw)
    cb(orb, 0, Y - 1.0, -10.4, 2.0, 2.0, 2.0, 'core')                                                       # glowing core in the rings
    sp = m.bone('spark', [0, Y, -10.5], orb)
    for (x, y, z, w, h) in ((5.2, Y + 2.0, -8.8, 0.5, 2.4), (5.8, Y + 0.6, -10.4, 0.5, 2.0), (-5.0, Y - 2.4, -9.0, 0.5, 2.6), (-4.2, Y + 3.4, -12.2, 2.2, 0.5),
                            (2.4, Y - 4.6, -12.0, 2.4, 0.5), (0.6, Y + 4.8, -9.2, 0.5, 1.8), (-2.8, Y - 3.8, -14.6, 1.8, 0.5)):
        cb(sp, x, y, z, w, h, 0.5, 'glow')                                                                   # crackling sparks
    m.hitbox(1.6, 1.6)
    return m


def skeleton_balloon():
    """Skeleton Barrel: dark wooden barrel with painted skull, spiked steel end hoops, ring on top, rope to three team balloons."""
    import math as _m
    m = new_model('clash_skeleton_balloon')
    m.mats_({'wood': ('#3c3a3c', 'soft'), 'endw': ('#7a4a32', 'wood'), 'steel': ('#aab2ba', 'metal'), 'steel_d': ('#80878f', 'metal'),
             'spike': ('#d0d6dc', 'metal'), 'rope': ('#c8a050', 'rope'), 'tc': ('#eef0f6', 'cloth'), 'tc_d': ('#c8ccd8', 'cloth'), 'shine': ('#ffffff', 'plain')})
    root = m.bone('root', [0, 0, 0])
    bk = m.bone('basket', [0, 4, 0], root)
    C = 8.0
    def octx(b, x0, x1, R, mat, r=None, **kw):                                          # octagonal prism along x
        r = R * 0.3 if r is None else r
        for (h, d) in ((2 * R, 2 * R - 2 * r), (2 * R - 2 * r, 2 * R), (2 * R - r, 2 * R - r)):
            cb(b, (x0 + x1) / 2, C - h / 2, 0, x1 - x0, h, d, mat, **kw)
    sk = lambda: [('fn', _staves(False, True, base=(60, 58, 60), seam=(30, 28, 30), upright=True))]
    pl = lambda: [('fn', _staves(False, base=(60, 58, 60), seam=(30, 28, 30)))]
    octx(bk, -4, 4, 8.0, 'wood', r=2.4, decals={'north': sk(), 'south': sk(), 'up': pl(), 'down': pl()})      # bulging belly
    for sx in (1, -1):
        for (x0, x1, R) in ((4, 6, 7.7), (6, 7.6, 7.2)):
            octx(bk, *sorted((sx * x0, sx * x1)), R, 'wood', r=R * 0.4, decals={'north': pl(), 'south': pl(), 'up': pl(), 'down': pl()})   # rounded taper
        octx(bk, *sorted((sx * 7.2, sx * 9.6)), 8.4, 'steel', r=3.2, decals={f: [('shade', 0, 0, 1, 0.25, 1.12), ('shade', 0, 0.75, 1, 1, 0.85)] for f in ('north', 'south', 'up', 'down')})   # thick hoop
        octx(bk, *sorted((sx * 9.6, sx * 10.0)), 6.8, 'endw', r=2.4, decals={f: [('fn', _staves(False, base=(122, 74, 50), seam=(80, 46, 30)))] for f in ('east', 'west')})   # recessed wooden end
        for (y, z, h, d) in ((C + 6.2, 0, 1.4, 9.0), (C - 7.6, 0, 1.4, 9.0), (C - 4.5, -6.9, 9.0, 1.4), (C - 4.5, 6.9, 9.0, 1.4)):
            cb(bk, sx * 10.1, y, z, 1.2, h, d, 'steel_d')                                                  # raised rim around the end
        for (yy, zz) in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            cb(bk, sx * 10.1, C + yy * 5.4 - 0.7, zz * 5.4, 1.2, 1.4, 1.4, 'steel_d')                     # rim corners
        for d in range(4):
            for rot in (0, 45):
                kw = dict(rot=('x', rot), rot_origin=[sx * 8.9, C, 0]) if rot else {}
                o = 8.0
                for (w, h) in ((2.6, 0.8), (2.0, 1.0), (1.3, 1.0), (0.6, 0.8)):                          # pyramid spikes all round
                    if d == 0:   cb(bk, sx * 8.9, C + o, 0, w, h, w, 'spike', **kw)
                    elif d == 1: cb(bk, sx * 8.9, C - o - h, 0, w, h, w, 'spike', **kw)
                    elif d == 2: cb(bk, sx * 8.9, C - w / 2, -o - h / 2, w, w, h, 'spike', **kw)
                    else:        cb(bk, sx * 8.9, C - w / 2, o + h / 2, w, w, h, 'spike', **kw)
                    o += h
    bn = m.bone('burner', [0, 15, 0], root)
    cb(bn, 0, 15.4, 0, 2.6, 0.8, 1.4, 'steel_d')                                                        # mounting plate
    cb(bn, -1.0, 16.2, 0, 0.6, 1.8, 0.6, 'steel'); cb(bn, 1.0, 16.2, 0, 0.6, 1.8, 0.6, 'steel'); cb(bn, 0, 17.8, 0, 2.6, 0.6, 0.6, 'steel')   # ring
    rp = m.bone('ropes', [0, 12, 0], root)
    L = 13.0
    for (ax, s) in (('z', 1), ('z', -1), ('x', 1)):
        kw = dict(rot=(ax, s * 22.5), rot_origin=[0, 18.2, 0])
        cb(rp, 0, 18.2, 0, 0.6, L, 0.6, 'rope', **kw)
    def tip(ax, s):                                                                     # where each rope ends
        d = L * _m.sin(_m.pi / 8)
        y = 18.2 + L * _m.cos(_m.pi / 8)
        return ((-s * d, y, 0) if ax == 'z' else (0, y, -s * d))
    env = m.bone('envelope', [0, 30, 0], root)
    tp = m.bone('tc_panels', [0, 30, 0], env)
    def ball(cx, by, cz, R):
        cy = by + 1.1 * R
        for (w, h) in ((2 * R, 1.1 * R), (1.85 * R, 1.6 * R), (1.55 * R, 2.0 * R), (1.0 * R, 2.3 * R)):
            cb(tp, cx, cy - h / 2, cz, w, h, w, 'tc', decals={'down': [('shade', 0, 0, 1, 1, 0.8)], 'north': [('lerp', '#9aa0b4', 0.55, 1.0, 'y')]})
        cb(tp, cx, by - 0.4, cz, 1.6, 1.4, 1.6, 'tc_d')                                                # knot
        cb(env, cx - 0.4 * R, cy + 0.15 * R, cz - R - 0.1, 0.35 * R, 0.45 * R, 0.2, 'shine')             # glossy highlight
    for (ax, s), R, k in ((('z', 1), 6.4, 1.5), (('z', -1), 6.4, 1.5), (('x', 1), 5.8, 1.7)):
        x, y, z = tip(ax, s)
        ball(x * k, y + (2.6 if ax == 'x' else 0.4 if s > 0 else 1.6), z * k, R)
    m.hitbox(1.4, 3.0)
    m.anim('idle', 2.4, 'loop', {'root': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 2.4)},
                                 'envelope': {'rotation': loop([[0, 0, -1.5], [1, 0, 1.5]], 2.4)},
                                 'basket': {'rotation': loop([[0, 0, 2], [-1.5, 0, -2]], 2.4)}})
    m.anim('walk', 1.6, 'loop', {'root': {'rotation': loop([[6, 0, 0], [8, 0, 0]], 1.6), 'position': loop([[0, 0, 0], [0, 0.8, 0]], 1.6)},
                                 'basket': {'rotation': loop([[-5, 0, 0], [-8, 0, 0]], 1.6)}})
    m.anim('hit', 0.4, 'once', {'envelope': {'rotation': [(0, [0, 0, 0]), (0.1, [-6, 0, 8]), (0.22, [4, 0, -5]), (0.4, [0, 0, 0])]}})
    m.anim('deploy', 0.6, 'once', {'envelope': {'scale': [(0, [0.2, 0.2, 0.2]), (0.35, [1.12, 1.12, 1.12]), (0.6, [1, 1, 1])]}})
    m.anim('death', 0.9, 'once', {'envelope': {'scale': [(0, [1, 1, 1]), (0.12, [1.25, 1.2, 1.25]), (0.22, [0.05, 0.05, 0.05]), (0.9, [0.01, 0.01, 0.01])]},
                                  'ropes': {'scale': [(0, [1, 1, 1]), (0.25, [1, 0.2, 1]), (0.9, [1, 0.01, 1])]},
                                  'basket': {'position': [(0, [0, 0, 0]), (0.2, [0, 2, 0]), (0.9, [0, -40, 0])], 'rotation': [(0, [0, 0, 0]), (0.9, [25, 0, 30])]},
                                  'burner': {'position': [(0, [0, 0, 0]), (0.9, [0, -38, 0])]}})
    return m


def rocket():
    """Rocket: bulging wooden barrel with painted skull, riveted steel nose cone + bands, 4 square steel fins, fiery exhaust."""
    m = new_model('clash_rocket')
    m.mats_({'wood': ('#965c32', 'soft'), 'steel': ('#a9b0b8', 'metal'), 'steel_d': ('#7e868f', 'metal'), 'steel_l': ('#ccd2d8', 'metal'),
             'tc': ('#e8e8e8', 'cloth'), 'fire': ('#ffcc33', 'glow'), 'fire_o': ('#ff7a1a', 'glow'), 'fire_y': ('#fff2a0', 'glow')})
    C = 8.8
    spin = m.bone('spin', [0, C, 0])
    def octa(b, z0, z1, R, mat, r=None, **kw):                                      # octagonal prism along z
        r = R * 0.38 if r is None else r
        for (w, h) in ((2 * R, 2 * R - 2 * r), (2 * R - 2 * r, 2 * R), (2 * R - r, 2 * R - r)):
            cb(b, 0, C - h / 2, (z0 + z1) / 2, w, h, z1 - z0, mat, **kw)
    def wood(z0, z1, R, skull=False):
        dec = {'east': [('fn', _staves(False, skull, True))], 'west': [('fn', _staves(False, skull, False))],
               'up': [('fn', _staves(True))], 'down': [('fn', _staves(True))]}
        octa(spin, z0, z1, R, 'wood', r=R * 0.26, decals=dec)
    wood(-10, 11, 14.0, skull=True)                                                  # bulging belly
    wood(-16, -10, 12.8); wood(11, 19, 12.8); wood(19, 22, 10.6)
    octa(spin, -21, -15, 14.8, 'steel', decals={f: [('shade', 0, 0, 1, 0.2, 1.12)] for f in ('east', 'west', 'up', 'down')})   # top band
    for (z0, z1, R) in ((-23, -21, 11.0), (-25, -23, 8.6), (-27, -25, 6.2), (-29, -27, 3.8), (-30.5, -29, 1.8)):
        cb(spin, 0, C - R, (z0 + z1) / 2, 2 * R, 2 * R, z1 - z0, 'steel', decals={'up': [('shade', 0, 0, 1, 1, 1.12)], 'down': [('shade', 0, 0, 1, 1, 0.85)]})   # stepped pyramid nose
    tc = m.bone('tc_band', [0, C, 0], spin)
    octa(tc, -15, -14, 13.4, 'tc')                                                  # thin team stripe under the top band
    octa(spin, 14, 17, 13.6, 'steel_d')                                               # lower band
    for ang in range(0, 8, 2):                                                              # rivets on both bands
        import math as _m
        a = ang * _m.pi / 4
        for (z, R) in ((-18, 15.0), (15.5, 13.8)):
            cb(spin, _m.cos(a) * R, C + _m.sin(a) * R - 1.0, z, 2.0, 2.0, 2.0, 'steel_l')
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):                               # 4 square fins
        if dx:
            cb(spin, dx * 15.0, C - 1.4, 18, 7.0, 2.8, 9.0, 'steel', decals={'up': [('shade', 0, 0, 1, 0.15, 1.15)]})
            cb(spin, dx * 18.4, C - 1.8, 18, 2.2, 3.6, 9.4, 'steel_d')
        else:
            cb(spin, 0, C + dy * 15.0 - 3.5, 18, 2.8, 7.0, 9.0, 'steel', decals={'east': [('shade', 0, 0, 1, 0.15, 1.15)]})
            cb(spin, 0, C + dy * 18.4 - 1.1, 18, 3.6, 2.2, 9.4, 'steel_d')
    fl = m.bone('flame', [0, C, 22], spin)
    octa(fl, 22, 24, 8.6, 'fire_o')
    octa(fl, 24, 27, 7.0, 'fire', decals={f: [('lerp', '#ff7a1a', 0.0, 0.6, 'y')] for f in ('east', 'west')})
    octa(fl, 27, 31, 4.4, 'fire_y')
    octa(fl, 31, 33, 2.0, 'fire')
    L = 2.4
    m.anim('idle', L, 'loop', {'spin': {'rotation': [(0, [0, 0, 0]), (L / 4, [0, 0, 90]), (L / 2, [0, 0, 180]), (3 * L / 4, [0, 0, 270]), (L, [0, 0, 360])]},
                               'flame': {'scale': [(0, [1, 1, 1]), (0.06, [1.1, 1.1, 1.4]), (0.12, [0.9, 0.9, 0.8]), (0.25, [1, 1, 1])] +
                                         [(t + k * 0.25, s) for k in range(1, 9) for (t, s) in ((0.06, [1.1, 1.1, 1.4]), (0.12, [0.9, 0.9, 0.8]), (0.25, [1, 1, 1]))]}})
    return m


def _chainmail(img, rng):
    """small round mail scales in offset rows"""
    import numpy as _np
    h, w, _ = img.shape
    base = img.copy()
    for y in range(h):
        for x in range(w):
            off = (y // 1) % 2
            if (x + off) % 2 == 0:
                img[y, x] = base[y, x] * 1.12
            else:
                img[y, x] = base[y, x] * 0.82
    img[:] = _np.clip(img, 0, 255)


def princess():
    """Princess: black bob + side bangs, gold crown, steel breastplate, chainmail skirt, team puffed striped sleeves +
    team leggings, brown gloves/boots/belt with gold crown buckle, recurve bow (archer rig)."""
    m = new_model('clash_princess')
    m.mats_({'skin': ('#f2c0a0', 'skin'), 'skin_d': ('#dca084', 'skin'), 'hair': ('#3a3030', 'hair'), 'hair_l': ('#54484a', 'hair'),
             'steel': ('#cdd3da', 'metal'), 'mail': ('#aab2bc', 'soft'), 'belt': ('#5a3a24', 'leather'), 'gold': ('#e2b23a', 'metal'),
             'boot': ('#6a4630', 'leather'), 'boot_l': ('#80583c', 'leather'), 'glove': ('#6a4630', 'leather'), 'tcl': ('#a8a8c4', 'cloth'),
             'tcs': ('#f2f2f2', 'cloth'), 'wood': ('#7a4a2a', 'wood'), 'wood_d': ('#3e2a1e', 'wood'), 'string': ('#e8e8e0', 'plain'),
             'fletch': ('#7070c8', 'cloth'), 'stripe': ('#f4f4f8', 'cloth'), 'shaft': ('#4a3426', 'wood')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.9
        lg = m.bone('leg_' + side, [x, 8, 0], root)
        tl = m.bone('tc_leg_' + side, [x, 8, 0], lg)
        cb(tl, x, 3.6, 0, 2.8, 4.6, 2.9, 'tcl')                                              # team leggings
        cb(lg, x, 0, -0.2, 3.2, 4.4, 3.4, 'boot', decals={'north': [('lerp', '#4a3020', 0.0, 0.3, 'y')]})   # boots
        cb(lg, x, 3.6, 0, 3.8, 1.4, 3.8, 'boot_l')                                            # floppy cuff
        cb(lg, x, 0, -2.0, 3.0, 1.4, 0.8, 'boot')                                             # toe
    body = m.bone('body', [0, 8, 0], root)
    tb = m.bone('tc_body', [0, 8, 0], body)
    cb(body, 0, 7.6, 0, 7.6, 4.6, 4.6, 'mail', decals={f: [('fn', _chainmail), ('shade', 0, 0.85, 1, 1, 0.8)] for f in ('north', 'south', 'east', 'west')})   # chainmail skirt
    cb(body, 0, 12.0, 0, 7.2, 1.4, 4.0, 'belt')                                               # belt
    cb(body, 0, 11.9, -2.15, 1.8, 1.8, 0.3, 'gold', decals={'north': pix(["k.k.k", "kkkkk", "kkkkk"], {'k': '#e2b23a'}) and [('rect', 0, 0, 0.2, 0.3, '#5a3a24'), ('rect', 0.4, 0, 0.6, 0.3, '#5a3a24'), ('rect', 0.8, 0, 1, 0.3, '#5a3a24')]})   # crown buckle
    cb(body, 0, 13.4, 0, 6.8, 6.6, 3.6, 'steel', decals={'north': [('rect', 0.47, 0, 0.53, 1, '#e8ecf0'), ('lerp', '#aab2bc', 0.1, 0.5, 'y'), ('rect', 0.35, 0.0, 0.65, 0.12, '#4a4a8a')]})   # breastplate
    hd = m.bone('head', [0, 20, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", ".p....p.", "...rr...", "........"],
               {'k': '#2a2020', 'w': '#ffffff', 'b': '#5a3a24', 'p': '#f29a9a', 'r': '#c2384a'})
    cb(hd, 0, 20, 0, 8, 8, 8, S, decals={'north': face})
    hr = m.bone('hair', [0, 24, 0], hd)
    cb(hr, 0, 26.4, 0.3, 8.8, 2.4, 8.8, 'hair', decals={'up': [('rect', 0.45, 0, 0.55, 1, '#54484a')]})   # crown of hair
    cb(hr, -0.9, 26.0, -4.45, 7.0, 2.0, 0.8, 'hair'); cb(hr, 3.6, 26.6, -4.45, 1.6, 1.4, 0.8, 'hair')   # side-swept bangs
    cb(hr, -3.0, 25.2, -4.45, 2.6, 1.0, 0.8, 'hair_l')
    for sx in (1, -1):
        cb(hr, sx * 4.45, 21.8, 0.6, 0.9, 5.6, 7.8, 'hair')                                  # bob sides
    cb(hr, 0, 21.0, 4.5, 8.8, 6.6, 1.0, 'hair'); cb(hr, 0, 20.6, 4.9, 8.0, 1.4, 1.0, 'hair_l')
    cr = m.bone('crown', [0, 28, 0], hd)
    cb(cr, 0, 28.6, 0.4, 5.4, 1.2, 5.4, 'gold', decals={f: [('lerp', '#f4d27a', 0.0, 0.4, 'y')] for f in ('north', 'east', 'west', 'south')})   # gold crown band
    for (x, h) in ((0, 2.2), (-2.0, 1.4), (2.0, 1.4)):
        cb(cr, x, 29.8, -2.0, 1.2 if x == 0 else 1.0, h, 0.6, 'gold')                              # front crown points
        cb(cr, x, 29.8, 2.8, 1.0, h - 0.4, 0.6, 'gold')                                           # back points
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.8
        a = m.bone('arm_' + side, [x, 18, 0], body)
        ta = m.bone('tc_arm_' + side, [x, 18, 0], a)
        stripes = [('rect', 0, y, 1, y + 0.2, '#6a6a96') for y in (0.12, 0.5, 0.86)]
        cb(ta, x + sx * 0.2, 15.4, 0, 3.8, 4.4, 3.8, 'tcs')                                     # puffed team sleeve
        for y in (16.2, 18.0):
            cb(a, x + sx * 0.2, y, 0, 3.9, 0.7, 3.9, 'stripe')                                    # white stripes
        cb(a, x, 11.4, 0, 2.8, 4.2, 2.8, S)                                                    # forearm
        cb(a, x, 8.0, 0, 3.0, 3.6, 3.0, 'glove'); cb(a, x, 11.0, 0, 3.4, 1.0, 3.4, 'boot_l')  # glove + cuff
    q = m.bone('quiver', [1.8, 14, 2.5], body)
    qr = dict(rot=('z', -22.5), rot_origin=[1.8, 14, 3.0])
    cb(q, 1.8, 9.4, 3.0, 2.6, 8.0, 2.6, 'belt', **qr)
    cb(q, 1.8, 17.2, 3.0, 3.0, 0.7, 3.0, 'gold', **qr)
    for (dx, dz) in ((-0.6, -0.5), (0.6, 0.5), (-0.5, 0.6)):
        cb(q, 1.8 + dx, 17.8, 3.0 + dz, 0.4, 2.4, 0.4, 'shaft', **qr); cb(q, 1.8 + dx, 18.8, 3.0 + dz, 1.0, 1.6, 0.25, 'fletch', **qr)
    bow = m.bone('bow', [-4.8, 8.6, -2.2], m.by_name('arm_l'))                                 # recurve bow, left hand
    bx, bz, by = -4.8, -2.2, 8.6
    cb(bow, bx, by - 2.2, bz, 1.3, 4.4, 1.5, 'wood_d')                                            # leather-wrapped grip
    segs = [(2.2, -0.4, 1.2), (3.9, -0.9, 1.1), (5.5, -1.2, 1.0), (7.0, -1.2, 0.9), (8.3, -0.6, 0.8), (9.3, 0.3, 0.7)]
    for sy in (1, -1):
        for j, (dy, dz, th) in enumerate(segs):
            h = 1.9 if j < 5 else 1.2
            yb = by + dy if sy > 0 else by - dy - h
            cb(bow, bx, yb, bz + dz, 0.9, h, th, 'wood_d' if j == 2 else 'wood')                     # curved limb with a dark wrap
        cb(bow, bx, by + 10.3 if sy > 0 else by - 10.9, bz + 1.0, 0.8, 0.6, 0.9, 'wood')              # recurved tip
    cb(bow, bx, by - 10.6, bz + 1.2, 0.2, 21.2, 0.2, 'string')
    arw = m.bone('arrow_tip', [bx, by, bz], bow)                                                # nocked arrow
    cb(arw, bx - 0.75, by + 1.4, bz - 3.0, 0.4, 0.4, 8.0, 'shaft')
    cb(arw, bx - 0.75, by + 1.1, bz - 7.6, 1.0, 1.0, 1.2, 'gold')
    cb(arw, bx - 0.75, by + 1.0, bz + 0.2, 0.25, 1.4, 1.8, 'fletch')
    m.hitbox(0.7, 1.9)
    shade_pass(m, ('skin', 'steel'))
    ready = {'arm_l': [-40, 15, 0], 'arm_r': [-72, -40, 10], 'bow': [90, 60, -30]}
    m.anim('idle', 2.0, 'loop', {'arm_l': {'rotation': loop([ready['arm_l'], [-42, 15, 0]], 2.0)},
                                 'arm_r': {'rotation': loop([ready['arm_r'], [-74, -40, 10]], 2.0)},
                                 'bow': {'rotation': loop([ready['bow'], ready['bow']], 2.0)},
                                 'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 4.0)},
                                 'body': {'position': loop([[0, 0, 0], [0, -0.2, 0]], 2.0)}})
    mc_walk(m, 0.7, 30, extra={'arm_l': {'rotation': loop([ready['arm_l'], [-38, 15, 0]], 0.7)},
                               'arm_r': {'rotation': loop([ready['arm_r'], [-70, -40, 10]], 0.7)},
                               'bow': {'rotation': loop([ready['bow'], ready['bow']], 0.7)}})
    al, ar_ = [-90, 25, 0], [-90, -12, 0]
    aim = {'arm_l': {'rotation': [(0, ready['arm_l']), (0.2, al), (0.65, al), (0.9, ready['arm_l'])]},
           'arm_r': {'rotation': [(0, ready['arm_r']), (0.2, ar_), (0.6, [-90, -18, 0]), (0.65, [-86, -6, 0]), (0.9, ready['arm_r'])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.2, [0, 12, 0]), (0.65, [0, 12, 0]), (0.9, [0, 0, 0])]},
           'bow': {'rotation': [(0, ready['bow']), (0.2, BOW_AIM), (0.65, BOW_AIM), (0.9, ready['bow'])]},
           'arrow_tip': {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 0]), (0.6, [0, 0, 2.5]), (0.62, [0, 0, 0])],
                         'scale': [(0, [1, 1, 1]), (0.6, [1, 1, 1]), (0.62, [0, 0, 0]), (0.85, [0, 0, 0]), (0.9, [1, 1, 1])]}}
    m.anim('attack', 0.9, 'once', aim)
    common_tail(m)
    return m


def _log_side(img, rng):
    """vanilla oak-log bark (lying on its side): streaky brown rows along the length"""
    import numpy as _np, random as _r
    h, w, _ = img.shape
    R = _r.Random(h * 131 + w)
    pal = [_np.array(c, float) for c in ((107, 82, 48), (79, 59, 33), (127, 100, 64), (94, 72, 42))]
    for y in range(h):
        x = 0
        while x < w:
            L = R.randint(2, 7)
            c = pal[0] if R.random() < 0.45 else R.choice(pal[1:])
            img[y, x:x + L] = c
            x += L
    img[:] = _np.clip(img, 0, 255)


def _log_end(img, rng):
    """vanilla oak-log top: tan rings + bark rim"""
    import numpy as _np
    h, w, _ = img.shape
    yy, xx = _np.mgrid[0:h, 0:w]
    dx, dy = (xx + 0.5 - w / 2) / 8.0, (yy + 0.5 - h / 2) / 8.0          # absolute scale: log radius = 8 px
    r = _np.maximum((_np.abs(dx) + _np.abs(dy)) / 1.38, _np.maximum(_np.abs(dx), _np.abs(dy)))
    img[:] = _np.array([176, 144, 92.0])
    for a0, a1 in ((0.2, 0.3), (0.48, 0.58), (0.72, 0.8)):
        img[(r > a0) & (r < a1)] = _np.array([150, 116, 68.0])
    img[r < 0.12] = _np.array([196, 164, 110.0])
    img[r >= 0.86] = _np.array([107, 82, 48.0])                           # bark rim


def log():
    """Spiked rolling log: octagonal orange log, painted bark planks + ringed end grain, chunky steel pyramid spikes."""
    m = new_model('clash_log')
    m.mats_({'wood': ('#6b5230', 'soft'), 'spike': ('#d4dadf', 'metal'), 'spike_d': ('#a8b2ba', 'metal')})
    C, L, Rr = 8.8, 52.0, 8.0
    roll = m.bone('roll', [0, C, 0])
    side = [('fn', _log_side)]
    r = 3.0
    for (h, d) in ((2 * Rr, 2 * Rr - 2 * r), (2 * Rr - 2 * r, 2 * Rr), (2 * Rr - r, 2 * Rr - r)):
        dec = {f: side for f in ('north', 'south', 'up', 'down')}; dec.update({'east': [('fn', _log_end)], 'west': [('fn', _log_end)]})
        cb(roll, 0, C - h / 2, 0, L, h, d, 'wood', decals=dec)                               # octagonal log
    sp = m.bone('spikes', [0, C, 0], roll)
    tiers = ((3.6, 0.6, 'spike_d'), (2.8, 1.2, 'spike'), (1.8, 1.2, 'spike'), (0.8, 1.0, 'spike'))
    def spike(x, k):
        d, diag = k // 2 % 4, k % 2
        rk = dict(rot=('x', 45), rot_origin=[x, C, 0]) if diag else {}
        o = Rr - 0.4
        for (w, h, mat) in tiers:
            sh = [('shade', 0, 0, 1, 1, 0.85)] if mat == 'spike' else []
            if d == 0:   cb(sp, x, C + o, 0, w, h, w, mat, decals={'north': sh}, **rk)
            elif d == 1: cb(sp, x, C - w / 2, -o - h / 2, w, w, h, mat, **rk)
            elif d == 2: cb(sp, x, C - o - h, 0, w, h, w, mat, **rk)
            else:        cb(sp, x, C - w / 2, o + h / 2, w, w, h, mat, **rk)
            o += h
    for x in (-19.0, -3.0, 13.0):
        spike(x, 0); spike(x, 4)                                                         # top / bottom rows
    for x in (-11.0, 5.0, 20.0):
        spike(x, 2); spike(x, 6)                                                         # side rows, staggered
    m.anim('idle', 0.43, 'loop', {'roll': {'rotation': [(0, [0, 0, 0]), (0.1075, [90, 0, 0]), (0.215, [180, 0, 0]), (0.3225, [270, 0, 0]), (0.43, [360, 0, 0])]}})
    return m


def musketeer():
    """Musketeer: silver morion with crest + team plume, big purple curls, team dress + cape, brown belt with gold buckle,
    silver pauldrons, tall brown boots, blunderbuss held two-handed at the hip."""
    m = new_model('clash_musketeer')
    m.mats_({'skin': ('#f2c0a0', 'skin'), 'skin_d': ('#dca084', 'skin'), 'hair': ('#a466c8', 'hair'), 'hair_d': ('#8448a8', 'hair'), 'hair_l': ('#c690e2', 'hair'),
             'tcd': ('#e8e8e8', 'cloth'), 'tcc': ('#c8c8c8', 'cloth'), 'belt': ('#6a4426', 'leather'), 'gold': ('#e2b23a', 'metal'),
             'boot': ('#8a5430', 'leather'), 'boot_l': ('#a86a40', 'leather'), 'steel': ('#c4cad2', 'metal'), 'steel_d': ('#9aa2ac', 'metal'), 'steel_l': ('#dfe3e8', 'metal'),
             'wood': ('#8a5530', 'wood'), 'wood_d': ('#6a3e22', 'wood'), 'iron': ('#6e747c', 'metal'), 'iron_l': ('#9aa0a8', 'metal'), 'void': ('#1a1a20', 'plain')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.8
        lg = m.bone('leg_' + side, [x, 8, 0], root)
        cb(lg, x, 4.4, 0, 2.6, 3.8, 2.6, S)                                                 # knee
        cb(lg, x, 0, 0, 3.0, 5.0, 3.2, 'boot', decals={'north': [('lerp', '#6a3e22', 0.0, 0.25, 'y')]})   # tall boot
        cb(lg, x, 4.4, 0, 3.6, 1.4, 3.8, 'boot_l')                                          # folded cuff
        cb(lg, x, 0, -1.8, 2.8, 1.4, 1.0, 'boot')                                           # toe
    body = m.bone('body', [0, 8, 0], root)
    tc = m.bone('tc_coat', [0, 13.5, 0], body)
    hem = [('shade', 0, 0, 1, 0.2, 0.85)]
    cb(tc, 0, 12.6, 0, 6.6, 6.0, 3.6, 'tcd', decals={'north': [('rect', 0.4, 0.75, 0.6, 1, '#f2c0a0')]})   # bodice, V neck
    cb(tc, 0, 7.6, 0.1, 7.8, 4.6, 4.6, 'tcd', decals={f: hem for f in ('north', 'south', 'east', 'west')})   # flared skirt
    cb(tc, 0, 6.6, 2.7, 8.0, 12.0, 0.6, 'tcc', decals={'south': [('shade', 0, 0, 1, 0.25, 0.85)]})          # cape down the back
    for sx in (1, -1):
        cb(tc, sx * 3.6, 6.8, 2.2, 0.6, 11.0, 1.2, 'tcc')                                     # cape sides
        cb(tc, sx * 2.6, 17.6, 1.6, 1.8, 1.2, 2.4, 'tcc')                                     # cape collar on the shoulders
    for x in (-2.2, 2.2):
        cb(body, x, 9.6, -2.38, 0.6, 0.6, 0.2, 'steel')                                        # skirt buttons
    cb(body, 0, 12.0, 0, 7.2, 1.4, 4.0, 'belt')                                               # belt
    cb(body, 0, 11.9, -2.1, 1.8, 1.6, 0.3, 'gold', decals={'north': [('rect', 0.35, 0.35, 0.65, 0.65, '#6a4426')]})   # buckle
    hd = m.bone('head', [0, 18.6, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", ".p....p.", "...rr...", "........"],
               {'k': '#5a2a6a', 'w': '#ffffff', 'b': '#4a2e20', 'p': '#f29a9a', 'r': '#c2384a'})
    cb(hd, 0, 18.6, 0, 8, 8, 8, S, decals={'north': face})
    hair = m.bone('hair', [0, 22, 0], hd)
    cb(hair, 0, 24.6, 0.4, 8.8, 2.4, 8.8, 'hair')                                              # crown under the helmet
    cb(hair, 0.8, 24.4, -4.4, 7.4, 1.8, 0.8, 'hair', decals={'north': [('rect', 0, 0, 1, 0.3, '#8448a8')]})   # side-swept bangs
    cb(hair, -3.4, 23.6, -4.4, 1.6, 1.4, 0.8, 'hair_d')
    cb(hair, 0, 19.0, 4.5, 8.6, 7.0, 1.0, 'hair')                                              # back
    curl = [('rect', 0.25, 0.25, 0.75, 0.75, '#c690e2'), ('rect', 0.4, 0.4, 0.6, 0.6, '#8448a8')]
    for sx in (1, -1):
        cb(hair, sx * 4.4, 21.4, 0.6, 0.8, 4.6, 8.0, 'hair')                                   # sides
        for (y, z, h, d) in ((20.2, -1.0, 3.0, 3.4), (19.2, 2.2, 3.4, 3.6)):
            cb(hair, sx * 4.9, y, z, 1.8, h, d, 'hair', decals={'east' if sx > 0 else 'west': curl, 'north': [('shade', 0, 0, 1, 0.3, 0.85)]})   # round curls
    pt = m.bone('ponytail', [0, 20, 4.8], hair)
    for sx in (-2.2, 2.2):
        cb(pt, sx, 18.6, 5.2, 3.4, 3.4, 1.6, 'hair', decals={'south': curl})                    # nape curls
    hm = m.bone('helmet', [0, 26, 0], hd)
    cb(hm, 0, 25.8, 0.3, 10.0, 0.8, 9.4, 'steel', decals={'up': [('shade', 0, 0, 1, 1, 1.08)]})   # morion brim (boat shaped)
    for sz in (1, -1):
        cb(hm, 0, 26.2, 0.3 + sz * 5.2, 7.6, 0.8, 1.4, 'steel'); cb(hm, 0, 26.8, 0.3 + sz * 6.2, 5.2, 0.8, 1.0, 'steel_d')   # brim sweeping up front/back
    cb(hm, 0, 26.4, 0.3, 8.6, 1.8, 9.0, 'steel', decals={'north': [('shade', 0, 0, 1, 0.3, 1.1)]})   # rounded dome
    cb(hm, 0, 28.2, 0.3, 7.6, 1.2, 8.0, 'steel'); cb(hm, 0, 29.4, 0.3, 6.0, 0.8, 6.6, 'steel'); cb(hm, 0, 30.2, 0.3, 4.0, 0.4, 4.6, 'steel')
    for (y, h, d) in ((28.6, 4.2, 3.6), (28.6, 3.4, 6.0), (28.6, 2.4, 8.0), (28.0, 1.6, 9.2)):
        cb(hm, 0, y, 0.3, 0.8, h, d, 'steel_l' if d < 4 else 'steel', decals={'east': [('shade', 0, 0, 1, 0.3, 0.85)], 'west': [('shade', 0, 0, 1, 0.3, 0.85)]})   # arched comb
    pl = m.bone('tc_plume', [3.4, 28, 3.0], hm)
    for (y, z, h, d) in ((27.8, 3.2, 1.8, 1.4), (29.4, 3.8, 1.8, 1.6), (31.0, 4.5, 1.8, 1.8), (32.6, 5.2, 1.6, 2.0), (33.6, 6.4, 1.2, 2.2), (32.6, 7.6, 1.4, 1.4)):
        cb(pl, 3.6 + (y - 27.8) * 0.06, y, z, 1.2, h, d + 0.8, 'tcd', decals={'east': [('rect', 0, 0.4, 1, 0.6, '#ffffff')]})   # feather sweeping back, curled tip
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.6
        a = m.bone('arm_' + side, [x, 18, 0], body)
        cb(a, x, 9.0, 0, 2.8, 7.0, 2.8, S)                                                    # bare arm
        cb(a, x, 14.6, 0, 3.0, 3.6, 3.0, 'tcd')                                               # short sleeve (team)
        cb(a, x + sx * 0.3, 16.0, 0, 3.8, 2.6, 3.8, 'steel', decals={'up': [('shade', 0, 0, 1, 1, 1.08)]})   # pauldron
        cb(a, x + sx * 0.3, 15.4, 0, 4.0, 0.6, 4.0, 'steel_d')
    P = (-0.6, 12.9, -4.0)                                                                    # gun held across the belly, pointing front-left
    rf = m.bone('rifle', list(P), body)
    def gcb(x, y, z, w, h, d, mat, **kw):
        return cb(rf, x, y + 1.0, z - 0.6, w, h, d, mat, rot=('y', GUN_YAW), rot_origin=list(P), **kw)
    X = P[0]
    gcb(X, 11.0, -2.2, 2.2, 2.8, 2.6, 'wood', decals={'east': [('shade', 0, 0, 1, 0.3, 0.8)], 'west': [('shade', 0, 0, 1, 0.3, 0.8)]})   # butt stock
    gcb(X, 11.6, -3.6, 1.8, 1.8, 1.4, 'wood_d')                                                  # grip
    gcb(X, 11.2, -8.6, 2.6, 1.8, 8.8, 'wood')                                                     # fore-stock
    gcb(X, 12.8, -10.2, 3.0, 3.0, 14.0, 'iron', decals={'up': [('rect', 0.35, 0, 0.65, 1, '#9aa0a8')]})   # barrel
    for z in (-6.0, -12.0):
        gcb(X, 12.5, z, 3.6, 3.6, 0.8, 'iron_l')                                                  # barrel bands
    gcb(X, 11.6, -17.6, 5.4, 5.4, 2.2, 'iron', decals={'north': [('rect', 0.22, 0.22, 0.78, 0.78, '#1a1a20')]})   # flared muzzle
    gcb(X, 12.1, -16.2, 4.4, 4.4, 0.8, 'iron_l')
    gcb(X + 1.3, 12.6, -3.8, 0.4, 1.2, 1.6, 'iron_l')                                              # flintlock
    m.hitbox(0.7, 1.9)
    shade_pass(m, ('skin', 'tcd', 'tcc'))
    P = POSE_MUSK
    def hold(L, k=0):
        return {'arm_r': {'rotation': loop([P['arm_r'], [P['arm_r'][0] - 3, P['arm_r'][1], P['arm_r'][2]]], L)},
                'rifle': {'rotation': loop([P['rifle'], [P['rifle'][0] + 3, P['rifle'][1], P['rifle'][2]]], L)},
                'arm_l': {'rotation': loop([P['arm_l'], [P['arm_l'][0] - 3, P['arm_l'][1], P['arm_l'][2]]], L)}}
    mc_idle(m, 2.0, extra=hold(2.0))
    w = hold(0.7); w['tc_coat'] = {'rotation': loop([[4, 0, 0], [8, 0, 0]], 0.35)}
    mc_walk(m, 0.7, 30, extra=w)
    A, K = POSE_AIM, POSE_KICK                                                               # swing the barrel forward, fire, recoil
    seq = lambda b: [(0, P[b]), (0.15, A[b]), (0.35, A[b]), (0.4, K[b]), (0.55, A[b]), (0.75, A[b]), (0.9, P[b])]
    at = {b: {'rotation': seq(b)} for b in ('arm_r', 'arm_l', 'rifle')}
    at['body'] = {'rotation': [(0, [0, 0, 0]), (0.35, [0, 0, 0]), (0.4, [-6, 0, 0]), (0.55, [0, 0, 0])]}
    m.anim('attack', 0.9, 'once', at)
    common_tail(m)
    return m


GUN_YAW = 45
PROW_YAW = -22.5
POSE_MUSK = {'arm_r': [-31, -17, -36], 'rifle': [14, 0, 14], 'arm_l': [-42, 4, 8]}
POSE_AIM = {'arm_r': [-32, -17, -36], 'rifle': [0, 45, 0], 'arm_l': [-40, 13, 24]}
POSE_KICK = {'arm_r': [-34, -17, -36], 'rifle': [-15, 45, 0], 'arm_l': [-42, 14, 25]}


def mini_pekka():
    """Mini P.E.K.K.A: squat dark steel-blue robot, round bucket helm with T visor + single glowing eye, glowing horns,
    big beak chest plate over the chin, layered skirt, stubby boots, segmented arms, cleaver in the right hand and a
    glowing spike on the left gauntlet. Eye/horns/spike = soft team colour."""
    m = new_model('clash_mini_pekka')
    m.mats_({'steel': ('#55657a', 'metal'), 'steel_d': ('#3a4656', 'metal'), 'steel_l': ('#7c8ea4', 'metal'), 'void': ('#0e1218', 'plain'),
             'joint': ('#2a323c', 'metal'), 'soft': ('#f4f4f4', 'gem'), 'blade': ('#a4aeb8', 'metal'), 'edge': ('#dde3e8', 'metal'), 'grip': ('#4a3424', 'wood')})
    def rb(b, x, y, z, w, h, d, mat, r=0.7, **kw):
        cb(b, x, y + r, z, w, h - 2 * r, d, mat, **kw); cb(b, x, y, z, w - 2 * r, h, d - 2 * r, mat); cb(b, x, y + r * 0.5, z, w - r, h - r, d + 0.02, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2.2, 5.4, 0], root)
        cb(lg, sx * 2.2, 2.6, 0, 2.6, 3.0, 2.6, 'joint')                                          # short thigh
        rb(lg, sx * 2.3, 2.4, 0, 3.4, 1.6, 3.4, 'steel_d', r=0.4)                                  # knee ring
        rb(lg, sx * 2.4, 0, -0.6, 4.0, 2.6, 5.0, 'steel', r=0.6)                                   # chunky boot
        cb(lg, sx * 2.4, 0, -3.2, 3.2, 1.4, 0.6, 'steel_d')                                        # toe cap
    body = m.bone('body', [0, 6.4, 0], root)
    for (y, w, d, mat) in ((4.6, 9.4, 7.4, 'steel_d'), (5.8, 10.2, 8.0, 'steel'), (7.0, 9.6, 7.6, 'steel_d')):
        rb(body, 0, y, 0.2, w, 1.4, d, mat, r=0.4)                                                 # layered skirt
    for x in (-3.2, 0, 3.2):
        cb(body, x, 4.2, -3.9, 2.6, 2.6, 0.6, 'steel_l' if x == 0 else 'steel', decals={'north': [('shade', 0, 0, 1, 0.4, 0.8)]})   # front tassets
    rb(body, 0, 8.2, 0.6, 9.0, 6.0, 7.0, 'steel_d', r=0.8)                                         # torso core
    for sx in (1, -1):
        rb(body, sx * 5.6, 11.4, 0.6, 4.6, 3.6, 6.0, 'steel', r=1.0)                               # round pauldron
        cb(body, sx * 5.6, 14.6, 0.6, 3.2, 0.5, 4.6, 'steel_l')
    hd = m.bone('head', [0, 14.0, 0.6], body)
    rb(hd, 0, 13.0, 0.8, 8.4, 7.4, 8.0, 'steel', r=1.0)                                            # bucket helm
    rb(hd, 0, 19.8, 0.8, 6.8, 1.6, 6.6, 'steel', r=0.6)                                            # dome
    cb(hd, 0, 21.0, 0.8, 1.2, 0.6, 5.6, 'steel_l')                                                  # crest
    cb(hd, 0, 17.6, -3.25, 6.6, 1.4, 0.2, 'void')                                                   # visor slot
    for sx in (1, -1):
        cb(hd, sx * 2.1, 19.0, -3.6, 3.2, 0.9, 0.8, 'steel_l', rot=('z', sx * 22.5), rot_origin=[sx * 2.1, 19.45, -3.6])   # angry V brow
        cb(hd, sx * 4.25, 16.4, 0.8, 0.3, 0.8, 0.8, 'steel_l')                                     # side rivets
    ey = m.bone('ts_eye', [0, 17.6, -3.3], hd)
    cb(ey, 0, 17.8, -3.4, 1.6, 1.0, 0.2, 'soft', decals={'north': [('rect', 0.3, 0.3, 0.7, 0.7, '#ffffff')]})   # single glowing eye
    cb(hd, 0, 13.0, -3.9, 7.6, 3.4, 1.6, 'steel', decals={'north': [('shade', 0, 0, 1, 0.3, 0.85)]})      # flat closed jaw plate
    cb(hd, 0, 16.0, -3.9, 7.8, 0.4, 1.8, 'steel_l')                                                 # jaw upper rim
    cb(hd, 0, 14.5, -4.75, 4.6, 0.4, 0.1, 'void')                                                   # shut mouth line
    for sx in (1, -1):
        cb(hd, sx * 2.45, 14.1, -4.75, 0.4, 0.8, 0.1, 'void')                                       # down-turned corners
        cb(hd, sx * 3.0, 15.3, -4.8, 0.5, 0.5, 0.2, 'steel_l')                                      # jaw rivets
    hn = m.bone('ts_horns', [0, 18, 0.8], hd)
    for sx in (1, -1):
        for (dx, dy, w, h) in ((4.6, 17.0, 1.8, 1.8), (5.8, 17.8, 1.6, 1.8), (6.6, 19.2, 1.4, 1.8), (6.9, 20.8, 1.1, 1.6), (6.8, 22.2, 0.7, 1.2)):
            cb(hn, sx * dx, dy, 0.6, w, h, w, 'soft', decals={'north': [('rect', 0.15, 0, 0.4, 1, '#ffffff')], 'east': [('shade', 0, 0, 1, 1, 0.8)]})   # glowing horns
    rb(body, 0, 8.6, -2.6, 8.0, 6.4, 2.0, 'steel', r=0.6, decals={'north': [('rect', 0.47, 0, 0.53, 1, '#7c8ea4'), ('shade', 0, 0, 1, 0.3, 0.85)]})   # round breastplate
    for sx in (1, -1):
        cb(body, sx * 3.0, 12.0, -3.65, 0.6, 0.6, 0.3, 'steel_l')                                   # rivets
    arms = {}
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = arms[side] = m.bone('arm_' + side, [sx * 5.6, 12.8, 0.6], body)
        cb(a, sx * 6.2, 9.0, 0.6, 2.2, 2.6, 2.2, 'joint')                                          # upper arm
        rb(a, sx * 6.2, 8.0, 0.6, 3.0, 1.4, 3.0, 'steel_d', r=0.4)                                  # elbow ring
        cb(a, sx * 6.2, 6.6, 0.6, 2.0, 1.6, 2.0, 'joint')
        rb(a, sx * 6.4, 2.6, 0.4, 4.0, 4.4, 4.2, 'steel', r=0.6)                                    # blocky gauntlet
        cb(a, sx * 6.4, 6.6, 0.4, 4.4, 0.7, 4.6, 'steel_l')
        rb(a, sx * 6.4, 0.6, 0.0, 3.6, 2.4, 3.8, 'steel_d', r=0.5)                                  # fist
    sw = m.bone('sword', [6.4, 1.2, 0.0], arms['r'])
    cb(sw, 6.4, -0.4, 0.0, 1.2, 3.2, 1.2, 'grip')                                                   # grip through the fist
    cb(sw, 6.4, -1.0, 0.0, 1.6, 0.8, 1.6, 'steel_d')                                                # pommel
    cb(sw, 6.4, 0.8, -2.4, 1.0, 1.2, 1.8, 'steel_d')                                                # guard block
    cb(sw, 6.4, -0.6, -9.6, 0.8, 4.6, 12.8, 'blade', decals={'east': [('lerp', '#c4ccd4', 0.0, 0.6, 'y')], 'west': [('lerp', '#c4ccd4', 0.0, 0.6, 'y')]})   # wide cleaver blade
    cb(sw, 6.4, 3.6, -9.6, 1.0, 0.6, 12.8, 'steel_d')                                               # thick spine
    cb(sw, 6.4, -1.0, -9.6, 0.6, 0.5, 12.8, 'edge')                                                 # sharp lower edge
    cb(sw, 6.4, 0.6, -16.4, 0.8, 3.0, 0.8, 'blade'); cb(sw, 6.4, 2.2, -16.2, 0.8, 1.4, 0.4, 'blade')   # squared tip, clipped corner
    m.hitbox(0.9, 1.4)
    shade_pass(m, ('steel',))
    hold = {'arm_r': {'rotation': loop([[-30, 0, 4], [-33, 0, 6]], 2.0)}, 'arm_l': {'rotation': loop([[-20, 0, -4], [-23, 0, -6]], 2.0)}}
    mc_idle(m, 2.0, extra=hold)
    mc_walk(m, 0.6, 28, arm_r=False, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-40, 0, 4]], 0.6)},
                                            'body': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 0.6)}})
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 4]), (0.2, [-160, 0, 10]), (0.32, [-15, 0, 0]), (0.6, [-30, 0, 4])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-8, 12, 0]), (0.32, [12, -12, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m)
    return m


def clone_into(m, src, parent, names, s=1.0, off=(0, 0, 0)):
    """copy bones/cubes of model src into m under parent. names: {src_name: new_name or None(skip)}; scale s about origin then offset"""
    import copy
    pre = 'cl_' + src.name.replace('clash_', '') + '_'
    for k, v in src.mats.items():
        m.mats[pre + k] = v
    made = {}
    T = lambda p: [p[0] * s + off[0], p[1] * s + off[1], p[2] * s + off[2]]
    for bn in src.bones:
        if bn.name not in names or names[bn.name] is None:
            continue
        par = made.get(bn.parent.name, parent) if bn.parent is not None else parent
        nb = m.bone(names[bn.name], T(bn.origin), par)
        made[bn.name] = nb
        for c in bn.cubes:
            f, t = T(c['frm']), T(c['to'])
            nc = cb(nb, (f[0] + t[0]) / 2, f[1], (f[2] + t[2]) / 2, t[0] - f[0], t[1] - f[1], t[2] - f[2], pre + c['mat'],
                    rot=c['rot'], rot_origin=T(c['rot_origin']))
            nc['decals'] = copy.deepcopy(c['decals']); nc['faces'] = {k: pre + v for k, v in c['faces'].items()}
    return made

def compare(doc, name, out):
    import json
    from bbrender import render
    from PIL import Image
    W = os.path.dirname(os.path.abspath(__file__))
    hr = json.load(open(os.path.join(W, 'pkg342/ClashMC_v3.4.2/models/base/clash_hog_rider.bbmodel')))
    card = {'clash_mega_knight': 'mega-knight', 'clash_giant_skeleton': 'giant-skeleton', 'clash_valkyrie': 'valkyrie',
            'clash_executioner': 'executioner', 'clash_lumberjack': 'lumberjack', 'clash_royal_hog': 'royal-hogs'}[name]
    S = 360
    cam = (0.6, 0.5, -1.0)
    a = render(hr, S, cam=cam)
    b = render(doc, S, cam=cam, tint=(60, 100, 240))
    c = render(doc, S, cam=(-0.6, 0.4, 1.0), tint=(225, 60, 60))
    ref = Image.open(os.path.join(os.path.dirname(W), 'refimg', card + '.png')).convert('RGBA')
    img = Image.new('RGBA', (S * 3 + 302, max(S, 363)), (255, 255, 255, 255))
    img.paste(a, (0, 0)); img.paste(b, (S, 0)); img.paste(c, (2 * S, 0)); img.paste(ref, (3 * S, 0), ref)
    img.save(os.path.join(out, 'cmp_%s.png' % name))


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    rest = sys.argv[3:]
    only = [a for a in rest if not a.startswith('--')]
    os.makedirs(out, exist_ok=True)
    for fn in (firecracker, cursed_hog, mother_witch, electro_giant, electro_dragon, flying_machine, ram_rider, royal_giant, guard_parts, prince, inferno_dragon, magic_archer, electro_wizard, ice_wizard, bandit, wall_breaker, pekka, hunter, elixir_collector, dart_goblin, goblin_brawler, goblin_cage, spear_goblin, goblin, night_witch, witch, zappies, wizard, x_bow, tombstone, sparky, skeleton_balloon, rocket, princess, log, musketeer, mini_pekka, mega_minion, minion, miner, knight, ice_golem, golem, golemite, elixir_golem, elixir_golemite, elixir_blob, giant, heal_spirit, ice_spirit, fire_spirit, electro_spirit, dark_prince, bomber, bomb_tower, bats, barbarian_hut, battle_ram, barbarian_barrel, elite_barbarian, barbarian, balloon, baby_dragon, archer, mega_knight, giant_skeleton, valkyrie, executioner, lumberjack, royal_hog):
        if only and fn.__name__ not in only:
            continue
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        doc = m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad, 'hitbox', getattr(m, 'hitbox_size', None))
        if '--no-preview' not in rest:
            compare(doc, m.name, out)
