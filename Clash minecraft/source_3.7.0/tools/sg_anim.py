"""spear goblin attack: spear raised overhead pointing forward, thrown at release (spear hidden until re-equip)"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
SR = [float(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [-80, 0, 0]
p = 'newmodels3/clash_spear_goblin.bbmodel'; d, n = load(p)
I = [-15, 0, -4]
setk(d, n, 'attack', 'left_arm', 'rotation', [(0, I), (0.18, [-165, 0, -8]), (0.26, [-170, 0, -8]), (0.34, [-60, 0, 0]), (0.45, [-40, 0, 0]), (0.6, I)])
setk(d, n, 'attack', 'spear', 'rotation', [(0, [0, 0, 0]), (0.18, SR), (0.3, SR), (0.34, [0, 0, 0]), (0.6, [0, 0, 0])])
setk(d, n, 'attack', 'spear', 'scale', [(0, [1, 1, 1]), (0.27, [1, 1, 1]), (0.28, [0.01, 0.01, 0.01]), (0.52, [0.01, 0.01, 0.01]), (0.6, [1, 1, 1])])
json.dump(d, open(p, 'w'))
