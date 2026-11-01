def _elixir_brute(name, S, hb):
    """HQ vanilla-like Elixir Golem body: magenta gummy gorilla build, small blocky head with glowing angry eyes,
    huge shoulders/arms, drips, spiked team wristbands, short legs with toes"""
    m = new_model(name)
    m.mats_({'ex': ('#c040d8', 'soft'), 'ex_d': ('#9a28b0', 'soft'), 'ex_l': ('#e070f0', 'soft'), 'eye': ('#ffd0ff', 'glow'),
             'band': ('#efefef', 'leather'), 'spike': ('#c8ccd4', 'metal')})
    r = Rig(m, S); B = r.box
    drip = lambda: [('rect', 0.2, 0.6, 0.28, 1.0, '#9a28b0'), ('rect', 0.6, 0.7, 0.68, 1.0, '#9a28b0')]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = r.bone('leg_' + side, [x, 9, 0], root)
        B(lg, x, 1.0, 0, 4.4, 8.0, 4.6, 'ex')
        B(lg, x, 0, -0.6, 5.0, 1.4, 6.0, 'ex_d', decals={'north': pix(["k.k.k.k", "......."], {'k': '#8a2098'})})   # feet + toes
    body = r.bone('body', [0, 9, 0], root)
    B(body, 0, 8.6, 0.4, 10.4, 6.0, 7.0, 'ex', decals={'north': drip(), 'south': drip()})      # pot belly
    B(body, 0, 14.0, 0.8, 15.0, 8.4, 8.4, 'ex', decals={'north': [('rect', 0.48, 0.2, 0.52, 0.7, '#9a28b0')] + drip()})   # huge chest
    for sx in (1, -1):
        B(body, sx * 3.6, 16.0, -3.6, 6.0, 4.0, 0.8, 'ex_l')                                 # pecs
        B(body, sx * 5.4, 22.0, 1.2, 5.4, 2.6, 6.4, 'ex')                                    # trapezius
    for (x, y) in ((-4.0, 13.8), (3.0, 14.2), (5.6, 10.0)):
        B(body, x, y, -3.7, 1.0, 1.6, 0.6, 'ex_l')                                           # drip blobs
    hd = r.bone('head', [0, 22, -1.4], body)
    B(hd, 0, 21.6, -1.6, 5.2, 5.2, 5.2, 'ex', decals={'north': pix(["......", "......", ".k..k.", "......", "......", "......"], {'k': '#7a1890'})})
    B(hd, 1.0, 26.8, -0.8, 2.0, 1.6, 2.0, 'ex')                                          # pointy top
    for sx in (1, -1):
        B(hd, sx * 1.3, 23.4, -4.3, 1.6, 0.8, 0.3, 'eye')                                    # glowing angry eyes
        B(hd, sx * 1.3, 24.4, -4.3, 2.0, 0.6, 0.5, 'ex_d', rot=('z', -sx * 22.5), rot_origin=[sx * 1.3, 24.7, -4.3])   # brows
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 10.2
        a = r.bone('arm_' + side, [x, 21.5, 1], body)
        B(a, x, 15.0, 1.0, 5.6, 7.0, 5.6, 'ex', decals={'north': drip()})                    # upper arm
        B(a, x, 7.4, 0.6, 6.4, 7.6, 6.4, 'ex', decals={'north': drip(), 'east': drip(), 'west': drip()})   # thick forearm
        tc = r.bone('tc_band_' + side, [x, 9, 1], a)
        B(tc, x, 8.4, 0.6, 7.2, 2.6, 7.2, 'band')                                            # team wristband
        for (dx, dz) in ((sx * 3.8, 0), (0, -3.8), (0, 3.8), (-sx * 3.8, 0)):
            B(tc, x + dx, 9.0, 0.6 + dz, 1.4, 1.4, 1.4, 'spike')                               # spikes
        B(a, x, 3.0, 0.2, 6.0, 4.6, 6.0, 'ex_d', decals={'north': pix(["k.k.k", ".....", "....."], {'k': '#7a1890'})})   # big fist
    m.hitbox(*hb)
    shade_pass(m, ('ex',))
    mc_idle(m, 2.4); mc_walk(m, 1.4, 20)
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.4, [-160, 0, 0]), (0.6, [-20, 0, 0]), (1.2, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    slam['body'] = {'rotation': [(0, [0, 0, 0]), (0.4, [-10, 0, 0]), (0.6, [18, 0, 0]), (1.2, [0, 0, 0])]}
    m.anim('attack', 1.2, 'once', slam)
    common_tail(m)
    return m


def elixir_golem():
    return _elixir_brute('clash_elixir_golem', 1.25, (2.0, 2.8))


def elixir_golemite():
    return _elixir_brute('clash_elixir_golemite', 0.75, (1.3, 1.6))


def elixir_blob():
    """small elixir gummy blob with the golem's face and a tiny team wristband-ribbon"""
    m = new_model('clash_elixir_blob')
    m.mats_({'ex': ('#c040d8', 'soft'), 'ex_d': ('#9a28b0', 'soft'), 'eye': ('#ffd0ff', 'glow'), 'band': ('#efefef', 'leather')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 3, 0], root)
    cb(body, 0, 0, 0, 7.0, 5.0, 7.0, 'ex'); cb(body, 0, 0, 0, 5.6, 6.4, 5.6, 'ex'); cb(body, 0.8, 6.4, 0.4, 2.0, 1.4, 2.0, 'ex')
    for sx in (1, -1):
        cb(body, sx * 1.4, 3.6, -2.85, 1.4, 0.8, 0.2, 'eye')
        cb(body, sx * 1.4, 4.6, -2.9, 1.8, 0.5, 0.3, 'ex_d')
    cb(body, 0, 1.6, -3.55, 3.0, 0.8, 0.1, 'ex_d')                                         # mouth
    tc = m.bone('tc_ribbon', [0, 2, 0], body)
    cb(tc, 0, 1.2, 0, 7.2, 1.0, 7.2, 'band')
    m.hitbox(0.7, 0.7)
    shade_pass(m, ('ex',))
    m.anim('idle', 1.0, 'loop', {'body': {'scale': loop([[1, 1, 1], [1.08, 0.9, 1.08]], 1.0)}})
    m.anim('walk', 0.5, 'loop', {'root': {'position': loop([[0, 0, 0], [0, 2.0, 0]], 0.25)}, 'body': {'scale': loop([[1.1, 0.85, 1.1], [0.92, 1.1, 0.92]], 0.25)}})
    m.anim('attack', 0.5, 'once', {'body': {'scale': [(0, [1, 1, 1]), (0.2, [1.25, 0.8, 1.25]), (0.3, [0.85, 1.2, 0.85]), (0.5, [1, 1, 1])]},
                                   'root': {'position': [(0, [0, 0, 0]), (0.3, [0, 1, -2]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


