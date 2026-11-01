def fire_spirit():
    """HQ vanilla-like Fire Spirit: charred dark round body with glowing cracks, big recessed glowing eyes,
    heavy brow ridge, tall layered flame (red -> orange -> yellow), stubby glowing-tipped limbs"""
    m = new_model('clash_fire_spirit')
    m.mats_({'char': ('#4a2416', 'soft'), 'char_d': ('#2e140c', 'soft'), 'glow': ('#ff9a30', 'glow'), 'eye': ('#fff4c8', 'glow'),
             'iris': ('#ffb040', 'glow'), 'f1': ('#e8401a', 'glow'), 'f2': ('#ff8a20', 'glow'), 'f3': ('#ffd050', 'glow'), 'void': ('#1a0a06', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    cracks = [('rect', 0.2, 0.3, 0.22, 0.7, '#ff7a20'), ('rect', 0.22, 0.68, 0.4, 0.7, '#ff7a20'), ('rect', 0.7, 0.2, 0.72, 0.5, '#ff7a20')]
    G = {f: [('lerp', '#7a3a1a', 0.0, 0.5, 'y')] + cracks for f in ('south', 'east', 'west')}
    cb(body, 0, 2.4, 0.5, 8.0, 7.0, 6.0, 'char', decals=G)                              # body (back part)
    cb(body, 0, 1.8, 0.6, 6.6, 8.4, 5.4, 'char'); cb(body, 0, 3.0, 0.6, 8.8, 5.0, 5.4, 'char')
    cb(body, 0, 2.4, -3.0, 8.0, 4.2, 1.0, 'char', decals={'north': [('lerp', '#2e140c', 0.0, 0.6, 'y')]})   # lower face
    cb(body, 0, 9.0, -3.0, 8.0, 0.4, 1.0, 'char')
    for x, w in ((-3.55, 0.9), (0.0, 1.4), (3.55, 0.9)):
        cb(body, x, 6.6, -3.0, w, 2.4, 1.0, 'char')
    for sx in (1, -1):
        cb(body, sx * 1.9, 6.6, -2.4, 2.4, 2.4, 0.2, 'eye')                               # recessed glowing eyes
        cb(body, sx * 1.9 + sx * 0.3, 7.0, -2.6, 1.0, 1.4, 0.2, 'iris')                    # amber pupil looking aside
        cb(body, sx * 2.0, 9.0, -3.7, 3.0, 1.0, 1.4, 'char_d')                            # heavy brow ridge
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.2, 6, 0], body)
        cb(a, sx * 5.0, 3.8, 0, 1.8, 2.8, 1.8, 'char'); cb(a, sx * 5.0, 3.2, 0, 1.6, 0.8, 1.6, 'glow')   # arms with glowing tips
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0.6, 0, 2.4, 1.8, 2.6, 'char_d'); cb(lg, sx * 1.8, 0, 0, 2.2, 0.6, 2.4, 'glow')
    cb(body, 0, 9.4, 0.6, 8.2, 0.6, 6.0, 'char_d')                                       # charred crown
    fl = m.bone('flame', [0, 10, 0], body)                                              # layered flame
    for (x, z, h, w, mat) in ((0, 0.6, 3.0, 7.0, 'f1'), (-1.8, 0.6, 5.0, 2.6, 'f1'), (1.6, 0.0, 6.2, 2.8, 'f1'), (0.0, 1.8, 4.0, 2.6, 'f1'),
                              (-0.4, 0.2, 7.0, 2.0, 'f2'), (2.2, 1.2, 4.6, 1.8, 'f2'), (-2.4, -0.4, 3.6, 1.6, 'f2'),
                              (0.4, -0.2, 8.4, 1.2, 'f3'), (-1.6, 0.8, 5.6, 1.0, 'f3'), (2.6, 0.4, 6.0, 0.8, 'f3')):
        cb(fl, x, 10.0, z, w, h, w * 0.85, mat)
    for (x, y, z) in ((1.0, 19.4, 0.0), (-1.6, 16.8, 0.8), (2.8, 17.2, 0.6)):
        cb(fl, x, y, z, 0.6, 0.8, 0.6, 'f3')                                              # embers
    m.hitbox(0.6, 1.0)
    shade_pass(m, ('char',))
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.6, 0]], 0.8)},
                                 'flame': {'scale': loop([[1, 1, 1], [1.05, 1.15, 1.05], [0.97, 0.95, 0.97]], 0.3), 'rotation': loop([[0, 0, 4], [0, 0, -4]], 0.4)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.2)}, 'flame': {'rotation': loop([[12, 0, 0], [18, 0, 0]], 0.2)},
                                 'arm_r': {'rotation': loop([[20, 0, 0], [-20, 0, 0]], 0.4)}, 'arm_l': {'rotation': loop([[-20, 0, 0], [20, 0, 0]], 0.4)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]},
                                   'flame': {'scale': [(0, [1, 1, 1]), (0.25, [1.6, 1.8, 1.6]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m


