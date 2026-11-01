def giant_skeleton():
    """HQ vanilla-like CR giant skeleton: sculpted skull (real eye/nose cavities, cheekbones, single teeth),
    hollow ribcage of separate ribs, segmented spine, condyle joints, segmented curled fingers, toes,
    hollow open barrel with stave rim + rope straps, team ushanka with fur lining"""
    m = new_model('clash_giant_skeleton')
    m.mats_({'bone': ('#e8e5dc', 'bone'), 'bone_d': ('#cbc7bb', 'bone'), 'bone_k': ('#a39f94', 'bone'),
             'tooth': ('#f6f3ea', 'bone'), 'void': ('#141210', 'plain'),
             'fur': ('#efefef', 'cloth'), 'lining': ('#e2ebf0', 'fur'),
             'wood': ('#8a5a32', 'wood', {'planks': True}), 'wood_d': ('#5a3820', 'wood'),
             'hoop': ('#80848c', 'metal'), 'rope': ('#c9a265', 'rope')})
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
        B(body, sx * 2.8, 9.6, 0.6, 3.4, 3.0, 1.2, 'bone_d', rot=('y', -sx * 22))  # iliac wings
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
        B(body, sx * 4.4, 25.4, -2.6, 6.6, 1.2, 1.2, 'bone', rot=('z', sx * 6))     # clavicles
        B(body, sx * 3.6, 21.4, 4.1, 3.6, 4.4, 0.8, 'bone_d', rot=('y', sx * 12))   # shoulder blades
    # ---------------------------------------------------------------- skull
    hd = r.bone('head', [0, 26.4, -0.6], body)
    B(hd, 0, 27.4, -0.1, 10, 9, 8.6, 'bone', faces={'north': 'void'})            # cranium (front = dark cavity)
    fz = -5.1                                                                     # face plate centre z (1.4 thick)
    B(hd, 0, 33.4, fz, 10, 3.0, 1.4, 'bone')                                      # forehead
    B(hd, 0, 33.0, -5.95, 10.2, 0.9, 0.5, 'bone_d')                               # brow ridge
    for sx in (1, -1):
        B(hd, sx * 4.6, 29.6, fz, 0.8, 3.8, 1.4, 'bone')                          # outer socket rim
        B(hd, sx * 2.6, 29.6, fz, 3.2, 0.6, 1.4, 'bone')                          # under-socket cheekbone
        B(hd, sx * 5.3, 29.2, -3.0, 0.8, 1.6, 4.2, 'bone_d')                      # zygomatic arch
        B(hd, sx * 2.75, 27.4, fz, 4.5, 2.2, 1.4, 'bone')                         # maxilla
    B(hd, 0, 31.8, fz, 2.0, 1.6, 1.4, 'bone')                                     # nasal bridge
    B(hd, 0, 27.4, fz + 0.4, 1.0, 1.0, 0.6, 'bone_d')                             # under-nose
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
    B(fl, 0, 34.4, -6.4, 11.8, 2.6, 1.6, 'lining')                                # front fold-up
    for i in range(6):
        B(fl, -4.8 + i * 1.9, 34.0 + (i % 2) * 0.3, -6.9, 1.4, 0.6, 0.8, 'lining')   # fluffy edge tufts
    for sx in (1, -1):
        B(fl, sx * 5.6, 28.6, 0.0, 0.4, 6.4, 7.2, 'lining')                        # inner flap fur
        B(fl, sx * 6.3, 27.6, 0.0, 1.3, 0.9, 8.2, 'lining')                        # flap bottom edge
    B(fl, 0, 27.6, 5.0, 11.6, 0.9, 1.3, 'lining')
    # ---------------------------------------------------------------- open barrel on the back
    bar = r.bone('barrel', [0, 22, 3.6], body)
    zc, y0, H = 9.6, 15.0, 11.6
    B(bar, 0, y0, zc - 4.1, 10.4, H, 1.0, 'wood')                                 # front wall
    B(bar, 0, y0, zc + 4.1, 10.4, H, 1.0, 'wood')                                 # back wall
    for sx in (1, -1):
        B(bar, sx * 4.7, y0, zc, 1.0, H, 7.2, 'wood')                             # side walls
    B(bar, 0, y0, zc, 8.4, 0.8, 7.2, 'wood_d')                                    # bottom
    for i, (dx, dz) in enumerate(((-3.2, -4.1), (1.8, -4.1), (4.7, 1.6), (-4.7, -1.4), (0.4, 4.1))):
        B(bar, dx, y0 + H, zc + dz, 1.0, 0.5 + (i % 2) * 0.3, 1.0, 'wood')        # uneven stave tops
    for y in (16.6, 24.2):                                                        # steel bands (4 strips each)
        B(bar, 0, y, zc - 4.7, 11.0, 1.1, 0.4, 'hoop')
        B(bar, 0, y, zc + 4.7, 11.0, 1.1, 0.4, 'hoop')
        for sx in (1, -1):
            B(bar, sx * 5.3, y, zc, 0.4, 1.1, 9.0, 'hoop')
    for sx in (1, -1):                                                            # rope straps
        x = sx * 5.2
        B(bar, x, 26.4, 0.4, 1.3, 1.3, 9.6, 'rope')                               # over the shoulder
        B(bar, x, 17.4, -4.6, 1.3, 9.6, 1.3, 'rope')                              # down the chest
        B(bar, x, 16.6, 0.4, 1.3, 1.3, 9.6, 'rope')                               # back under the arm
        B(bar, x, 15.0, -4.6, 1.2, 1.6, 1.2, 'rope')                              # knot
    # ---------------------------------------------------------------- long arms
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.0
        a = r.bone('arm_' + side, [x, 24.8, 0], body)
        B(a, x, 22.4, 0, 3.6, 3.6, 3.6, 'bone_d')                                 # humeral head
        B(a, x, 17.4, 0, 2.2, 5.2, 2.2, 'bone')                                   # humerus
        for dz in (-0.8, 0.8):
            B(a, x, 15.4, dz, 3.2, 2.0, 1.4, 'bone_d')                            # elbow condyles
        B(a, x, 15.2, 1.6, 1.4, 1.4, 1.0, 'bone')                                 # olecranon
        for dz in (-0.6, 0.6):
            B(a, x, 10.6, dz, 1.0, 4.8, 1.0, 'bone')                              # radius + ulna
        B(a, x, 9.8, 0, 2.6, 0.9, 2.8, 'bone_d')                                  # wrist
        B(a, x, 7.4, 0, 3.0, 2.4, 3.6, 'bone')                                    # palm
        for i, dz in enumerate((-1.35, -0.45, 0.45, 1.35)):
            ln = 1.6 - abs(dz) * 0.2
            B(a, x, 7.4 - ln, dz, 0.8, ln, 0.8, 'bone_d')                         # proximal phalanx
            B(a, x - sx * 0.3, 7.4 - ln - 1.4, dz, 0.7, 1.4, 0.7, 'bone')          # distal phalanx (curled in)
        B(a, x - sx * 1.6, 6.8, -1.4, 0.9, 1.6, 0.9, 'bone_d')                     # thumb
        B(a, x - sx * 1.9, 5.6, -1.6, 0.8, 1.2, 0.8, 'bone')
    m.hitbox(2.2, 4.2)
    stoop = {'body': {'rotation': loop([[10, 0, 0], [12, 0, 0]], 2.4), 'position': loop([[0, 0, 0], [0, -0.3, 0]], 2.4)},
             'head': {'rotation': loop([[-8, 8, 0], [-8, 0, 0], [-8, -8, 0], [-8, 0, 0]], 4.8)},
             'jaw': {'rotation': loop([[0, 0, 0], [6, 0, 0], [0, 0, 0], [0, 0, 0]], 2.4)},
             'arm_r': {'rotation': loop([[-10, 0, 3], [-14, 0, 5]], 2.4)}, 'arm_l': {'rotation': loop([[-10, 0, -3], [-14, 0, -5]], 2.4)}}
    m.anim('idle', 2.4, 'loop', stoop)
    mc_walk(m, 1.2, 22, extra={'body': {'rotation': loop([[12, 0, 0], [12, 0, 0]], 1.2)},
                               'head': {'rotation': loop([[-10, 0, 0], [-10, 0, 0]], 1.2)}})
    punch = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [35, 0, sg * 20]), (0.42, [38, 0, sg * 20]), (0.55, [-92, -sg * 22, 0]),
                              (0.7, [-88, -sg * 20, 0]), (1.0, [0, 0, 0])]} for s, sg in (('arm_r', 1), ('arm_l', -1))}
    punch['body'] = {'rotation': [(0, [10, 0, 0]), (0.4, [0, 0, 0]), (0.55, [24, 0, 0]), (1.0, [10, 0, 0])]}
    punch['jaw'] = {'rotation': [(0, [0, 0, 0]), (0.5, [18, 0, 0]), (0.7, [0, 0, 0])]}
    m.anim('attack', 1.0, 'once', punch)
    common_tail(m, death={'root': {'scale': [(0, [1, 1, 1]), (0.5, [1, 0.9, 1]), (0.9, [1.05, 0.25, 1.05])]},
                          'jaw': {'rotation': [(0, [0, 0, 0]), (0.4, [25, 0, 0])]}})
    return m


