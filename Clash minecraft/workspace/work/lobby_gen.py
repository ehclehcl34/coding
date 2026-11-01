"""클래시 마크 로비 (3.3.0) — 크기·좌표는 예전과 같음 (49 x 22 x 49, Offset -24,-3,-28).
로컬 좌표 = 로비 기준점(스폰) 기준. 바닥 윗면 = y -1, 플레이어 발 = y 0.
플러그인 고정 위치 (Lobby.java):
  포털: AI (-13, -19), 랭크 (0, -21), 친선 (13, -19)  — 판정 |dx|<=2, |dz|<=1.2, 글씨 y 4.6
  랭킹판 글씨 (18.4, 3, 0) 서쪽을 봄 / 안내판 글씨 (0, 4, 15.4) 북쪽을 봄
  스킨 전시대 스탠드 (-17, 1, z=-6,-2,2,6) 동쪽을 봄, 이름표 y 4.3
"""
import math, random
import numpy as np
import schem

W, H, L = 49, 22, 49
OX, OY, OZ = 24, 3, 28
AIR = 'minecraft:air'
g = np.full((H, L, W), AIR, dtype=object)
rng = random.Random(3300)


def S(x, y, z, b):
    X, Y, Z = x + OX, y + OY, z + OZ
    if 0 <= X < W and 0 <= Y < H and 0 <= Z < L:
        g[Y, Z, X] = b if b.startswith('minecraft:') else 'minecraft:' + b


def G(x, y, z):
    X, Y, Z = x + OX, y + OY, z + OZ
    if 0 <= X < W and 0 <= Y < H and 0 <= Z < L:
        return g[Y, Z, X]
    return None


def fill(x0, y0, z0, x1, y1, z1, b):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                S(x, y, z, b)


def stairs(m, f, half='bottom'):
    return f'{m}_stairs[facing={f},half={half},shape=straight,waterlogged=false]'


def slab(m, t='bottom'):
    return f'{m}_slab[type={t},waterlogged=false]'


def lantern(h=False):
    return 'lantern[hanging=%s,waterlogged=false]' % ('true' if h else 'false')


def mix(ch):
    r = rng.random(); a = 0
    for b, w in ch:
        a += w
        if r <= a:
            return b
    return ch[-1][0]


X0, X1, Z0, Z1 = -24, 24, -28, 20
FL = -1   # 바닥 윗면 높이

# ------------------------------------------------------------------ 1. 땅
for z in range(Z0, Z1 + 1):
    for x in range(X0, X1 + 1):
        fill(x, -3, z, x, -2, z, 'stone')
        S(x, FL, z, 'grass_block[snowy=false]')

# ------------------------------------------------------------------ 2. 광장 바닥 (성벽 안쪽 전부 포장)
PAVE = [('stone_bricks', 0.5), ('polished_andesite', 0.25), ('cracked_stone_bricks', 0.1), ('mossy_stone_bricks', 0.15)]
for z in range(-24, 17):
    for x in range(-20, 21):
        S(x, FL, z, mix(PAVE))

# 길: 가운데 → 4 방향 (흑암 벽돌 + 금 테두리, 가장자리 아래 빛)
def path_x(z0, z1, xc, half):
    for z in range(min(z0, z1), max(z0, z1) + 1):
        for x in range(xc - half, xc + half + 1):
            edge = abs(x - xc) == half
            S(x, FL, z, 'polished_blackstone_bricks' if not edge else 'gilded_blackstone' if z % 4 == 0 else 'polished_blackstone')
            if edge and z % 4 == 2:
                S(x, FL, z, 'yellow_stained_glass'); S(x, FL - 1, z, 'shroomlight')


def path_z(x0, x1, zc, half):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(zc - half, zc + half + 1):
            edge = abs(z - zc) == half
            S(x, FL, z, 'polished_blackstone_bricks' if not edge else 'gilded_blackstone' if x % 4 == 0 else 'polished_blackstone')
            if edge and x % 4 == 2:
                S(x, FL, z, 'yellow_stained_glass'); S(x, FL - 1, z, 'shroomlight')


path_x(-9, -17, 0, 2)          # 북 (랭크 포털)
path_z(9, 17, 0, 2)            # 동 (명예의 전당)
path_z(-9, -14, 0, 2)          # 서 (갤러리)
path_x(9, 14, 0, 2)            # 남 (안내판)
# 북쪽 포털 앞 반원 광장
for z in range(-21, -13):
    for x in range(-18, 19):
        d = math.hypot(x / 1.5, (z + 13) * 1.0)
        if d <= 12.5 and G(x, FL, z) != 'minecraft:polished_blackstone_bricks':
            S(x, FL, z, 'smooth_stone' if (x + z) % 2 == 0 else 'polished_andesite')

# ------------------------------------------------------------------ 3. 가운데 문장 (스폰)
for z in range(-9, 10):
    for x in range(-9, 10):
        d = math.hypot(x, z)
        if d <= 5.6:
            S(x, FL, z, 'blue_concrete' if x < 0 else 'red_concrete' if x > 0 else 'white_concrete')
        elif d <= 6.6:
            S(x, FL, z, 'gold_block')
        elif d <= 7.8:
            S(x, FL, z, 'polished_blackstone_bricks' if int(math.degrees(math.atan2(z, x)) // 15) % 2 else 'polished_blackstone')
        elif d <= 8.6:
            S(x, FL, z, 'gilded_blackstone' if (x + z) % 3 == 0 else 'chiseled_polished_blackstone')
# 왕관 (금) — 북쪽이 위
CROWN = ['#...#...#',
         '##..#..##',
         '###.#.###',
         '#########',
         '#########',
         '.#######.']
for r, row in enumerate(CROWN):
    for c, ch in enumerate(row):
        if ch == '#':
            S(c - 4, FL, r - 3, 'gold_block')
for (x, z) in ((-4, -4), (0, -4), (4, -4)):          # 왕관 끝 보석 (빛남)
    S(x, FL, z, 'yellow_stained_glass'); S(x, FL - 1, z, 'glowstone')
for x in (-2, 0, 2):                                   # 왕관 띠 보석
    S(x, FL, 1, 'diamond_block' if x == 0 else 'emerald_block')

# ------------------------------------------------------------------ 4. 포털 3개
def portal(cx, cz, theme):
    T = {
        'ai': dict(p='mossy_stone_bricks', p2='moss_block', trim='emerald_block', glass='lime_stained_glass', glow='sea_lantern',
                   top='green_glazed_terracotta', leaf='azalea_leaves[distance=1,persistent=true,waterlogged=false]'),
        'ranked': dict(p='polished_blackstone_bricks', p2='gilded_blackstone', trim='gold_block', glass='yellow_stained_glass', glow='glowstone',
                       top='yellow_glazed_terracotta', leaf=None),
        'friendly': dict(p='prismarine_bricks', p2='dark_prismarine', trim='sea_lantern', glass='light_blue_stained_glass', glow='sea_lantern',
                         top='light_blue_glazed_terracotta', leaf=None),
    }[theme]
    hi = 6 if theme == 'ranked' else 5
    # 빛나는 바닥 (판정 칸)
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 1, cz + 2):
            S(x, FL, z, T['glass']); S(x, FL - 1, z, T['glow'])
    # 기둥 (두 겹) + 받침
    for sx in (-3, 3):
        for x in (cx + sx, cx + sx + (1 if sx > 0 else -1)):
            for z in (cz - 1, cz, cz + 1):
                fill(x, FL, z, x, FL, z, T['p2'])
            fill(x, 0, cz, x, hi, cz, T['p'] if x == cx + sx else T['p2'])
            S(x, 0, cz - 1, stairs('polished_blackstone', 'south' if True else 'north'))
            S(x, 0, cz + 1, stairs('polished_blackstone', 'north'))
        S(cx + sx, 2, cz, T['trim']); S(cx + sx, hi - 1, cz, T['trim'])
        S(cx + sx, hi + 1, cz, lantern())
    # 아치 윗부분
    for x in range(cx - 3, cx + 4):
        S(x, hi, cz, T['p'])
        S(x, hi + 1, cz, T['top'] if abs(x - cx) <= 1 else slab('polished_blackstone_brick'))
    for x in (cx - 2, cx + 2):
        S(x, hi - 1, cz, stairs('polished_blackstone_brick', 'east' if x < cx else 'west', 'top'))
    S(cx, hi + 2, cz, T['trim'])
    if theme == 'ranked':          # 꼭대기 왕관
        for x in range(cx - 2, cx + 3):
            S(x, hi + 3, cz, 'gold_block')
        for x in (cx - 2, cx, cx + 2):
            S(x, hi + 4, cz, 'gold_block')
        S(cx, hi + 5, cz, 'diamond_block')
    if T['leaf']:
        for x in range(cx - 4, cx + 5):
            if rng.random() < 0.7:
                S(x, hi + 1, cz + 1, T['leaf'])
    # 포털 뒤 빛 기둥 (안쪽은 비워둠)
    for x in range(cx - 2, cx + 3):
        S(x, FL, cz - 2, T['p2'])


portal(-13, -19, 'ai')
portal(0, -21, 'ranked')
portal(13, -19, 'friendly')

# ------------------------------------------------------------------ 5. 북쪽 성 정면 + 가운데 탑
for x in range(-23, 24):
    for z in range(-27, -23):
        fill(x, FL, z, x, 9, z, 'stone_bricks' if (x + z) % 7 else 'cracked_stone_bricks')
    S(x, 10, -24, 'stone_bricks' if x % 2 == 0 else AIR)
    for y in (3, 7):
        if x % 6 == 0:
            S(x, y, -24, 'blue_stained_glass' if x < 0 else 'red_stained_glass' if x > 0 else 'yellow_stained_glass')
    if x % 6 == 3:
        S(x, 6, -23, 'blue_wall_banner[facing=south]' if x < 0 else 'red_wall_banner[facing=south]')
        S(x, 8, -23, lantern())
# 가운데 큰 탑 (랭크 포털 뒤)
for x in range(-5, 6):
    for z in range(-28, -23):
        edge = x in (-5, 5) or z in (-28, -24)
        fill(x, FL, z, x, 15, z, 'polished_blackstone_bricks' if edge else AIR)
        S(x, 15, z, 'polished_blackstone')
    for z in range(-28, -23):
        pass
for x in range(-5, 6, 2):
    S(x, 16, -24, 'polished_blackstone_bricks'); S(x, 16, -28, 'polished_blackstone_bricks')
for z in range(-28, -23, 2):
    S(-5, 16, z, 'polished_blackstone_bricks'); S(5, 16, z, 'polished_blackstone_bricks')
for y in range(10, 15):
    S(0, y, -24, 'yellow_stained_glass')
S(0, 9, -24, 'gold_block'); S(-1, 10, -24, 'gold_block'); S(1, 10, -24, 'gold_block')
fill(0, 16, -26, 0, 18, -26, 'dark_oak_fence')
S(1, 18, -26, 'yellow_wool'); S(1, 17, -26, 'yellow_wool'); S(2, 18, -26, 'yellow_wool')

# ------------------------------------------------------------------ 6. 서쪽 스킨 갤러리 (받침대 x -17)
for z in range(-10, 11):
    fill(-21, FL, z, -21, 7, z, 'polished_blackstone_bricks' if z % 4 else 'chiseled_polished_blackstone')
    for x in range(-21, -14):
        S(x, 7, z, 'dark_oak_planks' if x > -21 else 'polished_blackstone_bricks')
    S(-14, 7, z, slab('dark_oak', 'top'))
    if z % 4 == 0:
        S(-20, 4, z, 'shroomlight')
for z in (-10, 10):
    for x in range(-21, -13):
        fill(x, FL, z, x, 6, z, 'polished_blackstone_bricks' if x < -15 else AIR)
for z in (-9, -4, 0, 4, 9):                     # 지붕 기둥 (전시대 사이, 시야 안 가림)
    fill(-14, 0, z, -14, 6, z, 'stripped_dark_oak_log[axis=y]')
    S(-14, 0, z, 'gilded_blackstone')
for zc in (-6, -2, 2, 6):
    for x in range(-18, -15):
        for z in range(zc - 1, zc + 2):
            S(x, FL, z, 'polished_blackstone_bricks')
    S(-17, FL, zc, 'gold_block')
    S(-17, 0, zc, 'gold_block')            # 스탠드는 그 위 (y 1)
    S(-18, 0, zc, stairs('polished_blackstone', 'east'))
    S(-16, 0, zc, stairs('polished_blackstone', 'west'))
    S(-17, 0, zc - 1, stairs('polished_blackstone', 'south'))
    S(-17, 0, zc + 1, stairs('polished_blackstone', 'north'))
    S(-17, 6, zc, lantern(True))
    S(-20, 3, zc, 'purple_stained_glass')
    S(-20, 5, zc, 'purple_wall_banner[facing=east]')

# ------------------------------------------------------------------ 7. 동쪽 명예의 전당 (랭킹판 x 18.4)
for z in range(-8, 9):
    fill(20, FL, z, 21, 9, z, 'polished_blackstone')
    S(19, FL, z, 'polished_blackstone_bricks')
for z in (-8, 8):
    fill(19, 0, z, 19, 9, z, 'gold_block')
    S(19, 10, z, lantern())
for z in range(-8, 9):
    S(19, 9, z, stairs('polished_blackstone_brick', 'west', 'top'))
    S(20, 10, z, 'gilded_blackstone' if z % 2 else 'polished_blackstone_bricks')
# 왕관 장식 (전당 위)
for z in range(-3, 4):
    S(20, 11, z, 'gold_block')
for z in (-3, 0, 3):
    S(20, 12, z, 'gold_block')
S(20, 13, 0, 'diamond_block')
# 붉은 카펫 길
for x in range(9, 19):
    for z in (-1, 0, 1):
        S(x, 0, z, 'red_carpet')
for x in (10, 13, 16):
    for z in (-3, 3):
        fill(x, 0, z, x, 1, z, 'polished_blackstone_wall')
        S(x, 2, z, lantern())

# ------------------------------------------------------------------ 8. 남쪽 성문 + 안내판 뒤판
for x in range(-23, 24):
    fill(x, FL, 18, x, 7, 19, 'stone_bricks' if (x * 7 + 3) % 5 else 'mossy_stone_bricks')
    S(x, 8, 18, 'stone_bricks' if x % 2 == 0 else AIR)
for x in range(-7, 8):                          # 안내판 뒤판 (아래는 성문이 보이게 비움)
    fill(x, 3, 17, x, 8, 17, 'polished_blackstone' if abs(x) < 7 else 'polished_blackstone_bricks')
    if abs(x) == 7:
        fill(x, 0, 17, x, 2, 17, 'polished_blackstone_bricks')
for x in range(-2, 3):                          # 성문 (가운데 아래)
    for y in range(0, 4):
        S(x, y, 18, 'iron_bars'); S(x, y, 19, AIR)
S(-7, 9, 17, lantern()); S(7, 9, 17, lantern())
for x in range(-6, 7):
    S(x, 8, 16, stairs('polished_blackstone_brick', 'north', 'top'))
for x in (-5, 5):
    S(x, 6, 16, 'blue_wall_banner[facing=north]' if x < 0 else 'red_wall_banner[facing=north]')

# ------------------------------------------------------------------ 9. 바깥 성벽 (동서) + 모서리 탑
for z in range(Z0 + 1, Z1):
    for x in (-23, 23):
        if -10 <= z <= 10 and x == -23:
            continue
        fill(x, FL, z, x, 6, z, 'stone_bricks' if (z * 3 + x) % 7 else 'mossy_stone_bricks')
        S(x, 7, z, 'stone_bricks' if z % 2 == 0 else AIR)
        if z % 6 == 0:
            S(x + (1 if x < 0 else -1), 5, z, lantern())


def tower(cx, cz, col, r=3.3, top=11):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                for y in range(FL, top + 1):
                    S(x, y, z, ('stone_bricks' if (x + y + z) % 6 else 'mossy_stone_bricks') if d > r - 1.2 else ('polished_andesite' if y == FL else AIR))
                if d > r - 1.2 and (x + z) % 2 == 0:
                    S(x, top + 1, z, 'stone_bricks')
    for k in range(7):
        rr = r + 0.4 - k * 0.6
        if rr <= 0.2:
            break
        for x in range(int(cx - rr - 1), int(cx + rr + 2)):
            for z in range(int(cz - rr - 1), int(cz + rr + 2)):
                if math.hypot(x - cx, z - cz) <= rr:
                    S(x, top + 2 + k, z, 'deepslate_tiles' if k % 2 == 0 else f'{col}_terracotta')
    fx, fz = int(round(cx)), int(round(cz))
    fill(fx, top + 7, fz, fx, top + 9, fz, 'dark_oak_fence')
    S(fx + 1, top + 9, fz, f'{col}_wool'); S(fx + 1, top + 8, fz, f'{col}_wool')
    for y in (FL + 4, FL + 8):
        S(int(round(cx + r - 0.5)), y, fz, 'glowstone')


tower(-20.5, -24.5, 'blue'); tower(20.5, -24.5, 'red')
tower(-20.5, 16.5, 'blue'); tower(20.5, 16.5, 'red')

# ------------------------------------------------------------------ 10. 벚꽃 나무 + 분수 + 꽃밭
def cherry(cx, cz, h=5):
    for y in range(0, h):
        S(cx, y, cz, 'cherry_log[axis=y]')
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S(cx + dx, h - 1, cz + dz, 'cherry_log[axis=%s]' % ('x' if dx else 'z'))
    for y in range(h - 1, h + 3):
        rr = 3.2 if y < h + 1 else 2.2 if y == h + 1 else 1.2
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                d = math.hypot(x - cx, z - cz)
                if d <= rr and G(x, y, z) == AIR and rng.random() < 0.92:
                    S(x, y, z, 'cherry_leaves[distance=1,persistent=true,waterlogged=false]')
    for _ in range(10):
        x, z = cx + rng.randint(-4, 4), cz + rng.randint(-4, 4)
        if G(x, 0, z) == AIR and G(x, FL, z) not in (None,) and 'stained_glass' not in G(x, FL, z):
            S(x, 0, z, 'pink_petals[facing=north,flower_amount=%d]' % rng.randint(1, 4))


def bed(x0, z0, x1, z1):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            S(x, FL, z, 'polished_andesite' if edge else 'grass_block[snowy=false]')
            if not edge:
                S(x, 0, z, rng.choice(['poppy', 'cornflower', 'azure_bluet', 'allium', 'oxeye_daisy', 'short_grass', 'lily_of_the_valley']))


bed(-14, -12, -6, -7); bed(6, -12, 14, -7)
# (북쪽 나무는 포털을 가려서 뺌 → 꽃밭 가운데 등불만)
for (x, z) in ((-10, -10), (10, -10)):
    S(x, 0, z, 'polished_blackstone_wall'); S(x, 1, z, 'polished_blackstone_wall'); S(x, 2, z, lantern())
bed(-15, 6, -11, 13); bed(11, 6, 15, 13)
cherry(-13, 10, 5); cherry(13, 10, 5)


def fountain(cx, cz):
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            d = math.hypot(x - cx, z - cz)
            if d <= 3.3:
                rim = d > 2.4
                S(x, FL, z, 'quartz_bricks' if rim else 'water[level=0]')
                S(x, FL - 1, z, 'sea_lantern' if not rim else 'stone')
                if rim:
                    S(x, 0, z, slab('quartz'))
    fill(cx, FL, cz, cx, 1, cz, 'quartz_pillar[axis=y]')
    S(cx, 2, cz, 'water[level=0]')
    S(cx, 0, cz - 1, slab('quartz')); S(cx, 0, cz + 1, slab('quartz'))


fountain(-7, 12); fountain(7, 12)

# 길가 등불 기둥
for (x, z) in ((-3, -12), (3, -12), (-3, -16), (3, -16), (12, -3), (12, 3), (-12, -3), (-12, 3), (-3, 12), (3, 12)):
    S(x, 0, z, 'polished_blackstone_wall'); S(x, 1, z, 'polished_blackstone_wall'); S(x, 2, z, lantern())


# ------------------------------------------------------------------ 11. 벽/울타리/판유리 연결
def solid(b):
    if b in (AIR, None):
        return False
    n = b.split('[')[0]
    for bad in ('lantern', 'banner', 'carpet', 'water', 'grass', 'petals', 'poppy', 'cornflower', 'bluet', 'allium', 'daisy', 'valley',
                'slab', 'stairs', 'leaves', 'iron_bars'):
        if bad in n and not n.endswith('grass_block'):
            return False
    return True


def connect():
    for y in range(H):
        for z in range(L):
            for x in range(W):
                b = g[y, z, x]
                base = b.split('[')[0]
                wall = base.endswith('_wall') and 'banner' not in base
                fence = base.endswith('_fence')
                pane = base.endswith('_pane') or base.endswith('iron_bars')
                if not (wall or fence or pane):
                    continue
                sides = {}
                for name, dx, dz in (('north', 0, -1), ('south', 0, 1), ('east', 1, 0), ('west', -1, 0)):
                    xx, zz = x + dx, z + dz
                    nb = g[y, zz, xx] if 0 <= xx < W and 0 <= zz < L else AIR
                    nbase = nb.split('[')[0]
                    same = (nbase.endswith('_wall') and 'banner' not in nbase) or nbase.endswith('_fence') or nbase.endswith('_pane') or nbase.endswith('iron_bars')
                    sides[name] = same or solid(nb)
                if wall:
                    above = g[y + 1, z, x] if y + 1 < H else AIR
                    straight = (sides['north'] and sides['south'] and not sides['east'] and not sides['west']) or \
                               (sides['east'] and sides['west'] and not sides['north'] and not sides['south'])
                    up = (not straight) or (above != AIR)
                    st = ','.join(f'{k}={"low" if sides[k] else "none"}' for k in ('east', 'north', 'south', 'west'))
                    g[y, z, x] = f'{base}[{st},up={"true" if up else "false"},waterlogged=false]'
                else:
                    st = ','.join(f'{k}={"true" if sides[k] else "false"}' for k in ('east', 'north', 'south', 'west'))
                    g[y, z, x] = f'{base}[{st},waterlogged=false]'


connect()

# 판정 확인: 포털 판정 칸 / 스폰 / 전시대 위는 비어 있어야 함
for (cx, cz) in ((-13, -19), (0, -21), (13, -19)):
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 1, cz + 2):
            for y in (0, 1, 2):
                assert G(x, y, z) == AIR, ('portal blocked', x, y, z, G(x, y, z))
for y in (0, 1):
    assert G(0, y, 0) == AIR
for zc in (-6, -2, 2, 6):
    assert G(-17, 1, zc) == AIR and G(-17, 2, zc) == AIR

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else 'clash_lobby.schem'
    schem.save(out, g, [-24, -3, -28], name='clash_lobby')
    print('saved', out)
