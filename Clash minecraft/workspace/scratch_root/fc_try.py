import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad'); sys.path.insert(0, 'pkg340/ClashMC_v3.4.0/source/model_tools')
from animlib import *
import bbrender; from PIL import Image
ims = []
for s in sys.argv[2:]:
    a = json.loads(s)
    d, n = load('newmodels3/clash_firecracker.bbmodel')
    setk(d, n, 'idle', 'arm_r', 'rotation', [(0, a), (1.6, a)])
    P = bbrender.sample(d, 'idle', 0)
    for c in ((1, 0.15, 0), (0.4, 0.15, -1)):
        ims.append(bbrender.render(d, 300, cam=c, tint=(60, 100, 240), pose=P))
im = Image.new('RGBA', (300 * len(ims), 300), 'white'); [im.paste(x, (i * 300, 0)) for i, x in enumerate(ims)]; im.save(sys.argv[1])
