"""라바 펍: 모양 그대로, 색만 주황 용암색으로 (어두운 바위 → 주황, 빛나던 눈·입 → 진한 갈색, 날개막 → 주홍)"""
import json, base64, io, sys, colorsys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
for t in d['textures']:
    im = Image.open(io.BytesIO(base64.b64decode(t['source'].split(',')[1]))).convert('RGBA')
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            if a == 0: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if v > 0.55 and s > 0.45:                      # 빛나던 눈·입·틈 → 진한 갈색
                c = (70, 22, 6)
            elif s < 0.2 and v > 0.4:                       # 회색 발톱 → 그을린 갈색
                c = (110, 44, 14)
            elif s > 0.5 and v > 0.25:                      # 붉은 날개막 → 주홍
                k = (v - 0.25) / 0.4
                c = (int(225 + 25 * k), int(70 + 30 * k), 12)
            else:                                           # 어두운 바위 몸 → 주황 용암 (밝기 따라 단계)
                k = max(0.0, min(1.0, (v - 0.12) / 0.16))
                c = (255, int(105 + 60 * k), int(10 + 30 * k))
            px[x, y] = c + (a,)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    t['source'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
json.dump(d, open(dst, 'w'))
