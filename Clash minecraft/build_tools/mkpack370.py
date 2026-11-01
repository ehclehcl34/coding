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
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in sorted(files):
        zi = zipfile.ZipInfo(n, (1980, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_STORED if n.endswith('.ogg') else zipfile.ZIP_DEFLATED
        z.writestr(zi, files[n])
print(len(files), os.path.getsize(out))
