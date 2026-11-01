"""규격표 → 모델별 배율 계산 (현재 패키지 모델 기준). 결과: spec_factors.json"""
import json, sys, yaml
sys.path.insert(0, '.')
from size_spec import SPEC, SAME, FOLLOW, WEAPON
from measure_model import measure
B = sys.argv[1]  # models/base 폴더 (규격 적용 전)
cards = yaml.safe_load(open('dec/config.yml', encoding='utf-8'))['cards']
def mid(card):
    return 'clash_skeleton_balloon' if card == 'skeleton_barrel' else cards[card]['model'].split(':')[0]
out = {}
for card, (ft, at) in SPEC.items():
    m = mid(card); d = json.load(open('%s/%s.bbmodel' % (B, m)))
    full = measure(d); core = measure(d, WEAPON)
    bld = cards[card].get('type') == 'BUILDING'
    cur = max(full[0], full[1]) if bld else max(full[0], core[1])
    out[m] = {'factor': round(at * 3 / cur, 4), 'cur': round(cur, 3), 'target': at * 3, 'height': round(full[2] * at * 3 / cur, 3)}
for card, src in SAME.items():
    m = cards[card]['model'].split(':')[0]
    if m not in out:
        d = json.load(open('%s/%s.bbmodel' % (B, m))); full = measure(d); core = measure(d, WEAPON)
        cur = max(full[0], core[1]); at = SPEC[src][1]
        out[m] = {'factor': round(at * 3 / cur, 4), 'cur': round(cur, 3), 'target': at * 3, 'height': round(full[2] * at * 3 / cur, 3)}
for m, src in FOLLOW.items():
    d = json.load(open('%s/%s.bbmodel' % (B, m))); full = measure(d); f = out[src]['factor']
    out[m] = {'factor': f, 'cur': round(max(full[0], full[1]), 3), 'target': round(max(full[0], full[1]) * f, 3), 'height': round(full[2] * f, 3), 'follow': src}
from size_spec import ADJUST
for m, a in ADJUST.items():
    m = m.split('@')[0]   # 같은 모델 두 번째 조정
    v = out[m]
    if isinstance(a, (int, float)): k = a
    elif a[0] == 'm': k = max(out[a[1]]['height'], out[a[1]]['target']) * a[2] / max(v['height'], v['target'])
    else: k = out[a[1]]['height' if a[0] == 'h' else 'target'] * a[2] / v['height' if a[0] == 'h' else 'target']
    v['factor'] = round(v['factor'] * k, 4); v['target'] = round(v['target'] * k, 3); v['height'] = round(v['height'] * k, 3); v['adjust'] = round(k, 3)
for m, src in FOLLOW.items():
    if src in ADJUST and m not in ADJUST and m + '@2' not in ADJUST and m + '@3' not in ADJUST:
        out[m]['factor'] = out[src]['factor']
from size_spec import TOWERS, TOWER_FOLLOW
for m, tgt in TOWERS.items():
    d = json.load(open('%s/%s.bbmodel' % (B, m))); full = measure(d); cur = max(full[0], full[1])
    out[m] = {'factor': round(tgt / cur, 4), 'cur': round(cur, 3), 'target': tgt, 'height': round(full[2] * tgt / cur, 3)}
for m, src in TOWER_FOLLOW.items():
    out[m] = {'factor': out[src]['factor'], 'follow': src}
from size_spec import WIDEN
for m, (kx, kz) in WIDEN.items():
    out[m]['widen'] = [kx, kz]; out[m]['target'] = round(out[m]['target'] * kx, 3)
json.dump(out, open('spec_factors.json', 'w'), indent=1, ensure_ascii=False)
for k, v in sorted(out.items()):
    if 'cur' in v: print('%-26s x%.2f  폭 %.2f→%.2f  높이 %.2f' % (k, v['factor'], v['cur'], v['target'], v['height']))
