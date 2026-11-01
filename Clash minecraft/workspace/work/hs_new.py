def heal_spirit():
    """Heal Spirit: glowing yellow gummy body with a pointy tip, recessed orange eye sockets with glowing pupils,
    huge open mouth, one buck tooth, big red tongue hanging out, stubby arms and legs"""
    m = new_model('clash_heal_spirit')
    m.mats_({'y': ('#f8d838', 'soft'), 'y_d': ('#e0b020', 'soft'), 'sock': ('#f0a020', 'glow'), 'pupil': ('#fff4a0', 'glow'),
             'mouth': ('#a0401a', 'plain'), 'tongue': ('#e04838', 'skin'), 'tooth': ('#fff8e0', 'bone')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 4, 0], root)
    cb(body, 0, 2.0, 0.6, 9.0, 9.4, 7.0, 'y')                                          # body (back)
    cb(body, 0, 1.4, 0.6, 7.4, 10.8, 5.6, 'y'); cb(body, 0, 3.0, 0.6, 10.2, 7.0, 5.6, 'y')
    cb(body, 1.4, 12.2, 0.6, 2.4, 1.6, 2.4, 'y'); cb(body, 2.2, 13.8, 0.6, 1.2, 1.2, 1.2, 'y')   # pointy tip
    cb(body, 0, 9.4, -3.3, 9.0, 1.6, 1.0, 'y')                                          # forehead
    for x, w in ((-4.15, 0.7), (0.0, 1.4), (4.15, 0.7)):
        cb(body, x, 7.0, -3.3, w, 2.4, 1.0, 'y')
    for sx in (1, -1):
        cb(body, sx * 2.25, 7.0, -2.9, 3.1, 2.4, 0.2, 'sock')                              # recessed orange sockets
        cb(body, sx * 2.25, 7.6, -3.1, 1.2, 1.2, 0.2, 'pupil')                             # glowing pupils
    cb(body, 0, 1.8, -3.3, 9.0, 1.4, 1.0, 'y')                                          # chin
    for sx in (1, -1):
        cb(body, sx * 4.1, 3.2, -3.3, 0.8, 3.8, 1.0, 'y')
    cb(body, 0, 3.2, -2.9, 7.4, 3.8, 0.2, 'mouth')                                      # big open mouth
    cb(body, -1.6, 6.0, -3.3, 1.4, 1.0, 1.0, 'tooth')                                   # buck tooth
    tg = m.bone('tongue', [1.0, 3.6, -3.4], body)
    cb(tg, 1.0, 3.2, -4.2, 3.4, 0.8, 2.6, 'tongue', decals={'up': [('rect', 0.48, 0, 0.52, 1, '#b83020')]})
    cb(tg, 1.0, 0.8, -5.4, 3.4, 3.0, 0.8, 'tongue', decals={'north': [('rect', 0.48, 0, 0.52, 0.8, '#b83020')]})   # tongue hanging out
    for sx in (1, -1):
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 4.8, 7, 0], body)
        cb(a, sx * 6.0, 5.6, 0.4, 2.4, 3.0, 2.2, 'y'); cb(a, sx * 7.0, 7.2, 0.4, 1.4, 1.6, 1.6, 'y')   # waving arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.9, 2, 0], root)
        cb(lg, sx * 1.9, 0, 0.4, 2.8, 2.6, 3.0, 'y_d')
    m.hitbox(0.7, 0.9)
    shade_pass(m, ('y',))
    m.anim('idle', 1.0, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.8, 0]], 1.0)}, 'tongue': {'rotation': loop([[0, 0, 0], [12, 0, 0]], 0.5)},
                                 'arm_r': {'rotation': loop([[0, 0, -15], [0, 0, 15]], 1.0)}, 'arm_l': {'rotation': loop([[0, 0, 15], [0, 0, -15]], 1.0)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 0.2)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m


