#!/bin/bash
set -e
W=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work
cd $W
T=pkg340/ClashMC_v3.4.0/source/model_tools
python3 card_icons2.py $T chk/pack/assets/clashmc/textures/item newmodels2 newicons2 >/dev/null
python3 mkpack350.py
python3 sheet350.py
./build350.sh 2>&1 | grep -E "verified|error|Error" || true
P=$W/pkg350/ClashMC_v3.5.0; rm -rf $W/pkg350; mkdir -p $P/plugin $P/models/base $P/preview $P/source_3.5.0/src $P/source_3.5.0/tools
cp ClashMC-3.5.0.jar $P/plugin/; cp dec/config.yml $P/plugin/config.yml; cp pkg342/ClashMC_v3.4.2/plugin/skins.yml $P/plugin/
cp pkg342/ClashMC_v3.4.2/models/base/*.bbmodel $P/models/base/
cp rocket2/clash_rocket.bbmodel giant2/clash_giant.bbmodel $P/models/base/
cp newmodels2/*.bbmodel $P/models/base/
cp -r pkg342/ClashMC_v3.4.2/preview/* $P/preview/; cp newmodels2/new_cards_3.5.0.png $P/preview/; cp prev_350_bridge.png $P/preview/arena_3.5.0_bridge.png; cp prev_350_top.png $P/preview/arena_3.5.0_top.png; cp newicons2/_sheet350.png $P/preview/card_icons_3.5.0.png
for f in witch wizard zappies bomb_tower sparky pekka; do cp newmodels2/preview_clash_$f.png $P/preview/ 2>/dev/null || true; done
cp pkg342/ClashMC_v3.4.2/server-icon.png $P/
mkdir -p $P/source_3.5.0/src/kr/kjmn/clashmc && cp dec/kr/kjmn/clashmc/*.java $P/source_3.5.0/src/kr/kjmn/clashmc/
cp arena_gen.py scale_model.py models_m1.py models_m2.py models_m3.py card_icons2.py mkpack350.py rocket_scale.py bgm/compose.py $P/source_3.5.0/tools/
python3 - <<PY
s=open('$W/pkg342/ClashMC_v3.4.2/README.md',encoding='utf-8').read()
s=s.replace('# 클래시 마크 3.4.2','# 클래시 마크 3.5.0',1).replace('ClashMC-3.4.2.jar','ClashMC-3.5.0.jar')
import re, os
n=len([f for f in os.listdir('$P/models/base') if f.endswith('.bbmodel')])
s=re.sub(r'\`models/base/\*\.bbmodel\`\(\d+\)','\`models/base/*.bbmodel\`(%d)'%n,s)
add=open('$W/readme350.md',encoding='utf-8').read()
i=s.index('## 3.4.2')
s=s[:i]+add+'\n'+s[i:]
s=s.replace('| ff | leave | status\n','| ff | leave | status | bgm\n',1)
open('$P/README.md','w',encoding='utf-8').write(s)
PY
cd $W/pkg350 && rm -f /home/user/ClashMC_v3.5.0.zip && zip -q -r /home/user/ClashMC_v3.5.0.zip ClashMC_v3.5.0 && ls -la /home/user/ClashMC_v3.5.0.zip && ls $P/models/base | wc -l
