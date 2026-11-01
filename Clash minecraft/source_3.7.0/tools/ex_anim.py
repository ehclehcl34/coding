"""executioner attack: wind up and fling the axe (the axe itself flies as clash_executioner_axe; plugin hides the hand axe)"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
p = 'newmodels3/clash_executioner.bbmodel'; d, n = load(p)
clear(d, 'attack', n, ['axe'])
setk(d, n, 'attack', 'arm_r', 'rotation', [(0, [0, 0, 0]), (0.18, [-150, 0, 10]), (0.26, [-70, 0, -10]), (0.36, [-45, 0, -20]), (0.6, [-40, 0, -15]), (0.8, [0, 0, 0])])
json.dump(d, open(p, 'w'))
