import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad'); sys.path.insert(0, 'pkg340/ClashMC_v3.4.0/source/model_tools')
from animlib import *
import bbrender; from PIL import Image
out = sys.argv[1]; sets = [tuple(json.loads(x)) for x in sys.argv[2:]]
ims = []
for (ar, cr, cp) in sets:
    d, n = load('newmodels3/clash_royal_giant.bbmodel')
    setk(d, n, 'idle', 'arm_r', 'rotation', [(0, ar), (2.4, ar)])
    setk(d, n, 'idle', 'cannon', 'rotation', [(0, cr), (2.4, cr)])
    setk(d, n, 'idle', 'cannon', 'position', [(0, cp), (2.4, cp)])
    P = bbrender.sample(d, 'idle', 0)
    for c in ((1, 0.15, 0), (0.5, 0.15, -1)):
        ims.append(bbrender.render(d, 300, cam=c, tint=(60, 100, 240), pose=P))
im = Image.new('RGBA', (300 * len(ims), 300), 'white'); [im.paste(a, (i * 300, 0)) for i, a in enumerate(ims)]; im.save(out)
