def lava_hound():
    """라바 하운드 v2: 바위 판이 겹친 몸통 + 용암 이음새, 녹아 흐르는 배, 이빨 달린 턱과 입 안 용암,
    두 마디 뿔, 손가락 뼈가 있는 날개 (끝 마디 접힘), 세 마디 꼬리. 공격: 몸을 젖혀 모았다가 용암을 뱉으며 돌진"""
    m = Model('clash_lava_hound', density=1.5)
    m.mats_({
        'rock': ('#3a2a25', 'stone'), 'rock_d': ('#261b18', 'stone'), 'rock_l': ('#54423a', 'stone'),
        'plate': ('#463530', 'stone'), 'lava': ('#ff7414', 'glow'), 'lava_h': ('#ffb82e', 'glow'), 'lava_w': ('#fff0a0', 'glow'),
        'eye': ('#ffd23a', 'glow'), 'wing': ('#55190f', 'leather', {'stitch': False}), 'wing_d': ('#3a120b', 'leather', {'stitch': False}),
        'spar': ('#2a1b17', 'bone'), 'claw': ('#d8c6a8', 'bone'), 'tooth': ('#efe2c4', 'bone'), 'maw': ('#ff5a0a', 'glow'),
    })
    crack = [('rect', 0.06, 0.34, 0.46, 0.44, '#ff8a1e'), ('rect', 0.38, 0.34, 0.48, 0.82, '#ff8a1e'),
             ('rect', 0.55, 0.1, 0.64, 0.58, '#ff6a10'), ('rect', 0.58, 0.5, 0.95, 0.6, '#ff6a10'),
             ('rect', 0.12, 0.7, 0.32, 0.77, '#ff9a2a'), ('rect', 0.4, 0.4, 0.46, 0.5, '#ffe27a'),
             ('rect', 0.58, 0.22, 0.62, 0.3, '#ffe27a'), ('px', 0.24, 0.6, '#ffc23a'), ('px', 0.8, 0.3, '#ffc23a')]
    crack2 = [('rect', 0.1, 0.55, 0.6, 0.63, '#ff7a14'), ('rect', 0.5, 0.2, 0.58, 0.6, '#ff7a14'),
              ('rect', 0.7, 0.62, 0.92, 0.7, '#ffb02a'), ('px', 0.3, 0.3, '#ffd25a')]
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 15, 0], root)
    # --- 몸통: 큰 가슴 + 좁아지는 허리, 바위 판 겹침
    cb(body, 0, 7, -3, 22, 17, 15, 'rock', decals={'east': crack, 'west': crack, 'up': crack2})
    cb(body, 0, 8.5, 7.5, 16, 13, 8, 'rock', decals={'east': crack2, 'west': crack2})
    cb(body, 0, 10, 12, 11, 9, 4, 'rock_d')
    for sx in (1, -1):                                                       # 어깨 판 (기울어짐)
        cb(body, sx * 10, 17, -5, 7, 7, 10, 'plate', rot=('z', -sx * 22.5), decals={'north': crack2})
        cb(body, sx * 9.5, 12, 4, 5, 7, 9, 'plate', rot=('z', -sx * 22.5))
        cb(body, sx * 11.6, 16.5, -5, 0.8, 5, 8, 'lava')                     # 판 사이 용암 이음새
    cb(body, 0, 23.5, -4, 16, 2.5, 12, 'plate', decals={'up': crack2})       # 등판
    cb(body, 0, 23, 3.5, 12, 2, 7, 'plate')
    cb(body, 0, 23.2, -0.5, 14, 0.6, 1, 'lava')
    # --- 배: 녹은 용암 + 흘러내리는 방울
    cb(body, 0, 5.2, -2, 17, 2.2, 19, 'lava', decals={'down': [('rect', 0.2, 0.2, 0.8, 0.8, '#ffd25a')]})
    cb(body, 0, 6.2, -3, 20, 1.2, 14, 'rock_d')
    for (x, z, h) in ((-5, -6, 2.4), (3, -2, 3.2), (-1, 4, 2.0), (6, 3, 1.6), (-6, 1, 1.4)):
        cb(body, x, 5.2 - h, z, 1.6, h, 1.6, 'lava_h')
        cb(body, x, 5.2 - h - 0.9, z, 1.0, 0.9, 1.0, 'lava_w')
    # --- 등 가시 (끝이 빛남)
    for i, (z, h) in enumerate(((-8, 4.5), (-3.5, 5.5), (1, 4.8), (5.5, 3.8), (9.5, 3))):
        y0 = 25.5 - (1.2 if z > 4 else 0)
        cb(body, 0, y0, z, 3.2, h, 3.2, 'rock_d', rot=('x', 22.5))
        cb(body, 0, y0 + h - 0.6, z + 1.1, 1.8, 1.8, 1.8, 'lava_h', rot=('x', 22.5))
    # --- 목 / 머리
    neck = m.bone('neck', [0, 19, -10], body)
    cb(neck, 0, 13, -12, 12, 10, 6, 'rock', decals={'east': crack2, 'west': crack2})
    head = m.bone('head', [0, 19, -14], neck)
    cb(head, 0, 12, -19.5, 15, 12, 11, 'rock', decals={
        'north': [('rect', 0.1, 0.3, 0.38, 0.5, '#ffd23a'), ('rect', 0.62, 0.3, 0.9, 0.5, '#ffd23a'),
                  ('rect', 0.17, 0.34, 0.3, 0.46, '#fff4b0'), ('rect', 0.7, 0.34, 0.83, 0.46, '#fff4b0'),
                  ('rect', 0.2, 0.36, 0.26, 0.44, '#ffffff'), ('rect', 0.74, 0.36, 0.8, 0.44, '#ffffff')],
        'east': crack2, 'west': crack2})
    cb(head, 0, 21, -21, 16, 3, 8, 'rock_d')                                   # 눈썹 뼈 (눈 위로 튀어나옴)
    cb(head, 0, 23.5, -18, 10, 2, 7, 'plate')
    cb(head, 0, 12, -27.5, 11, 6.5, 7, 'rock_l', decals={'north': [('rect', 0.22, 0.12, 0.36, 0.32, '#ff7a14'), ('rect', 0.64, 0.12, 0.78, 0.32, '#ff7a14')],
                                                         'up': [('rect', 0.1, 0.6, 0.9, 0.7, '#3a2a25')]})   # 주둥이 + 콧구멍
    for x in (-4.2, -2.1, 0, 2.1, 4.2):                                        # 윗니
        cb(head, x, 10.6, -30.4, 1.1, 1.8, 1.1, 'tooth')
    for sx in (1, -1):
        cb(head, sx * 4.5, 10.2, -30.2, 1.2, 2.6, 1.2, 'tooth')               # 송곳니
    maw = m.bone('maw', [0, 11, -24], head)
    cb(maw, 0, 9.6, -24.5, 9, 2.4, 8, 'maw')                                  # 입 안 용암 (공격 때 커짐)
    jaw = m.bone('jaw', [0, 11, -18], head)
    cb(jaw, 0, 6.8, -24, 11, 3.4, 11, 'rock_d', decals={'up': [('rect', 0.1, 0.05, 0.9, 0.8, '#ff6a10')]})
    for x in (-3.8, -1.3, 1.3, 3.8):                                           # 아랫니
        cb(jaw, x, 10.2, -28.6, 1.1, 1.6, 1.1, 'tooth')
    cb(jaw, 0, 6.2, -21, 8, 1, 6, 'lava')                                      # 턱 아래 용암 줄
    for sx, side in ((1, 'r'), (-1, 'l')):                                     # 두 마디 뿔 (뒤로 휨)
        h1 = m.bone('horn_' + side, [sx * 6, 23, -17], head)
        cb(h1, sx * 6.5, 23, -16, 3.6, 5, 3.6, 'rock_d', rot=('z', -sx * 22.5))
        h2 = m.bone('horn2_' + side, [sx * 8.2, 27.5, -15], h1)
        cb(h2, sx * 8.6, 27.2, -13.5, 2.6, 4, 2.6, 'rock_d', rot=('x', 45))
        cb(h2, sx * 8.6, 29.6, -11.4, 1.8, 2, 1.8, 'lava_h', rot=('x', 45))
        cb(head, sx * 7.8, 17, -17, 2, 4, 3, 'plate')                           # 귀 판
    # --- 날개: 팔 뼈 + 막 3장 + 끝 마디 (접힘)
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 10, 21, -5], body)
        cb(w, sx * 16, 20.6, -9.5, 12, 2, 2, 'spar')                            # 앞 팔 뼈
        for k, (zc, ch) in enumerate(((-4.5, 8), (3, 7))):
            cb(w, sx * 16, 20.6, zc, 12, 0.8, ch, 'wing' if k == 0 else 'wing_d')
        for t in (0.33, 0.66):
            cb(w, sx * (10 + 12 * t), 20.8, -2, 1.2, 1.2, 14, 'spar')
        tip = m.bone('wingtip_' + side, [sx * 22, 21, -9], w)
        cb(tip, sx * 28, 20.6, -9.5, 12, 1.6, 1.6, 'spar')
        cb(tip, sx * 28, 20.6, -4, 12, 0.8, 9, 'wing')
        cb(tip, sx * 26.5, 20.8, -3, 1, 1, 12, 'spar')
        cb(tip, sx * 34.4, 19.8, -9.5, 1.6, 2.6, 1.6, 'claw')
        w2 = m.bone('wing_%s2' % side, [sx * 8, 20, 7], body)                    # 뒤 작은 날개
        cb(w2, sx * 13.5, 19.6, 7, 11, 0.8, 7, 'wing_d')
        cb(w2, sx * 13.5, 19.8, 4, 11, 1.4, 1.4, 'spar')
        cb(w2, sx * 19, 19, 4, 1.4, 2, 1.4, 'claw')
    # --- 다리 4개 (공중에 매달림)
    legs = []
    for name, x, z, wdt in (('leg_fr', 7, -6, 5.6), ('leg_fl', -7, -6, 5.6), ('leg_br', 5.5, 8, 4.6), ('leg_bl', -5.5, 8, 4.6)):
        lg = m.bone(name, [x, 9, z], body)
        cb(lg, x, 1.5, z, wdt, 8, wdt, 'rock_d', decals={'north': [('rect', 0.42, 0.15, 0.58, 0.85, '#ff6a10')]})
        cb(lg, x, 0, z - 0.8, wdt + 1, 2.4, wdt + 1.6, 'rock')
        for dx in (-1.8, 0, 1.8):
            cb(lg, x + dx * wdt / 5.6, -0.6, z - wdt / 2 - 1.4, 1.1, 1.4, 1.8, 'claw')
        legs.append(name)
    # --- 꼬리 3마디
    t1 = m.bone('tail', [0, 15, 13], body)
    cb(t1, 0, 13, 16.5, 5, 4.6, 7, 'rock_d', decals={'east': crack2, 'west': crack2})
    t2 = m.bone('tail2', [0, 15, 20], t1)
    cb(t2, 0, 13.6, 23, 3.8, 3.6, 6, 'rock_d')
    cb(t2, 0, 17.1, 22, 1.6, 1.8, 1.6, 'lava_h')
    t3 = m.bone('tail3', [0, 15, 26], t2)
    cb(t3, 0, 14, 28.5, 2.8, 2.8, 5, 'rock_d')
    cb(t3, 0, 13.6, 32, 3.4, 3.4, 3, 'lava_h')
    cb(t3, 0, 14.3, 33.5, 2, 2, 1.4, 'lava_w')
    m.hitbox(2.2, 2.0)

    # ================= 애니메이션
    def wings(L, amp, base=0, tipamp=10):
        tr = {}
        for side, s in (('r', 1), ('l', -1)):
            tr['wing_' + side] = {'rotation': [(t * L, [0, 0, s * (base + v)]) for t, v in ((0, amp), (0.5, -amp), (1, amp))]}
            tr['wingtip_' + side] = {'rotation': [(t * L, [0, 0, s * v]) for t, v in ((0, tipamp), (0.25, 0), (0.5, -tipamp), (0.75, 0), (1, tipamp))]}
            tr['wing_%s2' % side] = {'rotation': [(t * L, [0, 0, s * (v * 0.8)]) for t, v in ((0, -amp), (0.5, amp), (1, -amp))]}
        return tr

    def tailwave(L, amp, pitch=0):
        return {'tail': {'rotation': loop([[pitch, amp, 0], [pitch, -amp, 0]], L)},
                'tail2': {'rotation': [(0, [0, -amp * 0.8, 0]), (L * 0.5, [0, amp * 0.8, 0]), (L, [0, -amp * 0.8, 0])]},
                'tail3': {'rotation': [(0, [0, amp * 0.6, 0]), (L * 0.25, [0, 0, 0]), (L * 0.5, [0, -amp * 0.6, 0]), (L * 0.75, [0, 0, 0]), (L, [0, amp * 0.6, 0])]}}

    idle = wings(1.0, 22)
    idle.update(tailwave(2.0, 14))
    idle['body'] = {'position': loop([[0, 0, 0], [0, 1.6, 0]], 1.0)}
    idle['neck'] = {'rotation': loop([[3, 0, 0], [-3, 0, 0]], 2.0)}
    idle['head'] = {'rotation': loop([[0, 6, 0], [0, -6, 0]], 4.0)}
    idle['jaw'] = {'rotation': loop([[2, 0, 0], [8, 0, 0]], 2.0)}
    idle['maw'] = {'scale': loop([[1, 1, 1], [1.08, 1.3, 1.08]], 0.6)}
    for i, lg in enumerate(legs):
        idle[lg] = {'rotation': loop([[10 if i % 2 else -2, 0, 0], [-2 if i % 2 else 10, 0, 0]], 1.0)}
    m.anim('idle', 2.0, 'loop', idle)

    walk = wings(0.6, 32, tipamp=16)
    walk.update(tailwave(0.6, 20, pitch=8))
    walk['body'] = {'position': loop([[0, 0, 0], [0, 2.2, 0]], 0.6), 'rotation': [(0, [12, 0, 0]), (0.6, [12, 0, 0])]}
    walk['neck'] = {'rotation': [(0, [-8, 0, 0]), (0.6, [-8, 0, 0])]}
    for lg in legs:
        walk[lg] = {'rotation': [(0, [35, 0, 0]), (0.3, [28, 0, 0]), (0.6, [35, 0, 0])]}
    m.anim('walk', 0.6, 'loop', walk)

    # 공격 (1.3초 = 공격 속도): 0~0.12 몸 젖히며 날개 활짝 → 0.2 용암 뱉기 (턱 쩍, 입 안 용암 커짐, 목 앞으로 쭉) →
    # 0.35 반동으로 몸 뒤로 → 0.6~1.3 날갯짓하며 원래 자세
    att = {}
    for side, s in (('r', 1), ('l', -1)):
        att['wing_' + side] = {'rotation': [(0, [0, 0, s * 10]), (0.12, [0, 0, s * 48]), (0.22, [0, 0, -s * 30]), (0.4, [0, 0, s * 20]),
                                            (0.7, [0, 0, -s * 18]), (1.0, [0, 0, s * 15]), (1.3, [0, 0, s * 10])]}
        att['wingtip_' + side] = {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, s * 25]), (0.22, [0, 0, -s * 30]), (0.5, [0, 0, s * 10]), (1.3, [0, 0, 0])]}
        att['wing_%s2' % side] = {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, s * 35]), (0.22, [0, 0, -s * 20]), (0.6, [0, 0, s * 10]), (1.3, [0, 0, 0])]}
    att['body'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-16, 0, 0]), (0.22, [12, 0, 0]), (0.4, [-4, 0, 0]), (0.8, [2, 0, 0]), (1.3, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.12, [0, 2.5, 3]), (0.22, [0, -1, -4]), (0.4, [0, 0.5, 2]), (0.8, [0, 0, 0]), (1.3, [0, 0, 0])]}
    att['neck'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-28, 0, 0]), (0.22, [22, 0, 0]), (0.45, [6, 0, 0]), (1.3, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.12, [0, 1, 2]), (0.22, [0, -1, -3.5]), (0.5, [0, 0, -1]), (1.3, [0, 0, 0])]}
    att['head'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-14, 0, 0]), (0.22, [10, 0, 0]), (0.3, [10, 6, 0]), (0.4, [8, -6, 0]), (0.6, [4, 0, 0]), (1.3, [0, 0, 0])]}
    att['jaw'] = {'rotation': [(0, [0, 0, 0]), (0.1, [12, 0, 0]), (0.2, [46, 0, 0]), (0.4, [40, 0, 0]), (0.7, [10, 0, 0]), (1.3, [0, 0, 0])]}
    att['maw'] = {'scale': [(0, [1, 1, 1]), (0.12, [1.4, 1.8, 1.3]), (0.2, [1.8, 2.6, 1.6]), (0.32, [0.6, 0.6, 0.6]), (0.7, [1, 1, 1]), (1.3, [1, 1, 1])],
                  'position': [(0, [0, 0, 0]), (0.2, [0, 0, -2]), (0.4, [0, 0, 0])]}
    att.update({k: v for k, v in tailwave(0.65, 26, pitch=-10).items()})
    att['tail']['rotation'] = [(0, [0, 0, 0]), (0.12, [-25, 0, 0]), (0.22, [20, 0, 0]), (0.5, [0, 18, 0]), (0.9, [0, -12, 0]), (1.3, [0, 0, 0])]
    for i, lg in enumerate(legs):
        att[lg] = {'rotation': [(0, [0, 0, 0]), (0.12, [-30, 0, 0]), (0.22, [40, 0, 0]), (0.6, [10, 0, 0]), (1.3, [0, 0, 0])]}
    m.anim('attack', 1.3, 'once', att)

    common_tail(m, death={'root': {'scale': [(0, [1, 1, 1]), (0.25, [1.18, 1.18, 1.18]), (0.5, [0.1, 0.1, 0.1]), (0.9, [0.01, 0.01, 0.01])],
                                   'rotation': [(0, [0, 0, 0]), (0.5, [0, 40, 0])]},
                          'maw': {'scale': [(0, [1, 1, 1]), (0.25, [2.5, 3, 2.5])]}})
    return m
