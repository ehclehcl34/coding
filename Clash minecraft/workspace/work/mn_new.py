def miner():
    """HQ vanilla-like Miner: dark mining helmet with brim + candle lamp, big grin, brown hair/sideburns,
    team sleeveless shirt, leather suspenders + belt with brass buckle, blue-ish trousers, boots, shovel"""
    m = new_model('clash_miner')
    m.mats_({'skin': ('#e8a878', 'skin'), 'skin_d': ('#c88a5e', 'skin'), 'hair': ('#6a3a1e', 'hair'), 'helm': ('#3a4048', 'metal'),
             'helm_l': ('#5a626c', 'metal'), 'wax': ('#f0e6c8', 'bone'), 'flame': ('#ffc040', 'glow'), 'tc': ('#efefef', 'cloth'),
             'strap': ('#6a4224', 'leather'), 'brass': ('#c89a40', 'metal'), 'pants': ('#efefef', 'cloth'), 'boot': ('#4a3020', 'leather'),
             'wood': ('#7a4a26', 'wood'), 'steel': ('#3a4048', 'metal'), 'steel_l': ('#6a727c', 'metal')})
    root = m.bone('root', [0, 0, 0])
    for sx, side in ((1, 'r'), (-1, 'l')):
        lg = m.bone('leg_' + side, [sx * 2, 12, 0], root)
        tp = m.bone('tc_pants_' + side, [sx * 2, 12, 0], lg)
        cb(tp, sx * 2, 2.4, 0, 4, 9.6, 4, 'pants', decals={'north': [('shade', 0, 0, 1, 1, 0.85)]})   # trousers (team, darker)
        cb(lg, sx * 2, 0, -0.3, 4.4, 2.8, 4.8, 'boot')
    body = m.bone('body', [0, 12, 0], root)
    tc = m.bone('tc_shirt', [0, 12, 0], body)
    cb(tc, 0, 12, 0, 8.4, 12, 4.4, 'tc')                                                   # team sleeveless shirt
    for sx in (1, -1):
        cb(body, sx * 2.6, 15.6, -2.3, 1.2, 8.4, 0.3, 'strap'); cb(body, sx * 2.6, 15.6, 2.3, 1.2, 8.4, 0.3, 'strap')   # suspenders
        cb(body, sx * 2.6, 23.6, 0, 1.2, 0.5, 4.8, 'strap')
    cb(body, 0, 12.4, 0, 8.8, 1.6, 4.8, 'strap'); cb(body, 1.6, 12.2, -2.5, 2.0, 2.0, 0.3, 'brass')   # belt + buckle
    cb(body, -3.2, 10.6, -1.8, 2.0, 2.4, 1.6, 'strap')                                       # pouch
    hd = m.bone('head', [0, 24, 0], body)
    face = pix(["........", "........", "........", ".kk..kk.", ".wb..bw.", "........", ".tttttt.", "..kkkk.."],
               {'k': '#4a2a14', 'w': '#ffffff', 'b': '#3a2a1a', 't': '#f8f6ee'})
    cb(hd, 0, 24, 0, 8, 8, 8, 'skin', decals={'north': face})
    cb(hd, 0, 27.0, -4.4, 1.6, 2.0, 1.0, 'skin_d')                                           # nose
    for sx in (1, -1):
        cb(hd, sx * 4.15, 25.4, 0.4, 0.4, 3.4, 4.0, 'hair')                                   # sideburns
    cb(hd, 0, 26.6, 4.15, 8.2, 3.0, 0.4, 'hair')
    hm = m.bone('helmet', [0, 30, 0], hd)
    cb(hm, 0, 29.6, 0.2, 8.8, 3.4, 8.8, 'helm'); cb(hm, 0, 33.0, 0.2, 7.0, 0.8, 7.0, 'helm')   # domed helmet
    cb(hm, 0, 29.4, 0.2, 10.6, 0.6, 10.6, 'helm_l')                                          # wide brim
    cb(hm, 0, 31.0, -4.65, 2.6, 2.4, 0.6, 'helm_l')                                          # lamp mount
    cb(hm, 0, 33.4, -4.0, 2.2, 1.6, 1.4, 'wax'); cb(hm, 0.6, 34.6, -4.0, 0.9, 1.0, 0.9, 'wax')   # melted candle
    cb(hm, 0, 35.0, -4.0, 0.7, 1.2, 0.7, 'flame')
    for sx, side in ((1, 'r'), (-1, 'l')):
        a = m.bone('arm_' + side, [sx * 5, 22, 0], body)
        sl = m.bone('tc_sleeve_' + side, [sx * 5, 22, 0], a)
        cb(sl, sx * 6, 21.0, 0, 4.2, 3.0, 4.2, 'tc')                                          # short sleeve
        cb(a, sx * 6, 12, 0, 4, 9, 4, 'skin', decals={'north': [('rect', 0.45, 0.2, 0.55, 0.7, '#c88a5e')]})   # big bare arms
        cb(a, sx * 6, 11.2, -0.2, 4.2, 2.2, 4.2, 'skin_d')                                      # fist
    sh = m.bone('pickaxe', [6, 12.4, 0], m.by_name('arm_r'))                                  # shovel (kept bone name)
    cb(sh, 6, 12.0, -1.4, 0.9, 0.9, 4.0, 'wood')                                             # grip below the fist
    cb(sh, 6, 12.0, 0.0, 1.0, 1.0, 1.0, 'steel_l')
    cb(sh, 6, 12.0 - 0.0, -6.0, 0.9, 0.9, 8.0, 'wood')                                        # long handle forward
    cb(sh, 6, 11.4, -11.0, 0.6, 2.2, 1.6, 'steel')                                            # collar
    cb(sh, 6, 10.4, -14.6, 0.4, 4.4, 5.6, 'steel', decals={'east': [('rect', 0, 0, 1, 0.12, '#6a727c')], 'west': [('rect', 0, 0, 1, 0.12, '#6a727c')]})   # spade blade
    cb(sh, 6, 11.4, -17.8, 0.4, 2.4, 1.2, 'steel')                                            # pointed tip
    m.hitbox(0.9, 2.1)
    shade_pass(m, ('skin', 'tc'))
    mc_idle(m, 2.0, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-33, 0, 6]], 2.0)}})
    mc_walk(m, 0.75, 32, arm_r=False, extra={'arm_r': {'rotation': loop([[-30, 0, 4], [-40, 0, 4]], 0.75)}})
    m.anim('attack', 0.65, 'once', {'arm_r': {'rotation': [(0, [-30, 0, 4]), (0.25, [-160, 0, 10]), (0.4, [-10, 0, 0]), (0.65, [-30, 0, 4])]},
                                    'body': {'rotation': [(0, [0, 0, 0]), (0.25, [-8, 10, 0]), (0.4, [12, -8, 0]), (0.65, [0, 0, 0])]}})
    m.anim('deploy', 0.9, 'once', {'root': {'position': [(0, [0, -30, 0]), (0.5, [0, 3, 0]), (0.7, [0, 0, 0]), (0.9, [0, 0, 0])]}})
    m.anim('hit', 0.3, 'once', {'body': {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', {'root': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])], 'position': [(0, [0, 0, 0]), (0.9, [0, -8, 0])]}})
    return m


