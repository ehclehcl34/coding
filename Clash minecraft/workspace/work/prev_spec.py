import sys, time
sys.path.insert(0, '.')
from scene_render import Scene
M = 'pkg370/ClashMC_v3.7.0/models/base/clash_%s.bbmodel'
BLUE, RED = (70, 120, 235), (225, 65, 55)
X0, Z0, Y = 9, 17, 6
def T(tx, tz, h=0): return (X0 + tx * 3 + 1.5, Y + h, Z0 + tz * 3 + 1.5)
S = Scene(); t = time.time()
S.add_schem('prevmap/clash_arena.schem')
for team, tz, ktz, yaw, col in (('b', 5, 1, 180, BLUE), ('r', 24, 27, 0, RED)):
    for tx in (2, 13):
        p = (X0 + tx * 3 + 4.5, Y, Z0 + tz * 3 + 4.5)
        S.add_model(M % 'princess_tower', p, yaw, col)
        S.add_model(M % 'princess_top', (p[0], Y + 78 / 16 * 1.4529, p[2]), yaw, col)
    S.add_model(M % 'king', (X0 + 7 * 3 + 6, Y, Z0 + ktz * 3 + 6), yaw, col)
# 파랑: 건물 줄 + 유닛 줄
for name, tx in (('goblin_hut', 1), ('cannon', 4), ('tesla', 7), ('inferno', 10), ('bomb_tower', 13), ('x_bow', 16)):
    S.add_model(M % name, T(tx, 10), 180, BLUE)
for name, x in (('giant', 6), ('golem', 15), ('pekka', 23), ('knight', 29.5), ('hog_rider', 34), ('goblin', 39), ('archer', 43), ('skeletons', 47), ('valkyrie', 52)):
    S.add_model(M % name, (X0 + x, Y, Z0 + 13 * 3 + 1.5), 180, BLUE)
# 빨강: 다리 건너오는 유닛 + 공중
for name, x in (('mega_knight', 6), ('royal_giant', 16), ('mini_pekka', 24), ('musketeer', 29), ('prince', 34), ('wizard', 40), ('bowler', 47)):
    S.add_model(M % name, (X0 + x, Y, Z0 + 19 * 3 + 1.5), 0, RED)
for name, x in (('baby_dragon', 8), ('balloon', 20), ('lava_hound', 36), ('minion', 44)):
    S.add_model(M % name, (X0 + x, Y + 4, Z0 + 21 * 3 + 1.5), 0, RED)
print('quads', len(S.quads), round(time.time() - t, 1))
cx = X0 + 27
S.render((1800, 1200), (0.0, 1.1, -1.0), (cx, 6, Z0 + 46), 92).save('preview_tmp/spec_iso.png'); print('iso', round(time.time() - t, 1))
S.render((1800, 1200), (0.75, 0.75, -1.0), (cx, 6, Z0 + 40), 64).save('preview_tmp/spec_close.png'); print('close', round(time.time() - t, 1))
# 위에서 본 그림 + 히트박스(원) / 건물 배치 칸(사각형)
import yaml
from PIL import ImageDraw
cards = yaml.safe_load(open('dec/config.yml', encoding='utf-8'))['cards']
bymodel = {}
for k, v in cards.items():
    m = (v.get('model') or '').split(':')[0]
    if m and m not in bymodel: bymodel[m] = v
W, H, span = 1400, 2000, 60
cz = Z0 + 48
img = S.render((W, H), (0.0, 1.0, -0.02), (cx, 6, cz), span)
sc = W / span
P = lambda x, z: (W / 2 - (x - cx) * sc, H / 2 - (z - cz) * sc)
dr = ImageDraw.Draw(img)
# 타일 격자
for i in range(19):
    dr.line([P(X0 + i * 3, Z0), P(X0 + i * 3, Z0 + 96)], fill=(255, 255, 255), width=1)
for j in range(33):
    dr.line([P(X0, Z0 + j * 3), P(X0 + 54, Z0 + j * 3)], fill=(255, 255, 255), width=1)
placed = []
for name, tx in (('goblin_hut', 1), ('cannon', 4), ('tesla', 7), ('inferno', 10), ('bomb_tower', 13), ('x_bow', 16)):
    placed.append(('clash_' + name, T(tx, 10)))
for name, x in (('giant', 6), ('golem', 15), ('pekka', 23), ('knight', 29.5), ('hog_rider', 34), ('goblin', 39), ('archer', 43), ('skeletons', 47), ('valkyrie', 52)):
    placed.append(('clash_' + name, (X0 + x, Y, Z0 + 40.5)))
for name, x in (('mega_knight', 6), ('royal_giant', 16), ('mini_pekka', 24), ('musketeer', 29), ('prince', 34), ('wizard', 40), ('bowler', 47)):
    placed.append(('clash_' + name, (X0 + x, Y, Z0 + 58.5)))
for m, (x, y, z) in placed:
    c = bymodel[m]; w = c['hitbox'][0] / 2
    a, b = P(x - w, z - w), P(x + w, z + w)
    dr.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], outline=(255, 230, 0), width=3)
    if c.get('type') == 'BUILDING':
        h = c['size']
        a, b = P(x - h, z - h), P(x + h, z + h)
        dr.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], outline=(0, 255, 255), width=3)
img.save('preview_tmp/spec_top.png'); print('top done')
