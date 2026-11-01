"""Build ClashMC models from the user's own Blockbench files.
Buildings / towers: ONE model for both teams (team-coloured cubes in '*_tc_' bones, tinted by the plugin)."""
import json, os, sys
sys.path.insert(0, '/home/claude/umodels')
from adapt import adapt, teamify, check, bones, TINT
from bbrender import render
import prep

SRC = '/home/claude/umodels/src'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/umodels/out'
ART = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/rpack/skin_art'
BASE, CARD = OUT + '/base', OUT + '/art'
for d in (BASE, CARD, ART):
    os.makedirs(d, exist_ok=True)

DEFS = {   # src key: (file, source team colour or None, scale, building?, card id, model id, extra)
    'princess': ('princessbluemodelengine', 'blue', 1.3, True, None, 'clash_princess', {}),
    'king': ('kingbluemodelengine', 'blue', 1.07, True, None, 'clash_king', {}),
    'cannon': ('cannonblue', 'blue', 0.8, True, 'cannon', 'clash_cannon',
               dict(renames={'head': 'top', 'left_arm': 'base'}, prefix_children={'head': 1, 'left_arm': 1})),
    'tesla': ('electro_red', 'red', 0.85, True, 'tesla', 'clash_tesla', dict(pre=prep.prep_tesla)),
    'inferno_tower': ('inferno_red', 'red', 0.5, True, 'inferno_tower', 'clash_inferno', {}),
    'giant': ('giantmodelengine', None, 1.0, False, 'giant', 'clash_giant', dict(pre=prep.prep_giant)),
    'hog_rider': ('hogridermodelengine', None, 1.0, False, 'hog_rider', 'clash_hog_rider', dict(pre=prep.prep_hog)),
    'goblin': ('goblin', None, 1.0, False, 'goblins', 'clash_goblin', dict(pre=prep.prep_goblin)),
}


def portrait(doc, building, path, tint=None, size=256):
    cam = (0.55, 0.45, -1.0) if building else (0.4, 0.25, -1.0)
    im = render(doc, size, cam, bg=(0, 0, 0, 0), tint=tint)
    im = im.crop(im.getbbox())
    if not building:
        w, h = im.size
        if h > w * 1.15:
            im = im.crop((0, 0, w, int(max(w * 1.15, h * 0.62))))
    im.save(path)


HIT_BONE = {'tesla': 'body', 'inferno_tower': 'body'}
for src, (f, team, scale, building, card, mid, extra) in DEFS.items():
    doc, _ = adapt('%s/%s.bbmodel' % (SRC, f), mid, scale=scale, **extra)
    moved = teamify(doc, team) if team else 0
    if building:   # 맞으면 흔들림 (테슬라/인페르노는 숨기·올라오기 본과 안 겹치게 body 본)
        prep.add_hit(doc, HIT_BONE.get(src, 'all'), amp=1.6 if src in ('princess', 'king') else 3.5)
    bad = check(doc)
    assert not bad, (mid, bad[:3])
    json.dump(doc, open('%s/%s.bbmodel' % (BASE, mid), 'w', encoding='utf-8'), ensure_ascii=False)
    tint = TINT['blue'] if team else None
    portrait(doc, building, os.path.join(ART, 'default_%s.png' % src), tint)
    if card:
        portrait(doc, building, os.path.join(CARD, 'card_%s.png' % card), tint)
    print(mid, 'cubes', len(doc['elements']), 'bones', len(bones(doc)), 'tex', doc['resolution']['width'], 'team cubes', moved,
          'anims', [a['name'] for a in doc.get('animations', [])])

# 고블린 통 (날아가는 투사체 모델): 다듬은 고블린 머리 3개가 든 큰 통, 쇠테는 팀색
gb = prep.build_goblin_barrel(SRC + '/goblin.bbmodel', SRC + '/princessbluemodelengine.bbmodel')
tmp = OUT + '/_gb_raw.bbmodel'
json.dump(gb, open(tmp, 'w', encoding='utf-8'))
doc, _ = adapt(tmp, 'clash_goblin_barrel')
os.remove(tmp)
assert not check(doc)
json.dump(doc, open('%s/clash_goblin_barrel.bbmodel' % BASE, 'w', encoding='utf-8'), ensure_ascii=False)
portrait(doc, True, os.path.join(CARD, 'card_goblin_barrel.png'), TINT['blue'])
print('clash_goblin_barrel cubes', len(doc['elements']), 'anims', [a['name'] for a in doc['animations']])

# 통나무 카드 아이콘 (모델은 models2/spells.py → build_free.py 에서 출력)
sys.path.insert(0, '/home/claude/models2')
import spells
_lg = spells.the_log()
_lg.export(OUT + '/_log.bbmodel')
_ld = json.load(open(OUT + '/_log.bbmodel'))
os.remove(OUT + '/_log.bbmodel')
_im = render(_ld, 256, (0.75, 0.35, -0.6), bg=(0, 0, 0, 0), tint=TINT['blue'])
_im.crop(_im.getbbox()).save(os.path.join(CARD, 'card_the_log.png'))

# 해골 비행선 카드 아이콘
_sb = spells.skeleton_balloon()
_sb.export(OUT + '/_sb.bbmodel')
_sd = json.load(open(OUT + '/_sb.bbmodel'))
os.remove(OUT + '/_sb.bbmodel')
_im = render(_sd, 256, (0.45, 0.25, -1.0), bg=(0, 0, 0, 0), tint=TINT['blue'])
_im.crop(_im.getbbox()).save(os.path.join(CARD, 'card_skeleton_barrel.png'))
