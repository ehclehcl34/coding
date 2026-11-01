"""얼음 마법사: 삐죽 선 얼음 머리 → 뒤로 넘긴 올백 파란 머리"""
import json, sys, copy, uuid, base64, io, random
from PIL import Image
p = sys.argv[1]
d = json.load(open(p))
E = d['elements']
tex = d['textures'][0]
im = Image.open(io.BytesIO(base64.b64decode(tex['source'].split(',')[1]))).convert('RGBA')
random.seed(3)
# 머리카락 색 패치 (빈 텍스처 영역 y 64~)
PAL = {'main': ((60, 150, 228), (44, 122, 205)), 'light': ((128, 206, 252), (96, 182, 245)), 'dark': ((30, 88, 168), (24, 70, 140)), 'grey': ((70, 110, 150), (55, 90, 128))}
P = {}
for i, (k, (a, b)) in enumerate(PAL.items()):
    x0, y0 = i * 16, 64
    for x in range(16):
        for y in range(16):
            c = a if (x % 4 != 0) else b          # 세로 줄무늬 = 빗어 넘긴 결
            j = random.randint(-6, 6)
            im.putpixel((x0 + x, y0 + y), tuple(max(0, min(255, v + j)) for v in c) + (255,))
    P[k] = (x0, y0)
buf = io.BytesIO(); im.save(buf, 'PNG')
tex['source'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

head_idx = [i for i, e in enumerate(E) if e['name'] == 'head']
drop = set(head_idx[15:])       # 21~35 남기고 뒤쪽 가시(36~50) + 왕관 가시(51~86) 삭제
drop |= {head_idx[12]}          # 32 윗머리 판 (새로 만듦)
tmpl = E[head_idx[0]]
def find_head(o):
    for x in o:
        if isinstance(x, dict):
            if x['name'] == 'head': return x
            r = find_head(x.get('children', []))
            if r: return r
hb = find_head(d['outliner'])
dropu = {E[i]['uuid'] for i in drop}
hb['children'] = [c for c in hb['children'] if not (isinstance(c, str) and c in dropu)]
keep = [e for i, e in enumerate(E) if i not in drop]

def cube(fr, to, col, rot=None, org=None):
    e = copy.deepcopy(tmpl); e['uuid'] = str(uuid.uuid4()); e['name'] = 'head'
    e['from'] = list(fr); e['to'] = list(to)
    e['origin'] = list(org) if org else [(a + b) / 2 for a, b in zip(fr, to)]
    if rot: e['rotation'] = list(rot)
    else: e.pop('rotation', None)
    x0, y0 = P[col]
    for fn in ('north', 'south', 'east', 'west', 'up', 'down'):
        e['faces'][fn] = {'uv': [x0 + 1, y0 + 1, x0 + 15, y0 + 15], 'texture': 0}
    keep.append(e); hb['children'].append(e['uuid'])

R = [-22.5, 0, 0]   # +z(뒤)로 뻗은 머리끝이 살짝 위로
# 이마에서 뒤로 넘어가는 윗머리
cube((-4.1, 27.4, -3.7), (4.1, 29.2, 4.3), 'main')
cube((-3.8, 28.9, -4.0), (3.8, 30.1, -0.6), 'light')          # 앞머리 볼륨
cube((-3.4, 29.1, -0.8), (3.4, 29.9, 3.6), 'main')
cube((-1.0, 29.9, -3.6), (1.0, 30.4, 3.0), 'light')           # 가운데 결
# 옆머리 (귀 위로 빗어 넘김)
cube((-4.45, 23.6, -1.8), (-3.6, 28.8, 4.4), 'main')
cube((3.6, 23.6, -1.8), (4.45, 28.8, 4.4), 'main')
# 뒷머리
cube((-4.1, 21.2, 3.6), (4.1, 29.0, 4.7), 'dark')
# 뒤로 뻗는 머리끝 (위로 살짝 휨)
cube((-1.3, 26.8, 4.2), (1.3, 28.6, 9.0), 'light', R, (0, 27.6, 4.2))
cube((-0.8, 27.1, 8.8), (0.8, 28.3, 10.8), 'light', R, (0, 27.6, 4.2))
cube((-3.9, 26.2, 4.2), (-1.4, 27.8, 8.0), 'main', R, (-2.6, 27.0, 4.2))
cube((-3.4, 26.5, 7.8), (-2.0, 27.5, 9.4), 'main', R, (-2.6, 27.0, 4.2))
cube((1.4, 26.2, 4.2), (3.9, 27.8, 8.0), 'main', R, (2.6, 27.0, 4.2))
cube((2.0, 26.5, 7.8), (3.4, 27.5, 9.4), 'main', R, (2.6, 27.0, 4.2))
cube((-3.2, 23.6, 4.4), (3.2, 25.6, 7.2), 'dark', R, (0, 24.6, 4.4))   # 아래층
cube((-2.0, 24.0, 7.0), (2.0, 25.2, 8.6), 'dark', R, (0, 24.6, 4.4))
d['elements'] = keep
json.dump(d, open(p, 'w'))
print('elements', len(keep))
