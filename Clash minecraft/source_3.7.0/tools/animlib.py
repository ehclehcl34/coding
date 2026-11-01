import json, uuid
def load(p):
    d = json.load(open(p)); names = {}
    def w(t):
        for c in t:
            if isinstance(c, dict): names[c['name']] = c['uuid']; w(c.get('children', []))
    w(d['outliner']); return d, names
def kf(t, v, ch='rotation', interp='linear'):
    return {'channel': ch, 'data_points': [{'x': str(v[0]), 'y': str(v[1]), 'z': str(v[2])}], 'uuid': str(uuid.uuid4()), 'time': t, 'color': -1, 'interpolation': interp}
def setk(d, names, anim, bone, ch, seq, keep_other=True):
    a = [x for x in d['animations'] if x['name'] == anim][0]
    u = names[bone]
    an = a['animators'].setdefault(u, {'name': bone, 'type': 'bone', 'keyframes': []})
    an['keyframes'] = [k for k in an['keyframes'] if k['channel'] != ch] + [kf(t, v, ch) for t, v in seq]
def clear(d, anim, names, bones):
    a = [x for x in d['animations'] if x['name'] == anim][0]
    for b in bones: a['animators'].pop(names[b], None)
