"""텍스처가 여러 장인 모델을 한 장으로 합침 (BetterModel 에서 두 번째 텍스처가 붙으면 UV 가 밀려 엉뚱한 무늬가 나오는 문제).
텍스처들을 가로로 이어 붙이고 (세로로 길면 마크/BetterModel 이 애니메이션 텍스처로 봄), 각 면의 UV 를 새 위치로 옮김. usage: merge_tex.py a.bbmodel [b.bbmodel ...]"""
import json, sys, base64, io, math
from PIL import Image
for p in sys.argv[1:]:
    d = json.load(open(p))
    T = d['textures']
    if len(T) < 2: continue
    res = d.get('resolution', {'width': 16, 'height': 16})
    info = []
    for i, t in enumerate(T):
        im = Image.open(io.BytesIO(base64.b64decode(t['source'].split(',', 1)[1]))).convert('RGBA')
        uw = t.get('uv_width') or res['width']; uh = t.get('uv_height') or res['height']
        info.append((im, uw, uh))
    D = max(im.size[0] / uw for im, uw, uh in info)          # 픽셀/UV 밀도 (가장 촘촘한 것 기준)
    Hh = max(uh for _, _, uh in info)
    offs, x = [], 0
    for im, uw, uh in info:
        offs.append(x); x += uw
    W2 = 1 << math.ceil(math.log2(max(x, 1)))
    H = 1 << math.ceil(math.log2(Hh))
    H = max(H, W2)                                            # 정사각형 (가로가 더 길어도 애니메이션으로 안 봄, 안전하게)
    atlas = Image.new('RGBA', (int(W2 * D), int(H * D)), (0, 0, 0, 0))
    for (im, uw, uh), oy in zip(info, offs):
        atlas.paste(im.resize((int(uw * D), int(uh * D)), Image.NEAREST), (int(oy * D), 0))
    idmap = {}
    for i, t in enumerate(T):
        idmap[i] = i; idmap[str(t.get('id', i))] = i
    for e in d['elements']:
        for f in e['faces'].values():
            tx = f.get('texture')
            if tx is None: continue
            i = idmap.get(tx, idmap.get(str(tx), 0))
            if f.get('uv'):
                u = f['uv']; f['uv'] = [u[0] + offs[i], u[1], u[2] + offs[i], u[3]]
            f['texture'] = 0
    buf = io.BytesIO(); atlas.save(buf, 'PNG')
    t0 = T[0]
    t0['source'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    t0['width'], t0['height'] = atlas.size; t0['uv_width'], t0['uv_height'] = W2, H
    t0['id'] = '0'
    d['textures'] = [t0]
    d['resolution'] = {'width': W2, 'height': H}
    json.dump(d, open(p, 'w'))
    print('merged', p.split('/')[-1], len(T), '->', atlas.size, 'uv', W2, H)
