#!/bin/bash
set -e
W=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work
cd $W
python3 mkpack370.py >/dev/null
rm -rf models_final && mkdir -p models_final && cp newmodels2/*.bbmodel models_final/ && cp newmodels3/*.bbmodel models_final/
P=$W/pkg370/ClashMC_v3.7.0; rm -rf $W/pkg370; mkdir -p $P/plugin $P/models/base $P/preview $P/source_3.7.0/src $P/source_3.7.0/tools
cp ClashMC-3.7.0.jar $P/plugin/; cp dec/config.yml $P/plugin/config.yml; cp pkg360/ClashMC_v3.6.0/plugin/skins.yml $P/plugin/
cp pkg360/ClashMC_v3.6.0/models/base/*.bbmodel $P/models/base/
cp models_final/*.bbmodel $P/models/base/
rm -f $P/models/base/clash_guard_parts.bbmodel
python3 fix_parts.py $P/models/base
python3 fix_split.py $P/models/base/clash_prince.bbmodel 24 lance,tc_lance,tc_pennant
for kv in royal_giant:1.32 electro_giant:1.31 bomb:2.0 elixir_golem:1.8 barbarian_hut:1.5 goblin_hut:1.4 giant:1.4 skeleton_balloon:1.4 balloon:1.5 ice_golem:1.8 golem:1.4 cannon_cart:1.8 cannon_cart_broken:1.8 tombstone:1.4 inferno:1.15 tesla:1.15 elixir_collector:1.15; do
  n=${kv%%:*}; k=${kv##*:}; f=$P/models/base/clash_$n.bbmodel; python3 scale_model.py $f $f $k > /dev/null
done
python3 - $P/models/base <<'PY2'
import json, subprocess, sys
B = sys.argv[1]
for m, v in json.load(open('spec_factors.json')).items():
    f = '%s/%s.bbmodel' % (B, m)
    subprocess.run(['python3', 'scale_model.py', f, f, str(v['factor'])], check=True, stdout=subprocess.DEVNULL)
    if 'widen' in v:
        subprocess.run(['python3', 'widen_model.py', f, str(v['widen'][0]), str(v['widen'][1])], check=True)
PY2
python3 dedupe_bones.py $P/models/base/*.bbmodel
python3 merge_tex.py $P/models/base/*.bbmodel
python3 fix_scale.py $P/models/base/*.bbmodel | wc -l
cp -r pkg360/ClashMC_v3.6.0/preview/* $P/preview/; cp newicons3_sheet.png $P/preview/card_icons_3.7.0.png; cp newmodels2/new_cards_3.7.0.png $P/preview/
mkdir -p $P/preview/models_3.7.0 && cp preview_final/*.png $P/preview/models_3.7.0/
cp pkg360/ClashMC_v3.6.0/server-icon.png $P/
mkdir -p $P/source_3.7.0/src/kr/kjmn/clashmc && cp dec/kr/kjmn/clashmc/*.java $P/source_3.7.0/src/kr/kjmn/clashmc/
cp prev_final.py widen_model.py scene_render.py prev_spec.py size_spec.py spec_factors.py spec_factors.json measure_model.py apply_spec_config.py gen_heights.py card_icons4.py mkpack370.py models_mc_b.py mk_guard.py mk_ptower.py mk_axe.py fix_scale.py fix_parts.py fix_split.py merge_tex.py dedupe_bones.py mk_proj.py recolor_pup.py iw_hair.py scale_model.py ../sg_anim.py ../mi_anim.py ../ex_anim.py ../vhw_anim.py ../iw_anim.py ../ban_anim.py ../animlib.py $P/source_3.7.0/tools/
python3 - <<PY
s=open('$W/pkg360/ClashMC_v3.6.0/README.md',encoding='utf-8').read()
s=s.replace('# 클래시 마크 3.6.0','# 클래시 마크 3.7.0',1).replace('ClashMC-3.6.0.jar','ClashMC-3.7.0.jar')
import re, os
n=len([f for f in os.listdir('$P/models/base') if f.endswith('.bbmodel')])
s=re.sub(r'\`models/base/\*\.bbmodel\`\(\d+\)','\`models/base/*.bbmodel\`(%d)'%n,s)
i=s.index('## 3.6.0')
s=s[:i]+open('$W/readme370.md',encoding='utf-8').read()+'\n'+s[i:]
open('$P/README.md','w',encoding='utf-8').write(s)
PY
cd $W/pkg370 && rm -f /home/user/ClashMC_v3.7.0.zip && zip -q -r /home/user/ClashMC_v3.7.0.zip ClashMC_v3.7.0 && ls -la /home/user/ClashMC_v3.7.0.zip && ls $P/models/base | wc -l
