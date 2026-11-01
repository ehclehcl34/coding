import sys,json;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools')
import bbrender;from PIL import Image
d=json.load(open(sys.argv[1] if '/' in sys.argv[1] else 'newmodels3/%s.bbmodel'%sys.argv[1]))
an=sys.argv[2];ts=[float(x) for x in sys.argv[4].split(',')]
cam=(0.9,0.25,-0.5) if len(sys.argv)<6 else tuple(float(x) for x in sys.argv[5].split(','))
ims=[bbrender.render(d,360,cam=cam,tint=(60,100,240),pose=bbrender.sample(d,an,t)) for t in ts]
im=Image.new('RGBA',(360*len(ims),360),'white')
for i,a in enumerate(ims): im.paste(a,(i*360,0))
im.save(sys.argv[3])
