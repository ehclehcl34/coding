def balloon():
    """HQ vanilla-like Balloon: round team-coloured patched envelope with rope net, burner flame,
    rope-hung wooden basket with sandbags, skeleton pilot in leather flight cap holding a big bomb"""
    import random
    rng = random.Random(3)
    m = new_model('clash_balloon')
    m.mats_({'fab': ('#efefef', 'cloth'), 'rope': ('#c9a265', 'rope'), 'wood': ('#8a5a32', 'wood', {'planks': True}),
             'wood_d': ('#5e3a20', 'wood'), 'metal': ('#9aa0a8', 'metal'), 'flame': ('#ffb030', 'glow'), 'flame2': ('#ff6a1a', 'glow'),
             'bone': ('#ece6d6', 'bone'), 'cap': ('#7a4a2a', 'leather'), 'bomb': ('#26272c', 'soft'), 'sand': ('#b08a5a', 'leather'),
             'spark': ('#ffe04a', 'glow'), 'void': ('#141210', 'plain'), 'ring': ('#3a2a20', 'plain')})
    root = m.bone('root', [0, 0, 0])
    env = m.bone('envelope', [0, 36, 0], root)
    fab = m.bone('tc_band', [0, 36, 0], env)                                       # whole envelope is team coloured
    cy, R, n = 36.0, 11.0, 11
    hgt = 2 * R / n
    for i in range(n):
        yc = -R + hgt * (i + 0.5)
        rr = max(2.5, (R * R - yc * yc) ** 0.5)
        y0 = cy + yc - hgt / 2
        dec = []
        for _ in range(3):                                                          # sewn-on patches + stitches
            x0, yy = rng.random() * 0.7, rng.random() * 0.4
            dec += [('rect', x0, yy, x0 + 0.25, yy + 0.5, rng.choice(('#ffffff', '#d4d4d4')))]
            dec += [('px', x0 + k * 0.06, yy, '#6a6a6a') for k in range(4)]
        for rot in (None, ('y', 45)):
            cb(fab, 0, y0, 0, 2 * rr, hgt, 0.8 * rr, 'fab', rot=rot, decals={'north': dec, 'south': dec} if rot is None else {})
            cb(fab, 0, y0, 0, 0.8 * rr, hgt, 2 * rr, 'fab', rot=rot, decals={'east': dec, 'west': dec} if rot is None else {})
        cb(fab, 0, y0, 0, 1.5 * rr, hgt, 1.5 * rr, 'fab')
        for ang in (0, 90, 180, 270):                                                # rope net meridians
            import math
            dx, dz = math.sin(math.radians(ang)), math.cos(math.radians(ang))
            cb(env, dx * (rr + 0.15), y0, dz * (rr + 0.15), 0.7 if dz else 0.4, hgt + 0.05, 0.4 if dz else 0.7, 'rope')
        if i in (n // 2, n // 2 - 3):                                                # horizontal rope rings
            for rot in (None, ('y', 45)):
                cb(env, 0, y0 + hgt / 2 - 0.35, 0, 2 * rr + 0.5, 0.7, 0.3, 'rope', rot=rot)
                cb(env, 0, y0 + hgt / 2 - 0.35, 0, 0.3, 0.7, 2 * rr + 0.5, 'rope', rot=rot)
    cb(env, 0, cy - R - 0.2, 0, 5.4, 0.6, 5.4, 'ring')                              # dark mouth of the envelope
    # burner + flame
    bu = m.bone('burner', [0, 24, 0], root)
    cb(bu, 0, 23.6, 0, 4.6, 0.8, 4.6, 'metal')
    for sx in (1, -1):
        cb(bu, sx * 2.4, 22.4, 0, 0.5, 2.0, 0.5, 'metal')
    fl = m.bone('flame', [0, 24.4, 0], bu)
    cb(fl, 0, 24.4, 0, 2.4, 1.6, 2.4, 'flame2')
    cb(fl, 0, 25.4, 0, 1.4, 1.4, 1.4, 'flame')
    # hanging ropes to the basket corners
    for sx in (1, -1):
        for sz in (1, -1):
            cb(root, sx * 4.4, 12.6, sz * 4.4, 0.5, 12.4, 0.5, 'rope')
            cb(root, sx * 5.2, 24.6, sz * 5.2, 0.5, 2.4, 0.5, 'rope')
    # basket
    bk = m.bone('basket', [0, 6, 0], root)
    cb(bk, 0, 5.6, 0, 9.2, 7.0, 9.2, 'wood')
    cb(bk, 0, 6.0, 0, 7.6, 6.8, 7.6, 'wood_d')                                     # inside (seen from above)
    for y in (5.4, 12.2):
        cb(bk, 0, y, 0, 9.8, 0.8, 9.8, 'rope')                                       # rope rims
    for (x, z) in ((5.4, 0.0), (-5.0, 2.6)):
        cb(bk, x, 7.4, z, 1.8, 2.6, 1.8, 'sand', decals={'up': [('rect', 0.3, 0.3, 0.7, 0.7, '#8a6a40')]})   # sandbags
        cb(bk, x, 10.0, z, 0.5, 2.4, 0.5, 'rope')
    # pilot
    pl = m.bone('pilot', [0, 12, 1], bk)
    cb(pl, 0, 11.0, 1.0, 3.4, 3.0, 2.0, 'bone', decals={'north': pix(["k.k", "...", "k.k"], {'k': '#a8a294'})})   # ribs over the rim
    sk = m.bone('skull', [0, 14, 1], pl)
    cb(sk, 0, 14.0, 0.8, 4.0, 4.0, 4.0, 'bone',
       decals={'north': pix(["....", "kk.k", "..k.", ".tt."], {'k': '#141210', 't': '#f6f4ea'})})
    cb(sk, 0, 16.6, 0.8, 4.6, 1.8, 4.6, 'cap')                                       # leather flight cap
    for sx in (1, -1):
        cb(sk, sx * 2.3, 14.4, 0.8, 0.5, 2.4, 2.4, 'cap')                             # ear flaps
    ar = m.bone('arm', [3.5, 12, -1], pl)
    cb(ar, 2.6, 11.0, -1.8, 0.9, 3.4, 0.9, 'bone')
    cb(ar, 1.6, 12.8, -3.2, 1.2, 1.0, 1.2, 'bone')                                   # bony hand on the bomb
    # bomb held on the front rim
    bo = m.bone('bomb', [1.0, 13, -5], root)
    for (w, h, d, dy) in ((3.6, 2.4, 3.6, 0.6), (2.4, 3.6, 2.4, 0.0), (3.0, 3.0, 3.0, 0.3)):
        cb(bo, 1.0, 11.4 + dy, -5.4, w, h, d, 'bomb')
    cb(bo, 1.0, 15.0, -5.4, 0.9, 0.5, 0.9, 'metal')
    cb(bo, 1.4, 15.5, -5.4, 0.4, 1.0, 0.4, 'rope')
    cb(bo, 1.4, 16.5, -5.4, 0.6, 0.6, 0.6, 'spark')
    m.hitbox(2.2, 3.0)
    shade_pass(m, ('fab', 'wood', 'bone'))
    sway = {'root': {'rotation': loop([[0, 0, 3], [0, 0, -3]], 2.4), 'position': loop([[0, 0, 0], [0, 1.0, 0]], 2.4)},
            'flame': {'scale': loop([[1, 1, 1], [1.2, 1.4, 1.2]], 0.3)},
            'skull': {'rotation': loop([[0, 15, 0], [0, -15, 0]], 2.4)}}
    m.anim('idle', 2.4, 'loop', sway)
    walk = dict(sway); walk['root'] = {'rotation': loop([[6, 0, 2], [6, 0, -2]], 1.6), 'position': loop([[0, 0, 0], [0, 0.6, 0]], 1.6)}
    m.anim('walk', 1.6, 'loop', walk)
    m.anim('attack', 1.0, 'once', {'arm': {'rotation': [(0, [0, 0, 0]), (0.3, [30, 0, 0]), (0.5, [0, 0, 0])]},
                                   'bomb': {'position': [(0, [0, 0, 0]), (0.3, [0, 0, -1]), (0.7, [0, -14, -1]), (0.72, [0, 0, 0])],
                                            'scale': [(0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.72, [0, 0, 0]), (0.95, [0, 0, 0]), (1.0, [1, 1, 1])]}})
    common_tail(m)
    return m


