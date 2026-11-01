"""새 카드 아이콘 (32x32, 기존 UI 팩과 같은 틀): 등급 테두리 + 파란 그라데이션 + 모델 초상화 + 엘릭서 배지, _off(회색) 버전."""
import sys, json, collections, os
import numpy as np
from PIL import Image

TOOLS, ICONS, MODELS, OUT = sys.argv[1:5]
sys.path.insert(0, TOOLS)
from bbrender import render

TINT_BLUE = (60, 90, 255)
RARITY_TEMPLATE = {'legendary': 'miner', 'rare': 'musketeer', 'epic': 'prince', 'common': 'knight'}
BADGE_COLORS = {(0x3d, 0x0a, 0x52), (0xc1, 0x3c, 0xf0), (0xe9, 0xa4, 0xff), (0xff, 0xff, 0xff)}
WHITE = (255, 255, 255)
HI = (0xe9, 0xa4, 0xff)
MID = (0xc1, 0x3c, 0xf0)
# 엘릭서 숫자 (x 4..8, y 3..9) — 기존 아이콘과 같은 5x7 글꼴
DIGITS = {
    7: ['#####', '....#', '...#.', '...#.', '..#..', '..#..', '..#..'],
}


def load(n):
    return np.array(Image.open(os.path.join(ICONS, 'card_%s.png' % n)).convert('RGBA'))


def bg_rows():
    rows = {}
    for f in os.listdir(ICONS):
        if f.startswith('card_') and not f.endswith('_off.png'):
            a = np.array(Image.open(os.path.join(ICONS, f)).convert('RGB'))
            for y in range(3, 29):
                c = rows.setdefault(y, collections.Counter())
                for x in range(3, 29):
                    c[tuple(int(v) for v in a[y, x])] += 1
    return {y: c.most_common(1)[0][0] for y, c in rows.items()}


BG = bg_rows()


def badge_mask(a):
    m = np.zeros((32, 32), bool)
    for y in range(0, 13):
        for x in range(0, 12):
            if tuple(int(v) for v in a[y, x, :3]) in BADGE_COLORS and a[y, x, 3] > 0:
                m[y, x] = True
    return m


def highlight_region():
    hi = np.zeros((32, 32), bool)
    for f in os.listdir(ICONS):
        if f.startswith('card_') and not f.endswith('_off.png'):
            a = np.array(Image.open(os.path.join(ICONS, f)).convert('RGB'))
            for y in range(0, 12):
                for x in range(0, 11):
                    if tuple(int(v) for v in a[y, x]) == HI:
                        hi[y, x] = True
    return hi


def badge_for(elixir):
    """엘릭서 숫자가 같은 기존 카드의 배지, 없으면 숫자를 직접 그림"""
    for f in sorted(os.listdir(ICONS)):
        if not f.startswith('card_') or f.endswith('_off.png'):
            continue
    src = {1: 'ice_spirit', 2: 'zap', 3: 'miner', 4: 'musketeer', 5: 'prince', 6: 'lightning', 8: 'golem', 9: 'three_musketeers'}
    if elixir in src:
        a = load(src[elixir])
        return a, badge_mask(a)
    a = load('miner').copy()
    m = badge_mask(a)
    hi = highlight_region()
    for y in range(0, 13):
        for x in range(0, 12):
            if m[y, x] and tuple(int(v) for v in a[y, x, :3]) == WHITE:
                a[y, x, :3] = HI if hi[y, x] else MID
    for dy, row in enumerate(DIGITS[elixir]):
        for dx, ch in enumerate(row):
            if ch == '#':
                a[3 + dy, 4 + dx, :3] = WHITE
    return a, m


def portrait(model, crop_top=None, zoom=1.0, cam=(0.4, 0.25, -1.0), anchor='bottom'):
    doc = json.load(open(os.path.join(MODELS, model + '.bbmodel'), encoding='utf-8'))
    im = render(doc, 256, cam, bg=(0, 0, 0, 0), tint=TINT_BLUE)
    im = im.crop(im.getbbox())
    w, h = im.size
    if crop_top:
        im = im.crop((0, 0, w, int(h * crop_top)))
        w, h = im.size
    s = min(26 / w, 26 / h) * zoom
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (26, 26), (0, 0, 0, 0))
    ox = (26 - nw) // 2
    oy = 26 - nh if anchor == 'bottom' else (26 - nh) // 2 if anchor == 'center' else 0
    canvas.paste(im, (ox, oy), im)
    return canvas


def compose(card, rarity, elixir, port):
    base = load(RARITY_TEMPLATE[rarity]).copy()
    for y in range(3, 29):
        base[y, 3:29, :3] = BG[y]
        base[y, 3:29, 3] = 255
    img = Image.fromarray(base, 'RGBA')
    img.alpha_composite(port, (3, 3))
    a = np.array(img)
    b, m = badge_for(elixir)
    a[m] = b[m]
    on = Image.fromarray(a, 'RGBA')
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    g = np.clip(0.551 * lum - 0.58, 0, 255).astype(np.uint8)
    off = np.stack([g, g, g, a[..., 3]], -1)
    os.makedirs(OUT, exist_ok=True)
    on.save(os.path.join(OUT, 'card_%s.png' % card))
    Image.fromarray(off, 'RGBA').save(os.path.join(OUT, 'card_%s_off.png' % card))
    return on


CARDS = [
    ('elixir_collector', 'rare', 6, dict(model='clash_elixir_collector', zoom=1.0)),
    ('royal_hogs', 'rare', 5, dict(model='clash_royal_hog', zoom=1.05)),
    ('valkyrie', 'rare', 4, dict(model='clash_valkyrie', zoom=1.2, crop_top=0.8)),
    ('guards', 'epic', 3, dict(model='clash_guard', zoom=1.1)),
    ('giant_skeleton', 'epic', 6, dict(model='clash_giant_skeleton', zoom=1.15, crop_top=0.85)),
    ('bowler', 'epic', 5, dict(model='clash_bowler', zoom=1.15, crop_top=0.85)),
    ('wall_breakers', 'epic', 2, dict(model='clash_wall_breaker', zoom=1.1)),
    ('hunter', 'epic', 4, dict(model='clash_hunter', zoom=1.2, crop_top=0.8)),
    ('executioner', 'epic', 5, dict(model='clash_executioner', zoom=1.2, crop_top=0.8)),
    ('princess', 'legendary', 3, dict(model='clash_princess', zoom=1.25, crop_top=0.75)),
    ('ice_wizard', 'legendary', 3, dict(model='clash_ice_wizard', zoom=1.25, crop_top=0.75)),
    ('lumberjack', 'legendary', 4, dict(model='clash_lumberjack', zoom=1.2, crop_top=0.8)),
    ('magic_archer', 'legendary', 4, dict(model='clash_magic_archer', zoom=1.25, crop_top=0.75)),
    ('bandit', 'legendary', 3, dict(model='clash_bandit', zoom=1.25, crop_top=0.75)),
    ('inferno_dragon', 'legendary', 4, dict(model='clash_inferno_dragon', zoom=1.1, anchor='center')),
    ('mega_knight', 'legendary', 7, dict(model='clash_mega_knight', zoom=1.15, crop_top=0.85)),
]
if __name__ == '__main__':
    only = sys.argv[5:] if len(sys.argv) > 5 else None
    sheet = Image.new('RGBA', (128 * 8, 128 * 4), (30, 30, 30, 255))
    for i, (card, rar, el, p) in enumerate(CARDS):
        if only and card not in only:
            continue
        on = compose(card, rar, el, portrait(**p))
        off = Image.open(os.path.join(OUT, 'card_%s_off.png' % card))
        x, y = (i % 8) * 128, (i // 8) * 256
        sheet.paste(on.resize((128, 128), Image.NEAREST), (x, y))
        sheet.paste(off.resize((128, 128), Image.NEAREST), (x, y + 128))
    sheet.save(os.path.join(OUT, '_sheet360.png'))
    print('ok')
