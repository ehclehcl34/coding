"""도끼맨이 던지는 도끼 투사체: 도끼맨 모델의 양날 도끼를 눕혀서 세로축으로 빙글빙글 (clash_executioner_axe, 애니메이션 spin)"""
import json, uuid, copy
d = json.load(open('newmodels3/clash_executioner.bbmodel'))
def find(t, name):
    for c in t:
        if isinstance(c, dict):
            if c['name'] == name: return c
            r = find(c['children'], name)
            if r: return r
g = find(d['outliner'], 'axe')
ids = [c for c in g['children'] if not isinstance(c, dict)]
C = [6.4, 13.7, -9.0]                                      # 손잡이 가운데쯤을 중심으로
FM = {'east': 'up', 'up': 'west', 'west': 'down', 'down': 'east', 'north': 'north', 'south': 'south'}
def R(v):  # z 축 90도: (x, y, z) -> (-y, x, z), 중심 기준 + 높이 1블록
    x, y, z = v[0] - C[0], v[1] - C[1], v[2] - C[2]
    return [-y, x + 8, z]
E = []
for e in d['elements']:
    if e['uuid'] not in ids: continue
    e = copy.deepcopy(e)
    a, b = R(e['from']), R(e['to'])
    e['from'] = [min(a[i], b[i]) for i in range(3)]; e['to'] = [max(a[i], b[i]) for i in range(3)]
    e['origin'] = R(e['origin'])
    e['faces'] = {FM[k]: v for k, v in e['faces'].items()}
    E.append(e)
sp = {'name': 'spin', 'origin': [0, 8, 0], 'color': 0, 'uuid': str(uuid.uuid4()), 'export': True, 'isOpen': True, 'locked': False, 'visibility': True, 'autouv': 0, 'children': [e['uuid'] for e in E]}
root = dict(sp, name='root', uuid=str(uuid.uuid4()), origin=[0, 0, 0], children=[sp])
kf = lambda t, y: {'channel': 'rotation', 'data_points': [{'x': '0', 'y': str(y), 'z': '0'}], 'uuid': str(uuid.uuid4()), 'time': t, 'color': -1, 'interpolation': 'linear'}
anim = {'uuid': str(uuid.uuid4()), 'name': 'spin', 'loop': 'loop', 'override': False, 'length': 0.3, 'snapping': 20, 'selected': False, 'anim_time_update': '', 'blend_weight': '', 'start_delay': '', 'loop_delay': '',
        'animators': {sp['uuid']: {'name': 'spin', 'type': 'bone', 'keyframes': [kf(0, 0), kf(0.1, -120), kf(0.2, -240), kf(0.3, -360)]}}}
idle = dict(anim, uuid=str(uuid.uuid4()), name='idle')
d['elements'] = E; d['outliner'] = [root]; d['animations'] = [anim, idle]; d['name'] = 'clash_executioner_axe'
json.dump(d, open('newmodels3/clash_executioner_axe.bbmodel', 'w'))
print(len(E))
