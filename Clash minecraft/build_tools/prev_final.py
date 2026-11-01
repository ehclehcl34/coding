"""최종 프리뷰: 종류별로 나눠서, 탑뷰 + 플레이어(지휘대) 시점"""
import sys, json, os
sys.path.insert(0, '.')
from scene_render import Scene, project
from measure_model import measure
from PIL import Image, ImageDraw, ImageFont
B = 'pkg370/ClashMC_v3.7.0/models/base/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'preview_final'
os.makedirs(OUT, exist_ok=True)
BLUE, RED = (70, 120, 235), (225, 65, 55)
X0, Z0, Y = 9, 17, 6
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)
TFONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 34)
KO = {'cannon':'대포','tesla':'뇌전탑','inferno':'인페르노 타워','x_bow':'대형 석궁','bomb_tower':'폭탄 타워','goblin_hut':'고블린 오두막',
 'barbarian_hut':'바바리안 오두막','goblin_cage':'고블린 우리','tombstone':'해골 무덤','elixir_collector':'엘릭서 정제소',
 'giant':'자이언트','royal_giant':'로얄 자이언트','electro_giant':'일렉트로 자이언트','giant_skeleton':'자이언트 해골','golem':'골렘',
 'elixir_golem':'엘릭서 골렘','mega_knight':'메가 나이트','pekka':'P.E.K.K.A','ice_golem':'얼음 골렘','goblin_brawler':'고블린 싸움꾼',
 'bowler':'볼러','prince':'프린스','dark_prince':'다크 프린스','hog_rider':'호그 라이더','ram_rider':'램 라이더','battle_ram':'배틀 램',
 'cannon_cart':'대포 카트','knight':'기사','mini_pekka':'미니 P.E.K.K.A','valkyrie':'발키리','wizard':'마법사','ice_wizard':'얼음 마법사',
 'electro_wizard':'일렉트로 마법사','witch':'마녀','night_witch':'밤의 마녀','mother_witch':'어미 마녀','magic_archer':'마법 아처',
 'hunter':'사냥꾼','miner':'광부','lumberjack':'나무꾼','executioner':'도끼맨','barbarian':'바바리안','elite_barbarian':'엘리트 바바리안',
 'musketeer':'머스킷병','archer':'아처','princess':'프린세스','bandit':'도둑','goblin':'고블린','spear_goblin':'창 고블린',
 'dart_goblin':'다트 고블린','skeletons':'해골 병사','bomber':'폭탄병','wall_breaker':'해골 돌격병','guard':'가드','firecracker':'로켓병',
 'zappies':'감전돌이','royal_hog':'로얄 호그','cursed_hog':'저주 호그','fire_spirit':'파이어 스피릿','ice_spirit':'아이스 스피릿',
 'electro_spirit':'일렉트로 스피릿','heal_spirit':'힐링 스피릿','golemite':'작은 골렘','elixir_golemite':'엘릭서 골렘 조각',
 'elixir_blob':'엘릭서 방울','lava_pup':'라바 펍','bat':'박쥐','minion':'미니언','baby_dragon':'베이비 드래곤','inferno_dragon':'인페르노 드래곤',
 'electro_dragon':'일렉트로 드래곤','lava_hound':'라바 하운드','balloon':'해골 비행선','skeleton_balloon':'해골 통','flying_machine':'플라잉 머신',
 'sparky':'스파키','mega_minion':'메가 미니언'}
GROUPS = [
 ('건물 1', ['cannon', 'tesla', 'inferno', 'x_bow', 'bomb_tower']),
 ('건물 2', ['goblin_hut', 'barbarian_hut', 'goblin_cage', 'tombstone', 'elixir_collector']),
 ('대형 1', ['giant', 'royal_giant', 'electro_giant', 'giant_skeleton']),
 ('대형 2', ['golem', 'elixir_golem', 'mega_knight', 'pekka', 'ice_golem', 'goblin_brawler', 'bowler']),
 ('기마·돌격', ['prince', 'dark_prince', 'hog_rider', 'ram_rider', 'battle_ram', 'cannon_cart', 'royal_hog', 'cursed_hog']),
 ('인간형 1', ['knight', 'mini_pekka', 'valkyrie', 'wizard', 'ice_wizard', 'electro_wizard', 'witch', 'night_witch', 'mother_witch']),
 ('인간형 2', ['magic_archer', 'hunter', 'miner', 'lumberjack', 'executioner', 'barbarian', 'elite_barbarian', 'musketeer', 'archer', 'princess']),
 ('소형', ['bandit', 'goblin', 'spear_goblin', 'dart_goblin', 'skeletons', 'bomber', 'wall_breaker', 'guard', 'firecracker', 'zappies']),
 ('스피릿·조각', ['fire_spirit', 'ice_spirit', 'electro_spirit', 'heal_spirit', 'golemite', 'elixir_golemite', 'elixir_blob', 'lava_pup']),
 ('공중', ['baby_dragon', 'inferno_dragon', 'electro_dragon', 'lava_hound', 'flying_machine', 'mega_minion', 'minion', 'bat']),
 ('공중·비행선', ['balloon', 'skeleton_balloon', 'sparky']),
]
AIR = {'baby_dragon', 'inferno_dragon', 'electro_dragon', 'lava_hound', 'flying_machine', 'mega_minion', 'minion', 'bat', 'lava_pup', 'balloon', 'skeleton_balloon'}
SZ = {}
def size(m):
    if m not in SZ:
        a = measure(json.load(open(B + 'clash_%s.bbmodel' % m))); SZ[m] = (a[0], a[1], a[2])
    return SZ[m]
def towers(S):
    for tz, ktz, yaw, col in ((5, 1, 180, BLUE), (24, 27, 0, RED)):
        for tx in (2, 13):
            p = (X0 + tx * 3 + 4.5, Y, Z0 + tz * 3 + 4.5)
            S.add_model(B + 'clash_princess_tower.bbmodel', p, yaw, col)
            S.add_model(B + 'clash_princess_top.bbmodel', (p[0], Y + 78 / 16 * 1.4529, p[2]), yaw, col)
        S.add_model(B + 'clash_king.bbmodel', (X0 + 7 * 3 + 6, Y, Z0 + ktz * 3 + 6), yaw, col)
BASE = Scene(); BASE.add_schem('arena_350.schem'); towers(BASE)
NB = len(BASE.quads)
for gi, (title, names) in enumerate(GROUPS, 1):
    # 줄 나누기: 한 줄 폭 44 블록, 간격 넉넉하게
    rows, cur, w = [], [], 0
    for m in names:
        mw = max(size(m)[0], 2.0)
        if cur and w + mw > 44: rows.append(cur); cur, w = [], 0
        cur.append(m); w += mw + 4.0
    rows.append(cur)
    zs = [Z0 + 57] if len(rows) == 1 else [Z0 + 52, Z0 + 65]
    S = Scene(); S.quads = BASE.quads[:NB]
    placed = []
    for row, zc in zip(rows, zs):
        tot = sum(max(size(m)[0], 2.0) for m in row) + 4.0 * (len(row) - 1)
        x = X0 + 27 + tot / 2
        for m in row:
            mw, dp, h = size(m); mw = max(mw, 2.0)
            px = x - mw / 2; y = Y + (4 if m in AIR else 0)
            S.add_model(B + 'clash_%s.bbmodel' % m, (px, y, zc), 0, RED)
            placed.append((m, px, zc, dp, h, y)); x -= mw + 4.0
    views = [('top', (1400, 1150), (0.0, 1.0, -0.02), (X0 + 27, Y, Z0 + 58), 58),
             ('player', (1800, 1100), (0.0, 0.70, -1.0), (X0 + 27, Y + 3, Z0 + 56), 62)]
    for vn, size_, cam, ctr, span in views:
        im = S.render(size_, cam, ctr, span); dr = ImageDraw.Draw(im)
        for i, (m, px, zc, dp, h, y) in enumerate(placed):
            u, v = project(size_, cam, ctr, span, (px, Y, zc - max(dp, 1.5) / 2 - 0.8))
            t = '%s  %.1f×%.1f' % (KO.get(m, m), size(m)[0], h)
            tw = dr.textlength(t, font=FONT)
            dr.text((u - tw / 2, v + 4 + 26 * (i % 2 if len(placed) > 6 else 0)), t, font=FONT, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
        hdr = '%d. %s  (%s)' % (gi, title, '탑뷰' if vn == 'top' else '플레이어 시점')
        dr.text((24, 18), hdr, font=TFONT, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
        im.save('%s/%02d_%s.png' % (OUT, gi, vn))
    print(gi, title, len(placed), [len(r) for r in rows])
