def barbarian_barrel():
    """HQ vanilla-like Barbarian Barrel: octagonal wooden barrel (axis X) with team hoops + steel spikes,
    barbarian head poking out of one end, sandaled feet out of the other, rolls forward"""
    m = new_model('clash_barbarian_barrel')
    m.mats_({'wood': ('#a8743e', 'wood', {'planks': True}), 'wood_d': ('#6a4424', 'wood'), 'hoop': ('#efefef', 'metal'),
             'steel': ('#a8b0b8', 'metal'), 'skin': ('#e8a878', 'skin'), 'hair': ('#f0c848', 'hair'), 'sandal': ('#4a3020', 'leather'),
             'grip': ('#6a4426', 'leather'), 'gold': ('#e8b830', 'metal')})
    cy, R, L = 12.0, 8.6, 22.0
    roll = m.bone('roll', [0, cy, 0], None)
    staves = [('rect', 0, f, 1, f + 0.03, '#6a4424') for f in (0.2, 0.4, 0.6, 0.8)]
    for rot in (None, ('x', 45)):
        cb(roll, 0, cy - R, 0, L, 2 * R, 0.83 * R, 'wood', rot=rot, rot_origin=[0, cy, 0],
           decals={f: staves for f in ('north', 'south', 'up', 'down')})
        cb(roll, 0, cy - 0.415 * R, 0, L, 0.83 * R, 2 * R, 'wood', rot=rot, rot_origin=[0, cy, 0],
           decals={f: staves for f in ('north', 'south', 'up', 'down')})
    for sx in (1, -1):
        cb(roll, sx * (L / 2 - 0.2), cy - 0.6 * R, 0, 0.6, 1.2 * R, 1.2 * R, 'wood_d')       # dark end lids
    hp = m.bone('tc_hoops', [0, cy, 0], roll)
    sp = m.bone('spikes', [0, cy, 0], roll)
    for hx in (-6.8, 6.8):
        for rot in (None, ('x', 45)):
            cb(hp, hx, cy - R - 0.3, 0, 2.6, 2 * R + 0.6, 0.83 * R + 0.3, 'hoop', rot=rot, rot_origin=[0, cy, 0])
            cb(hp, hx, cy - 0.415 * R - 0.15, 0, 2.6, 0.83 * R + 0.3, 2 * R + 0.6, 'hoop', rot=rot, rot_origin=[0, cy, 0])
        for (dy, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):                               # spikes on each hoop
            for k, (w, o) in enumerate(((1.6, 0.0), (0.9, 1.2))):
                h = 1.2
                y = cy + dy * (R + 0.3 + o) + (0 if dy >= 0 else -h)
                z = dz * (R + 0.3 + o + (h / 2 if dz else 0))
                if dz:
                    cb(sp, hx, cy - w / 2, z, w, w, h, 'steel')
                else:
                    cb(sp, hx, y, 0, w, h, w, 'steel')
    sw = m.bone('sword', [0, 24, 0], roll)                                                # sword hilt poking out between staves
    cb(sw, -2.0, cy + R - 0.4, 0, 0.9, 3.0, 0.9, 'grip')
    cb(sw, -2.0, cy + R - 0.6, 0, 2.6, 0.6, 0.8, 'gold')
    cb(sw, -2.0, cy + R + 2.6, 0, 1.1, 0.8, 1.1, 'gold')
    for sz in (1, -1):                                                                    # feet out of the back end
        cb(roll, -L / 2 - 2.0, cy - 2.0, sz * 2.4, 4.0, 3.2, 3.0, 'skin')
        cb(roll, -L / 2 - 4.2, cy - 2.4, sz * 2.4, 1.0, 4.0, 3.6, 'sandal',
           decals={'west': pix(["....", "kkkk", "....", "...."], {'k': '#e8a878'})})
    pk = m.bone('peek', [L / 2, cy, 0], None)                                            # barbarian head out of the front end
    face = pix(["........", "........", "........", ".wb..bw.", "........", "........", ".k....k.", "..kkkk.."],
               {'w': '#ffffff', 'b': '#3a7ad8', 'k': '#6a3a2a'})
    hx = L / 2 + 1.6
    cb(pk, hx, cy - 2.6, 0, 6.0, 6.8, 6.8, 'skin', decals={'east': face})
    cb(pk, hx + 3.2, cy - 0.4, 0, 1.0, 2.0, 1.6, 'skin')                                   # nose
    cb(pk, hx, cy + 4.0, 0, 6.6, 2.2, 7.4, 'hair')                                         # blond hair
    for sz in (1, -1):
        cb(pk, hx + 0.6, cy - 2.4, sz * 3.6, 5.0, 6.4, 0.8, 'hair')                          # side locks
    cb(pk, hx + 3.2, cy - 1.6, 0, 0.8, 1.2, 5.0, 'hair')                                   # moustache bar
    for sz in (1, -1):
        cb(pk, hx + 3.2, cy - 3.6, sz * 2.2, 0.8, 2.2, 1.0, 'hair')
    m.hitbox(1.8, 1.4)
    m.anim('idle', 0.589, 'loop', {'roll': {'rotation': [(0, [0, 0, 0]), (0.196, [-120, 0, 0]), (0.393, [-240, 0, 0]), (0.589, [-360, 0, 0])]},
                                   'peek': {'position': loop([[0, 0, 0], [0, 0.6, 0]], 0.589)}}, interp='linear')
    return m


