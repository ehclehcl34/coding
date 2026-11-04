#!/usr/bin/env python3
"""gen_streamer_ui.py 결과 미리보기 → preview_streamer_ui.png"""
import os, sys
from PIL import Image
W = os.path.dirname(os.path.abspath(__file__))
G, I = os.path.join(W, 'newgui'), os.path.join(W, 'newicons3')


def slot_xy(s):
    r, c = divmod(s, 9)
    return 8 + c * 18, 18 + r * 18


def gui(name, items):
    bg = Image.new('RGBA', (176, 222), (198, 198, 198, 255))
    bg.alpha_composite(Image.open(os.path.join(G, name + '.png')).convert('RGBA'))
    for s, ic in items.items():
        im = Image.open(os.path.join(I, 'ui_' + ic + '.png')).convert('RGBA').resize((16, 16), Image.LANCZOS)
        bg.alpha_composite(im, slot_xy(s))
    return bg.resize((176 * 3, 222 * 3), Image.NEAREST)


a = gui('gui_streamer', {10: 'live_on', 13: 'whisper_on', 16: 'filter_off', 28: 'chat_shown', 31: 'spectate', 34: 'lock', 49: 'streamer', 53: 'streamer'})
b = gui('gui_spectate', {9: 'lock', 10: 'spectate', 47: 'spectate_off', 49: 'spectate'})
c = gui('gui_streamer_admin', {49: 'spectate'})
icons = sorted(f for f in os.listdir(I) if f[3:-4] in ('live_on', 'live_off', 'whisper_on', 'whisper_off', 'filter_on', 'filter_off', 'chat_hidden', 'chat_shown', 'spectate', 'spectate_off', 'streamer', 'lock'))
sheet = Image.new('RGBA', (176 * 9 + 40, 222 * 3 + 20 + 120), (40, 40, 40, 255))
for i, g in enumerate((a, b, c)):
    sheet.alpha_composite(g, (10 + i * (176 * 3 + 10), 10))
for i, f in enumerate(icons):
    im = Image.open(os.path.join(I, f)).convert('RGBA').resize((96, 96), Image.NEAREST)
    sheet.alpha_composite(im, (10 + i * 104, 222 * 3 + 20))
sheet.save(sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, 'preview_streamer_ui.png'))
print(len(icons))
