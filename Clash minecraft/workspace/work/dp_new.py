def dark_prince():
    """HQ vanilla-like Dark Prince: bucket helm with rivets + eye slit, team plume, dark steel cuirass, chainmail,
    spiked block mace, wooden crown shield with steel rim, riding a brown pony with blond mane, bridle + team saddle cloth"""
    m = new_model('clash_dark_prince')
    m.mats_({'steel': ('#5a6068', 'metal'), 'steel_l': ('#8a929a', 'metal'), 'mail': ('#7a828a', 'metal'), 'skin': ('#e8a878', 'skin'),
             'pony': ('#7a4a32', 'fur'), 'pony_d': ('#5a3424', 'fur'), 'muzzle': ('#d8906a', 'skin'), 'mane': ('#e8cc6a', 'hair'),
             'strap': ('#8a3a2a', 'leather'), 'tc': ('#efefef', 'cloth'), 'wood': ('#7a4a2a', 'wood', {'planks': True}),
             'gold': ('#e8b830', 'metal'), 'grip': ('#5a3a22', 'leather'), 'hoof': ('#3a2a20', 'plain'), 'eye': ('#ffffff', 'plain')})
    mail = [('px', i / 6, j / 6, '#5a626a') for i in range(0, 6, 2) for j in range(0, 6, 2)]
    root = m.bone('root', [0, 0, 0])
    # ---- pony
    pony = m.bone('pony', [0, 9, 0], root)
    cb(pony, 0, 7.4, 1.0, 8.0, 7.0, 15.0, 'pony')                                       # barrel body
    cb(pony, 0, 7.0, 1.0, 6.6, 0.6, 12.0, 'pony_d')
    for i, (lx, lz) in enumerate(((2.6, -4.6), (-2.6, -4.6), (2.6, 6.2), (-2.6, 6.2))):
        lg = m.bone('leg_%d' % i, [lx, 8, lz], pony)
        cb(lg, lx, 2.0, lz, 2.8, 6.4, 2.8, 'pony')
        cb(lg, lx, 1.0, lz, 3.4, 1.8, 3.4, 'mane')                                          # shaggy fetlock
        cb(lg, lx, 0, lz, 2.8, 1.0, 2.8, 'hoof')
    nk = m.bone('pony_head', [0, 13, -6], pony)
    cb(nk, 0, 12.0, -7.6, 5.0, 6.4, 5.0, 'pony')                                         # neck
    cb(nk, 0, 15.0, -11.4, 5.0, 4.8, 6.4, 'pony')                                        # head
    cb(nk, 0, 14.4, -15.0, 4.4, 4.0, 2.6, 'muzzle', decals={'north': pix(["....", "k..k", "....", ".kk."], {'k': '#5a2a1a'})})   # muzzle, nostrils, mouth
    for sx in (1, -1):
        cb(nk, sx * 2.6, 17.2, -11.0, 0.4, 1.0, 1.0, 'eye', decals={'east': pix(["k"], {'k': '#1a1010'}), 'west': pix(["k"], {'k': '#1a1010'})})
        cb(nk, sx * 1.6, 19.8, -9.6, 1.2, 1.8, 1.0, 'pony_d')                              # ears
        cb(nk, sx * 2.6, 14.6, -13.6, 0.4, 1.4, 1.4, 'steel_l')                            # bridle rings
    tcr = m.bone('tc_reins', [0, 15, -12], nk)
    cb(tcr, 0, 16.6, -12.6, 5.4, 0.8, 1.0, 'tc'); cb(tcr, 0, 14.4, -14.0, 4.8, 0.8, 0.6, 'tc')   # bridle
    for sx in (1, -1):
        cb(tcr, sx * 2.7, 14.6, -9.6, 0.4, 0.8, 6.0, 'tc')
    cb(nk, 0, 18.4, -8.0, 1.6, 2.0, 8.0, 'mane'); cb(nk, 0, 17.2, -13.0, 3.6, 1.6, 2.0, 'mane')   # mane + forelock
    for sx in (1, -1):
        cb(nk, sx * 1.4, 13.6, -7.0, 0.8, 5.4, 5.0, 'mane')
    cb(pony, 0, 10.6, 9.2, 2.0, 3.6, 2.0, 'mane'); cb(pony, 0, 7.4, 9.8, 2.4, 3.4, 2.0, 'mane')   # tail
    sad = m.bone('tc_saddle', [0, 14.4, 1], pony)
    cb(sad, 0, 14.2, 1.4, 8.6, 0.8, 7.0, 'tc')
    for sx in (1, -1):
        cb(sad, sx * 4.3, 9.6, 1.4, 0.4, 5.0, 6.4, 'tc', decals={'east': [('rect', 0, 0.85, 1, 1, '#c8c8c8')], 'west': [('rect', 0, 0.85, 1, 1, '#c8c8c8')]})
    # ---- rider
    body = m.bone('body', [0, 16, 1], pony)
    for sx in (1, -1):
        cb(body, sx * 3.0, 14.6, 0.0, 2.6, 2.4, 5.0, 'mail', decals={'east': mail, 'west': mail, 'up': mail})   # thighs astride
        cb(body, sx * 4.3, 10.6, -1.6, 2.2, 5.0, 2.4, 'mail', decals={'east': mail, 'west': mail})
        cb(body, sx * 4.3, 9.6, -2.0, 2.6, 1.4, 3.4, 'grip')                               # boots
    cb(body, 0, 15.4, 1.0, 6.8, 2.6, 4.4, 'mail', decals={'north': mail, 'south': mail})
    cb(body, 0, 15.6, 1.0, 7.4, 1.2, 4.8, 'grip'); cb(body, 0, 15.5, -1.45, 1.6, 1.4, 0.3, 'gold')   # belt + buckle
    cb(body, 0, 16.8, 1.0, 7.6, 7.6, 4.6, 'steel', decals={'north': [('rect', 0.48, 0, 0.52, 1, '#8a929a')]})   # cuirass
    for sx in (1, -1):
        cb(body, sx * 4.4, 22.2, 1.0, 2.8, 2.4, 4.8, 'steel')                              # pauldrons
    hd = m.bone('head', [0, 24.4, 1], body)
    slit = [('rect', 0.12, 0.42, 0.88, 0.62, '#e8a878'), ('px', 0.3, 0.5, '#2a1a10'), ('px', 0.7, 0.5, '#2a1a10'), ('rect', 0.45, 0.55, 0.55, 0.75, '#c87a5a')]
    cb(hd, 0, 24.4, 1.0, 7.0, 8.0, 7.0, 'steel', decals={'north': slit + [('rect', 0.48, 0, 0.52, 0.42, '#8a929a')]})   # bucket helm
    for y in (25.0, 31.2):
        cb(hd, 0, y, 1.0, 7.4, 0.8, 7.4, 'steel_l')                                        # bands
    for sx in (1, -1):
        cb(hd, sx * 2.6, 31.4, -2.75, 0.8, 0.8, 0.4, 'steel_l'); cb(hd, sx * 2.6, 25.2, -2.75, 0.8, 0.8, 0.4, 'steel_l')   # rivets
    pl = m.bone('tc_plume', [0, 32.4, 1.0], hd)
    cb(pl, 0, 32.4, 1.0, 1.2, 1.6, 1.2, 'steel_l')
    for k, (y, z, h) in enumerate(((34.0, 1.6, 2.4), (35.6, 3.0, 2.0), (36.2, 4.8, 1.8), (35.6, 6.6, 1.6))):
        cb(pl, 0, y, z, 1.4, h, 2.0, 'tc')                                                # curling plume
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 5.2
        a = m.bone('arm_' + side, [x, 23.0, 1.0], body)
        cb(a, x, 18.4, 1.0, 2.4, 4.6, 2.6, 'mail', decals={'north': mail, 'east': mail, 'west': mail})
        cb(a, x, 15.0, 1.0, 2.8, 3.6, 2.8, 'steel')                                        # gauntlet
    mace = m.bone('mace', [5.2, 15.6, 1.0], m.by_name('arm_r'))
    cb(mace, 5.2, 15.2, -1.6, 0.9, 0.9, 6.0, 'grip')                                      # haft (forward)
    cb(mace, 5.2, 13.6, -6.6, 4.2, 4.2, 4.2, 'steel')                                     # block head
    for (dx, dy, dz) in ((2.4, 1.5, 0), (-2.4, 1.5, 0), (0, 3.8, 0), (0, -0.8, 0), (0, 1.5, -2.4)):
        cb(mace, 5.2 + dx * 1.0, 13.6 + dy + (0.3 if dy == 3.8 else 0), -6.6 + dz, 1.6 if dx else 1.6, 1.6, 1.6, 'steel_l')   # pyramid spikes
    sh = m.bone('shield', [-6.6, 18, 1], m.by_name('arm_l'))
    cb(sh, -6.8, 13.6, 1.0, 0.8, 9.0, 7.4, 'wood', decals={'west': [('rect', 0.3, 0.35, 0.7, 0.6, '#e8b830')]})   # wooden shield
    cb(sh, -7.0, 13.2, 1.0, 0.6, 9.8, 8.2, 'steel_l')                                     # steel rim (behind)
    for dz in (-2.6, 2.6):
        cb(sh, -7.3, 22.4, 1.0 + dz, 0.6, 1.8, 2.2, 'steel_l')                             # notched top
    cb(sh, -7.3, 16.6, 1.0, 0.4, 2.6, 3.4, 'gold', decals={'west': pix(["k.k.k", "kkkkk", "kkkkk"], {'k': '#f0c848'})})   # crown emblem
    m.hitbox(1.4, 2.4)
    shade_pass(m, ('pony', 'steel', 'wood', 'mane'))
    hold = {'arm_r': {'rotation': loop([[-30, 0, 0], [-34, 0, 0]], 2.0)}, 'arm_l': {'rotation': loop([[-10, 0, 0], [-12, 0, 0]], 2.0)},
            'pony_head': {'rotation': loop([[0, 0, 0], [6, 0, 0]], 2.0)}}
    m.anim('idle', 2.0, 'loop', hold)
    gal = {('leg_%d' % i): {'rotation': loop([[-35 if i in (0, 3) else 35, 0, 0], [35 if i in (0, 3) else -35, 0, 0]], 0.5)} for i in range(4)}
    gal['pony'] = {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.25)}
    gal.update({k: {'rotation': loop([v['rotation'][0][1], v['rotation'][0][1]], 0.5)} for k, v in hold.items() if k.startswith('arm')})
    m.anim('walk', 0.5, 'loop', gal)
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 0]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, -10]), (0.6, [-30, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-8, 15, 0]), (0.35, [12, -15, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m, hit_bone='pony')
    return m


