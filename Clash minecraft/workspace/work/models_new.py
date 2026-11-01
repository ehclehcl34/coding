"""3.1.0 새 모델: 라바 하운드 / 라바 펍 / 얼음 골렘 / 해골 비행선 (bbgen2, BetterModel 용).
단위: 픽셀 (16 = 1블록), 정면 = 북쪽(-Z), 원점 = 발 중앙.
애니메이션: idle / walk / attack / deploy(spawn) / hit / death  (기존 모델과 같은 이름)"""
import sys, os, math
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else '.')
from bbgen2 import Model


def cb(bone, x, y, z, w, h, d, mat, **kw):
    """가운데(x,z) / 바닥(y) 기준 상자"""
    return bone.box([x - w / 2, y, z - d / 2], [x + w / 2, y + h, z + d / 2], mat, **kw)


def loop(vals, length):
    """같은 간격 키프레임 (마지막 = 처음)"""
    n = len(vals)
    return [(round(length * i / n, 4), v) for i, v in enumerate(vals)] + [(length, vals[0])]


def common_tail(m, root='root', hit_bone='body', death=None):
    """deploy / hit / death 공통"""
    m.anim('spawn', 0.5, 'once', {root: {'position': [(0, [0, -6, 0]), (0.35, [0, 1.5, 0]), (0.5, [0, 0, 0])],
                                         'scale': [(0, [0.3, 0.3, 0.3]), (0.35, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1])]}})
    m.anim('hit', 0.3, 'once', {hit_bone: {'position': [(0, [0, 0, 0]), (0.08, [0, 0, 1.5]), (0.18, [0, 0, -0.5]), (0.3, [0, 0, 0])],
                                           'rotation': [(0, [0, 0, 0]), (0.08, [-6, 0, 0]), (0.3, [0, 0, 0])]}})
    m.anim('death', 0.9, 'hold', death or {root: {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 80]), (0.9, [0, 0, 90])],
                                                  'position': [(0, [0, 0, 0]), (0.6, [0, -4, 0]), (0.9, [0, -8, 0])]}})


# =================================================================== 라바 하운드
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
        att['wing_' + side] = {'rotation': [(0, [0, 0, s * 10]), (0.12, [0, 0, s * 40]), (0.22, [0, 0, -s * 30]), (0.4, [0, 0, s * 20]),
                                            (0.7, [0, 0, -s * 18]), (1.0, [0, 0, s * 15]), (1.3, [0, 0, s * 10])]}
        att['wingtip_' + side] = {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, s * 25]), (0.22, [0, 0, -s * 30]), (0.5, [0, 0, s * 10]), (1.3, [0, 0, 0])]}
        att['wing_%s2' % side] = {'rotation': [(0, [0, 0, 0]), (0.12, [0, 0, s * 35]), (0.22, [0, 0, -s * 20]), (0.6, [0, 0, s * 10]), (1.3, [0, 0, 0])]}
    att['body'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-11, 0, 0]), (0.22, [12, 0, 0]), (0.4, [-4, 0, 0]), (0.8, [2, 0, 0]), (1.3, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.12, [0, 2.5, 3]), (0.22, [0, -1, -4]), (0.4, [0, 0.5, 2]), (0.8, [0, 0, 0]), (1.3, [0, 0, 0])]}
    att['neck'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-20, 0, 0]), (0.22, [22, 0, 0]), (0.45, [6, 0, 0]), (1.3, [0, 0, 0])],
                   'position': [(0, [0, 0, 0]), (0.12, [0, 1, 2]), (0.22, [0, -1, -3.5]), (0.5, [0, 0, -1]), (1.3, [0, 0, 0])]}
    att['head'] = {'rotation': [(0, [0, 0, 0]), (0.12, [-10, 0, 0]), (0.22, [10, 0, 0]), (0.3, [10, 6, 0]), (0.4, [8, -6, 0]), (0.6, [4, 0, 0]), (1.3, [0, 0, 0])]}
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


# =================================================================== 라바 펍
def lava_pup():
    m = Model('clash_lava_pup', density=1.5)
    m.mats_({'rock': ('#3e2c26', 'stone'), 'rock_d': ('#2a1e1b', 'stone'), 'lava': ('#ff7a1a', 'glow'),
             'lava_h': ('#ffc23a', 'glow'), 'wing': ('#5a2418', 'leather', {'stitch': False}), 'claw': ('#c9b8a0', 'bone')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    cb(body, 0, 2, 0, 9, 7, 9, 'rock', decals={'east': [('rect', 0.2, 0.4, 0.8, 0.5, '#ff8a1e'), ('rect', 0.5, 0.2, 0.58, 0.7, '#ff8a1e')],
                                               'west': [('rect', 0.2, 0.5, 0.8, 0.6, '#ff8a1e')],
                                               'north': [('rect', 0.18, 0.25, 0.4, 0.45, '#ffe14a'), ('rect', 0.6, 0.25, 0.82, 0.45, '#ffe14a'),
                                                         ('rect', 0.3, 0.65, 0.7, 0.8, '#ff6a10')]})
    cb(body, 0, 1.4, 0, 7, 1, 7, 'lava')
    cb(body, 0, 9, 0.5, 4, 1.5, 4, 'rock_d')
    cb(body, 0, 10.5, 0.5, 2, 1, 2, 'lava_h')
    for sx in (1, -1):
        cb(body, sx * 3.2, 8.6, -2.5, 1.6, 2.4, 1.6, 'rock_d')         # 작은 뿔
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 4.5, 6.5, 1], body)
        cb(w, sx * 7, 6.5, 1, 5, 0.8, 4, 'wing')
        cb(w, sx * 7, 6.9, -0.6, 5, 1, 1, 'rock_d')
        cb(w, sx * 9.8, 6.2, -0.6, 1, 1.4, 1, 'claw')
    tail = m.bone('tail', [0, 4, 4.5], body)
    cb(tail, 0, 3, 7, 2, 2, 5, 'rock_d')
    cb(tail, 0, 3.2, 9.8, 1.6, 1.6, 1.6, 'lava_h')
    for sx in (1, -1):
        cb(body, sx * 2.5, 0, -2.5, 2, 2, 2, 'claw')
    m.hitbox(0.8, 0.8)
    idle = {'body': {'position': loop([[0, 0, 0], [0, 1, 0]], 0.5)}, 'tail': {'rotation': loop([[0, 18, 0], [0, -18, 0]], 0.5)}}
    for side, s in (('r', 1), ('l', -1)):
        idle['wing_' + side] = {'rotation': loop([[0, 0, s * 30], [0, 0, -s * 25]], 0.25)}
    m.anim('idle', 0.5, 'loop', idle)
    walk = {k: v for k, v in idle.items()}
    walk['body'] = {'position': loop([[0, 0, 0], [0, 1, 0]], 0.5), 'rotation': [(0, [12, 0, 0]), (0.5, [12, 0, 0])]}
    m.anim('walk', 0.5, 'loop', walk)
    m.anim('attack', 0.6, 'once', {'body': {'position': [(0, [0, 0, 0]), (0.2, [0, 0, 2]), (0.35, [0, 0, -3]), (0.6, [0, 0, 0])],
                                            'rotation': [(0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.35, [20, 0, 0]), (0.6, [0, 0, 0])]}})
    common_tail(m, death={'root': {'scale': [(0, [1, 1, 1]), (0.3, [1.2, 1.2, 1.2]), (0.6, [0.01, 0.01, 0.01])]}})
    return m


# =================================================================== 얼음 골렘
def ice_golem():
    m = Model('clash_ice_golem', density=1.0)
    m.mats_({
        'ice': ('#9fd3f2', 'stone'), 'ice_l': ('#cdeeff', 'stone'), 'ice_d': ('#6aa9d6', 'stone'),
        'crystal': ('#d9f4ff', 'gem'), 'snow': ('#f2f8fc', 'plain'), 'eye': ('#1d4a8c', 'glow'), 'core': ('#d0d0d0', 'gem'),
    })
    ice_dec = [('rect', 0.15, 0.2, 0.45, 0.26, '#e8f8ff'), ('rect', 0.55, 0.55, 0.9, 0.6, '#e8f8ff'),
               ('rect', 0.3, 0.6, 0.36, 0.95, '#7fb8dc'), ('rect', 0.7, 0.1, 0.76, 0.45, '#7fb8dc'), ('px', 0.2, 0.75, '#ffffff')]
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 10, 0], root)
    cb(body, 0, 8, 0, 20, 15, 13, 'ice', decals={'north': ice_dec, 'south': ice_dec, 'east': ice_dec[:3], 'west': ice_dec[2:]})
    cb(body, 0, 20, 0.5, 22, 5, 14, 'ice_l')                              # 어깨 덩어리
    cb(body, 0, 25, 0.5, 18, 1.5, 12, 'snow')                             # 어깨 위 눈
    for (x, z, h, r) in ((-6, 5, 7, 0), (-1, 6, 9, 0), (4, 5, 6, 0), (8, 3, 5, 0)):   # 등 결정
        cb(body, x, 24, z, 3, h, 3, 'crystal', rot=('x', 22.5))
    tc = m.bone('tc_core', [0, 15, -6.6], body)
    cb(tc, 0, 13, -6.8, 5, 5, 1.2, 'core')                               # 팀색 가슴 결정
    head = m.bone('head', [0, 25, -3], body)
    cb(head, 0, 23.5, -5, 10, 7, 8, 'ice', decals={'north': [('rect', 0.15, 0.35, 0.38, 0.55, '#1d4a8c'), ('rect', 0.62, 0.35, 0.85, 0.55, '#1d4a8c'),
                                                             ('rect', 0.22, 0.4, 0.3, 0.5, '#8fd0ff'), ('rect', 0.7, 0.4, 0.78, 0.5, '#8fd0ff'),
                                                             ('rect', 0.1, 0.22, 0.42, 0.3, '#5f97c4'), ('rect', 0.58, 0.22, 0.9, 0.3, '#5f97c4'),
                                                             ('rect', 0.3, 0.75, 0.7, 0.85, '#4f86b8')]})
    cb(head, 0, 30.5, -4.5, 9, 1.5, 7, 'snow')
    cb(head, -2, 32, -4, 2, 2.5, 2, 'crystal'); cb(head, 2.5, 32, -5, 1.6, 1.8, 1.6, 'crystal')
    for sx, side in ((1, 'r'), (-1, 'l')):
        arm = m.bone('arm_' + side, [sx * 12, 23, 0], body)
        cb(arm, sx * 13, 13, 0, 6, 11, 7, 'ice_d', decals={'north': ice_dec[2:4]})
        cb(arm, sx * 13.5, 5, -0.5, 8, 8, 9, 'ice', decals={'north': ice_dec[:2]})            # 큰 주먹
        cb(arm, sx * 13, 21, 0, 8, 4, 9, 'ice_l')
        cb(arm, sx * 13, 25, 0, 7, 1.2, 8, 'snow')
        cb(arm, sx * 14.5, 24.5, 2, 2, 4, 2, 'crystal', rot=('z', -sx * 22.5))
    for sx, side in ((1, 'r'), (-1, 'l')):
        leg = m.bone('leg_' + side, [sx * 5, 9, 0], root)
        cb(leg, sx * 5, 0, 0, 7, 9, 8, 'ice_d')
        cb(leg, sx * 5, 0, -1, 8, 2.5, 9, 'ice')
    m.hitbox(1.3, 2.1)
    m.head_scale = None
    idle = {'body': {'position': loop([[0, 0, 0], [0, -0.6, 0]], 2.4)},
            'arm_r': {'rotation': loop([[0, 0, 2], [3, 0, 0]], 2.4)}, 'arm_l': {'rotation': loop([[0, 0, -2], [3, 0, 0]], 2.4)},
            'head': {'rotation': loop([[0, 6, 0], [0, -6, 0]], 4.8)}}
    m.anim('idle', 2.4, 'loop', idle)
    walk = {'leg_r': {'rotation': loop([[22, 0, 0], [-22, 0, 0]], 1.4)}, 'leg_l': {'rotation': loop([[-22, 0, 0], [22, 0, 0]], 1.4)},
            'arm_r': {'rotation': loop([[-16, 0, 3], [16, 0, 3]], 1.4)}, 'arm_l': {'rotation': loop([[16, 0, -3], [-16, 0, -3]], 1.4)},
            'body': {'rotation': loop([[4, 0, 4], [4, 0, -4]], 1.4), 'position': loop([[0, 0, 0], [0, 0.8, 0], [0, 0, 0], [0, 0.8, 0]], 1.4)}}
    m.anim('walk', 1.4, 'loop', walk)
    att = {'arm_r': {'rotation': [(0, [0, 0, 0]), (0.45, [-150, 0, 10]), (0.65, [25, 0, 0]), (1.0, [0, 0, 0])]},
           'arm_l': {'rotation': [(0, [0, 0, 0]), (0.45, [-150, 0, -10]), (0.65, [25, 0, 0]), (1.0, [0, 0, 0])]},
           'body': {'rotation': [(0, [0, 0, 0]), (0.45, [-10, 0, 0]), (0.65, [14, 0, 0]), (1.0, [0, 0, 0])]}}
    m.anim('attack', 1.0, 'once', att)
    common_tail(m, death={'body': {'rotation': [(0, [0, 0, 0]), (0.6, [70, 0, 0]), (0.9, [85, 0, 0])],
                                   'position': [(0, [0, 0, 0]), (0.6, [0, -6, -4]), (0.9, [0, -8, -6])]},
                          'arm_r': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, 40])]}, 'arm_l': {'rotation': [(0, [0, 0, 0]), (0.6, [0, 0, -40])]},
                          'root': {'scale': [(0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.9, [0.6, 0.4, 0.6])]}})
    return m


# =================================================================== 해골 비행선 (원작 Balloon)
def balloon():
    m = Model('clash_balloon', density=1.0)
    m.mats_({
        'cloth': ('#b98f5c', 'soft'), 'cloth_d': ('#8e6c46', 'soft'), 'cloth_l': ('#e3c899', 'soft'),
        'band': ('#d8d8d8', 'cloth'), 'rope': ('#7a5a36', 'rope'), 'wicker': ('#8a5a2b', 'rope'), 'wood': ('#6b4423', 'wood'),
        'bone': ('#ece6d2', 'bone'), 'goggle': ('#b88a3a', 'metal'), 'lens': ('#7fd6ff', 'gem'), 'scarf': ('#9e2a22', 'cloth'),
        'bomb': ('#26262c', 'metal'), 'fuse': ('#5a4a32', 'rope'), 'spark': ('#ffd04a', 'glow'), 'flame': ('#ff8a1e', 'glow'),
        'iron': ('#55575c', 'metal', {'rivets': True}),
    })
    patch = []
    for i in range(6):                         # 세로 천 조각 (밝은 / 어두운 번갈아)
        x0 = i / 6.0
        patch.append(('rect', x0, 0.0, x0 + 1 / 6.0, 1.0, '#e4c89a' if i % 2 == 0 else '#b48d5e'))
        patch.append(('rect', x0, 0.0, x0 + 0.02, 1.0, '#6e5232'))
    patch += [('rect', 0.2, 0.3, 0.3, 0.55, '#9c7650'), ('rect', 0.2, 0.3, 0.3, 0.32, '#5a4028'),   # 기운 천
              ('rect', 0.7, 0.55, 0.78, 0.8, '#f0dcb4'), ('rect', 0.7, 0.55, 0.78, 0.57, '#5a4028')]
    topdec = [('ering', 0.5, 0.5, 0.48, 0.48, 0.08, '#6e5232'), ('ering', 0.5, 0.5, 0.25, 0.25, 0.15, '#b48d5e')]
    root = m.bone('root', [0, 0, 0])
    env = m.bone('envelope', [0, 38, 0], root)
    # 둥근 풍선: 위아래로 쌓은 층 (높이, 반폭)
    prof = [(22, 5), (24, 9), (27, 12), (31, 14), (36, 15), (41, 15), (45, 13.5), (48, 11), (50.5, 8), (52, 4)]
    for (y0, r0), (y1, r1) in zip(prof, prof[1:]):
        w = r0 * 2 if r0 > r1 else r1 * 2
        w = max(r0, r1) * 2
        i = prof.index((y0, r0))
        dec = [('rect', 0.0, 0.0, 1.0, 0.08, '#7a5a38')]                 # 층 사이 바느질선
        if i in (3, 5):
            dec += [('rect', 0.18, 0.3, 0.34, 0.8, '#a07a50'), ('rect', 0.18, 0.3, 0.34, 0.36, '#5a4028'),
                    ('rect', 0.66, 0.2, 0.8, 0.7, '#f2e0bc'), ('rect', 0.66, 0.2, 0.8, 0.26, '#5a4028')]
        cb(env, 0, y0, 0, w, y1 - y0, w, 'cloth_l' if i % 2 == 0 else 'cloth',
           decals=dict({f: dec for f in ('north', 'south', 'east', 'west')}, up=topdec, down=topdec))
    # 아래쪽 그물 밧줄 (풍선 아래 반을 감쌈)
    for (y0, r0) in prof[1:4]:
        cb(env, 0, y0 + 0.2, 0, max(r0, 1) * 2 + 0.5, 0.8, max(r0, 1) * 2 + 0.5, 'rope')
    tc = m.bone('tc_band', [0, 38, 0], env)
    cb(tc, 0, 36.5, 0, 31.2, 3.5, 31.2, 'band')                       # 팀색 띠
    cb(env, 0, 52, 0, 5, 1.6, 5, 'rope')                                # 꼭대기 매듭
    cb(env, 0, 53.4, 0, 2, 1.6, 2, 'wood')
    # 버너 (불꽃)
    burner = m.bone('burner', [0, 18, 0], root)
    cb(burner, 0, 17, 0, 5, 2, 5, 'iron')
    cb(burner, 0, 19, 0, 3, 3, 3, 'flame')
    cb(burner, 0, 22, 0, 1.6, 1.6, 1.6, 'spark')
    # 밧줄 (바구니 모서리 → 풍선 아래)
    for sx in (1, -1):
        for sz in (1, -1):
            cb(root, sx * 6.2, 12, sz * 6.2, 0.7, 11, 0.7, 'rope')
            cb(root, sx * 4.5, 22.5, sz * 4.5, 0.7, 2.5, 0.7, 'rope')
    # 바구니
    basket = m.bone('basket', [0, 6, 0], root)
    cb(basket, 0, 3, 0, 14, 9, 14, 'wicker', decals={f: [('rect', 0.0, 0.45, 1.0, 0.52, '#5e3a18')] for f in ('north', 'south', 'east', 'west')})
    cb(basket, 0, 11.6, 0, 15.4, 1.6, 15.4, 'wood')
    cb(basket, 0, 2.2, 0, 13, 1, 13, 'wood')
    for sx in (1, -1):                                                   # 옆에 묶은 폭탄
        cb(basket, sx * 7.8, 5, 3, 3, 3, 3, 'bomb'); cb(basket, sx * 7.8, 8, 3, 0.8, 1.2, 0.8, 'fuse')
    # 해골 조종사
    pilot = m.bone('pilot', [0, 12, 1], basket)
    cb(pilot, 0, 10.5, 1, 6, 3.5, 4, 'scarf')                            # 목도리
    cb(pilot, 2.6, 12.8, 3.5, 1.6, 1.2, 4, 'scarf', rot=('x', -22.5))    # 휘날리는 끝
    skull = m.bone('skull', [0, 14, 1], pilot)
    cb(skull, 0, 13.5, 0.5, 7, 6.5, 6.5, 'bone', decals={'north': [('rect', 0.15, 0.35, 0.42, 0.62, '#1c1a18'), ('rect', 0.58, 0.35, 0.85, 0.62, '#1c1a18'),
                                                                     ('rect', 0.45, 0.62, 0.55, 0.75, '#3a3530'),
                                                                     ('rect', 0.25, 0.82, 0.75, 0.88, '#3a3530'), ('rect', 0.35, 0.82, 0.38, 0.95, '#3a3530'),
                                                                     ('rect', 0.5, 0.82, 0.53, 0.95, '#3a3530'), ('rect', 0.65, 0.82, 0.68, 0.95, '#3a3530')]})
    cb(skull, 0, 17.6, 0.5, 7.6, 1.4, 7.2, 'goggle')                     # 고글 끈
    for sx in (1, -1):
        cb(skull, sx * 1.8, 17.2, -2.9, 2.6, 2.4, 1, 'goggle')
        cb(skull, sx * 1.8, 17.6, -3.5, 1.6, 1.6, 0.4, 'lens')
    cb(skull, 0, 19.8, 0.5, 6.4, 1.2, 6, 'leather' if False else 'cloth_d')  # 가죽 모자
    arm = m.bone('arm', [3.5, 12, -1], pilot)
    cb(arm, 4.5, 10.5, -3, 1.4, 1.4, 6, 'bone')
    cb(arm, 4.5, 9.3, -6.5, 3.6, 3.6, 3.6, 'bomb')                      # 손에 든 폭탄
    cb(arm, 4.5, 12.9, -6.5, 0.6, 1.2, 0.6, 'fuse')
    cb(arm, 4.5, 14.1, -6.5, 0.9, 0.9, 0.9, 'spark')
    # 바구니 아래 매달린 큰 폭탄
    bomb = m.bone('bomb', [0, 2.5, 0], root)
    cb(bomb, 0, 1.5, 0, 0.7, 2, 0.7, 'rope')
    cb(bomb, 0, -4.5, 0, 6, 6, 6, 'bomb', decals={'north': [('rect', 0.15, 0.15, 0.35, 0.35, '#6a6a74')]})
    cb(bomb, 0, -5.2, 0, 7, 1, 7, 'iron')
    cb(bomb, 0, 0, 0, 2.4, 1.2, 2.4, 'iron')
    m.hitbox(1.8, 3.4)
    idle = {'root': {'position': loop([[0, 0, 0], [0, 1.5, 0]], 2.4), 'rotation': loop([[0, 0, 2], [0, 0, -2]], 2.4)},
            'envelope': {'scale': loop([[1, 1, 1], [1.02, 0.99, 1.02]], 1.2)},
            'bomb': {'rotation': loop([[6, 0, 3], [-6, 0, -3]], 1.2)},
            'burner': {'scale': loop([[1, 1, 1], [1.1, 1.3, 1.1]], 0.3)},
            'skull': {'rotation': loop([[0, 12, 0], [0, -12, 0]], 4.8)}}
    m.anim('idle', 2.4, 'loop', idle)
    walk = dict(idle)
    walk['root'] = {'position': loop([[0, 0, 0], [0, 1, 0]], 1.6), 'rotation': [(0, [8, 0, 0]), (0.8, [8, 0, 2]), (1.6, [8, 0, 0])]}
    walk['bomb'] = {'rotation': loop([[-14, 0, 0], [-8, 0, 0]], 0.8)}
    m.anim('walk', 1.6, 'loop', walk)
    att = {'bomb': {'position': [(0, [0, 0, 0]), (0.25, [0, -14, 0]), (0.26, [0, -14, 0]), (0.27, [0, 0, 0]), (1.0, [0, 0, 0])],
                    'scale': [(0, [1, 1, 1]), (0.25, [1, 1, 1]), (0.26, [0.01, 0.01, 0.01]), (0.7, [0.01, 0.01, 0.01]), (1.0, [1, 1, 1])]},
           'arm': {'rotation': [(0, [0, 0, 0]), (0.2, [-60, 0, 0]), (0.45, [30, 0, 0]), (1.0, [0, 0, 0])]},
           'root': {'position': [(0, [0, 0, 0]), (0.3, [0, 2, 0]), (1.0, [0, 0, 0])]}}
    m.anim('attack', 1.0, 'once', att)
    common_tail(m, hit_bone='envelope', death={
        'envelope': {'scale': [(0, [1, 1, 1]), (0.4, [0.8, 0.6, 0.8]), (0.9, [0.4, 0.2, 0.4])],
                     'position': [(0, [0, 0, 0]), (0.9, [0, -12, 0])]},
        'root': {'position': [(0, [0, 0, 0]), (0.9, [0, -20, 0])], 'rotation': [(0, [0, 0, 0]), (0.9, [25, 0, 35])]},
        'bomb': {'scale': [(0, [1, 1, 1]), (0.1, [0.01, 0.01, 0.01])]}})
    return m


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    os.makedirs(out, exist_ok=True)
    for fn in (lava_hound, lava_pup, ice_golem, balloon):
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad)
