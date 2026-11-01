"""앞 프리뷰에 없던 모델들을 경기장에 자동 배치해서 렌더"""
import sys, json
sys.path.insert(0, '.')
from scene_render import Scene
from measure_model import measure
from PIL import Image, ImageDraw, ImageFont
B = 'pkg370/ClashMC_v3.7.0/models/base/'
BLUE, RED = (70, 120, 235), (225, 65, 55)
X0, Z0, Y = 9, 17, 6
REST = ['electro_giant', 'giant_skeleton', 'elixir_golem', 'goblin_brawler', 'ice_golem', 'battle_ram', 'skeleton_balloon',
        'barbarian_hut', 'goblin_cage', 'tombstone', 'elixir_collector', 'cannon_cart',
        'dark_prince', 'ram_rider', 'executioner', 'mother_witch', 'night_witch', 'witch', 'magic_archer', 'ice_wizard',
        'electro_wizard', 'hunter', 'miner', 'lumberjack', 'barbarian', 'elite_barbarian', 'zappies', 'royal_hog', 'cursed_hog',
        'princess', 'firecracker', 'bandit', 'guard', 'bomber', 'dart_goblin', 'spear_goblin', 'wall_breaker',
        'elixir_golemite', 'golemite', 'fire_spirit', 'ice_spirit', 'electro_spirit', 'heal_spirit', 'elixir_blob']
AIR = ['electro_dragon', 'inferno_dragon', 'flying_machine', 'sparky', 'mega_minion', 'bat', 'lava_pup']
AIRSET = {'electro_dragon', 'inferno_dragon', 'flying_machine', 'mega_minion', 'bat', 'lava_pup'}
def size(m):
    d = json.load(open(B + 'clash_%s.bbmodel' % m)); a = measure(d)
    return a[0], a[1], a[2]
KO = {'electro_giant':'일렉트로 자이언트','giant_skeleton':'자이언트 해골','elixir_golem':'엘릭서 골렘','goblin_brawler':'고블린 싸움꾼','ice_golem':'얼음 골렘',
 'battle_ram':'배틀 램','skeleton_balloon':'해골 통','barbarian_hut':'바바리안 오두막','goblin_cage':'고블린 우리','tombstone':'해골 무덤','elixir_collector':'엘릭서 정제소',
 'cannon_cart':'대포 카트','dark_prince':'다크 프린스','ram_rider':'램 라이더','executioner':'도끼맨','mother_witch':'어미 마녀','night_witch':'밤의 마녀','witch':'마녀',
 'magic_archer':'마법 아처','ice_wizard':'얼음 마법사','electro_wizard':'일렉트로 마법사','hunter':'사냥꾼','miner':'광부','lumberjack':'나무꾼','barbarian':'바바리안',
 'elite_barbarian':'엘리트 바바리안','zappies':'감전돌이','royal_hog':'로얄 호그','cursed_hog':'저주 호그','princess':'프린세스','firecracker':'로켓병','bandit':'도둑',
 'guard':'가드','bomber':'폭탄병','dart_goblin':'다트 고블린','spear_goblin':'창 고블린','wall_breaker':'해골 돌격병','elixir_golemite':'엘릭서 골렘 조각','golemite':'작은 골렘',
 'fire_spirit':'파이어 스피릿','ice_spirit':'아이스 스피릿','electro_spirit':'일렉트로 스피릿','heal_spirit':'힐 스피릿','elixir_blob':'엘릭서 방울',
 'electro_dragon':'일렉트로 드래곤','inferno_dragon':'인페르노 드래곤','flying_machine':'플라잉 머신','sparky':'스파키','mega_minion':'메가 미니언','bat':'박쥐','lava_pup':'라바 펍'}
from scene_render import project
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 21)
def towers(S):
    for team, tz, ktz, yaw, col in (('b', 5, 1, 180, BLUE), ('r', 24, 27, 0, RED)):
        for tx in (2, 13):
            p = (X0 + tx * 3 + 4.5, Y, Z0 + tz * 3 + 4.5)
            S.add_model(B + 'clash_princess_tower.bbmodel', p, yaw, col)
            S.add_model(B + 'clash_princess_top.bbmodel', (p[0], Y + 78 / 16 * 1.4529, p[2]), yaw, col)
        S.add_model(B + 'clash_king.bbmodel', (X0 + 7 * 3 + 6, Y, Z0 + ktz * 3 + 6), yaw, col)
allm = sorted(REST + AIR, key=lambda m: -size(m)[2])
# 줄 나누기 (폭 52 안에)
rows = []; cur = []; x = 0
for m in allm:
    w = size(m)[0]
    if cur and x + w > 50:
        rows.append(cur); cur = []; x = 0
    cur.append(m); x += w + 1.6
rows.append(cur)
print('rows', [len(r) for r in rows])
for gi in range(0, len(rows), 2):
    S = Scene(); S.add_schem('prevmap/clash_arena.schem'); towers(S)
    placed = []
    for k, (row, zc) in enumerate(zip(rows[gi:gi + 2], (Z0 + 28, Z0 + 40))):
        tot = sum(size(m)[0] for m in row) + 1.6 * (len(row) - 1)
        x = X0 + 27 - tot / 2   # 빨강 쪽에서 보면 오른쪽이 +x
        for m in row:
            w, dpt, h = size(m)
            px = x + w / 2
            y = Y + (4 if m in AIRSET else 0)
            S.add_model(B + 'clash_%s.bbmodel' % m, (px, y, zc), 180, BLUE)
            placed.append((m, px, zc + max(dpt, 1.5) / 2 + 1.0, h)); x += w + 1.6
    cam = (0.0, 0.55, 1.0); ctr = (X0 + 27, Y + 4, Z0 + 33); size_ = (2200, 1300); span = 58
    im = S.render(size_, cam, ctr, span); dr = ImageDraw.Draw(im)
    for i, (m, px, lz, h) in enumerate(placed):
        u, v = project(size_, cam, ctr, span, (px, Y, lz)); t = KO.get(m, m)
        v += 30 * (i % 2)
        t2 = '%s  %.1f×%.1f' % (t, size(m)[0], h)
        tw = dr.textlength(t2, font=FONT)
        dr.text((u - tw / 2, v), t2, font=FONT, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    im.save('preview_tmp/rest_%d.png' % (gi // 2 + 1))
