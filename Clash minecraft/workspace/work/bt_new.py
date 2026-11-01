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
    cb(tw, 0, 0, 0, 22, 4, 20, 'stone')                                                 # stone core
    def stud(bone, x, y, z, face):                                                      # 2-step pyramid stud
        if face in 'ns':
            sg = -1 if face == 'n' else 1
            cb(bone, x, y, z + sg * 0.4, 3.0, 3.0, 0.8, 'stone_d'); cb(bone, x, y + 0.75, z + sg * 1.0, 1.5, 1.5, 0.6, 'stone_d')
        else:
            sg = -1 if face == 'w' else 1
            cb(bone, x + sg * 0.4, y, z, 0.8, 3.0, 3.0, 'stone_d'); cb(bone, x + sg * 1.0, y + 0.75, z, 0.6, 1.5, 1.5, 'stone_d')
    for sz in (1, -1):                                                                  # front/back stone blocks
        cb(tw, 0, 0, sz * 9.2, 20, 9, 5, 'stone'); cb(tw, 0, 9, sz * 9.0, 18, 1.2, 4.4, 'stone')
        for x in (-5.0, 5.0):
            stud(tw, x, 3.0, sz * 11.7, 'n' if sz < 0 else 's')
    for sx in (1, -1):                                                                  # side blocks + corner spikes
        cb(tw, sx * 11.0, 0, 0, 5, 8, 12, 'stone')
        stud(tw, sx * 13.5, 2.6, 0, 'e' if sx > 0 else 'w')
        for sz in (1, -1):
            cb(tw, sx * 12.4, 2.0, sz * 9.6, 2.4, 2.4, 2.4, 'stone_d'); cb(tw, sx * 13.4, 2.6, sz * 10.8, 1.2, 1.2, 1.2, 'stone_d')
    for sx in (1, -1):                                                                  # thick pine posts
        cb(tw, sx * 5.5, 8, 0, 6.0, 21, 8.0, 'pine')
        cb(tw, sx * 5.5, 25.0, 0, 7.4, 2.0, 9.4, 'rope')                                 # rope coils
        cb(tw, sx * 5.5, 27.0, 0, 7.6, 2.0, 9.6, 'rope_d')
        cb(tw, sx * 5.5, 29.0, 0, 7.2, 1.4, 9.2, 'rope')
    cb(tw, 0, 15.4, -4.6, 20.0, 3.4, 1.4, 'pine', rot=('z', 22.5), rot_origin=[0, 17.1, -4.6])   # diagonal brace
    for x in (-7.0, 7.0):
        cb(tw, x, 17.1 + (x * 0.41) - 0.6, -5.5, 1.2, 1.2, 0.5, 'steel')                # rivets
    cb(tw, 0, 30.4, 0, 22, 10, 14, 'pine', decals={f: [('rect', 0, k, 1, k + 0.04, '#9a7030') for k in (0.33, 0.66)] for f in ('north', 'south', 'east', 'west')})   # plank crate
    cb(tw, 0, 39.8, 0, 23, 1.2, 15, 'pine_d')                                            # lid rim
    st = m.bone('base_tc_stripe', [0, 15, 0], tw)
    cb(st, 0, 30.3, 0, 4.4, 10.2, 14.2, 'tc'); cb(st, 0, 39.7, 0, 4.4, 1.4, 15.2, 'tc')   # team stripe over the crate
    # bomber on top
    top = m.bone('top', [0, 41, 0], root)
    body = m.bone('top_body', [0, 41, 0], top)
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('top_leg_' + side, [sx * 1.5, 43, 0], top)
        cb(lg, sx * 1.6, 41.0, -1.0, 1.0, 1.0, 3.0, 'bone')                              # legs folded (sitting)
    for k, y in enumerate((42.2, 43.4, 44.6)):
        cb(body, 0, y, 0.4, 4.0 - k * 0.4, 0.7, 2.6, 'bone')                              # ribs
    cb(body, 0, 41.0, 1.4, 0.9, 5.0, 0.9, 'bone')                                        # spine
    hd = m.bone('top_head', [0, 46.5, 0], body)
    cb(hd, 0, 45.8, 0.4, 4.6, 4.2, 4.4, 'bone', faces={'north': 'void'})
    for sx in (1, -1):
        cb(hd, sx * 1.95, 46.4, -1.95, 0.7, 2.4, 0.3, 'bone')
    cb(hd, 0, 48.8, -1.95, 4.6, 1.2, 0.3, 'bone'); cb(hd, 0, 46.4, -1.95, 0.6, 0.8, 0.3, 'bone')
    cb(hd, 0, 45.0, -1.4, 4.0, 1.0, 3.4, 'bone', decals={'north': pix(["tktktk"], {'t': '#f6f4ea', 'k': '#3a3630'})})   # jaw + teeth
    cap = m.bone('top_tc_cap', [0, 50, 0], hd)
    cb(cap, 0, 49.4, 0.4, 5.2, 2.2, 5.0, 'cap')                                          # team leather cap
    cb(cap, 0, 48.6, 3.0, 5.2, 2.0, 0.6, 'cap')
    for sx in (1, -1):
        cb(cap, sx * 2.6, 46.2, 0.6, 0.5, 3.4, 2.8, 'cap')                                # ear flaps
        cb(hd, sx * 1.2, 48.4, -2.4, 1.8, 1.8, 0.6, 'brass', decals={'north': [('rect', 0.2, 0.2, 0.8, 0.8, '#bfe6f2')]})   # goggles
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('top_arm_' + side, [sx * 2.6, 45, 0], body)
        cb(a, sx * 2.6, 43.4, -1.0, 0.8, 0.8, 3.2, 'bone')                                 # arms hugging the bomb
        cb(a, sx * 2.4, 43.0, -2.8, 1.2, 1.2, 1.0, 'bone')
    bo = m.bone('top_bomb', [0, 45.5, -5], m.by_name('top_arm_r'))
    k = 0.6
    fz = m.bone('top_fuse', [0, 41.6 + 15.4 * k, -5.2], bo)
    def bs(x, y, z, w, mat):
        cb(fz, x * k, 41.6 + y * k, -5.2 + z * k, w * k, w * k, w * k, mat)
    bs(0, 14.6, 0, 2.2, 'flame'); bs(0, 15.0, 0, 1.4, 'spark'); bs(0, 15.3, 0, 0.7, 'core')
    for (dx, dy, dz) in ((1.5, 1.6, 0.5), (-0.8, 2.0, -0.7), (0.3, 2.5, 1.2), (1.9, 0.6, -1.0)):
        bs(dx, 15.0 + dy, dz, 0.45, 'spark')
    m.hitbox(2.0, 3.2)
    shade_pass(m, ('pine', 'stone', 'rope'))
    m.anim('idle', 2.0, 'loop', {'top_head': {'rotation': loop([[0, 12, 0], [0, -12, 0]], 2.0)},
                                 'top_fuse': {'scale': loop([[1, 1, 1], [1.4, 1.4, 1.4]], 0.3)}})
    m.anim('attack', 0.8, 'once', {'top_arm_r': {'rotation': [(0, [0, 0, 0]), (0.15, [40, 0, 0]), (0.3, [-70, 0, 0]), (0.8, [0, 0, 0])]},
                                   'top_arm_l': {'rotation': [(0, [0, 0, 0]), (0.15, [40, 0, 0]), (0.3, [-70, 0, 0]), (0.8, [0, 0, 0])]},
                                   'top_bomb': {'scale': [(0, [1, 1, 1]), (0.3, [1, 1, 1]), (0.32, [0, 0, 0]), (0.7, [0, 0, 0]), (0.8, [1, 1, 1])]},
                                   'top_body': {'rotation': [(0, [0, 0, 0]), (0.15, [-15, 0, 0]), (0.3, [20, 0, 0]), (0.8, [0, 0, 0])]}})
    m.anim('deploy', 0.8, 'once', {'root': {'position': [(0, [0, -30, 0]), (0.6, [0, 1, 0]), (0.8, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'base': {'position': [(0, [0, 0, 0]), (0.1, [0.6, 0, 0]), (0.2, [-0.6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 1.0, 'hold', {'base': {'scale': [(0, [1, 1, 1]), (0.6, [1.05, 0.5, 1.05]), (1.0, [1.1, 0.05, 1.1])]},
                                  'top': {'scale': [(0, [1, 1, 1]), (0.2, [0, 0, 0])]}})
    return m


