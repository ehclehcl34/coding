import sys, json, numpy as np; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad'); sys.path.insert(0, 'pkg340/ClashMC_v3.4.0/source/model_tools')
from animlib import *
import bbrender; from PIL import Image
from scipy.optimize import minimize
R = lambda v: bbrender.rot_matrix(-v[0], -v[1], v[2])
d0, n0 = load('newmodels3/clash_royal_giant.bbmodel')
def org(name):
    def w(t):
        for c in t:
            if isinstance(c, dict):
                if c['name'] == name: return c['origin']
                r = w(c['children'])
                if r: return r
    return np.array(w(d0['outliner']), float)
OA, OC = org('arm_r'), org('cannon')
def solve(a, T):
    Ra = R(a)
    c = minimize(lambda v: np.sum((Ra @ R(v) - np.eye(3)) ** 2), -np.array(a, float)).x
    p = Ra.T @ (np.array(T) - OA) - (OC - OA)
    return [round(x, 2) for x in c], [round(x, 2) for x in p]
if __name__ == '__main__':
    out = sys.argv[1]; ims = []
    print('OA', OA, 'OC', OC)
    for s in sys.argv[2:]:
        a, T = json.loads(s)
        c, p = solve(a, T); print(a, T, '->', c, p)
        d, n = load('newmodels3/clash_royal_giant.bbmodel')
        setk(d, n, 'idle', 'arm_r', 'rotation', [(0, a), (2.4, a)]); setk(d, n, 'idle', 'cannon', 'rotation', [(0, c), (2.4, c)]); setk(d, n, 'idle', 'cannon', 'position', [(0, p), (2.4, p)])
        P = bbrender.sample(d, 'idle', 0)
        for cam in ((1, 0.15, 0), (0.4, 0.15, -1)):
            ims.append(bbrender.render(d, 300, cam=cam, tint=(60, 100, 240), pose=P))
    im = Image.new('RGBA', (300 * len(ims), 300), 'white'); [im.paste(x, (i * 300, 0)) for i, x in enumerate(ims)]; im.save(out)
