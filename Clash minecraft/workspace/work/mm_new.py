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
    rb(hm, 0, 15.8, -0.4, 7.6, 9.0, 7.4, 'steel', r=0.9, decals={'north': [('rect', 0.47, 0, 0.53, 0.35, '#ccd2d8')]})   # tall rounded bucket helm
    cb(hm, 0, 18.8, -4.2, 6.2, 2.8, 0.2, 'void')                                              # wide visor slot
    cb(hm, 0, 16.6, -4.2, 1.4, 2.4, 0.2, 'void')                                              # mouth slot under the bar
    cb(hm, 0, 18.4, -4.35, 1.2, 3.6, 0.5, 'steel_l')                                          # centre bar
    cb(hm, 0, 21.6, -4.35, 7.0, 0.8, 0.5, 'steel_l')                                          # brow band
    for (x, y) in ((-2.8, 22.8), (2.8, 22.8), (-2.8, 16.0), (2.8, 16.0)):
        cb(hm, x, y, -4.35, 0.7, 0.7, 0.4, 'steel_l')                                          # rivets
    ey = m.bone('ts_eyes', [0, 19, -4], hm)
    for sx in (1, -1):
        cb(ey, sx * 1.9, 19.4, -4.4, 1.6, 1.2, 0.2, 'soft')                                     # glowing eyes in the slot
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
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 2.4, 16.6, 3.6], body)
        ro = dict(rot=('z', sx * 45), rot_origin=[sx * 2.4, 16.6, 3.6])
        tw = m.bone('ts_wing_' + side, [sx * 2.4, 16.6, 3.6], w)
        cb(tw, sx * 5.8, 16.4, 3.8, 7.6, 1.0, 1.0, 'soft', **ro)                                 # wing bone
        for (x0, x1, h) in ((2.4, 4.8, 3.6), (4.8, 7.2, 4.4), (7.2, 9.4, 3.4)):
            cb(tw, sx * (x0 + x1) / 2, 16.6 - h, 3.9, x1 - x0, h, 0.3, 'soft',
               decals={f: [('rect', 0.85, 0, 1, 1, '#b0b0b0'), ('rect', 0, 0.85, 1, 1, '#b0b0b0'), ('shade', 0, 0, 1, 0.5, 1.05)] for f in ('north', 'south')}, **ro)
    m.hitbox(1.0, 1.6)
    shade_pass(m, ('steel',))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -10, -a], [0, 10, a * 0.5]], L)}, 'wing_l': {'rotation': loop([[0, 10, a], [0, -10, -a * 0.5]], L)}}
    hang = {'arm_r': {'rotation': loop([[-20, 0, 25], [-24, 0, 27]], 1.0)}, 'arm_l': {'rotation': loop([[-20, 0, -25], [-24, 0, -27]], 1.0)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 1.0)}}; idle.update(flap(0.5, 35)); idle.update(hang)
    m.anim('idle', 1.0, 'loop', idle)
    walk = dict(idle); walk['body'] = {'rotation': loop([[15, 0, 0], [15, 0, 0]], 0.6)}; walk.update(flap(0.3, 40))
    m.anim('walk', 0.6, 'loop', walk)
    m.anim('attack', 0.75, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 25]), (0.25, [-140, 0, 10]), (0.4, [-30, 0, 0]), (0.75, [-20, 0, 25])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-10, 10, 0]), (0.4, [15, -10, 0]), (0.75, [0, 0, 0])]}})
    common_tail(m)
    return m


