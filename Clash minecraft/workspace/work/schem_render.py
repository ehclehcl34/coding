"""schem → 등각 투영 / 위에서 본 미리보기 PNG (블록 대표색)."""
import sys, numpy as np
from PIL import Image, ImageDraw
import schem

COL = {
    'grass_block': (104, 163, 64), 'green_terracotta': (76, 83, 42), 'dirt': (134, 96, 67), 'terracotta': (152, 94, 67),
    'stone': (125, 125, 125), 'andesite': (136, 136, 137), 'tuff': (108, 109, 102), 'cobblestone': (122, 121, 122),
    'mossy_cobblestone': (110, 118, 94), 'water': (52, 92, 190), 'sand': (219, 207, 163), 'gravel': (131, 127, 126),
    'clay': (160, 166, 179), 'mud': (60, 57, 60), 'seagrass': (40, 120, 30), 'tall_seagrass': (40, 120, 30),
    'lily_pad': (32, 128, 48), 'stone_bricks': (122, 121, 122), 'mossy_stone_bricks': (115, 121, 105),
    'cracked_stone_bricks': (118, 117, 118), 'chiseled_stone_bricks': (119, 118, 119), 'polished_andesite': (132, 135, 134),
    'spruce_planks': (114, 84, 48), 'stripped_spruce_log': (115, 89, 52), 'stone_brick_wall': (122, 121, 122),
    'stone_brick_stairs': (122, 121, 122), 'stone_brick_slab': (122, 121, 122), 'lantern': (255, 200, 90),
    'blue_glazed_terracotta': (47, 64, 139), 'red_glazed_terracotta': (181, 59, 53), 'blue_concrete': (44, 46, 143),
    'red_concrete': (142, 32, 32), 'blue_wool': (53, 57, 157), 'red_wool': (160, 39, 34), 'blue_terracotta': (74, 59, 91),
    'red_terracotta': (143, 61, 46), 'blue_carpet': (53, 57, 157), 'red_carpet': (160, 39, 34), 'iron_bars': (140, 140, 140),
    'dark_oak_planks': (66, 43, 20), 'dark_oak_fence': (66, 43, 20), 'stripped_dark_oak_log': (96, 76, 49),
    'deepslate_tile_slab': (54, 54, 55), 'deepslate_tiles': (54, 54, 55), 'deepslate_bricks': (70, 70, 71),
    'polished_deepslate': (72, 72, 73), 'smooth_stone': (158, 158, 158), 'blue_stained_glass': (51, 76, 178),
    'red_stained_glass': (153, 51, 51), 'blue_stained_glass_pane': (51, 76, 178), 'red_stained_glass_pane': (153, 51, 51),
    'blue_wall_banner': (53, 57, 157), 'red_wall_banner': (160, 39, 34), 'shroomlight': (240, 146, 70), 'glowstone': (250, 220, 120),
    'azalea_leaves': (90, 117, 44), 'flowering_azalea_leaves': (112, 120, 74), 'poppy': (200, 40, 30), 'dandelion': (240, 220, 50),
    'cornflower': (70, 100, 220), 'oxeye_daisy': (230, 230, 220), 'azure_bluet': (220, 230, 240), 'short_grass': (95, 150, 55),
    'spruce_fence': (114, 84, 48), 'dirt_path': (148, 122, 65), 'coarse_dirt': (119, 85, 59),
}
THIN = ('carpet', 'banner', 'grass', 'poppy', 'dandelion', 'cornflower', 'daisy', 'bluet', 'lily_pad', 'seagrass', 'lantern')


def col(b):
    n = b.split('[')[0].replace('minecraft:', '')
    if n in COL:
        return COL[n]
    for k, v in COL.items():
        if k in n:
            return v
    return (255, 0, 255)


def render(path, out, scale=6, yaw='iso'):
    s = schem.load(path)
    g = s['grid']; H, L, W = g.shape
    air = 'minecraft:air'
    # iso: x→right-down, z→left-down
    sx, sy = scale, scale / 2
    w_img = int((W + L) * sx + 20); h_img = int((W + L) * sy + H * scale + 20)
    im = Image.new('RGB', (w_img, h_img), (24, 26, 32))
    dr = ImageDraw.Draw(im)
    ox = L * sx + 10; oy = H * scale + 10
    order = []
    for y in range(H):
        for z in range(L):
            for x in range(W):
                b = g[y, z, x]
                if b == air:
                    continue
                order.append((x + z, y, x, z, b))
    order.sort()
    for _, y, x, z, b in order:
        c = np.array(col(b), dtype=float)
        px = ox + (x - z) * sx
        py = oy + (x + z) * sy - y * scale
        top = [(px, py), (px + sx, py + sy), (px, py + 2 * sy), (px - sx, py + sy)]
        thin = any(t in b for t in THIN) and 'grass_block' not in b
        hgt = scale * (0.25 if thin else 1.0)
        left = [(px - sx, py + sy), (px, py + 2 * sy), (px, py + 2 * sy + hgt), (px - sx, py + sy + hgt)]
        right = [(px, py + 2 * sy), (px + sx, py + sy), (px + sx, py + sy + hgt), (px, py + 2 * sy + hgt)]
        if thin:
            top = [(p[0], p[1] + scale - hgt) for p in top]
            left = [(p[0], p[1] + scale - hgt) for p in left]
            right = [(p[0], p[1] + scale - hgt) for p in right]
        dr.polygon(left, fill=tuple((c * 0.7).astype(int)))
        dr.polygon(right, fill=tuple((c * 0.55).astype(int)))
        dr.polygon(top, fill=tuple(c.astype(int)))
    im = im.crop(im.getbbox())
    im.save(out)


def top(path, out, scale=6):
    s = schem.load(path)
    g = s['grid']; H, L, W = g.shape
    im = Image.new('RGB', (W * scale, L * scale))
    px = im.load()
    for z in range(L):
        for x in range(W):
            for y in range(H - 1, -1, -1):
                b = g[y, z, x]
                if b != 'minecraft:air':
                    c = np.array(col(b), float) * (0.7 + 0.3 * y / H)
                    for i in range(scale):
                        for j in range(scale):
                            px[x * scale + i, z * scale + j] = tuple(c.astype(int))
                    break
    im.save(out)


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2] + '_iso.png')
    top(sys.argv[1], sys.argv[2] + '_top.png')
