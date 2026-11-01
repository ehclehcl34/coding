def ice_spirit():
    """Ice Spirit: round snowball body, recessed cyan eyes, huge open grin with ice teeth, ice-crystal spikes, crystal arms/feet"""
    m = new_model('clash_ice_spirit')
    m.mats_({'snow': ('#f2f4f8', 'soft'), 'ice': ('#58c0f0', 'gem'), 'ice_l': ('#a8e4ff', 'gem'), 'mouth': ('#3a3aa0', 'plain'),
             'eye': ('#7ad8f8', 'glow'), 'tooth': ('#bce8ff', 'gem')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    cb(body, 0, 2.0, 0.6, 9.0, 9.0, 7.6, 'snow')                                        # snowball (back)
    cb(body, 0, 1.2, 0.6, 7.0, 10.6, 6.0, 'snow'); cb(body, 0, 3.2, 0.6, 10.4, 6.6, 6.0, 'snow')
    cb(body, 0, 8.2, -3.6, 9.0, 2.8, 1.0, 'snow')                                       # forehead
    for x, w in ((-3.9, 1.2), (0.0, 2.2), (3.9, 1.2)):
        cb(body, x, 6.6, -3.6, w, 1.6, 1.0, 'snow')
    for sx in (1, -1):
        cb(body, sx * 2.2, 6.6, -3.0, 2.2, 1.6, 0.2, 'eye')                               # recessed eyes
    cb(body, 0, 1.6, -3.6, 9.0, 1.4, 1.0, 'snow')                                       # chin
    for sx in (1, -1):
        cb(body, sx * 4.1, 3.0, -3.6, 0.8, 3.6, 1.0, 'snow')
    cb(body, 0, 3.0, -2.6, 7.4, 3.6, 0.2, 'mouth')                                      # big open mouth
    for x in (-2.7, -0.9, 0.9, 2.7):
        cb(body, x, 5.6, -3.4, 1.5, 1.0, 1.2, 'tooth')                                    # upper ice teeth
    for x in (-1.8, 0.0, 1.8):
        cb(body, x, 3.0, -3.4, 1.4, 0.9, 1.2, 'tooth')                                    # lower
    sp = m.bone('crystals', [0, 10, 0], body)
    for (x, y, z, w, h, r) in ((-3.0, 10.4, 0.6, 2.0, 4.0, ('z', 22.5)), (0.4, 10.8, 1.0, 2.4, 5.0, None), (3.2, 10.2, 0.4, 2.0, 3.6, ('z', -22.5)),
                               (-5.2, 6.0, 1.2, 1.8, 3.4, ('z', 45)), (5.4, 5.4, 1.4, 1.8, 3.2, ('z', -45)), (0.0, 7.0, 4.4, 2.0, 3.6, ('x', -45))):
        cb(sp, x, y, z, w, h, w, 'ice', rot=r, rot_origin=[x, y, z], decals={'north': [('rect', 0.2, 0.0, 0.4, 1, '#a8e4ff')]})
    for sx in (1, -1):
        a = m.bone('arm_' + ('r' if sx > 0 else 'l'), [sx * 5.0, 5, 0], body)
        cb(a, sx * 6.6, 4.4, -0.4, 3.0, 1.6, 1.8, 'ice'); cb(a, sx * 8.2, 4.8, -0.4, 1.2, 2.2, 1.6, 'ice_l')   # crystal arms
        lg = m.bone('leg_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 2, 0], root)
        cb(lg, sx * 1.8, 0, 0.4, 1.6, 2.6, 1.6, 'ice')                                     # crystal feet
    m.hitbox(0.6, 1.0)
    m.anim('idle', 0.8, 'loop', {'body': {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.8)}, 'crystals': {'rotation': loop([[0, 0, 3], [0, 0, -3]], 0.8)},
                                 'arm_r': {'rotation': loop([[0, 0, -10], [0, 0, 10]], 0.8)}, 'arm_l': {'rotation': loop([[0, 0, 10], [0, 0, -10]], 0.8)}})
    m.anim('walk', 0.4, 'loop', {'leg_r': {'rotation': loop([[-30, 0, 0], [30, 0, 0]], 0.4)}, 'leg_l': {'rotation': loop([[30, 0, 0], [-30, 0, 0]], 0.4)},
                                 'body': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 0.2)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.2, 0.85, 1.2]), (0.3, [0.8, 1.3, 0.8]), (0.5, [1, 1, 1])]}})
    common_tail(m)
    return m


