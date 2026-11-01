"""Spell models: 통나무 (굴러가는 통나무)."""
import math, random
from bbgen2 import Model

BLOCK = 16.0


def the_log(length_blocks=3.9, diameter_blocks=1.1):
    m = Model('clash_log', density=2.0)
    m.round = False   # 이미 팔각
    m.mats_({'bark': ('#5b3d22', 'wood', {'grain': 'h'}), 'bark2': ('#4a311b', 'wood', {'grain': 'h'}),
             'cut': ('#c9a06a', 'wood', {'grain': 'h'}), 'moss': ('#5f7d2e', 'fur'),
             'tc': ('#efefef', 'rope'), 'stub': ('#5b3d22', 'wood', {'grain': 'v'}),
             'spike': ('#7d848e', 'metal', {'rivets': False}), 'tip': ('#c9ced6', 'metal', {'rivets': False}),
             'plate': ('#4a4f57', 'metal', {'rivets': True})})
    L, D = length_blocks * BLOCK, diameter_blocks * BLOCK
    a, b = D / 2, D * 0.2071
    c = a                                          # 통나무 중심 높이 (바닥에 닿아 굴러감)
    roll = m.bone('roll', [0, c, 0])
    rng = random.Random(7)

    def rings(w, h):
        """잘린 면: 바깥 껍질 고리 + 나이테 + 심"""
        spec = []
        rx, ry = (D / 2) / w, (D / 2) / h
        spec.append(('ering', 0.5, 0.5, rx, ry, 0.16, '#4a311b'))
        for k, col in ((0.78, '#a77d4a'), (0.58, '#b48b56'), (0.38, '#a77d4a'), (0.2, '#9a7042')):
            spec.append(('ering', 0.5, 0.5, rx * k, ry * k, 0.13, col))
        spec.append(('ering', 0.5, 0.5, rx * 0.07, ry * 0.07, 1.0, '#6b4a2a'))
        return spec

    def knots(n):
        out = []
        for _ in range(n):
            x, y = rng.random() * 0.9 + 0.05, rng.random() * 0.6 + 0.2
            out += [('rect', x - 0.012, y - 0.12, x + 0.012, y + 0.12, '#3a2614'), ('rect', x - 0.006, y - 0.05, x + 0.006, y + 0.05, '#7a5634')]
        for _ in range(n * 2):     # 껍질 갈라진 틈
            x, y = rng.random(), rng.random()
            out.append(('rect', x, y, min(1, x + 0.05 + rng.random() * 0.08), y + 0.04, '#2f1f10'))
        return out

    # 팔각 기둥 (가로 두 덩어리) : 직사각형 2개 + 45도 돌린 2개
    for seg, (x0, x1) in enumerate(((-L / 2, 0), (0, L / 2))):
        for k, (hy, hz, rot) in enumerate(((b, a, None), (a, b, None), (b, a, ('x', 45)), (a, b, ('x', 45)))):
            mat = 'bark' if k % 2 == 0 else 'bark2'
            dec = {f: knots(3) for f in ('north', 'south', 'up', 'down')}
            if x0 == -L / 2:
                dec['west'] = rings(2 * hz, 2 * hy)
            if x1 == L / 2:
                dec['east'] = rings(2 * hz, 2 * hy)
            faces = {'west': 'cut'} if x0 == -L / 2 else {}
            if x1 == L / 2:
                faces['east'] = 'cut'
            if k == 0 and seg == 0:
                dec['up'] = dec['up'] + [('rect', 0.2, 0.0, 0.55, 1.0, '#58742a'), ('rect', 0.3, 0.2, 0.42, 0.8, '#6c8a34')]   # 이끼
            roll.box([x0, c - hy, -hz], [x1, c + hy, hz], mat, faces=faces, decals=dec, rot=rot, rot_origin=[(x0 + x1) / 2, c, 0])
    # 쇠 가시: 5줄, 줄마다 4방향씩 엇갈리게 (팔각 둘레 8방향 중 짝/홀)
    sp = m.bone('spikes', [0, c, 0], roll)
    for i, xr in enumerate((-L * 0.42, -L * 0.21, 0.0, L * 0.21, L * 0.42)):
        for k in (range(0, 8, 2) if i % 2 == 0 else range(1, 8, 2)):
            base = k - (k % 2)                       # 축 방향 (0=위, 2=앞+Z, 4=아래, 6=뒤-Z)
            rot = ('x', 45) if k % 2 else None
            r0 = a - 0.6
            def seg(r_in, r_out, half, mat):
                if base == 0:
                    frm, to = [xr - half, c + r_in, -half], [xr + half, c + r_out, half]
                elif base == 4:
                    frm, to = [xr - half, c - r_out, -half], [xr + half, c - r_in, half]
                elif base == 2:
                    frm, to = [xr - half, c - half, r_in], [xr + half, c + half, r_out]
                else:
                    frm, to = [xr - half, c - half, -r_out], [xr + half, c + half, -r_in]
                sp.box(frm, to, mat, rot=rot, rot_origin=[xr, c, 0])
            seg(r0 - 0.4, r0 + 0.8, 3.0, 'plate')      # 박힌 쇠판
            seg(r0, r0 + 2.6, 1.9, 'spike')            # 가시 밑동
            seg(r0 + 2.6, r0 + 5.2, 1.2, 'spike')      # 가시 몸통
            seg(r0 + 5.2, r0 + 7.4, 0.55, 'tip')       # 뾰족한 끝
    # 팀색 밧줄 (양쪽 끝 근처)
    tc = m.bone('tc_rope', [0, c, 0], roll)
    for xr in (-L * 0.315, L * 0.315):
        for hy, hz, rot in ((b + 0.5, a + 0.5, None), (a + 0.5, b + 0.5, None), (b + 0.5, a + 0.5, ('x', 45)), (a + 0.5, b + 0.5, ('x', 45))):
            tc.box([xr - 1.5, c - hy, -hz], [xr + 1.5, c + hy, hz], 'tc', rot=rot, rot_origin=[xr, c, 0])
    # 굴러가기: 앞(-Z)으로 구르는 회전 (블록벤치 애니메이션 x 는 반전 → 양수)
    T = 0.43   # 지름 1.1블록, 초당 8블록에 맞춘 회전
    m.anim('idle', T, 'loop', {'roll': {'rotation': [(0, (0, 0, 0)), (T / 4, (90, 0, 0)), (T / 2, (180, 0, 0)), (3 * T / 4, (270, 0, 0)), (T, (360, 0, 0))]}},
           interp='linear')
    m.fit()
    return m


# =================================================================== 해골 비행선 (풍선)
def skull_decal(bg=None):
    """천 조각 위 하얀 해골 (fraction 좌표)"""
    W, D, T = '#efe8d6', '#1b1712', '#cfc6ae'
    s = []
    if bg:
        s.append(('rect', 0.0, 0.0, 1.0, 1.0, bg))
    s += [('rect', 0.22, 0.10, 0.78, 0.62, W), ('rect', 0.16, 0.20, 0.84, 0.52, W), ('rect', 0.30, 0.04, 0.70, 0.12, W),   # 머리통
          ('rect', 0.30, 0.60, 0.70, 0.78, W), ('rect', 0.26, 0.60, 0.74, 0.70, W),                                       # 턱
          ('rect', 0.26, 0.28, 0.45, 0.47, D), ('rect', 0.55, 0.28, 0.74, 0.47, D),                                       # 눈
          ('rect', 0.47, 0.48, 0.53, 0.58, D),                                                                            # 코
          ('rect', 0.34, 0.66, 0.66, 0.68, D), ('rect', 0.40, 0.62, 0.42, 0.74, D), ('rect', 0.49, 0.62, 0.51, 0.74, D),
          ('rect', 0.58, 0.62, 0.60, 0.74, D),                                                                            # 이빨
          ('rect', 0.16, 0.20, 0.18, 0.52, T), ('rect', 0.82, 0.20, 0.84, 0.52, T),
          # 엇갈린 뼈 (아래)
          ('rect', 0.08, 0.82, 0.92, 0.88, W), ('rect', 0.04, 0.78, 0.12, 0.92, W), ('rect', 0.88, 0.78, 0.96, 0.92, W)]
    return s


def skeleton_balloon():
    from kit import cb
    m = Model('clash_skeleton_balloon', density=1.5)
    m.mats_({'tc': ('#f2f2f2', 'cloth'), 'cloth': ('#54474b', 'cloth'), 'cap': ('#2c2427', 'leather'),
             'patch': ('#2a2326', 'cloth'), 'rope': ('#b99a62', 'rope'), 'drope': ('#6e5a3a', 'rope'),
             'wicker': ('#a8773f', 'rope'), 'wick2': ('#7d5428', 'wood', {'grain': 'v'}), 'rim': ('#5e3d1e', 'wood'),
             'bone': ('#e6dfcc', 'bone'), 'iron': ('#4e555d', 'metal', {'rivets': True}), 'glow': ('#ffb347', 'glow'),
             'sand': ('#c9b07a', 'cloth'), 'dark': ('#1a1512', 'plain')})
    root = m.bone('root', [0, 0, 0])
    env = m.bone('envelope', [0, 30, 0], root)
    tc = m.bone('tc_panels', [0, 30, 0], env)
    # 둥근 풍선: 층마다 폭이 다른 판 (위로 갈수록 넓다가 꼭대기에서 좁아짐), 세로 줄무늬 = 팀색/짙은 천 번갈아
    tiers = [(18, 21, 0.56), (21, 25, 0.82), (25, 30, 0.97), (30, 36, 1.0), (36, 41, 0.95), (41, 45, 0.78), (45, 47.5, 0.5)]
    R = 13.0
    for (y0, y1, k) in tiers:
        r = R * k
        cb(env, 0, y0, 0, 2 * r, y1 - y0, 2 * r * 0.86, 'cloth')            # 짙은 천 몸통
        cb(env, 0, y0, 0, 2 * r * 0.86, y1 - y0, 2 * r, 'cloth')
        # 팀색 세로 판 (앞뒤좌우 2줄씩, 바깥으로 살짝)
        for sx in (-0.42, 0.42):
            cb(tc, sx * 2 * r * 0.86 / 2 * 1.0, y0, -r - 0.15, r * 0.42, y1 - y0, 0.4, 'tc')
            cb(tc, sx * 2 * r * 0.86 / 2 * 1.0, y0, r - 0.25, r * 0.42, y1 - y0, 0.4, 'tc')
            cb(tc, -r - 0.15, y0, sx * 2 * r * 0.86 / 2, 0.4, y1 - y0, r * 0.42, 'tc')
            cb(tc, r - 0.25, y0, sx * 2 * r * 0.86 / 2, 0.4, y1 - y0, r * 0.42, 'tc')
    cb(env, 0, 47.5, 0, 9, 1.6, 9, 'cap')                                  # 꼭대기 덮개
    cb(env, 0, 49.1, 0, 3, 1.2, 3, 'iron')
    # 해골 문장 (앞/뒤)
    for z, f in ((-R - 0.75, 'north'), (R + 0.35, 'south')):
        env.box([-6.5, 27.5, z], [6.5, 40.5, z + 0.4], 'patch', decals={f: skull_decal('#2a2326')})
    # 풍선 입구 고리 + 버너
    cb(env, 0, 16.6, 0, 11, 1.4, 11, 'drope')
    cb(env, 0, 17.2, 0, 8, 1.0, 8, 'dark')
    burner = m.bone('burner', [0, 15, 0], root)
    cb(burner, 0, 13.5, 0, 3.2, 2.2, 3.2, 'iron')
    cb(burner, 0, 15.6, 0, 1.8, 1.4, 1.8, 'glow')
    for sx in (-1, 1):
        cb(burner, sx * 3.0, 14.0, 0, 0.6, 0.6, 6.4, 'iron')
        cb(burner, 0, 14.0, sx * 3.0, 6.4, 0.6, 0.6, 'iron')
    # 밧줄 4가닥 (풍선 입구 → 바구니 모서리, 살짝 기울게)
    ropes = m.bone('ropes', [0, 12, 0], root)
    for sx in (-1, 1):
        for sz in (-1, 1):
            ropes.box([sx * 4.6 - 0.25, 6.5, sz * 4.0 - 0.25], [sx * 4.6 + 0.25, 17.2, sz * 4.0 + 0.25], 'rope',
                      rot=('z', -sx * 22.5), rot_origin=[sx * 4.6, 6.5, sz * 4.0])
    # 바구니
    bk = m.bone('basket', [0, 4, 0], root)
    cb(bk, 0, 0, 0, 10, 6.5, 9, 'wicker')
    cb(bk, 0, -0.4, 0, 9, 0.6, 8, 'wick2')
    cb(bk, 0, 6.2, 0, 11, 1.1, 10, 'rim')
    for sx in (-1, 1):                                                      # 모서리 기둥
        for sz in (-1, 1):
            cb(bk, sx * 4.9, 0, sz * 4.4, 1.0, 7.3, 1.0, 'rim')
    # 앞면 엇갈린 뼈
    bk.box([-4.6, 2.7, -4.85], [4.6, 3.7, -4.45], 'bone', rot=('z', 22.5), rot_origin=[0, 3.2, -4.65])
    bk.box([-4.6, 2.7, -4.95], [4.6, 3.7, -4.55], 'bone', rot=('z', -22.5), rot_origin=[0, 3.2, -4.75])
    for a in (22.5, -22.5):   # 뼈 끝 마디
        for sx in (-1, 1):
            x = sx * 4.4 * math.cos(math.radians(a)); y = 3.2 + sx * 4.4 * math.sin(math.radians(a))
            cb(bk, x, y - 0.7, -5.0, 1.4, 1.4, 0.5, 'bone')
    # 바구니 안 해골들 (머리만 빼꼼)
    for x, z, h in ((-2.4, -1.2, 0), (2.3, 0.6, 0.6), (-0.2, 2.6, -0.3)):
        sk = cb(bk, x, 6.0 + h, z, 3.4, 3.2, 3.4, 'bone', decals={'north': [('rect', 0.12, 0.3, 0.42, 0.6, '#1b1712'), ('rect', 0.58, 0.3, 0.88, 0.6, '#1b1712'),
                                                                         ('rect', 0.3, 0.78, 0.7, 0.86, '#1b1712')]})
    # 매달린 모래주머니
    for sx in (-1, 1):
        cb(bk, sx * 5.6, 2.2, 0, 1.6, 2.4, 1.8, 'sand')
        cb(bk, sx * 5.4, 4.6, 0, 0.4, 1.6, 0.4, 'drope')
    # 애니메이션
    m.anim('idle', 2.4, 'loop', {
        'root': {'position': [(0, (0, 0, 0)), (1.2, (0, 1.2, 0)), (2.4, (0, 0, 0))]},
        'envelope': {'rotation': [(0, (0, 0, -1.5)), (1.2, (1, 0, 1.5)), (2.4, (0, 0, -1.5))]},
        'basket': {'rotation': [(0, (0, 0, 2)), (1.2, (-1.5, 0, -2)), (2.4, (0, 0, 2))]},
        'burner': {'scale': [(0, (1, 1, 1)), (0.3, (1.15, 1.3, 1.15)), (0.6, (1, 1, 1)), (2.4, (1, 1, 1))]}})
    m.anim('walk', 1.6, 'loop', {
        'root': {'rotation': [(0, (6, 0, 0)), (0.8, (8, 0, 0)), (1.6, (6, 0, 0))], 'position': [(0, (0, 0, 0)), (0.8, (0, 0.8, 0)), (1.6, (0, 0, 0))]},
        'basket': {'rotation': [(0, (-5, 0, 0)), (0.8, (-8, 0, 0)), (1.6, (-5, 0, 0))]}})
    m.anim('hit', 0.4, 'once', {'envelope': {'rotation': [(0, (0, 0, 0)), (0.1, (-6, 0, 8)), (0.22, (4, 0, -5)), (0.4, (0, 0, 0))],
                                             'scale': [(0, (1, 1, 1)), (0.08, (1.08, 0.94, 1.08)), (0.4, (1, 1, 1))]}})
    m.anim('spawn', 0.6, 'once', {'envelope': {'scale': [(0, (0.2, 0.2, 0.2)), (0.35, (1.12, 1.12, 1.12)), (0.6, (1, 1, 1))]}})
    m.anim('death', 0.9, 'hold', {
        'envelope': {'scale': [(0, (1, 1, 1)), (0.12, (1.25, 1.2, 1.25)), (0.22, (0.05, 0.05, 0.05)), (0.9, (0.01, 0.01, 0.01))]},
        'tc_panels': {'scale': [(0, (1, 1, 1)), (0.12, (1.25, 1.2, 1.25)), (0.22, (0.05, 0.05, 0.05)), (0.9, (0.01, 0.01, 0.01))]},
        'ropes': {'scale': [(0, (1, 1, 1)), (0.25, (1, 0.2, 1)), (0.9, (1, 0.01, 1))]},
        'basket': {'position': [(0, (0, 0, 0)), (0.2, (0, 2, 0)), (0.9, (0, -40, 0))], 'rotation': [(0, (0, 0, 0)), (0.9, (25, 0, 30))]},
        'burner': {'position': [(0, (0, 0, 0)), (0.9, (0, -38, 0))]}})
    m.fit()
    return m
