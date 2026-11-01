"""라바 펍: 용암색 통통한 새끼 용 (둥근 몸, 노란 배, 큰 눈, 작은 뿔, 주황 박쥐 날개, 짧은 다리, 꼬리).
usage: python3 mk_pup.py <model_tools dir> <out dir>"""
import sys, os
from models_mc_b import cb, loop, pix, new_model, common_tail


def lava_pup():
    m = new_model('clash_lava_pup')
    m.mats_({'lava': ('#ff7a1a', 'glow'), 'lava_d': ('#e04a12', 'glow'), 'lava_y': ('#ffc23a', 'glow'), 'lava_w': ('#fff0a0', 'glow'),
             'crust': ('#5a2614', 'stone'), 'eye': ('#2a1206', 'plain'), 'mouth': ('#8a1a0a', 'plain'),
             'wing': ('#ff6a18', 'leather', {'stitch': False}), 'wing_d': ('#c8380e', 'leather', {'stitch': False})})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 6, 0], root)
    spots = [('rect', 0.15, 0.2, 0.35, 0.35, '#e04a12'), ('rect', 0.65, 0.55, 0.85, 0.7, '#e04a12')]
    # 둥근 몸통 (가운데 넓고 위아래 좁게)
    cb(body, 0, 2.4, 0, 8.0, 7.0, 7.6, 'lava', decals={f: spots for f in ('east', 'west', 'south')})
    cb(body, 0, 3.2, 0, 9.0, 5.4, 6.6, 'lava')
    cb(body, 0, 3.2, 0, 6.6, 5.4, 8.6, 'lava')
    cb(body, 0, 1.6, 0, 6.0, 1.0, 6.0, 'lava_d')
    cb(body, 0, 9.4, 0, 6.4, 1.0, 6.0, 'lava')
    # 노란 배
    cb(body, 0, 2.6, -4.35, 5.0, 4.6, 0.4, 'lava_y', decals={'north': [('rect', 0.2, 0.25, 0.8, 0.75, '#fff0a0')]})
    # 얼굴: 큰 눈 + 작은 입 + 콧구멍
    face = pix(["........", ".ww..ww.", ".ek..ke.", ".kk..kk.", "........", "..n..n..", "..mmmm..", "........"],
               {'w': '#fff6d0', 'e': '#ffffff', 'k': '#2a1206', 'n': '#a8300c', 'm': '#8a1a0a'})
    cb(body, 0, 5.0, -4.4, 6.6, 4.6, 0.3, 'lava', decals={'north': face})
    cb(body, 0, 6.0, -5.0, 3.0, 1.6, 1.0, 'lava')                                   # 동그란 주둥이
    cb(body, -0.7, 6.6, -5.55, 0.5, 0.5, 0.2, 'mouth'); cb(body, 0.7, 6.6, -5.55, 0.5, 0.5, 0.2, 'mouth')
    for sx in (1, -1):
        cb(body, sx * 2.0, 8.6, -3.5, 2.2, 0.6, 0.6, 'lava_d')                       # 눈썹
        cb(body, sx * 2.6, 10.2, -0.6, 1.6, 1.4, 1.6, 'crust')                        # 작은 뿔
        cb(body, sx * 2.8, 11.6, -0.2, 0.9, 1.0, 0.9, 'crust')
        cb(body, sx * 4.7, 4.0, 0, 0.5, 2.0, 2.0, 'lava_y')                           # 옆구리 빛
        # 짧은 다리 + 발톱
        cb(body, sx * 2.2, 0.0, -0.8, 2.2, 1.8, 2.4, 'lava_d')
        cb(body, sx * 2.2, -0.4, -1.8, 2.2, 0.6, 0.8, 'crust')
        # 작은 팔
        cb(body, sx * 4.4, 3.4, -2.6, 1.4, 1.8, 1.4, 'lava_d')
    cb(body, 0, 10.4, 0.6, 1.4, 1.0, 3.6, 'lava_d')                                  # 등 줄기
    # 날개 (주황 박쥐 날개, 뼈대 진한 색)
    for sx, side in ((1, 'r'), (-1, 'l')):
        w = m.bone('wing_' + side, [sx * 3.0, 8.4, 1.6], body)
        cb(w, sx * 5.6, 8.2, 1.6, 5.4, 0.8, 0.8, 'wing_d')                            # 날개 팔
        cb(w, sx * 8.6, 8.2, 1.6, 1.0, 1.6, 1.0, 'wing_d')                            # 손목 갈고리
        cb(w, sx * 6.0, 7.9, 4.0, 5.8, 0.4, 4.4, 'wing',
           decals={f: [('rect', 0.32, 0, 0.38, 1, '#c8380e'), ('rect', 0.66, 0, 0.72, 1, '#c8380e')] for f in ('up', 'down')})
        cb(w, sx * 7.6, 7.9, 6.8, 2.6, 0.4, 1.4, 'wing')                              # 날개 끝 뾰족
    t = m.bone('tail', [0, 4.0, 3.8], body)
    cb(t, 0, 3.2, 5.4, 1.8, 1.6, 3.4, 'lava_d')
    cb(t, 0, 3.6, 7.6, 1.0, 1.0, 1.6, 'lava')
    cb(t, 0, 3.4, 8.8, 1.6, 1.4, 0.8, 'crust')                                      # 꼬리 끝
    m.hitbox(0.8, 0.8)
    flap = lambda L, a: {'wing_r': {'rotation': loop([[0, 0, -a], [0, 0, a * 0.6]], L)},
                         'wing_l': {'rotation': loop([[0, 0, a], [0, 0, -a * 0.6]], L)}}
    idle = {'body': {'position': loop([[0, 0, 0], [0, 1.0, 0]], 0.8)}, 'tail': {'rotation': loop([[0, 15, 0], [0, -15, 0]], 0.8)}}
    idle.update(flap(0.27, 35))
    m.anim('idle', 0.8, 'loop', idle)
    walk = dict(idle); walk.update(flap(0.2, 45))
    walk['root'] = {'rotation': loop([[10, 0, 0], [10, 0, 0]], 0.8)}
    m.anim('walk', 0.8, 'loop', walk)
    m.anim('attack', 0.5, 'once', {'body': {'position': [(0, [0, 0, 0]), (0.12, [0, 0.5, 1.5]), (0.25, [0, -0.5, -3.0]), (0.5, [0, 0, 0])],
                                            'rotation': [(0, [0, 0, 0]), (0.12, [-12, 0, 0]), (0.25, [14, 0, 0]), (0.5, [0, 0, 0])]}})
    common_tail(m)
    return m


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    os.makedirs(out, exist_ok=True)
    m = lava_pup()
    m.sculpt(); n = m.fit(48); bad = m.check(48)
    m.export(os.path.join(out, m.name + '.bbmodel'))
    print(m.name, 'cubes', m.cubes_total, 'split', n, 'bad', bad)
