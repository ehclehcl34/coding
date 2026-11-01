def battle_ram():
    """Two real barbarians (cloned from barbarian()) carrying an octagonal log overhead with an iron ram head + rings"""
    import copy
    m = new_model('clash_battle_ram')
    bb = barbarian()
    for k, v in bb.mats.items():
        m.mats.setdefault(k, v)
    m.mats_({'log': ('#a86a3a', 'wood', {'planks': True}), 'log_d': ('#7a4a26', 'wood'), 'iron': ('#5a6066', 'metal'),
             'iron_l': ('#8a9098', 'metal')})
    root = m.bone('root', [0, 0, 0])
    for pre, dx in (('a', -5.2), ('b', 5.2)):
        made = {}
        for bn in bb.bones:
            if bn.name in ('root', 'sword', 'hitbox'):
                continue
            nm = bn.name
            if nm == 'tc_sash':
                nm = 'tc_%s_shirt' % pre
            elif nm in ('arm_r', 'arm_l'):
                inner = (nm == 'arm_r') == (dx < 0)
                nm = '%s_arm_%s' % (pre, 'in' if inner else 'out')
            else:
                nm = '%s_%s' % (pre, nm)
            par = made.get(bn.parent.name) if bn.parent is not None and bn.parent.name != 'root' else root
            nb = m.bone(nm, [bn.origin[0] + dx, bn.origin[1], bn.origin[2]], par)
            made[bn.name] = nb
            for c in bn.cubes:
                f, t = c['frm'], c['to']
                nc = cb(nb, (f[0] + t[0]) / 2 + dx, f[1], (f[2] + t[2]) / 2, t[0] - f[0], t[1] - f[1], t[2] - f[2], c['mat'], rot=c['rot'])
                nc['decals'] = copy.deepcopy(c['decals']); nc['faces'] = dict(c['faces'])
    # the ram: octagonal log overhead, iron ram head in front, iron band + ring at the back
    ram = m.bone('ram', [0, 32.6, 0], root)
    cy = 32.6
    def octa(bone, z, ln, r, mat, dec=None):
        for rot in (None, ('z', 45)):
            cb(bone, 0, cy - r, z, 0.83 * r, 2 * r, ln, mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
            cb(bone, 0, cy - 0.415 * r, z, 2 * r, 0.83 * r, ln, mat, rot=rot, rot_origin=[0, cy, 0], decals=dec or {})
    grain = {f: [('rect', 0, k, 1, k + 0.04, '#7a4a26') for k in (0.3, 0.65)] for f in ('east', 'west', 'up', 'down')}
    octa(ram, -1.0, 18.0, 3.2, 'log', grain)                                            # log
    octa(ram, -12.4, 5.0, 4.4, 'iron')                                                  # ram head
    octa(ram, -15.6, 1.6, 3.2, 'iron')                                                  # faceted nose
    octa(ram, -16.8, 0.8, 1.8, 'iron_l')
    tb = m.bone('tc_band', [0, cy, 7], ram)
    octa(ram, 7.4, 2.2, 3.7, 'iron')                                                    # back band
    for z in (-12.4, 7.4):                                                              # rivets
        for (rx, ry) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            r = 4.6 if z < 0 else 3.9
            cb(ram, rx * r, cy + ry * r - 0.5, z, 1.0, 1.0, 1.0, 'iron_l')
    for sx in (1, -1):                                                                  # rings on the sides
        for z in (-12.4, 7.4):
            x0 = sx * (5.0 if z < 0 else 4.3)
            cb(ram, x0 + sx * 0.6, cy - 2.0, z, 0.5, 0.5, 2.2, 'iron_l')
            cb(ram, x0 + sx * 0.6, cy - 2.0, z - 1.0, 0.5, 1.6, 0.5, 'iron_l')
            cb(ram, x0 + sx * 0.6, cy - 2.0, z + 1.0, 0.5, 1.6, 0.5, 'iron_l')
    m.hitbox(2.0, 2.4)
    up_in_a, up_out_a = [-172, 0, -8], [-172, 0, 12]
    pose = {'a_arm_in': up_in_a, 'a_arm_out': up_out_a, 'b_arm_in': [-172, 0, 8], 'b_arm_out': [-172, 0, -12]}
    hold = {k: {'rotation': loop([v, [v[0] + 3, v[1], v[2]]], 2.0)} for k, v in pose.items()}
    hold['ram'] = {'position': loop([[0, 0, 0], [0, -0.4, 0]], 2.0)}
    m.anim('idle', 2.0, 'loop', hold)
    walk = {k: {'rotation': loop([v, v], 0.4)} for k, v in pose.items()}
    for pre, ph in (('a', 1), ('b', -1)):
        walk[pre + '_leg_r'] = {'rotation': loop([[-35 * ph, 0, 0], [35 * ph, 0, 0]], 0.4)}
        walk[pre + '_leg_l'] = {'rotation': loop([[35 * ph, 0, 0], [-35 * ph, 0, 0]], 0.4)}
    walk['ram'] = {'position': loop([[0, 0, 0], [0, 0.8, 0]], 0.2)}
    m.anim('walk', 0.4, 'loop', walk)
    atk = {k: {'rotation': [(0, v), (0.15, [v[0] + 20, v[1], v[2]]), (0.25, [v[0] - 15, v[1], v[2]]), (0.4, v)]} for k, v in pose.items()}
    atk['ram'] = {'position': [(0, [0, 0, 0]), (0.15, [0, 0, 3]), (0.25, [0, 0, -5]), (0.4, [0, 0, 0])]}
    m.anim('attack', 0.4, 'once', atk)
    common_tail(m, hit_bone='ram')
    return m


