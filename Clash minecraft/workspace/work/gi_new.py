def giant():
    """HQ vanilla-like Giant: bald head, ginger hair ring + big bushy beard/moustache, heavy brow, big nose,
    laced leather vest, team belt with brass buckle, dark shorts, huge fists, bare feet"""
    m = new_model('clash_giant')
    m.mats_({'skin': ('#eeb08a', 'skin'), 'skin_d': ('#d08e68', 'skin'), 'beard': ('#d8783a', 'hair'), 'beard_d': ('#b45a24', 'hair'),
             'vest': ('#8a5a36', 'leather'), 'vest_d': ('#6a4224', 'leather'), 'lace': ('#d8c0a0', 'rope'), 'belt': ('#efefef', 'leather'),
             'brass': ('#c89a40', 'metal'), 'shorts': ('#4a3428', 'cloth')})
    D = '#c88a64'
    r = Rig(m, 1.75); B = r.box
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 2.4
        lg = r.bone('leg_' + side, [x, 11, 0], root)
        B(lg, x, 1.2, 0, 4.0, 9.8, 4.0, 'skin')
        B(lg, x, 8.0, 0, 4.4, 3.4, 4.4, 'shorts')                                         # shorts legs
        B(lg, x, 0, -0.6, 4.4, 1.4, 5.4, 'skin_d', decals={'north': pix(["k.k.k.k", "......."], {'k': D})})   # bare feet + toes
    body = r.bone('body', [0, 11, 0], root)
    lace = pix(["...k...", "..k.k..", "...k...", "..k.k..", "...k...", "..k.k..", "...k..."], {'k': '#d8c0a0'})
    B(body, 0, 11.0, 0, 9.0, 3.0, 5.0, 'shorts')
    B(body, 0, 13.6, 0, 9.6, 11.0, 5.4, 'vest', decals={'north': [('rect', 0.42, 0, 0.58, 1, '#eeb08a')] + lace, 'south': [('shade', 0, 0.8, 1, 1, 0.8)]})   # laced vest open at the chest
    B(body, 0, 12.6, -0.1, 10.0, 1.4, 5.6, 'vest_d', decals={'north': pix(["k.k.k.k.k"], {'k': '#5a3418'})})   # ragged hem
    tc = r.bone('tc_belt', [0, 14, 0], body)
    B(tc, 0, 13.6, 0, 10.0, 1.8, 5.8, 'belt')                                            # team belt
    B(body, 0, 13.4, -2.95, 2.4, 2.2, 0.3, 'brass', decals={'north': [('rect', 0.25, 0.25, 0.75, 0.75, '#6a4a18')]})   # buckle
    for sx in (1, -1):
        B(body, sx * 4.0, 23.6, 0, 3.6, 1.2, 5.6, 'vest_d')                              # shoulder seams
    hd = r.bone('head', [0, 24.6, -0.4], body)
    face = pix(["........", "........", "........", ".kw..wk.", "........", "........", "........", "........"], {'k': '#3a2a1a', 'w': '#ffffff'})
    B(hd, 0, 24.6, -0.4, 7.0, 7.4, 7.0, 'skin', decals={'north': face, 'up': [('rect', 0.3, 0.3, 0.7, 0.7, '#f8c8a0')]})   # bald head
    B(hd, 0, 28.6, -4.1, 7.2, 1.0, 0.6, 'skin_d')                                        # heavy brow
    B(hd, 0, 26.4, -4.3, 1.8, 2.2, 1.2, 'skin_d')                                        # big nose
    for sx in (1, -1):
        B(hd, sx * 3.6, 26.6, -0.4, 0.4, 3.4, 6.0, 'beard')                               # ginger side hair
        B(hd, sx * 3.7, 26.6, 0.4, 0.4, 1.6, 1.4, 'skin')                                 # ears
    B(hd, 0, 26.6, 3.15, 7.2, 3.4, 0.4, 'beard')                                          # back hair ring
    B(hd, 0, 24.6, -4.1, 6.4, 1.0, 1.0, 'beard')                                         # moustache
    B(hd, 0, 21.6, -3.7, 7.2, 3.4, 2.0, 'beard', decals={'north': pix(["k.k.k.k", ".k.k.k."], {'k': '#b45a24'})})   # bushy beard
    B(hd, 0, 23.2, -2.4, 7.4, 2.8, 4.0, 'beard')
    B(hd, 0, 20.8, -3.2, 4.6, 1.2, 1.4, 'beard_d')
    for sx, side in ((1, 'r'), (-1, 'l')):
        x = sx * 6.6
        a = r.bone('arm_' + side, [x, 23.0, 0], body)
        B(a, x, 18.6, 0, 4.4, 5.6, 4.4, 'skin')                                           # huge shoulders / biceps
        B(a, x, 12.6, 0, 3.8, 6.0, 3.8, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.7, D)]})
        B(a, x, 9.6, -0.2, 4.6, 3.4, 4.6, 'skin_d', decals={'north': pix(["k.k.k", ".....", "....."], {'k': D})})   # big fist
    m.hitbox(1.8, 3.8)
    shade_pass(m, ('skin', 'vest'))
    mc_idle(m, 2.4)
    mc_walk(m, 1.4, 22)
    m.anim('attack', 1.2, 'once', {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.4, [-150, 0, 10]), (0.6, [-20, 0, 0]), (1.2, [0, 0, 0])]},
                                   'body': {'rotation': [(0, [0, 0, 0]), (0.4, [-8, 10, 0]), (0.6, [12, -8, 0]), (1.2, [0, 0, 0])]}})
    common_tail(m)
    return m


