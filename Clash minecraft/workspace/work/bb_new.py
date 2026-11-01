def barbarian():
    """HQ vanilla-like Barbarian: gold helmet + cheek guards, blond horseshoe moustache, big nose, muscular bare torso,
    spiked wristbands, team belt with shield buckle, brown kilt, sandals, sword"""
    m = new_model('clash_barbarian')
    m.mats_({'skin': ('#e8a878', 'skin'), 'skin_d': ('#c88a5e', 'skin'), 'gold': ('#e8b830', 'metal'), 'gold_d': ('#b88a20', 'metal'),
             'hair': ('#f0c848', 'hair'), 'kilt': ('#6a4a34', 'leather', {'stitch': False}), 'belt': ('#efefef', 'leather'),
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
    hair = m.bone('hair', [0, 26, 0], hd)                                                 # gold helmet
    cb(hair, 0, 25.6, -0.4, 8.2, 3.0, 8.0, 'gold')
    cb(hair, 0, 28.6, -0.4, 6.8, 0.8, 6.6, 'gold')
    cb(hair, 0, 25.2, -4.3, 8.2, 1.4, 0.6, 'gold_d')                                     # brow rim
    cb(hair, 0, 26.0, -0.4, 1.0, 3.6, 8.4, 'gold_d')                                     # centre ridge
    cb(hair, 0, 21.2, 3.4, 8.2, 4.6, 1.0, 'gold')                                        # neck guard
    for sx in (1, -1):
        cb(hair, sx * 4.0, 20.2, -1.6, 0.9, 5.4, 4.0, 'gold')                              # cheek guards
    br = m.bone('beard', [0, 20.8, -3.6], hd)                                             # horseshoe moustache
    cb(br, 0, 21.6, -4.3, 5.8, 1.4, 1.2, 'hair')
    for sx in (1, -1):
        cb(br, sx * 2.6, 17.8, -4.2, 1.3, 4.6, 1.2, 'hair')
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
    cb(sw, 6.4, 8.8, 0, 0.9, 0.9, 3.0, 'grip')                                           # grip across the fist
    cb(sw, 6.4, 8.6, -1.9, 1.2, 1.2, 0.8, 'gold')                                        # guard
    cb(sw, 6.4, 8.9, 1.9, 1.0, 1.0, 0.8, 'gold')                                         # pommel
    cb(sw, 6.4, 8.9, -1.9, 3.4, 0.7, 0.7, 'gold')                                        # cross-guard
    cb(sw, 6.4, 8.8, -7.4, 1.6, 0.6, 10.0, 'steel', decals={'up': [('rect', 0.45, 0, 0.55, 1, '#d8dde2')]})   # blade
    cb(sw, 6.4, 8.9, -12.8, 0.8, 0.4, 1.0, 'steel')                                      # tip
    m.hitbox(0.9, 1.9)
    shade_pass(m, ('skin', 'kilt'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-20, 0, 4], [-24, 0, 6]], 2.0)}})
    mc_walk(m, 0.7, 30, arm_r=False, extra={'arm_r': {'rotation': loop([[-20, 0, 4], [-30, 0, 4]], 0.7)}})
    m.anim('attack', 0.55, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 4]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, 0]), (0.55, [-20, 0, 4])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-6, 10, 0]), (0.35, [10, -10, 0]), (0.55, [0, 0, 0])]}})
    common_tail(m)
    return m


