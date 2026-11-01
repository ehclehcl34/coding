"""Sponge schematic v3 read/write helpers + quick top-down renderer."""
import nbtlib, numpy as np
from nbtlib import tag


def varints(data):
    out, i, n = [], 0, len(data)
    b = bytes(int(x) & 0xFF for x in data)
    while i < n:
        v = 0; s = 0
        while True:
            c = b[i]; i += 1
            v |= (c & 0x7F) << s
            if not c & 0x80:
                break
            s += 7
        out.append(v)
    return out


def enc_varints(vals):
    out = bytearray()
    for v in vals:
        while True:
            c = v & 0x7F; v >>= 7
            if v:
                out.append(c | 0x80)
            else:
                out.append(c); break
    return out


def load(path):
    f = nbtlib.load(path)
    r = f['Schematic'] if 'Schematic' in f else f
    W, H, L = int(r['Width']), int(r['Height']), int(r['Length'])
    pal = {int(v): str(k) for k, v in r['Blocks']['Palette'].items()}
    ids = np.array(varints(r['Blocks']['Data']), dtype=np.int32).reshape(H, L, W)
    grid = np.empty((H, L, W), dtype=object)
    names = np.array([pal[i] for i in range(len(pal))], dtype=object)
    grid[:] = names[ids]
    return dict(W=W, H=H, L=L, grid=grid, offset=[int(v) for v in r['Offset']], data_version=int(r['DataVersion']),
                block_entities=r['Blocks'].get('BlockEntities', []), raw=f)


def save(path, grid, offset, data_version=4189, name='clash_arena', block_entities=None):
    H, L, W = grid.shape
    flat = grid.reshape(-1)
    pal = {}
    vals = []
    for b in flat:
        if b not in pal:
            pal[b] = len(pal)
        vals.append(pal[b])
    root = nbtlib.File({'Schematic': tag.Compound({
        'Version': tag.Int(3), 'DataVersion': tag.Int(data_version),
        'Width': tag.Short(W), 'Height': tag.Short(H), 'Length': tag.Short(L),
        'Offset': tag.IntArray(offset),
        'Metadata': tag.Compound({'Name': tag.String(name), 'Author': tag.String('kjmn2134'),
                                  'WorldEdit': tag.Compound({'Origin': tag.IntArray([0, 0, 0]), 'Version': tag.String('7.3.10')})}),
        'Blocks': tag.Compound({
            'Palette': tag.Compound({k: tag.Int(v) for k, v in pal.items()}),
            'Data': tag.ByteArray([(x if x < 128 else x - 256) for x in enc_varints(vals)]),
            'BlockEntities': tag.List[tag.Compound](block_entities or []),
        }),
    })}, root_name='')
    root.save(path, gzipped=True)
