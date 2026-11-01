def shade_pass(m, prefixes=('skin',), seed=7):
    """per-face shading for flat materials: lit top, darker bottom/edges, light mottling"""
    import random
    rng = random.Random(seed)
    for bn in m.bones:
        for c in bn.cubes:
            if not c['mat'].startswith(prefixes):
                continue
            for f in ('north', 'south', 'east', 'west'):
                base = [('shade', 0, 0, 1, 0.15, 1.08), ('shade', 0, 0.8, 1, 1, 0.86),
                        ('shade', 0, 0, 0.1, 1, 0.92), ('shade', 0.9, 0, 1, 1, 0.92)]
                for _ in range(4):
                    x0, y0 = rng.random() * 0.85, rng.random() * 0.85
                    base.append(('shade', x0, y0, x0 + 0.12, y0 + 0.12, rng.choice((0.95, 1.05))))
                c['decals'][f] = base + c['decals'].get(f, [])


def archer():
    """HQ vanilla-like CR/CoC Archer: pink bob + bangs, sleeveless green dress, team cape + hood,
    gold arm ring, brown belt + quiver, bare feet, recurve bow"""
    m = new_model('clash_archer')
    m.mats_({'skin': ('#f0b896', 'skin'), 'skin_d': ('#d89878', 'skin'), 'hair': ('#e8509e', 'hair'), 'hair_d': ('#c03a82', 'hair'),
             'dress': ('#7cc23a', 'cloth'), 'dress_d': ('#5e9a2a', 'cloth'), 'cape': ('#efefef', 'cloth'), 'cape_d': ('#d2d2d2', 'cloth'),
             'belt': ('#6a4426', 'leather'), 'gold': ('#e2b23a', 'metal'), 'wood': ('#8a5530', 'wood'), 'string': ('#e8e8e0', 'plain'),
             'feather': ('#f06aa8', 'cloth'), 'steel': ('#b8bcc4', 'metal')})
    S = 'skin'
    root = m.bone('root', [0, 0, 0])
    toes = pix(["........", "k.k.k.k."], {'k': '#c88a6a'})
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 1.9
        lg = m.bone('leg_' + side, [x, 12, 0], root)
        cb(lg, x, 1.0, 0, 3.2, 11.0, 3.2, S)                                      # bare leg
        cb(lg, x, 0, -0.5, 3.4, 1.0, 4.2, 'skin_d', decals={'north': toes})       # bare foot
    body = m.bone('body', [0, 12, 0], root)
    cb(body, 0, 18, 0, 6.6, 6.0, 3.4, 'dress', decals={'north': pix(["..k..k..", "...kk...", "........"], {'k': '#5e9a2a'})})
    skirt = m.bone('tc_skirt', [0, 17, 0], body)                                   # (kept name; dress is green, not team)
    cb(skirt, 0, 11.6, 0, 7.6, 5.6, 4.4, 'dress',
       decals={'north': pix(["........", "........", "........", "k..k..k.", "kk.kk.kk"], {'k': '#5e9a2a'}),
               'south': pix(["........", "........", "........", "k..k..k.", "kk.kk.kk"], {'k': '#5e9a2a'})})
    cb(body, 0, 16.6, 0, 7.2, 1.3, 4.0, 'belt')                                    # belt
    cb(body, -1.6, 16.5, -2.1, 1.6, 1.5, 0.3, 'gold')                              # buckle
    cb(body, 2.4, 13.4, -2.3, 1.8, 2.4, 0.6, 'belt')                               # pouch
    vest = m.bone('tc_vest', [0, 22, 0], body)                                     # cape + hood (team colour)
    cb(vest, 0, 22.6, 2.4, 7.4, 2.4, 2.8, 'cape_d')                                # hood bunched at the neck
    cb(vest, 0, 9.0, 2.2, 7.4, 14.4, 0.6, 'cape', decals={'south': pix(["....", "....", "....", "....", "....", "....", "k..k", "kkkk"], {'k': '#d2d2d2'})})
    cb(vest, 0, 6.6, 2.6, 8.4, 3.0, 0.6, 'cape_d')                                 # flared hem
    for sx in (1, -1):
        cb(vest, sx * 3.4, 23.0, 0.4, 1.6, 1.4, 4.0, 'cape')                       # over the shoulders
    q = m.bone('quiver', [1.6, 17, 3.4], body)
    cb(q, 1.6, 13.6, 3.6, 2.4, 8.0, 2.4, 'belt', rot=('z', -22.5))
    for i, dx in enumerate((-0.6, 0.6, 0.0)):
        cb(q, 3.6 + dx, 21.6 + i * 0.3, 3.6 + (i - 1) * 0.6, 0.8, 2.0, 0.6, 'feather', rot=('z', -22.5))   # pink fletching
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", "........", ".p.rr.p.", "........"],
               {'k': '#7a2a5a', 'w': '#ffffff', 'b': '#3a6aa8', 'p': '#f29a9a', 'r': '#c2384a'})
    cb(hd, 0, 24, 0, 8, 8, 8, S, decals={'north': face})
    hair = m.bone('hair', [0, 28, 0], hd)
    cb(hair, 0, 29.6, 0.2, 9.0, 3.2, 8.8, 'hair')                                  # crown
    cb(hair, 0, 30.4, -4.5, 8.8, 1.6, 0.8, 'hair_d')                               # straight-cut bangs
    cb(hair, 0, 29.4, -4.6, 8.8, 1.2, 0.6, 'hair', decals={'north': pix(["k.k.k.k.k"], {'k': '#c03a82'})})
    for sx in (1, -1):
        cb(hair, sx * 4.4, 23.4, 0.4, 0.9, 6.6, 8.2, 'hair')                       # bob sides to the jaw
        cb(hair, sx * 4.3, 23.0, -3.6, 1.0, 1.2, 1.2, 'hair_d')                    # flicked ends
    cb(hair, 0, 23.4, 4.4, 9.0, 6.6, 0.9, 'hair')                                  # back
    rib = m.bone('tc_ribbon', [3.4, 30, 0.8], hair)
    cb(rib, 3.6, 30.4, 1.6, 0.6, 1.2, 1.6, 'cape')                                 # small team hair clip
    braid = m.bone('braid', [0, 24, 4.2], hair)                                    # (kept bone) short tuft at the nape
    cb(braid, 0, 22.6, 4.6, 3.0, 1.6, 0.8, 'hair_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 4.8
        a = m.bone('arm_' + side, [x, 22, 0], body)
        cb(a, x, 12.0, 0, 3.0, 12.0, 3.0, S)                                       # slim bare arm
        cb(a, x, 19.0, 0, 3.4, 0.9, 3.4, 'gold')                                   # gold arm ring
        if side == 'l':
            cb(a, x, 13.0, 0, 3.4, 3.0, 3.4, 'belt')                               # leather bracer
    bow = m.bone('bow', [-4.8, 12.6, -2.2], m.by_name('arm_l'))                    # recurve bow in the left hand
    bx, bz = -4.8, -2.2
    cb(bow, bx, 11.4, bz, 1.0, 2.6, 1.0, 'gold')                                   # grip wrap
    for sy in (1, -1):
        y0 = 14.0 if sy > 0 else 6.0
        cb(bow, bx, y0, bz + 0.3, 0.8, 4.0, 0.8, 'wood')                           # limb
        yt = 18.0 if sy > 0 else 3.2
        cb(bow, bx, yt, bz + 1.0, 0.8, 2.8, 0.8, 'wood', rot=('x', -sy * 22.5))     # limb bending back
        cb(bow, bx, (20.6 if sy > 0 else 2.2), bz - 0.2, 0.8, 1.2, 0.8, 'gold')     # recurved gold tip
    cb(bow, bx, 3.2, bz + 2.0, 0.2, 17.2, 0.2, 'string')                            # string
    m.hitbox(0.7, 2.0)
    shade_pass(m, ('skin', 'dress', 'cape'))
    mc_idle(m, 2.0)
    mc_walk(m, 0.7, 30)
    aim = {'arm_l': {'rotation': [(0, [0, 0, 0]), (0.25, [-88, 6, 0]), (0.7, [-88, 6, 0]), (0.9, [0, 0, 0])]},
           'arm_r': {'rotation': [(0, [0, 0, 0]), (0.25, [-88, -30, 0]), (0.55, [-88, -45, 0]), (0.6, [-85, -10, 0]), (0.9, [0, 0, 0])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.25, [0, 25, 0]), (0.7, [0, 25, 0]), (0.9, [0, 0, 0])]},
           'head': {'rotation': [(0, [0, 0, 0]), (0.25, [0, -20, 0]), (0.7, [0, -20, 0]), (0.9, [0, 0, 0])]}}
    m.anim('attack', 0.9, 'once', aim)
    common_tail(m)
    return m


