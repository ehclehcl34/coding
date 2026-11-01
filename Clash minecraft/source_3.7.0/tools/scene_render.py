"""경기장 schem + bbmodel 들을 한 장면에 렌더 (공유 z-버퍼)."""
import json, math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'pkg340/ClashMC_v3.4.0/source/model_tools')
import bbrender as BR
import schem, schem_render as SR

def ry(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

class Scene:
    def __init__(self):
        self.quads = []   # (A, B, C, colfn/texinfo, spec, n, tint)
    def add_schem(self, path, origin=(0, 0, 0), skip_y_below=3):
        g = schem.load(path)['grid']; H, L, W = g.shape
        air = 'minecraft:air'
        solid = np.vectorize(lambda b: b != air and 'barrier' not in b and not any(t in b for t in SR.THIN))(g)
        cache = {}
        for y in range(skip_y_below, H):
            for z in range(L):
                for x in range(W):
                    b = g[y, z, x]
                    if b == air or 'barrier' in b: continue
                    thin = not solid[y, z, x]
                    hgt = 0.15 if thin else 1.0
                    if b not in cache:
                        c = np.array(SR.col(b) + (255,), float).reshape(1, 1, 4); cache[b] = (c, 1, 1)
                    tex = cache[b]
                    p = np.array([x, y, z], float) + origin
                    f, t = p, p + [1, hgt, 1]
                    for face, nb in (('up', (y + 1, z, x)), ('north', (y, z - 1, x)), ('south', (y, z + 1, x)), ('west', (y, z, x - 1)), ('east', (y, z, x + 1))):
                        yy, zz, xx = nb
                        if not thin and 0 <= yy < H and 0 <= zz < L and 0 <= xx < W and solid[yy, zz, xx]: continue
                        TLs, TRs, BLs = BR.FACE_CORNERS[face]
                        sel = lambda s_: np.array([(t if s_[k] else f)[k] for k in range(3)])
                        self.quads.append((sel(TLs), sel(TRs), sel(BLs), {'uv': [0, 0, 1, 1]}, tex, np.array(BR.NORMALS[face], float), None))
    def add_model(self, path, pos, yaw=0, tint=None, hide=('hitbox',)):
        doc = json.load(open(path)) if isinstance(path, str) else path
        texs = {}
        for i, t in enumerate(doc['textures']):
            im = BR.load_tex(t)
            uvw = t.get('uv_width') or doc.get('resolution', {}).get('width', 16)
            uvh = t.get('uv_height') or doc.get('resolution', {}).get('height', 16)
            texs[str(t.get('id', i))] = (np.array(im).astype(float) if im is not None else None, uvw, uvh); texs[i] = texs[str(t.get('id', i))]
        parents = BR.element_parents(doc)
        R = ry(yaw); P = np.array(pos, float)
        for e in doc['elements']:
            if e.get('visibility') is False: continue
            chain = parents.get(e['uuid'], [])
            if any((b[2] or '') in hide or b[3] is False for b in chain): continue
            f, t = np.array(e['from'], float) - e.get('inflate', 0), np.array(e['to'], float) + e.get('inflate', 0)
            Re = BR.rot_matrix(*e.get('rotation', [0, 0, 0])); eo = np.array(e.get('origin', [0, 0, 0]), float)
            def xf(p):
                p = Re @ (p - eo) + eo
                for (bo, br, _, _, _) in chain:
                    if any(br): bo = np.array(bo, float); p = BR.rot_matrix(*br) @ (p - bo) + bo
                return R @ (p / 16.0) + P
            def xn(n):
                n = Re @ n
                for (_, br, _, _, _) in chain:
                    if any(br): n = BR.rot_matrix(*br) @ n
                return R @ n
            tc = tint is not None and any('tc_' in (b[2] or '') for b in chain)
            for face, spec in e.get('faces', {}).items():
                tex = spec.get('texture')
                if tex is None or tex is False: continue
                ti = texs.get(tex)
                if ti is None or ti[0] is None: continue
                c = [np.array([(t if s else f)[k] for k, s in enumerate(sel)]) for sel in BR.FACE_CORNERS[face]]
                self.quads.append((xf(c[0]), xf(c[1]), xf(c[2]), spec, ti, xn(np.array(BR.NORMALS[face], float)), tint if tc else None))
    def render(self, size, cam, center, span, bg=(24, 26, 32)):
        W, H = size
        fwd = -np.array(cam, float); fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
        light = np.array([0.4, 1.0, -0.6]); light /= np.linalg.norm(light)
        C = np.array(center, float); scale = W / span
        img = np.zeros((H, W, 3)); img[:] = bg; zb = np.full((H, W), np.inf)
        def proj(p):
            d = p - C
            return np.array([d @ right * scale + W / 2, H / 2 - d @ up * scale, d @ fwd])
        for A, B, Cq, spec, (tx, uvw, uvh), n, tint in self.quads:
            if np.dot(n, fwd) >= 0: continue
            a, b, c = proj(A), proj(B), proj(Cq); d = b + c - a
            xs = [a[0], b[0], c[0], d[0]]; ys = [a[1], b[1], c[1], d[1]]
            x0, x1 = int(max(0, math.floor(min(xs)))), int(min(W - 1, math.ceil(max(xs))))
            y0, y1 = int(max(0, math.floor(min(ys)))), int(min(H - 1, math.ceil(max(ys))))
            if x1 < x0 or y1 < y0: continue
            M = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
            if abs(np.linalg.det(M)) < 1e-9: continue
            Mi = np.linalg.inv(M)
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            dx, dy = X - a[0], Y - a[1]
            s = Mi[0, 0] * dx + Mi[0, 1] * dy; tt = Mi[1, 0] * dx + Mi[1, 1] * dy
            inside = (s >= -0.01) & (s <= 1.01) & (tt >= -0.01) & (tt <= 1.01)
            if not inside.any(): continue
            z = a[2] + s * (b[2] - a[2]) + tt * (c[2] - a[2])
            u0, v0, u1, v1 = spec.get('uv', [0, 0, uvw, uvh])
            ss, ts = s, tt
            for _ in range(((spec.get('rotation', 0) or 0) // 90) % 4): ss, ts = ts, 1 - ss
            u = u0 + (u1 - u0) * np.clip(ss, 0, 1); v = v0 + (v1 - v0) * np.clip(ts, 0, 1)
            Ht, Wt = tx.shape[:2]
            px = np.clip((u / uvw * Wt).astype(int), 0, Wt - 1); py = np.clip((v / uvh * Ht).astype(int), 0, Ht - 1)
            col = tx[py, px]
            sh = 0.55 + 0.45 * max(0.0, float(np.dot(n, light)))
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            ok = inside & (col[..., 3] > 20) & (z < sub)
            sub[ok] = z[ok]
            rgb = col[..., :3] * sh
            if tint is not None: rgb = rgb * np.array(tint, float) / 255.0
            img[y0:y1 + 1, x0:x1 + 1][ok] = rgb[ok]
        return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def project(size, cam, center, span, p):
    W, H = size
    fwd = -np.array(cam, float); fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    d = np.array(p, float) - np.array(center, float); sc = W / span
    return (d @ right * sc + W / 2, H / 2 - d @ up * sc)
