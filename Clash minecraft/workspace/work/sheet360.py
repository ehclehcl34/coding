import sys, json, os
sys.path.insert(0,'pkg340/ClashMC_v3.4.0/source/model_tools')
from bbrender import render
from PIL import Image, ImageDraw
names=['elixir_collector','royal_hog','valkyrie','guard','giant_skeleton','bowler','boulder','wall_breaker','hunter','executioner','princess','ice_wizard','lumberjack','magic_archer','bandit','inferno_dragon','mega_knight']
S=220; cols=7; im_rows=3
im=Image.new('RGBA',(S*cols,(S+20)*3),(232,236,241,255)); d=ImageDraw.Draw(im)
for i,n in enumerate(names):
    doc=json.load(open('models_final/clash_%s.bbmodel'%n))
    r=render(doc,S,(0.6,0.45,-1.0),tint=(60,90,255) if i%2==0 else (230,60,60))
    x,y=(i%cols)*S,(i//cols)*(S+20)
    im.alpha_composite(r.convert('RGBA'),(x,y+20)); d.text((x+6,y+4),n,fill=(20,20,20,255))
im.save('newmodels2/new_cards_3.6.0.png')
