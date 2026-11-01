def ice_golem():
    """HQ vanilla-like Ice Golem: lumpy snow body, ice-crystal mohawk, glowing icy eyes, black rock nose,
    big toothy underbite, huge ice-crystal forearms + fists, black rock feet, team-coloured ice core crystals on the back"""
    m = new_model('clash_ice_golem')
    m.mats_({'snow': ('#eef2f8', 'soft'), 'snow_d': ('#d0d8e6', 'soft'), 'ice': ('#78c8f0', 'gem'), 'ice_l': ('#b8e6ff', 'gem'),
             'coal': ('#2a2a30', 'stone'), 'eye': ('#70e0ff', 'glow'), 'tooth': ('#ffffff', 'bone'), 'cry': ('#f4f8ff', 'gem')})
    r = Rig(m, 1.0); B = r.box
    def lump(bone, x, y, z, w, h, d, mat='snow'):
        B(bone, x, y + 0.8, z, w, h - 1.6, d, mat); B(bone, x, y, z, w - 1.6, h, d - 1.6, mat)
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 3.0
        lg = r.bone('leg_' + side, [x, 8, 0.6], root)
        lump(lg, x, 2.6, 0.6, 4.6, 5.6, 4.6)
        lump(lg, x, 0, 0.0, 5.2, 2.8, 6.0, 'coal')                                         # black rock feet
    body = r.bone('body', [0, 8, 0], root)
    lump(body, 0, 7.4, 1.0, 10.0, 5.6, 7.4, 'snow_d')                                     # hips
    lump(body, 0, 12.0, 0.4, 15.0, 8.4, 9.6)                                              # big chest
    lump(body, 0, 19.6, 2.4, 10.0, 3.4, 6.0, 'snow_d')                                    # hunched back
    tc = r.bone('tc_core', [0, 21, 4], body)                                              # team ice crystals on the back
    for (x, y, z, w, h, rot) in ((0.0, 21.6, 4.6, 2.2, 4.0, None), (-2.0, 21.2, 4.4, 1.6, 3.0, ('z', 22.5)), (2.2, 21.2, 4.2, 1.6, 3.2, ('z', -22.5))):
        B(tc, x, y, z, w, h, w, 'cry', **(dict(rot=rot, rot_origin=[x, y, z]) if rot else {}), decals={'north': [('rect', 0.15, 0, 0.35, 1, '#ffffff')]})
    hd = r.bone('head', [0, 18, -3.6], body)
    lump(hd, 0, 15.6, -4.4, 7.0, 6.4, 5.8)                                               # head sunk between the shoulders
    for (x, z, h) in ((-1.6, -3.0, 3.0), (0.0, -2.0, 4.0), (1.4, -1.0, 3.4), (0.0, 0.2, 3.0), (-0.6, 1.4, 2.4)):
        B(hd, x, 21.6, z, 1.6, h, 1.8, 'ice', rot=('x', -22.5), rot_origin=[x, 21.6, z], decals={'north': [('rect', 0.2, 0, 0.4, 1, '#b8e6ff')]})   # ice mohawk
    for sx in (1, -1):
        B(hd, sx * 1.8, 19.4, -7.4, 1.8, 0.7, 0.2, 'eye', rot=('z', sx * 22.5), rot_origin=[sx * 1.8, 19.75, -7.4])   # icy glowing eyes
        B(hd, sx * 1.8, 20.2, -7.5, 2.4, 0.8, 0.6, 'snow_d')                               # brows
    B(hd, 0, 17.6, -7.8, 2.0, 2.0, 1.2, 'coal')                                           # black rock nose
    B(hd, 0, 15.0, -7.6, 6.4, 2.4, 1.6, 'snow', decals={'north': pix(["t.t.t.t", "ttttttt", "......."], {'t': '#ffffff'})})   # underbite with teeth
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 9.8
        a = r.bone('arm_' + side, [x, 19, 1], body)
        lump(a, x, 14.4, 1.0, 5.6, 5.6, 5.6)                                               # snow shoulder
        lump(a, x + sx * 0.3, 9.4, 0.6, 4.4, 5.6, 4.4, 'snow_d')                            # upper arm
        B(a, x + sx * 0.6, 2.6, 0.2, 5.6, 7.4, 5.6, 'ice', decals={f: [('rect', 0.2, 0, 0.3, 1, '#b8e6ff'), ('rect', 0.6, 0.3, 0.68, 1, '#5aa8d8')] for f in ('north', 'south', 'east', 'west')})   # ice forearm
        B(a, x + sx * 0.6, -1.4, -0.4, 6.8, 4.6, 6.8, 'ice')                                # big ice fist
        for dz in (-2.4, -0.8, 0.8, 2.4):
            B(a, x + sx * 0.6, -2.2, -3.8 + (dz + 2.4) * 0 + 0, 1.4, 1.6, 1.4, 'ice_l') if False else None
        for dx in (-2.2, -0.7, 0.8, 2.3):
            B(a, x + sx * 0.6 + dx, -2.0, -4.0, 1.3, 2.0, 1.2, 'ice_l')                     # crystal knuckles
        B(a, x + sx * 0.6, 7.6, 2.6, 2.0, 2.6, 1.4, 'ice_l', rot=('x', -22.5), rot_origin=[x, 7.6, 2.6])   # crystal shard on the back of the arm
    m.hitbox(1.6, 2.2)
    shade_pass(m, ('snow',))
    mc_idle(m, 2.4, extra={'body': {'rotation': loop([[12, 0, 0], [14, 0, 0]], 2.4)}})
    mc_walk(m, 1.0, 20, extra={'body': {'rotation': loop([[14, 0, -3], [14, 0, 3]], 1.0)}})
    slam = {s: {'rotation': [(0, [0, 0, 0]), (0.35, [-150, 0, 0]), (0.55, [-15, 0, 0]), (1.0, [0, 0, 0])]} for s in ('arm_r', 'arm_l')}
    m.anim('attack', 1.0, 'once', slam)
    common_tail(m)
    return m


