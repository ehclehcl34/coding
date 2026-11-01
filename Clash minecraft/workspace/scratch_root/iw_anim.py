"""ice wizard attack: modest frost glow in the hands (was blowing up to 2.4x)"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad')
from animlib import *
p = 'newmodels3/clash_ice_wizard.bbmodel'; d, n = load(p)
for b in ('frost_r', 'frost_l'):
    setk(d, n, 'attack', b, 'scale', [(0, [1, 1, 1]), (0.2, [1.15, 1.15, 1.15]), (0.3, [1.35, 1.35, 1.35]), (0.38, [0.8, 0.8, 0.8]), (0.6, [1, 1, 1])])
json.dump(d, open(p, 'w'))
