"""투사체 모델: 램 라이더 볼라 (clash_bola), 미니언 다크 엘릭서 침 (clash_minion_goo).
usage: python3 mk_proj.py <bbgen2 dir> <out dir>"""
import sys, os
sys.argv = [sys.argv[0], sys.argv[1]] + sys.argv[2:]
from models_m3 import Model, cb, sphere


def bola():
    m = Model('clash_bola', density=2.5)
    m.mats_({'stone': ('#5e5a55', 'stone'), 'stone_d': ('#47433f', 'stone'), 'stone_l': ('#77726b', 'stone'),
             'rope': ('#b8945a', 'rope'), 'rope_d': ('#8e6c3e', 'rope'), 'leather': ('#6a4426', 'leather')})
    root = m.bone('root', [0, 0, 0])
    sp = m.bone('spin', [0, 4, 0], root)
    for sx in (1, -1):                                                      # 무거운 돌 2개 + 가죽 감싼 매듭
        sphere(sp, sx * 7.0, 4.0, 0, 2.8, ['stone_d', 'stone', 'stone_l', 'stone', 'stone_l', 'stone', 'stone_d', 'stone'], n=6)
        cb(sp, sx * 4.6, 3.1, 0, 1.6, 1.8, 1.8, 'leather')
    for i, x0 in enumerate((-4.0, -1.4, 1.2)):                              # 꼬인 밧줄 (마디마다 살짝 엇갈림)
        cb(sp, x0 + 1.4, 3.55 + (0.25 if i % 2 else 0), 0, 2.8, 0.9, 0.9, 'rope' if i % 2 else 'rope_d')
    cb(sp, 0, 3.0, 0, 1.6, 2.0, 1.6, 'rope_d')                              # 가운데 손잡이 매듭
    m.hitbox(0.6, 0.6)
    spin = {'spin': {'rotation': [(0, [0, 0, 0]), (0.1, [0, 90, 0]), (0.2, [0, 180, 0]), (0.3, [0, 270, 0]), (0.4, [0, 360, 0])]}}
    m.anim('idle', 0.4, 'loop', spin, interp='linear')
    m.anim('spin', 0.4, 'loop', spin, interp='linear')
    return m


def minion_goo():
    m = Model('clash_minion_goo', density=3.0)
    m.mats_({'goo': ('#2e1438', 'soft'), 'goo_l': ('#4e2462', 'soft'), 'goo_d': ('#1a0a22', 'soft'), 'shine': ('#b58ad0', 'glow')})
    root = m.bone('root', [0, 0, 0])
    b = m.bone('blob', [0, 4, 0], root)
    sphere(b, 0, 4.0, 0, 3.2, ['goo_d', 'goo', 'goo', 'goo', 'goo', 'goo_l'], n=6)   # 다크 엘릭서 방울 (보랏빛 검정)
    cb(b, -1.1, 5.6, -1.6, 1.0, 1.0, 0.6, 'shine')                          # 반짝임
    for (z, w, y) in ((3.4, 2.2, 3.2), (5.2, 1.4, 3.0), (6.6, 0.8, 2.8)):   # 뒤로 늘어지는 꼬리 (앞 = -Z)
        cb(b, 0, y, z, w, w, w, 'goo')
    for (x, y, z) in ((2.6, 2.0, 1.4), (-2.4, 1.8, 2.2)):                   # 튀는 작은 방울
        cb(b, x, y, z, 0.8, 0.8, 0.8, 'goo_l')
    m.hitbox(0.5, 0.5)
    wob = {'blob': {'scale': [(0, [1, 1, 1]), (0.15, [1.15, 0.88, 1.15]), (0.3, [0.9, 1.12, 0.9]), (0.45, [1, 1, 1])]}}
    m.anim('idle', 0.45, 'loop', wob)
    return m


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    os.makedirs(out, exist_ok=True)
    for fn in (bola, minion_goo):
        m = fn()
        m.sculpt()
        n = m.fit(48)
        bad = m.check(48)
        m.export(os.path.join(out, m.name + '.bbmodel'))
        print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad)
