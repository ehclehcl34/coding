def electro_wizard():
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
        cb(a, sx * 6, 15, 0, 4, 7, 4, 'robe'); cb(a, sx * 6, 12, 0, 3.6, 3, 3.6, 'skin')
        cb(a, sx * 6, 13.6, 0, 4.2, 1.4, 4.2, 'robe')                                       # wristband
        z = m.bone('zap_' + side, [sx * 6, 11, 0], a)
        for (dx, y, dz, w, h, d) in ((0.8, 10.0, -1.4, 0.4, 2.2, 0.4), (1.4, 9.0, -0.8, 0.4, 0.4, 1.6), (-1.2, 9.4, 1.0, 0.4, 2.0, 0.4),
                                     (0.0, 8.0, -2.4, 0.4, 0.4, 2.0), (-0.6, 7.2, 0.6, 1.6, 0.4, 0.4)):
            cb(z, sx * 6 + dx, y, dz, w, h, d, 'zap')
    m.hitbox(0.9, 2.1)
    shade_pass(m, ('skin', 'robe'))
    zl = {'zap_r': {'scale': loop([[1, 1, 1], [0.2, 0.2, 0.2], [1.3, 1.3, 1.3]], 0.25)}, 'zap_l': {'scale': loop([[0.6, 0.6, 0.6], [1.3, 1.3, 1.3], [0, 0, 0]], 0.25)}}
    mc_idle(m, 2.0, extra=dict(zl)); mc_walk(m, 0.7, 30, extra=dict(zl))
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.2, [-90, 15, 0]), (0.5, [-90, 15, 0]), (0.6, [0, 0, 0])]},
                                   'arm_l': {'rotation': [(0, [0, 0, 0]), (0.2, [-90, -15, 0]), (0.5, [-90, -15, 0]), (0.6, [0, 0, 0])]},
                                   'zap_r': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.6, [1, 1, 1])]}, 'zap_l': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.6, [1, 1, 1])]}})
    common_tail(m)
    return m


