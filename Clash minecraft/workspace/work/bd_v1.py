def baby_dragon():
    """HQ vanilla-like CR Baby Dragon: pudgy upright green body + pale belly bands, big head with wide open mouth
    (teeth, tongue out), bulging side eyes, top horn, orange bat wings, tan paws/feet, spiked tail, team neck band"""
    m = new_model('clash_baby_dragon')
    m.mats_({'grn': ('#5ec83a', 'skin'), 'grn_d': ('#45a42a', 'skin'), 'belly': ('#a6e27a', 'skin'), 'tan': ('#d9935a', 'skin'),
             'wing': ('#c8743e', 'leather', {'stitch': False}), 'wing_m': ('#e6a466', 'leather', {'stitch': False}),
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
           decals={'north': pix(["k.k.k", "....."], {'k': '#a86a3a'})})              # tan foot + claws
        ar = m.bone('f%s_leg' % side, [sx * 5.0, 14.0, -1.6], body)                   # little arm
        cb(ar, sx * 5.4, 10.4, -1.8, 2.6, 4.4, 2.8, 'grn')
        cb(ar, sx * 5.4, 8.6, -2.2, 3.0, 2.0, 3.2, 'tan', decals={'north': pix(["k.k", "..."], {'k': '#a86a3a'})})   # paw
    # head
    hd = m.bone('head', [0, 16, -1], body)
    cb(hd, 0, 16.2, -1.6, 9.4, 7.2, 8.4, 'grn')                                     # skull
    cb(hd, 0, 19.0, -8.8, 8.2, 4.0, 6.0, 'grn',                                     # big snout
       decals={'north': pix(["........", ".kk..kk.", "........", "........"], {'k': '#2a5a1a'})})   # nostrils
    cb(hd, 0, 23.2, -2.4, 2.0, 2.6, 2.0, 'tan')                                     # horn
    cb(hd, 0, 25.6, -2.4, 1.2, 1.0, 1.2, 'tan')
    for i in range(7):                                                              # upper teeth
        cb(hd, -3.0 + i * 1.0, 18.2, -11.4 + (0 if i in (0, 6) else 0), 0.7, 0.9, 0.7, 'tooth')
    for sx in (1, -1):
        cb(hd, sx * 3.7, 18.2, -8.0, 0.7, 0.9, 4.6, 'tooth', decals={'east': pix(["k.k.k."], {'k': '#d0ccc0'}), 'west': pix(["k.k.k."], {'k': '#d0ccc0'})})
        cb(hd, sx * 4.9, 20.0, -4.6, 1.4, 2.6, 2.6, 'eye',                            # bulging side eyes
           decals={'north': pix(["...", ".kk", ".kk"], {'k': '#2a1a10'}), 'east' if sx > 0 else 'west': pix(["...", "kk.", "kk."], {'k': '#2a1a10'})})
        cb(hd, sx * 4.9, 22.4, -4.6, 1.5, 0.6, 2.8, 'grn_d')                          # eyelid
        ear = m.bone('ear_' + ('r' if sx > 0 else 'l'), [sx * 4.6, 21, 1.0], hd)
        cb(ear, sx * 5.0, 21.0, 1.4, 0.8, 2.6, 2.4, 'tan')                           # little ear frills
    cb(hd, 0, 17.0, -6.0, 7.2, 1.4, 6.4, 'mouth')                                    # mouth interior
    jaw = m.bone('jaw', [0, 17.4, -2.0], hd)                                         # lower jaw, open
    cb(jaw, 0, 14.6, -6.2, 8.4, 2.6, 7.6, 'grn')
    cb(jaw, 0, 17.2, -6.0, 7.0, 0.3, 6.8, 'mouth')
    for sx in (1, -1):
        cb(jaw, sx * 3.6, 17.2, -6.8, 0.7, 0.9, 5.0, 'tooth', decals={'east': pix(["k.k.k."], {'k': '#d0ccc0'}), 'west': pix(["k.k.k."], {'k': '#d0ccc0'})})
    tg = m.bone('tongue', [0, 17.4, -6.0], jaw)
    cb(tg, 0, 17.2, -8.8, 2.6, 0.8, 5.8, 'tongue', decals={'up': pix(["..", "k.", "..", ".k"], {'k': '#c45a68'})})
    cb(tg, 0, 14.6, -12.0, 2.6, 3.4, 0.8, 'tongue')                                 # tongue hanging over the chin
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
        cb(t, 0, 3.0 + (3.6 if z == 6.0 else 2.6 if z == 9.0 else 1.8), z, 0.8, h, 1.4, 'tan')   # back spikes
    m.hitbox(1.2, 1.6)
    shade_pass(m, ('grn', 'tan'))
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


