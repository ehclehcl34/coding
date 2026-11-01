import sys,json;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools')
from bbrender import render;from PIL import Image
d=json.load(open('newmodels3/%s.bbmodel'%sys.argv[1]))
import bbrender
P=bbrender.sample(d,'idle',0) if len(sys.argv)>3 else None
a=render(d,560,cam=(0.6,0.2,-1.0),tint=(60,100,240),pose=P);b=render(d,560,cam=(-0.7,0.35,0.8),tint=(225,60,60),pose=P)
im=Image.new('RGBA',(1120,560),'white');im.paste(a,(0,0));im.paste(b,(560,0));im.save(sys.argv[2])
