#!/usr/bin/env python3
"""스트리머 모드 / 관전 GUI 배경 + 아이콘 생성
- 배경: newgui/gui_streamer.png, gui_spectate.png, gui_streamer_admin.png (176x222, 기존 GUI 스타일)
- 아이콘: newicons3/ui_*.png (32x32) → mkpack370.py 가 팩에 넣음
"""
import os, sys, zipfile, io
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(W, 'ClashMC_UI_pack_360.zip')
OUT_GUI = os.path.join(W, 'newgui')
OUT_ICON = os.path.join(W, 'newicons3')
os.makedirs(OUT_GUI, exist_ok=True)
FONT = None
for f in ('/mnt/c/Windows/Fonts/malgunbd.ttf', 'C:/Windows/Fonts/malgunbd.ttf'):
    if os.path.exists(f):
        FONT = f
        break

z = zipfile.ZipFile(PACK)


def tex(path):
    return Image.open(io.BytesIO(z.read(path))).convert('RGBA')


def font(size):
    return ImageFont.truetype(FONT, size)


# ------------------------------------------------------------------ 글자
def text_img(s, size, fill, outline=(0, 0, 0, 255)):
    f = font(size)
    l, t, r, b = f.getbbox(s)
    w, h = r - l + 4, b - t + 4
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((2 - l, 2 - t), s, font=f, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    mp = m.load()
    op = out.load()
    if outline is not None:
        for y in range(h):
            for x in range(w):
                if mp[x, y]:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            xx, yy = x + dx, y + dy
                            if 0 <= xx < w and 0 <= yy < h:
                                op[xx, yy] = outline
    for y in range(h):
        for x in range(w):
            if mp[x, y]:
                op[x, y] = fill
    return out


def put_text(img, s, cx, cy, size=10, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255)):
    t = text_img(s, size, fill, outline)
    img.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))


# ------------------------------------------------------------------ 배경 다시 칠하기
def wipe(img, src):
    """윗칸(슬롯 영역) 내용을 지우고 줄무늬 배경만 다시 그림"""
    p, sp = img.load(), src.load()
    for y in range(16, 127):
        c = sp[4, y] if sp[4, y][3] > 200 else sp[5, y]
        for x in range(5, 171):
            p[x, y] = (255, 255, 255, 6) if (x - y) % 6 == 0 else c


def slot_xy(slot):
    r, c = divmod(slot, 9)
    return 8 + c * 18, 18 + r * 18


def frames(img, slots):
    """기존 GUI 와 같은 어두운 아이템 칸 테두리"""
    d = ImageDraw.Draw(img)
    for s in slots:
        x, y = slot_xy(s)
        d.rectangle([x - 1, y - 1, x + 16, y + 16], fill=(14, 16, 24, 255))
        d.line([x - 1, y - 1, x + 16, y - 1], fill=(6, 7, 10, 255))
        d.line([x - 1, y - 1, x - 1, y + 16], fill=(6, 7, 10, 255))
        d.line([x - 1, y + 16, x + 16, y + 16], fill=(110, 116, 140, 255))
        d.line([x + 16, y - 1, x + 16, y + 16], fill=(110, 116, 140, 255))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def panel(img, r0, c0, r1, c1, top, bot, label, sub=None):
    x0, y0 = 8 + c0 * 18, 18 + r0 * 18
    x1, y1 = 8 + (c1 + 1) * 18 - 3, 18 + (r1 + 1) * 18 - 3
    d = ImageDraw.Draw(img)
    d.rectangle([x0 + 1, y0, x1 - 1, y1], fill=(0, 0, 0, 255))
    d.rectangle([x0, y0 + 1, x1, y1 - 1], fill=(0, 0, 0, 255))
    for y in range(y0 + 1, y1):
        c = lerp(top, bot, (y - y0) / max(1, y1 - y0))
        d.line([x0 + 1, y, x1 - 1, y], fill=c)
    d.line([x0 + 2, y0 + 1, x1 - 2, y0 + 1], fill=lerp(top, (255, 255, 255), 0.35))
    d.line([x0 + 2, y1 - 1, x1 - 2, y1 - 1], fill=lerp(bot, (0, 0, 0), 0.35))
    # 가운데 아이템 칸 자리 (살짝 어둡게)
    put_text(img, label, (x0 + x1) / 2 + 0.5, y1 - 7, 9)
    if sub:
        put_text(img, sub, (x0 + x1) / 2 + 0.5, y0 + 6, 8, fill=(255, 255, 255, 220))


def icon_spot(img, slot, col):
    """패널 가운데 아이템이 놓일 자리: 둥근 반투명 원"""
    x, y = slot_xy(slot)
    d = ImageDraw.Draw(img)
    d.ellipse([x - 3, y - 3, x + 18, y + 18], fill=col)


# ------------------------------------------------------------------ GUI: 스트리머 모드
def gui_streamer():
    base = tex('assets/clashmc/textures/font/gui_ai.png')
    img = base.copy()
    wipe(img, base)
    frames(img, [45, 49, 53])
    # 위 3개: 큰 토글
    panel(img, 0, 0, 2, 2, (232, 70, 70), (140, 24, 30), '스트리머')
    panel(img, 0, 3, 2, 5, (160, 92, 220), (88, 40, 140), '귓속말 차단')
    panel(img, 0, 6, 2, 8, (236, 140, 50), (160, 76, 18), '욕설 필터')
    # 아래 3개
    panel(img, 3, 0, 4, 2, (70, 140, 232), (30, 76, 160), '채팅 끄기')
    panel(img, 3, 3, 4, 5, (40, 180, 170), (18, 104, 100), '관전 목록')
    panel(img, 3, 6, 4, 8, (110, 120, 140), (58, 64, 80), '도움말')
    for s, c in ((10, (0, 0, 0, 70)), (13, (0, 0, 0, 70)), (16, (0, 0, 0, 70)), (28, (0, 0, 0, 70)), (31, (0, 0, 0, 70)), (34, (0, 0, 0, 70))):
        icon_spot(img, s, c)
    img.save(os.path.join(OUT_GUI, 'gui_streamer.png'))


def gui_grid(name, title):
    base = tex('assets/clashmc/textures/font/gui_rooms.png')
    img = base.copy()
    frames(img, [45, 47, 49, 51, 53])
    put_text(img, title, 88, 26, 9, fill=(220, 230, 220, 255), outline=(12, 14, 22, 255))
    img.save(os.path.join(OUT_GUI, name + '.png'))


# ------------------------------------------------------------------ 아이콘 (32x32)
K = (20, 20, 28, 255)  # 외곽선


def new():
    return Image.new('RGBA', (32, 32), (0, 0, 0, 0))


def save_icon(img, name):
    img.save(os.path.join(OUT_ICON, 'ui_%s.png' % name))


FONT3 = {
    'L': ['X..', 'X..', 'X..', 'X..', 'XXX'],
    'I': ['XXX', '.X.', '.X.', '.X.', 'XXX'],
    'V': ['X.X', 'X.X', 'X.X', 'X.X', '.X.'],
    'E': ['XXX', 'X..', 'XX.', 'X..', 'XXX'],
    '*': ['X.X', '.X.', 'X.X', '...', '...'],
}


def pix_text(d, s, x, y, col, scale=1):
    for ch in s:
        g = FONT3[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    d.rectangle([x + i * scale, y + j * scale, x + i * scale + scale - 1, y + j * scale + scale - 1], fill=col)
        x += 4 * scale


def rrect(d, box, fill, shade=None, outline=K):
    x0, y0, x1, y1 = box
    d.rectangle([x0 + 1, y0, x1 - 1, y1], fill=outline)
    d.rectangle([x0, y0 + 1, x1, y1 - 1], fill=outline)
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=fill)
    if shade:
        d.rectangle([x0 + 1, y1 - 3, x1 - 1, y1 - 1], fill=shade)
        d.line([x0 + 2, y0 + 1, x1 - 2, y0 + 1], fill=lerp(fill, (255, 255, 255), 0.4))


def icon_live(on):
    img = new()
    d = ImageDraw.Draw(img)
    body, shade, txt = ((226, 56, 56, 255), (160, 28, 34, 255), (255, 255, 255, 255)) if on else ((128, 136, 150, 255), (88, 94, 106, 255), (200, 204, 212, 255))
    # 안테나
    d.line([10, 3, 14, 8], fill=K, width=2)
    d.line([22, 3, 18, 8], fill=K, width=2)
    rrect(d, (2, 8, 29, 27), body, shade)
    d.rectangle([5, 11, 26, 23], fill=lerp(body, (0, 0, 0), 0.25))
    pix_text(d, 'LIVE', 6, 13, txt, 1)
    # 녹화 점
    dot = (255, 240, 120, 255) if on else (150, 154, 162, 255)
    d.rectangle([24, 13, 25, 14], fill=dot)
    save_icon(img, 'live_on' if on else 'live_off')


def bubble(d, fill, shade):
    d.rectangle([3, 4, 28, 21], fill=K)
    d.rectangle([4, 3, 27, 22], fill=K)
    d.rectangle([4, 4, 27, 21], fill=fill)
    d.rectangle([4, 19, 27, 21], fill=shade)
    d.polygon([(8, 21), (8, 28), (15, 21)], fill=K)
    d.polygon([(9, 21), (9, 26), (13, 21)], fill=fill)


def lock(d, x, y, body=(244, 196, 64, 255), shade=(184, 130, 20, 255)):
    d.rectangle([x + 2, y, x + 8, y + 6], fill=K)
    d.rectangle([x + 4, y + 2, x + 6, y + 6], fill=(0, 0, 0, 0))
    d.rectangle([x + 3, y + 1, x + 7, y + 1], fill=(170, 176, 188, 255))
    d.rectangle([x + 3, y + 1, x + 3, y + 5], fill=(170, 176, 188, 255))
    d.rectangle([x + 7, y + 1, x + 7, y + 5], fill=(170, 176, 188, 255))
    d.rectangle([x, y + 5, x + 10, y + 14], fill=K)
    d.rectangle([x + 1, y + 6, x + 9, y + 13], fill=body)
    d.rectangle([x + 1, y + 11, x + 9, y + 13], fill=shade)
    d.rectangle([x + 5, y + 8, x + 5, y + 10], fill=K)


def slash(d):
    d.line([4, 28, 28, 4], fill=K, width=5)
    d.line([5, 27, 27, 5], fill=(230, 50, 50, 255), width=3)


def icon_whisper(on):
    img = new()
    d = ImageDraw.Draw(img)
    if on:
        bubble(d, (196, 150, 240, 255), (150, 100, 200, 255))
        for x in (9, 15, 21):
            d.rectangle([x, 11, x + 2, 13], fill=(90, 50, 130, 255))
        lock(d, 19, 15)
    else:
        bubble(d, (228, 232, 242, 255), (186, 192, 210, 255))
        for x in (9, 15, 21):
            d.rectangle([x, 11, x + 2, 13], fill=(110, 118, 140, 255))
    save_icon(img, 'whisper_on' if on else 'whisper_off')


def icon_filter(on):
    img = new()
    d = ImageDraw.Draw(img)
    body, shade = ((70, 140, 236, 255), (40, 90, 180, 255)) if on else ((128, 136, 150, 255), (90, 96, 108, 255))
    pts = [(16, 2), (28, 6), (28, 16), (16, 30), (4, 16), (4, 6)]
    d.polygon(pts, fill=K)
    d.polygon([(16, 4), (26, 7), (26, 16), (16, 27), (6, 16), (6, 7)], fill=body)
    d.polygon([(16, 4), (16, 27), (6, 16), (6, 7)], fill=lerp(body, (255, 255, 255), 0.18))
    d.polygon([(16, 20), (26, 16), (16, 27)], fill=shade)
    star = (255, 255, 255, 255) if on else (205, 208, 216, 255)
    for x in (9, 14, 19):
        pix_text(d, '*', x, 12, star, 1)
    save_icon(img, 'filter_on' if on else 'filter_off')


def icon_chat(hidden):
    img = new()
    d = ImageDraw.Draw(img)
    bubble(d, (96, 204, 96, 255), (56, 150, 60, 255))
    for x in (9, 15, 21):
        d.rectangle([x, 11, x + 2, 13], fill=(255, 255, 255, 255))
    if hidden:
        slash(d)
    save_icon(img, 'chat_hidden' if hidden else 'chat_shown')


def icon_eye(off):
    img = new()
    d = ImageDraw.Draw(img)
    d.ellipse([1, 7, 30, 25], fill=K)
    d.ellipse([3, 9, 28, 23], fill=(240, 244, 250, 255))
    d.ellipse([10, 9, 21, 22], fill=K)
    d.ellipse([11, 10, 20, 21], fill=(60, 150, 230, 255))
    d.ellipse([13, 12, 18, 19], fill=(16, 22, 40, 255))
    d.rectangle([14, 12, 15, 13], fill=(255, 255, 255, 255))
    if off:
        slash(d)
    save_icon(img, 'spectate_off' if off else 'spectate')


def icon_streamer():
    img = new()
    d = ImageDraw.Draw(img)
    # 캠코더
    rrect(d, (2, 9, 21, 25), (156, 92, 216, 255), (110, 56, 170, 255))
    d.polygon([(21, 13), (29, 9), (29, 25), (21, 21)], fill=K)
    d.polygon([(22, 14), (28, 11), (28, 23), (22, 20)], fill=(120, 70, 180, 255))
    d.ellipse([5, 3, 12, 10], fill=K)
    d.ellipse([6, 4, 11, 9], fill=(90, 96, 110, 255))
    d.ellipse([12, 3, 19, 10], fill=K)
    d.ellipse([13, 4, 18, 9], fill=(90, 96, 110, 255))
    d.ellipse([5, 13, 10, 18], fill=(255, 70, 70, 255))
    d.rectangle([6, 14, 7, 15], fill=(255, 200, 200, 255))
    save_icon(img, 'streamer')


def icon_lock():
    img = new()
    d = ImageDraw.Draw(img)
    big = Image.new('RGBA', (11, 15), (0, 0, 0, 0))
    lock(ImageDraw.Draw(big), 0, 0)
    img.alpha_composite(big.resize((22, 30), Image.NEAREST), (5, 1))
    save_icon(img, 'lock')


if __name__ == '__main__':
    if FONT is None:
        sys.exit('malgunbd.ttf 없음')
    gui_streamer()
    gui_grid('gui_spectate', '관전할 경기를 고르세요')
    gui_grid('gui_streamer_admin', '클릭해서 스트리머 지정 / 해제')
    for b in (True, False):
        icon_live(b)
        icon_whisper(b)
        icon_filter(b)
        icon_chat(b)
        icon_eye(b)
    icon_streamer()
    icon_lock()
    print('ok')
