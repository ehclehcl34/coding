def electro_spirit():
    """HQ vanilla-like Electro Spirit: round blue-violet flame body fading pink at the flame tips, big toothy grin,
    glowing eyes, stubby arms/legs, crackling electric zigzags"""
    m = new_model('clash_electro_spirit')
    m.mats_({'body': ('#6a6ae0', 'soft'), 'body_d': ('#5050c0', 'soft'), 'flame': ('#a07ae8', 'soft'), 'tip': ('#d890e8', 'soft'),
             'mouth': ('#2a1a40', 'plain'), 'tooth': ('#f6f4f0', 'bone'), 'eye': ('#f0e8ff', 'glow'), 'zap': ('#e8f4ff', 'glow')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    grad = lambda c, a0, a1: [('lerp', c, a0, a1, 'y')]
    cb(body, 0, 2.4, 0, 8.0, 7.0, 7.0, 'body', decals={f: grad('#8a7ae8', 0.6, 0.0) for f in ('north', 'south', 'east', 'west')})   # round body
    cb(body, 0, 1.8, 0, 6.6, 8.4, 5.6, 'body')
    cb(body, 0, 3.0, 0, 8.8, 5.0, 5.8, 'body')
    fl = m.bone('flame', [0, 10, 0], body)                                              # flame top, violet -> pink tips
    cb(fl, 0, 9.0, 0.2, 6.4, 2.6, 5.6, 'flame', decals={f: grad('#6a6ae0', 0.0, 0.6) for f in ('north', 'south', 'east', 'west')})
    for (x, z, h, w) in ((-1.6, 0.4, 3.2, 2.4), (1.4, -0.6, 4.2, 2.6), (0.2, 1.4, 2.6, 2.2), (2.6, 1.0, 2.0, 1.6)):
        cb(fl, x, 11.4, z, w, h, w, 'tip', decals={f: grad('#a07ae8', 1.0, 0.0) for f in ('north', 'south', 'east', 'west')})
    cb(fl, 1.6, 15.4, -0.6, 1.2, 1.4, 1.2, 'tip')
    cb(body, 0, 3.4, -3.55, 6.0, 3.2, 0.3, 'mouth')                                     # big grin
    for k, x in enumerate((-2.2, -0.75, 0.75, 2.2)):
        cb(body, x, 5.6, -3.7, 1.2, 1.0, 0.3, 'tooth')                                   # upper teeth
    for x in (-1.5, 0.0, 1.5):
        cb(body, x, 3.4, -3.7, 1.1, 0.9, 0.3, 'tooth')                                   # lower teeth
    for sx in (1, -1):
        cb(body, sx * 1.8, 7.0, -3.6, 1.8, 1.6, 0.3, 'eye', decals={'north': [('rect', 0.3, 0.2, 0.7, 0.8, '#ffffff')]})   # glowing eyes
        cb(body, sx * 1.8, 8.6, -3.55, 2.0, 0.5, 0.3, 'body_d')                         # brows
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.2, 6, 0], body)
        cb(a, sx * 5.0, 3.6, 0, 1.8, 2.8, 1.8, 'body')                                   # stubby arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0, 0, 2.4, 2.4, 2.6, 'body_d')                                  # stubby legs
    zp = m.bone('zaps', [0, 6, 0], body)                                                 # electric zigzags (pulse)
    for (x, y, z, w, h, d) in ((-4.8, 8.0, -1.0, 0.4, 2.0, 0.4), (-5.2, 9.6, -0.6, 0.4, 0.4, 1.6), (4.6, 10.6, 0.8, 0.4, 2.2, 0.4),
                               (5.0, 12.4, 0.2, 0.4, 0.4, 1.4), (-2.0, 15.0, 0.6, 1.6, 0.4, 0.4), (-2.6, 15.4, 0.4, 0.4, 1.4, 0.4)):
        cb(zp, x, y, z, w, h, d, 'zap')
    m.hitbox(0.6, 1.0)
    shade_pass(m, ('body',))
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.6, 0]], 0.8), 'scale': loop([[1, 1, 1], [1.04, 0.97, 1.04]], 0.8)},
                                 'flame': {'rotation': loop([[0, 0, 4], [0, 0, -4]], 0.4)}, 'zaps': {'scale': loop([[1, 1, 1], [0, 0, 0], [1.2, 1.2, 1.2]], 0.3)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.2)}, 'flame': {'rotation': loop([[10, 0, 0], [16, 0, 0]], 0.2)},
                                 'arm_r': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], 0.4)}, 'arm_l': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], 0.4)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]},
                                   'zaps': {'scale': [(0, [1, 1, 1]), (0.25, [2.2, 2.2, 2.2]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m


