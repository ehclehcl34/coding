def barbarian_hut():
    """HQ vanilla-like Barbarian Hut: stone base + steps, plaster walls, thick wooden posts with steel studs,
    dark doorway, team-coloured plank gable roof, big sword on the roof, round target on an A-stand, elixir puddle"""
    m = new_model('clash_barbarian_hut')
    m.mats_({'stone': ('#a8a8a4', 'stone'), 'plaster': ('#c4c6c8', 'stone'), 'wood': ('#c08a4a', 'wood', {'planks': True}),
             'wood_d': ('#8a5a30', 'wood'), 'roof': ('#efefef', 'wood', {'planks': True}), 'steel': ('#b8c0c8', 'metal'),
             'void': ('#1a1612', 'plain'), 'gold': ('#e8b830', 'metal'), 'grip': ('#6a4426', 'leather'), 'elixir': ('#e040c8', 'glow')})
    root = m.bone('root', [0, 0, 0])
    top = m.bone('top', [0, 0, 0], root)
    cb(top, 0, 0, 0, 25, 2.0, 23, 'stone')                                              # stone base
    cb(top, 0, 0, -13.2, 9, 1.4, 3.4, 'stone')                                          # steps
    cb(top, 0, 1.4, -12.4, 9, 1.2, 1.8, 'stone')
    cb(top, 0, 2.0, 0.6, 19, 14, 17, 'plaster')                                         # walls
    cb(top, 0, 2.0, -8.0, 7.0, 10.0, 0.4, 'void')                                        # dark doorway
    stud = {'north': pix(["....", ".kk.", ".kk.", "....", "....", "....", "....", ".kk.", ".kk.", "...."], {'k': '#b8c0c8'})}
    for sx in (1, -1):
        for sz in (1, -1):
            cb(top, sx * 10.0, 0, sz * 8.6, 3.2, 18.0, 3.2, 'wood', decals=stud if sz < 0 else {})   # thick corner posts
            for y in (6.0, 12.0):
                if sz < 0:
                    cb(top, sx * 10.0, y, -10.4, 1.2, 1.2, 0.6, 'steel')                 # diamond studs
        cb(top, sx * 4.4, 2.0, -9.0, 1.8, 11.0, 1.6, 'wood_d')                          # door jambs
    for sz in (1, -1):
        cb(top, 0, 15.4, sz * 9.0, 24, 2.6, 2.6, 'wood')                                 # lintel beams
    for sx in (1, -1):
        cb(top, sx * 10.6, 15.4, 0, 2.4, 2.6, 18, 'wood')
    for k, (w, h) in enumerate(((19, 2.0), (13, 2.0), (7, 2.0))):                       # stepped plaster gables
        for sz in (1, -1):
            cb(top, 0, 18.0 + k * 2.0, sz * 8.0, w, h, 1.0, 'plaster')
    roof = m.bone('tc_shields', [0, 0, 0], top)                                          # team-coloured plank roof
    planks = [('rect', f, 0, f + 0.02, 1, '#b4b4b4') for f in (0.2, 0.4, 0.6, 0.8)]
    for sx in (1, -1):
        cb(roof, sx * 6.2, 21.0, 0, 13.6, 1.4, 22.0, 'roof', rot=('z', -sx * 22.5), rot_origin=[0, 24.6, 0],
           decals={'up': planks, 'down': planks})
        for (x, z) in ((sx * 4.0, -5.0), (sx * 8.0, 4.0)):
            cb(roof, x, 22.6 - abs(x) * 0.4, z, 3.4, 0.6, 3.0, 'roof', rot=('z', -sx * 22.5), rot_origin=[0, 24.6, 0])   # loose shingles
    cb(top, 0, 24.2, 0, 1.6, 1.6, 23.0, 'wood_d')                                        # ridge beam
    # big sword lying on the front of the roof
    sw = m.bone('tc_shield', [0, 15, -12.6], top)
    cb(top, -2.0, 17.2, -11.6, 13.0, 2.2, 0.8, 'steel', rot=('z', -22.5), rot_origin=[-2.0, 18.3, -11.6],
       decals={'north': [('rect', 0, 0.4, 1, 0.6, '#e0e6ec')]})                          # blade
    cb(top, 5.6, 19.4, -11.6, 1.2, 4.6, 1.4, 'gold', rot=('z', -22.5), rot_origin=[5.6, 21.7, -11.6])   # cross-guard
    cb(top, 8.0, 21.6, -11.6, 3.6, 1.2, 1.2, 'grip', rot=('z', -22.5), rot_origin=[8.0, 22.2, -11.6])   # grip
    cb(top, 10.2, 22.4, -11.6, 1.4, 1.4, 1.4, 'gold')                                     # pommel
    # round practice target on an A-frame stand
    tg = m.bone('target', [-15.5, 7, 4], top)
    for rot in (None, ('x', 45)):
        cb(tg, -15.5, 7 - 5.0, 4, 2.0, 10.0, 4.1, 'wood', rot=rot, rot_origin=[-15.5, 7, 4])
        cb(tg, -15.5, 7 - 2.05, 4, 2.0, 4.1, 10.0, 'wood', rot=rot, rot_origin=[-15.5, 7, 4])
        cb(tg, -15.4, 7 - 5.4, 4, 1.4, 10.8, 4.5, 'steel', rot=rot, rot_origin=[-15.5, 7, 4])   # steel rim
        cb(tg, -15.4, 7 - 2.25, 4, 1.4, 4.5, 10.8, 'steel', rot=rot, rot_origin=[-15.5, 7, 4])
    cb(tg, -16.8, 6.0, 4, 0.8, 2.0, 2.0, 'steel')                                         # centre boss
    for sz in (1, -1):
        cb(tg, -14.4, 0, 4 + sz * 2.4, 1.4, 6.0, 1.4, 'wood_d', rot=('x', sz * 22.5), rot_origin=[-14.4, 3, 4 + sz * 2.4])   # A-frame legs
    cb(top, -14.0, 0.05, 9.0, 5.0, 0.2, 3.4, 'elixir')                                   # elixir puddle
    m.hitbox(3.0, 2.0)
    m.anim('idle', 3.0, 'loop', {'target': {'rotation': loop([[0, 0, 0], [0, 0, 2], [0, 0, 0], [0, 0, -2]], 3.0)}})
    m.anim('attack', 0.5, 'once', {'top': {'scale': [(0, [1, 1, 1]), (0.15, [1.04, 0.96, 1.04]), (0.5, [1, 1, 1])]}})
    m.anim('deploy', 0.8, 'once', {'root': {'position': [(0, [0, -20, 0]), (0.6, [0, 1, 0]), (0.8, [0, 0, 0])]}})
    m.anim('death', 1.0, 'hold', {'root': {'scale': [(0, [1, 1, 1]), (0.6, [1.05, 0.5, 1.05]), (1.0, [1.1, 0.05, 1.1])]}})
    m.anim('hit', 0.3, 'once', {'top': {'position': [(0, [0, 0, 0]), (0.1, [0.6, 0, 0]), (0.2, [-0.6, 0, 0]), (0.3, [0, 0, 0])]}})
    shade_pass(m, ('wood', 'plaster', 'stone'))
    return m


