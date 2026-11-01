import json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work/pkg340/ClashMC_v3.4.0/source/model_tools')
from bbrender import render, sample
from PIL import Image
S = '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/'
pairs = [('princess', 'princess'), ('ice_wizard', 'ice-wizard'), ('magic_archer', 'magic-archer'), ('hunter', 'hunter'), ('bandit', 'bandit')]
sel = sys.argv[1:] or [p[0] for p in pairs]
pairs = [p for p in pairs if p[0] in sel]
out = Image.new('RGBA', (560, 280 * len(pairs)), (255, 255, 255, 255))
for i, (mn, rn) in enumerate(pairs):
    ref = Image.open(S + 'refimg/' + rn + '.png').convert('RGBA'); ref.thumbnail((230, 276))
    out.paste(ref, (0, i * 280), ref)
    d = json.load(open(S + 'work/newmodels2/clash_' + mn + '.bbmodel'))
    out.paste(render(d, 276, cam=(0.35, 0.2, -1.0), tint=(60, 110, 255), pose=sample(d, 'idle', 0)), (240, i * 280))
out.save(S + 'm1_cmp.png')
