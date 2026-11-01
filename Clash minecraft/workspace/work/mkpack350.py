"""3.4.2 UI 팩 + 새 카드 아이콘 14종 + 배경음악 → ClashMC_UI_pack_350.zip"""
import zipfile, json, os, sys
W = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(W, 'chk/ClashMC_UI_pack.zip')
out = os.path.join(W, 'ClashMC_UI_pack_350.zip')
CARDS = ['goblin_cage', 'witch', 'sparky', 'zappies', 'night_witch', 'pekka', 'x_bow', 'dark_prince', 'cannon_cart', 'battle_ram',
         'wizard', 'dart_goblin', 'heal_spirit', 'elixir_golem', 'bomb_tower']
files = {}
with zipfile.ZipFile(src) as z:
    for n in z.namelist():
        if not n.endswith('/'):
            files[n] = z.read(n)
for c in CARDS:
    for suf in ('', '_off'):
        k = 'card_%s%s' % (c, suf)
        files['assets/clashmc/items/%s.json' % k] = json.dumps({"model": {"type": "minecraft:model", "model": "clashmc:item/%s" % k}}).encode()
        files['assets/clashmc/models/item/%s.json' % k] = json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": "clashmc:item/%s" % k}}).encode()
        files['assets/clashmc/textures/item/%s.png' % k] = open(os.path.join(W, 'newicons2', k + '.png'), 'rb').read()
for k in ('ui_music_on', 'ui_music_off'):
    files['assets/clashmc/items/%s.json' % k] = json.dumps({"model": {"type": "minecraft:model", "model": "clashmc:item/%s" % k}}).encode()
    files['assets/clashmc/models/item/%s.json' % k] = json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": "clashmc:item/%s" % k}}).encode()
    files['assets/clashmc/textures/item/%s.png' % k] = open(os.path.join(W, 'newicons2', k + '.png'), 'rb').read()
bgm = os.path.join(W, 'bgm/assets/clashmc')
if os.path.isdir(bgm):
    for root, _, fs in os.walk(bgm):
        for f in fs:
            p = os.path.join(root, f)
            files[os.path.relpath(p, os.path.join(W, 'bgm')).replace(os.sep, '/')] = open(p, 'rb').read()
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, (1980, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_STORED if n.endswith('.ogg') else zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
print(len(files), os.path.getsize(out))
