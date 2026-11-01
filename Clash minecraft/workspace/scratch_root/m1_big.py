import json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work/pkg340/ClashMC_v3.4.0/source/model_tools')
from bbrender import render, sample
from PIL import Image
S = '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/'
ref = {'princess': 'princess', 'ice_wizard': 'ice-wizard', 'magic_archer': 'magic-archer', 'hunter': 'hunter', 'bandit': 'bandit'}
names = sys.argv[1:]
out = Image.new('RGBA', (700, 400 * len(names)), (255, 255, 255, 255))
for i, n in enumerate(names):
    r = Image.open(S + 'refimg/' + ref[n] + '.png').convert('RGBA'); r.thumbnail((290, 390)); out.paste(r, (0, i * 400), r)
    d = json.load(open(S + 'work/newmodels2/clash_' + n + '.bbmodel'))
    out.paste(render(d, 400, cam=(0.35, 0.2, -1.0), tint=(60, 110, 255), pose=sample(d, 'idle', 0)), (300, i * 400))
out.save(S + 'm1_big.png')
