#!/bin/bash
# 3.6.0 빌드: 바뀐 클래스 컴파일 → 3.4.2 jar 에 덮어쓰기 → 검증
set -e
W=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work
Z=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/zip
cd $W
D=dec/kr/kjmn/clashmc
rm -rf stubcls3 && mkdir stubcls3 && javac -nowarn -d stubcls3 $(find stubs2 stubs_extra -name '*.java') 2>&1 | grep -A2 error || true
rm -rf out13 && mkdir out13
javac -Xmaxerrs 100 -nowarn -encoding UTF-8 -cp stubcls3:$Z/plugin/ClashMC-3.0.0.jar -d out13 $D/Battle.java $D/Combatant.java $D/CardDef.java $D/Clash.java $D/Arena.java $D/GameListener.java $D/ClashPlugin.java $D/Bars.java $D/Lobby.java $D/PackHost.java $D/PackMerge.java $D/ModelHook.java $D/BetterModelBackend.java $D/Bgm.java $D/Menus.java 2>&1 | grep -v JAVA_TOOL | grep -v '^Note' || true
ls out13/kr/kjmn/clashmc | wc -l
V=$W/verify360; rm -rf $V && mkdir -p $V && cd $V && unzip -q $W/ClashMC-3.5.0.jar
cp -r $W/out13/kr/kjmn/clashmc/* $V/kr/kjmn/clashmc/
cp $W/dec/config.yml $V/config.yml
cp $W/arena_350.schem $V/clash_arena.schem
sed -i 's/^version: .*/version: 3.6.0/' $V/plugin.yml
sed -i 's/usage: \/clash \[menu|ranked|ai|room|deck|skin|profile|top|ff|leave|status\]/usage: \/clash [menu|ranked|ai|room|deck|skin|profile|top|ff|leave|status|bgm]/' $V/plugin.yml
if [ -f $W/ClashMC_UI_pack_360.zip ]; then cp $W/ClashMC_UI_pack_360.zip $V/ClashMC_UI_pack.zip; fi
rm -f $W/ClashMC-3.6.0.jar
cd $V && zip -q -X -r $W/ClashMC-3.6.0.jar META-INF $(ls | grep -v META-INF)
cd $W
java -Xverify:all -cp $W/vchk:$V:$W/stubcls3:$W/lib/gson.jar V8 2>&1 | grep -v JAVA_TOOL
ext(){ grep -oE '(invoke\w+|getstatic|getfield|putfield|putstatic) +#[0-9]+(, +[0-9]+)? +// (Method|InterfaceMethod|Field) [a-z][^ ]*/[^ ]+' | sed -E 's/ +#[0-9]+(, +[0-9]+)? +\/\/ / /' | grep -v ' kr/\| java/' | sort -u; }
javap -c -p $(find out13 -name '*.class') 2>/dev/null | ext > new_refs14.txt
echo "--- new external refs vs 3.4.2 build:"; comm -23 new_refs14.txt new_refs13b.txt | grep -E 'org/bukkit|com/|net/' || true
