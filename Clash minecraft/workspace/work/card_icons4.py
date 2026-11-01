"""카드 아이콘 3.7.0: 실제 클래시 로얄 카드 일러스트(RoyaleAPI cr-api-assets) 128x128 + 엘릭서 배지, _off 는 흑백."""
import os, sys, yaml
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(W, '../crart'); OUT = os.path.join(W, 'newicons3')
cfg = yaml.safe_load(open(os.path.join(W, 'dec/config.yml'), encoding='utf-8'))['cards']
FONT = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 30 * 4 // 2)
S = 128

def drop(n):
    """엘릭서 물방울 배지 (4배로 그려서 줄임)"""
    k = 4; w, h = 34 * k, 40 * k
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def shape(off, fill):
        cx, cy, r = w / 2, h - 16 * k, 14 * k - off
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
        d.polygon([(cx - r * 0.86, cy - r * 0.5), (cx, 2 * k + off * 1.6), (cx + r * 0.86, cy - r * 0.5)], fill=fill)
    shape(0, (40, 6, 56, 255)); shape(2.2 * k, (196, 54, 232, 255)); 
    # 하이라이트
    d.ellipse([w / 2 - 8 * k, h - 27 * k, w / 2 - 3 * k, h - 21 * k], fill=(240, 180, 255, 255))
    t = str(n)
    bb = d.textbbox((0, 0), t, font=FONT, stroke_width=3 * k // 2)
    x = (w - (bb[2] - bb[0])) / 2 - bb[0]; y = h - 16 * k - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((x, y), t, font=FONT, fill=(255, 255, 255, 255), stroke_width=3 * k // 2, stroke_fill=(40, 6, 56, 255))
    return im.resize((w // k, h // k), Image.LANCZOS)

def make(cid):
    art = Image.open(os.path.join(ART, cid + '.png')).convert('RGBA')
    h = S - 2; w = round(art.width * h / art.height)
    art = art.resize((w, h), Image.LANCZOS)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    im.alpha_composite(art, ((S - w) // 2 + 4, 1))
    el = (cfg.get(cid) or {}).get('elixir')
    if el is not None:
        im.alpha_composite(drop(el), (0, 0))
    im.save(os.path.join(OUT, 'card_%s.png' % cid))
    g = im.convert('LA').convert('RGBA'); g.putalpha(im.getchannel('A'))
    g = ImageEnhance.Brightness(g).enhance(0.55)
    g.save(os.path.join(OUT, 'card_%s_off.png' % cid))
    return el

if __name__ == '__main__':
    miss = []
    for f in sorted(os.listdir(ART)):
        cid = f[:-4]
        if make(cid) is None: miss.append(cid)
    print('no elixir:', miss)
