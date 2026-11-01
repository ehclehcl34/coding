"""ClashMC original unit designs (role-readable, not based on any existing game's characters)."""
from bbgen2 import Model
from kit import cb, part, face, visor, hood_face, humanoid, humanoid_anims, common_anims, quad_walk, flap

TC = '#efefef'   # team-tint base (bones named tc_* are tinted with the team colour in game)

STEEL = ('#a7b0ba', 'metal')
DSTEEL = ('#5f6770', 'metal')
GOLD = ('#d8aa3c', 'metal')
LEATHER = ('#6a4328', 'leather')
DLEATHER = ('#3e2818', 'leather')
SKIN = ('#e9b48f', 'skin')


def tc_cloth():
    return (TC, 'cloth')


# =================================================================== KNIGHT
def knight():
    """기사: 사슬 갑옷 + 팀색 서코트, 투구/방패 없이 장검 하나. 짧은 갈색 머리 + 짧게 다듬은 턱수염"""
    m = Model('clash_knight')
    m.mats_({'steel': STEEL, 'dsteel': DSTEEL, 'gold': GOLD, 'leather': LEATHER, 'dleather': DLEATHER,
             'tc': tc_cloth(), 'blade': ('#dfe5ea', 'metal'), 'chain': ('#8a929b', 'scale'), 'dchain': ('#6b727b', 'scale'),
             'skin': SKIN, 'hair': ('#5a3a22', 'hair'), 'beard': ('#6b4428', 'hair'), 'boot': ('#3e2a1c', 'leather')})
    fc = face(eye='#2b3a4a', brow='#4a2e1a', mouth='#6a3030', nose=0.82) + [
        ('rect', 0.0, 0.70, 1.0, 1.0, '#6b4428'), ('rect', 0.06, 0.60, 0.20, 0.72, '#6b4428'), ('rect', 0.80, 0.60, 0.94, 0.72, '#6b4428'),  # 턱수염
        ('rect', 0.30, 0.64, 0.70, 0.69, '#5a3820'), ('rect', 0.38, 0.75, 0.62, 0.79, '#7a3434'),                                          # 콧수염/입
        ('rect', 0.70, 0.30, 0.74, 0.50, '#c98f7a')]                                                                                     # 눈가 흉터
    H = humanoid(m, dict(s=1.0, leg_h=11, leg_w=4.6, tsize=(11, 11, 6.5), hsize=(9, 9.2, 9), asize=(4.4, 11),
                         pants='chain', boot='boot', torso='chain', belt='dleather', buckle='gold', skin='skin',
                         sleeve='chain', glove='leather', head='skin', face=fc, cuff='dleather', head_k=0.8))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td, hw, hh, hd = H['lh'], H['neck'], H['head_y'], H['tw'], H['td'], H['hw'], H['hh'], H['hd']
    # 짧은 머리 (윗머리 + 옆/뒤 짧게)
    hr = m.bone('hair', [0, hy, 0], head)
    cb(hr, 0, hy + hh - 1.4, 0.4, hw + 0.6, 2.0, hd + 0.4, 'hair')
    cb(hr, 0, hy + 3.0, hd / 2 - 0.6, hw + 0.6, hh - 3.6, 1.4, 'hair')
    for sx in (-1, 1):
        cb(hr, sx * (hw / 2 + 0.25), hy + 4.4, 0.8, 0.6, hh - 5.0, hd - 2.6, 'hair')
    cb(hr, -1.0, hy + hh - 1.8, -hd / 2 - 0.25, hw - 3.0, 1.0, 0.6, 'hair')       # 앞머리 살짝
    # 사슬 두건처럼 목 둘레 사슬 깃 (머리는 안 덮음)
    cb(body, 0, neck - 1.6, 0, tw + 1.2, 2.2, td + 1.2, 'dchain')
    # 팀색 서코트 (앞뒤 + 허리 아래로 늘어짐) + 가죽 벨트
    sc = m.bone('tc_surcoat', [0, lh + 2, 0], body)
    cb(sc, 0, lh - 5.0, -td / 2 - 0.35, tw - 1.0, neck - lh + 2.4, 0.6, 'tc',
       decals={'north': [('rect', 0.42, 0.18, 0.58, 0.62, '#d0d0d0'), ('rect', 0.22, 0.30, 0.78, 0.40, '#d0d0d0')]})
    cb(sc, 0, lh - 5.0, td / 2 + 0.35, tw - 1.0, neck - lh + 2.4, 0.6, 'tc')
    cb(body, 0, lh + 1.2, 0, tw + 1.0, 1.8, td + 1.4, 'dleather')
    cb(body, 0, lh + 1.0, -td / 2 - 0.9, 2.2, 2.2, 0.6, 'gold')
    cb(body, 3.2, lh - 1.2, -td / 2 - 0.8, 1.6, 3.0, 1.0, 'dleather')              # 칼집 고리
    # 가죽 어깨 보호대 (가볍게)
    for a, sx in ((ar, 1), (al, -1)):
        x = sx * (tw / 2 + 2.2)
        cb(a, x, neck - 3.4, 0, 5.6, 2.6, 5.6, 'leather')
        cb(a, x + sx * 0.3, neck - 4.6, 0, 5.2, 1.2, 5.2, 'dleather')
    # 장검 (오른손)
    hx, hyy, _ = H['hand_r']
    sw = m.bone('sword', [hx, hyy, 0], ar)
    cb(sw, hx, hyy - 1.0, 1.6, 1.8, 1.8, 1.4, 'gold')                  # 폼멜
    cb(sw, hx, hyy - 0.5, -0.9, 1.2, 1.2, 4.6, 'dleather')             # 손잡이 (두 손 길이)
    cb(sw, hx, hyy - 1.0, -3.6, 1.6, 2.2, 1.0, 'gold')                 # 날밑 가운데
    cb(sw, hx, hyy - 0.4, -3.6, 7.0, 1.0, 1.0, 'gold')                 # 날밑
    for sx in (-1, 1):
        cb(sw, hx + sx * 3.6, hyy - 0.6, -3.6, 1.2, 1.4, 1.2, 'gold')
    sw.box([hx - 0.4, hyy - 1.25, -20.0], [hx + 0.4, hyy + 1.25, -4.1], 'blade',
           decals={'east': [('rect', 0.0, 0.42, 1.0, 0.58, '#9aa3ab')], 'west': [('rect', 0.0, 0.42, 1.0, 0.58, '#9aa3ab')]})
    sw.box([hx - 0.3, hyy - 0.75, -21.6], [hx + 0.3, hyy + 0.75, -20.0], 'blade')
    sw.box([hx - 0.2, hyy - 0.3, -22.4], [hx + 0.2, hyy + 0.3, -21.6], 'blade')
    humanoid_anims(m, 'melee', atk=0.6, walk=0.8)
    m.hitbox(1.0, 2.1)
    return m


# =================================================================== GIANT (tank, buildings only)
def giant():
    m = Model('clash_giant')
    m.mats_({'skin': ('#d9a07c', 'skin'), 'leather': LEATHER, 'dleather': DLEATHER, 'iron': ('#6f7781', 'metal', {'rivets': True}),
             'tc': tc_cloth(), 'pants': ('#4b3a2c', 'cloth'), 'fur': ('#8a6b48', 'fur'), 'gold': GOLD, 'hair': ('#4a3a2a', 'hair'),
             'rope': ('#b99a62', 'rope'), 'helm': ('#7c858f', 'metal')})
    S = 1.55
    H = humanoid(m, dict(s=S, leg_h=10, leg_w=5.2, hip_w=13 * S, tsize=(14, 12, 8), hsize=(8.5, 8.5, 8.5), asize=(5.6, 13),
                         pants='pants', boot='dleather', torso='leather', belt='dleather', buckle='gold', skin='skin',
                         sleeve='skin', glove='iron', head='skin', head_dens=2.4,
                         face=face(eye='#2a2a2a', brow='#3b2b1d', beard='#4a3a2a', mouth='#5a2626', mustache='#3f3022')))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td = H['lh'], H['neck'], H['head_y'], H['tw'], H['td']
    # barrel chest + belly band (team)
    cb(body, 0, lh + 6, -td / 2 - 0.8, tw * 0.75, 9, 1.2, 'leather')
    band = m.bone('tc_sash', [0, lh + 4, 0], body)
    for i in range(5):
        y = lh + 3 + i * 3.4
        x = -tw / 2 + 2 + i * 4.2
        cb(band, x, y, -td / 2 - 1.6, 4.6, 3.4, 0.8, 'tc')
    # fur mantle over shoulders
    cb(body, 0, neck - 2.2, 0, tw * 0.62, 3.0, td + 1.6, 'fur')
    # iron cap with nose guard (simple, original)
    cb(head, 0, hy + 9.0, 0, 13.6, 4.5, 13.6, 'helm')
    cb(head, 0, hy + 8.4, 0, 14.4, 1.4, 14.4, 'iron')
    cb(head, 0, hy + 4.5, -6.9, 1.6, 5.4, 1.0, 'iron')
    # massive gauntlets and bracers
    for a, sx in ((ar, 1), (al, -1)):
        x = sx * (tw / 2 + H['aw'] / 2)
        cb(a, x, neck - H['ah'] - 1.5, 0, H['aw'] + 3, 7.5, H['aw'] + 3, 'iron')
        cb(a, x, neck - H['ah'] + 6, 0, H['aw'] + 1.6, 5, H['aw'] + 1.6, 'leather')
        cb(a, x, neck - 4.5, 0, H['aw'] + 2.4, 4.5, H['aw'] + 2.4, 'iron')                      # shoulder plate
        for k in (-1, 1):
            cb(a, x + k * 1.8, neck - H['ah'] - 2.2, -H['aw'] / 2 - 1.9, 1.2, 1.2, 1.2, 'gold')  # knuckle studs
    humanoid_anims(m, 'slam', atk=1.0, walk=1.3)
    m.hitbox(1.8, 3.2)
    return m


# =================================================================== MUSKETEER (ranged)
def musketeer():
    m = Model('clash_musketeer')
    m.mats_({'tc': tc_cloth(), 'coat': ('#3b3f4a', 'cloth'), 'leather': LEATHER, 'dleather': DLEATHER, 'skin': SKIN,
             'gold': GOLD, 'hat': ('#2a2b31', 'cloth'), 'wood': ('#7b4f2b', 'wood'), 'barrel': ('#4d5560', 'metal'),
             'shirt': ('#e9e2d2', 'cloth'), 'hair': ('#6b3f22', 'hair'), 'boot': ('#2b211b', 'leather'),
             'iron': ('#3d434a', 'metal', {'rivets': True}), 'spark': ('#ffb347', 'glow')})
    fc = face(eye='#2b3a55', brow='#3a2416', cheeks='#eea08e', mouth='#b84a50', eye_y=0.42) + [
        ('rect', 0.16, 0.38, 0.40, 0.42, '#1e1416'), ('rect', 0.60, 0.38, 0.84, 0.42, '#1e1416'),      # 속눈썹
        ('rect', 0.14, 0.40, 0.18, 0.46, '#1e1416'), ('rect', 0.82, 0.40, 0.86, 0.46, '#1e1416')]
    H = humanoid(m, dict(leg_h=11.5, leg_w=3.8, hip_w=9.2, tsize=(8.8, 10, 5.4), hsize=(8.6, 8.8, 8.6), asize=(3.5, 10.5),
                         pants='coat', boot='boot', torso='coat', belt='dleather', buckle='gold', skin='skin',
                         sleeve='coat', glove='leather', head='skin', cuff='gold', face=fc, head_k=0.82))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td = H['lh'], H['neck'], H['head_y'], H['tw'], H['td']
    # long team coat: tails + lapels
    coat = m.bone('tc_coat', [0, lh + 2, 0], body)
    cb(coat, 0, lh - 6, td / 2 + 0.6, tw + 2.0, 8.5, 0.8, 'tc')                   # 뒷자락 (치마처럼 퍼짐)
    cb(coat, -tw / 2 - 0.6, lh - 6, 0, 0.8, 8.5, td + 1.6, 'tc')
    cb(coat, tw / 2 + 0.6, lh - 6, 0, 0.8, 8.5, td + 1.6, 'tc')
    cb(coat, 0, lh + 2, 0, tw + 0.6, 9, td + 0.6, 'tc', decals={'north': [('rect', 0.38, 0.0, 0.62, 1.0, '#c9c9c9')]})
    cb(body, 0, lh + 6, -td / 2 - 0.6, 3, 5, 0.6, 'shirt')                        # cravat
    # bandolier
    for i in range(5):
        cb(body, -tw / 2 + 1.5 + i * 1.9, lh + 3 + i * 1.6, -td / 2 - 1.0, 2.2, 2.2, 0.6, 'dleather')
    # tricorn-style hat
    cb(head, 0, hy + 8.4, 0, 12.5, 1.2, 12.5, 'hat')
    cb(head, 0, hy + 9.4, 0, 9.4, 3.2, 9.4, 'hat')
    cb(head, 0, hy + 9.4, -6.0, 9.0, 2.2, 0.8, 'gold')
    plume = m.bone('tc_plume', [3, hy + 11, 0], head)
    cb(plume, 3.5, hy + 10.8, 2, 1.4, 1.6, 7, 'tc')
    cb(plume, 3.5, hy + 12.0, 4.5, 1.4, 1.6, 4, 'tc')
    hr = m.bone('hair', [0, hy, 0], head)                                          # 짙은 갈색 긴 머리
    cb(hr, 0, hy + 7.0, 0.4, 9.6, 1.8, 9.4, 'hair')
    cb(hr, 0, hy + 1.0, 3.6, 9.6, 6.6, 2.2, 'hair')
    for sx in (-1, 1):
        cb(hr, sx * 4.55, hy + 2.0, 0.2, 1.0, 5.8, 7.6, 'hair')
    cb(hr, -0.8, hy + 6.6, -4.6, 7.6, 1.4, 0.6, 'hair')
    tail = m.bone('ponytail', [0, hy + 5, 4.8], head)                              # 리본 묶은 긴 포니테일
    cb(tail, 0, hy + 4.4, 5.0, 2.4, 1.6, 1.4, 'tc')
    for k in range(4):
        cb(tail, 0, hy + 2.4 - k * 2.3, 5.4 + k * 0.35, 3.0 - k * 0.35, 2.4, 2.4 - k * 0.2, 'hair')
    # 손대포 (오른손으로 잡고 왼손으로 받침): 굵은 포신 + 쇠 띠 + 나팔 포구 + 심지
    hx, hyy, _ = H['hand_r']
    g = m.bone('rifle', [hx, hyy, 0], ar)
    gx, gy = hx - 0.6, hyy + 0.4                                                     # 몸 쪽으로 살짝
    cb(g, gx, gy - 3.4, 2.4, 2.4, 3.8, 5.2, 'wood')                                  # 개머리
    cb(g, gx, gy - 3.6, 4.9, 2.6, 4.2, 0.6, 'dleather')                              # 개머리 끝판
    cb(g, gx, gy - 1.6, -1.0, 2.2, 2.6, 3.0, 'wood')                                 # 손잡이 목
    cb(g, gx, gy - 2.6, -0.4, 0.6, 1.4, 1.4, 'iron')                                 # 방아쇠
    cb(g, gx, gy - 2.2, -3.4, 4.4, 4.4, 2.6, 'iron')                                 # 약실 덩어리
    cb(g, gx, gy - 1.6, -10.4, 3.4, 3.4, 11.6, 'barrel')                             # 포신
    for z in (-5.6, -9.6, -13.6):
        cb(g, gx, gy - 1.85, z, 3.9, 3.9, 1.0, 'gold')                               # 쇠 띠
    cb(g, gx, gy - 2.5, -17.0, 4.8, 4.8, 1.6, 'iron',
       decals={'north': [('rect', 0.22, 0.22, 0.78, 0.78, '#111316'), ('rect', 0.3, 0.3, 0.7, 0.7, '#070809')]})   # 나팔 포구
    cb(g, gx, gy - 2.1, -15.8, 4.0, 4.0, 1.0, 'iron')
    cb(g, gx, gy - 4.4, -8.0, 2.0, 1.6, 4.4, 'wood')                                 # 앞 손받침
    cb(g, gx, gy + 0.4, -3.0, 0.8, 1.2, 0.8, 'iron')                                 # 점화구
    cb(g, gx, gy + 1.6, -3.0, 0.3, 1.4, 0.3, 'shirt', noround=True)                   # 심지
    cb(g, gx, gy + 3.0, -3.0, 0.7, 0.7, 0.7, 'spark', noround=True)                  # 불똥
    cb(g, gx, gy + 1.8, -9.0, 1.2, 0.8, 3.0, 'iron')                                 # 위 손잡이 고리
    m.scale_bone('rifle', 1.3, [hx, hyy, 0])                                          # 대포 크게
    humanoid_anims(m, 'ranged', atk=0.8, walk=0.8)
    # 손대포는 허리에 대고 쏨: 조준 → 쾅 (반동으로 뒤로 밀림)
    m.anims = [a for a in m.anims if a['name'] != 'attack']
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': [(0, (0, 0, 0)), (0.25, (-14, 0, 4)), (0.42, (-14, 0, 4)), (0.47, (12, 0, 4)), (0.8, (0, 0, 0))]},
        'arm_l': {'rotation': [(0, (0, 0, 0)), (0.25, (-38, -30, 0)), (0.42, (-38, -30, 0)), (0.47, (-20, -30, 0)), (0.8, (0, 0, 0))]},
        'rifle': {'position': [(0, (0, 0, 0)), (0.42, (0, 0, 0)), (0.47, (0, 0.6, 2.2)), (0.8, (0, 0, 0))]},
        'body': {'rotation': [(0, (0, 0, 0)), (0.25, (6, 10, 0)), (0.42, (6, 10, 0)), (0.47, (-8, 10, 0)), (0.8, (0, 0, 0))],
                 'position': [(0, (0, 0, 0)), (0.42, (0, 0, 0)), (0.47, (0, 0, 1.5)), (0.8, (0, 0, 0))]},
        'head': {'rotation': [(0, (0, 0, 0)), (0.25, (6, -10, 0)), (0.47, (-4, -10, 0)), (0.8, (0, 0, 0))]}})
    m.hitbox(0.9, 2.0)
    return m


# =================================================================== ARCHER
def archer():
    """여자 궁수: 적갈색 단발 + 뒤로 땋은 머리, 팀색 조끼/치마, 활은 왼손 (쏠 때 세워서 당김)"""
    m = Model('clash_archer')
    m.mats_({'tc': tc_cloth(), 'leather': LEATHER, 'dleather': DLEATHER, 'skin': ('#f1c9aa', 'skin'),
             'wood': ('#8a5a2e', 'wood', {'grain': 'v'}), 'dwood': ('#5e3b1c', 'wood', {'grain': 'v'}), 'string': ('#efe8d0', 'plain'),
             'pants': ('#3b2f3a', 'cloth'), 'feather': ('#f2f2f2', 'cloth'), 'iron': ('#9aa2ab', 'metal'), 'gold': GOLD,
             'hair': ('#8a3b1e', 'hair'), 'hair2': ('#5e2412', 'hair'), 'boot': ('#4a3324', 'leather'),
             'blouse': ('#ece4d2', 'cloth')})
    fc = face(eye='#2f4a2a', brow='#5e2412', cheeks='#f0a090', mouth='#b8505a', eye_y=0.42)
    fc += [('rect', 0.16, 0.38, 0.40, 0.42, '#2a1a2a'), ('rect', 0.60, 0.38, 0.84, 0.42, '#2a1a2a'),     # 속눈썹
           ('rect', 0.14, 0.40, 0.18, 0.46, '#2a1a2a'), ('rect', 0.82, 0.40, 0.86, 0.46, '#2a1a2a')]
    H = humanoid(m, dict(leg_h=11.5, leg_w=3.7, hip_w=9.0, tsize=(8.4, 9.5, 5.0), hsize=(8.4, 8.6, 8.4), asize=(3.3, 10),
                         pants='pants', boot='boot', torso='blouse', belt='dleather', buckle='gold', skin='skin',
                         sleeve='blouse', glove='leather', head='skin', face=fc, head_k=0.82))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td, hw, hh, hd = H['lh'], H['neck'], H['head_y'], H['tw'], H['td'], H['hw'], H['hh'], H['hd']
    # ── 진분홍 단발 (윗머리 + 옆/뒤는 턱선까지 + 끝이 살짝 퍼짐 + 앞머리)
    hr = m.bone('hair', [0, hy, 0], head)
    cb(hr, 0, hy + hh - 1.2, 0.3, hw + 1.0, 2.4, hd + 0.9, 'hair')                 # 윗머리
    cb(hr, 0, hy + 1.2, hd / 2 - 1.6, hw + 1.0, hh - 1.4, 3.6, 'hair')             # 뒷머리
    for sx in (-1, 1):
        cb(hr, sx * (hw / 2 + 0.45), hy + 1.0, -0.4, 1.0, hh - 1.2, hd - 0.6, 'hair')    # 옆머리
        cb(hr, sx * (hw / 2 + 0.75), hy + 0.6, 0.4, 1.0, 1.8, hd - 1.6, 'hair2')         # 끝 퍼짐
    cb(hr, 0, hy + 0.6, hd / 2 + 0.3, hw + 1.6, 1.8, 1.2, 'hair2')
    cb(hr, -0.6, hy + hh - 2.2, -hd / 2 - 0.35, hw - 0.4, 1.6, 0.7, 'hair')        # 앞머리
    cb(hr, -2.4, hy + hh - 3.2, -hd / 2 - 0.35, 2.6, 1.2, 0.6, 'hair')            # 옆으로 넘긴 앞머리
    cb(hr, hw / 2 - 1.0, hy + hh - 3.0, -hd / 2 - 0.3, 1.2, 1.8, 0.6, 'hair')
    rib = m.bone('tc_ribbon', [hw / 2, hy + hh - 2, 1], head)                        # 팀색 머리띠 리본
    cb(rib, hw / 2 + 0.9, hy + hh - 3.0, 1.2, 0.8, 1.6, 2.6, 'tc')
    cb(rib, hw / 2 + 1.0, hy + hh - 2.6, 1.2, 0.6, 0.8, 0.8, 'gold')
    # ── 몸: 가죽 코르셋 + 튜닉 치마 (아래로 퍼짐) + 짧은 망토 + 왼쪽 어깨 보호대 + 팔 보호대
    vest = m.bone('tc_vest', [0, lh + 4, 0], body)                                   # 팀색 조끼 (블라우스 위)
    cb(vest, 0, lh + 2.0, 0, tw + 0.35, H['th'] - 4.2, td + 0.35, 'tc')
    for sx in (-1, 1):
        cb(vest, sx * (tw / 2 - 1.3), lh + H['th'] - 2.4, 0, 2.2, 2.4, td + 0.35, 'tc')    # 어깨끈
    cb(body, 0, lh + 1.0, 0, tw + 0.6, 3.6, td + 0.6, 'dleather')                   # 코르셋 벨트
    sk = m.bone('tc_skirt', [0, lh, 0], body)
    cb(sk, 0, lh - 3.2, 0, tw + 1.2, 3.4, td + 1.2, 'tc')
    cb(sk, 0, lh - 4.4, 0, tw + 2.4, 1.6, td + 2.2, 'tc')
    # 뒤로 땋아 내린 머리
    br = m.bone('braid', [0, hy + 1, hd / 2 + 0.6], head)
    for k in range(4):
        cb(br, (k % 2) * 0.4 - 0.2, hy + 0.6 - k * 2.0, hd / 2 + 1.0 + k * 0.25, 2.2 - k * 0.2, 2.0, 2.0 - k * 0.15, 'hair' if k % 2 == 0 else 'hair2')
    cb(br, 0, hy - 7.6, hd / 2 + 1.9, 1.2, 0.8, 1.2, 'leather')
    cb(al, -(tw / 2 + 1.8), neck - 3.0, 0, 4.4, 2.6, 4.2, 'leather')                # 어깨 보호대
    cb(al, -(tw / 2 + 1.65), neck - 8.4, 0, 3.9, 2.8, 3.9, 'dleather')               # 팔 보호대
    # ── 등 화살통 + 화살
    q = m.bone('quiver', [2, lh + 6, td / 2 + 2], body)
    q.box([0.5, lh + 3, td / 2 + 1.2], [4, lh + 12, td / 2 + 4.2], 'dleather', rot=('z', -22.5), rot_origin=[2, lh + 7, td / 2 + 2])
    q.box([0.3, lh + 11.2, td / 2 + 1.0], [4.2, lh + 12.2, td / 2 + 4.4], 'gold', rot=('z', -22.5), rot_origin=[2, lh + 7, td / 2 + 2])
    for i, dx in enumerate((1.0, 2.0, 3.0, 3.6)):
        q.box([dx, lh + 12, td / 2 + 2 + (i % 2) * 0.8], [dx + 0.6, lh + 15.5, td / 2 + 2.6 + (i % 2) * 0.8], 'feather', rot=('z', -22.5), rot_origin=[2, lh + 7, td / 2 + 2])
    # ── 활: 왼손, 세로. 등(나무)이 앞(-z), 시위가 뒤. 끝이 앞으로 휘는 리커브
    hx, hyy, _ = H['hand_l']
    bow = m.bone('bow', [hx, hyy, 0], al)
    x, z0 = hx, -1.6
    cb(bow, x, hyy - 1.6, z0, 1.4, 3.2, 1.6, 'leather')                            # 손잡이
    for sy in (1, -1):
        y = hyy if sy > 0 else hyy - 1.6
        segs = [(0.0, 4.2, 0.0, 1.2), (4.2, 3.6, 0.6, 1.1), (7.8, 3.0, 1.5, 1.0), (10.8, 2.0, 2.4, 0.9), (12.8, 1.4, 2.0, 0.8)]
        for off, ln, dz, wd in segs:
            yy = y + off if sy > 0 else y - off - ln
            cb(bow, x, yy, z0 - 0.2 + dz, wd, ln, wd, 'wood' if off < 12 else 'dwood')
    cb(bow, x, hyy - 1.6 - 14.2, z0 + 2.6, 0.3, 14.2 * 2 + 1.6, 0.3, 'string', noround=True)
    # 애니메이션: 대기/걷기/쏘기 (쏠 때 왼팔 앞으로 → 활 세워 유지, 오른팔이 시위 당겼다 놓기)
    A = 0.9
    m.anim('idle', 2.0, 'loop', {
        'body': {'position': [(0, (0, 0, 0)), (1.0, (0, -0.35, 0)), (2.0, (0, 0, 0))]},
        'arm_l': {'rotation': [(0, (-12, 0, -4)), (1.0, (-16, 0, -6)), (2.0, (-12, 0, -4))]},
        'arm_r': {'rotation': [(0, (0, 0, 3)), (1.0, (-3, 0, 5)), (2.0, (0, 0, 3))]},
        'head': {'rotation': [(0, (0, 0, 0)), (1.0, (2, 6, 0)), (2.0, (0, 0, 0))]},
        'braid': {'rotation': [(0, (0, 0, 0)), (1.0, (-4, 0, 2)), (2.0, (0, 0, 0))]}})
    q4 = 0.7 / 4
    m.anim('walk', 0.7, 'loop', {
        'leg_r': {'rotation': [(0, (0, 0, 0)), (q4, (-28, 0, 0)), (2 * q4, (0, 0, 0)), (3 * q4, (28, 0, 0)), (0.7, (0, 0, 0))]},
        'leg_l': {'rotation': [(0, (0, 0, 0)), (q4, (28, 0, 0)), (2 * q4, (0, 0, 0)), (3 * q4, (-28, 0, 0)), (0.7, (0, 0, 0))]},
        'arm_r': {'rotation': [(0, (0, 0, 0)), (q4, (24, 0, 0)), (2 * q4, (0, 0, 0)), (3 * q4, (-24, 0, 0)), (0.7, (0, 0, 0))]},
        'arm_l': {'rotation': [(0, (-15, 0, -4)), (q4, (-25, 0, -4)), (2 * q4, (-15, 0, -4)), (3 * q4, (-5, 0, -4)), (0.7, (-15, 0, -4))]},
        'body': {'position': [(0, (0, 0, 0)), (q4, (0, 0.6, 0)), (2 * q4, (0, 0, 0)), (3 * q4, (0, 0.6, 0)), (0.7, (0, 0, 0))]},
        'braid': {'rotation': [(0, (0, 0, 0)), (q4, (-10, 0, 4)), (2 * q4, (0, 0, 0)), (3 * q4, (-10, 0, -4)), (0.7, (0, 0, 0))]},
        'tc_skirt': {'rotation': [(0, (0, 0, 0)), (q4, (4, 0, 0)), (2 * q4, (0, 0, 0)), (3 * q4, (-4, 0, 0)), (0.7, (0, 0, 0))]}})
    m.anim('attack', A, 'once', {
        'body': {'rotation': [(0, (0, 0, 0)), (0.2, (0, -25, 0)), (0.75, (0, -25, 0)), (A, (0, 0, 0))]},
        'head': {'rotation': [(0, (0, 0, 0)), (0.2, (0, 22, 0)), (0.75, (0, 22, 0)), (A, (0, 0, 0))]},
        'arm_l': {'rotation': [(0, (0, 0, 0)), (0.2, (-90, 25, 0)), (0.75, (-90, 25, 0)), (A, (0, 0, 0))]},
        'bow': {'rotation': [(0, (0, 0, 0)), (0.2, (90, 0, 0)), (0.75, (90, 0, 0)), (A, (0, 0, 0))]},
        'arm_r': {'rotation': [(0, (0, 0, 0)), (0.2, (-95, 25, 0)), (0.6, (-90, -35, 0)), (0.66, (-90, -55, 10)), (0.8, (-40, -20, 0)), (A, (0, 0, 0))]}})
    common_anims(m)
    m.hitbox(0.8, 1.8)
    return m


# =================================================================== ELECTRO MAGE (stun caster)
def electro_wizard():
    m = Model('clash_electro_wizard')
    m.mats_({'tc': tc_cloth(), 'robe': ('#283246', 'cloth'), 'copper': ('#c7773d', 'metal'), 'dleather': DLEATHER,
             'glow': ('#6fe9ff', 'glow'), 'core': ('#e8fdff', 'glow'), 'skin': SKIN, 'gold': GOLD, 'boot': ('#1d2230', 'leather'),
             'inner': ('#15171d', 'plain'), 'hair': ('#1c1e25', 'soft'), 'hair2': ('#2c3445', 'soft'), 'brass': ('#b8893a', 'metal'),
             'lens': ('#9fe9ff', 'gem')})
    crazy = [('rect', 0.14, 0.36, 0.42, 0.56, '#ffffff'), ('rect', 0.58, 0.34, 0.86, 0.58, '#ffffff'),        # 짝짝이 눈
             ('rect', 0.22, 0.40, 0.34, 0.52, '#33d6ff'), ('rect', 0.66, 0.40, 0.80, 0.54, '#33d6ff'),
             ('rect', 0.26, 0.44, 0.30, 0.48, '#ffffff'), ('rect', 0.71, 0.44, 0.75, 0.48, '#ffffff'),
             ('rect', 0.10, 0.24, 0.44, 0.30, '#16171c'), ('rect', 0.56, 0.20, 0.90, 0.26, '#16171c'),        # 삐친 눈썹
             ('rect', 0.38, 0.30, 0.44, 0.34, '#16171c'), ('rect', 0.84, 0.26, 0.90, 0.32, '#16171c'),
             ('shade', 0.45, 0.56, 0.55, 0.70, 0.84),
             ('rect', 0.26, 0.74, 0.74, 0.86, '#3a1a1a'), ('rect', 0.28, 0.74, 0.72, 0.79, '#ffffff'),         # 이 드러낸 웃음
             ('rect', 0.38, 0.74, 0.40, 0.79, '#bbbbbb'), ('rect', 0.50, 0.74, 0.52, 0.79, '#bbbbbb'), ('rect', 0.62, 0.74, 0.64, 0.79, '#bbbbbb'),
             ('rect', 0.22, 0.70, 0.28, 0.76, '#3a1a1a'), ('rect', 0.72, 0.70, 0.78, 0.76, '#3a1a1a'),
             ('rect', 0.44, 0.88, 0.56, 1.0, '#1c1e25')]                                                        # 꼬불 염소수염
    H = humanoid(m, dict(leg_h=11, leg_w=4.2, tsize=(9.5, 11.5, 6), hsize=(8.6, 8.8, 8.6), asize=(4, 11),
                         pants='robe', boot='boot', torso='robe', belt='copper', buckle='glow', skin='skin',
                         sleeve='robe', glove='copper', head='skin', face=crazy, head_k=0.84))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td = H['lh'], H['neck'], H['head_y'], H['tw'], H['td']
    # team mantle + long skirt panels
    mant = m.bone('tc_mantle', [0, neck, 0], body)
    cb(mant, 0, neck - 4, 0, tw + 2.5, 4, td + 2.5, 'tc')
    cb(mant, 0, lh - 7, -td / 2 - 0.3, 5, 9.5, 0.6, 'tc', decals={'north': [('rect', 0.35, 0.1, 0.65, 0.2, '#bbbbbb')]})
    cb(mant, 0, lh - 7, td / 2 + 0.3, tw + 0.8, 9.5, 0.6, 'tc')
    # chest rune (lightning bolt)
    cb(body, 0, lh + 4, -td / 2 - 0.3, 4, 6, 0.4, 'glow',
       decals={'north': [('rect', 0.0, 0.0, 1.0, 1.0, '#283246'), ('rect', 0.45, 0.0, 0.75, 0.4, '#8ff6ff'),
                         ('rect', 0.25, 0.35, 0.75, 0.55, '#8ff6ff'), ('rect', 0.25, 0.5, 0.55, 1.0, '#8ff6ff')]})
    hw, hh, hd = H['hw'], H['hh'], H['hd']
    # ── 하늘로 삐쭉 솟은 전기 머리 (가운데는 높게, 바깥은 비스듬히) + 머리카락 사이 불꽃
    hr = m.bone('hair', [0, hy + hh, 0], head)
    cb(hr, 0, hy + hh - 1.6, 0.6, hw + 0.8, 2.4, hd + 0.6, 'hair')                       # 머리 바탕
    cb(hr, 0, hy + 2.4, hd / 2 - 0.4, hw + 0.8, hh - 3.6, 1.6, 'hair')                    # 뒷머리
    for sx in (-1, 1):
        cb(hr, sx * (hw / 2 + 0.3), hy + 4.4, 0.8, 0.8, hh - 5.2, hd - 3.0, 'hair')         # 옆머리 (귀 위)
    spikes = [  # x, z, 높이, 굵기, (축, 각도)
        (0.0, 0.0, 9.0, 2.0, None), (-2.4, -1.6, 7.0, 1.7, ('z', 22.5)), (2.4, -1.6, 7.4, 1.7, ('z', -22.5)),
        (-2.2, 2.2, 7.6, 1.7, ('x', -22.5)), (2.2, 2.2, 7.2, 1.7, ('x', -22.5)), (0.0, -3.0, 6.0, 1.6, ('x', 22.5)),
        (-4.2, 0.4, 5.8, 1.5, ('z', 45)), (4.2, 0.4, 6.0, 1.5, ('z', -45)), (0.0, 3.6, 6.4, 1.6, ('x', -45)),
        (-3.6, 3.2, 5.0, 1.4, ('x', -45)), (3.6, -3.0, 5.0, 1.4, ('z', -45))]
    for k, (x, z, ln, w, rot) in enumerate(spikes):
        y0 = hy + hh + 0.4
        mat = 'hair' if k % 3 else 'hair2'
        w = w * 1.45
        hr.box([x - w / 2, y0, z - w / 2], [x + w / 2, y0 + ln * 0.55, z + w / 2], mat, rot=rot, rot_origin=[x, y0, z], noround=True)
        hr.box([x - w * 0.32, y0 + ln * 0.55, z - w * 0.32], [x + w * 0.32, y0 + ln * 0.9, z + w * 0.32], 'hair2', rot=rot, rot_origin=[x, y0, z], noround=True)
        hr.box([x - w * 0.15, y0 + ln * 0.9, z - w * 0.15], [x + w * 0.15, y0 + ln * 1.05, z + w * 0.15], 'glow', rot=rot, rot_origin=[x, y0, z], noround=True)   # 끝에 전기
    sp = m.bone('sparks', [0, hy + hh + 4, 0], head)                                        # 파지직 불꽃
    for (x, y, z) in ((-1.4, 6.0, -0.4), (1.6, 4.6, 1.0), (-0.2, 9.4, 1.4), (3.2, 3.2, -2.0), (-3.0, 3.6, 1.8)):
        cb(sp, x, hy + hh + y, z, 0.8, 0.8, 0.8, 'core', noround=True)
        cb(sp, x + 0.6, hy + hh + y + 0.6, z, 0.5, 1.2, 0.5, 'glow', noround=True)
    # ── 이마 위 동그란 놋쇠 고글
    gz = -hd / 2
    cb(head, 0, hy + hh - 0.9, 0, hw + 0.5, 0.9, hd + 0.5, 'dleather')
    for sx in (-1, 1):
        cb(head, sx * 2.0, hy + hh - 1.3, gz - 0.6, 3.0, 2.8, 1.2, 'brass')
        cb(head, sx * 2.0, hy + hh - 1.0, gz - 1.25, 2.0, 2.0, 0.3, 'lens', noround=True)
    cb(head, 0, hy + hh - 0.6, gz - 0.7, 1.2, 0.8, 0.8, 'brass')
    # 높은 깃 (실험 가운 느낌)
    for sx in (-1, 1):
        cb(body, sx * 3.0, neck - 1.2, -0.4, 2.2, 3.4, td + 0.8, 'tc' if False else 'robe')
    # copper coil bracers + floating crackling shards in both hands
    for a, side, sx in ((ar, 'r', 1), (al, 'l', -1)):
        x = sx * (tw / 2 + H['aw'] / 2)
        for k in range(3):
            cb(a, x, neck - H['ah'] + 3.8 + k * 1.6, 0, H['aw'] + 1.2, 0.8, H['aw'] + 1.2, 'copper')
        hx, hyy, _ = H['hand_' + side]
        o = m.bone('orb_' + side, [hx, hyy - 4, -2], a)
        cb(o, hx, hyy - 6.6, -2, 3.6, 3.6, 3.6, 'core')
        for (dx, dy, dz, w, h) in ((2.6, 0.4, -0.6, 1.0, 4.2), (-2.6, -1.2, 0.4, 1.0, 3.6), (0.2, 2.2, -2.6, 1.0, 3.8), (0.0, -3.6, 2.2, 1.0, 3.2)):
            o.box([hx + dx - w / 2, hyy - 6 + dy, -2 + dz - w / 2], [hx + dx + w / 2, hyy - 6 + dy + h, -2 + dz + w / 2], 'glow',
                  rot=('z', 22.5 * (1 if dx >= 0 else -1)), rot_origin=[hx + dx, hyy - 6 + dy, -2 + dz])
    humanoid_anims(m, 'cast', atk=0.7, walk=0.85)
    # orbiting shards in idle (override idle with extra tracks)
    idle = next(a for a in m.anims if a['name'] == 'idle')
    for side in ('r', 'l'):
        idle['tracks']['orb_' + side] = {'rotation': [(0, (0, 0, 0)), (1.0, (0, 180, 0)), (2.0, (0, 360, 0))],
                                         'position': [(0, (0, 0, 0)), (1.0, (0, 0.8, 0)), (2.0, (0, 0, 0))]}
    # 머리카락 파지직 떨림 + 불꽃 깜빡
    idle['tracks']['hair'] = {'scale': [(0, (1, 1, 1)), (0.2, (1.04, 1.08, 1.04)), (0.3, (0.98, 0.97, 0.98)), (0.9, (1, 1, 1)),
                                        (1.1, (1.05, 1.1, 1.05)), (1.2, (1, 1, 1)), (2.0, (1, 1, 1))]}
    idle['tracks']['sparks'] = {'scale': [(0, (1, 1, 1)), (0.15, (0.2, 0.2, 0.2)), (0.4, (1.2, 1.2, 1.2)), (0.7, (0.3, 0.3, 0.3)),
                                          (1.0, (1, 1, 1)), (1.3, (0.2, 0.2, 0.2)), (1.6, (1.1, 1.1, 1.1)), (2.0, (1, 1, 1))],
                                'rotation': [(0, (0, 0, 0)), (2.0, (0, 360, 0))]}
    atk = next(a for a in m.anims if a['name'] == 'attack')
    atk['tracks']['hair'] = {'scale': [(0, (1, 1, 1)), (0.3, (1.12, 1.25, 1.12)), (0.45, (1.0, 1.0, 1.0)), (0.7, (1, 1, 1))]}
    m.hitbox(0.9, 2.1)
    return m


# =================================================================== MINER (tunneller)
def miner():
    m = Model('clash_miner')
    m.mats_({'tc': tc_cloth(), 'overall': ('#5c4a35', 'cloth'), 'leather': LEATHER, 'dleather': DLEATHER, 'skin': SKIN,
             'hat': ('#8e959e', 'metal'), 'hat2': ('#5f656d', 'metal', {'rivets': True}), 'lamp': ('#fff4b0', 'glow'),
             'iron': ('#6f7882', 'metal'), 'iron2': ('#3d434a', 'metal', {'rivets': True}), 'steel': ('#c3cad3', 'metal'),
             'wood': ('#80562f', 'wood', {'grain': 'v'}), 'grip': ('#4a2f1c', 'leather'),
             'beard': ('#8a5a33', 'hair'), 'glass': ('#7fb6c9', 'gem'), 'sack': ('#a68b62', 'cloth'), 'dirt': ('#6e5338', 'stone')})
    H = humanoid(m, dict(leg_h=9.5, leg_w=4.8, tsize=(11, 10, 7), hsize=(8.0, 7.6, 8.0), asize=(4.6, 10), head_k=0.95,
                         pants='overall', boot='dleather', torso='tc', belt='dleather', buckle='iron', skin='skin',
                         sleeve='tc', glove='leather', head='skin', knee='dirt',
                         face=face(eye='#2a2a2a', brow='#6a4326', mouth='#6a3a30', nose=0.8) +
                              [('rect', 0.08, 0.66, 0.24, 0.74, '#9c7a5a'), ('rect', 0.74, 0.58, 0.86, 0.64, '#9c7a5a'),   # 볼에 흙
                               ('rect', 0.30, 0.12, 0.44, 0.18, '#9c7a5a')]))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td = H['lh'], H['neck'], H['head_y'], H['tw'], H['td']
    HH, HD = 7.6, 8.0
    shirt = m.bone('tc_shirt', [0, lh + 4, 0], body)
    cb(shirt, 0, lh + 2.2, 0, tw + 0.3, neck - lh - 2.2, td + 0.3, 'tc')
    for a, sx in ((ar, 1), (al, -1)):
        sl = m.bone('tc_sleeve_' + ('r' if sx > 0 else 'l'), [sx * (tw / 2 + 2.3), neck - 1, 0], a)
        cb(sl, sx * (tw / 2 + 2.3), neck - 5.5, 0, 4.9, 5.5, 4.9, 'tc')
    # 멜빵 작업복
    cb(body, 0, lh + 2, -td / 2 - 0.4, 7, 5.5, 0.6, 'overall')
    for sx in (-1, 1):
        cb(body, sx * 2.6, lh + 7, -td / 2 - 0.4, 1.4, neck - lh - 7, 0.6, 'overall')
        cb(body, sx * 2.6, lh + 6.6, -td / 2 - 0.8, 1.2, 1.2, 0.6, 'iron')
    # ── 큰 회색 안전모 (머리 위에 푹 눌러씀)
    top = hy + HH
    cb(head, 0, top - 1.5, 0, 13.2, 1.0, 13.2, 'hat')                 # 넓은 챙
    cb(head, 0, top - 1.6, 0, 13.4, 0.35, 13.4, 'hat2')              # 챙 테두리
    cb(head, 0, top - 0.5, 0, 10.2, 3.4, 10.2, 'hat')                 # 아래 돔
    cb(head, 0, top + 2.9, 0, 8.6, 1.8, 8.6, 'hat')                   # 위 돔
    cb(head, 0, top + 4.7, 0, 6.2, 0.8, 6.2, 'hat')
    cb(head, 0, top + 4.6, 0, 1.6, 1.2, 10.8, 'hat2')                 # 가운데 등줄
    cb(head, 0, top - 0.5, 0, 10.4, 0.7, 10.4, 'hat2')                # 띠
    # ── 헤드라이트 (앞)
    cb(head, 0, top - 0.2, -5.25, 4.6, 4.0, 0.6, 'iron2')             # 받침판
    cb(head, 0, top + 0.1, -6.0, 3.8, 3.4, 1.2, 'iron2')              # 등 몸통
    cb(head, 0, top + 0.1, -6.75, 4.2, 3.8, 0.4, 'iron')              # 테두리
    cb(head, 0, top + 0.4, -7.0, 2.8, 2.8, 0.3, 'lamp')               # 렌즈 (빛남)
    for sx in (-1, 1):
        cb(head, sx * 2.6, top + 1.3, -5.8, 0.6, 0.6, 0.6, 'steel')   # 나사
    cb(head, 0, top - 1.0, -4.3, 1.0, 1.2, 0.6, 'dleather')
    # ── 고글 (이마 위)
    cb(head, 0, top - 2.6, -HD / 2 - 0.15, 8.4, 0.9, 0.4, 'dleather')
    for sx in (-1, 1):
        cb(head, sx * 1.9, top - 3.1, -HD / 2 - 0.5, 2.6, 1.9, 0.8, 'iron')
        cb(head, sx * 1.9, top - 2.85, -HD / 2 - 0.95, 1.8, 1.3, 0.25, 'glass')
    # ── 곡괭이 (오른손): 손잡이 + 가죽 감개 + 쇠고리 + 휘어진 곡괭이 머리
    hx, hyy, _ = H['hand_r']
    p = m.bone('pickaxe', [hx, hyy, 0], ar)
    cb(p, hx, hyy - 0.75, -6.5, 1.4, 1.4, 17, 'wood')                 # 손잡이 (z 2 → -15)
    cb(p, hx, hyy - 0.95, 2.3, 2.0, 1.8, 1.0, 'iron2')                # 끝 마개
    for z in (0.6, -1.4, -3.4):
        cb(p, hx, hyy - 0.95, z, 1.8, 1.8, 1.1, 'grip')               # 가죽 감개
    cb(p, hx, hyy - 1.1, -13.8, 2.6, 2.6, 3.4, 'iron2')               # 머리 고리
    for sx in (-1, 1):
        cb(p, hx + sx * 1.35, hyy, -13.8, 0.3, 0.6, 0.6, 'steel')     # 리벳
    # 위쪽: 뾰족 (앞으로 살짝 휨)
    cb(p, hx, hyy + 0.9, -13.8, 2.0, 2.4, 2.2, 'iron')
    cb(p, hx, hyy + 3.2, -13.4, 1.6, 2.4, 1.8, 'iron')         # 날은 손잡이(손) 쪽으로 휨
    cb(p, hx, hyy + 5.4, -12.8, 1.2, 2.2, 1.3, 'iron')
    cb(p, hx, hyy + 7.4, -12.1, 0.8, 1.8, 0.9, 'steel')
    cb(p, hx, hyy + 9.0, -11.5, 0.4, 1.2, 0.5, 'steel')
    # 아래쪽: 넓적 끌
    cb(p, hx, hyy - 4.9, -13.8, 2.0, 2.4, 2.2, 'iron')
    cb(p, hx, hyy - 7.1, -13.4, 1.7, 2.2, 1.8, 'iron')
    cb(p, hx, hyy - 8.9, -12.9, 2.8, 1.5, 1.3, 'steel')
    cb(p, hx, hyy - 9.9, -12.5, 3.2, 0.8, 0.9, 'steel')
    # 등 자루
    cb(body, 0, lh + 1.5, td / 2 + 2.2, 7.5, 8, 4.4, 'sack')
    cb(body, 0, lh + 9.5, td / 2 + 2.2, 3, 1.6, 2.4, 'dleather')
    # 흙 묻은 옷/장비: 얼룩 무늬
    import random as _r
    rng = _r.Random(11)
    dirty = {'overall', 'tc', 'sack', 'dleather', 'leather', 'hat', 'skin'}
    for b in m.bones:
        for c in b.cubes:
            if c['mat'] not in dirty or b.name == 'head' and c['mat'] == 'skin':
                continue
            for f in ('north', 'south', 'east', 'west', 'up'):
                n = rng.randint(1, 3) if c['mat'] != 'hat' else rng.randint(0, 2)
                spots = []
                for _ in range(n):
                    x, y = rng.random() * 0.8, rng.random() * 0.8 + (0.15 if f != 'up' else 0)
                    w, h = 0.12 + rng.random() * 0.25, 0.08 + rng.random() * 0.18
                    spots.append(('rect', x, min(y, 0.9), min(1, x + w), min(1, y + h), rng.choice(['#5b4632', '#6e5338', '#4a3826'])))
                    if rng.random() < 0.5:
                        spots.append(('rect', x + w * 0.3, min(0.98, y + h), min(1, x + w * 0.6), min(1, y + h + 0.08), '#5b4632'))
                c['decals'] = dict(c['decals'], **{f: c['decals'].get(f, []) + spots})
    humanoid_anims(m, 'melee', atk=0.65, walk=0.75)
    # emerge-from-ground spawn
    m.anims = [a for a in m.anims if a['name'] != 'spawn']
    m.anim('spawn', 0.9, 'once', {
        'root': {'position': [(0, (0, -30, 0)), (0.55, (0, 3, 0)), (0.75, (0, -0.5, 0)), (0.9, (0, 0, 0))],
                 'rotation': [(0, (0, 0, 0)), (0.55, (0, 360, 0)), (0.9, (0, 360, 0))]},
        'arm_r': {'rotation': [(0, (-170, 0, 0)), (0.55, (-170, 0, 0)), (0.9, (0, 0, 0))]}})
    m.hitbox(1.0, 1.8)
    return m


# =================================================================== GOBLIN (fast, cheap)
def goblin():
    m = Model('clash_goblin')
    m.mats_({'tc': tc_cloth(), 'skin': ('#7fb14a', 'skin'), 'dskin': ('#5f8f37', 'skin'), 'leather': LEATHER,
             'dleather': DLEATHER, 'iron': ('#a4acb5', 'metal'), 'rag': ('#6c5640', 'cloth'), 'gold': GOLD})
    S = 0.68
    H = humanoid(m, dict(s=S, leg_h=9, leg_w=4.6, tsize=(10, 9, 6.5), hsize=(12, 10.5, 11), asize=(4.2, 10),
                         pants='rag', boot='dleather', torso='rag', belt='dleather', buckle='gold', skin='skin',
                         sleeve='skin', glove='dskin', head='skin', head_dens=2.2,
                         face=face(eye='#c62d1f', white='#f6e46a', brow='#3d5a20', mouth='#3b1d16', nose=0.78, wide=True,
                                   eye_y=0.30) + [('rect', 0.38, 0.79, 0.44, 0.86, '#f4f0dc'), ('rect', 0.56, 0.79, 0.62, 0.86, '#f4f0dc')]))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td, hw, hh = H['lh'], H['neck'], H['head_y'], H['tw'], H['td'], H['hw'], H['hh']
    # long pointed ears (stepped outward + up)
    for sx in (-1, 1):
        x = sx * (hw / 2)
        ey = hy + hh * 0.5
        for k, (ln, hgt, up) in enumerate(((2.2, 2.6, 0.0), (2.0, 1.8, 0.9), (1.8, 1.0, 1.8))):
            x0 = x + sx * (k * 2.0)
            x1 = x0 + sx * ln
            head.box([min(x0, x1), ey + up, -0.9 + k * 0.3], [max(x0, x1), ey + up + hgt, 0.9 - k * 0.1], 'skin' if k < 2 else 'dskin')
    # big nose
    cb(head, 0, hy + hh * 0.35, -H['hd'] / 2 - 1.0, 2.0, 2.2, 2.0, 'dskin')
    # team bandana with knot tails
    band = m.bone('tc_bandana', [0, hy + hh, 0], head)
    cb(band, 0, hy + hh * 0.84, 0, hw + 0.4, 1.8, H['hd'] + 0.4, 'tc')
    cb(band, 0, hy + hh * 0.98, 0.4, hw - 0.6, 0.8, H['hd'] - 0.8, 'tc')
    cb(band, 0, hy + hh * 0.5, H['hd'] / 2 + 0.8, 1.6, 2.4, 1.2, 'tc')
    # dagger
    hx, hyy, _ = H['hand_r']
    d = m.bone('dagger', [hx, hyy, 0], ar)
    cb(d, hx, hyy - 0.6, -1.5, 1.1, 1.1, 2.5, 'dleather')
    cb(d, hx, hyy - 0.9, -3.0, 3.0, 1.6, 0.8, 'gold')
    cb(d, hx, hyy - 0.5, -6.4, 0.6, 1.4, 6.0, 'iron')
    humanoid_anims(m, 'melee', atk=0.45, walk=0.5)
    m.hitbox(0.7, 1.2)
    return m


# =================================================================== SKELETON
def skeleton():
    m = Model('clash_skeleton')
    m.mats_({'bone': ('#ece6d2', 'bone'), 'dbone': ('#cdc4aa', 'bone'), 'tc': tc_cloth(), 'rust': ('#a39486', 'metal'),
             'dleather': DLEATHER, 'void': ('#1c1a1f', 'plain'), 'teeth': ('#f4efe0', 'bone')})
    S = 0.78
    skull = [('rect', 0.14, 0.34, 0.42, 0.62, '#1c1a1f'), ('rect', 0.58, 0.34, 0.86, 0.62, '#1c1a1f'),        # 눈구멍
             ('rect', 0.12, 0.30, 0.44, 0.34, '#bdb49a'), ('rect', 0.56, 0.30, 0.88, 0.34, '#bdb49a'),        # 눈썹뼈 그늘
             ('rect', 0.24, 0.44, 0.33, 0.53, '#ffde6b'), ('rect', 0.67, 0.44, 0.76, 0.53, '#ffde6b'),        # 눈빛
             ('rect', 0.45, 0.64, 0.55, 0.78, '#2b2620'), ('rect', 0.47, 0.62, 0.53, 0.64, '#2b2620'),        # 코구멍
             ('rect', 0.08, 0.62, 0.20, 0.72, '#cfc6ac'), ('rect', 0.80, 0.62, 0.92, 0.72, '#cfc6ac'),        # 광대
             ('rect', 0.30, 0.86, 0.70, 1.0, '#2b2620')] + [('rect', 0.31 + i * 0.065, 0.86, 0.36 + i * 0.065, 0.97, '#f4efe0') for i in range(6)]
    H = humanoid(m, dict(s=S, leg_h=11, leg_w=2.0, hip_w=8, tsize=(8, 11, 4.5), hsize=(10, 9.5, 9.5), asize=(2.0, 11), gap=0.8,
                         pants='bone', boot='dbone', torso='void', belt='void', skin='bone', sleeve='bone', glove='dbone',
                         head='bone', face=skull, head_k=0.86))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    lh, neck, hy, tw, td = H['lh'], H['neck'], H['head_y'], H['tw'], H['td']
    # 몸통 안쪽은 어둡게 (갈비뼈 사이로 보이게) → humanoid 가 만든 몸통/벨트 상자를 얇게 뒤로
    for c in body.cubes:
        if c['mat'] == 'void':
            c['frm'][0] += 1.0; c['to'][0] -= 1.0; c['frm'][2] += 1.2; c['to'][2] -= 0.4
    # 척추: 마디마디
    y = lh - 0.4
    while y < neck - 0.6:
        cb(body, 0, y, td / 2 - 1.0, 1.5, 0.75, 1.5, 'dbone')
        cb(body, 0, y + 0.75, td / 2 - 1.0, 1.0, 0.35, 1.0, 'void', noround=True)
        y += 1.1
    # 흉골
    cb(body, 0, lh + 5.4, -td / 2 + 0.1, 1.4, neck - lh - 6.6, 0.9, 'bone')
    cb(body, 0, lh + 4.6, -td / 2 + 0.2, 0.9, 0.9, 0.7, 'bone')
    # 갈비뼈 5쌍: 척추에서 옆으로 돌아 앞쪽 흉골로 (아래로 갈수록 짧고, 마지막은 떠 있는 갈비)
    for i in range(5):
        yy = neck - 2.6 - i * 1.55
        half = tw / 2 + 0.2 - (0.15 * i if i < 3 else 0.4 * (i - 2) + 0.3)
        thick = 0.7
        for sx in (-1, 1):
            # 뒤쪽 (척추 → 옆)
            cb(body, sx * (half / 2 + 0.4), yy + 0.25, td / 2 - 1.1, half - 0.6, thick, 0.8, 'bone', noround=True)
            # 옆 (휘어 내려옴)
            cb(body, sx * half, yy, 0.3, 0.8, thick + 0.2, td - 1.6, 'bone', noround=True)
            # 앞쪽 (옆 → 흉골, 살짝 아래로)
            if i < 4:
                fl = half - 0.9 if i < 3 else half * 0.55
                cb(body, sx * (half - fl / 2), yy - 0.25, -td / 2 + 0.35, fl, thick, 0.8, 'bone', noround=True)
    # 쇄골
    for sx in (-1, 1):
        body.box([sx * 0.6 if sx > 0 else -tw / 2 - 0.8, neck - 1.3, -td / 2 + 0.2], [tw / 2 + 0.8 if sx > 0 else -0.6, neck - 0.6, -td / 2 + 1.0],
                 'bone', rot=('z', -sx * 22.5 / 2 if False else 0), noround=True)
    # 골반: 엉치뼈 + 양쪽 날개
    cb(body, 0, lh - 0.6, td / 2 - 1.2, 2.2, 2.0, 1.4, 'dbone')
    for sx in (-1, 1):
        body.box([sx * 0.8 if sx > 0 else -3.8, lh - 0.4, -1.2], [3.8 if sx > 0 else -0.8, lh + 1.6, 1.4], 'dbone',
                 rot=('z', sx * 22.5), rot_origin=[sx * 2.3, lh + 0.6, 0])
    cb(body, 0, lh - 1.0, -td / 2 + 0.6, 2.6, 0.9, 1.0, 'dbone')                     # 치골
    # 팔다리 관절 (팔꿈치/무릎/어깨 뼈마디)
    for a, sx in ((ar, 1), (al, -1)):
        x = sx * (tw / 2 + H['aw'] / 2 + 0.8 * S)
        cb(a, x, neck - 2.0, 0, 2.8, 1.6, 2.8, 'bone')
        cb(a, x, neck - H['ah'] / 2 - 1.0, 0, 2.5, 1.4, 2.5, 'dbone')
    for lg, sx in ((H['leg_r'], 1), (H['leg_l'], -1)):
        x = sx * (8 * S / 2 - 2.0 * S / 2 - 0.1 * S)
        cb(lg, x, lh * 0.45, -0.2, 2.6, 1.6, 2.6, 'dbone')
        cb(lg, x, lh - 1.4, 0, 2.8, 1.4, 2.8, 'bone')
    # 아래턱 (따로) + 광대
    cb(head, 0, hy - 1.7, -0.9, 6.2, 1.8, 6.6, 'dbone', decals={'north': [('rect', 0.1, 0.0, 0.9, 0.35, '#f4efe0')] +
                                                          [('rect', 0.12 + k * 0.13, 0.0, 0.16 + k * 0.13, 0.35, '#2b2620') for k in range(6)]})
    # 팀색 스카프
    sc = m.bone('tc_scarf', [0, neck, 0], body)
    cb(sc, 0, neck - 1.0, 0, tw + 1.0, 2.0, td + 1.6, 'tc')
    cb(sc, 2.0, neck - 5.0, td / 2 + 0.8, 1.8, 4.2, 0.8, 'tc')
    # 녹슨 단검
    hx, hyy, _ = H['hand_r']
    sw = m.bone('sword', [hx, hyy, 0], ar)
    cb(sw, hx, hyy - 0.5, -1.4, 1.0, 1.0, 2.6, 'dleather')
    cb(sw, hx, hyy - 0.8, -2.9, 3.4, 1.6, 0.6, 'rust')
    cb(sw, hx, hyy - 0.6, -8.1, 0.6, 1.6, 9.8, 'rust')
    humanoid_anims(m, 'melee', atk=0.5, walk=0.6)
    m.hitbox(0.7, 1.3)
    return m


# =================================================================== BOAR JOUSTER (fast building charger)
def hog_rider():
    m = Model('clash_hog_rider')
    m.mats_({'fur': ('#5a3d2b', 'fur'), 'dfur': ('#33231a', 'fur'), 'snout': ('#c98f7a', 'skin'), 'tusk': ('#f1ead6', 'bone'),
             'hoof': ('#2a2420', 'stone'), 'leather': LEATHER, 'dleather': DLEATHER, 'tc': tc_cloth(), 'steel': STEEL,
             'dsteel': DSTEEL, 'gold': GOLD, 'wood': ('#8a5a2e', 'wood'), 'skin': SKIN, 'eye': ('#1b1b1b', 'plain'),
             'helm': ('#a8b0b9', 'metal')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 12, 0], root)
    # boar torso: big shoulders, smaller hind
    cb(body, 0, 9, -3.5, 13, 11, 13, 'fur')
    cb(body, 0, 10, 7.5, 11, 9, 10, 'fur')
    cb(body, 0, 19.5, -4, 4, 2.4, 14, 'dfur')                                  # bristle ridge
    cb(body, 0, 18.2, 6, 3, 1.8, 7, 'dfur')
    cb(body, 0, 12.5, 13.0, 1.2, 4, 1.2, 'dfur', rot=('x', 22.5))               # tail
    # head
    head = m.bone('head', [0, 15, -10], body)
    cb(head, 0, 9.5, -14.5, 10, 9.5, 8.5, 'fur',
       decals={'north': [('rect', 0.1, 0.18, 0.3, 0.34, '#1b1b1b'), ('rect', 0.7, 0.18, 0.9, 0.34, '#1b1b1b'),
                         ('rect', 0.14, 0.2, 0.2, 0.26, '#ffffff'), ('rect', 0.74, 0.2, 0.8, 0.26, '#ffffff')]})
    cb(head, 0, 10, -20.5, 6.4, 5.0, 3.6, 'snout', decals={'north': [('rect', 0.2, 0.3, 0.38, 0.6, '#5a3434'), ('rect', 0.62, 0.3, 0.8, 0.6, '#5a3434')]})
    for sx in (-1, 1):
        cb(head, sx * 3.6, 11.2, -20.6, 1.2, 4.6, 1.2, 'tusk', rot=('z', -22.5 * sx), rot_origin=[sx * 3.6, 11.2, -20.6])
        cb(head, sx * 4.4, 18.5, -12.5, 2.4, 3.0, 1.2, 'dfur', rot=('z', -22.5 * sx), rot_origin=[sx * 4.4, 18.5, -12.5])  # ears
    # chamfron (head armour)
    cb(head, 0, 16.6, -16.0, 6.4, 2.4, 6.0, 'steel')
    cb(head, 0, 18.4, -16.0, 1.4, 2.6, 1.4, 'steel')
    # legs
    for n, x, z in (('fl_leg', -4, -7), ('fr_leg', 4, -7), ('bl_leg', -3.8, 9), ('br_leg', 3.8, 9)):
        b = m.bone(n, [x, 12, z], body)
        cb(b, x, 2.4, z, 3.6, 10, 3.6, 'fur')
        cb(b, x, 0, z - 0.2, 3.8, 2.6, 4.0, 'hoof')
    # saddle + team caparison
    cb(body, 0, 20, 0.5, 9, 1.6, 9, 'leather')
    cb(body, 0, 21.6, 4.6, 8, 2.6, 1.6, 'dleather')
    cap = m.bone('tc_caparison', [0, 18, 0], body)
    cb(cap, -6.9, 12, 0.5, 0.8, 8.5, 12, 'tc', decals={'west': [('rect', 0.4, 0.25, 0.6, 0.75, '#c8c8c8')]})
    cb(cap, 6.9, 12, 0.5, 0.8, 8.5, 12, 'tc', decals={'east': [('rect', 0.4, 0.25, 0.6, 0.75, '#c8c8c8')]})
    # rider -------------------------------------------------------
    rb = m.bone('rider', [0, 22, 0], body)
    cb(rb, 0, 22, 0.5, 8.5, 10, 5.5, 'steel')
    cb(rb, 0, 21.8, 0.5, 9, 1.6, 6, 'dleather')
    rtab = m.bone('tc_rider', [0, 26, 0], rb)
    cb(rtab, 0, 22.4, -2.4, 5, 8.5, 0.6, 'tc')
    for sx in (-1, 1):  # legs astride
        cb(rb, sx * 5.4, 15.5, -0.5, 3.4, 7.5, 4.0, 'dleather')
        cb(rb, sx * 5.4, 15.0, -1.4, 3.8, 2.6, 5.4, 'dsteel')
    rh = m.bone('rider_head', [0, 32, 0], rb)
    cb(rh, 0, 32, 0.5, 8, 8, 8, 'helm', decals={'north': visor()}, dens=2)
    cb(rh, 0, 34.5, 0.5, 9, 1.0, 9, 'dsteel')
    plume = m.bone('tc_plume', [0, 40, 0], rh)
    cb(plume, 0, 40, 1.5, 1.6, 2.4, 6, 'tc')
    cb(plume, 0, 38.5, 5.0, 1.6, 2.4, 2, 'tc')
    # lance arm (right) + shield arm (left)
    la = m.bone('arm_r', [5.8, 30, 0.5], rb)
    cb(la, 5.8, 21, 0.5, 3.6, 9.5, 3.6, 'steel')
    cb(la, 5.8, 29, 0.5, 5, 3, 5, 'dsteel')
    lance = m.bone('lance', [5.8, 23, 0], la)
    cb(lance, 5.8, 22, -1.5, 1.6, 1.6, 4, 'wood')
    cb(lance, 5.8, 21.3, -5.2, 4.4, 3.0, 3.4, 'steel')                          # vamplate
    cb(lance, 5.8, 22.2, -18.5, 1.4, 1.4, 23, 'wood')
    cb(lance, 5.8, 22.4, -31, 0.8, 1.0, 2.5, 'steel')
    la2 = m.bone('arm_l', [-5.8, 30, 0.5], rb)
    cb(la2, -5.8, 21, 0.5, 3.6, 9.5, 3.6, 'steel')
    cb(la2, -5.8, 29, 0.5, 5, 3, 5, 'dsteel')
    sh = m.bone('tc_shield', [-8, 24, 0], la2)
    cb(sh, -8.2, 20, -0.5, 1.0, 8, 7, 'tc', decals={'west': [('rect', 0.0, 0.45, 1.0, 0.58, '#c6c6c6')]})
    # animations ---------------------------------------------------
    m.anim('idle', 2.0, 'loop', {
        'body': {'position': [(0, (0, 0, 0)), (1.0, (0, -0.5, 0)), (2.0, (0, 0, 0))]},
        'head': {'rotation': [(0, (0, 0, 0)), (0.6, (6, 0, 0)), (1.2, (0, 6, 0)), (2.0, (0, 0, 0))]},
        'rider_head': {'rotation': [(0, (0, 0, 0)), (1.0, (0, -8, 0)), (2.0, (0, 0, 0))]}})
    quad_walk(m, walk=0.42, amp=40, extra={
        'head': {'rotation': [(0, (0, 0, 0)), (0.105, (-6, 0, 0)), (0.21, (0, 0, 0)), (0.315, (-6, 0, 0)), (0.42, (0, 0, 0))]},
        'rider': {'position': [(0, (0, 0, 0)), (0.105, (0, -1, 0.4)), (0.21, (0, 0, 0)), (0.315, (0, -1, 0.4)), (0.42, (0, 0, 0))]},
        'arm_r': {'rotation': [(0, (-8, 0, 0)), (0.21, (-12, 0, 0)), (0.42, (-8, 0, 0))]}})
    m.anim('attack', 0.8, 'once', {
        'arm_r': {'rotation': [(0, (0, 0, 0)), (0.25, (25, 0, 0)), (0.42, (-30, 0, 0)), (0.8, (0, 0, 0))]},
        'rider': {'rotation': [(0, (0, 0, 0)), (0.25, (8, 0, 0)), (0.42, (-14, 0, 0)), (0.8, (0, 0, 0))]},
        'head': {'rotation': [(0, (0, 0, 0)), (0.3, (-14, 0, 0)), (0.45, (16, 0, 0)), (0.8, (0, 0, 0))]}})
    m.anim('jump', 0.7, 'once', {
        'root': {'position': [(0, (0, 0, 0)), (0.12, (0, -1.5, 0)), (0.35, (0, 26, 0)), (0.6, (0, 0, 0)), (0.7, (0, 0, 0))],
                 'rotation': [(0, (0, 0, 0)), (0.2, (-18, 0, 0)), (0.45, (12, 0, 0)), (0.7, (0, 0, 0))]},
        'fl_leg': {'rotation': [(0, (0, 0, 0)), (0.2, (-60, 0, 0)), (0.5, (30, 0, 0)), (0.7, (0, 0, 0))]},
        'fr_leg': {'rotation': [(0, (0, 0, 0)), (0.2, (-60, 0, 0)), (0.5, (30, 0, 0)), (0.7, (0, 0, 0))]},
        'bl_leg': {'rotation': [(0, (0, 0, 0)), (0.2, (50, 0, 0)), (0.5, (-20, 0, 0)), (0.7, (0, 0, 0))]},
        'br_leg': {'rotation': [(0, (0, 0, 0)), (0.2, (50, 0, 0)), (0.5, (-20, 0, 0)), (0.7, (0, 0, 0))]}})
    common_anims(m)
    m.hitbox(1.3, 2.2)
    return m


# =================================================================== WHELP DRAGON (flying splash)
def blob(bone, x, y, z, w, h, d, mat, r=None, decals=None):
    """동글동글한 덩어리: 축마다 한 겹씩 3개 상자 (모서리를 크게 깎아 둥글게)"""
    r = r if r is not None else min(w, h, d) * 0.22
    decals = decals or {}
    pick = lambda fs: {f: v for f, v in decals.items() if f in fs}
    cb(bone, x, y + r, z, w, h - 2 * r, d - 2 * r, mat, decals=pick(('east', 'west')), noround=True)
    cb(bone, x, y, z, w - 2 * r, h, d - 2 * r, mat, decals=pick(('up', 'down')), noround=True)
    return cb(bone, x, y + r, z, w - 2 * r, h - 2 * r, d, mat, decals=pick(('north', 'south')), noround=True)


def ball(bone, x, y, z, w, h, d, mat, prof=(0.62, 0.88, 1.0, 1.0, 0.9, 0.66)):
    """가로 조각을 쌓아 둥근 덩어리 (아래→위로 폭 변화). 위/아래 조각은 앞뒤로도 짧아져서 옆에서 봐도 둥글게"""
    n = len(prof)
    sh = h / n
    for i, k in enumerate(prof):
        yy = y + i * sh
        cb(bone, x, yy, z, w * k, sh + 0.02, d * k, mat, noround=True)
        if 0.8 < k < 1.0:      # 가장자리 부드럽게: 한 겹 더 (가로만 조금 넓게)
            cb(bone, x, yy + sh * 0.2, z, w * min(1.0, k + 0.06), sh * 0.6, d * (k - 0.08), mat, noround=True)


def baby_dragon():
    """순둥순둥 동글동글 아기 용: 통통한 몸, 큰 머리, 큰 눈, 짧은 뿔, 작은 날개, 말린 꼬리"""
    m = Model('clash_baby_dragon', density=1.5)
    m.mats_({'scale': ('#ef8a3a', 'soft'), 'dscale': ('#d9702a', 'soft'), 'belly': ('#ffe1a6', 'soft'),
             'wing': ('#f4b26a', 'leather', {'stitch': False}), 'wbone': ('#e07a30', 'skin'), 'horn': ('#fff1d6', 'bone'),
             'tc': tc_cloth(), 'claw': ('#fff1d6', 'bone'), 'gold': GOLD, 'mouth': ('#7a2e2a', 'plain'),
             'white': ('#ffffff', 'plain'), 'pupil': ('#2a1a12', 'plain'), 'cheek': ('#ff9f8a', 'plain'), 'nostril': ('#8a4a30', 'plain')})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 10, 0], root)
    # 통통한 몸 (둥근 조각 쌓기) + 크림색 배
    ball(body, 0, 4.0, 1.4, 12.6, 11.4, 12.0, 'scale')
    ball(body, 0, 5.2, -3.6, 8.4, 7.6, 4.2, 'belly', prof=(0.7, 0.95, 1.0, 0.95, 0.75))
    for k, z in enumerate((-0.6, 3.0, 6.4)):                                      # 등 위 말랑한 돌기
        ball(body, 0, 14.8 - k * 0.6, z, 2.6, 2.2 - k * 0.3, 2.6, 'dscale', prof=(1.0, 0.7))
    # 큰 머리: 옆으로 넓고 위아래로 둥근 공 모양 + 큰 입체 눈
    head = m.bone('head', [0, 15, -4], body)
    HW, HH, HD = 11.8, 11.0, 11.0
    ball(head, 0, 13.4, -7.6, HW, HH, HD, 'scale', prof=(0.72, 0.93, 1.0, 1.0, 0.95, 0.8, 0.55))
    fz = -7.6 - HD / 2
    for sx in (-1, 1):
        ex = sx * 2.7
        cb(head, ex, 17.4, fz + 0.15, 2.8, 3.2, 1.0, 'white', noround=True)          # 흰자
        cb(head, ex - sx * 0.2, 17.4, fz - 0.2, 2.0, 2.6, 0.6, 'pupil', noround=True)     # 눈동자
        cb(head, ex - sx * 0.5, 19.0, fz - 0.4, 0.7, 0.7, 0.4, 'white', noround=True)     # 반짝
        cb(head, sx * 4.4, 15.9, fz + 0.5, 1.8, 0.9, 0.6, 'cheek', noround=True)          # 볼터치
    # 작은 주둥이 (얼굴 아래쪽, 살짝만 튀어나옴) + 웃는 입
    ball(head, 0, 13.6, fz - 0.6, 5.4, 2.6, 2.6, 'belly', prof=(0.8, 1.0, 0.85))
    for sx in (-1, 1):
        cb(head, sx * 1.2, 15.5, fz - 1.75, 0.6, 0.5, 0.4, 'nostril', noround=True)
    jaw = m.bone('jaw', [0, 13.8, fz + 1], head)
    ball(jaw, 0, 12.6, fz + 0.2, 5.0, 1.4, 2.4, 'belly', prof=(0.8, 1.0))
    cb(jaw, 0, 13.7, fz - 1.75, 2.8, 0.45, 0.4, 'mouth', noround=True)
    for sx in (-1, 1):
        cb(jaw, sx * 1.6, 14.0, fz - 1.75, 0.55, 0.6, 0.4, 'mouth', noround=True)
    # 짧고 동글한 뿔 + 귀 지느러미
    for sx in (-1, 1):
        ball(head, sx * 3.0, 24.0, -6.8, 2.4, 2.4, 2.4, 'horn', prof=(1.0, 0.8, 0.55))
        ball(head, sx * 6.1, 17.6, -6.8, 1.4, 3.2, 3.4, 'dscale', prof=(0.7, 1.0, 0.7))
    # 팀색 스카프
    col = m.bone('tc_scarf', [0, 14, -3], body)
    ball(col, 0, 12.4, -1.6, 11.4, 2.6, 10.6, 'tc', prof=(1.0, 0.94))
    cb(col, 2.6, 9.6, -7.2, 2.4, 3.2, 0.8, 'tc', noround=True)
    cb(col, 0, 12.4, -7.0, 2.0, 2.0, 0.7, 'gold', noround=True)
    # 작은 날개 (동글한 막)
    for side, sx in (('wing_r', 1), ('wing_l', -1)):
        w = m.bone(side, [sx * 5.5, 14.5, 2.5], body)
        x0 = sx * 5.5
        lo, hi = (x0, x0 + sx * 8.5) if sx > 0 else (x0 + sx * 8.5, x0)
        w.box([lo, 14.4, 1.0], [hi, 15.6, 2.6], 'wbone', noround=True)                     # 날개 뼈
        w.box([min(x0, x0 + sx * 8), 14.8, 2.6], [max(x0, x0 + sx * 8), 15.3, 8.0], 'wing', noround=True)
        w.box([min(x0 + sx * 1.5, x0 + sx * 6.5), 14.8, 8.0], [max(x0 + sx * 1.5, x0 + sx * 6.5), 15.3, 9.8], 'wing', noround=True)
        ball(w, x0 + sx * 8.6, 14.0, 1.8, 1.8, 2.0, 1.8, 'claw', prof=(1.0, 0.6))
    # 짧고 통통한 다리
    for n, x, z in (('fl_leg', -3.6, -2.4), ('fr_leg', 3.6, -2.4), ('bl_leg', -3.8, 5.0), ('br_leg', 3.8, 5.0)):
        b = m.bone(n, [x, 6.5, z], body)
        ball(b, x, 3.0, z, 4.2, 4.0, 4.2, 'scale', prof=(0.85, 1.0, 1.0, 0.85))      # 짧은 다리 (날고 있으니 쏙)
        ball(b, x, 2.6, z - 0.5, 4.4, 1.6, 4.6, 'dscale', prof=(1.0, 0.8))
        for k in (-1, 0, 1):
            cb(b, x + k * 1.2, 2.7, z - 2.9, 0.7, 0.8, 0.6, 'claw', noround=True)
    # 위로 말린 꼬리 + 둥근 끝
    tail = m.bone('tail', [0, 8.5, 8], body)
    ball(tail, 0, 6.4, 10.4, 6.0, 5.0, 5.4, 'scale', prof=(0.8, 1.0, 1.0, 0.8))
    ball(tail, 0, 7.6, 14.2, 4.2, 3.8, 4.0, 'scale', prof=(0.8, 1.0, 0.8))
    ball(tail, 0, 9.4, 17.0, 3.0, 3.2, 3.0, 'dscale', prof=(0.8, 1.0, 0.8))
    ball(tail, 0, 12.0, 18.2, 2.4, 3.0, 2.4, 'dscale', prof=(0.8, 1.0, 0.8))
    ball(tail, 0, 14.6, 17.8, 3.8, 2.8, 2.2, 'horn', prof=(0.7, 1.0, 0.6))
    # 애니메이션: 파닥파닥 + 꼬리 살랑 + 고개 갸웃
    m.anim('idle', 1.0, 'loop', dict(flap('wing_l', 'wing_r', 0.5, 26, bob=1.2),
                                     tail={'rotation': [(0, (0, -12, 0)), (0.5, (0, 12, 0)), (1.0, (0, -12, 0))]},
                                     head={'rotation': [(0, (0, 0, -5)), (0.5, (3, 0, 5)), (1.0, (0, 0, -5))]}))
    m.anims[-1]['length'] = 1.0
    m.anim('walk', 0.4, 'loop', dict(flap('wing_l', 'wing_r', 0.4, 36, bob=1.0),
                                     tail={'rotation': [(0, (6, -10, 0)), (0.2, (6, 10, 0)), (0.4, (6, -10, 0))]},
                                     root={'rotation': [(0, (8, 0, 0)), (0.4, (8, 0, 0))]}))
    m.anim('attack', 0.7, 'once', {
        'head': {'rotation': [(0, (0, 0, 0)), (0.25, (-18, 0, 0)), (0.4, (10, 0, 0)), (0.7, (0, 0, 0))]},
        'jaw': {'rotation': [(0, (0, 0, 0)), (0.25, (0, 0, 0)), (0.38, (30, 0, 0)), (0.6, (30, 0, 0)), (0.7, (0, 0, 0))]},
        'body': {'position': [(0, (0, 0, 0)), (0.25, (0, 0.6, 1.0)), (0.4, (0, 0, -1.5)), (0.7, (0, 0, 0))]}})
    common_anims(m)
    m.round = False
    m.hitbox(1.6, 1.3)
    return m


# =================================================================== GARGOYLE IMP (flying swarm)
def minion():
    """악동 임프: 팔다리 제대로, 뿔 + 뾰족 귀 + 씩 웃는 얼굴, 작은 뾰족 박쥐 날개, 화살촉 꼬리, 손톱으로 할퀴기"""
    m = Model('clash_minion', density=1.5)
    m.mats_({'skin': ('#6c5d86', 'soft'), 'dskin': ('#53466b', 'soft'), 'belly': ('#9a8bb3', 'soft'),
             'wing': ('#3b3150', 'leather', {'stitch': False}), 'wbone': ('#4a3e62', 'soft'), 'horn': ('#efe4cc', 'bone'),
             'tc': tc_cloth(), 'claw': ('#f2ead6', 'bone'), 'iron': ('#7b838d', 'metal'), 'wood': ('#6b4428', 'wood', {'grain': 'v'}),
             'shorts': ('#3a2f2a', 'leather'), 'tc2': ('#bdbdbd', 'cloth'), 'gold': GOLD})
    grin = [('rect', 0.12, 0.34, 0.40, 0.52, '#fff6c8'), ('rect', 0.60, 0.34, 0.88, 0.52, '#fff6c8'),        # 노란 눈
            ('rect', 0.24, 0.36, 0.34, 0.52, '#1c1420'), ('rect', 0.66, 0.36, 0.76, 0.52, '#1c1420'),
            ('rect', 0.08, 0.26, 0.40, 0.32, '#3a2f4c'), ('rect', 0.60, 0.22, 0.92, 0.28, '#3a2f4c'),        # 장난스런 눈썹 (짝짝이)
            ('shade', 0.44, 0.52, 0.56, 0.64, 0.82),
            ('rect', 0.20, 0.70, 0.80, 0.80, '#2a1a24'), ('rect', 0.14, 0.64, 0.22, 0.72, '#2a1a24'),        # 씩 웃는 입 (한쪽 올라감)
            ('rect', 0.80, 0.60, 0.88, 0.70, '#2a1a24'),
            ('rect', 0.30, 0.70, 0.36, 0.76, '#ffffff'), ('rect', 0.62, 0.70, 0.68, 0.76, '#ffffff')]        # 송곳니
    H = humanoid(m, dict(s=0.72, leg_h=8.5, leg_w=3.4, hip_w=7.4, tsize=(8, 8.5, 5.4), hsize=(10, 9, 9), asize=(3.0, 9.5), gap=0.2,
                         pants='skin', boot='dskin', torso='skin', belt='shorts', buckle='iron', skin='skin',
                         sleeve='skin', glove='dskin', head='skin', face=grin, head_k=0.92))
    body, head, ar, al = H['body'], H['head'], H['arm_r'], H['arm_l']
    s_, lh, neck, hy, tw, td, hw, hh, hd = H['s'], H['lh'], H['neck'], H['head_y'], H['tw'], H['td'], H['hw'], H['hh'], H['hd']
    # 볼록 배 + 반바지
    cb(body, 0, lh + 1.4, -td / 2 - 0.2, tw - 2.4, 4.0, 0.8, 'belly')
    cb(body, 0, lh - 1.0, 0, tw + 0.5, 2.6, td + 0.5, 'shorts')
    # 뿔 (뒤로 휨) + 뾰족 귀
    for sx in (-1, 1):
        head.box([sx * 2.6 - 0.9, hy + hh, -1.4], [sx * 2.6 + 0.9, hy + hh + 2.6, 0.4], 'horn', rot=('x', -22.5), rot_origin=[sx * 2.6, hy + hh, -0.5])
        head.box([sx * 2.6 - 0.5, hy + hh + 2.2, 0.4], [sx * 2.6 + 0.5, hy + hh + 4.0, 1.4], 'horn', rot=('x', -45), rot_origin=[sx * 2.6, hy + hh + 2.2, 0.9])
        head.box([sx * hw / 2 if sx > 0 else -hw / 2 - 3.2, hy + hh * 0.45, -0.8], [sx * hw / 2 + 3.2 if sx > 0 else -hw / 2, hy + hh * 0.45 + 1.6, 0.8],
                 'skin', rot=('z', sx * 22.5), rot_origin=[sx * hw / 2, hy + hh * 0.5, 0])
        cb(head, sx * (hw / 2 + 2.6), hy + hh * 0.45 + 1.4, 0, 1.0, 1.4, 1.0, 'dskin', noround=True)
    # 팀색 반다나 (목) + 꼬리 끝
    bd = m.bone('tc_bandana', [0, neck, 0], body)
    cb(bd, 0, neck - 2.0, 0, tw + 1.6, 2.0, td + 1.6, 'tc', noround=True)                   # 목에 감은 도톰한 띠
    cb(bd, 0, neck - 1.2, 0, tw + 1.0, 0.6, td + 1.0, 'tc', noround=True)
    fz = -td / 2 - 1.0                                                                      # 몸에서 앞으로 튀어나오게
    rows = ((tw + 0.4, neck - 3.2, 1.4), (tw - 1.6, neck - 4.2, 1.3), (tw - 3.6, neck - 5.2, 1.2), (tw - 5.4, neck - 6.1, 1.0))
    for k, (w, y, dz) in enumerate(rows):                                                   # 앞 삼각 반다나 (아래로 갈수록 살짝 앞으로)
        cb(bd, 0, y, fz - 0.15 * k, max(1.0, w), 1.05, dz, 'tc', noround=True)
    cb(bd, 0, neck - 6.9, fz - 0.6, 1.0, 0.9, 0.9, 'tc', noround=True)                      # 뾰족 끝
    cb(bd, -1.2, neck - 3.6, fz - 0.6, 0.5, 0.5, 0.5, 'gold', noround=True)                 # 무늬 점
    cb(bd, 1.3, neck - 4.6, fz - 0.7, 0.5, 0.5, 0.5, 'gold', noround=True)
    bz = td / 2 + 0.9                                                                       # 뒤 큰 매듭 + 끈 두 가닥
    cb(bd, 0, neck - 2.6, bz, 2.0, 1.8, 1.4, 'tc', noround=True)
    bd.box([-1.8, neck - 5.6, bz - 0.4], [-0.6, neck - 2.4, bz + 0.6], 'tc', rot=('z', -22.5), rot_origin=[-0.6, neck - 2.4, bz], noround=True)
    bd.box([0.6, neck - 5.0, bz - 0.4], [1.8, neck - 2.4, bz + 0.6], 'tc', rot=('z', 22.5), rot_origin=[0.6, neck - 2.4, bz], noround=True)
    # 작은 박쥐 날개 (등): 바깥 끝이 뾰족하게 솟고, 아래 가장자리는 톱니처럼 들쭉날쭉
    for side, sx in (('wing_r', 1), ('wing_l', -1)):
        w = m.bone(side, [sx * 1.5, neck - 1, td / 2], body)
        x0, z0 = sx * 1.5, td / 2
        def seg(a, b, y0, y1, mat, dz=0.5, t=0.4):
            lo, hi = min(x0 + sx * a, x0 + sx * b), max(x0 + sx * a, x0 + sx * b)
            w.box([lo, y0, z0 + dz], [hi, y1, z0 + dz + t], mat, noround=True)
        # 막: (안쪽 x, 바깥 x, 아래, 위) — 바깥으로 갈수록 위로 솟아 뾰족
        cols = [(0.0, 1.2, neck - 2.2, neck + 1.4), (1.2, 2.4, neck - 1.0, neck + 2.4), (2.4, 3.4, neck - 2.0, neck + 3.4),
                (3.4, 4.4, neck - 0.4, neck + 4.4), (4.4, 5.2, neck + 0.6, neck + 5.4), (5.2, 5.9, neck + 2.6, neck + 6.4)]
        for a, b, y0, y1 in cols:
            seg(a, b, y0, y1, 'wing')
        # 날개 뼈: 어깨 → 바깥 위 끝 (계단), 손가락 뼈 2개
        for k in range(6):
            seg(k, k + 1.0, neck + 0.4 + k * 1.0, neck + 1.2 + k * 1.0, 'wbone', dz=0.3, t=0.8)
        seg(2.2, 2.8, neck - 2.0, neck + 2.8, 'wbone', dz=0.35, t=0.7)
        seg(4.0, 4.5, neck - 0.4, neck + 4.6, 'wbone', dz=0.35, t=0.7)
        seg(5.8, 6.6, neck + 6.0, neck + 7.4, 'claw', dz=0.2, t=0.9)                                      # 끝 발톱
    # 짧게 톡 튀어나온 꼬리 + 작은 화살촉
    tail = m.bone('tail', [0, lh, td / 2], body)
    cb(tail, 0, lh - 0.6, td / 2 + 0.5, 1.3, 1.3, 1.8, 'dskin', noround=True)
    cb(tail, 0, lh - 0.1, td / 2 + 1.6, 1.1, 1.1, 1.4, 'dskin', noround=True)
    cb(tail, 0, lh + 0.1, td / 2 + 2.5, 2.0, 0.8, 0.9, 'dskin', noround=True)        # 화살촉 양옆
    cb(tail, 0, lh - 0.1, td / 2 + 3.0, 0.8, 1.2, 0.8, 'dskin', noround=True)        # 화살촉 끝
    # 손: 장갑(손) 끝에 붙은 손톱 3개 (앞쪽 아래로)
    aw_, ah_ = H['aw'], H['ah']
    for a, side, sx in ((ar, 'r', 1), (al, 'l', -1)):
        hx = sx * (tw / 2 + aw_ / 2 + 0.2 * s_)
        bottom = neck - ah_
        for k in (-1, 0, 1):
            cb(a, hx + k * aw_ * 0.32, bottom - 0.7, -aw_ / 2 + 0.1, 0.45, 1.0, 0.9, 'claw', noround=True)
    # 애니메이션: 날면서 다리 달랑 + 장난스런 고개 / 쇠스랑 찌르기
    fl = flap('wing_l', 'wing_r', 0.32, 34, bob=1.0)
    m.anim('idle', 0.64, 'loop', dict(
        {k: {'rotation': [(0, v['rotation'][0][1]), (0.16, v['rotation'][1][1]), (0.32, v['rotation'][0][1]), (0.48, v['rotation'][1][1]), (0.64, v['rotation'][0][1])]}
         for k, v in fl.items() if k.startswith('wing')},
        body={'position': [(0, (0, 0, 0)), (0.32, (0, 0.8, 0)), (0.64, (0, 0, 0))]},
        leg_r={'rotation': [(0, (10, 0, 0)), (0.32, (25, 0, 0)), (0.64, (10, 0, 0))]},
        leg_l={'rotation': [(0, (25, 0, 0)), (0.32, (10, 0, 0)), (0.64, (25, 0, 0))]},
        head={'rotation': [(0, (0, 0, -6)), (0.32, (-4, 8, 6)), (0.64, (0, 0, -6))]},
        tail={'rotation': [(0, (0, -15, 0)), (0.32, (0, 15, 0)), (0.64, (0, -15, 0))]},
        tc_bandana_front={'rotation': [(0, (0, 0, 0)), (0.32, (-8, 0, 0)), (0.64, (0, 0, 0))]}))
    m.anim('walk', 0.32, 'loop', dict(
        {k: {'rotation': [(0, v['rotation'][0][1]), (0.16, v['rotation'][1][1]), (0.32, v['rotation'][0][1])]} for k, v in fl.items() if k.startswith('wing')},
        root={'rotation': [(0, (14, 0, 0)), (0.32, (14, 0, 0))]},
        leg_r={'rotation': [(0, (30, 0, 0)), (0.16, (40, 0, 0)), (0.32, (30, 0, 0))]},
        leg_l={'rotation': [(0, (40, 0, 0)), (0.16, (30, 0, 0)), (0.32, (40, 0, 0))]},
        arm_l={'rotation': [(0, (20, 0, -10)), (0.16, (30, 0, -10)), (0.32, (20, 0, -10))]},
        tail={'rotation': [(0, (10, -12, 0)), (0.16, (10, 12, 0)), (0.32, (10, -12, 0))]},
        tc_bandana_front={'rotation': [(0, (-20, 0, 0)), (0.16, (-28, 0, 0)), (0.32, (-20, 0, 0))]}))
    m.anim('attack', 0.5, 'once', {   # 양손 손톱 할퀴기 (오른손 → 왼손)
        'arm_r': {'rotation': [(0, (0, 0, 0)), (0.1, (-120, 0, 30)), (0.2, (-60, 0, -25)), (0.32, (-20, 0, 0)), (0.5, (0, 0, 0))]},
        'arm_l': {'rotation': [(0, (0, 0, 0)), (0.18, (-30, 0, -10)), (0.28, (-120, 0, -30)), (0.38, (-60, 0, 25)), (0.5, (0, 0, 0))]},
        'body': {'rotation': [(0, (0, 0, 0)), (0.12, (0, -15, 0)), (0.22, (10, 15, 0)), (0.34, (10, -15, 0)), (0.5, (0, 0, 0))]},
        'head': {'rotation': [(0, (0, 0, 0)), (0.22, (8, 0, 8)), (0.5, (0, 0, 0))]}})
    common_anims(m)
    m.hitbox(0.9, 1.0)
    return m


# =================================================================== BONE COPTER CRATE (flying carrier)
def skeleton_barrel():
    m = Model('clash_skeleton_barrel')
    m.mats_({'wood': ('#8a5d33', 'wood', {'planks': True}), 'dwood': ('#5b3b20', 'wood'), 'iron': ('#6d747c', 'metal', {'rivets': True}),
             'bone': ('#ece6d2', 'bone'), 'tc': tc_cloth(), 'rope': ('#b99a62', 'rope'), 'void': ('#1c1a1f', 'plain'), 'gold': GOLD})
    root = m.bone('root', [0, 0, 0])
    body = m.bone('body', [0, 8, 0], root)
    skull = [('rect', 0.28, 0.2, 0.72, 0.58, '#ece6d2'), ('rect', 0.34, 0.58, 0.66, 0.7, '#ece6d2'),
             ('rect', 0.33, 0.33, 0.46, 0.48, '#1c1a1f'), ('rect', 0.54, 0.33, 0.67, 0.48, '#1c1a1f'),
             ('rect', 0.48, 0.5, 0.52, 0.56, '#1c1a1f'), ('rect', 0.40, 0.62, 0.42, 0.7, '#6e6656'), ('rect', 0.47, 0.62, 0.49, 0.7, '#6e6656'),
             ('rect', 0.53, 0.62, 0.55, 0.7, '#6e6656'), ('rect', 0.59, 0.62, 0.61, 0.7, '#6e6656'),
             ('rect', 0.16, 0.76, 0.84, 0.8, '#ece6d2'), ('rect', 0.16, 0.84, 0.84, 0.88, '#ece6d2'),
             ('rect', 0.12, 0.74, 0.18, 0.9, '#ece6d2'), ('rect', 0.82, 0.74, 0.88, 0.9, '#ece6d2')]
    cb(body, 0, 0, 0, 16, 14, 16, 'wood', decals={f: skull for f in ('north', 'south', 'east', 'west')})
    for y in (0.5, 12.5):                                                       # iron bands
        cb(body, 0, y, 0, 16.6, 1.4, 16.6, 'iron')
    for x in (-8.1, 8.1):
        for z in (-8.1, 8.1):
            cb(body, x, 0, z, 1.2, 14, 1.2, 'iron')
    # bony hands gripping the rim (peeking passengers)
    for x, z in ((-4, -8.4), (3.5, -8.4), (8.4, 2), (-8.4, -3)):
        cb(body, x, 12.4, z, 2.0, 3.0, 1.2 if abs(z) > 8 else 2.0, 'bone')
    # mast + rotor
    cb(body, 0, 14, 0, 2.4, 9, 2.4, 'dwood')
    cb(body, 0, 15, 0, 4, 1.2, 4, 'iron')
    rotor = m.bone('rotor', [0, 23.5, 0], body)
    cb(rotor, 0, 22.6, 0, 3.4, 2.0, 3.4, 'iron')
    cb(rotor, 0, 23.6, 0, 1.2, 1.2, 1.2, 'gold')
    for ang in (0, 1):
        if ang == 0:
            rotor.box([-22, 23.0, -1.6], [-1.7, 23.6, 1.6], 'bone')
            rotor.box([1.7, 23.0, -1.6], [22, 23.6, 1.6], 'bone')
        else:
            rotor.box([-1.6, 23.0, -22], [1.6, 23.6, -1.7], 'bone')
            rotor.box([-1.6, 23.0, 1.7], [1.6, 23.6, 22], 'bone')
    # team pennant on a rope
    pen = m.bone('tc_pennant', [8, 10, 8], body)
    cb(pen, 8.8, -5, 8.8, 0.4, 13, 0.4, 'rope')
    cb(pen, 8.8, -5, 11.3, 0.6, 4.2, 5, 'tc')
    spin = lambda T, step: [(round(i * step, 3), (0, 180 * i, 0)) for i in range(int(round(T / step)) + 1)]
    bob = lambda T: [(round(i * 0.4, 3), (0, 0.6 if i % 2 else 0, 0)) for i in range(int(round(T / 0.4)) + 1)]
    m.anim('idle', 2.0, 'loop', {'rotor': {'rotation': spin(2.0, 0.2)}, 'body': {'position': bob(2.0)}}, interp='linear')
    m.anim('walk', 0.6, 'loop', {'rotor': {'rotation': spin(0.6, 0.15)},
                                 'root': {'rotation': [(0, (8, 0, 0)), (0.6, (8, 0, 0))]},
                                 'tc_pennant': {'rotation': [(0, (14, 0, 0)), (0.15, (22, 0, 0)), (0.3, (14, 0, 0)), (0.45, (22, 0, 0)), (0.6, (14, 0, 0))]}}, interp='linear')
    m.anim('attack', 0.4, 'once', {'body': {'scale': [(0, (1, 1, 1)), (0.2, (1.08, 0.94, 1.08)), (0.4, (1, 1, 1))]}})
    m.anim('spawn', 0.5, 'once', {'root': {'scale': [(0, (0.2, 0.2, 0.2)), (0.35, (1.1, 1.1, 1.1)), (0.5, (1, 1, 1))]}})
    m.anim('hit', 0.3, 'once', {'body': {'rotation': [(0, (0, 0, 0)), (0.1, (0, 0, 10)), (0.3, (0, 0, 0))]}})
    m.anim('death', 0.8, 'hold', {'root': {'position': [(0, (0, 0, 0)), (0.8, (0, -40, 0))],
                                           'rotation': [(0, (0, 0, 0)), (0.8, (20, 0, 30))],
                                           'scale': [(0, (1, 1, 1)), (0.6, (1, 1, 1)), (0.8, (1.3, 0.4, 1.3))]}})
    m.hitbox(1.4, 1.8)
    return m


# =================================================================== GOBLIN BARREL (thrown projectile)
def goblin_barrel_proj():
    """날아가는 고블린 통: 통 안에서 고블린 귀와 손이 삐져나옴. idle = 공중제비 회전"""
    m = Model('clash_goblin_barrel')
    m.mats_({'wood': ('#8a5d33', 'wood', {'planks': True, 'grain': 'v'}), 'dwood': ('#5b3b20', 'wood'),
             'iron': ('#6d747c', 'metal', {'rivets': True}), 'skin': ('#7fb14a', 'skin'), 'dskin': ('#5f8f37', 'skin'),
             'tc': tc_cloth(), 'rope': ('#b99a62', 'rope'), 'dark': ('#1c1a1f', 'plain'), 'eye': ('#f6e46a', 'glow'),
             'iron2': ('#a4acb5', 'metal')})
    root = m.bone('root', [0, 9, 0])
    spin = m.bone('spin', [0, 9, 0], root)
    # 통 몸통 (가운데가 볼록하게 3단)
    cb(spin, 0, 1.0, 0, 12, 3, 12, 'wood')
    cb(spin, 0, 4.0, 0, 13.6, 10, 13.6, 'wood')
    cb(spin, 0, 14.0, 0, 12, 3, 12, 'wood')
    for y in (2.6, 7.6, 12.6):                                   # 쇠테
        cb(spin, 0, y, 0, 14.2 if y == 7.6 else 13.0, 1.2, 14.2 if y == 7.6 else 13.0, 'iron')
    cb(spin, 0, 0.4, 0, 10.4, 0.8, 10.4, 'dwood')                 # 바닥
    # 열린 뚜껑 + 안쪽 어둠
    cb(spin, 0, 16.8, 0, 10.6, 0.6, 10.6, 'dark')
    lid = m.bone('lid', [-5.3, 17.2, 0], spin)
    lid.box([-5.6, 17.2, -5.3], [5.0, 18.2, 5.3], 'dwood', rot=('z', 22.5), rot_origin=[-5.3, 17.2, 0])
    # 삐져나온 고블린 (귀, 눈, 손, 단검) + 팀색 두건
    gob = m.bone('goblin', [0, 17, 0], spin)
    cb(gob, 0, 16.6, 0.5, 6, 3.2, 6, 'skin', decals={'north': [('rect', 0.12, 0.3, 0.38, 0.6, '#f6e46a'), ('rect', 0.62, 0.3, 0.88, 0.6, '#f6e46a'),
                                                              ('rect', 0.2, 0.38, 0.32, 0.6, '#c62d1f'), ('rect', 0.68, 0.38, 0.8, 0.6, '#c62d1f')]}, dens=2)
    for sx in (-1, 1):
        gob.box([min(sx * 3, sx * 7), 18.0, 0.0], [max(sx * 3, sx * 7), 19.4, 1.2], 'skin', rot=('z', 22.5 * sx), rot_origin=[sx * 3, 18.6, 0.6])
        gob.box([min(sx * 6.6, sx * 8.4), 19.2, 0.2], [max(sx * 6.6, sx * 8.4), 20.2, 1.0], 'dskin', rot=('z', 22.5 * sx), rot_origin=[sx * 3, 18.6, 0.6])
        cb(gob, sx * 5.8, 15.6, -3.6, 2.0, 2.4, 2.0, 'skin')     # 통 가장자리를 잡은 손
    band = m.bone('tc_band', [0, 19.4, 0], gob)
    cb(band, 0, 19.4, 0.5, 6.4, 1.4, 6.4, 'tc')
    cb(band, 0, 18.6, 4.0, 1.6, 2.4, 1.0, 'tc')
    cb(gob, 4.6, 16.2, -2.0, 0.6, 5.0, 0.6, 'iron2')              # 치켜든 단검
    cb(gob, 4.6, 15.6, -2.0, 1.8, 0.8, 0.8, 'dwood')
    # 밧줄 손잡이
    for sx in (-1, 1):
        cb(spin, sx * 7.3, 6.0, 0, 0.8, 4, 3, 'rope')
    # 날아가는 동안 앞으로 구르기 (2초 = 4바퀴)
    rot = [(round(i * 0.125, 3), (-90 * i, 0, 0)) for i in range(17)]
    m.anim('idle', 2.0, 'loop', {'spin': {'rotation': rot},
                                 'goblin': {'position': [(0, (0, 0, 0)), (0.25, (0, 0.8, 0)), (0.5, (0, 0, 0))]},
                                 'lid': {'rotation': [(0, (0, 0, 0)), (0.25, (0, 0, -20)), (0.5, (0, 0, 0))]}}, interp='linear')
    m.anim('walk', 0.5, 'loop', {'spin': {'rotation': rot[:5]}}, interp='linear')   # 고블린 walk(0.5초)와 길이 맞춤
    m.anim('spawn', 0.3, 'once', {'root': {'scale': [(0, (0.6, 0.6, 0.6)), (0.3, (1, 1, 1))]}})
    m.anim('death', 0.3, 'hold', {'root': {'scale': [(0, (1, 1, 1)), (0.3, (1.3, 0.3, 1.3))]}})
    return m
