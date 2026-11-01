def _rock_golem(name, S, hb):
    """HQ vanilla-like Golem: hunched stack of faceted boulders, small head sunk between huge shoulders,
    glowing magenta eyes under a heavy brow, long rock arms with big boulder fists, short stubby legs, team rune on the chest"""
    m = new_model(name)
    m.mats_({'rock': ('#9a9288', 'stone'), 'rock_d': ('#7a7268', 'stone'), 'rock_l': ('#b0a89c', 'stone'), 'eye': ('#ff60e8', 'glow'),
             'void': ('#2a2420', 'plain'), 'rune': ('#efefef', 'glow')})
    r = Rig(m, S); B = r.box
    root = m.bone('root', [0, 0, 0])
    def boulder(bone, x, y, z, w, h, d, mat='rock'):
        B(bone, x, y + 0.6, z, w, h - 1.2, d, mat); B(bone, x, y, z, w - 1.2, h, d - 1.2, mat)   # chamfered rock chunk
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.4
        lg = r.bone('leg_' + side, [x, 8, 0.6], root)
        boulder(lg, x, 3.0, 0.6, 4.6, 5.0, 4.6, 'rock_d')
        boulder(lg, x, 0, 0.0, 5.4, 3.2, 6.2)                                              # stubby rock feet
    body = r.bone('body', [0, 8, 0], root)
    boulder(body, 0, 7.0, 1.2, 9.0, 5.4, 7.0, 'rock_d')                                   # hips
    boulder(body, 0, 11.6, 0.4, 14.0, 8.0, 9.6)                                           # massive chest
    boulder(body, -3.6, 18.4, 1.6, 7.0, 4.0, 7.4, 'rock_l'); boulder(body, 3.8, 18.6, 1.0, 7.0, 4.2, 7.4)   # hunched shoulder humps
    boulder(body, 0, 19.6, 3.4, 8.0, 3.0, 5.0, 'rock_d')                                  # back hump
    tc = r.bone('tc_rune', [0, 15, -4.4], body)
    B(tc, 0, 13.6, -4.45, 3.0, 0.8, 0.2, 'rune'); B(tc, 0, 13.6, -4.45, 0.8, 3.4, 0.2, 'rune')   # glowing team rune
    hd = r.bone('head', [0, 17, -3.6], body)
    boulder(hd, 0, 14.6, -4.6, 6.4, 5.6, 5.4)                                            # head sunk between shoulders
    B(hd, 0, 18.2, -7.0, 6.8, 1.6, 1.4, 'rock_l')                                         # heavy brow
    for sx in (1, -1):
        B(hd, sx * 1.6, 17.0, -7.35, 2.0, 1.0, 0.2, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 1.6, 17.5, -7.35])   # angry glowing eyes
    B(hd, 0, 14.6, -7.1, 5.8, 1.8, 1.0, 'rock_d', decals={'north': pix(["k.k.k.k", "......."], {'k': '#3a3430'})})   # jaw with crack-teeth
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.6
        a = r.bone('arm_' + side, [x, 19, 1], body)
        boulder(a, x, 14.6, 1.0, 5.6, 5.6, 5.6, 'rock_l')                                  # shoulder boulder
        boulder(a, x + sx * 0.4, 8.6, 0.6, 4.6, 6.6, 4.6)                                  # upper arm
        boulder(a, x + sx * 0.6, 3.4, 0.2, 5.0, 5.8, 5.0, 'rock_d')                         # forearm
        boulder(a, x + sx * 0.6, -1.6, -0.2, 6.6, 5.6, 6.6)                                # huge fist (knuckles near the ground)
        B(a, x + sx * 0.6, 1.2, -3.55, 5.2, 0.5, 0.3, 'void')                              # finger cracks
    m.hitbox(*hb)
    shade_pass(m, ('rock',))
    mc_idle(m, 3.0, extra={'body': {'rotation': loop([[12, 0, 0], [14, 0, 0]], 3.0)}})
    mc_walk(m, 1.2, 18, extra={'body': {'rotation': loop([[14, 0, -3], [14, 0, 3]], 1.2)}})
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [-150, 0, 0]), (0.55, [-15, 0, 0]), (1.0, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    slam['body'] = {'rotation': [(0, [12, 0, 0]), (0.35, [0, 0, 0]), (0.55, [26, 0, 0]), (1.0, [12, 0, 0])]}
    m.anim('attack', 1.0, 'once', slam)
    common_tail(m)
    return m


def golem():
    return _rock_golem('clash_golem', 1.5, (2.4, 3.0))


def golemite():
    return _rock_golem('clash_golemite', 0.75, (1.2, 1.5))


