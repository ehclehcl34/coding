def bats():
    """HQ vanilla-like CR Bat: chubby dark-purple body, huge pointed ears, team-coloured glowing eyes,
    little fangs, segmented membrane wings with finger bones, tiny clawed feet"""
    m = new_model('clash_bats')
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
        e = m.bone('tc_eye_' + ('r' if sx > 0 else 'l'), [sx * 1.5, 10, -2.7], hd)
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


