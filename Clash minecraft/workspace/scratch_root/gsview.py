import sys,json;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools')
from bbrender import render;from PIL import Image
d=json.load(open('newmodels3/clash_giant_skeleton.bbmodel'))
ims=[render(d,900,cam=c,tint=(60,100,240)).crop((200,250,700,650)) for c in ((0.6,0.2,-1.0),(1.0,0.1,-0.2),(0.1,-0.3,-1.0))]
im=Image.new('RGBA',(1500,400),'white')
for i,a in enumerate(ims): im.paste(a,(i*500,0))
im.save(sys.argv[1])
