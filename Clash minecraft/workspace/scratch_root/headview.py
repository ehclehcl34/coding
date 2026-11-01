import sys,json;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools');import bbrender;from PIL import Image
d=json.load(open('newmodels3/%s.bbmodel'%sys.argv[1])); keep=sys.argv[3].split(',')
par=bbrender.element_parents(d)
d['elements']=[e for e in d['elements'] if any(b[2] in keep for b in par[e['uuid']])]
im=Image.new('RGBA',(1200,400),'white')
for i,c in enumerate(((0.001,0.15,-1),(0.7,0.25,-0.8),(-1,0.1,0.001))): im.paste(bbrender.render(d,400,cam=c,tint=(60,100,240)),(400*i,0))
im.save(sys.argv[2])
