def elite_barbarian():
    """Barbarian + iron horned viking helmet (eye mask + nose guard, team stripe), yelling mouth"""
    m = barbarian()
    m.name = 'clash_elite_barbarian'
    m.mats_({'iron': ('#5e666c', 'metal'), 'iron_d': ('#40464c', 'metal'), 'horn': ('#e6dcc4', 'bone'), 'horn_d': ('#b8a888', 'bone'),
             'tcm': ('#efefef', 'metal'), 'mouth': ('#8a2a2a', 'plain'), 'tooth': ('#f6f4ea', 'bone')})
    hd = m.by_name('head')
    cb(hd, 0, 19.6, -4.1, 4.0, 1.8, 0.2, 'mouth', decals={'north': pix(["tttt", "....", "tttt"], {'t': '#f6f4ea'})})   # yelling mouth
    hm = m.bone('helmet', [0, 26, 0], hd)
    cb(hm, 0, 25.4, -0.4, 8.8, 3.6, 8.6, 'iron')                                        # dome
    cb(hm, 0, 29.0, -0.4, 7.4, 1.0, 7.2, 'iron')
    cb(hm, 0, 25.0, -4.9, 8.8, 1.4, 0.6, 'iron_d')                                      # brow band
    cb(hm, 0, 23.2, -4.9, 1.6, 3.4, 0.6, 'iron_d')                                      # nose guard
    for sx in (1, -1):
        cb(hm, sx * 2.9, 23.6, -4.9, 3.0, 0.6, 0.6, 'iron_d')                             # eye-mask rim under the eyes
        cb(hm, sx * 4.2, 23.6, -4.9, 0.6, 1.8, 0.6, 'iron_d')
        cb(hm, sx * 4.5, 22.4, -0.4, 0.5, 3.6, 8.0, 'iron')                               # side plates
        hr = m.bone('horn_' + ('r' if sx > 0 else 'l'), [sx * 4.6, 27, -0.4], hm)
        cb(hr, sx * 5.4, 26.2, -0.4, 1.8, 1.8, 1.8, 'horn_d')                              # horn base
        cb(hr, sx * 6.8, 27.0, -0.4, 1.4, 1.4, 1.4, 'horn')
        cb(hr, sx * 7.8, 28.2, -0.4, 1.1, 1.4, 1.1, 'horn')
        cb(hr, sx * 8.3, 29.6, -0.4, 0.8, 1.2, 0.8, 'horn')                                # tip curving up
    tc = m.bone('tc_helm', [0, 29, 0], hm)
    cb(tc, 0, 28.8, -0.4, 1.2, 1.4, 8.8, 'tcm')                                          # team crest stripe
    return m


