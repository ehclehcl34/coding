"""miner attack: shovel overhead chop — blade swings over and strikes forward/down"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
W = [float(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [60, 0, 0]
S = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [-90, 0, 0]
p = 'newmodels3/clash_miner.bbmodel'; d, n = load(p)
I = [-30, 0, 4]
setk(d, n, 'attack', 'arm_r', 'rotation', [(0, I), (0.22, [-165, 0, 8]), (0.36, [-35, 0, 0]), (0.46, [-30, 0, 0]), (0.65, I)])
setk(d, n, 'attack', 'arm_l', 'rotation', [(0, [0, 0, -2]), (0.22, [-140, 0, -8]), (0.36, [-40, 0, 0]), (0.46, [-35, 0, 0]), (0.65, [0, 0, -2])])
setk(d, n, 'attack', 'pickaxe', 'rotation', [(0, [0, 0, 0]), (0.22, W), (0.36, S), (0.46, S), (0.65, [0, 0, 0])])
json.dump(d, open(p, 'w'))
