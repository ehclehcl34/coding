def baby_dragon():
    """HQ vanilla-like CR Baby Dragon. Wings, paws, feet, horn, ears are TEAM coloured (tc_ bones, white base);
    a green overlay shell with ordered-dither alpha fades green -> team colour (vanilla-style gradient).
    Rounded head/snout/body built from cross-slab stacks."""
    m = new_model('clash_baby_dragon')
    m.mats_({'grn': ('#5ec83a', 'skin'), 'grn_d': ('#45a42a', 'skin'), 'belly': ('#a6e27a', 'skin'),
             'tm': ('#efefef', 'skin'), 'tm_d': ('#cfcfcf', 'skin'),
             'mouth': ('#ff8a2a', 'glow'), 'mouth_d': ('#c8461a', 'glow'), 'tongue': ('#e07482', 'skin'),
             'tooth': ('#f4f2ea', 'bone'), 'eye': ('#fbf6e6', 'plain')})

    def rbox(bone, x, y, z, w, h, d, mat, r=0.8, **kw):                            # rounded box: 3 cross slabs
        cb(bone, x, y + r, z, w, h - 2 * r, d, mat, **kw)
        cb(bone, x, y, z, w - 2 * r, h, d - 2 * r, mat, **kw)
        cb(bone, x, y + r * 0.5, z, w - r, h - r, d - r * 0.0, mat, **kw)

    def team(parent, name, origin, boxes, fade):
        """boxes: list of (x,y,z,w,h,d). team-coloured core + green dithered shell. fade=(a0,a1,axis[,flip])"""
        t = m.bone(name, origin, parent)
        for (x, y, z, w, h, d) in boxes:
            cb(t, x, y, z, w, h, d, 'tm')
            c = cb(parent, x, y - 0.05, z, w + 0.12, h + 0.1, d + 0.12, 'grn')
            c['dither'] = fade
        return t

    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 10, 0], root)
    stripes = [('rect', 0.1, f, 0.9, f + 0.07, '#86c85e') for f in (0.2, 0.45, 0.7)]
    rbox(body, 0, 2.6, 0.2, 10.6, 9.0, 9.2, 'grn', r=1.2)                            # round pot belly
    cb(body, 0, 3.6, -4.6, 7.0, 7.6, 0.6, 'belly', decals={'north': stripes})
    rbox(body, 0, 11.0, 0.4, 9.2, 5.6, 8.0, 'grn', r=1.0)                            # chest
    cb(body, 0, 11.4, -3.75, 6.0, 4.0, 0.5, 'belly', decals={'north': stripes[:2]})
    tc_band = m.bone('tc_scarf', [0, 15, -1], body)                                  # (kept) hidden tiny tag
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('b%s_leg' % side, [sx * 3.4, 4.5, 1.0], body)
        rbox(lg, sx * 3.6, 1.2, 1.0, 3.8, 3.6, 4.4, 'grn', r=0.6)                        # stubby thigh
        team(lg, 'tc_foot_' + side, [sx * 3.6, 1, 0.4], [(sx * 3.6, 0, 0.2, 4.0, 1.6, 5.2)], (1.0, 0.0, 'y'))
        cb(lg, sx * 3.6, 0, -2.5, 3.0, 0.6, 0.4, 'tm_d', decals={'north': pix(["k.k.k"], {'k': '#ffffff'})})   # toe claws
        ar = m.bone('f%s_leg' % side, [sx * 5.0, 14.0, -1.6], body)                        # little arm
        team(ar, 'tc_paw_' + side, [sx * 5.4, 11, -1.8],
             [(sx * 5.4, 10.0, -1.8, 2.8, 4.8, 3.0), (sx * 5.4, 8.4, -2.2, 3.2, 2.0, 3.4)], (1.0, -0.2, 'y'))
    # head: round skull + round snout
    hd = m.bone('head', [0, 16, -1], body)
    rbox(hd, 0, 16.2, -1.6, 9.6, 7.4, 8.6, 'grn', r=1.2)
    rbox(hd, 0, 18.8, -8.6, 8.2, 4.4, 6.2, 'grn', r=0.9,
         decals={'north': pix(["........", ".kk..kk.", "........", "........"], {'k': '#2a5a1a'})})   # snout + nostrils
    cb(hd, 0, 23.0, -6.0, 6.0, 0.6, 3.0, 'grn')                                      # brow bump
    team(hd, 'tc_horn', [0, 23, -2.4], [(0, 23.4, -2.4, 2.2, 2.6, 2.2), (0, 26.0, -2.4, 1.4, 1.2, 1.4)], (1.0, 0.0, 'y'))
    for i in range(7):
        cb(hd, -3.0 + i * 1.0, 18.0, -11.0, 0.7, 1.0, 0.7, 'tooth')                   # upper teeth
    for sx in (1, -1):
        cb(hd, sx * 3.7, 18.0, -8.0, 0.7, 1.0, 4.6, 'tooth')
        cb(hd, sx * 4.9, 19.8, -4.6, 1.4, 2.6, 2.6, 'eye',                            # bulging side eyes, amber iris
           decals={'north': pix(["...", ".ok", ".kk"], {'k': '#2a1a10', 'o': '#c8782a'}),
                   'east' if sx > 0 else 'west': pix(["...", "ko.", "kk."], {'k': '#2a1a10', 'o': '#c8782a'})})
        cb(hd, sx * 4.9, 22.2, -4.6, 1.5, 0.6, 2.8, 'grn_d')                          # eyelid
        ear = m.bone('ear_' + ('r' if sx > 0 else 'l'), [sx * 4.6, 21, 1.0], hd)
        team(ear, 'tc_ear_' + ('r' if sx > 0 else 'l'), [sx * 5.0, 21, 1.4], [(sx * 5.1, 20.8, 1.4, 0.9, 2.8, 2.6)], (1.0, 0.0, 'y'))
    cb(hd, 0, 16.8, -6.0, 7.2, 1.6, 6.4, 'mouth', decals={'up': [('rect', 0.2, 0.3, 0.8, 1.0, '#c8461a')]})   # glowing mouth
    jaw = m.bone('jaw', [0, 17.4, -2.0], hd)
    rbox(jaw, 0, 14.4, -6.2, 8.4, 2.8, 7.6, 'grn', r=0.7)
    cb(jaw, 0, 17.2, -6.0, 7.0, 0.3, 6.8, 'mouth_d')
    for sx in (1, -1):
        cb(jaw, sx * 3.6, 17.2, -6.8, 0.7, 1.0, 5.0, 'tooth')
    tg = m.bone('tongue', [0, 17.4, -6.0], jaw)
    cb(tg, 0, 17.2, -8.8, 2.6, 0.8, 5.8, 'tongue', decals={'up': pix(["..", "k.", "..", ".k"], {'k': '#c45a68'})})
    cb(tg, 0, 14.6, -12.0, 2.6, 3.4, 0.8, 'tongue')
    # bat wings (team), fading from green at the root
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 3.0, 15.0, 3.8], body)
        fade = (1.2, -0.6, 'x', sx < 0)
        team(w, 'tc_wing_' + side, [sx * 3.0, 15.0, 3.8],
             [(sx * 8.0, 15.0, 4.2, 10.0, 7.0, 0.6), (sx * 8.0, 21.6, 4.2, 10.4, 1.4, 1.2), (sx * 13.4, 18.4, 4.2, 1.2, 4.6, 1.0),
              (sx * 5.4, 15.6, 4.2, 0.8, 6.0, 0.9), (sx * 9.0, 15.6, 4.2, 0.8, 6.0, 0.9)], fade)
    # tail
    t = m.bone('tail', [0, 5.0, 4.4], body)
    rbox(t, 0, 2.8, 6.0, 4.8, 3.8, 3.6, 'grn', r=0.6)
    rbox(t, 0, 2.2, 9.0, 3.2, 2.8, 3.4, 'grn', r=0.5)
    cb(t, 0, 1.8, 11.6, 1.8, 1.8, 2.6, 'grn')
    for z, y, h in ((6.0, 6.6, 1.6), (9.0, 5.0, 1.2), (11.4, 3.6, 1.0)):
        team(t, 'tc_spike%d' % int(z), [0, y, z], [(0, y, z, 0.8, h, 1.4)], (0.6, 0.0, 'y'))
    m.hitbox(1.2, 1.6)
    shade_pass(m, ('grn', 'tm'))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -10, -a], [0, 10, a * 0.4]], L)},
                         'wing_l': {'rotation': loop([[0, 10, a], [0, -10, -a * 0.4]], L)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.2, 0]], 1.0)},
            'tail': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 1.0)},
            'jaw': {'rotation': loop([[20, 0, 0], [26, 0, 0]], 1.0)},
            'fr_leg': {'rotation': loop([[-20, 0, 0], [-10, 0, 0]], 1.0)}, 'fl_leg': {'rotation': loop([[-20, 0, 0], [-10, 0, 0]], 1.0)}}
    idle.update(flap(0.5, 35))
    m.anim('idle', 1.0, 'loop', idle)
    walk = dict(idle); walk.update(flap(0.3, 45)); walk['body'] = {'rotation': loop([[12, 0, 0], [12, 0, 0]], 0.4)}
    walk['root'] = {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.4)}
    m.anim('walk', 0.4, 'loop', walk)
    m.anim('attack', 0.7, 'once', {'head': {'rotation': [(0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.35, [10, 0, 0]), (0.7, [0, 0, 0])]},
                                   'jaw': {'rotation': [(0, [20, 0, 0]), (0.2, [10, 0, 0]), (0.35, [40, 0, 0]), (0.55, [40, 0, 0]), (0.7, [20, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.35, [10, 0, 0]), (0.7, [0, 0, 0])]}})
    common_tail(m)
    return m


