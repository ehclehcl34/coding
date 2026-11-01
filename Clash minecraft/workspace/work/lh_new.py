def lava_hound():
    """HQ Lava Hound: glowing lava core sphere wrapped in separate dark rock plates (lava glows through the gaps),
    plated round head with horns + glowing eyes/mouth, bat wings with finger bones and lava-lit membranes,
    segmented clawed legs hanging down, plated tail"""
    import math, random
    rng = random.Random(4)
    m = new_model('clash_lava_hound')
    m.mats_({'rock': ('#3e3634', 'stone'), 'rock_l': ('#564c48', 'stone'), 'rock_d': ('#2a2422', 'stone'), 'lava': ('#ff7a14', 'glow'),
             'lava_y': ('#ffc040', 'glow'), 'eye': ('#ffd060', 'glow'), 'mem': ('#5a2418', 'leather', {'stitch': False})})

    def sphere_core(bone, c, R, mat='lava', n=7):
        h = 2 * R / n
        for i in range(n):
            yc = -R + h * (i + 0.5); rr = max(1.0, (R * R - yc * yc) ** 0.5)
            for rot in (None, ('y', 45)):
                kw = dict(rot=rot, rot_origin=[c[0], c[1] + yc, c[2]]) if rot else {}
                cb(bone, c[0], c[1] + yc - h / 2, c[2], 2 * rr, h, 0.83 * rr, mat, **kw)
                cb(bone, c[0], c[1] + yc - h / 2, c[2], 0.83 * rr, h, 2 * rr, mat, **kw)

    def plates(bone, c, R, n, size, skip=lambda d: False, sx=1.0, sy=1.0, sz=1.0):
        ga = math.pi * (3 - 5 ** 0.5)
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / n; r = (1 - y * y) ** 0.5; th = ga * i
            d = (math.cos(th) * r, y, math.sin(th) * r)
            if skip(d):
                continue
            ax = max(range(3), key=lambda k: abs(d[k]))
            s = size * rng.uniform(0.8, 1.15); t = 1.6
            dims = [s, s * rng.uniform(0.75, 1.0), s]; dims[ax] = t
            p = [c[0] + d[0] * R * sx, c[1] + d[1] * R * sy, c[2] + d[2] * R * sz]
            mat = rng.choice(('rock', 'rock', 'rock_l', 'rock_d'))
            cb(bone, p[0], p[1] - dims[1] / 2, p[2], dims[0], dims[1], dims[2], mat,
               decals={'north': [('rect', 0.1, 0.1, 0.4, 0.3, '#665a54')], 'up': [('shade', 0, 0, 1, 1, 1.12)]})

    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 16, 2], root)
    BC, BR = (0, 16, 3), 9.0
    sphere_core(body, BC, BR - 1.2)
    plates(body, BC, BR, 46, 5.6)
    for (x, y, z, h) in ((-2.0, 24.6, 4.0, 2.6), (2.4, 25.0, 7.0, 2.2), (0.0, 24.4, 0.0, 2.0)):
        cb(body, x, y, z, 2.0, h, 2.0, 'rock_l')                                           # back spikes
    nk = m.bone('neck', [0, 17, -6], body)
    hd = m.bone('head', [0, 17, -9], nk)
    HC, HR = (0, 17, -11.5), 6.0
    sphere_core(hd, HC, HR - 1.0, n=5)
    plates(hd, HC, HR, 26, 4.2, skip=lambda d: d[2] < -0.55 and abs(d[1]) < 0.5)
    cb(hd, 0, 13.4, -16.4, 9.0, 6.6, 2.0, 'rock', decals={'north': [('rect', 0.1, 0.05, 0.9, 0.12, '#2a2422')]})   # face plate
    cb(hd, 0, 20.2, -16.8, 9.4, 1.6, 2.6, 'rock_l')                                        # heavy brow
    cb(hd, 0, 21.6, -14.0, 2.4, 2.4, 2.4, 'rock_l')                                        # forehead knob
    for sx in (1, -1):
        cb(hd, sx * 2.4, 17.8, -17.45, 2.8, 1.6, 0.3, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 2.4, 18.6, -17.45])   # glowing eyes
        cb(hd, sx * 2.4, 17.4, -17.3, 3.6, 2.6, 0.2, 'lava')                                # glow around the eyes
        h1 = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 4.4, 20.5, -12], hd)
        cb(h1, sx * 5.0, 20.0, -12.0, 2.6, 2.6, 2.6, 'rock_l')
        h2 = m.bone('horn2_' + ('r' if sx > 0 else 'l'), [sx * 5.6, 22.5, -12], h1)
        cb(h2, sx * 5.8, 22.4, -11.4, 1.6, 2.0, 1.6, 'rock'); cb(h2, sx * 6.0, 24.2, -10.8, 0.9, 1.2, 0.9, 'rock_d')
    mw = m.bone('maw', [0, 14, -17], hd)
    cb(mw, 0, 14.0, -17.5, 6.4, 1.0, 0.3, 'lava_y')                                        # glowing mouth seam
    jw = m.bone('jaw', [0, 14, -12], hd)
    cb(jw, 0, 11.0, -14.4, 8.0, 3.0, 5.6, 'rock', decals={'north': pix(["k.k.k.k"], {'k': '#ff7a14'})})
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 4.0, 24.0, 3.0], body)
        ro = dict(rot=('z', -sx * 22.5), rot_origin=[sx * 4.0, 24.0, 3.0])
        cb(w, sx * 9.0, 23.0, 3.0, 10.0, 2.0, 2.0, 'rock', **ro)                              # wing arm
        cb(w, sx * 4.6, 22.6, 3.0, 2.6, 2.6, 2.6, 'rock_l')                                   # shoulder joint
        w2 = m.bone('wing_' + side + '2', [sx * 4.0, 24.0, 3.0], w)
        for k, (zz, L) in enumerate(((3.6, 9.0), (7.0, 8.0), (10.0, 6.0))):                   # finger bones fanning back
            cb(w2, sx * 13.6, 23.6, 3.0 + zz / 2, 1.0, 1.0, zz + 1, 'rock_d', **ro)
        cb(w2, sx * 9.8, 23.6, 7.6, 8.8, 0.5, 9.0, 'mem',
           decals={f: [('lerp', '#ff6a14', 0.1, 0.9, 'y'), ('rect', 0.0, 0.48, 1, 0.52, '#3a1a10')] for f in ('up', 'down')}, **ro)   # lava-lit membrane
        wt = m.bone('wingtip_' + side, [sx * 14, 24, 3], w)
        cb(wt, sx * 14.6, 23.0, 2.6, 2.4, 2.4, 2.4, 'rock', **ro); cb(wt, sx * 15.2, 25.0, 1.6, 0.8, 1.8, 0.8, 'rock_d', **ro)   # wrist claw
    for (n, x, z) in (('leg_fr', 4.2, -3.0), ('leg_fl', -4.2, -3.0), ('leg_br', 5.0, 8.0), ('leg_bl', -5.0, 8.0)):
        lg = m.bone(n, [x, 10, z], body)
        cb(lg, x, 6.8, z, 3.0, 3.6, 3.0, 'rock', decals={f: [('rect', 0, 0.45, 1, 0.55, '#ff7a14')] for f in ('north', 'south', 'east', 'west')})
        cb(lg, x, 4.4, z, 2.2, 2.4, 2.2, 'rock_l')
        cb(lg, x, 3.4, z - 0.4, 2.8, 1.0, 2.8, 'rock_d')
        for dx in (-0.9, 0.0, 0.9):
            cb(lg, x + dx, 2.4, z - 1.6, 0.6, 1.2, 0.8, 'rock_d')                              # claws
    t1 = m.bone('tail', [0, 12, 11], body)
    cb(t1, 0, 10.6, 12.8, 4.0, 4.0, 4.0, 'rock', decals={f: [('rect', 0, 0.45, 1, 0.55, '#ff7a14')] for f in ('east', 'west', 'up')})
    t2 = m.bone('tail2', [0, 11.4, 14.8], t1); cb(t2, 0, 10.2, 16.0, 3.0, 3.0, 3.0, 'rock_l')
    t3 = m.bone('tail3', [0, 11, 17.4], t2); cb(t3, 0, 10.0, 18.6, 1.8, 1.8, 2.6, 'rock_d'); cb(t3, 0, 11.6, 18.6, 0.8, 1.4, 0.8, 'rock_d')
    m.hitbox(2.2, 2.4)
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, 0, -a], [0, 0, a * 0.5]], L)}, 'wing_l': {'rotation': loop([[0, 0, a], [0, 0, -a * 0.5]], L)}}
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.4, 0]], 2.0)}, 'tail': {'rotation': loop([[0, 10, 0], [0, -10, 0]], 2.0)}}
    idle.update(flap(0.6, 30))
    m.anim('idle', 2.0, 'loop', idle)
    walk = dict(idle); walk.update(flap(0.4, 40)); walk['body'] = {'rotation': loop([[8, 0, 0], [8, 0, 0]], 0.6)}
    m.anim('walk', 0.6, 'loop', walk)
    m.anim('attack', 1.3, 'once', {'head': {'rotation': [(0, [0, 0, 0]), (0.4, [-15, 0, 0]), (0.6, [12, 0, 0]), (1.3, [0, 0, 0])]},
                                   'jaw': {'rotation': [(0, [0, 0, 0]), (0.5, [25, 0, 0]), (0.8, [25, 0, 0]), (1.3, [0, 0, 0])]}})
    common_tail(m)
    return m


