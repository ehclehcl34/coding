"""Pre-processing of the user's models before adapt(): restructure bones, fix pivots, polish, new animations.
All coordinates here are in the SOURCE model units (adapt() scales afterwards, including position keyframes)."""
import copy, uuid as _uuid, io, base64
import numpy as np
from PIL import Image, ImageDraw


def uid():
    return str(_uuid.uuid4())


# ------------------------------------------------------------------ tree helpers
def nodes(doc):
    out = []

    def w(n, parent):
        if isinstance(n, str):
            return
        out.append((n, parent))
        for c in n.get('children', []):
            w(c, n)
    for n in doc['outliner']:
        w(n, None)
    return out


def find(doc, name):
    for n, _ in nodes(doc):
        if n.get('name') == name:
            return n
    raise KeyError(name)


def parent_of(doc, target):
    """parent node (None = top level) of a node or a cube uuid"""
    for n, p in nodes(doc):
        if n is target:
            return p
        if isinstance(target, str) and target in n.get('children', []):
            return n
    if isinstance(target, str) and target in doc['outliner']:
        return None
    return None


def detach(doc, target):
    p = parent_of(doc, target)
    lst = doc['outliner'] if p is None else p['children']
    for i, c in enumerate(lst):
        if c is target or (isinstance(target, str) and c == target):
            del lst[i]
            return target
    raise KeyError('not attached')


def bone(name, origin, children=None, rotation=None):
    return {'name': name, 'origin': list(origin), 'rotation': list(rotation or [0, 0, 0]), 'uuid': uid(), 'export': True,
            'isOpen': False, 'visibility': True, 'color': 0, 'children': children or []}


def own_cubes(n):
    return [c for c in n.get('children', []) if isinstance(c, str)]


def all_cubes(n):
    out = []
    for c in n.get('children', []):
        out += [c] if isinstance(c, str) else all_cubes(c)
    return out


def extent(doc, n):
    els = {e['uuid']: e for e in doc['elements']}
    cs = [els[u] for u in all_cubes(n)]
    lo = np.min([e['from'] for e in cs], 0)
    hi = np.max([e['to'] for e in cs], 0)
    return lo, hi


def transform_node(doc, n, fn):
    """apply point transform fn to every cube corner/origin and nested bone origins under n"""
    els = {e['uuid']: e for e in doc['elements']}

    def w(x):
        if isinstance(x, str):
            e = els[x]
            a, b = np.array(fn(e['from'])), np.array(fn(e['to']))
            e['from'], e['to'] = list(np.minimum(a, b)), list(np.maximum(a, b))
            if 'origin' in e:
                e['origin'] = list(fn(e['origin']))
            return
        x['origin'] = list(fn(x.get('origin', [0, 0, 0])))
        for c in x.get('children', []):
            w(c)
    for c in n.get('children', []):
        w(c)


def scale_about(doc, n, k, center, inner=True):
    c = np.array(center, float)
    transform_node(doc, n, lambda p: list(c + (np.array(p, float) - c) * k))


def move(doc, n, d):
    transform_node(doc, n, lambda p: list(np.array(p, float) + np.array(d, float)))
    n['origin'] = list(np.array(n.get('origin', [0, 0, 0]), float) + np.array(d, float))


def add_texture(doc, img, name):
    b = io.BytesIO(); img.save(b, 'PNG')
    doc['textures'].append({'path': '', 'name': name, 'folder': '', 'namespace': '', 'id': str(len(doc['textures']) + 50),
                            'width': img.size[0], 'height': img.size[1], 'uv_width': 16, 'uv_height': 16,
                            'source': 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), 'uuid': uid()})
    return len(doc['textures']) - 1


def add_cube(doc, parent, frm, to, tex, uv=(0, 0, 16, 16), name='cube'):
    faces = {f: {'uv': list(uv), 'texture': tex} for f in ('north', 'east', 'south', 'west', 'up', 'down')}
    e = {'name': name, 'box_uv': False, 'rescale': False, 'locked': False, 'from': list(frm), 'to': list(to), 'autouv': 0,
         'color': 0, 'origin': [(frm[i] + to[i]) / 2 for i in range(3)], 'rotation': [0, 0, 0], 'faces': faces,
         'type': 'cube', 'uuid': uid()}
    doc['elements'].append(e)
    parent['children'].append(e['uuid'])
    return e


# ------------------------------------------------------------------ animations
def set_anims(doc, anims):
    """anims: {name: (length, loop, {bone_name: {channel: [(t, (x,y,z)), ...]}})}"""
    by = {n['name']: n for n, _ in nodes(doc)}
    out = []
    for name, (length, loop, tracks) in anims.items():
        animators = {}
        for bn, chans in tracks.items():
            b = by[bn]
            kfs = []
            for ch, pts in chans.items():
                for t, v in pts:
                    kfs.append({'channel': ch, 'data_points': [{'x': '%g' % v[0], 'y': '%g' % v[1], 'z': '%g' % v[2]}],
                                'uuid': uid(), 'time': round(t, 4), 'color': -1, 'interpolation': 'catmullrom'
                                if loop == 'loop' else 'linear'})
            animators[b['uuid']] = {'name': bn, 'type': 'bone', 'keyframes': kfs}
        out.append({'uuid': uid(), 'name': name, 'loop': loop, 'override': False, 'length': length, 'snapping': 20,
                    'selected': False, 'anim_time_update': '', 'blend_weight': '', 'start_delay': '', 'loop_delay': '',
                    'animators': animators})
    doc['animations'] = out


def cyc(length, *vals):
    """evenly spaced keyframes over one loop (last = first)"""
    n = len(vals)
    pts = [(length * i / n, v) for i, v in enumerate(vals)]
    pts.append((length, vals[0]))
    return pts


def common(root, sink=14, drop=12):
    return {
        'deploy': (0.7, 'once', {root: {'position': [(0, (0, drop, 0)), (0.3, (0, 0, 0)), (0.7, (0, 0, 0))],
                                        'scale': [(0, (0.9, 1.1, 0.9)), (0.3, (1.15, 0.82, 1.15)), (0.5, (0.96, 1.04, 0.96)), (0.7, (1, 1, 1))]}}),
        'death': (1.0, 'hold', {root: {'position': [(0, (0, 0, 0)), (1.0, (0, -sink, 0))],
                                       'rotation': [(0, (0, 0, 0)), (1.0, (0, 0, 14))],
                                       'scale': [(0, (1, 1, 1)), (1.0, (0.8, 0.55, 0.8))]}}),
    }


# ------------------------------------------------------------------ GIANT
def prep_giant(doc):
    head, hw, body = find(doc, 'head'), find(doc, 'headwear'), find(doc, 'body')
    detach(doc, hw); head['children'].append(hw)
    head['origin'] = [0, 46, 0]
    for nm, x in (('right_leg', 4.5), ('left_leg', -4.5)):
        find(doc, nm)['origin'] = [x, 25, 0]
    for nm, x in (('right_arm', 14), ('left_arm', -14)):
        a = find(doc, nm); a['origin'] = [x, 44.5, 0]
        detach(doc, a); body['children'].append(a)
    detach(doc, head); body['children'].append(head)
    body['origin'] = [0, 25, 0]
    find(doc, 'all')['origin'] = [0, 0, 0]
    W = 1.4
    q = W / 4
    anims = {
        'idle': (2.4, 'loop', {
            'body': {'position': cyc(2.4, (0, 0, 0), (0, -0.6, 0)), 'rotation': cyc(2.4, (0, 0, 0), (2, 0, 0))},
            'right_arm': {'rotation': cyc(2.4, (0, 0, 0), (-4, 0, 3))},
            'left_arm': {'rotation': cyc(2.4, (0, 0, 0), (-4, 0, -3))},
            'head': {'rotation': cyc(2.4, (0, 0, 0), (-3, 4, 0), (0, 0, 0), (-3, -4, 0))}}),
        'walk': (W, 'loop', {
            'right_leg': {'rotation': cyc(W, (0, 0, 0), (-26, 0, 0), (0, 0, 0), (26, 0, 0))},
            'left_leg': {'rotation': cyc(W, (0, 0, 0), (26, 0, 0), (0, 0, 0), (-26, 0, 0))},
            'right_arm': {'rotation': cyc(W, (0, 0, 0), (18, 0, 2), (0, 0, 0), (-18, 0, 2))},
            'left_arm': {'rotation': cyc(W, (0, 0, 0), (-18, 0, -2), (0, 0, 0), (18, 0, -2))},
            'body': {'position': cyc(W, (0, 0.8, 0), (0, -0.5, 0), (0, 0.8, 0), (0, -0.5, 0)),
                     'rotation': cyc(W, (2, 0, 0), (2, 3, -2.5), (2, 0, 0), (2, -3, 2.5))},
            'head': {'rotation': cyc(W, (0, 0, 0), (0, -2, 2), (0, 0, 0), (0, 2, -2))}}),
        'attack': (1.2, 'once', {
            'right_arm': {'rotation': [(0, (0, 0, 0)), (0.42, (-150, 0, 12)), (0.55, (-160, 0, 10)), (0.68, (-45, 0, -6)), (0.85, (-35, 0, -4)), (1.2, (0, 0, 0))]},
            'left_arm': {'rotation': [(0, (0, 0, 0)), (0.42, (15, 0, -6)), (0.68, (-20, 0, 0)), (1.2, (0, 0, 0))]},
            'body': {'rotation': [(0, (0, 0, 0)), (0.42, (-8, 18, 0)), (0.68, (14, -22, 0)), (0.9, (8, -10, 0)), (1.2, (0, 0, 0))],
                     'position': [(0, (0, 0, 0)), (0.42, (0, 0, 1.5)), (0.68, (0, -1.2, -2.5)), (1.2, (0, 0, 0))]},
            'head': {'rotation': [(0, (0, 0, 0)), (0.42, (-6, 0, 0)), (0.68, (10, 0, 0)), (1.2, (0, 0, 0))]}}),
    }
    anims.update(common('all', sink=20, drop=16))
    set_anims(doc, anims)


# ------------------------------------------------------------------ HOG RIDER
def prep_hog(doc):
    root = find(doc, 'all')
    body, larm, rarm = find(doc, 'body'), find(doc, 'left_arm'), find(doc, 'right_arm')
    head, hw = find(doc, 'head'), find(doc, 'headwear')
    bone5 = find(doc, 'bone5')                       # pig body (top level)
    # --- pig
    pig = bone('pig', [0, 6, 0])
    pig_head = bone('pig_head', [0, 12, -7])
    for c in own_cubes(body):                         # the 'body' bone's own cube is the pig's head
        detach(doc, c); pig_head['children'].append(c)
    h2 = find(doc, 'head2'); detach(doc, h2); pig_head['children'].append(h2)
    detach(doc, bone5); pig['children'].append(bone5)
    pig['children'].append(pig_head)
    for nm in ('leg1', 'leg2', 'leg3', 'leg4'):
        l = find(doc, nm); detach(doc, l); pig['children'].append(l)
    # --- rider
    rider = bone('rider', [0, 16, 0])
    for nm in ('body_sub_0', 'left_leg', 'right_leg', 'bone6'):
        x = find(doc, nm); detach(doc, x); rider['children'].append(x)
    detach(doc, hw); head['children'].append(hw)
    detach(doc, head); rider['children'].append(head)
    for nm, new in (('bone3', 'arm_l'), ('bone2', 'arm_r')):
        x = find(doc, nm); detach(doc, x); x['name'] = new; rider['children'].append(x)
    for x in (body, larm, rarm):
        detach(doc, x)
    root['children'] += [pig, rider]
    root['origin'] = [0, 0, 0]
    W = 0.56
    anims = {
        'idle': (2.0, 'loop', {
            'pig': {'position': cyc(2.0, (0, 0, 0), (0, -0.3, 0))},
            'pig_head': {'rotation': cyc(2.0, (0, 0, 0), (5, 0, 0), (0, 0, 0), (2, 6, 0))},
            'rider': {'rotation': cyc(2.0, (0, 0, 0), (2, 5, 0), (0, 0, 0), (2, -5, 0))},
            'arm_r': {'rotation': cyc(2.0, (0, 0, 0), (-10, 0, 0))},
            'head': {'rotation': cyc(2.0, (0, 0, 0), (-3, -6, 0), (0, 0, 0), (-3, 6, 0))}}),
        'walk': (W, 'loop', {     # 질주
            'leg3': {'rotation': cyc(W, (38, 0, 0), (-38, 0, 0))},
            'leg4': {'rotation': cyc(W, (30, 0, 0), (-42, 0, 0))},
            'leg1': {'rotation': cyc(W, (-38, 0, 0), (38, 0, 0))},
            'leg2': {'rotation': cyc(W, (-30, 0, 0), (42, 0, 0))},
            'pig': {'position': cyc(W, (0, 0, 0), (0, 1.4, 0)), 'rotation': cyc(W, (4, 0, 0), (-4, 0, 0))},
            'pig_head': {'rotation': cyc(W, (-4, 0, 0), (6, 0, 0))},
            'rider': {'position': cyc(W, (0, 0.4, 0), (0, 2.2, 0)), 'rotation': cyc(W, (6, 0, 0), (12, 0, 0))},
            'arm_r': {'rotation': cyc(W, (-15, 0, 0), (-30, 0, 0))},
            'arm_l': {'rotation': cyc(W, (-5, 0, 0), (10, 0, 0))}}),
        'attack': (0.9, 'once', {
            'arm_r': {'rotation': [(0, (0, 0, 0)), (0.35, (-155, 0, 8)), (0.45, (-160, 0, 8)), (0.55, (-20, 0, -6)), (0.65, (-12, 0, -4)), (0.9, (0, 0, 0))]},
            'rider': {'rotation': [(0, (0, 0, 0)), (0.35, (-10, 12, 0)), (0.55, (14, -14, 0)), (0.9, (0, 0, 0))],
                      'position': [(0, (0, 0, 0)), (0.35, (0, 1.5, 0)), (0.55, (0, -0.8, -1.5)), (0.9, (0, 0, 0))]},
            'pig': {'position': [(0, (0, 0, 0)), (0.55, (0, -0.6, 0)), (0.9, (0, 0, 0))]},
            'pig_head': {'rotation': [(0, (0, 0, 0)), (0.5, (8, 0, 0)), (0.9, (0, 0, 0))]}}),
    }
    anims.update(common('all', sink=10, drop=12))
    set_anims(doc, anims)


# ------------------------------------------------------------------ GOBLIN (+ polish)
def prep_goblin(doc):
    head, body = find(doc, 'head'), find(doc, 'body')
    b5 = find(doc, 'bone5')
    for x in list(b5['children']):
        detach(doc, x); head['children'].append(x)
    detach(doc, b5)
    neck = [0, 17, 0]
    # 다듬기 1: 머리 크게 (고블린답게 큰 머리), 귀(bone4)는 조금 더 크게
    scale_about(doc, head, 1.3, neck)
    for c in own_cubes(head):
        pass
    ears = find(doc, 'bone4')
    lo, hi = extent(doc, ears)
    scale_about(doc, ears, 1.18, [(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
    # 다듬기 2: 팔을 몸통에서 살짝 떼고 조금 앞으로 (덩어리처럼 붙어 보이던 것)
    for nm, dx in (('left_arm', -0.7), ('right_arm', 0.7)):
        move(doc, find(doc, nm), [dx, 0, -0.4])
    # 다듬기 3: 다리 사이 간격
    for nm, dx in (('left_leg', -0.3), ('right_leg', 0.3)):
        move(doc, find(doc, nm), [dx, 0, 0])
    head['origin'] = neck
    dag = find(doc, 'bone')            # 왼손 단검
    dag['name'] = 'dagger'
    dag['origin'] = [-4.95, 10, -0.4]
    find(doc, 'left_arm')['origin'] = [-4.95, 16.5, -0.4]
    find(doc, 'right_arm')['origin'] = [4.95, 16.5, -0.4]
    find(doc, 'left_leg')['origin'] = [-2.0, 7.5, 0]
    find(doc, 'right_leg')['origin'] = [2.0, 7.5, 0]
    for nm in ('head', 'left_arm', 'right_arm'):
        x = find(doc, nm); detach(doc, x); body['children'].append(x)
    body['origin'] = [0, 8, 0]
    find(doc, 'all')['origin'] = [0, 0, 0]
    W = 0.44
    anims = {
        'idle': (1.2, 'loop', {
            'body': {'position': cyc(1.2, (0, 0, 0), (0, -0.4, 0)), 'rotation': cyc(1.2, (4, 0, 0), (6, 0, 0))},
            'head': {'rotation': cyc(1.2, (0, 0, -5), (-4, 6, 0), (0, 0, 5), (-4, -6, 0))},
            'left_arm': {'rotation': cyc(1.2, (-15, 0, -4), (-25, 0, -8))},
            'right_arm': {'rotation': cyc(1.2, (0, 0, 4), (-6, 0, 8))}}),
        'walk': (W, 'loop', {
            'right_leg': {'rotation': cyc(W, (0, 0, 0), (-38, 0, 0), (0, 0, 0), (38, 0, 0))},
            'left_leg': {'rotation': cyc(W, (0, 0, 0), (38, 0, 0), (0, 0, 0), (-38, 0, 0))},
            'right_arm': {'rotation': cyc(W, (0, 0, 6), (32, 0, 6), (0, 0, 6), (-32, 0, 6))},
            'left_arm': {'rotation': cyc(W, (-20, 0, -6), (-45, 0, -6), (-20, 0, -6), (5, 0, -6))},
            'body': {'position': cyc(W, (0, 0.9, 0), (0, 0, 0), (0, 0.9, 0), (0, 0, 0)),
                     'rotation': cyc(W, (10, 0, 0), (10, 5, -3), (10, 0, 0), (10, -5, 3))},
            'head': {'rotation': cyc(W, (-8, 0, 0), (-8, -4, 3), (-8, 0, 0), (-8, 4, -3))}}),
        'attack': (0.5, 'once', {   # 단검 찌르기
            'left_arm': {'rotation': [(0, (0, 0, 0)), (0.12, (25, 15, -10)), (0.22, (-100, -10, 0)), (0.3, (-95, -10, 0)), (0.5, (0, 0, 0))]},
            'dagger': {'rotation': [(0, (0, 0, 0)), (0.12, (0, 0, 0)), (0.22, (95, 0, 0)), (0.3, (90, 0, 0)), (0.5, (0, 0, 0))]},
            'right_arm': {'rotation': [(0, (0, 0, 0)), (0.12, (-20, 0, 10)), (0.22, (25, 0, 10)), (0.5, (0, 0, 0))]},
            'body': {'rotation': [(0, (0, 0, 0)), (0.12, (0, -18, 0)), (0.22, (12, 22, 0)), (0.5, (0, 0, 0))],
                     'position': [(0, (0, 0, 0)), (0.12, (0, 0, 1)), (0.22, (0, -0.3, -2.2)), (0.5, (0, 0, 0))]},
            'head': {'rotation': [(0, (0, 0, 0)), (0.22, (6, 0, 0)), (0.5, (0, 0, 0))]}}),
    }
    anims.update(common('all', sink=6, drop=8))
    set_anims(doc, anims)


# ------------------------------------------------------------------ TESLA (땅속에 숨어 뚜껑 닫기)
def lid_texture():
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # left 16px: iron plate with seams & rivets / right 16px: team stripe (red, recoloured per team in game)
    for y in range(32):
        for x in range(16):
            v = 92 + ((x * 7 + y * 13) % 11) - 5
            im.putpixel((x, y), (v, v + 3, v + 8, 255))
    d.rectangle([0, 0, 15, 0], fill=(60, 63, 70, 255)); d.rectangle([0, 31, 15, 31], fill=(52, 54, 60, 255))
    d.rectangle([0, 15, 15, 16], fill=(58, 61, 68, 255))
    for x, y in ((2, 3), (13, 3), (2, 28), (13, 28), (7, 9), (8, 22)):
        d.rectangle([x, y, x + 1, y + 1], fill=(150, 156, 166, 255))
    for y in range(32):
        for x in range(16, 32):
            v = 150 + ((x * 5 + y * 3) % 9) * 6
            im.putpixel((x, y), (v, 28, 28, 255))
    return im


def prep_tesla(doc):
    root = find(doc, 'all')
    lo, hi = extent(doc, root)
    H = hi[1]
    tex = add_texture(doc, lid_texture(), 'tesla_lid.png')
    R, T = 12.5, 2.0          # 뚜껑 반폭, 테두리 두께
    # 고정 테두리 (땅 위로 살짝)
    frame = bone('lid_frame', [0, 0, 0])
    for a, b in (((-R - T, 0, -R - T), (R + T, 1.0, -R)), ((-R - T, 0, R), (R + T, 1.0, R + T)),
                 ((-R - T, 0, -R), (-R, 1.0, R)), ((R, 0, -R), (R + T, 1.0, R))):
        add_cube(doc, frame, a, b, tex, uv=(0, 0, 8, 2))
    # 뚜껑 두 쪽: 기본 자세 = 열림 (바깥으로 밀려서 땅속에 숨음)
    OPEN = 13.0
    SINK = 2.6
    lids = []
    # 뚜껑은 Z 축으로 미끄러짐 (블록벤치 애니메이션은 X 위치 부호가 뒤집혀서 Z 사용)
    for nm, sz in (('lid_a', -1), ('lid_b', 1)):
        b = bone(nm, [0, 0.8, sz * R / 2])
        z0, z1 = (-R, 0) if sz < 0 else (0, R)
        add_cube(doc, b, [-R, 0.2 - SINK, z0 + sz * OPEN], [R, 1.6 - SINK, z1 + sz * OPEN], tex, uv=(0, 0, 8, 8))
        for x0 in (-R + 2, R - 4):   # 팀색 줄무늬
            add_cube(doc, b, [x0, 1.6 - SINK, z0 + sz * OPEN + 1.5], [x0 + 2, 1.9 - SINK, z1 + sz * OPEN - 1.5], tex, uv=(8, 0, 16, 16))
        lids.append(b)
    doc['outliner'] += [frame] + lids
    D = -40.0   # 0.15배로 줄여서 바닥 블록 한 칸 안에 쏙 들어가게

    def path(sz, closing):
        # 기본 자세(열림) 기준 오프셋: 닫힌 위치 = 안쪽으로 OPEN, 위로 SINK
        closed = (0, SINK, -sz * OPEN)
        up_open = (0, SINK, 0)
        if closing:
            return [(0, (0, 0, 0)), (0.2, (0, 0, 0)), (0.3, up_open), (0.5, closed)]
        return [(0, closed), (0.12, up_open), (0.2, (0, 0, 0)), (0.55, (0, 0, 0))]
    close_a, close_b, open_a, open_b = path(-1, True), path(1, True), path(-1, False), path(1, False)
    top = 'group7'
    set_anims(doc, {
        'retract': (0.5, 'hold', {
            'all': {'position': [(0, (0, 0, 0)), (0.08, (0, 2, 0)), (0.3, (0, D, 0)), (0.5, (0, D, 0))],
                    'scale': [(0, (1, 1, 1)), (0.3, (0.15, 0.15, 0.15)), (0.5, (0.15, 0.15, 0.15))]},
            'lid_a': {'position': close_a}, 'lid_b': {'position': close_b}}),
        'emerge': (0.55, 'hold', {
            'all': {'position': [(0, (0, D, 0)), (0.15, (0, D, 0)), (0.42, (0, 3, 0)), (0.55, (0, 0, 0))],
                    'scale': [(0, (0.15, 0.15, 0.15)), (0.15, (0.15, 0.15, 0.15)), (0.42, (1.05, 1.05, 1.05)), (0.55, (1, 1, 1))]},
            'lid_a': {'position': open_a}, 'lid_b': {'position': open_b}}),
        'attack': (0.35, 'once', {top: {'scale': [(0, (1, 1, 1)), (0.08, (1.18, 1.1, 1.18)), (0.35, (1, 1, 1))]}}),
        'death': (0.8, 'hold', {'all': {'position': [(0, (0, 0, 0)), (0.8, (0, -18, 0))],
                                        'scale': [(0, (1, 1, 1)), (0.8, (0.8, 0.5, 0.8))]}}),
    })


# ------------------------------------------------------------------ GOBLIN BARREL (고블린 3마리가 든 큰 통)
def goblin_mark():
    """하얀 고블린 얼굴 마크 (투명 배경 32x32): 뾰족 귀 + 둥근 머리 + 눈 구멍 + 이빨 웃음"""
    S = 4                                           # 4배로 그려서 축소 (가장자리 깔끔)
    im = Image.new('RGBA', (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = (246, 244, 236, 255)
    d.polygon([(3 * S, 9 * S), (11 * S, 13 * S), (10 * S, 19 * S)], fill=W)          # 왼쪽 귀
    d.polygon([(29 * S, 9 * S), (21 * S, 13 * S), (22 * S, 19 * S)], fill=W)        # 오른쪽 귀
    d.ellipse([8 * S, 6 * S, 24 * S, 27 * S], fill=W)                                 # 머리
    d.polygon([(13 * S, 6 * S), (16 * S, 2 * S), (19 * S, 6 * S)], fill=W)          # 정수리 삐침
    T = (0, 0, 0, 0)
    d.polygon([(10.5 * S, 13 * S), (15 * S, 14.5 * S), (14.5 * S, 17.5 * S), (11 * S, 16.5 * S)], fill=T)   # 눈(사나운)
    d.polygon([(21.5 * S, 13 * S), (17 * S, 14.5 * S), (17.5 * S, 17.5 * S), (21 * S, 16.5 * S)], fill=T)
    d.polygon([(15.2 * S, 18 * S), (16.8 * S, 18 * S), (16 * S, 20 * S)], fill=T)    # 코
    d.chord([11 * S, 17 * S, 21 * S, 25.5 * S], 0, 180, fill=T)                       # 입
    for k in range(4):                                                                  # 이빨
        x = 12.3 * S + k * 2.2 * S
        d.polygon([(x, 21.2 * S), (x + 1.8 * S, 21.2 * S), (x + 0.9 * S, 23.2 * S)], fill=W)
    return im.resize((32, 32), Image.LANCZOS)


def build_goblin_barrel(goblin_src, planks_src):
    import json
    from bbrender import load_tex
    gob = json.load(open(goblin_src, encoding='utf-8'))
    prep_goblin(gob)                                   # 다듬은 고블린 머리 사용
    gels = {e['uuid']: e for e in gob['elements']}
    head = find(gob, 'head')
    arm = find(gob, 'left_arm')
    planks = next(load_tex(t) for t in json.load(open(planks_src, encoding='utf-8'))['textures'] if 'planks' in t['name'])
    # 팀색 띠 (밝은 회색 → 플러그인이 팀색으로 칠함) + 못 자국
    band = Image.new('RGBA', (16, 16))
    for y in range(16):
        for x in range(16):
            v = 205 + ((x * 7 + y * 5) % 7) * 6
            band.putpixel((x, y), (v, v, v, 255))
    for x in (2, 8, 13):
        band.putpixel((x, 7), (150, 150, 150, 255)); band.putpixel((x, 8), (170, 170, 170, 255))
    # 짙은 쇠테
    iron = Image.new('RGBA', (16, 16))
    for y in range(16):
        for x in range(16):
            v = 58 + ((x * 5 + y * 3) % 5) * 5
            iron.putpixel((x, y), (v, v + 2, v + 6, 255))
    for x in (3, 9, 14):
        iron.putpixel((x, 7), (140, 144, 150, 255))
    dark = Image.new('RGBA', (16, 16), (26, 20, 16, 255))
    rim = planks.point(lambda v: int(v * 0.72))
    gtex = copy.deepcopy(gob['textures'][0])
    doc = {'meta': {'format_version': '4.10', 'model_format': 'free', 'box_uv': False}, 'name': 'clash_goblin_barrel',
           'model_identifier': 'clash_goblin_barrel', 'visible_box': [1, 1, 0], 'resolution': {'width': 16, 'height': 16},
           'elements': [], 'outliner': [], 'textures': [gtex], 'animations': []}
    tp = add_texture(doc, planks, 'planks.png')
    tb = add_texture(doc, band, 'band.png')
    ti = add_texture(doc, iron, 'iron.png')
    td = add_texture(doc, dark, 'dark.png')
    tr = add_texture(doc, rim, 'rim.png')
    tm = add_texture(doc, goblin_mark(), 'mark.png')
    C = 17.0                                          # 통 중심 높이 (회전 피벗)
    root = bone('barrel', [0, C, 0])
    shell = bone('shell', [0, C, 0])
    R, H = 15.0, 32.0                                 # 반지름, 높이 → 지름 약 2블록
    y0 = C - H / 2

    def stave(parent, frm, to, tex):
        """옆면은 나무결이 세로(통 널빤지)로 가게 uv 회전"""
        e = add_cube(doc, parent, frm, to, tex)
        for f in ('north', 'south', 'east', 'west'):
            e['faces'][f]['rotation'] = 90
        return e
    # 둥근 통: 위아래는 좁고 가운데가 불룩 (3단)
    for (a0, a1, k) in ((0, 7, 0.93), (7, H - 7, 1.0), (H - 7, H, 0.93)):
        r = R * k
        stave(shell, [-r, y0 + a0, -r * 0.72], [r, y0 + a1, r * 0.72], tp)
        stave(shell, [-r * 0.72, y0 + a0, -r], [r * 0.72, y0 + a1, r], tp)
    # 위/아래 테두리 (짙은 나무)
    for yy in (y0, y0 + H - 1.6):
        add_cube(doc, shell, [-R * 0.93 - 0.4, yy, -R * 0.67 - 0.4], [R * 0.93 + 0.4, yy + 1.6, R * 0.67 + 0.4], tr)
        add_cube(doc, shell, [-R * 0.67 - 0.4, yy, -R * 0.93 - 0.4], [R * 0.67 + 0.4, yy + 1.6, R * 0.93 + 0.4], tr)
    # 안쪽 어둠 (윗면 바로 아래)
    add_cube(doc, shell, [-R * 0.62, y0 + H - 0.7, -R * 0.62], [R * 0.62, y0 + H + 0.05, R * 0.62], td)
    # 팀색 띠: 양 끝에만
    bands = bone('tc_bands', [0, C, 0])
    for by in (y0 + 2.2, y0 + H - 5.4):
        r = R * 0.93
        add_cube(doc, bands, [-r - 0.5, by, -r * 0.74 - 0.5], [r + 0.5, by + 3.2, r * 0.74 + 0.5], tb, uv=(0, 0, 16, 4))
        add_cube(doc, bands, [-r * 0.74 - 0.5, by, -r - 0.5], [r * 0.74 + 0.5, by + 3.2, r + 0.5], tb, uv=(0, 0, 16, 4))
    # 짙은 쇠테: 불룩한 가운데 위아래 가장자리
    hoops = bone('hoops', [0, C, 0])
    for by in (y0 + 7.4, y0 + H - 9.4):
        add_cube(doc, hoops, [-R - 0.45, by, -R * 0.72 - 0.45], [R + 0.45, by + 2, R * 0.72 + 0.45], ti, uv=(0, 0, 16, 3))
        add_cube(doc, hoops, [-R * 0.72 - 0.45, by, -R - 0.45], [R * 0.72 + 0.45, by + 2, R + 0.45], ti, uv=(0, 0, 16, 3))
    # 가운데 하얀 고블린 마크 (네 면)
    mark = bone('mark', [0, C, 0])
    m = 13.0
    cy = C
    for f, (frm, to) in {'north': ([-m / 2, cy - m / 2, -R - 0.06], [m / 2, cy + m / 2, -R - 0.02]),
                         'south': ([-m / 2, cy - m / 2, R + 0.02], [m / 2, cy + m / 2, R + 0.06]),
                         'west': ([-R - 0.06, cy - m / 2, -m / 2], [-R - 0.02, cy + m / 2, m / 2]),
                         'east': ([R + 0.02, cy - m / 2, -m / 2], [R + 0.06, cy + m / 2, m / 2])}.items():
        e = add_cube(doc, mark, frm, to, tm)
        for ff in list(e['faces']):
            if ff != f:
                e['faces'][ff]['texture'] = None       # 마크는 바깥 면만
    root['children'] += [shell, bands, hoops, mark]

    def clone_into(src_node, target, dx, dy, dz):
        def w(n):
            out = []
            for c in n.get('children', []):
                if isinstance(c, str):
                    e = copy.deepcopy(gels[c]); e['uuid'] = uid()
                    e['from'] = [e['from'][0] + dx, e['from'][1] + dy, e['from'][2] + dz]
                    e['to'] = [e['to'][0] + dx, e['to'][1] + dy, e['to'][2] + dz]
                    e['origin'] = [e.get('origin', [0, 0, 0])[0] + dx, e.get('origin', [0, 0, 0])[1] + dy, e.get('origin', [0, 0, 0])[2] + dz]
                    for f in e['faces'].values():
                        if f.get('texture') is not None:
                            f['texture'] = 0
                    doc['elements'].append(e); out.append(e['uuid'])
                else:
                    nb = bone(n['name'] + '_' + c['name'], [c['origin'][0] + dx, c['origin'][1] + dy, c['origin'][2] + dz], w(c), c.get('rotation'))
                    out.append(nb)
            return out
        target['children'] += w(src_node)

    neck = head['origin']
    top = y0 + H
    spots = [(-6.5, -4.0, -25, 0), (6.5, -4.0, 25, 0), (0.0, 6.0, 180, 1.5)]   # x, z, 머리 방향(도), 높이 보정
    for i, (x, z, yaw, up) in enumerate(spots):
        g = bone('goblin%d' % (i + 1), [x, top - 2 + up, z], rotation=[0, yaw, 0])
        clone_into(head, g, x - neck[0], top - 0.8 + up - neck[1], z - neck[2])
        root['children'].append(g)
    # 앞 고블린 하나는 단검 든 팔을 내밀고 흔듦
    a = bone('wave_arm', [-9.0, top - 1, -5.0], rotation=[-150, 0, 20])
    ao = arm['origin']
    clone_into(arm, a, -9.0 - ao[0], top - 1 - ao[1], -5.0 - ao[2])
    root['children'].append(a)
    doc['outliner'] = [root]
    set_anims(doc, {
        'idle': (0.7, 'loop', {'barrel': {'rotation': [(0, (0, 0, 0)), (0.175, (-90, 0, 0)), (0.35, (-180, 0, 0)), (0.525, (-270, 0, 0)), (0.7, (-360, 0, 0))]},
                               'wave_arm': {'rotation': cyc(0.7, (0, 0, 0), (25, 0, 0))}}),
        'walk': (0.7, 'loop', {'barrel': {'rotation': [(0, (0, 0, 0)), (0.35, (-180, 0, 0)), (0.7, (-360, 0, 0))]}}),
    })
    return doc


# ------------------------------------------------------------------ 피격 흔들림 (건물/타워)
def add_hit(doc, bone_name, amp=3.0, squash=0.03):
    """맞았을 때 짧게 흔들리는 'hit' 애니메이션 추가 (기존 애니메이션은 유지)"""
    by = {n['name']: n for n, _ in nodes(doc)}
    b = by[bone_name]
    s = squash
    kfs = []
    for t, v in ((0, (0, 0, 0)), (0.05, (amp * 0.5, 0, amp)), (0.11, (-amp * 0.4, 0, -amp * 0.8)),
                 (0.18, (amp * 0.25, 0, amp * 0.45)), (0.25, (0, 0, -amp * 0.15)), (0.32, (0, 0, 0))):
        kfs.append({'channel': 'rotation', 'data_points': [{'x': '%g' % v[0], 'y': '%g' % v[1], 'z': '%g' % v[2]}],
                    'uuid': uid(), 'time': t, 'color': -1, 'interpolation': 'linear'})
    for t, v in ((0, (1, 1, 1)), (0.05, (1 + s, 1 - s, 1 + s)), (0.16, (1 - s * 0.4, 1 + s * 0.4, 1 - s * 0.4)), (0.32, (1, 1, 1))):
        kfs.append({'channel': 'scale', 'data_points': [{'x': '%g' % v[0], 'y': '%g' % v[1], 'z': '%g' % v[2]}],
                    'uuid': uid(), 'time': t, 'color': -1, 'interpolation': 'linear'})
    doc.setdefault('animations', [])
    doc['animations'] = [a for a in doc['animations'] if a['name'] != 'hit']
    doc['animations'].append({'uuid': uid(), 'name': 'hit', 'loop': 'once', 'override': False, 'length': 0.32, 'snapping': 20,
                              'selected': False, 'anim_time_update': '', 'blend_weight': '', 'start_delay': '', 'loop_delay': '',
                              'animators': {b['uuid']: {'name': bone_name, 'type': 'bone', 'keyframes': kfs}}})
