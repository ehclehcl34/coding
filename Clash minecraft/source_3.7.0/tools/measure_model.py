"""bbmodel 기본 자세 크기 (블록): X폭, Z깊이, 높이. 본/큐브 회전 반영."""
import json, sys, math
import numpy as np
def rot(r):
    rx, ry, rz = map(math.radians, r)
    X = np.array([[1,0,0],[0,math.cos(rx),-math.sin(rx)],[0,math.sin(rx),math.cos(rx)]])
    Y = np.array([[math.cos(ry),0,math.sin(ry)],[0,1,0],[-math.sin(ry),0,math.cos(ry)]])
    Z = np.array([[math.cos(rz),-math.sin(rz),0],[math.sin(rz),math.cos(rz),0],[0,0,1]])
    return Z@Y@X
SKIP = ('hitbox', 'fx', 'projectile', 'muzzle')
def measure(d, skip_words=()):
    els = {e['uuid']: e for e in d['elements']}
    pts = []
    def walk(n, chain):
        if isinstance(n, str):
            e = els.get(n)
            if not e or e.get('visibility', True) is False: return
            f, t = e['from'], e['to']
            c = [[x, y, z] for x in (f[0], t[0]) for y in (f[1], t[1]) for z in (f[2], t[2])]
            P = np.array(c, float)
            o = np.array(e.get('origin', [0,0,0]), float)
            P = (P - o) @ rot(e.get('rotation', [0,0,0])).T + o
            for (bo, br) in chain:
                bo = np.array(bo, float); P = (P - bo) @ rot(br).T + bo
            pts.append(P); return
        nm = (n.get('name') or '').lower()
        if any(w in nm for w in SKIP + tuple(skip_words)) or n.get('visibility', True) is False: return
        for c in n.get('children', []): walk(c, [(n.get('origin',[0,0,0]), n.get('rotation',[0,0,0]))] + chain)
    for n in d['outliner']: walk(n, [])
    if not pts: return (0,0,0,0,0)
    P = np.vstack(pts)
    mn, mx = P.min(0), P.max(0)
    return (mx[0]-mn[0])/16, (mx[2]-mn[2])/16, (mx[1]-mn[1])/16, max(abs(mn[0]),abs(mx[0]))/16*2, max(abs(mn[2]),abs(mx[2]))/16*2
if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = json.load(open(p))
        w, dep, h, wc, dc = measure(d)
        print('%-34s X %5.2f  Z %5.2f  H %5.2f' % (p.split('/')[-1][:-8], w, dep, h))
