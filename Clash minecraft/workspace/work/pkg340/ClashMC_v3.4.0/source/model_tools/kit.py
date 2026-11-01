"""Shared building blocks: centred boxes, detailed humanoid rig, faces, animation sets."""
import sys
sys.path.insert(0, '/home/claude/models')
from rigs import humanoid_anims, common_anims, quad_walk, flap, building_anims  # noqa: F401  (anim-only helpers)


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """centred (x,z) / bottom (y) box"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def part(m, name, parent, frm, to, mat, **kw):
    """bone whose pivot is the cube centre (keeps big cubes inside the ±48px limit)"""
    o = [(frm[i] + to[i]) / 2 for i in range(3)]
    b = m.bone(name, o, parent)
    b.box(frm, to, mat, **kw)
    return b


# ------------------------------------------------------------------ faces
def face(eye='#20242a', white='#f2f2f2', brow=None, mouth='#7a3434', nose=0.86, beard=None, cheeks=None,
         mustache=None, eye_y=0.40, wide=False):
    ex = (0.16, 0.38) if wide else (0.2, 0.38)
    sp = [('rect', ex[0], eye_y, ex[1], eye_y + 0.16, white), ('rect', 1 - ex[1], eye_y, 1 - ex[0], eye_y + 0.16, white),
          ('rect', ex[0] + 0.08, eye_y + 0.02, ex[1], eye_y + 0.16, eye), ('rect', 1 - ex[1], eye_y + 0.02, 1 - ex[0] - 0.08, eye_y + 0.16, eye),
          ('shade', 0.44, eye_y + 0.14, 0.56, eye_y + 0.30, nose)]
    if brow:
        sp += [('rect', ex[0] - 0.02, eye_y - 0.08, ex[1] + 0.02, eye_y - 0.02, brow),
               ('rect', 1 - ex[1] - 0.02, eye_y - 0.08, 1 - ex[0] + 0.02, eye_y - 0.02, brow)]
    if cheeks:
        sp += [('rect', 0.1, eye_y + 0.24, 0.22, eye_y + 0.30, cheeks), ('rect', 0.78, eye_y + 0.24, 0.9, eye_y + 0.30, cheeks)]
    if beard:
        sp += [('rect', 0.0, 0.66, 1.0, 1.0, beard), ('rect', 0.12, 0.58, 0.88, 0.7, beard)]
        sp += [('rect', 0.38, 0.72, 0.62, 0.78, mouth)]
    else:
        sp += [('rect', 0.36, 0.72, 0.64, 0.77, mouth)]
    if mustache:
        sp += [('rect', 0.28, 0.64, 0.72, 0.70, mustache)]
    return sp


def visor(slit='#121418', glow=None):
    sp = [('shade', 0.0, 0.0, 1.0, 0.12, 1.15), ('rect', 0.12, 0.36, 0.88, 0.47, slit),
          ('rect', 0.47, 0.47, 0.53, 0.9, '#4a5058')]
    for i in range(3):
        x = 0.2 + i * 0.08
        sp += [('rect', x, 0.62, x + 0.04, 0.82, slit), ('rect', 1 - x - 0.04, 0.62, 1 - x, 0.82, slit)]
    if glow:
        sp += [('rect', 0.22, 0.38, 0.34, 0.45, glow), ('rect', 0.66, 0.38, 0.78, 0.45, glow)]
    return sp


def hood_face(glow='#7ff3ff', inner='#15171d', skin=None):
    sp = [('rect', 0.12, 0.18, 0.88, 1.0, inner)]
    if skin:
        sp += [('rect', 0.2, 0.55, 0.8, 1.0, skin), ('rect', 0.38, 0.8, 0.62, 0.84, '#3a2020')]
    sp += [('rect', 0.24, 0.42, 0.40, 0.52, glow), ('rect', 0.60, 0.42, 0.76, 0.52, glow),
           ('rect', 0.28, 0.44, 0.36, 0.50, '#ffffff'), ('rect', 0.64, 0.44, 0.72, 0.50, '#ffffff')]
    return sp


# ------------------------------------------------------------------ humanoid
def humanoid(m, P):
    """Detailed humanoid. P: proportions + material keys. Returns dict of bones/points.
    keys: s, leg_h, leg_w, hip_w, torso (w,h,d), head (w,h,d), arm (w,h), gap
          mats: pants, boot, torso, belt, skin, sleeve, glove, head, face(decal list)"""
    s = P.get('s', 1.0)
    lh, lw = P.get('leg_h', 11) * s, P.get('leg_w', 4.5) * s
    tw, th, td = [v * s for v in P.get('tsize', (10, 11, 6))]
    hw, hh, hd = [v * s for v in P.get('hsize', (9, 9, 9))]
    aw, ah = [v * s for v in P.get('asize', (4, 11))]
    gap = P.get('gap', 0.0) * s
    hip_w = P.get('hip_w', tw)
    root = m.bone('root', [0, 0, 0])
    # legs ---------------------------------------------------------
    legs = {}
    for side, sx in (('r', 1), ('l', -1)):
        cx = sx * (hip_w / 2 - lw / 2 - 0.1 * s)
        b = m.bone('leg_' + side, [cx, lh, 0], root)
        cb(b, cx, 3 * s, 0, lw, lh - 3 * s, lw, P['pants'])                      # thigh/shin
        cb(b, cx, 0, -0.6 * s, lw + 0.6 * s, 3.4 * s, lw + 1.4 * s, P['boot'])    # boot w/ toe
        cb(b, cx, 3.2 * s, 0, lw + 0.9 * s, 1.0 * s, lw + 0.9 * s, P['boot'])     # boot cuff
        if P.get('knee'):
            cb(b, cx, lh * 0.45, -lw / 2 - 0.3 * s, lw * 0.8, 2.2 * s, 1.2 * s, P['knee'])
        legs[side] = b
    # body ---------------------------------------------------------
    body = m.bone('body', [0, lh, 0], root)
    cb(body, 0, lh - 0.5 * s, 0, hip_w + 0.4 * s, 3 * s, td + 0.4 * s, P['pants'])           # hips
    cb(body, 0, lh + 2 * s, 0, tw, th - 2 * s, td, P['torso'])                                # chest
    cb(body, 0, lh + 1.6 * s, 0, tw + 0.6 * s, 1.8 * s, td + 0.6 * s, P['belt'])              # belt
    if P.get('buckle'):
        cb(body, 0, lh + 1.4 * s, -td / 2 - 0.5 * s, 2.4 * s, 2.2 * s, 0.6 * s, P['buckle'])
    neck = lh + th
    # head ---------------------------------------------------------
    head = m.bone('head', [0, neck, 0], body)
    cb(head, 0, neck - 0.6 * s, 0, hw * 0.45, 1.2 * s, hd * 0.45, P['skin'])                   # neck
    cb(head, 0, neck + 0.4 * s, 0, hw, hh, hd, P['head'], faces={'north': P.get('face_mat', P['head'])},
       decals={'north': P.get('face', [])}, dens=P.get('head_dens', 2))
    # arms ---------------------------------------------------------
    arms = {}
    sh = neck - 1.2 * s
    for side, sx in (('r', 1), ('l', -1)):
        cx = sx * (tw / 2 + aw / 2 + gap)
        b = m.bone('arm_' + side, [cx, sh, 0], body)
        cb(b, cx, neck - ah + 3 * s, 0, aw, ah - 3 * s, aw, P['sleeve'])
        cb(b, cx, neck - ah, 0, aw + 0.5 * s, 3.6 * s, aw + 0.5 * s, P['glove'])                 # hand / glove
        if P.get('cuff'):
            cb(b, cx, neck - ah + 3.2 * s, 0, aw + 1.0 * s, 1.4 * s, aw + 1.0 * s, P['cuff'])
        arms[side] = b
    hand_y = neck - ah + 1.6 * s
    # 머리는 목 기준으로 줄임 (모자/투구 등 머리에 붙은 것도 같이) → fit() 때 적용
    m.head_scale = ('head', P.get('head_k', 0.8), [0, neck, 0])
    return dict(root=root, body=body, head=head, arm_r=arms['r'], arm_l=arms['l'], leg_r=legs['r'], leg_l=legs['l'],
                s=s, lh=lh, tw=tw, th=th, td=td, hw=hw, hh=hh, hd=hd, aw=aw, ah=ah, neck=neck,
                head_y=neck + 0.4 * s, hand_r=(tw / 2 + aw / 2 + gap, hand_y, 0), hand_l=(-tw / 2 - aw / 2 - gap, hand_y, 0))
