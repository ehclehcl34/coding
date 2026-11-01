import sys,json,re;sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools')
import bbrender;from bbrender import render;from PIL import Image;import subprocess
ims=[]
for cand in sys.argv[2:]:
    src=open('models_mc_b.py').read();src=re.sub(r"BOW_AIM = \[.*?\]","BOW_AIM = ["+cand+"]",src);open('models_mc_b.py','w').write(src)
    subprocess.run(['python3','models_mc_b.py','pkg340/ClashMC_v3.4.0/source/model_tools','newmodels3','--no-preview','archer'],capture_output=True)
    d=json.load(open('newmodels3/clash_archer.bbmodel'))
    ims.append(render(d,420,cam=(0.9,0.3,-0.6),tint=(60,100,240),pose=bbrender.sample(d,'attack',0.5)))
im=Image.new('RGBA',(420*len(ims),420),'white')
for i,a in enumerate(ims): im.paste(a,(i*420,0))
im.save(sys.argv[1])
