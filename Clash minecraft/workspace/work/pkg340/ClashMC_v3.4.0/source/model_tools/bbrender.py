"""Tiny orthographic software renderer for Blockbench .bbmodel files (preview + UI portraits)."""
import json, base64, io, math
import numpy as np
from PIL import Image


def load_tex(t):
    src = t.get('source', '')
    if not src.startswith('data:image'):
        return None
    im = Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))).convert('RGBA')
    w, h = im.size
    if h > w and h % w == 0:          # animated strip -> first frame
        im = im.crop((0, 0, w, w))
    return im


def rot_matrix(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    X = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Y = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Z = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Z @ Y @ X      # Blockbench (three.js 'ZYX' order)


FACE_CORNERS = {  # TL, TR, BL in terms of (from|to) per axis
    'north': ((1, 1, 0), (0, 1, 0), (1, 0, 0)),
    'south': ((0, 1, 1), (1, 1, 1), (0, 0, 1)),
    'east': ((1, 1, 1), (1, 1, 0), (1, 0, 1)),
    'west': ((0, 1, 0), (0, 1, 1), (0, 0, 0)),
    'up': ((0, 1, 0), (1, 1, 0), (0, 1, 1)),
    'down': ((0, 0, 1), (1, 0, 1), (0, 0, 0)),
}
NORMALS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'east': (1, 0, 0), 'west': (-1, 0, 0), 'up': (0, 1, 0), 'down': (0, -1, 0)}


def element_parents(doc):
    """uuid -> list of bones (innermost first) as (origin, rotation, name)"""
    out = {}

    def walk(node, chain):
        if isinstance(node, str):
            out[node] = chain
            return
        b = (node.get('origin', [0, 0, 0]), node.get('rotation', [0, 0, 0]), node.get('name'), node.get('visibility', True), node.get('uuid'))
        for c in node.get('children', []):
            walk(c, [b] + chain)
    for n in doc['outliner']:
        walk(n, [])
    return out


def sample(doc, anim_name, t):
    """bone uuid -> (rot, pos, scale) at time t (linear)"""
    a = next(x for x in doc['animations'] if x['name'] == anim_name)
    out = {}
    for u, an in a['animators'].items():
        ch = {}
        for kf in an['keyframes']:
            dp = kf['data_points'][0]
            ch.setdefault(kf['channel'], []).append((kf['time'], [float(dp['x']), float(dp['y']), float(dp['z'])]))
        res = {}
        for c, pts in ch.items():
            pts.sort()
            if t <= pts[0][0]:
                v = pts[0][1]
            elif t >= pts[-1][0]:
                v = pts[-1][1]
            else:
                for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                    if t0 <= t <= t1:
                        f = (t - t0) / max(1e-9, t1 - t0)
                        v = [v0[i] + (v1[i] - v0[i]) * f for i in range(3)]
                        break
            res[c] = v
        out[u] = (res.get('rotation', [0, 0, 0]), res.get('position', [0, 0, 0]), res.get('scale', [1, 1, 1]))
    return out


def render(doc, size=400, cam=(0.6, 0.5, -1.0), bg=(232, 236, 241, 255), skip=('hitbox',), margin=0.06, hide_bones=(), tint=None, pose=None):
    texs = {}
    for i, t in enumerate(doc['textures']):
        im = load_tex(t)
        uvw = t.get('uv_width') or doc.get('resolution', {}).get('width', 16)
        uvh = t.get('uv_height') or doc.get('resolution', {}).get('height', 16)
        texs[str(t.get('id', i))] = (np.array(im).astype(float) if im is not None else None, uvw, uvh)
        texs[i] = texs[str(t.get('id', i))]
    parents = element_parents(doc)
    fwd = -np.array(cam, float); fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    light = np.array([0.4, 1.0, -0.6]); light /= np.linalg.norm(light)
    quads = []
    for e in doc['elements']:
        if e.get('name') in skip or e.get('visibility') is False:
            continue
        chain = parents.get(e['uuid'], [])
        if any(b[2] in skip or b[2] in hide_bones for b in chain):
            continue
        f, t = np.array(e['from'], float), np.array(e['to'], float)
        infl = e.get('inflate', 0)
        f, t = f - infl, t + infl
        er = e.get('rotation', [0, 0, 0])
        eo = np.array(e.get('origin', [0, 0, 0]), float)
        Re = rot_matrix(*er)

        def bone_rot(br, bu):
            br = list(br or [0, 0, 0])
            if pose and bu in pose:
                ar = pose[bu][0]
                br = [br[0] - ar[0], br[1] - ar[1], br[2] + ar[2]]   # Blockbench: x,y 반전
            return br

        def xf(p):
            p = Re @ (p - eo) + eo
            for (bo, br, _, _, bu) in chain:
                bo = np.array(bo, float)
                if pose and bu in pose:
                    p = (p - bo) * np.array(pose[bu][2]) + bo
                r = bone_rot(br, bu)
                if any(r):
                    p = rot_matrix(*r) @ (p - bo) + bo
                if pose and bu in pose:
                    ap = pose[bu][1]
                    p = p + np.array([-ap[0], ap[1], ap[2]])
            return p

        def xn(n):
            n = Re @ n
            for (_, br, _, _, bu) in chain:
                r = bone_rot(br, bu)
                if any(r):
                    n = rot_matrix(*r) @ n
            return n
        for face, spec in e.get('faces', {}).items():
            tex = spec.get('texture')
            if tex is None or tex is False:
                continue
            ti = texs.get(tex) if not isinstance(tex, int) else texs.get(tex)
            if ti is None or ti[0] is None:
                continue
            n = xn(np.array(NORMALS[face], float))
            if np.dot(n, fwd) >= 0:
                continue
            c = [np.array([(t if s else f)[k] for k, s in enumerate(sel)]) for sel in FACE_CORNERS[face]]
            TL, TR, BL = (xf(p) for p in c)
            tc = tint is not None and any('tc_' in (b[2] or '') for b in chain)
            if tint is not None and any('ts_' in (b[2] or '') for b in chain):
                tc = 2
            quads.append((TL, TR, BL, spec, ti, n, tc))
    if not quads:
        return Image.new('RGBA', (size, size), bg)
    pts = np.array([q[i] for q in quads for i in range(3)] + [q[1] + q[2] - q[0] for q in quads])
    sx, sy = pts @ right, pts @ up
    span = max(sx.max() - sx.min(), sy.max() - sy.min()) * (1 + 2 * margin)
    cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2
    scale = size / span
    img = np.zeros((size, size, 4)); img[:] = bg
    zb = np.full((size, size), np.inf)

    def proj(p):
        return np.array([(p @ right - cx) * scale + size / 2, size / 2 - (p @ up - cy) * scale, p @ fwd])
    for TL, TR, BL, spec, (tx, uvw, uvh), n, tc in quads:
        a, b, c = proj(TL), proj(TR), proj(BL)
        d = b + c - a
        xs = [a[0], b[0], c[0], d[0]]; ys = [a[1], b[1], c[1], d[1]]
        x0, x1 = int(max(0, math.floor(min(xs)))), int(min(size - 1, math.ceil(max(xs))))
        y0, y1 = int(max(0, math.floor(min(ys)))), int(min(size - 1, math.ceil(max(ys))))
        if x1 < x0 or y1 < y0:
            continue
        M = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
        if abs(np.linalg.det(M)) < 1e-9:
            continue
        Mi = np.linalg.inv(M)
        X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        dx, dy = X - a[0], Y - a[1]
        s = Mi[0, 0] * dx + Mi[0, 1] * dy
        tt = Mi[1, 0] * dx + Mi[1, 1] * dy
        inside = (s >= 0) & (s <= 1) & (tt >= 0) & (tt <= 1)
        if not inside.any():
            continue
        z = a[2] + s * (b[2] - a[2]) + tt * (c[2] - a[2])
        u0, v0, u1, v1 = spec.get('uv', [0, 0, uvw, uvh])
        rot = spec.get('rotation', 0) or 0
        ss, ts = s, tt
        for _ in range((rot // 90) % 4):
            ss, ts = ts, 1 - ss
        u = u0 + (u1 - u0) * ss
        v = v0 + (v1 - v0) * ts
        H, W = tx.shape[:2]
        px = np.clip((u / uvw * W).astype(int), 0, W - 1)
        py = np.clip((v / uvh * H).astype(int), 0, H - 1)
        col = tx[py, px]
        sh = 0.55 + 0.45 * max(0.0, float(np.dot(n, light)))
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        ok = inside & (col[..., 3] > 20) & (z < sub)
        sub[ok] = z[ok]
        tgt = img[y0:y1 + 1, x0:x1 + 1]
        rgb = col[..., :3] * sh
        if tc is True or tc == 1:
            rgb = rgb * np.array(tint, float) / 255.0
        if tc == 2:
            rgb = rgb * (np.array([78, 192, 200.]) if tint[2] > tint[0] else np.array([240, 96, 72.])) / 255.0
        tgt[ok, :3] = rgb[ok]
        tgt[ok, 3] = 255
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGBA')


if __name__ == '__main__':
    import sys
    d = json.load(open(sys.argv[1]))
    render(d, 500).save(sys.argv[2])
