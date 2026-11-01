def minion():
    """HQ Minion (from the Sketchfab reference): pear-shaped body, head pushed forward with a long snout + wide grin,
    big side eyes, horns rising from the back of the skull with dark ring bases, small bat wings high on the back,
    long arms in ragged team sleeves (forearm + hand) with claws poking out, short legs with 2-toe feet, little tail"""
    m = new_model('clash_minion')
    m.mats_({'skin': ('#4a9ae0', 'skin'), 'skin_d': ('#2e6ab8', 'skin'), 'skin_l': ('#78c0f4', 'skin'), 'horn': ('#2a4a98', 'skin'),
             'wing': ('#3a78d0', 'leather', {'stitch': False}), 'rib': ('#1e3470', 'leather'), 'mitt': ('#e6e0f0', 'cloth'),
             'claw': ('#5aa0e8', 'bone'), 'eye': ('#ffffff', 'plain'), 'iris': ('#c02a8a', 'plain'), 'pupil': ('#1a0a1a', 'plain'),
             'mouth': ('#14203a', 'plain'), 'tooth': ('#f4f8ff', 'bone')})
    spk = [('px', i / 7, j / 7, '#8a4ab8') for (i, j) in ((1, 2), (4, 5), (5, 1), (2, 6))]
    def rb(b, x, y, z, w, h, d, mat, r=0.6, **kw):
        cb(b, x, y + r, z, w, h - 2 * r, d, mat, **kw); cb(b, x, y, z, w - 2 * r, h, d - 2 * r, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 1.5, 5, 0.6], root)
        rb(lg, sx * 1.5, 2.2, 0.6, 2.2, 3.0, 2.4, 'skin')
        cb(lg, sx * 1.5, 0.6, 0.8, 1.6, 1.8, 1.8, 'skin')
        for dx in (-0.45, 0.45):
            cb(lg, sx * 1.5 + dx, 0, -0.4, 0.8, 0.9, 2.4, 'skin_d')                          # two toes
    body = m.bone('body', [0, 5, 0], root)
    rb(body, 0, 4.4, 0.6, 5.8, 4.6, 4.8, 'skin', r=0.8, decals={'north': [('rect', 0.2, 0, 0.8, 1, '#78c0f4')] + spk, 'south': spk})   # round belly
    rb(body, 0, 8.4, 0.2, 6.4, 3.6, 4.4, 'skin', decals={'north': spk, 'south': spk})        # chest
    cb(body, 0, 11.4, 0.0, 7.4, 1.6, 4.0, 'skin')                                           # shoulders
    tl = m.bone('tail', [0, 5, 3], body)
    cb(tl, 0, 5.0, 3.4, 1.0, 1.6, 1.4, 'skin'); cb(tl, 0, 4.2, 4.0, 0.7, 1.0, 0.9, 'skin_d')
    hd = m.bone('head', [0, 12.4, -1.0], body)
    rb(hd, 0, 12.2, -0.6, 6.0, 5.4, 5.6, 'skin', r=0.8)                                     # skull
    rb(hd, 0, 12.4, -4.4, 4.6, 3.2, 3.4, 'skin', r=0.5)                                     # long snout
    cb(hd, 0, 14.2, -5.9, 2.4, 1.0, 0.6, 'skin_l', decals={'north': pix(["k..k"], {'k': '#14203a'})})   # nose + nostrils
    cb(hd, 0, 13.0, -6.15, 3.6, 0.5, 0.2, 'mouth')                                          # wide grin (front)
    for sx in (1, -1):
        cb(hd, sx * 2.35, 12.9, -4.6, 0.2, 0.5, 3.0, 'mouth')                               # grin runs along the sides
        cb(hd, sx * 2.45, 13.4, -3.6, 0.2, 0.5, 0.5, 'tooth'); cb(hd, sx * 2.45, 13.4, -4.6, 0.2, 0.5, 0.5, 'tooth')
        cb(hd, sx * 2.6, 15.0, -2.4, 1.0, 2.0, 2.0, 'eye')                                  # big eyes on the sides of the head
        cb(hd, sx * 2.7, 15.2, -3.0, 0.9, 1.4, 1.0, 'iris'); cb(hd, sx * 2.75, 15.5, -3.2, 0.9, 0.8, 0.5, 'pupil')
        cb(hd, sx * 2.4, 17.0, -2.4, 1.6, 0.5, 2.6, 'skin_d', rot=('z', sx * 22.5), rot_origin=[sx * 2.4, 17.2, -2.4])   # brow ridge
        h = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 1.8, 17.4, 0.6], hd)
        cb(h, sx * 1.9, 17.2, 0.6, 2.2, 0.8, 2.2, 'skin_d')                                  # dark ring base
        for k, (dx, dy, dz, w) in enumerate(((1.9, 18.0, 0.6, 1.8), (2.2, 19.6, 1.0, 1.5), (2.3, 21.0, 1.8, 1.2), (2.2, 22.0, 2.8, 0.9))):
            cb(h, sx * dx, dy, dz, w, 1.8, w, 'horn', rot=('x', -22.5 * min(k, 2)), rot_origin=[sx * dx, dy, dz])   # horn sweeping up and back
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 3.4, 11.6, 0], body)
        cb(a, sx * 4.3, 7.6, 0, 1.9, 4.4, 1.9, 'skin', decals={'north': spk})                  # long upper arm
        tc = m.bone('tc_mitt_' + side, [sx * 4.4, 7.6, 0], a)
        rb(tc, sx * 4.5, 2.4, -0.4, 3.4, 5.6, 3.6, 'mitt', r=0.5,
           decals={'north': [('rect', 0, 0, 1, 0.12, '#c8c0d8')], 'south': [('rect', 0, 0, 1, 0.12, '#c8c0d8')]})   # ragged sleeve over forearm + hand
        for (dx, dz) in ((-1.0, -1.6), (0.9, 1.4), (1.2, -1.2)):
            cb(tc, sx * 4.5 + dx, 7.8, dz, 1.0, 0.7, 1.0, 'mitt')                             # torn top edge
        for dx in (-1.1, -0.1, 0.9):
            cb(a, sx * 4.5 + dx, 1.0, -1.6, 0.7, 1.8, 0.8, 'claw')                             # claws poking out the bottom
        cb(a, sx * 4.5 - sx * 1.6, 2.4, -1.2, 0.7, 1.4, 0.7, 'claw')                          # thumb claw
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 1.6, 11.6, 2.4], body)
        ro = dict(rot=('z', -sx * 45), rot_origin=[sx * 1.6, 11.6, 2.4])
        cb(w, sx * 4.4, 11.4, 2.6, 5.6, 0.9, 0.9, 'rib', **ro)                                  # leading edge
        for (x0, x1, h) in ((1.6, 3.6, 3.6), (3.6, 5.6, 4.2), (5.6, 7.2, 3.4)):
            cb(w, sx * (x0 + x1) / 2, 11.8 - h, 2.7, x1 - x0, h, 0.25, 'wing',
               decals={f: [('lerp', '#2a5ab0', 0.0, 0.7, 'y'), ('rect', 0.85, 0, 1, 1, '#1e3470')] for f in ('north', 'south')}, **ro)   # membranes with ribs
        cb(w, sx * 7.4, 11.0, 2.6, 0.7, 1.4, 0.7, 'rib', **ro)
    m.bone('tc_bandana', [0, 13, 0], body)
    m.hitbox(0.6, 1.2)
    shade_pass(m, ('skin',))
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, -12, -a], [0, 12, a * 0.5]], L)}, 'wing_l': {'rotation': loop([[0, 12, a], [0, -12, -a * 0.5]], L)}}
    hang = {'arm_r': {'rotation': loop([[-20, 0, 18], [-24, 0, 20]], 0.64)}, 'arm_l': {'rotation': loop([[-20, 0, -18], [-24, 0, -20]], 0.64)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.64)}, 'tail': {'rotation': loop([[0, 15, 0], [0, -15, 0]], 0.64)},
            'body': {'rotation': loop([[12, 0, 0], [12, 0, 0]], 0.64)}, 'head': {'rotation': loop([[-10, 0, 0], [-10, 0, 0]], 0.64)}}
    idle.update(flap(0.32, 40)); idle.update(hang)
    m.anim('idle', 0.64, 'loop', idle)
    walk = dict(idle); walk['body'] = {'rotation': loop([[25, 0, 0], [25, 0, 0]], 0.32)}; walk['head'] = {'rotation': loop([[-20, 0, 0], [-20, 0, 0]], 0.32)}
    walk.update(flap(0.16, 45)); walk['root'] = {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.32)}
    m.anim('walk', 0.32, 'loop', walk)
    m.anim('attack', 0.5, 'once', {'arm_r': {'rotation': [(0, [-20, 0, 18]), (0.15, [-130, 0, 10]), (0.3, [-30, 0, 0]), (0.5, [-20, 0, 18])]},
                                   'body': {'rotation': [(0, [12, 0, 0]), (0.15, [0, 10, 0]), (0.3, [25, -10, 0]), (0.5, [12, 0, 0])]}})
    common_tail(m)
    return m


