def bowler():
    """HQ vanilla-like CR Bowler: indigo gorilla-built giant, bald, heavy brow, big bulbous nose, pointy ears,
    big jaw + grin, huge forearms + fists, team arm bands, leather belt + pale loincloth, craggy boulder"""
    m = mk('clash_bowler')
    m.mats_({'skin': ('#6b69dc', 'skin'), 'skin_d': ('#5452bc', 'skin'), 'skin_l': ('#8583ea', 'skin'), 'nose': ('#9a86e6', 'skin'),
             'loin': ('#c9a97a', 'leather', {'stitch': False}), 'loin_d': ('#a88a5e', 'leather', {'stitch': False}),
             'belt': ('#5e4026', 'leather'), 'buckle': ('#b9a06a', 'metal'), 'wrap': ('#8a6a48', 'leather'),
             'band': ('#efefef', 'cloth'), 'stone': ('#8c8c8c', 'stone'), 'stone_d': ('#727272', 'stone'), 'stone_l': ('#a2a2a2', 'stone')})
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
    cb(body, 0, 10.2, 0, 12.4, 2.2, 7.6, 'belt')
    cb(body, 0, 10.0, -4.0, 3.0, 2.6, 0.6, 'buckle', decals={'north': [prect(2, 2, 5, 5, '#5e4026')]})
    cb(body, 0, 3.6, -3.9, 6.4, 6.8, 0.6, 'loin', decals={'north': [prect(0, 7, 7, 7, '#a88a5e'), px(2, 6, '#a88a5e'), px(6, 6, '#a88a5e')]})
    cb(body, 0, 4.2, 3.9, 7.0, 6.2, 0.6, 'loin_d')
    for sx in (1, -1):
        cb(body, sx * 5.2, 6.2, 0, 1.0, 4.0, 5.4, 'loin_d')                        # side flaps
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
    face = [px(1, 3, '#ffffff'), px(2, 3, '#2a8aff'), px(5, 3, '#2a8aff'), px(6, 3, '#ffffff'),
            px(1, 4, D), px(2, 4, D), px(5, 4, D), px(6, 4, D),
            px(1, 6, '#2a2858'), prect(2, 6, 5, 6, '#2a2858'), px(3, 6, '#f2efe0'), px(4, 6, '#f2efe0'), px(6, 5, '#2a2858'), px(6, 6, '#2a2858')]
    cb(hd, 0, 23.6, -2.4, 8.0, 8.0, 8.0, 'skin', decals={'north': face, 'up': [prect(2, 2, 5, 5, '#7a78e2')]})
    cb(hd, 0, 28.4, -6.7, 8.4, 1.3, 1.2, 'skin_d')                                 # heavy brow ridge
    cb(hd, 0, 22.8, -3.2, 8.6, 2.4, 7.6, 'skin', decals={'north': [prect(1, 0, 6, 0, '#2a2858')]})   # big jaw
    cb(hd, 0, 22.4, -7.0, 4.4, 1.6, 0.8, 'skin_l')                                 # chin
    cb(hd, 0, 25.6, -7.2, 2.0, 2.8, 1.6, 'nose')                                   # nose bridge
    cb(hd, 0, 24.6, -7.9, 3.2, 2.2, 2.0, 'nose', decals={'down': [px(2, 3, D), px(5, 3, D)]})   # bulbous tip
    for sx in (1, -1):
        cb(hd, sx * 4.5, 25.8, -2.0, 1.0, 3.0, 2.6, 'skin')                         # big pointy ears
        cb(hd, sx * 4.7, 28.6, -1.0, 1.0, 2.6, 1.8, 'skin', decals={'east': [prect(2, 2, 5, 7, '#9a86e6')], 'west': [prect(2, 2, 5, 7, '#9a86e6')]})
        cb(hd, sx * 4.9, 31.0, 0.0, 0.9, 1.6, 1.0, 'skin')                          # ear tip
        cb(hd, sx * 3.0, 24.2, -6.5, 1.4, 1.2, 0.4, 'skin_l')                       # cheeks
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
        cb(a, x, 3.2, -0.2, 7.0, 4.6, 7.0, 'skin_d',                                # huge fist
           decals={'north': [prect(0, 1, 7, 1, D), px(2, 3, D), px(4, 3, D), px(6, 3, D)]})
        cb(a, x, 7.4, 0, 7.2, 1.2, 7.2, 'wrap')                                    # wrist wrap
        cb(a, x - sx * 3.0, 5.0, -2.4, 1.4, 2.2, 1.6, 'skin_d')                     # thumb
    # craggy boulder (held at chest by both hands via the arm pose)
    bo = m.bone('boulder', [0, 13, -9], m.by_name('arm_r'))
    cxb, cyb, czb, R = -9.6 + 9.6, 8.6, -9.0, 5.8
    n = 7
    hgt = 2 * R / n
    for i in range(n):
        yc = -R + hgt * (i + 0.5)
        rr = max(1.4, (R * R - yc * yc) ** 0.5)
        mat = 'stone' if i % 2 else 'stone_d'
        cb(bo, cxb, cyb + yc - hgt / 2, czb, 2 * rr, hgt, 1.5 * rr, mat)
        cb(bo, cxb, cyb + yc - hgt / 2, czb, 1.5 * rr, hgt, 2 * rr, mat)
    for (dx, dy, dz, w) in ((3.4, 2.0, -3.0, 2.6), (-3.6, -1.0, -2.6, 2.4), (0.6, 4.4, -1.4, 2.8),
                            (-1.8, -3.6, -3.4, 2.2), (4.2, -2.0, 1.4, 2.0), (-4.0, 2.6, 2.0, 2.2)):
        cb(bo, cxb + dx, cyb + dy - w / 2, czb + dz, w, w * 0.8, w, 'stone_l')      # craggy chunks
    shrink(m, 1.55)
    m.hitbox(1.8, 3.2)
    m.anim('idle', 2.4, 'loop', {'arm_r': {'rotation': loop([[-40, 0, 10], [-42, 0, 10]], 2.4)}, 'arm_l': {'rotation': loop([[-40, 0, -10], [-42, 0, -10]], 2.4)},
                                 'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 2.4)},
                                 'body': {'rotation': loop([[6, 0, 0], [8, 0, 0]], 2.4)}})
    w = walk_cycle(1.2, 25, arms=None)
    w['arm_r'] = {'rotation': [(0, [-40, 0, 10]), (1.2, [-40, 0, 10])]}
    w['arm_l'] = {'rotation': [(0, [-40, 0, -10]), (1.2, [-40, 0, -10])]}
    w['body'] = {'rotation': loop([[8, 0, -3], [8, 0, 3]], 1.2)}
    m.anim('walk', 1.2, 'loop', w)
    sw = [(0, [-40, 0, 10]), (0.25, [40, 0, 10]), (0.4, [-30, 0, 10]), (0.55, [-70, 0, 10]), (0.9, [-40, 0, 10])]
    m.anim('attack', 0.9, 'once', {'arm_r': {'rotation': sw}, 'arm_l': {'rotation': [(t, [v[0], 0, -10]) for t, v in sw]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-5, 15, 0]), (0.4, [15, 0, 0]), (0.9, [0, 0, 0])]},
                                   'boulder': {'scale': [(0, S(1)), (0.4, S(1)), (0.42, S(0.01)), (0.78, S(0.01)), (0.88, S(1))]}})
    troop_tail(m)
    return m


