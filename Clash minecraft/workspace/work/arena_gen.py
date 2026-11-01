"""클래시 마크 경기장 (3.1.0) — 1타일 = 3x3 블록, 잔디 블록 / 초록 테라코타 체크.

게임 좌표는 플러그인(Arena.java)과 똑같이 유지:
  필드 54 x 96 블록 (로컬 x 0..53, z 0..95), 바닥 = P-1 (schem y 5)
  강: 타일 행 15~16 (로컬 z 45..50), 다리: 타일 열 2~4 / 13~15 (로컬 x 6..14 / 39..47)
  프린세스 타워 3x3 타일: x 6..14, z 15..23(파랑) / 72..80(빨강)
  킹 타워 4x4 타일: x 21..32, z 3..14(파랑) / 81..92(빨강)
  지휘대: 바닥 P+15 (schem y 21), 로컬 x 20..33, z -12..-7(파랑) / 102..107(빨강)
schem: 72 x 30 x 130, Offset (-36, -6, -65) → 로컬 (0,0) = schem (9, 17)
"""
import math, random
import numpy as np
import schem

W, H, L = 72, 30, 130
OX, OZ = 9, 17          # 로컬 → schem
FY = 5                  # 바닥 블록 높이 (schem y)
AIR = 'minecraft:air'
g = np.full((H, L, W), AIR, dtype=object)
rng = random.Random(20261022)


def S(lx, y, lz, b):
    x, z = lx + OX, lz + OZ
    if 0 <= x < W and 0 <= z < L and 0 <= y < H:
        g[y, z, x] = b if b.startswith('minecraft:') else 'minecraft:' + b


def G(lx, y, lz):
    x, z = lx + OX, lz + OZ
    if 0 <= x < W and 0 <= z < L and 0 <= y < H:
        return g[y, z, x]
    return AIR


def fill(x0, y0, z0, x1, y1, z1, b):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                S(x, y, z, b)


def stairs(mat, facing, half='bottom'):
    return f'{mat}_stairs[facing={facing},half={half},shape=straight,waterlogged=false]'


def slab(mat, t='bottom'):
    return f'{mat}_slab[type={t},waterlogged=false]'


WALLS = ('_wall',)
FENCES = ('_fence',)
PANES = ('_pane', 'iron_bars')


def lantern(hanging=False):
    return f'lantern[hanging={"true" if hanging else "false"},waterlogged=false]'


def banner(color, facing):
    return f'{color}_wall_banner[facing={facing}]'


def mix(choices):
    r = rng.random(); acc = 0
    for b, w in choices:
        acc += w
        if r <= acc:
            return b
    return choices[-1][0]


# ------------------------------------------------------------------ 1. 땅 (전체 기반)
STONE_MIX = [('stone', 0.6), ('andesite', 0.2), ('tuff', 0.1), ('cobblestone', 0.1)]
for lz in range(-OZ, L - OZ):
    for lx in range(-OX, W - OX):
        for y in range(0, FY - 1):
            S(lx, y, lz, mix(STONE_MIX))
        S(lx, FY - 1, lz, 'dirt')
        S(lx, FY, lz, 'grass_block[snowy=false]')

# ------------------------------------------------------------------ 2. 필드: 잔디 / 초록 테라코타 체크 (3x3 타일)
for tz in range(32):
    for tx in range(18):
        b = 'grass_block[snowy=false]' if (tx + tz) % 2 == 0 else 'green_terracotta'
        fill(tx * 3, FY, tz * 3, tx * 3 + 2, FY, tz * 3 + 2, b)
        fill(tx * 3, FY - 1, tz * 3, tx * 3 + 2, FY - 1, tz * 3 + 2, 'dirt' if b.startswith('grass') else 'terracotta')

# 길 (흙길 블록 하나로 통일)
#  - 세로: 프린세스 타워 → 다리 → 반대편 프린세스 타워 (타일 열 3 / 14)
#  - 프린세스 타워와 킹 타워 사이 모서리를 길로 채움 (킹 타워 앞은 안 지나감)
PATH_TILES = set()
for tz in list(range(8, 15)) + list(range(17, 24)):
    PATH_TILES.add((3, tz)); PATH_TILES.add((14, tz))
# 프린세스 타워 ↔ 킹 타워 사이 모서리 덩어리 (파랑 기준, 빨강은 위아래 대칭)
CORNER_BLUE = {(5, 3), (6, 3), (4, 4), (5, 4), (6, 4), (5, 5),
               (11, 3), (12, 3), (11, 4), (12, 4), (13, 4), (12, 5)}
PATH_TILES |= CORNER_BLUE
PATH_TILES |= {(tx, 31 - tz) for (tx, tz) in CORNER_BLUE}
for (tx, tz) in PATH_TILES:
    fill(tx * 3, FY, tz * 3, tx * 3 + 2, FY, tz * 3 + 2, 'dirt_path')
    fill(tx * 3, FY - 1, tz * 3, tx * 3 + 2, FY - 1, tz * 3 + 2, 'dirt')

# ------------------------------------------------------------------ 3. 강 + 다리
RZ0, RZ1 = 45, 50
BRIDGES = [(9, 11), (42, 44)]   # 다리 상판 3블록 (길과 같은 폭) + 양쪽 난간 = 5칸 (플러그인 bridgeHalf 1.5, 가운데 x 10.5 / 43.5)
for lx in range(-3, 57):
    for lz in range(RZ0, RZ1 + 1):
        S(lx, 0, lz, 'stone')
        S(lx, 1, lz, mix([('sand', 0.45), ('gravel', 0.3), ('clay', 0.15), ('mud', 0.1)]))
        for y in (2, 3, 4):
            S(lx, y, lz, 'water[level=0]')
        S(lx, FY, lz, 'water[level=0]')
        if rng.random() < 0.18:
            S(lx, 2, lz, 'seagrass')
        elif rng.random() < 0.05:
            S(lx, 2, lz, 'tall_seagrass[half=lower]'); S(lx, 3, lz, 'tall_seagrass[half=upper]')
    # 둑: 강 양쪽 가장자리 아래를 돌로 받침
    for lz in (RZ0 - 1, RZ1 + 1):
        for y in range(1, FY):
            S(lx, y, lz, mix([('mossy_stone_bricks', 0.5), ('stone_bricks', 0.35), ('cracked_stone_bricks', 0.15)]))
# 연잎 (다리 아래 피해서)
for _ in range(26):
    lx = rng.randrange(0, 54); lz = rng.randrange(RZ0, RZ1 + 1)
    if not any(a - 1 <= lx <= b + 1 for a, b in BRIDGES):
        S(lx, FY + 1, lz, 'lily_pad')

for (bx0, bx1) in BRIDGES:
    # 아치: 돌벽돌 받침 + 상판
    for lz in range(RZ0, RZ1 + 1):
        for lx in range(bx0 - 1, bx1 + 2):
            S(lx, FY, lz, 'spruce_planks' if bx0 <= lx <= bx1 else 'stone_bricks')
        # 상판 무늬: 가운데 줄은 껍질 벗긴 통나무
        for lx in range(bx0, bx1 + 1):
            if (lx - bx0) % 4 == 0:
                S(lx, FY, lz, 'stripped_spruce_log[axis=z]')
    # 아치 밑 (물 위로 둥근 모양)
    for lz in range(RZ0, RZ1 + 1):
        t = (lz - RZ0 + 0.5) / (RZ1 - RZ0 + 1)
        depth = int(round(2.4 * (1 - math.sin(math.pi * t))))  # 가장자리일수록 깊이 내려감
        for lx in (bx0 - 1, bx1 + 1):
            for y in range(FY - 1 - depth, FY):
                S(lx, y, lz, 'stone_bricks')
        for lx in range(bx0, bx1 + 1):
            S(lx, FY - 1, lz, stairs('stone_brick', 'south' if lz < (RZ0 + RZ1) / 2 else 'north', 'top') if depth == 0 else 'stone_bricks')
            for y in range(FY - 1 - depth, FY - 1):
                S(lx, y, lz, 'stone_bricks')
    # 난간: 돌벽 + 기둥 + 등불
    for lz in range(RZ0, RZ1 + 1):
        for lx in (bx0 - 1, bx1 + 1):
            post = lz in (RZ0, RZ1)
            if post:
                S(lx, FY + 1, lz, 'chiseled_stone_bricks')
                S(lx, FY + 2, lz, 'stone_brick_wall')
                S(lx, FY + 3, lz, lantern())
            else:
                S(lx, FY + 1, lz, 'stone_brick_wall')

# ------------------------------------------------------------------ 4. 타워 받침
def pad(x0, z0, n, color):
    x1, z1 = x0 + n - 1, z0 + n - 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            corner = x in (x0, x1) and z in (z0, z1)
            ring2 = x in (x0 + 1, x1 - 1) or z in (z0 + 1, z1 - 1)
            if corner:
                b = 'chiseled_stone_bricks'
            elif edge:
                b = f'{color}_glazed_terracotta' if (x + z) % 2 == 0 else f'{color}_concrete'
            elif ring2:
                b = 'polished_andesite'
            else:
                b = mix([('stone_bricks', 0.7), ('cracked_stone_bricks', 0.12), ('mossy_stone_bricks', 0.18)])
            S(x, FY, z, b)
            S(x, FY - 1, z, 'stone_bricks')
    # 팀색 양털 (플러그인/관리자 기준점, 가운데 아래)
    S(x0 + n // 2, FY - 2, z0 + n // 2, f'{color}_wool')


pad(6, 15, 9, 'blue'); pad(39, 15, 9, 'blue')
pad(6, 72, 9, 'red'); pad(39, 72, 9, 'red')
pad(21, 3, 12, 'blue'); pad(21, 81, 12, 'red')

# ------------------------------------------------------------------ 5. 필드 테두리 / 해자 / 산책로
# x: -1 / 54 테두리 벽, z: -1 / 96 테두리 벽
def team_of(lz):
    return 'blue' if lz < 48 else 'red'


for lz in range(-1, 97):
    for lx in (-1, 54):
        S(lx, FY, lz, 'polished_andesite')
        S(lx, FY + 1, lz, 'stone_bricks' if lz % 6 else 'chiseled_stone_bricks')
        S(lx, FY + 2, lz, 'stone_brick_wall' if lz % 6 else lantern())
for lx in range(-1, 55):
    for lz in (-1, 96):
        S(lx, FY, lz, 'polished_andesite')
        S(lx, FY + 1, lz, 'stone_bricks' if lx % 6 else 'chiseled_stone_bricks')
        S(lx, FY + 2, lz, 'stone_brick_wall' if lx % 6 else lantern())
# 강이 벽을 지나는 곳: 철창 수문
for lz in range(RZ0, RZ1 + 1):
    for lx in (-1, 54):
        S(lx, FY, lz, 'water[level=0]')
        S(lx, FY + 1, lz, 'iron_bars')
        S(lx, FY + 2, lz, 'stone_bricks')
        S(lx, FY + 3, lz, slab('stone_brick'))

# 해자 (양옆 x -2..-3 / 55..56, 양끝 z -2..-3 / 97..98)
def moat(x, z):
    S(x, 1, z, mix([('gravel', 0.5), ('sand', 0.5)]))
    for y in (2, 3, 4):
        S(x, y, z, 'water[level=0]')
    S(x, FY, z, 'water[level=0]')


for lz in range(-3, 99):
    for lx in (-2, -3, 55, 56):
        moat(lx, lz)
for lx in range(-3, 57):
    for lz in (-2, -3, 97, 98):
        moat(lx, lz)
# 해자 바깥 산책로 (x -4 / 57, z -4 / 99)
for lz in range(-4, 100):
    for lx in (-4, 57):
        S(lx, FY, lz, mix([('cobblestone', 0.3), ('stone_bricks', 0.4), ('mossy_cobblestone', 0.3)]))
for lx in range(-4, 58):
    for lz in (-4, 99):
        S(lx, FY, lz, mix([('cobblestone', 0.3), ('stone_bricks', 0.4), ('mossy_cobblestone', 0.3)]))

# ------------------------------------------------------------------ 6. 관중석 (양옆, x -5..-9 / 58..62)
SEAT_WOOD = 'dark_oak'
for side, xs, facing in (('w', [-5, -6, -7, -8], 'east'), ('e', [58, 59, 60, 61], 'west')):
    for lz in range(2, 94):
        col = team_of(lz)
        if lz in (46, 47, 48, 49):        # 가운데 통로 (강 쪽)
            for i, lx in enumerate(xs):
                fill(lx, FY, lz, lx, FY + i, lz, 'stone_bricks')
                S(lx, FY + i + 1, lz, slab('stone_brick'))
            continue
        for i, lx in enumerate(xs):
            h = FY + 1 + i
            fill(lx, FY, lz, lx, h - 1, lz, 'stone_bricks' if i == 0 else 'spruce_planks')
            if lz % 8 == 0:               # 계단 통로
                S(lx, h, lz, stairs('stone_brick', facing))
            else:
                S(lx, h, lz, f'{col}_concrete' if (lz + i) % 2 else f'{col}_terracotta')
                S(lx, h + 1, lz, f'{col}_carpet')
    # 뒤 벽 + 기둥 + 깃발
    wx = -9 if side == 'w' else 62
    for lz in range(0, 96):
        col = team_of(lz)
        fill(wx, FY, lz, wx, FY + 6, lz, 'stone_bricks')
        S(wx, FY + 7, lz, 'stone_brick_wall' if lz % 2 else 'stone_bricks')
        if lz % 8 == 4:
            fill(wx, FY, lz, wx, FY + 8, lz, 'chiseled_stone_bricks' if True else 'stone_bricks')
            S(wx, FY + 9, lz, lantern())
            ffacing = 'east' if side == 'w' else 'west'
            S(wx + (1 if side == 'w' else -1), FY + 7, lz, banner(col, ffacing))
            S(wx + (1 if side == 'w' else -1), FY + 6, lz, lantern(True) if False else AIR)
        if lz % 8 == 0:
            S(wx, FY + 3, lz, 'shroomlight')

# ------------------------------------------------------------------ 7. 지휘대 (성 탑) — 바닥 schem y 21
BY = 21


def keep(z0, z1, col, toward):
    """로컬 x 18..35, z z0..z1 성 탑. toward = 필드 쪽 방향 (+1 / -1 z)"""
    x0, x1 = 18, 35
    # 몸통
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            wall = x in (x0, x1) or z in (z0, z1)
            for y in range(FY, BY):
                if wall:
                    b = 'stone_bricks'
                    if x in (x0, x1) and z in (z0, z1):
                        b = 'polished_deepslate'
                    elif (y - FY) % 5 == 4:
                        b = 'deepslate_bricks'
                    S(x, y, z, b)
                elif y == FY:
                    S(x, y, z, 'polished_andesite')
            S(x, BY, z, 'polished_andesite' if (x + z) % 2 else 'smooth_stone')
    # 창문 (팀색 유리)
    for y in (FY + 4, FY + 5, FY + 10, FY + 11):
        for x in range(x0 + 3, x1 - 2, 4):
            for z in (z0, z1):
                S(x, y, z, f'{col}_stained_glass')
    # 정문 (필드 반대쪽)
    gz = z0 if toward > 0 else z1
    for x in range(25, 29):
        for y in range(FY + 1, FY + 5):
            S(x, y, gz, AIR)
    S(24, FY + 3, gz - toward, lantern()); S(29, FY + 3, gz - toward, lantern())
    fill(25, FY + 5, gz, 28, FY + 5, gz, 'chiseled_stone_bricks')
    # 지휘 발코니 바닥 (로컬 x 20..33) + 필드 쪽 난간
    rz = z1 + 1 if toward > 0 else z0 - 1
    for x in range(x0, x1 + 1):
        S(x, BY, rz, 'polished_andesite')
        S(x, BY - 1, rz, stairs('stone_brick', 'south' if toward < 0 else 'north', 'top'))
        S(x, BY + 1, rz, f'{col}_stained_glass_pane' if 20 <= x <= 33 else 'stone_brick_wall')
    # 기둥 4개 + 지붕
    for x in (x0, x1):
        for z in (z0, z1, rz):
            fill(x, BY + 1, z, x, BY + 4, z, 'stripped_dark_oak_log[axis=y]')
    for x in range(x0 - 1, x1 + 2):
        for z in range(min(z0, rz) - 1, max(z1, rz) + 2):
            S(x, BY + 5, z, 'dark_oak_planks' if x in (x0 - 1, x1 + 1) or z in (min(z0, rz) - 1, max(z1, rz) + 1) else f'{col}_terracotta')
    for x in range(x0, x1 + 1):
        for z in range(min(z0, rz), max(z1, rz) + 1):
            S(x, BY + 6, z, slab('deepslate_tile'))
    # 지붕 아래 등불 + 팀 깃발
    for x in (x0 + 4, (x0 + x1) // 2, x1 - 4):
        S(x, BY + 4, (z0 + z1) // 2, lantern(True))
    for x in range(x0 + 2, x1 - 1, 3):
        S(x, BY + 4, rz + toward, banner(col, 'south' if toward > 0 else 'north'))
    # 성벽 꼭대기 톱니 (지붕 위 깃대)
    for x in (x0, x1):
        fill(x, BY + 6, (z0 + z1) // 2, x, BY + 8, (z0 + z1) // 2, 'dark_oak_fence')
        S(x, BY + 7, (z0 + z1) // 2 + 1, f'{col}_wool'); S(x, BY + 8, (z0 + z1) // 2 + 1, f'{col}_wool')


keep(-16, -7, 'blue', +1)    # 발코니 z -6 (필드 쪽)
keep(103, 112, 'red', -1)    # 발코니 z 102
# 지휘대 앞 다리 (해자 위, 성 탑 → 산책로)
for lz in list(range(-3, -1)) + list(range(97, 99)):
    for lx in range(24, 30):
        S(lx, FY, lz, 'spruce_planks')
    for lx in (23, 30):
        S(lx, FY, lz, 'stone_bricks'); S(lx, FY + 1, lz, 'spruce_fence')

# ------------------------------------------------------------------ 8. 모서리 원형 탑 4개
def round_tower(cx, cz, col, r=3.6, top=FY + 14):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                shell = d > r - 1.2
                for y in range(FY, top + 1):
                    if shell:
                        b = 'stone_bricks' if (y + x + z) % 7 else 'mossy_stone_bricks'
                        if (y - FY) % 6 == 5:
                            b = 'deepslate_bricks'
                        S(x, y, z, b)
                    else:
                        S(x, y, z, 'polished_andesite' if y in (FY, top) else AIR)
                if shell and (x + z) % 2 == 0:
                    S(x, top + 1, z, 'stone_bricks')     # 총안
    # 원뿔 지붕
    for k in range(7):
        rr = r + 0.4 - k * 0.65
        if rr <= 0.2:
            break
        for x in range(int(cx - rr - 1), int(cx + rr + 2)):
            for z in range(int(cz - rr - 1), int(cz + rr + 2)):
                if math.hypot(x - cx, z - cz) <= rr:
                    S(x, top + 2 + k, z, 'deepslate_tiles' if k % 2 == 0 else f'{col}_terracotta')
    # 깃대 + 깃발
    fx, fz = int(round(cx)), int(round(cz))
    fill(fx, top + 7, fz, fx, top + 9, fz, 'dark_oak_fence')
    S(fx + 1, top + 9, fz, f'{col}_wool'); S(fx + 1, top + 8, fz, f'{col}_wool'); S(fx + 2, top + 9, fz, f'{col}_wool')
    # 창 (빛)
    for y in (FY + 4, FY + 9):
        for (dx, dz) in ((r - 0.5, 0), (-r + 0.5, 0), (0, r - 0.5), (0, -r + 0.5)):
            S(int(round(cx + dx)), y, int(round(cz + dz)), 'glowstone' if y == FY + 9 else f'{col}_stained_glass')


round_tower(-5.5, -7.5, 'blue', r=3.4); round_tower(59.5, -7.5, 'blue', r=3.4)
round_tower(-5.5, 103.5, 'red', r=3.4); round_tower(59.5, 103.5, 'red', r=3.4)

# ------------------------------------------------------------------ 9. 끝쪽 성벽 (탑 사이) + 바깥 정원
for lz, col in ((-12, 'blue'), (108, 'red')):
    for lx in list(range(-3, 18)) + list(range(36, 57)):
        fill(lx, FY, lz, lx, FY + 7, lz, 'stone_bricks' if (lx % 9) else 'chiseled_stone_bricks')
        S(lx, FY + 8, lz, 'stone_bricks' if lx % 2 else AIR)
        if lx % 9 == 4:
            S(lx, FY + 5, lz + (1 if col == 'blue' else -1), banner(col, 'south' if col == 'blue' else 'north'))
            S(lx, FY + 9, lz, lantern())
    # 성벽과 해자 사이 정원
    z_lo, z_hi = (-11, -5) if col == 'blue' else (100, 107)
    for lz2 in range(z_lo, z_hi + 1):
        for lx in list(range(-3, 17)) + list(range(37, 57)):
            if G(lx, FY + 1, lz2) == AIR and G(lx, FY, lz2).startswith('minecraft:grass'):
                r = rng.random()
                if r < 0.08:
                    S(lx, FY + 1, lz2, 'azalea_leaves[distance=1,persistent=true,waterlogged=false]')
                elif r < 0.12:
                    S(lx, FY + 1, lz2, 'flowering_azalea_leaves[distance=1,persistent=true,waterlogged=false]')
                elif r < 0.2:
                    S(lx, FY + 1, lz2, rng.choice(['poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'azure_bluet']))
                elif r < 0.45:
                    S(lx, FY + 1, lz2, 'short_grass')

# 산책로 가로등 (해자 바깥 x -4 / 57)
for lz in range(4, 96, 12):
    for lx in (-4, 57):
        if G(lx, FY + 1, lz) == AIR:
            S(lx, FY + 1, lz, 'stone_brick_wall'); S(lx, FY + 2, lz, 'stone_brick_wall'); S(lx, FY + 3, lz, lantern())

# ------------------------------------------------------------------ 10. 벽/울타리/판유리 연결 상태 계산
def solid(b):
    if b == AIR:
        return False
    n = b.split('[')[0]
    for bad in ('lantern', 'banner', 'carpet', 'water', 'lily_pad', 'grass', 'seagrass', 'poppy', 'dandelion', 'cornflower',
                'daisy', 'bluet', 'slab', 'stairs', 'short_grass'):
        if bad in n and not n.endswith('grass_block'):
            return False
    return True


def connect():
    H_, L_, W_ = g.shape
    for y in range(H_):
        for z in range(L_):
            for x in range(W_):
                b = g[y, z, x]
                base = b.split('[')[0]
                is_wall = base.endswith('_wall') and 'banner' not in base
                is_fence = base.endswith('_fence')
                is_pane = base.endswith('_pane') or base.endswith('iron_bars')
                if not (is_wall or is_fence or is_pane):
                    continue
                sides = {}
                for name, dx, dz in (('north', 0, -1), ('south', 0, 1), ('east', 1, 0), ('west', -1, 0)):
                    xx, zz = x + dx, z + dz
                    nb = g[y, zz, xx] if 0 <= xx < W_ and 0 <= zz < L_ else AIR
                    nbase = nb.split('[')[0]
                    same = (nbase.endswith('_wall') and 'banner' not in nbase) or nbase.endswith('_fence') or nbase.endswith('_pane') or nbase.endswith('iron_bars')
                    sides[name] = same or solid(nb)
                if is_wall:
                    above = g[y + 1, z, x] if y + 1 < H_ else AIR
                    straight = (sides['north'] and sides['south'] and not sides['east'] and not sides['west']) or \
                               (sides['east'] and sides['west'] and not sides['north'] and not sides['south'])
                    up = (not straight) or (above != AIR and 'lantern' in above)
                    st = ','.join(f'{k}={"low" if v else "none"}' for k, v in (('east', sides['east']), ('north', sides['north']), ('south', sides['south']), ('west', sides['west'])))
                    g[y, z, x] = f'{base}[{st},up={"true" if up else "false"},waterlogged=false]'
                else:
                    st = ','.join(f'{k}={"true" if v else "false"}' for k, v in (('east', sides['east']), ('north', sides['north']), ('south', sides['south']), ('west', sides['west'])))
                    g[y, z, x] = f'{base}[{st},waterlogged=false]'


connect()

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else 'clash_arena.schem'
    schem.save(out, g, [-36, -6, -65], name='clash_arena')
    print('saved', out)
