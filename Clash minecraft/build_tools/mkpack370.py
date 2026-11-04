"""3.6.0 UI 팩 + 실제 카드 일러스트 아이콘(newicons3, 128x128) → ClashMC_UI_pack_370.zip"""
import zipfile, json, os
W = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(W, 'ClashMC_UI_pack_360.zip'); out = os.path.join(W, 'ClashMC_UI_pack_370.zip')
files = {}
with zipfile.ZipFile(src) as z:
    for n in z.namelist():
        if not n.endswith('/'):
            files[n] = z.read(n)
for f in os.listdir(os.path.join(W, 'newicons3')):
    k = f[:-4]
    files['assets/clashmc/items/%s.json' % k] = json.dumps({"model": {"type": "minecraft:model", "model": "clashmc:item/%s" % k}}).encode()
    files['assets/clashmc/models/item/%s.json' % k] = json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": "clashmc:item/%s" % k}}).encode()
    files['assets/clashmc/textures/item/%s.png' % k] = open(os.path.join(W, 'newicons3', f), 'rb').read()
# 새 GUI 배경 (newgui/*.png → 폰트 글자). gen_streamer_ui.py 가 만듦
GUI_EXTRA = {'gui_streamer': '', 'gui_spectate': '', 'gui_streamer_admin': ''}
fk = 'assets/minecraft/font/default.json'
fd = json.loads(files[fk].decode('utf-8'))
for name, ch in GUI_EXTRA.items():
    p = os.path.join(W, 'newgui', name + '.png')
    if not os.path.exists(p):
        continue
    fp = 'clashmc:font/%s.png' % name
    fd['providers'] = [x for x in fd['providers'] if x.get('file') != fp]
    assert ch not in {c for x in fd['providers'] for s in x.get('chars', []) for c in s}, name
    files['assets/clashmc/textures/font/%s.png' % name] = open(p, 'rb').read()
    fd['providers'].append({"type": "bitmap", "file": fp, "ascent": 13, "height": 222, "chars": [ch]})
files[fk] = json.dumps(fd, indent=1).encode('utf-8')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, (1980, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_STORED if n.endswith('.ogg') else zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
print(len(files), os.path.getsize(out))
