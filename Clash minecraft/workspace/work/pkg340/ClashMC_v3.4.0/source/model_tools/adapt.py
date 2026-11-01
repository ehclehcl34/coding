"""Adapt the user's hand-made Blockbench models for ClashMC (BetterModel / ModelEngine).

Per model:
  * single texture atlas (first frame of animated textures), resolution = atlas size
  * transparent texture for the hitbox / untextured faces
  * unique, tag-safe bone names; cannon: barrel bone -> 'top', mount -> 'base' (plugin turret)
  * loose cubes wrapped in a bone, invalid cube rotations moved onto a bone
  * cubes that overflow +-48 of their bone pivot moved to child bones (ModelEngine-safe)
  * optional uniform scale, team recolor (blue <-> red), skin theme recolor
"""
import json, base64, io, copy, math, colorsys, re, uuid as _uuid
import numpy as np
from PIL import Image

from bbrender import load_tex

LIMIT = 48


def uid():
    return str(_uuid.uuid4())


# ------------------------------------------------------------------ colours
def _hsv(arr):
    a = arr[..., :3] / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = d > 1e-6
    rm = m & (mx == r); gm = m & (mx == g) & ~rm; bm = m & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    h = h * 60
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def _from_hsv(h, s, v):
    h = (h % 360) / 60
    c = v * s
    x = c * (1 - np.abs(h % 2 - 1))
    z = np.zeros_like(h)
    i = np.floor(h).astype(int) % 6
    r = np.choose(i, [c, x, z, z, x, c]); g = np.choose(i, [x, c, c, x, z, z]); b = np.choose(i, [z, z, x, c, c, x])
    m = v - c
    return np.stack([r + m, g + m, b + m], -1) * 255


def team_mask(arr, team):
    h, s, v = _hsv(arr)
    if team == 'blue':
        hue = (h > 195) & (h < 265)
    else:
        hue = (h > 338) | (h < 12)
    return hue & (s > 0.35) & (v > 0.12) & (arr[..., 3] > 0)


def swap_team(img, src, dst):
    """recolour team-coloured pixels from src team to dst team (keeps shading)"""
    a = np.array(img.convert('RGBA')).astype(float)
    m = team_mask(a, src)
    h, s, v = _hsv(a)
    nh = np.where(m, 228.0 if dst == 'blue' else 358.0, h)
    rgb = _from_hsv(nh, s, v)
    if dst == 'red':     # blue team textures are a bit darker; lift a little
        rgb = np.where(m[..., None], np.clip(rgb * 1.08, 0, 255), rgb)
    a[..., :3] = np.where(m[..., None], rgb, a[..., :3])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


THEMES = {
    'frost': dict(tint=(0.80, 0.93, 1.10), add=(28, 42, 58), mix=0.65),
    'royal': dict(tint=(1.10, 0.95, 0.70), add=(30, 22, 0), mix=0.55),
    'shadow': dict(tint=(0.62, 0.52, 0.85), add=(10, 0, 22), mix=0.70, dark=0.55),
    'infernal': dict(tint=(1.05, 0.55, 0.42), add=(20, 0, 0), mix=0.70, dark=0.6),
}


def theme(img, name, keep_team=None, strength=1.0):
    t = THEMES[name]
    a = np.array(img.convert('RGBA')).astype(float)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114])
    lum = lum * t.get('dark', 1.0)
    target = lum[..., None] * np.array(t['tint']) + np.array(t['add'])
    mix = t['mix'] * strength
    out = a[..., :3] * (1 - mix) + target * mix
    if keep_team:
        m = team_mask(a, keep_team)
        out = np.where(m[..., None], a[..., :3], out)
    a[..., :3] = np.clip(out, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


# ------------------------------------------------------------------ atlas
def build_atlas(doc, tex_fn=None):
    imgs = []
    for i, t in enumerate(doc['textures']):
        im = load_tex(t)
        if im is None:
            im = Image.new('RGBA', (16, 16), (255, 0, 255, 255))
        if tex_fn:
            im = tex_fn(t['name'], im)
        uvw = t.get('uv_width') or doc.get('resolution', {}).get('width', 16)
        uvh = t.get('uv_height') or doc.get('resolution', {}).get('height', 16)
        imgs.append((i, im, uvw, uvh))
    clear = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
    items = imgs + [('clear', clear, 4, 4)]
    total = sum(im.size[0] * im.size[1] for _, im, _, _ in items)
    S = 16
    while True:
        if S * S >= total and S >= max(im.size[0] for _, im, _, _ in items):
            pos, x, y, row, ok = {}, 0, 0, 0, True
            for key, im, _, _ in sorted(items, key=lambda it: -it[1].size[1]):
                w, h = im.size
                if x + w > S:
                    x, y, row = 0, y + row, 0
                if y + h > S:
                    ok = False
                    break
                pos[key] = (x, y)
                x += w
                row = max(row, h)
            if ok:
                break
        S *= 2
    atlas = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    info = {}
    for key, im, uvw, uvh in items:
        atlas.paste(im, pos[key])
        info[key] = (pos[key], im.size, uvw, uvh)
    return atlas, S, info


def png_b64(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


# ------------------------------------------------------------------ main
VALID_ROT = {-45, -22.5, 0, 22.5, 45}


def adapt(src_path, name, scale=1.0, tex_fn=None, renames=None, prefix_children=None, extra=None, pre=None):
    doc = json.load(open(src_path, encoding='utf-8'))
    doc = copy.deepcopy(doc)
    if pre:
        pre(doc)
    els = {e['uuid']: e for e in doc['elements']}
    renames = renames or {}
    prefix_children = prefix_children or {}

    # --- scale
    if scale != 1.0:
        for e in doc['elements']:
            for k in ('from', 'to', 'origin'):
                if k in e:
                    e[k] = [v * scale for v in e[k]]
            if e.get('inflate'):
                e['inflate'] *= scale

        def sc(n):
            if isinstance(n, str):
                return
            n['origin'] = [v * scale for v in n.get('origin', [0, 0, 0])]
            for c in n.get('children', []):
                sc(c)
        for n in doc['outliner']:
            sc(n)
        for a in doc.get('animations', []):
            for an in a.get('animators', {}).values():
                for kf in an.get('keyframes', []):
                    if kf.get('channel') == 'position':
                        for dp in kf.get('data_points', []):
                            for ax in 'xyz':
                                try:
                                    dp[ax] = str(float(dp[ax]) * scale)
                                except (ValueError, KeyError):
                                    pass

    # --- atlas + uv remap
    atlas, S, info = build_atlas(doc, tex_fn)
    hit_uuids = set()

    def collect_hit(n, inside=False):
        if isinstance(n, str):
            if inside:
                hit_uuids.add(n)
            return
        ins = inside or n.get('name') == 'hitbox'
        for c in n.get('children', []):
            collect_hit(c, ins)
    for n in doc['outliner']:
        collect_hit(n)
    (cx, cy), _, _, _ = info['clear']
    for e in doc['elements']:
        hit = e['uuid'] in hit_uuids or e.get('name') == 'hitbox'
        for face, f in list(e.get('faces', {}).items()):
            tex = f.get('texture')
            if hit or tex is None or tex is False or tex not in info:
                f['uv'] = [cx + 1, cy + 1, cx + 3, cy + 3]
                f['texture'] = 0
                f.pop('rotation', None) if hit else None
                continue
            (ox, oy), (w, h), uvw, uvh = info[tex]
            u0, v0, u1, v1 = f.get('uv', [0, 0, uvw, uvh])
            kx, ky = w / uvw, h / uvh
            f['uv'] = [ox + u0 * kx, oy + v0 * ky, ox + u1 * kx, oy + v1 * ky]
            f['texture'] = 0
    doc['textures'] = [{
        'path': '', 'name': name + '.png', 'folder': '', 'namespace': '', 'id': '0', 'width': S, 'height': S,
        'uv_width': S, 'uv_height': S, 'particle': False, 'use_as_default': False, 'layers_enabled': False,
        'sync_to_project': '', 'render_mode': 'default', 'render_sides': 'auto', 'frame_time': 1,
        'frame_order_type': 'loop', 'frame_order': '', 'frame_interpolate': False, 'visible': True,
        'internal': True, 'saved': True, 'uuid': uid(), 'relative_path': '', 'source': png_b64(atlas)}]
    doc['resolution'] = {'width': S, 'height': S}
    doc['meta']['box_uv'] = False
    for e in doc['elements']:
        e['box_uv'] = False

    # --- wrap loose top-level cubes
    loose = [n for n in doc['outliner'] if isinstance(n, str)]
    if loose:
        doc['outliner'] = [n for n in doc['outliner'] if not isinstance(n, str)]
        doc['outliner'].insert(0, {'name': 'loose', 'origin': [0, 0, 0], 'rotation': [0, 0, 0], 'uuid': uid(),
                                   'export': True, 'isOpen': True, 'visibility': True, 'children': loose})

    # --- names
    used = set()

    def clean(nm):
        nm = re.sub(r'[^a-z0-9_]', '_', (nm or '').lower()).strip('_') or 'part'
        if nm[0].isdigit() or len(nm.split('_')[0]) <= 2:
            nm = 'g' + nm if nm[0].isdigit() else 'x' + nm
        base, k = nm, 1
        while nm in used:
            k += 1
            nm = '%s%d' % (base, k)
        used.add(nm)
        return nm

    def name_walk(n, pref=None):
        if isinstance(n, str):
            return
        raw = n.get('name', '')
        if raw == 'hitbox':
            n['name'] = 'hitbox'; used.add('hitbox')
        elif raw in renames:
            n['name'] = clean(renames[raw])
        elif pref:
            n['name'] = clean(pref + '_' + raw)
        else:
            n['name'] = clean(raw)
        child_pref = prefix_children.get(raw) and n['name'] or pref
        for c in n.get('children', []):
            name_walk(c, child_pref)
    for n in doc['outliner']:
        name_walk(n)

    # --- invalid cube rotations -> bone ; overflow -> child bones
    counter = [0]

    def fix(n):
        if isinstance(n, str):
            return n
        o = n.get('origin', [0, 0, 0])
        kids = []
        for c in n.get('children', []):
            if not isinstance(c, str):
                kids.append(fix(c))
                continue
            e = els[c]
            r = e.get('rotation', [0, 0, 0])
            nz = [v for v in r if abs(v) > 1e-6]
            node = c
            if len(nz) > 1 or (nz and min(VALID_ROT, key=lambda q: abs(q - nz[0])) != nz[0]):
                counter[0] += 1
                node = {'name': '%s_r%d' % (n['name'], counter[0]), 'origin': list(e.get('origin', [0, 0, 0])),
                        'rotation': list(r), 'uuid': uid(), 'export': True, 'isOpen': False, 'visibility': True, 'children': [c]}
                used.add(node['name'])
                e['rotation'] = [0, 0, 0]
                kids.append(fix(node))
                continue
            span = max(abs(e['to'][i] - e['from'][i]) for i in range(3))
            assert span <= 2 * LIMIT + 1e-6, (n['name'], e.get('name'), 'cube too large', span)
            over = any(max(abs(e['from'][i] - o[i]), abs(e['to'][i] - o[i])) > LIMIT for i in range(3))
            if over and n['name'] != 'hitbox':
                # 이미 만든 보조 본 중에 들어가는 게 있으면 같이 씀 (본 수 줄이기)
                host = None
                for k in kids:
                    if isinstance(k, dict) and k.get('_aux'):
                        ko = k['origin']
                        if all(max(abs(e['from'][i] - ko[i]), abs(e['to'][i] - ko[i])) <= LIMIT for i in range(3)):
                            host = k
                            break
                if host is not None:
                    host['children'].append(c)
                    continue
                counter[0] += 1
                ctr = [(e['from'][i] + e['to'][i]) / 2 for i in range(3)]
                # 피벗을 부모 쪽으로 최대한 당겨서 다음 큐브도 들어가게
                piv = []
                for i in range(3):
                    lo, hi = e['to'][i] - LIMIT, e['from'][i] + LIMIT
                    piv.append(min(max(o[i], lo), hi))
                node = {'name': '%s_p%d' % (n['name'], counter[0]), 'origin': piv, 'rotation': [0, 0, 0], 'uuid': uid(),
                        'export': True, 'isOpen': False, 'visibility': True, 'children': [c], '_aux': True}
                used.add(node['name'])
            kids.append(node)
        n['children'] = kids
        return n
    doc['outliner'] = [fix(n) for n in doc['outliner']]

    def strip(n):
        if isinstance(n, str):
            return
        n.pop('_aux', None)
        for c in n.get('children', []):
            strip(c)
    for n in doc['outliner']:
        strip(n)

    # --- tidy pivots of unrotated cubes
    for e in doc['elements']:
        if not any(abs(v) > 1e-6 for v in e.get('rotation', [0, 0, 0])):
            e['origin'] = [(e['from'][i] + e['to'][i]) / 2 for i in range(3)]
            e['rotation'] = [0, 0, 0]

    # --- animations: no auto 'spawn'
    for a in doc.get('animations', []):
        if a['name'] == 'spawn':
            a['name'] = 'deploy'
    if extra:
        extra(doc)
    # animator 이름을 최종 본 이름과 맞춤
    names = {}

    def nm(n):
        if isinstance(n, str):
            return
        names[n['uuid']] = n['name']
        for c in n.get('children', []):
            nm(c)
    for n in doc['outliner']:
        nm(n)
    for a in doc.get('animations', []):
        a['animators'] = {k: dict(v, name=names.get(k, v.get('name'))) for k, v in a.get('animators', {}).items() if k in names}
    doc['name'] = name
    doc['model_identifier'] = name
    return doc, atlas


def bones(doc):
    out = []

    def w(n):
        if isinstance(n, str):
            return
        out.append(n['name'])
        for c in n.get('children', []):
            w(c)
    for n in doc['outliner']:
        w(n)
    return out


def check(doc):
    """every cube within +-48 of its bone pivot"""
    els = {e['uuid']: e for e in doc['elements']}
    bad = []

    def w(n):
        if isinstance(n, str):
            return
        o = n.get('origin', [0, 0, 0])
        for c in n.get('children', []):
            if isinstance(c, str):
                e = els[c]
                if n['name'] != 'hitbox' and any(max(abs(e['from'][i] - o[i]), abs(e['to'][i] - o[i])) > LIMIT + 1e-6 for i in range(3)):
                    bad.append((n['name'], e.get('name')))
            else:
                w(c)
    for n in doc['outliner']:
        w(n)
    return bad


# ------------------------------------------------------------------ one model for both teams
TINT = {'blue': (60, 90, 255), 'red': (230, 50, 50)}   # TeamColor 색 (플러그인이 tc_ 본에 곱해서 칠함)


def teamify(doc, team):
    """team-coloured cubes -> '<bone>_tc_' child bones with a neutral (grey) texture; the plugin tints them per team.
    Cubes that mix team and plain pixels are split into two overlapping copies (each with the other part transparent)."""
    t = doc['textures'][0]
    src = Image.open(io.BytesIO(base64.b64decode(t['source'].split(',', 1)[1]))).convert('RGBA')
    S = src.size[0]
    a = np.array(src).astype(float)
    mask = team_mask(a, team)
    # grow atlas downward for split copies
    CAP = S * 8
    big = np.zeros((CAP, S, 4)); big[:S] = a
    bmask = np.zeros((CAP, S), bool); bmask[:S] = mask
    done = {}
    cursor = [0, S, 0]          # x, y, row height (shelf in the new half)
    els = {e['uuid']: e for e in doc['elements']}

    def region(f):
        u0, v0, u1, v1 = f['uv']
        x0, x1 = sorted((u0, u1)); y0, y1 = sorted((v0, v1))
        x0, y0 = int(math.floor(x0 + 1e-6)), int(math.floor(y0 + 1e-6))
        x1, y1 = max(int(math.ceil(x1 - 1e-6)), x0 + 1), max(int(math.ceil(y1 - 1e-6)), y0 + 1)
        return x0, y0, x1, y1

    def ratio(e):
        tot = tm = 0
        for f in e['faces'].values():
            x0, y0, x1, y1 = region(f)
            al = a[y0:y1, x0:x1, 3] > 0
            tot += al.sum(); tm += (mask[y0:y1, x0:x1] & al).sum()
        return None if tot == 0 else tm / tot

    def copy_region(f, keep_team):
        x0, y0, x1, y1 = region(f)
        w, h = x1 - x0, y1 - y0
        key = (x0, y0, x1, y1, keep_team)
        if key in done:
            nx, ny = done[key]
            u0, v0, u1, v1 = f['uv']
            f['uv'] = [u0 - x0 + nx, v0 - y0 + ny, u1 - x0 + nx, v1 - y0 + ny]
            return
        if cursor[0] + w > S:
            cursor[0], cursor[1], cursor[2] = 0, cursor[1] + cursor[2], 0
        nx, ny = cursor[0], cursor[1]
        assert ny + h <= CAP, 'atlas full'
        done[key] = (nx, ny)
        blk = big[y0:y1, x0:x1].copy(); mk = bmask[y0:y1, x0:x1].copy()
        drop = ~mk if keep_team else mk
        blk[drop] = 0
        big[ny:ny + h, nx:nx + w] = blk
        bmask[ny:ny + h, nx:nx + w] = mk & keep_team
        cursor[0] += w; cursor[2] = max(cursor[2], h)
        u0, v0, u1, v1 = f['uv']
        f['uv'] = [u0 - x0 + nx, v0 - y0 + ny, u1 - x0 + nx, v1 - y0 + ny]

    moved = 0

    def walk(n):
        nonlocal moved
        if isinstance(n, str) or n.get('name') == 'hitbox':
            return
        team_kids, keep = [], []
        for c in n.get('children', []):
            if not isinstance(c, str):
                walk(c); keep.append(c); continue
            e = els[c]
            r = ratio(e)
            if r is None or r < 0.03:
                keep.append(c)
            elif r > 0.97:
                team_kids.append(c)
            else:                                   # split
                dup = copy.deepcopy(e); dup['uuid'] = uid(); dup['inflate'] = e.get('inflate', 0) + 0.01
                for f in e['faces'].values():
                    copy_region(f, False)
                for f in dup['faces'].values():
                    copy_region(f, True)
                doc['elements'].append(dup); els[dup['uuid']] = dup
                keep.append(c); team_kids.append(dup['uuid'])
        if team_kids:
            moved += len(team_kids)
            keep.append({'name': n['name'] + '_tc_', 'origin': list(n.get('origin', [0, 0, 0])), 'rotation': [0, 0, 0],
                         'uuid': uid(), 'export': True, 'isOpen': False, 'visibility': True, 'children': team_kids})
        n['children'] = keep
    for n in doc['outliner']:
        walk(n)
    # team pixels -> grey so that  grey * tint ~= original colour
    tint = np.array(TINT[team], float)
    k = int(np.argmax(tint))
    g = np.clip(big[..., k] * 255.0 / tint[k], 0, 255)
    for ch in range(3):
        big[..., ch] = np.where(bmask, g, big[..., ch])
    used_h = cursor[1] + cursor[2]
    H = S
    while H < used_h:
        H *= 2
    side = max(S, H)
    out = np.zeros((side, side, 4)); out[:min(H, CAP), :S] = big[:min(H, CAP)]
    img = Image.fromarray(out.astype(np.uint8), 'RGBA')
    t['source'] = png_b64(img); t['width'] = t['height'] = t['uv_width'] = t['uv_height'] = side
    doc['resolution'] = {'width': side, 'height': side}
    return moved
