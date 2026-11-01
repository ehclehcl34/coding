def fine_sword(m, bone, x, y, z, L=10.0, gold='gold', grip='grip'):
    """detailed sword held at (x,y,z), blade pointing -Z: wrapped grip, round pommel, curved cross-guard,
    blade with bevelled edges + central fuller + tapered tip"""
    m.mats_({'blade': ('#c8d0d8', 'metal'), 'blade_l': ('#eef2f6', 'metal'), 'blade_d': ('#8a929c', 'metal')})
    wrap = [('rect', 0, k, 1, k + 0.12, '#3a2410') for k in (0.1, 0.4, 0.7)]
    cb(bone, x, y - 0.45, z + 0.4, 0.9, 0.9, 3.2, grip, decals={f: wrap for f in ('up', 'down', 'east', 'west')})   # wrapped grip
    cb(bone, x, y - 0.65, z + 2.4, 1.3, 1.3, 1.0, gold)                                     # pommel
    cb(bone, x, y - 0.4, z + 3.0, 0.8, 0.8, 0.4, gold)
    cb(bone, x, y - 0.5, z - 1.5, 1.0, 1.0, 0.8, gold)                                      # guard centre
    cb(bone, x, y - 0.45, z - 1.5, 4.6, 0.9, 0.7, gold)                                      # cross-guard
    for sx in (1, -1):
        cb(bone, x + sx * 2.5, y - 0.45, z - 1.9, 0.7, 0.9, 1.0, gold)                         # curled guard tips
    cb(bone, x, y - 0.35, z - 1.9 - L / 2, 1.8, 0.7, L, 'blade',
       decals={'up': [('rect', 0.42, 0, 0.58, 0.85, '#8a929c'), ('rect', 0, 0, 0.12, 1, '#eef2f6'), ('rect', 0.88, 0, 1, 1, '#eef2f6')],
               'down': [('rect', 0.42, 0, 0.58, 0.85, '#8a929c')]})                         # blade + fuller + bright edges
    cb(bone, x, y - 0.3, z - 1.9 - L - 0.6, 1.2, 0.6, 1.2, 'blade_l')                        # tapering tip
    cb(bone, x, y - 0.25, z - 1.9 - L - 1.4, 0.6, 0.5, 0.8, 'blade_l')


def knight():
    """HQ vanilla-like Knight: chainmail coif, blond curled moustache + brows, big nose, steel breastplate,
    team sash + team belt with gold buckle, chainmail skirt/sleeves, brown boots, fine sword"""
    m = new_model('clash_knight')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'mail': ('#8a929a', 'metal'), 'plate': ('#c8d0d8', 'metal'),
             'plate_d': ('#9aa4ae', 'metal'), 'hair': ('#f0c838', 'hair'), 'tc': ('#efefef', 'cloth'), 'gold': ('#e8b830', 'metal'),
             'boot': ('#6a4426', 'leather'), 'grip': ('#6a4426', 'leather'), 'eye': ('#ffffff', 'plain')})
    scale = [('px', i / 8, j / 8, '#5a626a') for i in range(0, 8, 2) for j in range(0, 8, 2)] + [('px', i / 8, j / 8, '#b0b8c0') for i in range(1, 8, 2) for j in range(1, 8, 2)]
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 10, 0], root)
        cb(lg, sx * 2, 1.6, 0, 3.6, 8.4, 3.6, 'skin')
        cb(lg, sx * 2, 0, -0.4, 4.2, 2.2, 5.0, 'boot', decals={'up': [('rect', 0.2, 0.5, 0.8, 0.7, '#9aa4ae')]})
    body = m.bone('body', [0, 10, 0], root)
    cb(body, 0, 7.4, 0, 9.0, 5.2, 5.0, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # chainmail skirt
    cb(body, 0, 12.0, 0, 9.4, 9.0, 5.4, 'plate', decals={'north': [('rect', 0.48, 0, 0.52, 1, '#9aa4ae'), ('shade', 0, 0.8, 1, 1, 0.85)]})   # breastplate
    cb(body, 0, 19.6, 0, 8.0, 1.2, 4.6, 'plate_d')                                          # gorget
    tc = m.bone('tc_surcoat', [0, 14, 0], body)
    cb(tc, 0, 11.6, 0, 9.8, 2.0, 5.8, 'tc')                                                  # team belt
    cb(tc, 0, 14.6, -2.85, 10.6, 1.8, 0.3, 'tc', rot=('z', -45), rot_origin=[0, 15.5, -2.85])   # team sash across the chest
    cb(tc, 0, 14.6, 2.85, 10.6, 1.8, 0.3, 'tc', rot=('z', 45), rot_origin=[0, 15.5, 2.85])
    cb(body, 2.0, 11.4, -2.95, 2.6, 2.4, 0.3, 'gold', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#3a6ae0')]})   # gold buckle
    hd = m.bone('head', [0, 20.6, 0], body)
    cb(hd, 0, 20.6, 0, 7.0, 7.0, 7.0, 'skin', decals={'north': pix([".......", ".......", ".......", ".we.ew.", ".......", ".......", "......."], {'w': '#ffffff', 'e': '#3a6aa8'})})
    cb(hd, 0, 23.0, -3.9, 1.4, 1.8, 1.0, 'skin_d')                                          # big nose
    hr = m.bone('hair', [0, 21, 0], hd)
    cb(hr, 0, 20.4, 0.3, 7.6, 7.8, 7.4, 'mail', decals={'north': [('rect', 0.12, 0.05, 0.88, 0.95, '#00000000')] if False else scale, 'east': scale, 'west': scale, 'south': scale, 'up': scale}, inflate=0)   # mail coif (front cut away below)
    cb(hr, 0, 20.4, -3.55, 6.0, 6.0, 0.2, 'skin')                                           # face opening
    for sx in (1, -1):
        cb(hr, sx * 1.7, 25.4, -3.9, 2.2, 0.8, 0.6, 'hair')                                   # blond brows
        cb(hr, sx * 1.3, 22.0, -4.0, 2.4, 0.9, 0.8, 'hair')                                   # moustache
        cb(hr, sx * 2.8, 21.6, -4.0, 0.9, 1.2, 0.8, 'hair'); cb(hr, sx * 3.3, 22.6, -4.0, 0.8, 0.9, 0.8, 'hair')   # curled tips
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5.6, 19.4, 0], body)
        cb(a, sx * 6.2, 15.4, 0, 3.6, 4.6, 3.6, 'mail', decals={f: scale for f in ('north', 'south', 'east', 'west')})   # mail sleeve
        cb(a, sx * 6.2, 18.2, 0, 4.2, 2.0, 4.6, 'plate_d')                                     # pauldron
        cb(a, sx * 6.2, 11.0, 0, 3.2, 4.6, 3.2, 'skin')
        cb(a, sx * 6.2, 9.4, -0.2, 3.4, 2.2, 3.4, 'skin_d')                                     # fist
    sw = m.bone('sword', [6.2, 10.4, 0], m.by_name('arm_r'))
    fine_sword(m, sw, 6.2, 10.6, 0.0, L=11.0)
    m.hitbox(0.9, 1.9)
    shade_pass(m, ('skin', 'plate'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-25, 0, 4], [-28, 0, 6]], 2.0)}})
    mc_walk(m, 0.8, 30, arm_r=False, extra={'arm_r': {'rotation': loop([[-25, 0, 4], [-35, 0, 4]], 0.8)}})
    m.anim('attack', 0.6, 'once', {'arm_r': {'rotation': [(0, [-25, 0, 4]), (0.2, [-160, 0, 10]), (0.35, [-10, 0, 0]), (0.6, [-25, 0, 4])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.2, [-6, 10, 0]), (0.35, [10, -10, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m)
    return m


