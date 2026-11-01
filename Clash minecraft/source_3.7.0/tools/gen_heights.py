"""models/base 의 모델 높이·폭(블록) → ModelHeights.java (체력바 높이, 배치 미리보기 초록 모델 범위에 씀)"""
import json, glob, os, sys
B = sys.argv[1]; out = sys.argv[2]
rows = []
for p in sorted(glob.glob(B + '/*.bbmodel')):
    d = json.load(open(p)); E = [e for e in d['elements'] if e['name'] != 'hitbox']
    if not E: continue
    # 회전된 큐브는 꼭짓점을 돌려서 실제 높이 계산 (체력바가 모델 맨 위에 오게)
    import math
    def corners(e):
        f, t = e['from'], e['to']
        pts = [(x, y, z) for x in (f[0], t[0]) for y in (f[1], t[1]) for z in (f[2], t[2])]
        r = e.get('rotation') or [0, 0, 0]
        if isinstance(r, dict): r = [0, 0, 0]
        o = e.get('origin') or [0, 0, 0]
        ax, ay, az = [math.radians(v) for v in r]
        out = []
        for x, y, z in pts:
            x -= o[0]; y -= o[1]; z -= o[2]
            # Blockbench: X → Y → Z 순서
            y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
            x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
            x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
            out.append((x + o[0], y + o[1], z + o[2]))
        return out
    h = max(c[1] for e in E for c in corners(e)) / 16.0
    w = max(max(e['to'][0], e['from'][0]) - min(e['to'][0], e['from'][0]) for e in E)
    xs = [v for e in E for v in (e['from'][0], e['to'][0])]; zs = [v for e in E for v in (e['from'][2], e['to'][2])]
    w = max(max(xs) - min(xs), max(zs) - min(zs)) / 16.0
    n = os.path.basename(p)[:-8]
    # 눈높이: 'head' 본(모자·투구 등 장식 제외) 중간쯤, 머리 본이 없으면 높이의 85%
    el = {e['uuid']: e for e in E if 'uuid' in e}
    hd = []
    def walk(node, inhead):
        if isinstance(node, str):
            if inhead and node in el: hd.append(el[node])
            return
        nm = node.get('name', '').lower()
        if inhead and any(k in nm for k in ('hat', 'helmet', 'crown', 'hair', 'plume', 'horn')):
            return
        hh = inhead or nm == 'head' or nm.endswith('_head') or nm.startswith('head') or nm.startswith('h_head')
        for c in node.get('children', []): walk(c, hh)
    for nd in d.get('outliner', []): walk(nd, False)
    if hd:
        ys = [c[1] for e in hd for c in corners(e)]
        eye = (min(ys) + (max(ys) - min(ys)) * 0.55) / 16.0
    else:
        eye = h * 0.85
    rows.append('        E.put("%s", %.2f);' % (n, eye))
    rows.append('        H.put("%s", %.2f);' % (n, h))
    rows.append('        W.put("%s", %.2f);' % (n, w))
open(out, 'w', encoding='utf-8').write('''package kr.kjmn.clashmc;

import java.util.HashMap;
import java.util.Map;

/** 자동 생성 (gen_heights.py): 기본 모델의 높이 (블록) */
final class ModelHeights {
    private static final Map<String, Double> H = new HashMap<>();
    private static final Map<String, Double> W = new HashMap<>();
    private static final Map<String, Double> E = new HashMap<>();

    static {
%s
    }

    private ModelHeights() {
    }

    private static String key(String model) {
        String m = model;
        int i = m.indexOf('#');
        if (i > 0) m = m.substring(0, i);
        i = m.indexOf(':');
        if (i > 0) m = m.substring(0, i);
        return m;
    }

    static double of(String model) {
        return model == null ? 0.0 : H.getOrDefault(key(model), 0.0);
    }

    /** 모델 눈높이 (블록, 머리 본 기준) - 없으면 0 */
    static double eye(String model) {
        return model == null ? 0.0 : E.getOrDefault(key(model), 0.0);
    }

    /** 모델 가로 폭 (블록, x·z 중 큰 쪽) */
    static double width(String model) {
        return model == null ? 0.0 : W.getOrDefault(key(model), 0.0);
    }
}
''' % '\n'.join(rows))
print(len(rows) // 3)
