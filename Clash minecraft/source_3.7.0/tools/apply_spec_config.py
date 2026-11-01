"""규격표 → config.yml (건물 size, 히트박스 높이(모델 배율), 유닛 footprint). 히트박스 폭(충돌·사거리)은 유닛은 그대로."""
import json, re, sys, yaml
sys.path.insert(0, '.')
from size_spec import SPEC, SAME
F = json.load(open('spec_factors.json'))
src = open('dec/config.yml.prespec', encoding='utf-8').read()
cards = yaml.safe_load(src)['cards']
lines = src.split('\n')
# 카드 블록 위치
start = {}
for i, l in enumerate(lines):
    m = re.match(r'^  ([a-z_]+):\s*$', l)
    if m and m.group(1) in cards: start[m.group(1)] = i
order = sorted(start.items(), key=lambda x: x[1])
def block(card):
    i = start[card]; nxt = [v for k, v in order if v > i]
    return i, (nxt[0] if nxt else len(lines))
def mf(card):
    if card == 'skeleton_barrel': return F['clash_skeletons']['factor']
    m = cards[card].get('model', '').split(':')[0]
    return F[m]['factor'] if m in F else None
edits = {}
for card in cards:
    c = cards[card]; f = mf(card)
    spec = SPEC.get(card) or (SPEC[SAME[card]] if card in SAME else None)
    hb = c.get('hitbox')
    new = {}
    if c.get('type') == 'BUILDING':
        if spec:
            new['size'] = '    size: %g                     # 배치 %d×%d타일 (%d×%d블록)' % (spec[0] * 1.5, spec[0], spec[0], spec[0] * 3, spec[0] * 3)
            if hb: new['hitbox'] = '    hitbox: [%.2f, %.2f]          # 외형 %.2f블록' % (F[cards[card]['model']]['target'], hb[1] * f, F[cards[card]['model']]['target'])
        elif card == 'cannon_cart_broken':
            new['size'] = '    size: 3                     # 배치 2×2타일 (대포 카트와 같음)'
            if hb and f: new['hitbox'] = '    hitbox: [%.2f, %.2f]' % (hb[0] * f, hb[1] * f)
    elif f and hb:
        w = (F['clash_skeletons']['target'] if card == 'skeleton_barrel' else F[cards[card]['model'].split(':')[0]]['target']) if spec else hb[0] * f
        new['hitbox'] = '    hitbox: [%.2f, %.2f]          # 모델 겉모습 크기 (x%.2f)' % (w, hb[1] * f, f)
        if spec and spec[0] > 1 and c.get('type') != 'SPELL':
            new['footprint'] = '    footprint: %d                 # 배치 %d×%d타일 (미리보기 테두리)' % (spec[0], spec[0], spec[0])
    edits[card] = new
out = list(lines)
for card, new in sorted(edits.items(), key=lambda x: -start[x[0]]):
    if not new: continue
    i, j = block(card)
    for key, txt in new.items():
        idx = [k for k in range(i + 1, j) if re.match(r'^    %s:' % key, out[k])]
        if idx: out[idx[0]] = txt
        else:
            # 블록 끝 (빈줄/주석 전)에 추가
            k = j
            while k - 1 > i and (out[k - 1].strip() == '' or out[k - 1].lstrip().startswith('#')): k -= 1
            out.insert(k, txt); j += 1
open('dec/config.yml', 'w', encoding='utf-8').write('\n'.join(out))
y = yaml.safe_load(open('dec/config.yml', encoding='utf-8'))['cards']
for card in ['knight', 'giant', 'golem', 'cannon', 'tesla', 'x_bow', 'skeleton_barrel', 'bats', 'pekka', 'cannon_cart_broken', 'goblin_gang']:
    print(card, y[card].get('size'), y[card].get('hitbox'), y[card].get('footprint'))
