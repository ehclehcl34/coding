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
    cb(hd, 0, 17.4, 0.2, 7.2, 6.4, 6.6, 'bone', faces={'north': 'void'})                 # big skull (front = mouth cavity)
    cb(hd, 0, 21.0, -3.2, 7.2, 2.8, 0.4, 'bone')                                         # face plate above the mouth
    cb(hd, 0, 19.8, -3.3, 6.0, 1.2, 0.5, 'tooth', decals={'north': pix(["tktktkt"], {'t': '#f8f6ee', 'k': '#4a4238'})})   # upper teeth
    cb(hd, 0, 16.4, -1.0, 6.4, 1.6, 5.0, 'bone')                                         # lower jaw, dropped open
    cb(hd, 0, 18.0, -3.4, 5.4, 0.9, 0.5, 'tooth', decals={'north': pix(["tktktk"], {'t': '#f8f6ee', 'k': '#4a4238'})})   # lower teeth
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
    cb(gg, 0, 21.6, 0.4, 8.0, 1.0, 7.6, 'strap')                                         # strap round the cap
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.6
        a = m.bone('arm_' + side, [x, 16.0, 0], body)
        cb(a, x, 12.4, 0, 0.9, 3.6, 0.9, 'bone')
        cb(a, x, 11.8, 0, 1.3, 1.0, 1.3, 'bone_d')                                         # elbow
        cb(a, x, 9.0, 0, 0.8, 3.0, 0.8, 'bone')
        cb(a, x, 8.8, 0, 2.2, 0.8, 2.2, 'glove')                                          # glove cuff
        cb(a, x, 6.8, -0.2, 2.0, 2.2, 2.0, 'glove', decals={'north': pix(["k.k.", "...."], {'k': '#5a3018'})})   # leather glove
    bh = m.bone('bomb_hand', [3.6, 6.0, -2.4], m.by_name('arm_r'))                       # bomb body injected from the user's model
    k = 0.6
    fz = m.bone('fuse', [3.6, 2.4 + 15.4 * k, -2.6], bh)
    def bs(x, y, z, w, mat):
        cb(fz, 3.6 + x * k, 2.4 + y * k, -2.6 + z * k, w * k, w * k, w * k, mat)
    bs(0, 14.6, 0, 2.2, 'flame'); bs(0, 15.0, 0, 1.4, 'spark'); bs(0, 15.3, 0, 0.7, 'core')
    for (dx, dy, dz) in ((1.5, 1.6, 0.5), (-0.8, 2.0, -0.7), (0.3, 2.5, 1.2), (1.9, 0.6, -1.0)):
        bs(dx, 15.0 + dy, dz, 0.45, 'spark')
    m.bone('tc_scarf', [0, 17.2, 0], body)
    m.hitbox(0.7, 1.6)
    hold = {'arm_r': {'rotation': loop([[-20, 0, 8], [-22, 0, 8]], 2.0)}, 'fuse': {'scale': loop([[1, 1, 1], [1.4, 1.4, 1.4]], 0.3)}}
    mc_idle(m, 2.0, extra=hold)
    mc_walk(m, 0.6, 30, arm_r=False, extra=hold)
    m.anim('attack', 0.7, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 8]), (0.2, [40, 0, 8]), (0.35, [-150, 0, 0]), (0.7, [-20, 0, 8])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-10, 15, 0]), (0.35, [15, -10, 0]), (0.7, [0, 0, 0])]},
                                   'bomb_hand': {'scale': [(0, [1, 1, 1]), (0.35, [1, 1, 1]), (0.37, [0, 0, 0]), (0.62, [0, 0, 0]), (0.7, [1, 1, 1])]}})
    common_tail(m)
    shade_pass(m, ('bone', 'cap', 'glove'))
    return m


